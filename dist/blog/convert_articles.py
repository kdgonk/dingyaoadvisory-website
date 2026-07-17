#!/usr/bin/env python3
"""
Convert English blog articles: remove Tailwind, use correct dark theme template.
"""
import re
import json
import os

BLOG_DIR = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/blog"


def remove_section(raw, start_pos):
    """Remove a <section>...</section> block handling nested sections."""
    if raw[start_pos:start_pos+9] != '<section ' and raw[start_pos:start_pos+9] != '<section>':
        return raw
    depth = 0
    end = start_pos
    for i in range(start_pos, len(raw)):
        if raw[i] == '<':
            if raw[i:i+9] == '<section ' or raw[i:i+9] == '<section>':
                depth += 1
            elif raw[i:i+10] == '</section>':
                depth -= 1
                if depth == 0:
                    end = i + 10
                    break
    return raw[:start_pos] + raw[end:]


def extract_body_content(content):
    """Extract the main article body from the original HTML.
    
    Strategy: Find the article content section (py-16 bg-white with article-content/prose),
    extract it, and strip all Tailwind classes.
    """
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
    if not body_match:
        return ''
    
    raw = body_match.group(1)
    
    # Remove the first navbar (dark theme one)
    raw = re.sub(r'<!-- NAVBAR -->.*?</nav>', '', raw, flags=re.DOTALL)
    
    # Remove GTM noscript
    raw = re.sub(r'<noscript>.*?</noscript>', '', raw, flags=re.DOTALL)
    
    # Remove the second nav (Tailwind one)
    raw = re.sub(r'<div[^>]*class=["\'][^"\']*fixed[^"\']*z-50[^"\']*["\'][^>]*>.*?</nav>\s*</div>', '', raw, flags=re.DOTALL)
    
    # Remove breadcrumb navs
    raw = re.sub(r'<nav[^>]*aria-label=["\']Breadcrumb["\'][^>]*>.*?</nav>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<nav[^>]*class=["\'][^"\']*bg-white[^"\']*border-b[^"\']*["\'][^>]*>.*?</nav>', '', raw, flags=re.DOTALL)
    
    # Remove hero section
    hero_match = re.search(r'<section[^>]*class=["\'][^"\']*relative[^"\']*pt-32[^>]*>', raw, re.IGNORECASE)
    if hero_match:
        raw = remove_section(raw, hero_match.start())
    
    # Remove hero-gradient CTA sections
    while True:
        m = re.search(r'<section[^>]*class=["\'][^"\']*hero-gradient[^>]*>', raw, re.IGNORECASE)
        if not m:
            break
        raw = remove_section(raw, m.start())
    
    # Remove bg-gray-50 sections (Related Articles)
    while True:
        m = re.search(r'<section[^>]*class=["\'][^"\']*bg-gray-50[^>]*>', raw, re.IGNORECASE)
        if not m:
            break
        raw = remove_section(raw, m.start())
    
    # Remove footer
    raw = re.sub(r'<footer[^>]*class=["\']footer["\'][^>]*>.*?</footer>', '', raw, flags=re.DOTALL)
    
    # Remove scripts
    raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL)
    
    # Remove cookie consent divs
    raw = re.sub(r'<div[^>]*class=["\'][^"\']*cookie[^>]*>.*?</div>', '', raw, flags=re.DOTALL)
    
    # Remove remaining empty sections
    raw = re.sub(r'<section[^>]*>\s*</section>', '', raw, flags=re.DOTALL)
    
    # Remove all class attributes (they contain Tailwind classes)
    raw = re.sub(r'\s+class=["\'][^"\']*["\']', '', raw)
    
    # Remove style attributes
    raw = re.sub(r'\s+style=["\'][^"\']*["\']', '', raw)
    
    # Clean up excessive whitespace
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    
    return raw.strip()


