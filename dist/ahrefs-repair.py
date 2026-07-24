"""
Ahrefs Site Audit Repair Script — P0/P1/P2 Fixes
Run from dist/ directory.

Fixes:
P0: Missing title/meta description on English articles, hreflang pointing to wrong URL
P1: Multiple H1 tags, missing H1, hreflang reciprocity, og:url mismatch
P2: Missing canonical/hreflang on blog/images pages
"""

import os, re

html_files = []
for root, dirs, files in os.walk('.'):
    # Skip __pycache__
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

stats = {
    'title_fixed': 0,
    'desc_fixed': 0,
    'hreflang_fixed': 0,
    'h1_fixed': 0,
    'h1_added': 0,
    'canonical_fixed': 0,
    'og_url_fixed': 0,
}

for fp in sorted(html_files):
    with open(fp, 'r') as fh:
        content = fh.read()
    original = content
    
    is_en = '-en.html' in fp
    is_zh = not is_en
    is_blog_article = fp.startswith('./blog/') and not fp.startswith('./blog/images/')
    is_blog_images = fp.startswith('./blog/images/')
    is_main_page = not fp.startswith('./blog/')
    filename = os.path.basename(fp)
    
    # ============================================================
    # P0: Fix missing <title> tag
    # ============================================================
    if '<title>' not in content or '</title>' not in content:
        # Try to get title from og:title
        og_title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', content)
        if og_title_match:
            og_title = og_title_match.group(1)
            # Add title tag after <head> or after charset
            if is_en:
                # English articles — add DingYao brand
                title_tag = f'<title>{og_title} | DingYao Advisory</title>'
            else:
                title_tag = f'<title>{og_title} | 鼎曜國際顧問</title>'
            
            # Insert after <head>
            content = content.replace('<head>', f'<head>\n{title_tag}')
            stats['title_fixed'] += 1
    
    # ============================================================
    # P0: Fix missing <meta name="description">
    # ============================================================
    if 'name="description"' not in content and "name='description'" not in content:
        # Try og:description
        og_desc_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', content)
        if og_desc_match:
            desc = og_desc_match.group(1)
            if len(desc) > 155:
                desc = desc[:152] + '...'
            desc_tag = f'<meta name="description" content="{desc}">'
            # Insert after title
            content = content.replace('</title>', f'</title>\n{desc_tag}')
            stats['desc_fixed'] += 1
    
    # ============================================================
    # P0/P1: Fix hreflang on English pages (zh-TW pointing to EN URL)
    # ============================================================
    if is_en and is_blog_article:
        # Current: hreflang zh-TW points to EN URL
        # Fix: point to ZH URL
        # Get the slug from canonical
        canon_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
        if canon_match:
            en_url = canon_match.group(1)
            zh_url = en_url.replace('-en', '')
            
            # Fix hreflang zh-TW pointing to wrong URL
            # Pattern: <link rel="alternate" hreflang="zh-TW" href="...-en">
            wrong_zh = re.search(r'<link\s+rel="alternate"\s+hreflang="zh-TW"\s+href="([^"]*-en)"', content)
            if wrong_zh:
                content = content.replace(wrong_zh.group(0), f'<link rel="alternate" hreflang="zh-TW" href="{zh_url}">')
                stats['hreflang_fixed'] += 1
    
    # ============================================================
    # P1: Fix multiple H1 tags — keep only the first one
    # ============================================================
    h1_tags = re.findall(r'<h1[^>]*>.*?</h1>', content, re.DOTALL)
    if len(h1_tags) > 1:
        # Keep the first H1, convert rest to H2
        first_h1 = h1_tags[0]
        for extra_h1 in h1_tags[1:]:
            # Convert <h1...> to <h2...> and </h1> to </h2>
            fixed = extra_h1.replace('<h1', '<h2').replace('</h1>', '</h2>')
            content = content.replace(extra_h1, fixed, 1)
        stats['h1_fixed'] += 1
    
    # ============================================================
    # P1: Add missing H1 tag
    # ============================================================
    if '<h1' not in content and not is_blog_images:
        # Try to get title
        title_match = re.search(r'<title>(.*?)</title>', content)
        if title_match:
            title_text = title_match.group(1)
            # Remove brand suffix
            h1_text = re.sub(r'\s*\|\s*(DingYao Advisory|鼎曜國際顧問)$', '', title_text).strip()
            # Insert H1 after <body> or at start of body content
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                body_end = body_match.end()
                # Find a good insertion point — after the body tag and any noscript
                insert_point = body_end
                after_body = content[body_end:]
                noscript_end = after_body.find('</noscript>')
                if noscript_end != -1:
                    insert_point = body_end + noscript_end + len('</noscript>')
                
                h1_html = f'\n<h1 class="sr-only">{h1_text}</h1>\n'
                content = content[:insert_point] + h1_html + content[insert_point:]
                stats['h1_added'] += 1
    
    # ============================================================
    # P2: Fix blog/images pages — add canonical + hreflang
    # ============================================================
    if is_blog_images:
        if 'rel="canonical"' not in content:
            slug = filename.replace('.html', '')
            canon_url = f'https://dingyaoadvisory.tw/blog/images/{slug}'
            content = content.replace('</title>', f'</title>\n<link rel="canonical" href="{canon_url}">')
            stats['canonical_fixed'] += 1
        
        if 'hreflang' not in content:
            # Add noindex since these are image pages
            if 'name="robots"' not in content:
                content = content.replace('</title>', f'</title>\n<meta name="robots" content="noindex, nofollow">')
    
    # ============================================================
    # P1: Fix og:url mismatch with canonical
    # ============================================================
    if is_blog_article:
        canon_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
        og_url_match = re.search(r'<meta\s+property="og:url"\s+content="([^"]*)"', content)
        if canon_match and og_url_match:
            canon_url = canon_match.group(1)
            og_url = og_url_match.group(1)
            if canon_url != og_url:
                # Fix og:url to match canonical
                old_og = og_url_match.group(0)
                new_og = f'<meta property="og:url" content="{canon_url}">'
                content = content.replace(old_og, new_og)
                stats['og_url_fixed'] += 1
    
    # Write if changed
    if content != original:
        with open(fp, 'w') as fh:
            fh.write(content)
        print(f"✅ {fp}")

print(f"\n=== Repair Summary ===")
print(f"Title tags added: {stats['title_fixed']}")
print(f"Meta descriptions added: {stats['desc_fixed']}")
print(f"Hreflang zh-TW URLs fixed: {stats['hreflang_fixed']}")
print(f"Multiple H1 → H2 converted: {stats['h1_fixed']}")
print(f"H1 tags added (sr-only): {stats['h1_added']}")
print(f"Canonical added to images: {stats['canonical_fixed']}")
print(f"og:url mismatches fixed: {stats['og_url_fixed']}")
