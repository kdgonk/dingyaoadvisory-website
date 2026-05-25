#!/usr/bin/env python3
"""
Complete SEO fix for dingyaoadvisory.tw:
1. Remove -zh files (duplicate content, non-standard naming)
2. Update blog.html links from -zh.html to .html
3. Remove -zh entries from sitemap
4. Fix any remaining canonical issues
"""

import os
import re
from pathlib import Path

DIST_DIR = Path('/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist')

def fix_blog_html_links():
    """Update blog.html to link to correct URLs (no -zh suffix for Chinese)."""
    blog_html = DIST_DIR / 'blog.html'
    
    with open(blog_html, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix links from -zh.html to .html
    # Pattern: blog/slug-zh.html -> blog/slug.html
    content = re.sub(
        r'blog/([a-zA-Z0-9-]+)-zh\.html',
        r'blog/\1.html',
        content
    )
    
    # Also fix the hreflang alternates if any
    content = re.sub(
        r'href="https://dingyaoadvisory\.tw/blog/([a-zA-Z0-9-]+)-zh"',
        r'href="https://dingyaoadvisory.tw/blog/\1"',
        content
    )
    
    if content != original:
        with open(blog_html, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Fixed blog.html links")
        return True
    return False

def fix_blog_en_html_links():
    """Update blog-en.html if it has similar issues."""
    blog_en_html = DIST_DIR / 'blog-en.html'
    
    if not blog_en_html.exists():
        return False
    
    with open(blog_en_html, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix links from -zh.html to .html
    content = re.sub(
        r'blog/([a-zA-Z0-9-]+)-zh\.html',
        r'blog/\1.html',
        content
    )
    
    if content != original:
        with open(blog_en_html, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Fixed blog-en.html links")
        return True
    return False

def remove_zh_from_sitemap():
    """Remove -zh URL entries from sitemap."""
    sitemap_file = DIST_DIR / 'sitemap.xml'
    
    with open(sitemap_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove entire URL entries containing -zh
    content = re.sub(
        r'<url>\s*\n\s*<loc>https://dingyaoadvisory\.tw/blog/[^<]+-zh</loc>.*?</url>\s*\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    if content != original:
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Removed -zh URLs from sitemap.xml")
        return True
    return False

def delete_zh_files():
    """Delete the -zh.html files as they are duplicates."""
    blog_dir = DIST_DIR / 'blog'
    deleted = []
    
    for zh_file in blog_dir.glob('*-zh.html'):
        # Get the base name without -zh
        base_name = zh_file.name.replace('-zh.html', '.html')
        base_file = blog_dir / base_name
        
        # Only delete if the base file exists
        if base_file.exists():
            zh_file.unlink()
            deleted.append(zh_file.name)
            print(f"  🗑️ Deleted duplicate: {zh_file.name}")
        else:
            print(f"  ⚠️ Keeping {zh_file.name} (no base version exists)")
    
    return deleted

def main():
    print("🔧 Complete SEO fix for -zh issues...")
    
    # 1. Fix blog.html links
    print("\n1️⃣ Fixing blog.html links...")
    fix_blog_html_links()
    
    # 2. Fix blog-en.html links
    print("\n2️⃣ Fixing blog-en.html links...")
    fix_blog_en_html_links()
    
    # 3. Remove -zh URLs from sitemap
    print("\n3️⃣ Cleaning sitemap.xml...")
    remove_zh_from_sitemap()
    
    # 4. Delete duplicate -zh files
    print("\n4️⃣ Removing duplicate -zh files...")
    deleted = delete_zh_files()
    
    print(f"\n✨ Complete! Deleted {len(deleted)} duplicate files")

if __name__ == '__main__':
    main()