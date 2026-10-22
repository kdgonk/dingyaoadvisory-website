#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Menu 全站統一：中英文各 11 項，三支柱（開戶/置產/教育）相鄰。

土星人 2026-10-20 第 4 批規格：
  中文（11 項）：戰略夥伴 /partners｜數位服務 /platform｜南非開戶｜南非置產｜教育留學｜
                退休生活｜身分規劃｜精選資產｜商業考察｜鼎曜觀點｜預約諮詢
  英文（11 項）：Partners /partners-en｜Platform /platform-en｜Bank Account｜SA Property｜
                Education｜Retirement｜Residency｜Assets｜Tour｜Insights｜Consultation

插入位置：/platform（或 /platform-en）之後、/education 之前 ——
         南非開戶與南非置產放在教育之前，符合三支柱優先序。

不動的東西（土星人明確要求）：
  1. 每頁現有 lang 切換器（TW/EN）結構
  2. .btn-nav class 給「預約諮詢」
  3. /retirement 的 class="gold"
  4. logo 連結（英文頁 /index-en、中文頁 https://dingyaoadvisory.tw）

用法：
    python3 unify_nav.py --dry <html...>
    python3 unify_nav.py <html...>
"""
import pathlib
import re
import sys
from collections import Counter

ZH_NEW = (
    '      <a href="/south-africa-bank-account" title="南非開戶">南非開戶</a>\n'
    '      <a href="/south-africa-property" title="南非置產">南非置產</a>\n'
)
EN_NEW = (
    '      <a href="/south-africa-bank-account-en" title="Bank Account">Bank Account</a>\n'
    '      <a href="/south-africa-property-en" title="SA Property">SA Property</a>\n'
)

ZH_ANCHOR = re.compile(r'(<a href="/platform"[^>]*>[^<]*</a>\n)')
EN_ANCHOR = re.compile(r'(<a href="/platform-en"[^>]*>[^<]*</a>\n)')


def process(path: pathlib.Path, dry: bool):
    try:
        c = path.read_text(encoding="utf-8")
    except Exception:
        return "SKIP", "讀取失敗"
    if '<nav class="navbar"' not in c:
        return "SKIP", "無 nav"

    # 已有新連結 → 冪等
    if 'href="/south-africa-bank-account"' in c or 'href="/south-africa-bank-account-en"' in c:
        nav_seg = re.search(r'<div class="nav-links"[^>]*>(.*?)(?=<div class="nav-lang")', c, re.S)
        if nav_seg and ('south-africa-bank-account' in nav_seg.group(1)):
            return "ALREADY", "nav 已有新服務頁"

    is_en = '/platform-en' in c
    anchor = EN_ANCHOR if is_en else ZH_ANCHOR
    new_links = EN_NEW if is_en else ZH_NEW

    m = anchor.search(c)
    if not m:
        return "FAIL", f"找不到 {'/platform-en' if is_en else '/platform'} 錨點"

    new = c[:m.end()] + new_links + c[m.end():]

    # 驗證：新連結在 nav-links 內、且位於 /education 之前
    nav_seg = re.search(r'<div class="nav-links"[^>]*>(.*?)(?=<div class="nav-lang")', new, re.S)
    if not nav_seg:
        return "FAIL", "結構異常（找不到 nav-links 區段）"
    seg = nav_seg.group(1)
    bank = 'south-africa-bank-account' in seg
    prop = 'south-africa-property' in seg
    if not (bank and prop):
        return "FAIL", "新連結未進入 nav-links"
    edu = seg.find('/education')
    bankpos = seg.find('/south-africa-bank-account')
    if edu > 0 and bankpos > edu:
        return "FAIL", "位置錯（新連結跑到 education 之後）"
    # 既有元素未被破壞
    if 'class="btn-nav"' not in seg:
        return "FAIL", "btn-nav 遺失"
    if is_en and 'class="nav-lang"' not in new:
        return "FAIL", "nav-lang 遺失"

    if not dry:
        path.write_text(new, encoding="utf-8")
    return "OK", "en" if is_en else "zh"


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = []
    for a in args:
        p = pathlib.Path(a)
        files.extend(sorted(p.parent.rglob(p.name)) if "*" in a else [p])

    stats = Counter()
    fails = []
    for f in files:
        status, note = process(f, dry)
        stats[status] += 1
        if status == "FAIL":
            fails.append((f, note))

    print(f"{'[DRY] ' if dry else ''}結果（{len(files)} 檔）：")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    if fails:
        print(f"\n❌ 失敗 {len(fails)}：")
        for f, n in fails[:10]:
            print(f"   {f}: {n}")
        sys.exit(1)


if __name__ == "__main__":
    main()
