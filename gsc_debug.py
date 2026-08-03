#!/usr/bin/env python3
"""Submit new URLs to Google Search Console - with full error details."""
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

# Try different site URL formats
site_formats = [
    'scoped:https://dingyaoadvisory.tw',
    'https://dingyaoadvisory.tw',
    'scoped:https://www.dingyaoadvisory.tw',
]

for site_url in site_formats:
    try:
        sites = service.sites().list().execute()
        print(f'Sites for {site_url}: {json.dumps(sites, indent=2)[:500]}')
        break
    except Exception as e:
        print(f'Site list error ({site_url}): {str(e)[:200]}')

# Try submitting sitemap with different format
for site_url in site_formats:
    try:
        result = service.sitemaps().submit(
            siteUrl=site_url,
            feedpath='https://dingyaoadvisory.tw/sitemap.xml'
        ).execute()
        print(f'Sitemap OK with {site_url}')
        break
    except Exception as e:
        print(f'Sitemap error ({site_url}): {str(e)[:200]}')

print('DONE')
