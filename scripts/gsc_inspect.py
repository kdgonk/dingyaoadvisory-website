#!/usr/bin/env python3
"""GSC URL Inspection 檢查器 — 印出覆蓋狀態 / 最後爬取時間 / verdict。

用法:
  python3 gsc_inspect.py <url> [<url> ...]
  python3 gsc_inspect.py --file urls.txt
"""
import json
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDS = '/Users/dingyao/.openclaw/secrets/hermes-gsc-service-account.json'
SITE = 'sc-domain:dingyaoadvisory.tw'


def service():
    creds = service_account.Credentials.from_service_account_info(
        json.load(open(CREDS)),
        scopes=['https://www.googleapis.com/auth/webmasters'],
    )
    return build('searchconsole', 'v1', credentials=creds)


def inspect(svc, url):
    res = svc.urlInspection().index().inspect(
        body={'inspectionUrl': url, 'siteUrl': SITE}
    ).execute()
    r = res.get('inspectionResult', {})
    idx = r.get('indexStatusResult', {})
    return {
        'url': url,
        'coverageState': idx.get('coverageState'),
        'verdict': idx.get('verdict'),
        'lastCrawlTime': idx.get('lastCrawlTime', '(never)'),
        'pageFetchState': idx.get('pageFetchState'),
        'indexingState': idx.get('indexingState'),
        'googleCanonical': idx.get('googleCanonical'),
        'userCanonical': idx.get('userCanonical'),
        'robotsTxtState': idx.get('robotsTxtState'),
        'sitemaps': idx.get('sitemaps'),
    }


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == '--file':
        urls = [l.strip() for l in open(args[1]) if l.strip() and not l.startswith('#')]
    else:
        urls = args
    svc = service()
    out = [inspect(svc, u) for u in urls]
    for row in out:
        print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
