#!/usr/bin/env python3
"""
Titan 專用：增量維護 dist/sitemap.xml。

規則：
- 以現有 sitemap.xml 為基礎，保留所有現有格式、priority、hreflang 風格。
- 掃描 dist/*.html 與 dist/blog/*.html，找出應該被索引的 URL。
- 新增「檔案存在但 sitemap 缺失」的條目。
- 移除「sitemap 中有但實體檔案不存在」的條目。
- 可選：對指定 slug 更新 lastmod 為今天，提示 Google 重新爬取。

排除：
- robots meta 含 noindex
- 404.html、project-phase1-old.html、blog-template.html、article-template.html
- 檔名含 -demo、-old、template、temp

首頁特殊對應：
- index.html -> /
- index-en.html -> /index-en
"""
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent / 'dist'
SITEMAP = ROOT / 'sitemap.xml'
DOMAIN = 'https://dingyaoadvisory.tw'

EXCLUDE_PREFIXES = ('404', 'project-phase1-old', 'blog-template', 'article-template')
EXCLUDE_SUBSTR = ('-demo', '-old', 'template', 'temp')

def should_index(path: Path) -> bool:
    name = path.name
    if name.startswith(EXCLUDE_PREFIXES):
        return False
    if any(s in name for s in EXCLUDE_SUBSTR):
        return False
    try:
        c = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False
    if re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', c, re.I):
        return False
    return True

def path_to_rel(path: Path) -> str:
    """把 dist/*.html 或 dist/blog/*.html 轉成 URL path"""
    rel = path.relative_to(ROOT).with_suffix('').as_posix()
    if rel == 'index':
        return '/'
    return '/' + rel

def get_expected_urls() -> set:
    """根據 dist/ 實際檔案產出應該在 sitemap 中的 URL 集合"""
    urls = set()
    for f in sorted(ROOT.glob('*.html')):
        if should_index(f):
            urls.add(DOMAIN + path_to_rel(f))
    blog_dir = ROOT / 'blog'
    if blog_dir.exists():
        for f in sorted(blog_dir.glob('*.html')):
            if should_index(f):
                urls.add(DOMAIN + path_to_rel(f))
    return urls

def get_lastmod_from_file(path: Path) -> str:
    c = path.read_text(encoding='utf-8', errors='ignore')
    for key in ('datePublished', 'dateModified'):
        m = re.search(rf'"{key}"\s*:\s*"([^"]+)"', c)
        if m:
            return m.group(1)[:10]
    return datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d')

def rel_to_path(rel: str) -> Path:
    """把 URL path 轉回 dist/ 下的檔案路徑。'/' -> index.html"""
    rel = rel.rstrip('/')
    if rel == '':
        return ROOT / 'index.html'
    return ROOT / (rel.lstrip('/') + '.html')

def find_block_end(content: str, start: int) -> int:
    """從 <url> 開始找到對應的 </url> 結尾"""
    end = content.find('</url>', start)
    if end == -1:
        return -1
    return end + len('</url>')

