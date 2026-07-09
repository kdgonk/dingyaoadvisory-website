#!/usr/bin/env python3
"""Fix remaining /xxx/en patterns in -en.html files (JSON-LD, footer links, etc.)"""

import os
import re
import glob

DIST = "/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist"

def fix_remaining_patterns(filepath):
    """Fix remaining /xxx/en patterns in -en.html files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Fix JSON-LD url: "url": "https://dingyaoadvisory.tw/xxx/en" -> "url": "https://dingyaoadvisory.tw/xxx-en"
    content, count = re.subn(
        r'("url": "https://dingyaoadvisory\.tw/[^/"]+)/en"',
        r'\1-en"',
        content
    )
    if count:
        changed = True
        print(f"  JSON-LD url fixed ({count}): {filepath}")
    
    # Fix footer links like /assets/en -> /assets-en, /education/en -> /education-en, etc.
    # These are in the footer "Core Services" section
    footer_links = [
        '/assets/en', '/education/en', '/retirement/en', 
        '/residency/en', '/platform/en', '/tour/en',
        '/privacy/en', '/terms/en'
    ]
    for old_link in footer_links:
        new_link = old_link.replace('/en', '-en')
        if old_link in content:
            content = content.replace(old_link, new_link)
            changed = True
            print(f"  Footer link fixed: {old_link} -> {new_link} in {filepath}")
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def main():
    print("=== Fixing remaining /xxx/en patterns in -en.html files ===")
    fixed = []
    
    # Main -en.html files
    for f in os.listdir(DIST):
        if f.endswith('-en.html'):
            filepath = os.path.join(DIST, f)
            if fix_remaining_patterns(filepath):
                fixed.append(filepath)
    
    # Blog -en.html files
    blog_dir = os.path.join(DIST, 'blog')
    if os.path.isdir(blog_dir):
        for f in os.listdir(blog_dir):
            if f.endswith('-en.html'):
                filepath = os.path.join(blog_dir, f)
                if fix_remaining_patterns(filepath):
                    fixed.append(filepath)
    
    print(f"\nFixed remaining patterns in {len(fixed)} files")

if __name__ == '__main__':
    main()
