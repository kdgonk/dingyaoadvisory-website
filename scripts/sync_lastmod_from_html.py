#!/usr/bin/env python3
"""讓 sitemap 的 <lastmod> 回到「真實內容變更日」。

背景（2026-10-26 土星人派工 S-20261026-01）
  82f4516d / 26518b70 只改 HTML/CSS 註解，卻透過 bump_lastmod.py 把 289 頁
  lastmod 全部推到 2026-10-23 → Google 收到「近 300 頁同時變更」的假訊號，
  lastmod 失去「何時真的改內容」的資訊價值，所有重抓閘門判準一起失效。

判定規則（本檔實作）
  1. 用「可見內容指紋」判斷內容是否真的變了：把該版本 HTML 的
     <script>…</script>（含 JSON-LD）、<style>…</style>、HTML 註解全部剝掉、
     壓縮空白後取 sha256。
     → 純註解 commit、純追蹤碼/consent script commit、純 dateModified 編輯
       都不會改變指紋 ⇒ **不觸發 lastmod bump**。
     → 正文文字、內連 <li>、footer/nav 可見字樣、img src 變更 ⇒ 指紋改變 ⇒ 算變更。
  2. lastmod = max(該頁 JSON-LD dateModified, 該頁最後一次「可見內容變更」commit 日期)
     —— 新頁的 dateModified 通常等於真實日期，取它；舊頁 dateModified 早已失準，
     由 git 真實變更日補上（不讓 lastmod 憑空變新，也不讓它停留在假的舊值）。
  3. 兩者都取不到（少數無 JSON-LD 日期、且 8 個 commit 內無變更）→ 列 KEEP，保留原值。

用法
  python3 scripts/sync_lastmod_from_html.py --dry-run
  python3 scripts/sync_lastmod_from_html.py --apply
  python3 scripts/sync_lastmod_from_html.py --dry-run --max-commits 12
"""
import argparse
import collections
import hashlib
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(REPO, 'dist', 'sitemap.xml')
BASE = 'https://dingyaoadvisory.tw'

_SCRIPT = re.compile(r'<script\b.*?</script\s*>', re.S | re.I)
_STYLE = re.compile(r'<style\b.*?</style\s*>', re.S | re.I)
_COMMENT = re.compile(r'<!--.*?-->', re.S)


def git(*args, binary=False):
    p = subprocess.run(['git', '-C', REPO, *args], capture_output=True)
    if binary:
        return p.stdout
    return p.stdout.decode('utf-8', 'ignore')


