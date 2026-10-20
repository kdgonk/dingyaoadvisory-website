#!/usr/bin/env python3
"""List/rewrite internal links pointing at _redirects source URLs.

Usage:
  python3 scripts/fix_links_to_redirect_sources.py            # dry-run report
  python3 scripts/fix_links_to_redirect_sources.py --apply    # rewrite hrefs

Rules:
  * 只改 .html 裡的 href="..."（不動 canonical <link>、不動 hreflang）
  * 來源檔本身（會被 _redirects 攔截的檔案）不改，避免動到自己的 canonical
  * 映射以 dist/_redirects 為唯一真相；保留原本路徑形式（絕對 /blog/… 或相對 blog/…）
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse, urlsplit

ROOT = Path(__file__).parent.parent / 'dist'
DOMAIN = 'https://dingyaoadvisory.tw'
APPLY = '--apply' in sys.argv
VERBOSE = '--verbose' in sys.argv

mapping = {}
for line in (ROOT / '_redirects').read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split()
    if len(parts) < 2 or '*' in parts[0] or parts[0].startswith('http'):
        continue
    mapping[parts[0].rstrip('/')] = parts[1]

skip_files = {p.lstrip('/') + '.html' for p in mapping} | {p.lstrip('/') for p in mapping}

files = sorted(ROOT.glob('*.html')) + sorted((ROOT / 'blog').glob('*.html'))
href_re = re.compile(r'href="([^"]+)"')


def rewrite_href(val: str, src: str, dst: str) -> str:
    """若 href 的 path 等於 src，換成 dst，保留原形式（絕對/相對/帶域名）。"""
    parsed = urlsplit(val)
    if parsed.path.rstrip('/').lstrip('/') != src.lstrip('/'):
        return val
    newpath = dst
    if not parsed.path.startswith('/') and not parsed.netloc:
        newpath = dst.lstrip('/')          # 相對路徑（blog/xxx）
    elif parsed.netloc == 'dingyaoadvisory.tw':
        newpath = dst                      # 絕對 URL 保留域名
    out = newpath
    if parsed.query:
        out += '?' + parsed.query
    if parsed.fragment:
        out += '#' + parsed.fragment
    if parsed.netloc == 'dingyaoadvisory.tw':
        out = 'https://' + parsed.netloc + out
    return out


total = 0
per_file = {}
for f in files:
    rel = f.relative_to(ROOT).as_posix()
    if rel in skip_files:
        continue
    txt = f.read_text(encoding='utf-8')
    hits = 0

    def repl(m):
        global hits
        val = m.group(1)
        for src, dst in mapping.items():
            nv = rewrite_href(val, src, dst)
            if nv != val:
                hits += 1
                if VERBOSE:
                    print(f'    {rel}: href="{val}" -> "{nv}"')
                return f'href="{nv}"'
        return m.group(0)

    new = href_re.sub(repl, txt)
    if hits:
        per_file[rel] = hits
        total += hits
        if APPLY and new != txt:
            f.write_text(new, encoding='utf-8')

print(f'{"APPLIED" if APPLY else "DRY-RUN"}: files={len(per_file)} hrefs={total}')
for rel, n in sorted(per_file.items(), key=lambda x: -x[1])[:15]:
    print(f'  {n:4d}  {rel}')
if len(per_file) > 15:
    print(f'  ... +{len(per_file)-15} more files')
