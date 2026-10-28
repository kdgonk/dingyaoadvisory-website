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

已部署過濾（2026-10-28）：
- 預設對每個候選 URL 做 HEAD，live 非 200（3xx/4xx/5xx）者排除，不寫進 sitemap
  —— 防「dist 有檔但還沒部署」的草稿被送進 sitemap ＋ IndexNow（10-27 valuation 事故）。
- 連線層失敗（ERR）保守視為未知 → 保留，只警告，避免偶發 SSL timeout 誤刪活頁。
- --offline（別名 --no-live）：跳過 live 檢查，供 CI／無網路環境使用。
- 用法：python3 scripts/update_sitemap.py [--offline] [slug1 slug2 ...]（slug = bump lastmod）
"""
import concurrent.futures as cf
import http.client
import re
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent / 'dist'
SITEMAP = ROOT / 'sitemap.xml'
DOMAIN = 'https://dingyaoadvisory.tw'
UA = {'User-Agent': 'Mozilla/5.0 TitanSitemapGen/1.1'}
LIVE_WORKERS = 20
LIVE_RETRIES = 2
LIVE_TIMEOUT = 20

EXCLUDE_PREFIXES = ('404', 'project-phase1-old', 'blog-template', 'article-template')
EXCLUDE_SUBSTR = ('-demo', '-old', 'template', 'temp')

def load_redirect_sources() -> set:
    """dist/_redirects 中「作為 redirect 來源」的 URL path 集合。

    為什麼需要：sitemap 產生器掃 dist/*.html，而被 301 攔截的檔案仍然存在
    → 那些 URL 會一直被收進 sitemap，GSC 報「Page with redirect」
    （2026-10-20 回歸事故：5 個 301 來源被 booking 那次重生 sitemap 帶回來）。
    這裡直接以 _redirects 為唯一真相，避免逐筆 hardcode。
    """
    redirects = ROOT / '_redirects'
    sources = set()
    if not redirects.exists():
        return sources
    for line in redirects.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        src = parts[0]
        # 只看真的會攔截的路徑（帶 301/302/307/308 狀態碼的規則；沒有 status 也視為 redirect）
        if src.startswith('http'):
            continue
        if src.endswith('/*') or '*' in src:
            continue  # splat 規則不逐筆處理
        sources.add('/' + src.lstrip('/').rstrip('/'))
    return sources


REDIRECT_SOURCES = load_redirect_sources()

# 由 main() 在 live 檢查後填入「live 非 200」的 URL path。
# hreflang 產生/修復時必須把它們視為「目標不存在」，否則會替 404 頁產生 hreflang。
LIVE_EXCLUDED_PATHS = set()


def check_url(url: str):
    """HEAD 單一 URL，回傳 (url, status, note)。

    status 為 int 或 'ERR'（連線層失敗）。ERR 不可當成 404 —— 並發下偶發
    SSL handshake timeout，誤判會把活頁從 sitemap 移除（2026-10-20 教訓）。
    """
    last = ('ERR', '')
    for attempt in range(LIVE_RETRIES + 1):
        try:
            p = urllib.parse.urlparse(url)
            conn = http.client.HTTPSConnection(p.netloc or 'dingyaoadvisory.tw', timeout=LIVE_TIMEOUT)
            path = (p.path or '/') + (('?' + p.query) if p.query else '')
            conn.request('HEAD', path, headers=UA)
            r = conn.getresponse()
            r.read()
            code = r.status
            conn.close()
            return url, code, ''
        except Exception as e:  # noqa: BLE001
            last = ('ERR', str(e)[:60])
            if attempt < LIVE_RETRIES:
                time.sleep(0.6 * (attempt + 1))
    return url, last[0], last[1]


def filter_deployed(urls: set):
    """只留下 live 200 的 URL。

    為什麼需要（2026-10-28）：舊版只認 dist/ 檔案存在，不認 live 狀態。
    10-27 把一頁尚未部署的 valuation 草稿（dist 有檔、live 404）送進
    sitemap ＋ IndexNow，讓 Google 收到 404。

    回傳 (kept, dropped, unknown)：
      kept    = live 200
      dropped = live 明確非 200（3xx/4xx/5xx）→ 排除
      unknown = 連線層失敗（ERR）→ 保守保留，只警告不刪
    """
    kept, dropped, unknown = set(), {}, {}
    todo = sorted(urls)
    print(f'[live] 檢查 {len(todo)} 個 URL 是否真的部署（並發 {LIVE_WORKERS}）...')
    with cf.ThreadPoolExecutor(max_workers=LIVE_WORKERS) as ex:
        for url, code, note in ex.map(check_url, todo):
            if code == 200:
                kept.add(url)
            elif code == 'ERR':
                unknown[url] = note
                kept.add(url)
            else:
                dropped[url] = code
    if dropped:
        print(f'[live] ⛔ 排除 {len(dropped)} 個非 200（未部署/已下線）:')
        for u, c in sorted(dropped.items()):
            print(f'       {c}  {u}')
    else:
        print('[live] ✅ 全部 200，無需排除')
    if unknown:
        print(f'[live] ⚠️  {len(unknown)} 個 URL 連線失敗（保守保留，請重跑確認）:')
        for u, n in sorted(unknown.items())[:10]:
            print(f'       ERR {u}  ({n})')
    return kept, dropped, unknown


def _path_of(url: str) -> str:
    return urlparse(url).path.rstrip('/') or '/'


def should_index(path: Path) -> bool:
    name = path.name
    if name.startswith(EXCLUDE_PREFIXES):
        return False
    if any(s in name for s in EXCLUDE_SUBSTR):
        return False
    if path_to_rel(path) in REDIRECT_SOURCES:
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
    # 2026-10-26（S-20261026-01）：lastmod 取「最後修改」而非「發布」
    for key in ('dateModified', 'datePublished'):
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

def _href_target_exists(href: str) -> bool:
    """hreflang href 的目標檔是否存在（/index 視為 /）。

    目標若是 _redirects 的來源（會被 301 攔截）也算不存在 → hreflang 不可指向 redirect。
    """
    path = urlparse(href).path
    if path == '/index':
        path = '/'
    if path.rstrip('/') in REDIRECT_SOURCES and path != '/':
        return False
    if path.rstrip('/') in LIVE_EXCLUDED_PATHS and path != '/':
        return False  # hreflang 不可指向 live 非 200 的頁（含未部署草稿）
    return rel_to_path(path).exists()

def repair_hreflang(content: str):
    """對既有 <url> 區塊做兩件事（防死連結殘留 + /index 正規化）：
       1) 移除 href 目標檔不存在的 <xhtml:link>（盲生 -en 對應的根因）
       2) /index -> /
       Idempotent。回傳 (content, dropped, normalized)。"""
    dropped, normalized = [], []

    def fix_block(m):
        out_lines = []
        for line in m.group(0).split('\n'):
            lm = re.search(r'hreflang="([^"]+)"\s+href="([^"]+)"', line)
            if lm:
                lang, href = lm.group(1), lm.group(2)
                if urlparse(href).path == '/index':
                    line = line.replace(href, DOMAIN + '/')
                    normalized.append((lang, href))
                    href = DOMAIN + '/'
                if not _href_target_exists(href):
                    dropped.append((lang, href))
                    continue
            out_lines.append(line)
        return '\n'.join(out_lines)

    content = re.sub(r'<url>.*?</url>', fix_block, content, flags=re.S)
    return content, dropped, normalized


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

def main(bump_slugs=None, offline=False):
    global LIVE_EXCLUDED_PATHS
    bump_slugs = bump_slugs or []
    content = SITEMAP.read_text(encoding='utf-8')
    expected_all = get_expected_urls()

    if offline:
        print('[offline] 跳過 live 部署檢查（CI／無網路時使用）')
        expected = expected_all
    else:
        expected, dropped_live, _unknown = filter_deployed(expected_all)
        LIVE_EXCLUDED_PATHS = {_path_of(u) for u in dropped_live}
    
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
    
    # 修復既有區塊的 hreflang 死連結 + /index 正規化（根治：既有 block 過去不重檢）
    content, dropped, normalized = repair_hreflang(content)
    if dropped:
        print(f'  ! dropped {len(dropped)} dead hreflang link(s):')
        for l, h in dropped:
            print(f'      DROP {l} {h}')
    if normalized:
        print(f'  ~ normalized {len(normalized)} /index -> /')

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
    args = sys.argv[1:]
    offline = ('--offline' in args) or ('--no-live' in args)
    bump = [a for a in args if not a.startswith('-')]
    main(bump_slugs=bump, offline=offline)
