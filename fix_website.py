#!/usr/bin/env python3
"""
DingYao Advisory Website Auto-Repair Script
Fixes: Font Awesome integrity typo, English navbar links/text, English footer LINE CTA
"""
import os
import re

def fix_file_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    modified = False

    # ===== 1. Font Awesome integrity link typo =====
    # Missing closing " after the hash
    wrong_fa = 'integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA== crossorigin="anonymous"'
    correct_fa = 'integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous"'
    if wrong_fa in content:
        content = content.replace(wrong_fa, correct_fa)
        modified = True

    # Also handle the same typo with different spacing
    wrong_fa2 = 'integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl\\+Vegovlnee1c9QX4TctnWMn13TZye\\+giMm8e2LwA== crossorigin="anonymous"'
    if wrong_fa2 in content:
        content = content.replace(wrong_fa2, correct_fa)
        modified = True

    filename = os.path.basename(filepath)
    is_en_file = '-en.html' in filename

    if is_en_file:
        # ===== 2. English Navbar: fix links and text =====
        # Fix logo link
        old_logo = 'href="https://dingyaoadvisory.tw" class="nav-logo"'
        new_logo = 'href="/index-en" class="nav-logo"'
        if old_logo in content:
            content = content.replace(old_logo, new_logo)
            modified = True

        # Fix nav links: href paths + display text
        nav_fixes = [
            # (old_href, new_href, old_text_pattern, new_text)
            ('/partners', '/partners-en', None, None),
            ('/platform', '/platform-en', None, None),
            ('/education', '/education-en', None, None),
            ('/retirement', '/retirement-en', None, None),
            ('/residency', '/residency-en', None, None),
            ('/assets', '/assets-en', None, None),
            ('/tour', '/tour-en', None, None),
            ('/blog', '/blog-en', None, None),
            ('/consultation', '/consultation-en', None, None),
        ]

        # First pass: fix href paths
        for old_href, new_href, _, _ in nav_fixes:
            # Match href="/partners" (with possible trailing quote or >)
            pattern = re.escape(old_href) + r'(?=")'
            if re.search(pattern, content):
                content = re.sub(pattern, new_href, content)
                modified = True

        # Second pass: fix display text for English nav links
        text_fixes = {
            'Partners': 'Strategic Partners',
            'Digital Platform': 'Platform',
            'Digital Services': 'Platform',
            'Education': 'Education & Study Abroad',
            'Retirement': 'Retirement Living',
            'Residency': 'Residency Planning',
            'Featured Assets': 'Featured Assets',  # already correct
            'Assets': 'Featured Assets',
            'Tours': 'Business Tours',
            'Tour': 'Business Tours',
            'Insights': 'DYA Insights',
            'Book a Consultation': 'Book Now',
        }

        # Find nav-links div and fix text inside
        nav_match = re.search(r'(<div class="nav-links"[^>]*>)(.*?)(</div>\s*</div>\s*<button class="nav-toggle)', content, re.DOTALL)
        if nav_match:
            nav_inner = nav_match.group(2)
            new_nav_inner = nav_inner
            for old_text, new_text in text_fixes.items():
                # Match >OldText</a> but not if already has new text
                pattern = r'>' + re.escape(old_text) + r'</a>'
                # Only replace if the new text isn't already there
                if re.search(pattern, new_nav_inner) and old_text != new_text:
                    new_nav_inner = re.sub(pattern, f'>{new_text}</a>', new_nav_inner)
            
            if new_nav_inner != nav_inner:
                content = content[:nav_match.start(2)] + new_nav_inner + content[nav_match.end(2):]
                modified = True

        # Fix lang switcher: EN should be active on English pages
        # Find lang switcher div
        lang_pattern = r'(<div class="nav-lang"[^>]*>)\s*<a href="#"([^>]*)>TW</a><span>/</span><a href="#"([^>]*)>EN</a>\s*</div>'
        lang_replacement = r'\1<a href="#" class="">TW</a><span>/</span><a href="#" class="active">EN</a>'
        if re.search(lang_pattern, content):
            content = re.sub(lang_pattern, lang_replacement, content)
            modified = True

        # ===== 3. English Footer: Add LINE CTA =====
        if 'lin.ee/Z6pyU1S' not in content and '<footer' in content:
            # Find the contact list items and add LINE CTA after them
            contact_pattern = r'(<li><a href="mailto:info@dingyaoadvisory\.tw"><i class="fas fa-envelope"[^>]*></i>\s*info@dingyaoadvisory\.tw</a></li>\s*</ul>)'
            line_cta_block = r'\1\n        <div class="footer-line-cta">\n          <a href="https://lin.ee/Z6pyU1S" target="_blank" rel="noopener">\n            <i class="fab fa-line"></i>\n            <span>Join Our LINE Official Account<br><small>Get Your Exclusive Investment Assessment</small></span>\n          </a>\n        </div>'
            if re.search(contact_pattern, content):
                content = re.sub(contact_pattern, line_cta_block, content)
                modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed: {filepath}")
        return True
    return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, 'dist')
    
    if not os.path.isdir(dist_dir):
        print(f"❌ dist directory not found at {dist_dir}")
        return

    fixed_count = 0
    total_count = 0
    
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            if file.endswith('.html'):
                total_count += 1
                filepath = os.path.join(root, file)
                if fix_file_content(filepath):
                    fixed_count += 1

    print(f"\n{'='*50}")
    print(f"Total HTML files scanned: {total_count}")
    print(f"Files modified: {fixed_count}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
