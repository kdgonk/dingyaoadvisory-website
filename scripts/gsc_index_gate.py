#!/usr/bin/env python3
"""S-20261019-01 索引閘門 — 每日 URL Inspection 追蹤（sitemap lastmod ≤14 天差集）。

設計（2026-10-19 土星人裁決 P1）：
  · 追蹤清單 = 固定 4 頁 gate targets ∪ sitemap 中 lastmod ≤14 天的 /blog/ 新頁
  · 每日逐頁呼叫 URL Inspection API，記錄 coverageState / lastCrawl
  · 只在「狀態變更」或「首次納管」或「T+7 仍未收錄」時輸出；其餘靜默（stdout 空 = 不發訊息）
  · 4/4 已 indexed → 輸出一次結案訊息後永久靜默
  · 遞送保留：每頁 3 天冷卻、每日上限 2 頁（Indexing API 200 不保證收錄，僅作訊號）

狀態檔：~/.hermes/state/gsc_index_gate_S-20261019-01.json（去重、first_seen、last_status）
監看清單：~/.hermes/state/gsc_gate_watchlist.json（{"until":"YYYY-MM-DD","urls":[...]}，
          until 前每日併入檢查並無條件輸出逐頁 verdict／coverageState／lastCrawl；
          未索引一律標「順延」不標失敗；不併入 tracked、不觸發 Indexing API 遞送。
          當日快照寫入 ~/.hermes/state/gsc_gate_watch_history.jsonl（date+url 去重）。
          `--watch-report` 只掃 watch 清單並輸出表格（驗證日回填用）。
"""
import datetime
import json
import os
import re
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDS = '/Users/dingyao/.openclaw/secrets/hermes-gsc-service-account.json'
SITE = 'sc-domain:dingyaoadvisory.tw'
STATE = os.path.expanduser('~/.hermes/state/gsc_index_gate_S-20261019-01.json')
SITEMAP = os.path.expanduser(
    '~/Documents/DingYao-Website/dingyaoadvisory-website/dist/sitemap.xml')
DEADLINE = '2026-11-02'
DAILY_LIMIT = 2
COOLDOWN_DAYS = 3
LOOKBACK_DAYS = 14        # sitemap lastmod 在此天數內 → 納管
MAX_NEW_PER_DAY = 8       # 每日最多新納管檢查頁數（backlog 每日消化，避免 cron 超時）
MAX_RECHECK = 6           # 每日最多複查（非 gate 頁、滿 7 天未被收錄者）
T7_DAYS = 7               # 納管滿 7 天仍未收錄 → 告警（即使狀態沒變）

# gate targets（策略卡保護對象）：最弱的先送
TRACKED_DEFAULT = [
    'https://dingyaoadvisory.tw/blog/taiwan-wealthy-overseas-asset-allocation-2026',
    'https://dingyaoadvisory.tw/blog/cape-town-safety-guide-foreign-buyers-2026',
    'https://dingyaoadvisory.tw/blog/cape-town-short-term-letting-by-law-2026',
    'https://dingyaoadvisory.tw/blog/cape-town-gated-communities-guide-2026',
]

OK_STATES = {'Submitted and indexed'}

# ── 驗證批次監看清單（2026-11-03 土星人指派 S-20261103-N2／S-20261019-02／-03／S-20261020-01）──
# 為什麼要有：這批 URL 的 sitemap lastmod 都在 10-26 前後，靠 lookback=14 天會在
# 11-16/11-17 當天滑出追蹤範圍（cut=11-02），導致最關鍵的驗證日看不到資料。
# 設計：watch URL 不併入 tracked（不動既有 gate 4 頁的摘要與結案語意），
#       只併入「今日檢查」並無條件輸出逐頁 verdict／coverageState／lastCrawl。
WATCHLIST = os.path.expanduser('~/.hermes/state/gsc_gate_watchlist.json')


def load_watchlist(today_d):
    """回傳 (urls, until, label)；today 不在 [from, until] 內 → ([], ...)。

    `from` 可省略（＝即刻生效）。設 from 是為了避免非驗證日拖長每日 cron 時間
    （實測 URL Inspection 約 7 秒／頁，10 頁 ≈ 72 秒）；--watch-report 不受 from 限制。
    """
    if not os.path.exists(WATCHLIST):
        return [], None, None
    try:
        d = json.load(open(WATCHLIST, encoding='utf-8'))
    except Exception:  # noqa: BLE001
        return [], None, None
    urls = [u.strip() for u in d.get('urls', []) if u and u.strip()]
    until = d.get('until')
    start = d.get('from')
    try:
        active = today_d <= datetime.date.fromisoformat(until)
        if start:
            active = active and today_d >= datetime.date.fromisoformat(start)
    except Exception:  # noqa: BLE001
        active = False
    return (urls if active else []), until, d.get('label')


