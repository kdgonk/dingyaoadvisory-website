#!/usr/bin/env python3
"""
Fix canonical URLs for English articles - ensure they end with -en.
Also fix hreflang EN URLs.
"""
import re
import os

BLOG_DIR = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/blog"

for f in sorted(os.listdir(BLOG_DIR)):
    if not f.endswith('-en.html'):
        continue
    
    filepath = os.path.join(BLOG_DIR, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    modified = False
    
    # Fix canonical URL
    m = re.search(r'<link\s+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content)
    if m:
        url = m.group(1)
        # If it doesn't end with -en, add it
        if not url.endswith('-en'):
            # Remove trailing slash if present
            url = url.rstrip('/')
            new_url = url + '-en'
            content = content.replace(f'href="{url}"', f'href="{new_url}"')
            modified = True
            print(f'{f}: Fixed canonical: {url} -> {new_url}')
    
    # Fix hreflang EN URL
    m = re.search(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=["\']en["\'][^>]*href=["\']([^"\']+)["\']', content)
    if m:
        url = m.group(1)
        if not url.endswith('-en'):
            url = url.rstrip('/')
            new_url = url + '-en'
            # Use a more specific replacement
            old_tag = f'hreflang="en" href="{m.group(1)}"'
            new_tag = f'hreflang="en" href="{new_url}"'
            content = content.replace(old_tag, new_tag)
            modified = True
            print(f'{f}: Fixed hreflang EN: {m.group(1)} -> {new_url}')
    
    # Fix hreflang x-default URL
    m = re.search(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=["\']x-default["\'][^>]*href=["\']([^"\']+)["\']', content)
    if m:
        url = m.group(1)
        if url.endswith('-en'):
            new_url = url[:-3]
            old_tag = f'hreflang="x-default" href="{url}"'
            new_tag = f'hreflang="x-default" href="{new_url}"'
            content = content.replace(old_tag, new_tag)
            modified = True
            print(f'{f}: Fixed hreflang x-default: {url} -> {new_url}')
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f'  Saved {f}')

print("\nDone fixing canonical/hreflang URLs")
