#!/usr/bin/env python3
"""套用英文頁 title/meta 規格（資料驅動，不手改 HTML）

策略：S-20261106-EN-META（土星人 2026-11-04 派工，水星人規格 §3）
為什麼要腳本而不是逐頁改：規格是「逐字照抄」，任何手改都可能漂移；
本檔把規格與套用分離，套用時強制比對 expected_len，不符就 ERROR 不寫入。

改動欄位（4 個規格欄位 + 2 個一致性欄位）：
  1. <title>
  2. <meta name="description">
  3. <meta property="og:description">
  4. <meta name="twitter:description">
  5. <meta property="og:title">      ← 一致性：避免「<title> 是新的、og 是壞的」
  6. <meta name="twitter:title">     ← 同上（remote-work-visa-en 的 og/tw 原本是壞值「How South Africa」）

絕對不動：H1、canonical、hreflang、JSON-LD、robots。

用法：
  python3 scripts/apply_en_meta_spec.py                      # dry-run
  python3 scripts/apply_en_meta_spec.py --apply              # 寫入
  python3 scripts/apply_en_meta_spec.py --spec scripts/xxx.json --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(REPO, "dist", "blog")
DEFAULT_SPEC = os.path.join(REPO, "scripts", "en-meta-spec-2026-11-06.json")

CJK = re.compile(r"[\u3400-\u9fff]")


def field_patterns():
    return {
        "title": re.compile(r"(<title>)(.*?)(</title>)", re.S),
        "description": re.compile(r'(<meta\s+name="description"\s+content=")([^"]*)(")'),
        "og:description": re.compile(r'(<meta\s+property="og:description"\s+content=")([^"]*)(")'),
        "twitter:description": re.compile(r'(<meta\s+name="twitter:description"\s+content=")([^"]*)(")'),
        "og:title": re.compile(r'(<meta\s+property="og:title"\s+content=")([^"]*)(")'),
        "twitter:title": re.compile(r'(<meta\s+name="twitter:title"\s+content=")([^"]*)(")'),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=DEFAULT_SPEC)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--no-sync-og-title", action="store_true", help="不同步 og:title/twitter:title")
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    pages = spec["pages"]
    pats = field_patterns()
    errors, changed_total = [], 0

    for slug, cfg in pages.items():
        path = os.path.join(BLOG, slug + ".html")
        if not os.path.exists(path):
            errors.append(f"{slug}: 檔案不存在")
            continue
        title, desc = cfg["title"], cfg["description"]
        # 規格自我檢查：字元數必須與規格給的一致
        if len(title) != cfg["title_len"]:
            errors.append(f"{slug}: title 長度 {len(title)} ≠ 規格 {cfg['title_len']}")
        if len(desc) != cfg["description_len"]:
            errors.append(f"{slug}: desc 長度 {len(desc)} ≠ 規格 {cfg['description_len']}")
        if CJK.search(title) or CJK.search(desc):
            errors.append(f"{slug}: 英文欄位含中日韓字元")
        if len(title) > 65 or not (150 <= len(desc) <= 320):
            errors.append(f"{slug}: 超出站規（title ≤65 / desc 150–320）")
        if errors:
            continue

        html = open(path, encoding="utf-8").read()
        before = {
            "title": pats["title"].search(html).group(2).strip(),
            "description": pats["description"].search(html).group(2).strip(),
        }
        targets = {
            "title": title,
            "description": desc,
            "og:description": desc,
            "twitter:description": desc,
        }
        if not a.no_sync_og_title:
            targets["og:title"] = title
            targets["twitter:title"] = title

        n = 0
        for field, value in targets.items():
            pat = pats[field]

            def _r(m, value=value):
                nonlocal n
                if m.group(2) != value:
                    n += 1
                    return m.group(1) + value + m.group(3)
                return m.group(0)

            html, cnt = pat.subn(_r, html, count=1)
            if cnt == 0:
                errors.append(f"{slug}: 找不到 {field} 欄位")

        print(f"\n{'✓' if a.apply else '·'} {slug}")
        print(f"  title  {len(before['title']):3d} → {len(title):3d}  {title}")
        print(f"  desc   {len(before['description']):3d} → {len(desc):3d}  {desc[:90]}…")
        print(f"  改動欄位數：{n}")
        changed_total += n
        if a.apply and n:
            open(path, "w", encoding="utf-8").write(html)

    print(f"\n頁數 {len(pages)}｜欄位改動 {changed_total}｜錯誤 {len(errors)}｜模式 {'APPLY' if a.apply else 'DRY-RUN'}")
    for e in errors:
        print("🔴", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