def watch_report(watch, pages):
    """逐頁表格：verdict／coverageState／lastCrawl。未索引一律標「順延」（不可寫成失敗）。"""
    if not watch:
        return
    print(f'🔎 驗證批次監看 {len(watch)} 頁')
    for u in watch:
        rec = pages.get(u, {})
        cov = rec.get('status', 'NOT_CHECKED')
        crawl = rec.get('lastCrawl') or 'never'
        verdict = rec.get('verdict', 'UNKNOWN')
        band = rec.get('band', 'n/a')
        tag = 'indexed' if band == 'indexed' else '順延'
        print(f'  · {u.rsplit("/", 1)[-1]} | verdict={verdict} | '
              f'coverageState={cov} | lastCrawl={crawl} | {tag}')


def record_watch_history(watch, pages, today):
    """把 watch 頁當日快照寫入 JSONL（同一 date+url 只留一筆），供驗證日做 11-16→11-17 對照。"""
    if not watch:
        return
    path = os.path.expanduser('~/.hermes/state/gsc_gate_watch_history.jsonl')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    seen = set()
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            try:
                d = json.loads(line)
                seen.add((d.get('date'), d.get('url')))
            except Exception:  # noqa: BLE001
                continue
    with open(path, 'a', encoding='utf-8') as fh:
        for u in watch:
            if (today, u) in seen:
                continue
            rec = pages.get(u, {})
            fh.write(json.dumps({
                'date': today,
                'url': u,
                'verdict': rec.get('verdict', 'UNKNOWN'),
                'coverageState': rec.get('status', 'NOT_CHECKED'),
                'lastCrawl': rec.get('lastCrawl'),
                'band': rec.get('band', 'n/a'),
            }, ensure_ascii=False) + '\n')


def band_of(cov):
    """把 coverageState 正規化成穩定頻帶，避免 Google 在 unknown/discovered 間跳動造成每日假告警。"""
    if cov in OK_STATES:
        return 'indexed'
    low = cov.lower()
    if 'unknown to google' in low or 'discovered' in low or 'crawled - currently not indexed' in low:
        return 'not_indexed'
    return cov


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as fh:
            return json.load(fh)
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + '.tmp'
    with open(tmp, 'w') as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE)


def services():
    info = json.load(open(CREDS))
    wm = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/webmasters'])
    ix = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/indexing'])
    return build('searchconsole', 'v1', credentials=wm), build('indexing', 'v3', credentials=ix)


def inspect(gsc, url):
    r = gsc.urlInspection().index().inspect(
        body={'inspectionUrl': url, 'siteUrl': SITE}).execute()
    idx = r.get('inspectionResult', {}).get('indexStatusResult', {})
    return (idx.get('coverageState') or 'UNKNOWN',
            idx.get('lastCrawlTime'),
            idx.get('verdict') or 'UNKNOWN')