def fingerprint(html):
    """可見內容指紋：剝掉 script/style/註解，壓縮空白。"""
    s = _SCRIPT.sub(' ', html)
    s = _STYLE.sub(' ', s)
    s = _COMMENT.sub(' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def blob_fp(rev, relpath):
    raw = git('show', f'{rev}:{relpath}', binary=True)
    if not raw:
        return None
    return fingerprint(raw.decode('utf-8', 'ignore'))


def content_change_date(relpath, max_commits):
    """該檔最後一次「可見內容」變更的 commit 日期 (YYYY-MM-DD)，沒有則 None。"""
    log = git('log', f'-n{max_commits}', '--format=%H|%ad', '--date=short', '--', relpath)
    for row in log.splitlines():
        if '|' not in row:
            continue
        sha, date = row.split('|', 1)
        cur = blob_fp(sha, relpath)
        prev = blob_fp(f'{sha}^', relpath)
        if cur is None:
            continue          # 該 commit 是刪檔
        if prev is None:      # 該 commit 新增此檔
            return date
        if cur != prev:
            return date
    return None


def url_to_path(loc):
    path = loc.replace(BASE, '')
    if path.endswith('/'):
        return 'dist' + path + 'index.html'
    if path.endswith('.xml') or path.endswith('.txt'):
        return 'dist' + path
    return 'dist' + path + '.html'


def jsonld_date_modified(abspath):
    try:
        html = open(abspath, encoding='utf-8', errors='ignore').read()
    except OSError:
        return None
    m = re.search(r'"dateModified"\s*:\s*"([0-9]{4}-[0-9]{2}-[0-9]{2})', html)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--apply', action='store_true')
    ap.add_argument('--max-commits', type=int, default=8)
    ap.add_argument('--sync-date-modified', action='store_true',
                    help='同時把 JSON-LD dateModified 對齊真實變更日（只改 metadata、不動可見文字；'
                         '工作區有未 commit 改動的檔案一律跳過，避免覆蓋其他 Agent 的手稿）')
    args = ap.parse_args()

    worktree_dirty = set(git('status', '--porcelain').splitlines())
    dirty_paths = {line[3:].strip() for line in worktree_dirty}

    sm = open(SITEMAP, encoding='utf-8').read()
    blocks = re.findall(r'<url>.*?</url>', sm, re.S)
    print(f'sitemap blocks: {len(blocks)}')

    plan, keep, stats = [], [], collections.Counter()
    allrows = []          # (loc, cur, truth, dateModified) 供 dateModified 對齊使用
    for block in blocks:
        loc = re.search(r'<loc>(.*?)</loc>', block).group(1).strip()
        cur = re.search(r'<lastmod>(.*?)</lastmod>', block)
        cur = cur.group(1).strip()[:10] if cur else None
        relpath = url_to_path(loc)
        dm = jsonld_date_modified(os.path.join(REPO, relpath))
        cd = content_change_date(relpath, args.max_commits)
        cands = [d for d in (dm, cd) if d]
        if not cands:
            keep.append((loc, cur))
            stats['keep'] += 1
            continue
        truth = max(cands)
        allrows.append((loc, cur, truth, dm))
        stats['both' if (dm and cd) else ('jsonld_only' if dm else 'git_only')] += 1
        if truth != cur:
            plan.append((loc, cur, truth, dm, cd))
            stats['changed'] += 1
        else:
            stats['same'] += 1

    print('stats:', dict(stats))
    print(f'\n--- CHANGE ({len(plan)}) ---')
    for loc, cur, truth, dm, cd in sorted(plan, key=lambda r: (r[2], r[0])):
        print(f'{cur} -> {truth}  (dateModified={dm} gitContent={cd})  {loc}')
    print(f'\n--- KEEP 無日期依據 ({len(keep)}) ---')
    for loc, cur in keep:
        print(f'{cur}  {loc}')

    new_dist = collections.Counter()
    for loc, cur, truth, dm, cd in plan:
        new_dist[truth] += 1
    if new_dist:
        print('\n新值分佈:', dict(sorted(new_dist.items(), reverse=True)))

    if args.sync_date_modified:
        dm_plan, dm_skip = [], []
        for loc, cur, truth, dm in allrows:
            relpath = url_to_path(loc)
            if not dm or dm >= truth:
                continue
            if relpath in dirty_paths:
                dm_skip.append(relpath)
                continue
            dm_plan.append((relpath, dm, truth))
        print(f'\n--- dateModified 對齊 ({len(dm_plan)}) ---')
        for relpath, dm, truth in dm_plan[:400]:
            print(f'{dm} -> {truth}  {relpath}')
        if dm_skip:
            print(f'SKIP {len(dm_skip)} 檔（工作區有未 commit 改動，留給該 Agent）：')
            for p in dm_skip:
                print(f'      {p}')
        if args.apply:
            for relpath, dm, truth in dm_plan:
                fp = os.path.join(REPO, relpath)
                html = open(fp, encoding='utf-8', errors='ignore').read()
                new_html, n = re.subn(r'("dateModified"\s*:\s*")' + re.escape(dm) + r'(")',
                                      lambda m, t=truth: m.group(1) + t + m.group(2),
                                      html, count=1)
                if n != 1:
                    print(f'!! MISS dateModified {relpath}')
                    continue
                open(fp, 'w', encoding='utf-8').write(new_html)
            print(f'dateModified 已更新 {len(dm_plan)} 檔')

    if args.apply:
        new_sm = sm
        miss = 0
        for loc, cur, truth, dm, cd in plan:
            pat = re.compile(r'<loc>' + re.escape(loc) + r'</loc>(\s*)<lastmod>[^<]*</lastmod>')
            new_sm, n = pat.subn(lambda m: f'<loc>{loc}</loc>{m.group(1)}<lastmod>{truth}</lastmod>',
                                 new_sm, count=1)
            if n != 1:
                miss += 1
                print(f'!! MISS {loc}')
        if miss:
            print(f'ABORT: {miss} 筆定位失敗，未寫檔')
            return 1
        open(SITEMAP, 'w', encoding='utf-8').write(new_sm)
        print('\nWROTE', SITEMAP)
    return 0


if __name__ == '__main__':
    sys.exit(main())
