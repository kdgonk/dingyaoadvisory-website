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

# ── Submit to IndexNow (Bing) ──
import urllib.request

INDEXNOW_KEY = '3576af12bca967c7a277faa91d3e0c03'
INDEXNOW_KEY_LOCATION = f'https://dingyaoadvisory.tw/{INDEXNOW_KEY}.txt'
INDEXNOW_HOST = 'dingyaoadvisory.tw'
INDEXNOW_API = 'https://api.indexnow.org/indexnow'

# Read all URLs from sitemap
import re
sitemap_path = '/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/sitemap.xml'
try:
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        sitemap_content = f.read()
    all_urls = re.findall(r'<loc>(https?://[^<]+)</loc>', sitemap_content)

    payload = {
        'host': INDEXNOW_HOST,
        'key': INDEXNOW_KEY,
        'keyLocation': INDEXNOW_KEY_LOCATION,
        'urlList': all_urls
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        INDEXNOW_API,
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        status = resp.status
        body = resp.read().decode('utf-8', errors='replace')
        print(f'IndexNow HTTP {status} — {len(all_urls)} URLs submitted to Bing')
        if body:
            print(f'   Body: {body[:200]}')
except urllib.error.HTTPError as e:
    print(f'IndexNow HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}')
except Exception as e:
    print(f'IndexNow error (non-blocking): {e}')

print('DONE')