def clone_nearest_block(content: str, url: str) -> str:
    """複製 sitemap 中最近的 <url> 區塊，修改 loc/lastmod/hreflang 為目標 URL"""
    # 找一個 blog 或根頁面條目當模板
    blocks = re.findall(r'\s*<url>.*?</url>\s*', content, re.S)
    if not blocks:
        raise ValueError('No existing <url> block found in sitemap.xml')
    template = blocks[-1]  # 用尾端條目格式
    
    rel = urlparse(url).path
    is_root = not rel.startswith('/blog/')
    is_en = rel.endswith('-en')
    
    if rel == '/':
        zh_rel = '/'
        en_rel = '/index-en'
    elif rel == '/index-en':
        zh_rel = '/'
        en_rel = '/index-en'
    elif is_en:
        zh_rel = rel[:-3]
        en_rel = rel
    else:
        zh_rel = rel
        en_rel = rel + '-en'
    
    path = rel_to_path(rel)
    lastmod = get_lastmod_from_file(path)
    
    # 替換 loc
    block = re.sub(r'<loc>[^<]+</loc>', f'<loc>{url}</loc>', template, count=1)
    # 替換 lastmod
    block = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{lastmod}</lastmod>', block, count=1)
    
    # 更新 hreflang
    def repl_hreflang(m):
        lang = m.group(1)
        if lang == 'zh-TW':
            return f'hreflang="zh-TW" href="{DOMAIN}{zh_rel}"'
        elif lang == 'en':
            if rel_to_path(en_rel).exists():
                return f'hreflang="en" href="{DOMAIN}{en_rel}"'
            else:
                return '__REMOVE_EN_HREFLANG__'
        elif lang == 'x-default':
            return f'hreflang="x-default" href="{DOMAIN}{zh_rel}"'
        return m.group(0)
    
    block = re.sub(r'hreflang="(zh-TW|en|x-default)" href="[^"]+"', repl_hreflang, block)
    block = block.replace('\n        <xhtml:link rel="alternate" hreflang="__REMOVE_EN_HREFLANG__"/>\n', '\n')
    block = block.replace('        <xhtml:link rel="alternate" hreflang="__REMOVE_EN_HREFLANG__"/>\n', '')
    block = block.replace('<xhtml:link rel="alternate" hreflang="__REMOVE_EN_HREFLANG__"/>\n', '')
    
    # 若 priority 是根頁面但複製到 blog，可能需要調整，但保留原格式即可
    return block

def main(bump_slugs=None):
    bump_slugs = bump_slugs or []
    content = SITEMAP.read_text(encoding='utf-8')
    expected = get_expected_urls()
    
    # 解析現有 sitemap 的 URL 區塊
    blocks = []
    for m in re.finditer(r'\s*(<url>.*?</url>)\s*', content, re.S):
        block = m.group(1)
        loc_match = re.search(r'<loc>([^<]+)</loc>', block)
        if not loc_match:
            continue
        loc = loc_match.group(1)
        blocks.append((loc, block, m.start(), m.end()))
    
    existing_urls = {loc for loc, _, _, _ in blocks}
    missing = sorted(expected - existing_urls)
    to_remove = sorted(existing_urls - expected)
    
    print(f'Expected URLs: {len(expected)}')
    print(f'Existing URLs: {len(existing_urls)}')
    print(f'Missing to add: {len(missing)}')
    for u in missing:
        print('  +', u)
    print(f'Orphan to remove: {len(to_remove)}')
    for u in to_remove:
        print('  -', u)
    
    # 移除不存在檔案的區塊
    for loc, _, start, end in reversed(blocks):
        if loc in to_remove:
            content = content[:start] + content[end:]
    
    # 新增缺失區塊（塞到 </urlset> 之前）
    if missing:
        insert_pos = content.rfind('</urlset>')
        new_blocks = ''.join(clone_nearest_block(content, url) for url in missing)
        content = content[:insert_pos] + new_blocks + content[insert_pos:]
    
    # 更新指定 slug 的 lastmod
    today = datetime.now().strftime('%Y-%m-%d')
    for slug in bump_slugs:
        for suffix in ('', '-en'):
            url = f'{DOMAIN}/blog/{slug}{suffix}'
            if url in expected:
                content = re.sub(
                    rf'(<loc>{re.escape(url)}</loc>\s*)<lastmod>[^<]+</lastmod>',
                    rf'\1<lastmod>{today}</lastmod>',
                    content,
                    count=1
                )
                print(f'  ~ bumped lastmod: {url} -> {today}')
    
    SITEMAP.write_text(content, encoding='utf-8')
    
    # 驗證
    final_urls = set(re.findall(r'<loc>([^<]+)</loc>', content))
    final_missing = expected - final_urls
    final_orphan = final_urls - expected
    print(f'\n✅ sitemap.xml updated: {len(final_urls)} URLs')
    if final_missing:
        print('Still missing:', final_missing)
    if final_orphan:
        print('Still orphan:', final_orphan)

if __name__ == '__main__':
    bump = sys.argv[1:] if len(sys.argv) > 1 else []
    main(bump_slugs=bump)