def extract_hero_image(content):
    patterns = [
        r'<meta\s+property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        r'<img[^>]*src=["\']([^"\']+hero[^"\']+)["\']',
        r'<source[^>]*srcset=["\']([^"\']+hero[^"\']+)["\']',
    ]
    for p in patterns:
        m = re.search(p, content, re.IGNORECASE)
        if m:
            return m.group(1)
    return ''


def extract_hero_alt(content):
    m = re.search(r'<img[^>]*alt=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return m.group(1) if m else ''


def extract_title(content):
    m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ''


def extract_og_title(content):
    m = re.search(r'<meta\s+property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return m.group(1) if m else extract_title(content)


def extract_og_description(content):
    m = re.search(r'<meta\s+property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return m.group(1) if m else ''


def extract_og_image(content):
    m = re.search(r'<meta\s+property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return m.group(1) if m else extract_hero_image(content)


def extract_canonical(content):
    m = re.search(r'<link\s+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return m.group(1) if m else ''


def extract_json_ld(content):
    blocks = re.findall(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL)
    
    article_ld = None
    faq_ld = None
    
    for block in blocks:
        if '"@type": "Article"' in block or '"@type":"Article"' in block:
            try:
                data = json.loads(block)
                data['author'] = {"@type": "Person", "name": "Scott Huang"}
                if 'publisher' in data:
                    data['publisher'] = {"@type": "Organization", "name": "DingYao Advisory", "url": "https://dingyaoadvisory.tw"}
                article_ld = json.dumps(data, indent=2)
            except:
                article_ld = block
        elif '"@type": "FAQPage"' in block or '"@type":"FAQPage"' in block:
            faq_ld = block
    
    result = ''
    if article_ld:
        result += f'<script type="application/ld+json">\n{article_ld}\n</script>\n'
    if faq_ld:
        result += f'<script type="application/ld+json">\n{faq_ld}\n</script>\n'
    return result


def extract_article_date(content):
    m = re.search(r'<meta\s+property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if m:
        date_str = m.group(1)
        date_str = date_str.replace('T08:00:00+08:00', '')
        date_str = date_str.replace('T00:00:00+00:00', '')
        return date_str.strip()
    return ''


def extract_read_time(content):
    m = re.search(r'(\d+)\s*min\s*read', content, re.IGNORECASE)
    if m:
        return m.group(0)
    m = re.search(r'閱讀時間\s*(\d+)', content)
    if m:
        return m.group(1) + ' min read'
    return '5 min read'


def extract_category(content):
    m = re.search(r'<meta\s+property=["\']article:section["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'<span[^>]*class=["\'][^"\']*rounded-full[^"\']*["\'][^>]*>([^<]+)</span>', content)
    if m:
        return m.group(1).strip()
    return 'Property Investment'


def extract_zh_url(content, filename):
    m = re.search(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=["\']zh-TW["\'][^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if m:
        return m.group(1)
    base = filename.replace('-en.html', '')
    return f'https://dingyaoadvisory.tw/blog/{base}'


def extract_seo_meta(content):
    metas = []
    for m in re.finditer(r'<meta\s+[^>]*name=["\'](author|robots)["\'][^>]*>', content, re.IGNORECASE):
        metas.append(m.group(0))
    for m in re.finditer(r'<meta\s+[^>]*name=["\']geo\.\w+["\'][^>]*>', content, re.IGNORECASE):
        metas.append(m.group(0))
    return '\n'.join(metas)


def build_output(filename, content):
    """Build the new HTML using the template structure."""
    
    # Extract all metadata
    title = extract_title(content)
    og_title = extract_og_title(content)
    og_description = extract_og_description(content)
    og_image = extract_og_image(content)
    canonical = extract_canonical(content)
    zh_url = extract_zh_url(content, filename)
    json_ld = extract_json_ld(content)
    seo_meta = extract_seo_meta(content)
    hero_image = extract_hero_image(content)
    hero_alt = extract_hero_alt(content)
    article_date = extract_article_date(content)
    read_time = extract_read_time(content)
    category = extract_category(content)
    body_content = extract_body_content(content)
    
    if not body_content or len(body_content) < 50:
        print(f"  WARNING: Body content too short ({len(body_content) if body_content else 0} chars)")
        return None
    
    # Read the template from file
    template_path = os.path.join(BLOG_DIR, 'article-template.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    output = template.replace('{seo_meta}', seo_meta)
    output = output.replace('{canonical_url}', canonical)
    output = output.replace('{zh_url}', zh_url)
    output = output.replace('{og_title}', og_title)
    output = output.replace('{og_description}', og_description)
    output = output.replace('{og_image}', og_image)
    output = output.replace('{json_ld}', json_ld)
    output = output.replace('{hero_image}', hero_image or og_image)
    output = output.replace('{hero_alt}', hero_alt or og_title)
    output = output.replace('{article_tag}', category)
    output = output.replace('{article_title}', title)
    output = output.replace('{article_date}', article_date)
    output = output.replace('{article_read_time}', read_time)
    output = output.replace('{article_category}', category)
    output = output.replace('{article_content}', body_content)
    
    return output


def convert_article(filename):
    """Convert a single article from Tailwind to dark theme."""
    filepath = os.path.join(BLOG_DIR, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'cdn.tailwindcss.com' not in content:
        print(f"  SKIP: No Tailwind found")
        return False
    
    print(f"  Processing...")
    
    output = build_output(filename, content)
    if output is None:
        return False
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"  DONE")
    return True


def main():
    files = []
    for f in sorted(os.listdir(BLOG_DIR)):
        if f.endswith('-en.html'):
            filepath = os.path.join(BLOG_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as fh:
                file_content = fh.read()
            if 'cdn.tailwindcss.com' in file_content:
                files.append(f)
    
    print(f"Found {len(files)} articles with Tailwind to convert")
    
    success = 0
    fail = 0
    
    for i, filename in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {filename}")
        try:
            if convert_article(filename):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
    
    print(f"\n\n=== SUMMARY ===")
    print(f"Total: {len(files)}")
    print(f"Success: {success}")
    print(f"Failed: {fail}")


if __name__ == '__main__':
    main()
