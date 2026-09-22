#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sort_blog_cards.py — blog 列表卡片排序重建腳本（唯一合法的卡片排序維護工具）

問題根因（2026-09-22 老闆發現）：
  blog.html / blog-en.html 的新卡片是手動 patch 插入「上一張卡片之後」的固定位置，
  插入點會漂移（09.22 新文被插在 09.18 之後變第 2 張），且卡片日期/閱讀時間
  格式長期不一致（ISO / 中文點號 / 自然語言日期 / 英文 min read 混入中文版）。

本腳本：
  1. 解析 index 的所有 <article class="blog-card"> 卡片
  2. 以各文章頁 JSON-LD 的 datePublished 為「唯一真實來源」，嚴格降序重排
  3. 統一卡片 blog-meta 格式：
       ZH → YYYY.MM.DD + N 分鐘閱讀
       EN → YYYY-MM-DD + N min read
  4. 閱讀時間取自文章頁本文（ZH：「N 分鐘閱讀」；EN：「N min read」），不得手寫
  5. 自我驗證（卡片數、標籤平衡、格式統一、嚴格降序、href 無重複），失敗即 exit 1

用法：
  python3 scripts/sort_blog_cards.py            # 重建 + 驗證（冪等：重跑無變化）
  python3 scripts/sort_blog_cards.py --check    # 只檢查不寫入

新文章發布流程（2026-09-22 起，取代手動插卡位置判斷）：
  1. 把新卡片 HTML 插入 blog-grid 內（任意位置，慣例：第一張卡之後）
  2. 執行本腳本 → 自動排到 datePublished 正確位置、meta 格式自動統一
  3. 跑 verify_blog_integrity.py + consistency_gate.py 全過後才可 git push

注意：
  - datePublished = 2026-01-01 的文章（佔位值）本腳本照 dp 排序/顯示，
    不發明日期；發現佔位日期 → 回報土星人 → 火星人修文章 JSON-LD。
