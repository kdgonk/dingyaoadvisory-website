#!/usr/bin/env python3
"""Fix language switcher JS from /en/ directory-based to -en suffix-based in all HTML files under dist/"""

import os
import re
import glob

DIST = "/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist"

OLD_JS = """<script>
(function(){
  var path = window.location.pathname;
  var isEn = path.indexOf('/en') !== -1 || path.indexOf('/en/') !== -1;
  var tw = document.getElementById('langTw');
  var en = document.getElementById('langEn');
  if(isEn){
    tw.href = path.replace(/\\/en(\\/|$)/, '$1') || '/';
    en.classList.add('active');
    tw.classList.remove('active');
  } else {
    en.href = path.replace(/\\/$/, '') + '/en';
  }
})();
</script>"""

NEW_JS = """<script>
(function(){
  var path = window.location.pathname;
  var tw = document.getElementById('langTw');
  var en = document.getElementById('langEn');
  // If current path ends with -en, TW goes to non-en version
  if (path.endsWith('-en')) {
    tw.href = path.slice(0, -3) || '/';
  } else if (path === '/en') {
    tw.href = '/';
  } else {
    tw.href = path;
  }
  // If current path is / or doesn't have -en, EN goes to -en version
  if (path === '/') {
    en.href = '/en';
  } else if (path.endsWith('-en')) {
    en.href = path;
  } else {
    en.href = path + '-en';
  }
  // Set active class based on -en suffix
  if (path.endsWith('-en') || path === '/en') {
    en.classList.add('active');
    tw.classList.remove('active');
  } else {
    tw.classList.add('active');
    en.classList.remove('active');
  }
})();
</script>"""

# Mapping of /en/xxx paths to xxx-en paths for internal links
LINK_MAP = {
    '/en/partners': '/partners-en',
    '/en/platform': '/platform-en',
    '/en/education': '/education-en',
    '/en/retirement': '/retirement-en',
    '/en/residency': '/residency-en',
    '/en/assets': '/assets-en',
    '/en/tour': '/tour-en',
    '/en/blog': '/blog-en',
    '/en/consultation': '/consultation-en',
    '/en/privacy': '/privacy-en',
    '/en/terms': '/terms-en',
    '/en/sandile-mbeko': '/sandile-mbeko-en',
    '/en/project-constantia': '/project-constantia-en',
    '/en/durbanville': '/project-durbanville-en',
    '/en/project-durbanville': '/project-durbanville-en',
    '/en/project-stellenbosch': '/project-stellenbosch-en',
    '/en/project-phase1': '/project-phase1-en',
    '/en/sitemap.xml': '/sitemap.xml',
    '/en/sitemap': '/sitemap',
    '/en/consultation.html': '/consultation-en',
}

# Also handle blog links: /blog/xxx/en -> /blog/xxx-en
# And hreflang/canonical: /en/blog/xxx -> /blog/xxx-en

