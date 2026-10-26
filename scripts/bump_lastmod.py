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
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITEMAP = REPO / "dist" / "sitemap.xml"

# ── 純雜訊變更判定（2026-10-26 土星人派工 S-20261026-01）──────────────────
# 82f4516d / 26518b70 只改 HTML/CSS 註解，卻讓 292 頁 lastmod 一起跳到 10-23，
# Google 因此收到「近 300 頁同時變更」的假訊號。此後 bump 前先比對
# 「可見內容指紋」：剝掉 script/style/註解後若位元組相同 ⇒ 不算內容變更，不 bump。
_VIS_DROP = (
    re.compile(r"<script\b.*?</script\s*>", re.S | re.I),
    re.compile(r"<style\b.*?</style\s*>", re.S | re.I),
    re.compile(r"<!--.*?-->", re.S),
)


def _fingerprint(raw: bytes) -> str:
    s = raw.decode("utf-8", "ignore")
    for pat in _VIS_DROP:
        s = pat.sub(" ", s)
    return hashlib.sha256(re.sub(r"\s+", " ", s).strip().encode()).hexdigest()


def _blob_fp(rev: str, relpath: str):
    p = subprocess.run(["git", "show", f"{rev}:{relpath}"], cwd=REPO, capture_output=True)
    return _fingerprint(p.stdout) if p.returncode == 0 and p.stdout else None


def content_changed(commit: str, url_path: str) -> bool:
    """該 commit 對這一頁是否造成可見內容變更（純註解／純追蹤碼 = False）。"""
    rel = url_path.strip("/")
    relpath = "dist/index.html" if rel == "" else f"dist/{rel}.html"
    cur, prev = _blob_fp(commit, relpath), _blob_fp(f"{commit}^", relpath)
    if cur is None:
        return False            # 該 commit 刪了檔 → 不是內容更新
    if prev is None:
        return True             # 新增檔
    return cur != prev


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
    touched = changed_paths(args.commit)
    noise = [p for p in touched if not content_changed(args.commit, p)]
    targets = [p for p in touched if p not in noise] + [
        "/" + e.strip("/") if not e.startswith("/") else e for e in args.extra
    ]

    if noise:
        print(f"NOISE {len(noise)} 頁只有註解／script 變更，不 bump lastmod：")
        for p in noise[:5]:
            print(f"      {p}")
        if len(noise) > 5:
            print(f"      … 其餘 {len(noise) - 5} 頁")
        print()

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
