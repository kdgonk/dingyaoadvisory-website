#!/usr/bin/env python3
"""
全站英文頁面選單文字統一 + Logo 連結修正
"""
import os
import re

DIST = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist"

# ============================================================
# 1. 英文選單文字替換表 (只改 nav-links 裡面的文字)
# ============================================================
EN_MENU_REPLACEMENTS = [
    # 注意順序：先長後短，避免部分匹配
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
LOGO_PATTERN = r'(<a href="https://dingyaoadvisory\.tw" class="nav-logo">)'
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

# ============================================================
# 4. 舊 script 區塊的 regex (flexible matching)
# ============================================================
# Match the old script block - from <script> through })();</script>
# We need to be careful to match the right one
OLD_SCRIPT_PATTERN = r'<script>\s*\(function\(\)\{\s*var path = window\.location\.pathname;\s*var tw = document\.getElementById\(\'langTw\'\);\s*var en = document\.getElementById\(\'langEn\'\);(.*?)\}\(\)\);\s*</script>'

def replace_in_nav_links(content, is_english):
    """Replace menu text only inside nav-links divs"""
    if not is_english:
        return content
    
    # Find all nav-links divs and replace text inside them
    # We use a regex to find content between <div class="nav-links"...> and </div>
    # But we need to be careful about nested divs
    
    # Simpler approach: replace text only within nav-links sections
    # Use a marker-based approach
    result = content
    
    # Find nav-links sections
    pattern = r'(<div class="nav-links"[^>]*>)(.*?)(</div>\s*<button class="nav-toggle)'
    
    def replace_in_section(match):
        open_tag = match.group(1)
        inner = match.group(2)
        close_tag = match.group(3)
        
        # Apply all replacements
        for old, new in EN_MENU_REPLACEMENTS:
            inner = inner.replace(old, new)
        
        return open_tag + inner + close_tag
    
    result = re.sub(pattern, replace_in_section, result, flags=re.DOTALL)
    
    return result


def add_logo_id(content):
    """Add id='navLogo' to the nav-logo anchor"""
    result = re.sub(LOGO_PATTERN, LOGO_REPLACEMENT, content)
    return result


def update_script(content):
    """Replace old language switcher script with new one that includes logo logic"""
    # Match the old script block
    # Pattern: <script>\n(function(){\n  var path = window.location.pathname;\n  var tw = ...\n  ...\n})();\n</script>
    old_script_re = r'<script>\s*\n\s*\(function\(\\)\{\s*\n\s*var path = window\.location\.pathname;\s*\n\s*var tw = document\.getElementById\(\'langTw\'\);\s*\n\s*var en = document\.getElementById\(\'langEn\'\);(?:\s*\n\s*//[^\n]*)?\s*\n\s*if \(path\.endsWith\(\'-en\'\)\) \{\s*\n\s*tw\.href = path\.slice\(0, -3\) \|\| \'/\';\s*\n\s*\} else \{\s*\n\s*tw\.href = path;\s*\n\s*\}\s*\n\s*//[^\n]*\s*\n\s*if \(path === \'/\'\) \{\s*\n\s*en\.href = \'/index-en\';\s*\n\s*\} else if \(path\.endsWith\(\'-en\'\)\) \{\s*\n\s*en\.href = path;\s*\n\s*\} else \{\s*\n\s*en\.href = path \+ \'-en\';\s*\n\s*\}\s*\n\s*//[^\n]*\s*\n\s*if \(path\.endsWith\(\'-en\'\)\) \{\s*\n\s*en\.classList\.add\(\'active\'\);\s*\n\s*tw\.classList\.remove\(\'active\'\);\s*\n\s*\} else \{\s*\n\s*tw\.classList\.add\(\'active\'\);\s*\n\s*en\.classList\.remove\(\'active\'\);\s*\n\s*\}\s*\n\s*\}\(\)\);\s*\n\s*</script>'
    
    # Simpler approach: find the script block by looking for the specific pattern
    # The script is always right after the lang switcher div
    result = content
    
    # Find the old script block
    # Pattern: <script>\n(function(){\n  var path = window.location.pathname;\n  var tw = document.getElementById('langTw');\n  var en = document.getElementById('langEn');\n  ...\n})();\n</script>
    
    # Use a more flexible regex
    pattern = r'(<script>\s*\n\s*\(function\(\)\{\s*\n\s*var path = window\.location\.pathname;\s*\n\s*var tw = document\.getElementById\(\'langTw\'\);\s*\n\s*var en = document\.getElementById\(\'langEn\'\);(?:\s*\n\s*[^<]*?)+\s*\n\s*\}\(\)\);\s*\n\s*</script>)'
    
    # Actually, let's use a simpler approach - find the exact script block
    # The script starts with <script> and ends with </script>, and contains the specific variables
    
    lines = result.split('\n')
    new_lines = []
    i = 0
    in_script_block = False
    script_start = -1
    
    while i < len(lines):
        line = lines[i]
        
        # Detect start of the lang switcher script
        if '<script>' in line and 'var path = window.location.pathname' in lines[i+1] if i+1 < len(lines) else False:
            in_script_block = True
            script_start = i
            # Skip until we find the closing </script>
            while i < len(lines):
                if '</script>' in lines[i]:
                    # Replace with new script
                    new_lines.append(NEW_SCRIPT)
                    in_script_block = False
                    i += 1
                    break
                i += 1
            continue
        
        # Also detect if this line starts the script
        if '<script>' in line and i+1 < len(lines) and 'var path' in lines[i+1]:
            in_script_block = True
            while i < len(lines):
                if '</script>' in lines[i]:
                    new_lines.append(NEW_SCRIPT)
                    in_script_block = False
                    i += 1
                    break
                i += 1
            continue
        
        if not in_script_block:
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
    # Collect all HTML files
    all_files = []
    
    # Root dist files
    for f in os.listdir(DIST):
        if f.endswith('.html') and f != 'temp.html' and f != 'card.html' and f != '404.html':
            all_files.append(os.path.join(DIST, f))
    
    # Blog files
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
                print(f"  MODIFIED: {filepath} (english={is_english})")
            else:
                print(f"  SKIPPED (no changes): {filepath}")
        except Exception as e:
            print(f"  ERROR: {filepath}: {e}")
    
    print(f"\nModified {modified} files")


if __name__ == '__main__':
    main()
