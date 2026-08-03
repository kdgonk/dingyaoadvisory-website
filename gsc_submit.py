#!/usr/bin/env python3
"""Submit new URLs to Google Search Console Indexing API."""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds_path = '/Users/dingyao/.openclaw/secrets/hermes-gsc-service-account.json'
with open(creds_path) as f:
    creds_info = json.load(f)

creds = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=['https://www.googleapis.com/auth/webmasters']
)

service = build('searchconsole', 'v1', credentials=creds)
site_url = 'scoped:https://dingyaoadvisory.tw'

urls = [
    'https://dingyaoadvisory.tw/blog/sarb-july-mpc-cape-town-property',
    'https://dingyaoadvisory.tw/blog/sarb-july-mpc-cape-town-property-en',
]

for url in urls:
    try:
        result = service.urlInspection().index().inspect(
            body={'inspectionUrl': url, 'siteUrl': site_url}
        ).execute()
        print(f'OK {url}')
    except Exception as e:
        print(f'ERR {url}: {str(e)[:120]}')

try:
    sitemap_url = 'https://dingyaoadvisory.tw/sitemap.xml'
    result = service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
    print(f'OK sitemap submitted')
except Exception as e:
    print(f'ERR sitemap: {str(e)[:120]}')

print('DONE')
