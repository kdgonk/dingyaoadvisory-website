#!/usr/bin/env python3
"""Fix remaining internal /en/ links in blog -en.html files"""

import os
import re

DIST = "/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist"
BLOG_DIR = os.path.join(DIST, 'blog')

def fix_blog_links(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Fix ../en/index.html#contact -> ../index-en.html#contact
    if '../en/index.html#contact' in content:
        content = content.replace('../en/index.html#contact', '../index-en.html#contact')
        changed = True
    
    # Fix ../en/index.html -> ../index-en.html
    if '../en/index.html' in content:
        content = content.replace('../en/index.html', '../index-en.html')
        changed = True
    
    # Fix "item": "https://dingyaoadvisory.tw/en/" -> "item": "https://dingyaoadvisory.tw/"
    if '"item": "https://dingyaoadvisory.tw/en/"' in content:
        content = content.replace('"item": "https://dingyaoadvisory.tw/en/"', '"item": "https://dingyaoadvisory.tw/"')
        changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def main():
    print("=== Fixing remaining internal /en/ links in blog -en.html files ===")
    fixed = []
    for f in os.listdir(BLOG_DIR):
        if f.endswith('-en.html'):
            filepath = os.path.join(BLOG_DIR, f)
            if fix_blog_links(filepath):
                fixed.append(filepath)
                print(f"  Fixed: {filepath}")
    
    print(f"\nFixed {len(fixed)} blog -en.html files")

if __name__ == '__main__':
    main()
