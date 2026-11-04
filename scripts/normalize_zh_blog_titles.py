#!/usr/bin/env python3
"""ZH blog <title> 品牌尾綴正規化器（全站唯一權威）

背景（土星人 2026-11-04 派工）：
  live 上 4 頁 title 被截成「…｜鼎曜」，品牌尾綴應為「｜鼎曜國際顧問」。
  追查結論：不是程式截斷，是 2026-10-19（commit a08485cc）「title 重寫」時
  文案手寫了短尾綴；另外模板 dist/blog/article-template.html 只把品牌加在
  <title>，og:title / twitter:title / JSON-LD headline 都沒有 → 四個輸出面不一致。
  舊的 scripts/fix_zh_title_length.py 在「品牌塞不下」時直接 return content，
  等於靜默丟掉品牌 → 結構性風險。

本檔做兩件事（不手改 HTML，一律由規則產生）：
  1. 定義唯一品牌常數 BRAND 與長度上限 MAX，並提供 build_title()
  2. 掃描 dist/blog/*.html（排除 -en），把 <title> / og:title / twitter:title /
     主 Article 的 "headline" 四處同步成同一個字串

用法：
  python3 scripts/normalize_zh_blog_titles.py            # dry-run 報告（修前/修後清單）
  python3 scripts/normalize_zh_blog_titles.py --apply     # 寫入
  python3 scripts/normalize_zh_blog_titles.py --apply --only-slug X   # 只跑一頁
  python3 scripts/normalize_zh_blog_titles.py --strict    # 有任何不合格就 exit 1

硬閘門（--strict / --apply 時）：
  最終 title 必須 endswith(BRAND) 且 len <= MAX，否則 exit 1。
  超長頁不自動亂切語意，必須在 scripts/zh_blog_title_map.json 給人寫好的 core。
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(REPO, "dist", "blog")
MAP_PATH = os.path.join(REPO, "scripts", "zh_blog_title_map.json")

#: 唯一品牌尾綴（全形豎線，與 article-template.html 一致）
BRAND = "｜鼎曜國際顧問"
#: 全長上限（含品牌）。SERP 安全值。
MAX = 60
#: 內容（不含品牌）上限
MAX_CORE = MAX - len(BRAND)

#: 結尾品牌變體（含常見錯字：鼎昰國際顯問）
BRAND_RE = re.compile(
    r"\s*[｜|]?\s*"
    r"(?:鼎曜國際顧問(?:\s*DingYao(?:\s*Advisory)?)?"
    r"|鼎曜國際顯問|鼎昰國際顯問|鼎曜國際"
    r"|DingYao(?:\s*Advisory)?"
    r"|鼎曜)"
    r"\s*$"
)

TITLE_RE = re.compile(r"(<title>)(.*?)(</title>)", re.S)
OG_RE = re.compile(r'(<meta\s+property="og:title"\s+content=")([^"]*)(")')
TW_RE = re.compile(r'(<meta\s+name="twitter:title"\s+content=")([^"]*)(")')
HL_RE = re.compile(r'("headline"\s*:\s*")([^"]*)(")')

#: 模板檔（非文章頁）：由 patch 直接修，不交給批次正規化
EXCLUDE = {"article-template.html", "blog-template.html"}

#: S-20261019-03 凍結頁（freeze_until 2026-11-17）：title 一律不碰
FROZEN = {
    "cape-town-quality-of-life-cost-comparison-en.html",
    "standard-bank-money-market-en.html",
    "south-africa-talent-skills-shortage-2026.html",
    "south-africa-transfer-duty-foreign-buyer-cape-town-tax-guide-2026.html",
    "cape-town-rental-yield-9-49-percent-reality-check-2026-en.html",
    "cape-town-property-investment-rates-net-return-2026-en.html",
}


def split_brand(title: str) -> tuple[str, str | None]:
    """剝離結尾品牌，回傳 (core, 原尾綴 or None)。"""
    t = title.strip()
    m = BRAND_RE.search(t)
    if m and m.start() > 0:
        core = t[: m.start()].rstrip(" ｜|")
        if core:
            return core, m.group(0).strip()
    return t, None


def fit(core: str) -> str:
    """core + BRAND。"""
    return core.rstrip() + BRAND


def load_map() -> dict[str, str]:
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("titles", {})
    return {}


def plan(path: str, title_map: dict[str, str]) -> dict | None:
    slug = os.path.basename(path)[: -len(".html")]
    html = open(path, encoding="utf-8").read()
    m = TITLE_RE.search(html)
    if not m:
        return None
    old = m.group(2).strip()

    # 1. 人工覆寫優先（已含品牌者亦可覆寫，但值必須自帶品牌）
    if slug in title_map:
        new = title_map[slug].strip()
        if not new.endswith(BRAND):
            new = fit(new)
        source = "map"
    else:
        core, _variant = split_brand(old)
        new = fit(core)
        source = "rule"

    # 2. 已合格且無覆寫 → 不動
    already_ok = old.endswith(BRAND) and len(old) <= MAX
    changed = new != old

    og = OG_RE.search(html)
    tw = TW_RE.search(html)
    hl = HL_RE.search(html)
    side_mismatch = any(
        g is not None and g.group(2).strip() != new for g in (og, tw, hl)
    )

    return {
        "slug": slug,
        "path": path,
        "old": old,
        "new": new,
        "source": source,
        "changed": changed,
        "already_ok": already_ok,
        "side_mismatch": side_mismatch,
        "ok": new.endswith(BRAND) and len(new) <= MAX,
        "og": og.group(2) if og else None,
        "tw": tw.group(2) if tw else None,
        "hl": hl.group(2) if hl else None,
        "has_hl": hl is not None,
    }


def rewrite(html: str, new: str) -> tuple[str, int]:
    """四處同步為 new，回傳 (html, 實際改動次數)。"""
    n = 0

    def sub(pattern, text, group=2, count=1):
        nonlocal n

        def _r(m):
            nonlocal n
            if m.group(group) != new:
                n += 1
                return m.group(1) + new + m.group(3)
            return m.group(0)

        return pattern.sub(_r, text, count=count)

    html = sub(TITLE_RE, html)
    html = sub(OG_RE, html)
    html = sub(TW_RE, html)
    html = sub(HL_RE, html, count=0)  # 主 Article 的 headline（含重複誤植，全部對齊）
    return html, n


def main() -> int:
    apply = "--apply" in sys.argv
    strict = "--strict" in sys.argv or apply
    only = None
    if "--only-slug" in sys.argv:
        only = sys.argv[sys.argv.index("--only-slug") + 1]

    title_map = load_map()
    files = sorted(glob.glob(os.path.join(BLOG_DIR, "*.html")))
    files = [
        f
        for f in files
        if not f.endswith("-en.html") and os.path.basename(f) not in EXCLUDE
    ]
    frozen_hit = [f for f in files if os.path.basename(f) in FROZEN]
    files = [f for f in files if os.path.basename(f) not in FROZEN]
    if only:
        files = [f for f in files if os.path.basename(f) == only + ".html"]

    rows, bad, touched, synced = [], [], 0, 0
    for f in files:
        p = plan(f, title_map)
        if not p:
            continue
        rows.append(p)
        if not p["ok"]:
            bad.append(p)
            continue
        if apply and (p["changed"] or p["side_mismatch"]):
            html = open(f, encoding="utf-8").read()
            out, n = rewrite(html, p["new"])
            if n:
                open(f, "w", encoding="utf-8").write(out)
                synced += 1
        if p["changed"]:
            touched += 1

    print(f"ZH blog 頁數：{len(rows)}｜title 需改：{touched}｜四處同步寫入：{synced}")
    print(f"排除：模板 {sorted(EXCLUDE)}｜凍結頁 {len(frozen_hit)} 頁不動（freeze_until 2026-11-17）")
    print("=" * 100)
    print("【需改清單】修前 → 修後")
    for p in rows:
        if not p["changed"]:
            continue
        mark = "map" if p["source"] == "map" else "auto"
        print(f"\n[{mark}] {p['slug']}")
        print(f"  修前({len(p['old'])})：{p['old']}")
        print(f"  修後({len(p['new'])})：{p['new']}")

    print("\n" + "=" * 100)
    unchanged = [p for p in rows if not p["changed"]]
    print(f"【不動清單】已合格 {len(unchanged)} 頁（title 已是『{BRAND}』且 ≤{MAX}）")
    for p in unchanged:
        print(f"  {len(p['old']):3d}  {p['slug']}")

    if bad:
        print("\n" + "!" * 100)
        print(f"🔴 不合格 {len(bad)} 頁（超長或缺品牌）→ 請在 scripts/zh_blog_title_map.json 補 core：")
        for p in bad:
            print(f"  {len(p['new']):3d}  {p['slug']}\n       {p['new']}")
        if strict:
            return 1

    print(f"\n模式：{'APPLY' if apply else 'DRY-RUN'}｜品牌常數：{BRAND}｜上限：{MAX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
