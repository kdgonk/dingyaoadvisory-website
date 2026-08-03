#!/usr/bin/env python3
"""Fix ALL remaining Chinese nav text in English files."""
import os

def fix_all_chinese_nav(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    modified = False

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
        ('立即預約諮詢', 'Book Now'),
        ('專欄觀點', 'DYA Insights'),
        ('專欄', 'DYA Insights'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
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
                if fix_all_chinese_nav(fp):
                    print(f"  ✅ Fixed: {f}")
                    fixed += 1
    print(f"\nTotal English files with Chinese nav text fixed: {fixed}")

if __name__ == '__main__':
    main()
