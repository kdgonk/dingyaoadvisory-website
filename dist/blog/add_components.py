#!/usr/bin/env python3
"""Add hero image section, language switcher JS, and cookie consent banner to blog articles."""

import os
import re

BLOG_DIR = "/Users/dingyao/.openclaw/workspace/dingyaoadvisory-website/dist/blog"

# Files that already have the components (skip these)
ALREADY_DONE = {
    "garlicke-bousfield-legal-guide.html",
    "standard-bank-money-market.html",
    "stellenbosch-retirement-living.html",
    "south-africa-pr-guide.html",
    "taiwan-parents-choosing-south-africa-private-schools.html",
    "cape-town-property-outlook-2026.html",
    "south-africa-march-and-march-protests.html",
    "blog-template.html",
}

# CSS to add
HERO_CSS = """
/* ===== ARTICLE HERO ===== */
.article-hero {
  position: relative;
  height: 50vh;
  min-height: 400px;
  overflow: hidden;
}
.article-hero .hero-bg-img {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  z-index: 0;
}
.article-hero .hero-overlay {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: linear-gradient(180deg, rgba(10,14,23,0.3) 0%, rgba(10,14,23,0.8) 100%);
  z-index: 1;
}
.article-hero .container {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  align-items: flex-end;
  padding-bottom: 40px;
}
"""

COOKIE_CSS = """
.cookie-consent {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: rgba(10,14,23,0.95);
  backdrop-filter: blur(10px);
  padding: 16px 24px;
  display: flex; align-items: center; justify-content: center;
  gap: 16px; flex-wrap: wrap;
  z-index: 9999;
  border-top: 1px solid rgba(201,168,76,0.1);
}
.cookie-consent p { font-size: 0.85rem; color: #F5F0E8AA; margin: 0; }
.cookie-consent a { color: #C9A84C; text-decoration: underline; }
.cookie-consent button {
  background: #C9A84C; color: #0A0E17;
  border: none; padding: 8px 24px; border-radius: 4px;
  font-weight: 600; cursor: pointer; white-space: nowrap;
}
"""

LANG_SWITCHER_JS = """
// Language switcher
(function(){
  var path = window.location.pathname;
  var tw = document.getElementById('langTw');
  var en = document.getElementById('langEn');
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
  } else {
    tw.classList.add('active');
    en.classList.remove('active');
  }
})();
"""

COOKIE_HTML = """
<div class="cookie-consent" id="cookieConsent">
  <p>本網站使用 cookies 提升您的使用體驗。繼續瀏覽即表示您同意我們的 <a href="/privacy">隱私權政策</a> 與 <a href="/terms">服務條款</a>。</p>
  <button onclick="document.getElementById('cookieConsent').style.display='none'">接受</button>
</div>
"""


def get_all_files():
    """Get all non-English, non-template HTML files in the blog directory."""
    files = []
    for f in os.listdir(BLOG_DIR):
        if not f.endswith(".html"):
            continue
        if f.endswith("-en.html"):
            continue
        if f == "blog-template.html":
            continue
        if f in ALREADY_DONE:
            continue
        full_path = os.path.join(BLOG_DIR, f)
        if os.path.isfile(full_path):
            files.append(f)
    return sorted(files)


def find_insertion_point(content):
    """
    Find where to insert the hero section.
    The structure is:
      <nav class="navbar" ...>...</nav>  (first navbar)
      <div class="fixed w-full z-50...">...<nav>...</nav></div>  (second navbar)
      <section class="relative pt-32...">  (article header)
    
    We want to insert the hero section right before the article header <section>.
    """
    # Find the article header section - it starts with <section class="relative pt-32
    # or similar pattern
    patterns = [
        r'<section\s+class="relative\s+pt-32',
        r'<section\s+class="relative\s+pt-24',
        r'<section\s+class="relative\s+pt-20',
        r'<section\s+class="relative\s+pt-16',
        r'<section\s+class="relative\s+pt-10',
    ]
    
    for pat in patterns:
        m = re.search(pat, content)
        if m:
            return m.start()
    
    # Fallback: find the last </nav> before <section
    # Find all </nav> positions
    nav_ends = [m.start() for m in re.finditer(r'</nav>', content)]
    if nav_ends:
        # Find the last </nav> that's before a <section
        last_nav = nav_ends[-1]
        return last_nav + len('</nav>')
    
    return -1


def process_file(filename):
    """Process a single file, adding all 3 components."""
    filepath = os.path.join(BLOG_DIR, filename)
    basename = os.path.splitext(filename)[0]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False

    # 1. Add hero image section
    if 'article-hero' not in content:
        insert_pos = find_insertion_point(content)
        if insert_pos == -1:
            print(f"  SKIP: Could not find insertion point in {filename}")
            return False
        
        hero_html = f"""
<!-- ARTICLE HERO -->
<div class="article-hero">
  <img src="https://assets.dingyaoadvisory.tw/blog/images/{basename}-hero.webp" alt="" class="hero-bg-img" loading="lazy">
  <div class="hero-overlay"></div>
</div>

"""
        content = content[:insert_pos] + hero_html + content[insert_pos:]
        modified = True
        print(f"  Added hero section")

    # 2. Add CSS for hero and cookie consent
    if '/* ===== ARTICLE HERO ===== */' not in content:
        style_close = content.rfind('</style>')
        if style_close != -1:
            content = content[:style_close] + HERO_CSS + content[style_close:]
            modified = True
            print(f"  Added hero CSS")
    
    if '.cookie-consent' not in content:
        style_close = content.rfind('</style>')
        if style_close != -1:
            content = content[:style_close] + COOKIE_CSS + content[style_close:]
            modified = True
            print(f"  Added cookie CSS")

    # 3. Update nav-lang div to add IDs
    old_lang = '<div class="nav-lang"><a href="#" class="active">TW</a><span>/</span><a href="#">EN</a></div>'
    new_lang = '<div class="nav-lang"><a href="#" class="active" id="langTw">TW</a><span>/</span><a href="#" id="langEn">EN</a></div>'
    
    if old_lang in content:
        content = content.replace(old_lang, new_lang)
        modified = True
        print(f"  Updated nav-lang with IDs")
    elif 'id="langTw"' not in content:
        print(f"  WARNING: Could not find nav-lang pattern in {filename}")

    # 4. Add language switcher JS before the last </script> before </body>
    if '// Language switcher' not in content:
        body_end = content.rfind('</body>')
        if body_end != -1:
            last_script_end = content.rfind('</script>', 0, body_end)
            if last_script_end != -1:
                insert_pos = last_script_end + len('</script>')
                content = content[:insert_pos] + '\n' + LANG_SWITCHER_JS + content[insert_pos:]
                modified = True
                print(f"  Added language switcher JS")

    # 5. Add cookie consent HTML before </body>
    if 'id="cookieConsent"' not in content:
        body_end = content.rfind('</body>')
        if body_end != -1:
            content = content[:body_end] + COOKIE_HTML + '\n' + content[body_end:]
            modified = True
            print(f"  Added cookie consent HTML")

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  -> Saved {filename}")
        return True
    else:
        print(f"  -> No changes needed for {filename}")
        return False


def main():
    files = get_all_files()
    print(f"Found {len(files)} files to process")
    
    modified_count = 0
    for f in files:
        print(f"\nProcessing: {f}")
        try:
            if process_file(f):
                modified_count += 1
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Done! {modified_count} of {len(files)} files modified.")


if __name__ == "__main__":
    main()
