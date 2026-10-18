#!/usr/bin/env python3
"""S-20261019-01 索引閘門 — 每日 1–2 頁送 Indexing API + 回報 URL Inspection 狀態。

背景：4 篇新頁停在 Discovered - currently not indexed、lastCrawl 從未發生。
Google 的「Request Indexing」只在 GSC UI 提供（無程式化 API），本腳本用
Indexing API URL_UPDATED 做每日錯開遞送（配額自律：每天最多 2 頁），
並用 URL Inspection API 追蹤 coverageState，目標 2026-11-02 前 4/4 indexed。

輸出（stdout 即訊息）：
  每日一行狀態 + 今日遞送清單；4/4 全 indexed 時輸出結案訊息。
無事可報（已全數 indexed 且已結案）→ 不輸出（靜默）。

狀態檔：~/.hermes/state/gsc_index_gate_S-20261019-01.json
"""
import datetime
import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDS = '/Users/dingyao/.openclaw/secrets/hermes-gsc-service-account.json'
SITE = 'sc-domain:dingyaoadvisory.tw'
STATE = os.path.expanduser('~/.hermes/state/gsc_index_gate_S-20261019-01.json')
DEADLINE = '2026-11-02'
DAILY_LIMIT = 2
COOLDOWN_DAYS = 3

# 排序 = 遞送優先序：最弱的先送（unknown to Google > discovered）
TARGETS = [
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
    return {'submissions': {}, 'history': []}


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


def main():
    today = datetime.date.today().isoformat()
    gsc, ix = services()
    state = load_state()
    subs = state.setdefault('submissions', {})

    rows, pending = [], []
    for url in TARGETS:
        try:
            cov, crawl = inspect(gsc, url)
        except Exception as exc:  # noqa: BLE001
            cov, crawl = f'INSPECT_ERROR: {exc}'[:80], None
        rows.append((url, cov, crawl))
        if cov not in OK_STATES:
            pending.append(url)

    if not pending:
        print(f'✅ S-20261019-01 結案：4/4 已 indexed（{today} 檢查）')
        return 0

    sent = []
    for url in pending:
        if len(sent) >= DAILY_LIMIT:
            break
        last = subs.get(url)
        if last:
            # 每頁 3 天內不重送（避免對同一頁刷遞送稀釋配額）
            try:
                if (datetime.date.today() - datetime.date.fromisoformat(last)).days < COOLDOWN_DAYS:
                    continue
            except ValueError:
                pass
        try:
            ix.urlNotifications().publish(body={'url': url, 'type': 'URL_UPDATED'}).execute()
            subs[url] = today
            sent.append(url)
        except Exception as exc:  # noqa: BLE001
            sent.append(f'{url}（送件失敗: {str(exc)[:60]}）')

    state.setdefault('history', []).append({'date': today, 'submitted': sent, 'pending': len(pending)})
    save_state(state)

    flag = ''
    if today > DEADLINE and pending:
        flag = f'🚨 已過 deadline {DEADLINE}，仍未 4/4 — 需人工在 GSC UI Request Indexing\n'
    print(f'{flag}📊 S-20261019-01 索引閘門 {today}（deadline {DEADLINE}）: indexed {len(TARGETS) - len(pending)}/4')
    for url, cov, crawl in rows:
        slug = url.rsplit('/', 1)[-1]
        print(f'  · {slug}: {cov} | lastCrawl={crawl or "never"}')
    if sent:
        print('  → 今日 Indexing API 遞送: ' + ', '.join(s.rsplit('/', 1)[-1] for s in sent))
    else:
        print('  → 今日無新遞送（今日配額已用或待明日錯開）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