def sitemap_recent(today):
    """回傳 [(url, lastmod)]，只取 /blog/ 且 lastmod ≥ today-LOOKBACK_DAYS，新到舊。"""
    if not os.path.exists(SITEMAP):
        return []
    xml = open(SITEMAP, encoding='utf-8').read()
    cut = (today - datetime.timedelta(days=LOOKBACK_DAYS)).isoformat()
    out = []
    for block in re.findall(r'<url>(.*?)</url>', xml, re.S):
        loc = re.search(r'<loc>(.*?)</loc>', block)
        lm = re.search(r'<lastmod>(.*?)</lastmod>', block)
        if not loc or not lm:
            continue
        url, lastmod = loc.group(1).strip(), lm.group(1).strip()[:10]
        if '/blog/' in url and lastmod >= cut:
            out.append((url, lastmod))
    out.sort(key=lambda x: x[1], reverse=True)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--watch-report', action='store_true',
                    help='只輸出驗證批次監看清單逐頁表格（verdict/coverageState/lastCrawl）')
    args = ap.parse_args()
    today_d = datetime.date.today()
    today = today_d.isoformat()
    state = load_state()
    pages = state.setdefault('pages', {})
    subs = state.setdefault('submissions', {})
    tracked = state.setdefault('tracked', list(TRACKED_DEFAULT))

    watch, watch_until, watch_label = load_watchlist(today_d)
    if args.watch_report and not watch:
        # 驗證日手動回填不受 from 限制
        try:
            watch = [u for u in json.load(open(WATCHLIST, encoding='utf-8')).get('urls', []) if u]
        except Exception:  # noqa: BLE001
            watch = []

    if state.get('closed') and not watch:
        return 0  # 結案後永久靜默

    gsc, ix = services()

    recent = sitemap_recent(today_d)
    new_urls = [u for u, _ in recent if u not in pages]
    # 非 gate 頁複查：滿 7 天仍未收錄者，每日最多 MAX_RECHECK 頁（避免 289 頁每日全掃拖垮 cron）
    recheck = []
    for u, rec in pages.items():
        if u in tracked or rec.get('band') == 'indexed':
            continue
        try:
            age_chk = (today_d - datetime.date.fromisoformat(rec.get('last_checked', today))).days
        except ValueError:
            age_chk = 0
        if age_chk >= 7:
            recheck.append(u)
    candidates = tracked + new_urls[:MAX_NEW_PER_DAY] + recheck[:MAX_RECHECK]
    candidates += watch
    if args.watch_report:  # 只掃 watch，避免拖長 cron 時間
        candidates = list(watch)
    candidates = list(dict.fromkeys(candidates))  # 去重且保序

    lines, changed, t7_alert = [], [], []
    pending = []
    for url in candidates:
        prev = pages.get(url, {})
        try:
            cov, crawl, verdict = inspect(gsc, url)
        except Exception as exc:  # noqa: BLE001
            cov, crawl, verdict = 'INSPECT_ERROR: ' + str(exc)[:80], None, 'UNKNOWN'
        is_new = not prev
        band = band_of(cov)
        pages[url] = {
            'status': cov,
            'band': band,
            'lastCrawl': crawl,
            'verdict': verdict,
            'first_seen': prev.get('first_seen', today),
            'last_checked': today,
        }
        if band != 'indexed':
            pending.append(url)
        is_tracked = url in tracked
        status_changed = is_new or prev.get('band') != band
        # T+7：納管滿 7 天仍未被收錄
        try:
            age = (today_d - datetime.date.fromisoformat(pages[url]['first_seen'])).days
        except ValueError:
            age = 0
        overdue = band != 'indexed' and age >= T7_DAYS
        # 只有 gate 頁的頻帶變化才報；非 gate 頁（backlog）靜默記錄，不逐頁洗版
        if is_tracked and status_changed:
            changed.append((url, cov, crawl, is_new))
        if is_tracked and overdue:
            t7_alert.append((url, cov, age))

    # 遞送（僅 gate targets，冷卻 3 天、每日 2 頁）
    sent = []
    for url in [u for u in tracked if u in pending]:
        if len(sent) >= DAILY_LIMIT:
            break
        last = subs.get(url)
        if last:
            try:
                if (today_d - datetime.date.fromisoformat(last)).days < COOLDOWN_DAYS:
                    continue
            except ValueError:
                pass
        try:
            ix.urlNotifications().publish(body={'url': url, 'type': 'URL_UPDATED'}).execute()
            subs[url] = today
            sent.append(url)
        except Exception as exc:  # noqa: BLE001
            sent.append(f'{url}（送件失敗: {str(exc)[:60]}）')

    if sent:
        state.setdefault('history', []).append({'date': today, 'submitted': sent})
    save_state(state)
    record_watch_history(watch, pages, today)

    if args.watch_report:
        watch_report(watch, pages)
        return 0

    indexed = sum(1 for u in tracked if pages.get(u, {}).get('band') == 'indexed')
    if tracked and indexed == len(tracked):
        state['closed'] = True
        state['closed_at'] = today
        save_state(state)
        print(f'✅ S-20261019-01 索引閘門結案：{indexed}/{len(tracked)} 全部 indexed（{today}）')
        return 0

    # 每日固定一行 gate 摘要（土星人 2026-10-19 驗收：每日要看得到 4 頁狀態、且不得重複噪音）
    def _tag(u):
        b = pages.get(u, {}).get('band', 'n/a')
        return {'indexed': 'indexed', 'not_indexed': 'not-indexed'}.get(b, b[:14])

    print(f'📊 索引閘門 {today}｜gate {indexed}/{len(tracked)}｜' + ', '.join(
        f'{u.rsplit("/", 1)[-1]}={_tag(u)}' for u in tracked))

    # 明細只在有變化／T+7／遞送／過 deadline 時輸出
    watch_report(watch, pages)
    if not changed and not t7_alert and not sent and today <= DEADLINE:
        return 0

    if today > DEADLINE:
        print(f'  🚨 已過 deadline {DEADLINE}，gate 仍 {indexed}/{len(tracked)}')
    if changed:
        print('  狀態變更：')
        for url, cov, crawl, is_new in changed:
            tag = 'NEW ' if is_new else 'DIFF'
            print(f'  [{tag}] {url.rsplit("/", 1)[-1]}: {cov} | lastCrawl={crawl or "never"}')
    if t7_alert:
        print(f'  ⏰ T+{T7_DAYS} 仍未收錄：')
        for url, cov, age in t7_alert:
            print(f'  · {url.rsplit("/", 1)[-1]}: {cov}（納管 {age} 天）')
    if sent:
        print('  → Indexing API 遞送: ' + ', '.join(s.rsplit('/', 1)[-1] for s in sent))
    return 0


if __name__ == '__main__':
    sys.exit(main())