def fix_js_in_file(filepath):
    """Replace old JS with new JS in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if OLD_JS in content:
        content = content.replace(OLD_JS, NEW_JS)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_internal_links(filepath):
    """Fix /en/xxx links to xxx-en in -en.html files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    for old_link, new_link in LINK_MAP.items():
        if old_link in content:
            content = content.replace(old_link, new_link)
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def fix_hreflang_canonical(filepath):
    """Fix hreflang and canonical URLs in blog -en.html files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Fix canonical: /en/blog/xxx -> /blog/xxx-en
    content, count = re.subn(
        r'(href="https://dingyaoadvisory\.tw)/en/blog/([^"]+)"',
        r'\1/blog/\2-en"',
        content
    )
    if count:
        changed = True
    
    # Fix hreflang en: /en/blog/xxx -> /blog/xxx-en
    content, count = re.subn(
        r'(hreflang="en" href="https://dingyaoadvisory\.tw)/en/blog/([^"]+)"',
        r'\1/blog/\2-en"',
        content
    )
    if count:
        changed = True
    
    # Fix hreflang zh-TW: /blog/xxx -> /blog/xxx (keep as-is, but ensure en points to -en)
    # Fix og:url: /en/blog/xxx -> /blog/xxx-en
    content, count = re.subn(
        r'(property="og:url" content="https://dingyaoadvisory\.tw)/en/blog/([^"]+)"',
        r'\1/blog/\2-en"',
        content
    )
    if count:
        changed = True
    
    # Fix @id in JSON-LD: /en/blog/xxx -> /blog/xxx-en
    content, count = re.subn(
        r'("@id": "https://dingyaoadvisory\.tw)/en/blog/([^"]+)"',
        r'\1/blog/\2-en"',
        content
    )
    if count:
        changed = True
    
    # Fix item in JSON-LD: /en/blog -> /blog-en
    content, count = re.subn(
        r'("item": "https://dingyaoadvisory\.tw)/en/blog"',
        r'\1/blog-en"',
        content
    )
    if count:
        changed = True
    
    # Fix breadcrumb items: /en/blog/xxx -> /blog/xxx-en
    content, count = re.subn(
        r'("item": "https://dingyaoadvisory\.tw)/en/blog/([^"]+)"',
        r'\1/blog/\2-en"',
        content
    )
    if count:
        changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def fix_blog_internal_links(filepath):
    """Fix /en/xxx links in blog -en.html files (same as main -en files)."""
    return fix_internal_links(filepath)

def fix_hreflang_main(filepath):
    """Fix hreflang tags in main -en.html files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Fix hreflang: /xxx/en -> /xxx-en
    # Pattern: href="https://dingyaoadvisory.tw/xxx/en"
    content, count = re.subn(
        r'(href="https://dingyaoadvisory\.tw/[^/"]+)/en"',
        r'\1-en"',
        content
    )
    if count:
        changed = True
    
    # Fix canonical: /xxx/en -> /xxx-en
    content, count = re.subn(
        r'(href="https://dingyaoadvisory\.tw/[^/"]+)/en"',
        r'\1-en"',
        content
    )
    if count:
        changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def main():
    # Step 1: Fix JS in all HTML files under dist/
    print("=== Step 1: Fixing language switcher JS ===")
    js_fixed = []
    for root, dirs, files in os.walk(DIST):
        for f in files:
            if f.endswith('.html'):
                filepath = os.path.join(root, f)
                if fix_js_in_file(filepath):
                    js_fixed.append(filepath)
                    print(f"  JS fixed: {filepath}")
    
    print(f"\nJS fixed in {len(js_fixed)} files")
    
    # Step 2: Fix internal links in -en.html files under dist/
    print("\n=== Step 2: Fixing internal links in -en.html files ===")
    links_fixed = []
    for root, dirs, files in os.walk(DIST):
        for f in files:
            if f.endswith('-en.html'):
                filepath = os.path.join(root, f)
                if fix_internal_links(filepath):
                    links_fixed.append(filepath)
                    print(f"  Links fixed: {filepath}")
    
    print(f"\nLinks fixed in {len(links_fixed)} files")
    
    # Step 3: Fix hreflang/canonical in blog -en.html files
    print("\n=== Step 3: Fixing hreflang/canonical in blog -en.html files ===")
    blog_fixed = []
    blog_dir = os.path.join(DIST, 'blog')
    if os.path.isdir(blog_dir):
        for f in os.listdir(blog_dir):
            if f.endswith('-en.html'):
                filepath = os.path.join(blog_dir, f)
                if fix_hreflang_canonical(filepath):
                    blog_fixed.append(filepath)
                    print(f"  Blog hreflang fixed: {filepath}")
    
    print(f"\nBlog hreflang fixed in {len(blog_fixed)} files")
    
    # Step 4: Fix hreflang in main -en.html files
    print("\n=== Step 4: Fixing hreflang in main -en.html files ===")
    main_fixed = []
    for f in os.listdir(DIST):
        if f.endswith('-en.html'):
            filepath = os.path.join(DIST, f)
            if fix_hreflang_main(filepath):
                main_fixed.append(filepath)
                print(f"  Main hreflang fixed: {filepath}")
    
    print(f"\nMain hreflang fixed in {len(main_fixed)} files")
    
    print("\n=== Summary ===")
    print(f"JS fixed: {len(js_fixed)} files")
    print(f"Internal links fixed: {len(links_fixed)} files")
    print(f"Blog hreflang/canonical fixed: {len(blog_fixed)} files")
    print(f"Main hreflang fixed: {len(main_fixed)} files")

if __name__ == '__main__':
    main()
