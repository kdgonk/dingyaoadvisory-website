#!/usr/bin/env python3
"""把某個 commit 動到的 dist 頁面，在 dist/sitemap.xml 裡的 lastmod 補成指定日期。

為什麼要有這支：push + purge ≠ Google 會重讀。Google 靠 <lastmod> 判斷是否重新抓取，
所以「內容改了、lastmod 沒動」等於策略不會生效（2026-09-30 教訓）。

用法：
  python3 scripts/bump_lastmod.py 66828741 --date 2026-10-22 --dry-run
  python3 scripts/bump_lastmod.py 66828741 --date 2026-10-22
  python3 scripts/bump_lastmod.py 66828741 --date 2026-10-22 --extra /education /education-en

行為：
  1. `git show --name-only <commit>` 取 dist/**/*.html
  2. 檔案路徑 → URL 路徑（去掉 dist、去掉 .html，index.html → /）
  3. 逐個在 sitemap 的 <url> block 比對 <loc>，lastmod 不等於目標日期就改
  4. 印出「原本日期 → 新日期」對照，最後印 bumped / already / missing 統計
不改任何其他欄位（changefreq / priority / hreflang 原樣保留）。
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITEMAP = REPO / "dist" / "sitemap.xml"


def changed_paths(commit: str):
    out = subprocess.run(
        ["git", "show", "--name-only", "--format=", commit],
        cwd=REPO, capture_output=True, text=True, check=True
    ).stdout
    paths = []
    for line in out.splitlines():
        line = line.strip()
        if not line or not line.startswith("dist/") or not line.endswith(".html"):
            continue
        rel = line[len("dist/"):-len(".html")]
        if rel.endswith("/index"):
            rel = rel[: -len("/index")]
        paths.append("/" + rel if rel != "index" else "/")
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("commit")
    ap.add_argument("--date", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sitemap", default=str(SITEMAP))
    args = ap.parse_args()

    sm = Path(args.sitemap)
    text = sm.read_text(encoding="utf-8")
    targets = changed_paths(args.commit) + ["/" + e.strip("/") if not e.startswith("/") else e for e in args.extra]

    bumped, already, missing = [], [], []
    for path in targets:
        loc = "https://dingyaoadvisory.tw" + path
        pat = re.compile(
            r'(<loc>' + re.escape(loc) + r'</loc>\s*<lastmod>)([^<]*)(</lastmod>)'
        )
        m = pat.search(text)
        if not m:
            missing.append(path)
            continue
        old = m.group(2)
        if old == args.date:
            already.append((path, old))
            continue
        bumped.append((path, old))
        text = text[: m.start(2)] + args.date + text[m.end(2):]

    for p, old in bumped:
        print(f"BUMP  {p:<75} {old} -> {args.date}")
    for p, old in already:
        print(f"SKIP  {p:<75} already {old}")
    for p in missing:
        print(f"MISS  {p:<75} 不在 sitemap")

    print(f"\nbumped={len(bumped)} already={len(already)} missing={len(missing)} total={len(targets)}")

    if not args.dry_run and bumped:
        sm.write_text(text, encoding="utf-8")
        print(f"已寫回 {sm}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
