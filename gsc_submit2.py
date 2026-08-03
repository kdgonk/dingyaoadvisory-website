#!/usr/bin/env python3
"""Submit sitemap to GSC using domain property format."""
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

# Domain property format
site_url = 'sc-domain:dingyaoadvisory.tw'

# Submit sitemap
try:
    result = service.sitemaps().submit(
        siteUrl=site_url,
        feedpath='https://dingyaoadvisory.tw/sitemap.xml'
    ).execute()
    print(f'OK sitemap submitted to {site_url}')
except Exception as e:
    print(f'ERR: {str(e)[:300]}')

# List sitemaps to verify
try:
    sitemaps = service.sitemaps().list(siteUrl=site_url).execute()
    print(f'Sitemaps: {json.dumps(sitemaps, indent=2)[:500]}')
except Exception as e:
    print(f'List ERR: {str(e)[:200]}')

print('DONE')
