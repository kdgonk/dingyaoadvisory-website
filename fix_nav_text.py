#!/usr/bin/env python3
"""
Step 3: Fix English navbar display text to standardized names.
Targeted replacement of full anchor tags.
"""
import os

def fix_nav_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    modified = False

    # Replace full anchor tags in nav-links
    # These are specific enough to only match nav links
    replacements = [
        ('<a href="/partners-en">Partners</a>', '<a href="/partners-en">Strategic Partners</a>'),
        ('<a href="/education-en">Education</a>', '<a href="/education-en">Education & Study Abroad</a>'),
        ('<a href="/retirement-en" class="gold">Retirement</a>', '<a href="/retirement-en" class="gold">Retirement Living</a>'),
        ('<a href="/retirement-en">Retirement</a>', '<a href="/retirement-en">Retirement Living</a>'),
        ('<a href="/residency-en">Residency</a>', '<a href="/residency-en">Residency Planning</a>'),
        ('<a href="/assets-en">Assets</a>', '<a href="/assets-en">Featured Assets</a>'),
        ('<a href="/tour-en">Tours</a>', '<a href="/tour-en">Business Tours</a>'),
        ('<a href="/tour-en">Tour</a>', '<a href="/tour-en">Business Tours</a>'),
        ('<a href="/blog-en">Insights</a>', '<a href="/blog-en">DYA Insights</a>'),
        # White-template style navbars
        ('Premium Education Planning', 'Education & Study Abroad'),
        ('Retirement Relocation Solutions', 'Retirement Living'),
        ('Residency & Permanent Residency', 'Residency Planning'),
        ('Digital Asset Platform', 'Platform'),
        ('Business Tours & Site Visits', 'Business Tours'),
        ('DYA Insights & Analysis', 'DYA Insights'),
        ('Book a Consultation', 'Book Now'),
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
                if fix_nav_text(fp):
                    print(f"  ✅ Fixed: {f}")
                    fixed += 1
    print(f"\nTotal English files with nav text fixes: {fixed}")

if __name__ == '__main__':
    main()
