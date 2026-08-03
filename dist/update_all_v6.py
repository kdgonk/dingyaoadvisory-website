#!/usr/bin/env python3
"""
全站英文頁面選單文字統一 + Logo 連結修正 (v6 - handles both navbar types correctly)
"""
import os
import re

DIST = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist"

EN_MENU_REPLACEMENTS = [
    ("Education & Study Abroad", "Education"),
    ("Education & Study", "Education"),
    ("Study Abroad", "Education"),
    ("Strategic Partners", "Partners"),
    ("Digital Services", "Platform"),
    ("Retirement Living", "Retirement"),
    ("Residency Planning", "Residency"),
    ("Featured Assets", "Assets"),
    ("Business Tours", "Tours"),
    ("DingYao Insights", "Insights"),
    ("Book a Consultation", "Book Now"),
    ("Book Consultation", "Book Now"),
]

LOGO_PATTERN = r'(<a href="https://dingyaoadvisory\.tw" class="nav-logo")>'
LOGO_REPLACEMENT = r'\1 id="navLogo">'

NEW_SCRIPT = """<script>
(function(){
  var path = window.location.pathname;
  var tw = document.getElementById('langTw');
  var en = document.getElementById('langEn');
  var logo = document.getElementById('navLogo');

  if (path.endsWith('-en')) {
    tw.href = path.slice(0, -3) || '/';
  } else {
    tw.href = path;
  }
  if (path === '/') {
    en.href = '/index-en';
  } else if (path.endsWith('-en')) {
    en.href = path;
  } else {
    en.href = path + '-en';
  }
  if (path.endsWith('-en')) {
    en.classList.add('active');
    tw.classList.remove('active');
    if (logo) logo.href = '/index-en';
  } else {
    tw.classList.add('active');
    en.classList.remove('active');
    if (logo) logo.href = 'https://dingyaoadvisory.tw';
  }
})();
</script>"""


def replace_in_nav_links(content, is_english):
    """Replace menu text in standard nav-links divs"""
    if not is_english:
        return content
    
    pattern = r'(<div class="nav-links"[^>]*>)(.*?)(</div>\s*<button class="nav-toggle)'
    
    def replace_in_section(match):
        open_tag = match.group(1)
        inner = match.group(2)
        close_tag = match.group(3)
        for old, new in EN_MENU_REPLACEMENTS:
            inner = inner.replace(old, new)
        return open_tag + inner + close_tag
    
    return re.sub(pattern, replace_in_section, content, flags=re.DOTALL)


def replace_in_tailwind_navbar(content, is_english):
    """Replace menu text in old Tailwind-style navbars"""
    if not is_english:
        return content
    
    # The old Tailwind navbar is inside:
    # <div class="fixed w-full z-50 top-4 md:top-6 px-4 pointer-events-none">
    #   <nav class="max-w-7xl mx-auto bg-white/...">
    #     ... links with old text ...
    #   </nav>
    # </div>
    
    # Match the entire Tailwind navbar container
    pattern = r'(<div class="fixed w-full z-50 top-4 md:top-6 px-4 pointer-events-none">\s*<nav class="max-w-7xl mx-auto bg-white[^>]*>)(.*?)(</nav>\s*</div>)'
    
    def replace_in_tailwind(match):
        open_tag = match.group(1)
        inner = match.group(2)
        close_tag = match.group(3)
        for old, new in EN_MENU_REPLACEMENTS:
            inner = inner.replace(old, new)
        return open_tag + inner + close_tag
    
    return re.sub(pattern, replace_in_tailwind, content, flags=re.DOTALL)


def add_logo_id(content):
    """Add id='navLogo' to the nav-logo anchor"""
    return re.sub(LOGO_PATTERN, LOGO_REPLACEMENT, content)


def update_script(content):
    """Replace old language switcher script with new one."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if '<script>' in line:
            lookahead = '\n'.join(lines[i:i+10])
            if ('(function(){' in lookahead and 
                'var path = window.location.pathname' in lookahead and 
                'var tw = document.getElementById' in lookahead):
                i += 1
                while i < len(lines):
                    if '</script>' in lines[i]:
                        new_lines.append(NEW_SCRIPT)
                        i += 1
                        break
                    i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def process_file(filepath, is_english):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Replace menu text in standard nav-links
    content = replace_in_nav_links(content, is_english)
    
    # Step 2: Replace menu text in old Tailwind navbars
    content = replace_in_tailwind_navbar(content, is_english)
    
    # Step 3: Add id="navLogo"
    content = add_logo_id(content)
    
    # Step 4: Update script block
    content = update_script(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    all_files = []
    
    for f in os.listdir(DIST):
        if f.endswith('.html') and f != 'temp.html' and f != 'card.html' and f != '404.html':
            all_files.append(os.path.join(DIST, f))
    
    blog_dir = os.path.join(DIST, 'blog')
    if os.path.isdir(blog_dir):
        for f in os.listdir(blog_dir):
            if f.endswith('.html') and f != 'blog-template.html':
                all_files.append(os.path.join(blog_dir, f))
    
    print(f"Total files to process: {len(all_files)}")
    
    modified = 0
    for filepath in sorted(all_files):
        filename = os.path.basename(filepath)
        is_english = '-en' in filename
        
        try:
            if process_file(filepath, is_english):
                modified += 1
                print(f"  MODIFIED: {filepath}")
        except Exception as e:
            print(f"  ERROR: {filepath}: {e}")
    
    print(f"\nModified {modified} files")


if __name__ == '__main__':
    main()