"""
import re
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "dist"))
BLOG_DIR = os.path.join(DIST, "blog")
ZH_INDEX = os.path.join(DIST, "blog.html")
EN_INDEX = os.path.join(DIST, "blog-en.html")

CARD_RE = re.compile(r'<article class="blog-card[^>]*>.*?</article>', re.DOTALL)
META_RE = re.compile(r'<div class="blog-meta">.*?</div>', re.DOTALL)
GRID_RE = re.compile(r'<div class="blog-grid[^"]*"[^>]*>')

ZH_META = '''<div class="blog-meta">
            <span><i class="far fa-calendar"></i> {date}</span>
            <span><i class="far fa-clock"></i> {rt} 分鐘閱讀</span>
          </div>'''
EN_META = '''<div class="blog-meta">
      <span><i class="far fa-calendar"></i> {date}</span>
      <span><i class="far fa-clock"></i> {rt} min read</span>
    </div>'''

ZH_SEP = "\n\n      "
EN_SEP = "\n\n  "


def card_slug(card):
    m = re.search(r'href="([^"]*)"', card)
    if not m:
        return None
    return m.group(1).rstrip("/").split("/")[-1]


def article_date_published(slug):
    """唯一真實來源：文章頁 JSON-LD datePublished"""
    fp = os.path.join(BLOG_DIR, slug + ".html")
    if not os.path.exists(fp):
        return None
    c = open(fp, encoding="utf-8").read()
    m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', c)
    return m.group(1) if m else None


def article_reading_time(slug, lang):
    """閱讀時間取自文章頁本文（不得手寫）"""
    fp = os.path.join(BLOG_DIR, slug + ".html")
    if not os.path.exists(fp):
        return None
    c = open(fp, encoding="utf-8").read()
    if lang == "zh":
        m = re.search(r"(\d+)\s*分鐘閱讀", c)
    else:
        m = re.search(r"(\d+)\s*min read", c, re.IGNORECASE)
    return m.group(1) if m else None


def rebuild(path, lang, dry=False):
    c = open(path, encoding="utf-8").read()
    sep = ZH_SEP if lang == "zh" else EN_SEP
    meta_tpl = ZH_META if lang == "zh" else EN_META

    matches = list(CARD_RE.finditer(c))
    if not matches:
        print(f"[{lang}] FATAL: 找不到任何卡片")
        return False, []
    grid = GRID_RE.search(c)
    if not grid or grid.end() > matches[0].start():
        print(f"[{lang}] FATAL: blog-grid 結構異常")
        return False, []

    rebuilt = []
    problems = []
    mismatch_report = []   # 卡片顯示日期 != datePublished 清單
    placeholder_report = []  # dp=2026-01-01 佔位
    for idx, m in enumerate(matches):
        block = m.group(0)
        slug = card_slug(block)
        if not slug:
            problems.append(f"#{idx+1} 卡片無 href")
            continue
        dp = article_date_published(slug)
        if not dp:
            problems.append(f"#{idx+1} {slug}: 文章頁無 datePublished")
            continue
        rt = article_reading_time(slug, lang)
        if not rt:
            problems.append(f"#{idx+1} {slug}: 文章頁無閱讀時間")
            continue
        if dp == "2026-01-01":
            placeholder_report.append(slug)
        # 記錄實質不一致（卡片上的日期 != dp）
        old_date = re.search(r"(\d{4}[-.]\d{2}[-.]\d{2})", block)
        if old_date and old_date.group(1).replace(".", "-") != dp:
            mismatch_report.append((idx + 1, slug, old_date.group(1), dp))

        display = dp.replace("-", ".") if lang == "zh" else dp
        new_meta = meta_tpl.format(date=display, rt=rt)
        if META_RE.search(block):
            block = META_RE.sub(new_meta, block, count=1)
        else:
            block = block.replace("</h3>", "</h3>\n" + new_meta, 1)
        rebuilt.append({"slug": slug, "dp": dp, "raw": block, "orig": idx})

    if problems:
        for p in problems:
            print(f"[{lang}] ❌ {p}")
        return False, []

    # 穩定嚴格降序（同日保持原相對順序）
    rebuilt.sort(key=lambda x: x["dp"], reverse=True)

    joined = sep.join(item["raw"] for item in rebuilt)
    new_c = c[:matches[0].start()] + joined + c[matches[-1].end():]

    print(f"[{lang}] 卡片 {len(matches)} 張；重排後首位: {rebuilt[0]['slug']} ({rebuilt[0]['dp']})")
    if mismatch_report:
        print(f"[{lang}] 卡片日期 != datePublished（已依 dp 修正）: {len(mismatch_report)} 筆")
        for pos, slug, cd, dp in mismatch_report:
            print(f"    #{pos} {slug}: 卡片={cd} → dp={dp}")
    if placeholder_report:
        print(f"[{lang}] ⚠️ dp=2026-01-01 佔位（需火星人修 JSON-LD）: {sorted(set(placeholder_report))}")

    if not dry:
        open(path, "w", encoding="utf-8").write(new_c)
        print(f"[{lang}] 已寫入 {path}")
    return True, rebuilt


def verify(path, lang):
    c = open(path, encoding="utf-8").read()
    cards = CARD_RE.findall(c)
    ok = True

    # 1. 標籤平衡（檔案內所有 <article> 都應是卡片）
    n_open = len(re.findall(r"<article", c))
    n_close = c.count("</article>")
    if not (n_open == n_close == len(cards)):
        print(f"[{lang}] ❌ 標籤不平衡: article開={n_open} 閉={n_close} 卡片={len(cards)}")
        ok = False
    else:
        print(f"[{lang}] 標籤平衡: {n_open}/{n_close} ({len(cards)} 卡)")

    # 2. 降序檢查
    seq = []
    for card in cards:
        slug = card_slug(card)
        dp = article_date_published(slug) if slug else None
        seq.append((dp, slug))
    disorders = 0
    for i in range(1, len(seq)):
        if seq[i][0] and seq[i - 1][0] and seq[i][0] > seq[i - 1][0]:
            print(f"[{lang}] ❌ 非降序: #{i+1} {seq[i][0]} > #{i} {seq[i-1][0]}")
            disorders += 1
    print(f"[{lang}] 非降序: {disorders} 處")
    if disorders:
        ok = False

    # 3. 格式檢查
    fmt_bad = 0
    for i, card in enumerate(cards):
        if lang == "zh":
            if re.search(r"\d{4}-\d{2}-\d{2}", card) or "min read" in card or "分鐘閱讀" not in card:
                print(f"[{lang}] ❌ #{i+1} 格式異常")
                fmt_bad += 1
        else:
            if re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}", card) or "min read" not in card:
                print(f"[{lang}] ❌ #{i+1} 格式異常")
                fmt_bad += 1
    print(f"[{lang}] 格式異常: {fmt_bad} 張")
    if fmt_bad:
        ok = False

    # 4. 重複 href
    hrefs = [card_slug(card) for card in cards]
    dup = [h for h in set(hrefs) if hrefs.count(h) > 1]
    if dup:
        print(f"[{lang}] ❌ 重複卡片 href: {dup}")
        ok = False
    else:
        print(f"[{lang}] 重複 href: 0")

    return ok


def main():
    dry = "--check" in sys.argv
    all_ok = True
    for path, lang in [(ZH_INDEX, "zh"), (EN_INDEX, "en")]:
        if not os.path.exists(path):
            print(f"[{lang}] FATAL: {path} 不存在")
            sys.exit(1)
        done, _ = rebuild(path, lang, dry=dry)
        if not done:
            all_ok = False
            continue
        if not verify(path, lang):
            all_ok = False
    if dry:
        print("\n--check 模式：未寫入任何檔案")
    print("\n" + ("✅ ALL SORT/FORMAT CHECKS PASSED" if all_ok else "❌ 有失敗項，嚴禁 git push"))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()