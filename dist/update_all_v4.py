#!/usr/bin/env python3
"""
全站英文頁面選單文字統一 + Logo 連結修正 (v4 - robust)
"""
import os
import re

DIST = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist"

# ============================================================
# 1. 英文選單文字替換表
# ============================================================
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

# ============================================================
# 2. Logo 加上 id="navLogo"
# ============================================================
LOGO_PATTERN = r'(<a href="https://dingyaoadvisory\.tw" class="nav-logo")>'
LOGO_REPLACEMENT = r'\1 id="navLogo">'

# ============================================================
# 3. 新的 script 區塊
# ============================================================
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
    """Replace menu text only inside nav-links divs"""
    if not is_english:
        return content
    
    # Find nav-links sections
    pattern = r'(<div class="nav-links"[^>]*>)(.*?)(</div>\s*<button class="nav-toggle)'
    
    def replace_in_section(match):
        open_tag = match.group(1)
        inner = match.group(2)
        close_tag = match.group(3)
        for old, new in EN_MENU_REPLACEMENTS:
            inner = inner.replace(old, new)
        return open_tag + inner + close_tag
    
    return re.sub(pattern, replace_in_section, content, flags=re.DOTALL)


def add_logo_id(content):
    """Add id='navLogo' to the nav-logo anchor"""
    return re.sub(LOGO_PATTERN, LOGO_REPLACEMENT, content)


def update_script(content):
    """Replace old language switcher script with new one that includes logo logic.
    Uses line-by-line state machine for robustness."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a <script> that is the lang switcher
        if '<script>' in line:
            # Look ahead to see if this is the lang switcher script
            # It should have (function(){ and var path = window.location.pathname
            lookahead = '\n'.join(lines[i:i+10])
            if '(function(){' in lookahead and 'var path = window.location.pathname' in lookahead and 'var tw = document.getElementById' in lookahead:
                # This is the lang switcher script - skip until </script>
                i += 1
                while i < len(lines):
                    if '</script>' in lines[i]:
                        # Replace with new script
                        new_lines.append(NEW_SCRIPT)
                        i += 1
                        break
                    i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def process_file(filepath, is_english):
    """Process a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Replace menu text in nav-links (English only)
    content = replace_in_nav_links(content, is_english)
    
    # Step 2: Add id="navLogo" to logo anchor
    content = add_logo_id(content)
    
    # Step 3: Update script block
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
