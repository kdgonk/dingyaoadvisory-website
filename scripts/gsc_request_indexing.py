#!/usr/bin/env python3
"""GSC Indexing API 送索引通知（URL_UPDATED）。

Google 官方只保證 JobPosting / BroadcastEvent，其他頁面多半回 200 但不保證收錄。
若回 403（service account 無 Indexing API 權限）就必須走 GSC UI 的 Request Indexing。

用法:
  python3 gsc_request_indexing.py https://dingyaoadvisory.tw/blog/xxx
"""
import json
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDS = '/Users/dingyao/.openclaw/secrets/hermes-gsc-service-account.json'


def main():
    urls = sys.argv[1:]
    if not urls:
        print(__doc__)
        return 1
    creds = service_account.Credentials.from_service_account_info(
        json.load(open(CREDS)),
        scopes=['https://www.googleapis.com/auth/indexing'],
    )
    svc = build('indexing', 'v3', credentials=creds)
    rc = 0
    for url in urls:
        try:
            res = svc.urlNotifications().publish(
                body={'url': url, 'type': 'URL_UPDATED'}
            ).execute()
            print(json.dumps({'url': url, 'ok': True, 'response': res}, ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            rc = 2
            print(json.dumps({'url': url, 'ok': False, 'error': str(exc)}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    sys.exit(main())
