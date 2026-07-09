#!/usr/bin/env python3
"""Fix blog -en.html canonical/hreflang URLs: blog-en/xxx -> blog/xxx-en"""

import os
import re

BLOG_DIR = "/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist/blog"

def fix_blog_urls(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Get the filename without extension
    filename = os.path.basename(filepath)
    basename = filename.replace('.html', '')  # e.g. cape-town-property-outlook-2026-en
    
    # Fix canonical: blog-en/xxx -> blog/xxx-en
    pattern = r'(href="https://dingyaoadvisory\.tw)blog-en/([^"]+)"'
    replacement = r'\1blog/' + basename + '"'
    
    new_content, count = re.subn(pattern, replacement, content)
    if count:
        changed = True
        content = new_content
        print(f"  Fixed canonical/hreflang URLs in {filepath}")
    
    # Also fix og:url
    pattern2 = r'(content="https://dingyaoadvisory\.tw)blog-en/([^"]+)"'
    replacement2 = r'\1blog/' + basename + '"'
    
    new_content, count2 = re.subn(pattern2, replacement2, content)
    if count2:
        changed = True
        content = new_content
    
    # Fix @id in JSON-LD
    pattern3 = r'("@id": "https://dingyaoadvisory\.tw)blog-en/([^"]+)"'
    replacement3 = r'\1blog/' + basename + '"'
    
    new_content, count3 = re.subn(pattern3, replacement3, content)
    if count3:
        changed = True
        content = new_content
    
    # Fix item in JSON-LD breadcrumb - blog-en -> blog-en (keep as is, it's the blog listing page)
    # Actually this should be blog-en since the blog listing page is at /blog-en
    pattern4 = r'("item": "https://dingyaoadvisory\.tw)blog-en"'
    replacement4 = r'\1blog-en"'
    
    new_content, count4 = re.subn(pattern4, replacement4, content)
    if count4:
        changed = True
        content = new_content
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def main():
    print("=== Fixing blog -en.html canonical/hreflang URLs ===")
    fixed = []
    for f in os.listdir(BLOG_DIR):
        if f.endswith('-en.html'):
            filepath = os.path.join(BLOG_DIR, f)
            if fix_blog_urls(filepath):
                fixed.append(filepath)
    
    print(f"\nFixed {len(fixed)} blog -en.html files")

if __name__ == '__main__':
    main()
