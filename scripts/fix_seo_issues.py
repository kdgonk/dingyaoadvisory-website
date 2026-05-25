#!/usr/bin/env python3
"""
Fix SEO issues in the generated HTML files:
1. Remove .html from canonical and hreflang URLs in blog articles
2. Remove .html URLs from sitemap
"""

import os
import re
from pathlib import Path

DIST_DIR = Path('/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist')

def fix_blog_article(filepath):
    """Fix canonical/hreflang URLs in blog article HTML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix canonical: /blog/slug.html -> /blog/slug
    content = re.sub(
        r'href="https://dingyaoadvisory\.tw/blog/([^"]+)\.html"',
        r'href="https://dingyaoadvisory.tw/blog/\1"',
        content
    )
    
    # Fix hreflang patterns
    content = re.sub(
        r'hreflang="zh-TW" href="https://dingyaoadvisory\.tw/blog/([^"]+)\.html"',
        r'hreflang="zh-TW" href="https://dingyaoadvisory.tw/blog/\1"',
        content
    )
    content = re.sub(
        r'hreflang="en" href="https://dingyaoadvisory\.tw/blog/([^"]+)\.html"',
        r'hreflang="en" href="https://dingyaoadvisory.tw/blog/\1"',
        content
    )
    content = re.sub(
        r'hreflang="x-default" href="https://dingyaoadvisory\.tw/blog/([^"]+)\.html"',
        r'hreflang="x-default" href="https://dingyaoadvisory.tw/blog/\1"',
        content
    )
    
    # Fix og:url
    content = re.sub(
        r'property="og:url" content="https://dingyaoadvisory\.tw/blog/([^"]+)\.html"',
        r'property="og:url" content="https://dingyaoadvisory.tw/blog/\1"',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_sitemap(filepath):
    """Remove .html URLs from sitemap."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove entire URL entries containing .html
    # Pattern matches from <url> to </url> if it contains .html
    content = re.sub(
        r'<url>\s*\n\s*<loc>https://dingyaoadvisory\.tw/blog/[^<]+\.html</loc>.*?</url>\s*\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 Fixing SEO issues...")
    
    # Fix blog articles
    blog_dir = DIST_DIR / 'blog'
    fixed_count = 0
    
    for html_file in blog_dir.glob('*.html'):
        if html_file.name == 'blog-template.html':
            continue
        if fix_blog_article(html_file):
            fixed_count += 1
            print(f"  ✅ Fixed: {html_file.name}")
    
    print(f"\n📝 Fixed {fixed_count} blog articles")
    
    # Fix sitemap
    sitemap_file = DIST_DIR / 'sitemap.xml'
    if sitemap_file.exists():
        if fix_sitemap(sitemap_file):
            print(f"  ✅ Fixed sitemap.xml")
        else:
            print("  ℹ️ No changes needed in sitemap.xml")
    
    print("\n✨ SEO fix complete!")

if __name__ == '__main__':
    main()