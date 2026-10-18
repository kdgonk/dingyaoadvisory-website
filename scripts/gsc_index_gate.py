#!/usr/bin/env python3
"""S-20261019-01 索引閘門 — 每日 URL Inspection 追蹤（sitemap lastmod ≤14 天差集）。

設計（2026-10-19 土星人裁決 P1）：
  · 追蹤清單 = 固定 4 頁 gate targets ∪ sitemap 中 lastmod ≤14 天的 /blog/ 新頁
  · 每日逐頁呼叫 URL Inspection API，記錄 coverageState / lastCrawl
  · 只在「狀態變更」或「首次納管」或「T+7 仍未收錄」時輸出；其餘靜默（stdout 空 = 不發訊息）
  · 4/4 已 indexed → 輸出一次結案訊息後永久靜默
  · 遞送保留：每頁 3 天冷卻、每日上限 2 頁（Indexing API 200 不保證收錄，僅作訊號）

狀態檔：~/.hermes/state/gsc_index_gate_S-20261019-01.json（去重、first_seen、last_status）
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
    return idx.get('coverageState') or 'UNKNOWN', idx.get('lastCrawlTime')


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
    today_d = datetime.date.today()
    today = today_d.isoformat()
    state = load_state()
    pages = state.setdefault('pages', {})
    subs = state.setdefault('submissions', {})
    tracked = state.setdefault('tracked', list(TRACKED_DEFAULT))

    if state.get('closed'):
        return 0  # 結案後永久靜默

    gsc, ix = services()

    recent = sitemap_recent(today_d)
    new_urls = [u for u, _ in recent if u not in pages]
    # 非 gate 頁複查：滿 7 天仍未收錄者，每日最多 MAX_RECHECK 頁（避免 289 頁每日全掃拖垮 cron）
    recheck = []
    for u, rec in pages.items():
        if u in tracked or rec.get('status') in OK_STATES:
            continue
        try:
            age_chk = (today_d - datetime.date.fromisoformat(rec.get('last_checked', today))).days
        except ValueError:
            age_chk = 0
        if age_chk >= 7:
            recheck.append(u)
    candidates = tracked + new_urls[:MAX_NEW_PER_DAY] + recheck[:MAX_RECHECK]
    candidates = list(dict.fromkeys(candidates))  # 去重且保序

    lines, changed, t7_alert = [], [], []
    pending = []
    for url in candidates:
        prev = pages.get(url, {})
        try:
            cov, crawl = inspect(gsc, url)
        except Exception as exc:  # noqa: BLE001
            cov, crawl = 'INSPECT_ERROR: ' + str(exc)[:80], None
        is_new = not prev
        pages[url] = {
            'status': cov,
            'lastCrawl': crawl,
            'first_seen': prev.get('first_seen', today),
            'last_checked': today,
        }
        if cov not in OK_STATES:
            pending.append(url)
        is_tracked = url in tracked
        status_changed = is_new or prev.get('status') != cov
        # T+7：納管滿 7 天仍未被收錄
        try:
            age = (today_d - datetime.date.fromisoformat(pages[url]['first_seen'])).days
        except ValueError:
            age = 0
        overdue = cov not in OK_STATES and age >= T7_DAYS
        if (is_tracked and status_changed) or (not is_tracked and status_changed and cov in OK_STATES):
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

    indexed = sum(1 for u in tracked if pages.get(u, {}).get('status') in OK_STATES)
    if tracked and indexed == len(tracked):
        state['closed'] = True
        state['closed_at'] = today
        save_state(state)
        print(f'✅ S-20261019-01 索引閘門結案：{indexed}/{len(tracked)} 全部 indexed（{today}）')
        return 0

    # 靜默條件：無狀態變更、無 T+7 告警、無遞送、未過 deadline
    if not changed and not t7_alert and not sent and today <= DEADLINE:
        return 0

    head = f'📊 索引閘門 {today}｜gate {indexed}/{len(tracked)}｜納管 {len(pages)} 頁'
    if today > DEADLINE:
        head = f'🚨 已過 deadline {DEADLINE}，gate 仍 {indexed}/{len(tracked)}｜' + head.split('｜', 1)[1]
    print(head)
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
