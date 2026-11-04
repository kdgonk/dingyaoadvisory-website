#!/usr/bin/env python3
"""
Convert English blog articles: remove Tailwind, use correct dark theme template.
"""
from __future__ import annotations  # Python 3.9：讓 str | None 型別註解可運作

import re
import json
import os

BLOG_DIR = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist/blog"

# ── 版面標題規則（唯一權威：scripts/normalize_zh_blog_titles.py，改動需兩邊同步）──
BRAND = "｜鼎曜國際顧問"
MAX_TITLE = 60
MAX_CORE = MAX_TITLE - len(BRAND)
BRAND_RE = re.compile(
    r"\s*[｜|]?\s*"
    r"(?:鼎曜國際顧問(?:\s*DingYao(?:\s*Advisory)?)?"
    r"|鼎曜國際顯問|鼎昰國際顯問|鼎曜國際"
    r"|DingYao(?:\s*Advisory)?"
    r"|鼎曜)"
    r"\s*$"
)


def ensure_page_title(raw):
    """把任意 title 正規化成『內容｜鼎曜國際顧問』，超過 60 字回傳 None（不靜默截斷）。"""
    t = (raw or "").strip()
    if not t:
        return None
    m = BRAND_RE.search(t)
    core = t[: m.start()].rstrip(" ｜|") if m and m.start() > 0 else t
    title = core + BRAND
    return title if len(title) <= MAX_TITLE else None


# ── EN title 防呆（2026-11-06 土星人要求）──
# 事故樣本：south-africa-remote-work-visa-cape-town-property-demand-2026-en
#   完整句 'How South Africa's Remote Work Visa is Driving Cape Town Property Demand…'
#   被切成 'How South Africa | DingYao'（26 字元）—— apostrophe 處截斷，句子不完整。
EN_MIN_TITLE = 30
EN_TAIL_STOPWORDS = {
    # 冠詞／介系詞／連接詞／be 動詞／疑問詞結尾 = 句子被切斷
    "the", "a", "an", "of", "and", "or", "for", "to", "in", "on", "at", "by",
    "with", "from", "as", "is", "are", "was", "were", "be", "been", "being",
    "how", "what", "why", "when", "where", "which", "who", "that", "this",
    "these", "those", "your", "our", "their", "its", "his", "her", "not",
    "into", "than", "then", "if", "so", "but", "about", "over", "under", "vs",
    "versus", "per", "via",
}


def validate_en_title(page_title: str) -> str | None:
    """EN title 防呆。回傳錯誤訊息；None 表示通過。

    抓的是「句子被切斷」而不是「不好看」：
      - 空白、>65 字元
      - 全長 <30 → 幾乎必然是截斷（事故樣本 26）
      - 主體最後一詞是功能詞（the/of/for/how…）→ 句子沒寫完
      - 含中日韓字元 → 中文標題誤入英文頁
    """
    t = (page_title or "").strip()
    if not t:
        return "EN title 空白"
    if len(t) > 65:
        return f"EN title 超過 65 字元（{len(t)}）：{t!r}"
    if len(t) < EN_MIN_TITLE:
        return f"EN title 過短（{len(t)}<{EN_MIN_TITLE}），疑似被截斷：{t!r}"
    main = t.split("|")[0].strip()
    words = re.findall(r"[A-Za-z][A-Za-z'’\-]*", main)
    if words and words[-1].lower() in EN_TAIL_STOPWORDS:
        return f"EN title 結尾是功能詞（{words[-1]!r}），句子被切斷：{t!r}"
    if re.search(r"[\u3400-\u9fff]", t):
        return f"EN title 含中日韓字元：{t!r}"
    return None


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

    # ── 語言屬性：一律依「檔名」判定，不繼承模板 ─────────────────────
    #    模板本體是中文（lang="zh-TW"），產英文頁時必須覆蓋成 lang="en"。
    is_en = filename.endswith('-en.html')
    html_lang = 'en' if is_en else 'zh-TW'
    og_locale = 'en_US' if is_en else 'zh_TW'
    slug = filename.replace('-en.html', '').replace('.html', '')
    # 站上慣例：中文＝裸 slug、英文＝slug + '-en'。hreflang 一律由 slug 推導，
    # 不信任來源檔的 canonical（來源可能是錯的，且 canonical 只代表自己）。
    en_url = f'https://dingyaoadvisory.tw/blog/{slug}-en'
    zh_url = f'https://dingyaoadvisory.tw/blog/{slug}'
    
    if not body_content or len(body_content) < 50:
        print(f"  WARNING: Body content too short ({len(body_content) if body_content else 0} chars)")
        return None
    
    # Read the template from file
    template_path = os.path.join(BLOG_DIR, 'article-template.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # ── title 四處同步（2026-11-04 事故：品牌尾綴被寫成「｜鼎曜」、og/twitter 無品牌）──
    #    ZH：一律「內容｜鼎曜國際顧問」且全長 ≤60；EN：不套中文品牌，僅驗長度
    if is_en:
        page_title = (og_title or title or "").strip()
        err = validate_en_title(page_title)
        if err:
            print(f"  ERROR: {err}")
            return None
    else:
        page_title = ensure_page_title(og_title or title)
        if page_title is None:
            print(f"  ERROR: title 超過 {MAX_TITLE} 字，請縮短後重跑：{og_title or title}")
            return None
    json_ld = re.sub(
        r'("headline"\s*:\s*")[^"]*(")',
        lambda m: m.group(1) + page_title + m.group(2),
        json_ld,
    )

    output = template.replace('{page_title}', page_title)
    output = output.replace('{seo_meta}', seo_meta)
    output = output.replace('{canonical_url}', canonical)
    output = output.replace('{zh_url}', zh_url)
    output = output.replace('{en_url}', en_url)
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

    # ── 用檔名判定的語言覆蓋模板的 lang / og:locale ────────────────
    output = re.sub(r'(<html[^>]*\blang=")[^"]*(")',
                    lambda m: m.group(1) + html_lang + m.group(2), output, count=1)
    output = re.sub(r'(<meta\s+property="og:locale"\s+content=")[^"]*(")',
                    lambda m: m.group(1) + og_locale + m.group(2), output, count=1)

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
