#!/usr/bin/env python3
"""
Step 3b: Fix English blog article navbars that still have Chinese text.
Only replaces text inside nav-links div.
"""
import os
import re

def fix_blog_nav(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    modified = False

    # Only process files that have Chinese nav text
    if '戰略夥伴' not in content:
        return False

    # Find nav-links div - look for the pattern
    # <div class="nav-links" id="navLinks"> ... </div>\n    <button class="nav-toggle"
    nav_match = re.search(
        r'(<div class="nav-links[^>]*>)(.*?)(</div>\s*\n\s*<button class="nav-toggle)',
        content, re.DOTALL
    )
    if not nav_match:
        return False

    nav_inner = nav_match.group(2)
    new_inner = nav_inner

    replacements = [
        ('戰略夥伴', 'Strategic Partners'),
        ('數位服務', 'Platform'),
        ('教育留學', 'Education & Study Abroad'),
        ('退休生活', 'Retirement Living'),
        ('身分規劃', 'Residency Planning'),
        ('精選資產', 'Featured Assets'),
        ('商業考察', 'Business Tours'),
        ('鼎曜觀點', 'DYA Insights'),
        ('預約諮詢', 'Book Now'),
    ]
    
    for old, new in replacements:
        if old in new_inner:
            new_inner = new_inner.replace(old, new)
    
    if new_inner != nav_inner:
        content = content[:nav_match.start(2)] + new_inner + content[nav_match.end(2):]
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base = '/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist'
    fixed = 0
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith('-en.html'):
                fp = os.path.join(root, f)
                if fix_blog_nav(fp):
                    print(f"  ✅ Fixed: {f}")
                    fixed += 1
    print(f"\nTotal English files with Chinese nav text fixed: {fixed}")

if __name__ == '__main__':
    main()
