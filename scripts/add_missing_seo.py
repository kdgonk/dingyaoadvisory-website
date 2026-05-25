#!/usr/bin/env python3
"""
Add missing canonical and hreflang tags to HTML files.
"""

import os
import re
from pathlib import Path

DIST_DIR = Path('/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist')

# Pages that need canonical/hreflang and their variants
# Format: (file, url_path, has_en_version)
PAGES_CONFIG = {
    # Main pages
    'card.html': ('card', False),  # No English version
    'project-constantia.html': ('project-constantia', True),
    'project-constantia-en.html': ('project-constantia-en', True),
    'project-durbanville.html': ('project-durbanville', True),
    'project-durbanville-en.html': ('project-durbanville-en', True),
    'project-stellenbosch.html': ('project-stellenbosch', True),
    'project-stellenbosch-en.html': ('project-stellenbosch-en', True),
    'project-phase1.html': ('project-phase1', False),
    'project-phase1-new.html': ('project-phase1-new', False),
    'project-phase1-old.html': ('project-phase1-old', False),
    'sandile-mbeko.html': ('sandile-mbeko', True),
    'sandile-mbeko-en.html': ('sandile-mbeko-en', True),
}

def generate_seo_tags(filename, url_path, has_en_version):
    """Generate canonical and hreflang tags."""
    
    if filename.endswith('-en.html'):
        # English version
        base_path = url_path.replace('-en', '')
        return f'''<!-- SEO Canonical & hreflang -->
<link rel="canonical" href="https://dingyaoadvisory.tw/{base_path}-en"/>
<link rel="alternate" hreflang="zh-TW" href="https://dingyaoadvisory.tw/{base_path}"/>
<link rel="alternate" hreflang="en" href="https://dingyaoadvisory.tw/{base_path}-en"/>
<link rel="alternate" hreflang="x-default" href="https://dingyaoadvisory.tw/{base_path}"/>'''
    elif has_en_version:
        # Chinese version with English counterpart
        return f'''<!-- SEO Canonical & hreflang -->
<link rel="canonical" href="https://dingyaoadvisory.tw/{url_path}"/>
<link rel="alternate" hreflang="zh-TW" href="https://dingyaoadvisory.tw/{url_path}"/>
<link rel="alternate" hreflang="en" href="https://dingyaoadvisory.tw/{url_path}-en"/>
<link rel="alternate" hreflang="x-default" href="https://dingyaoadvisory.tw/{url_path}"/>'''
    else:
        # Chinese only version
        return f'''<!-- SEO Canonical & hreflang -->
<link rel="canonical" href="https://dingyaoadvisory.tw/{url_path}"/>
<link rel="alternate" hreflang="zh-TW" href="https://dingyaoadvisory.tw/{url_path}"/>
<link rel="alternate" hreflang="x-default" href="https://dingyaoadvisory.tw/{url_path}"/>'''

def fix_html_file(filename):
    """Add or fix canonical/hreflang in HTML file."""
    filepath = DIST_DIR / filename
    
    if not filepath.exists():
        return False, "File not found"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has canonical tag
    if '<link rel="canonical"' in content:
        return False, "Already has canonical"
    
    # Get config
    if filename not in PAGES_CONFIG:
        return False, "No config for this file"
    
    url_path, has_en = PAGES_CONFIG[filename]
    seo_tags = generate_seo_tags(filename, url_path, has_en)
    
    # Find insertion point - after </title> or after last <meta> in <head>
    # Try after </title> first
    insertion_patterns = [
        (r'(</title>\s*\n)', r'\1' + seo_tags + '\n'),
        (r'(<meta[^>]*content="summary_large_image"[^>]*/>\s*\n)', r'\1' + seo_tags + '\n'),
        (r'(<meta[^>]*name="twitter:image"[^>]*/>\s*\n)', r'\1' + seo_tags + '\n'),
    ]
    
    for pattern, replacement in insertion_patterns:
        new_content = re.sub(pattern, replacement, content, count=1)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Added SEO tags"
    
    # Fallback: add after <head>
    new_content = content.replace('<head>', '<head>\n' + seo_tags, 1)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "Added SEO tags (fallback)"
    
    return False, "Could not find insertion point"

def main():
    print("🔧 Adding missing canonical & hreflang tags...\n")
    
    fixed_count = 0
    for filename in PAGES_CONFIG:
        result, message = fix_html_file(filename)
        if result:
            print(f"  ✅ {filename}: {message}")
            fixed_count += 1
        else:
            print(f"  ℹ️ {filename}: {message}")
    
    print(f"\n✨ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()