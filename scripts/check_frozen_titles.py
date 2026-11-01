#!/usr/bin/env python3
"""S-20261019-03 凍結守衛：6 頁 title/desc 在 2026-11-17 判定前不得再改。

背景（土星人 2026-11-02 裁決）：
  這 6 頁的 meta 是策略 S-20261019-03 的實驗處理（treatment），
  驗證窗已被切開兩次（10-26 首批、11-02 週合規檢查又改 2 頁），
  再改就無法判定成效 → 凍結至 2026-11-17。

用法：
  python3 scripts/check_frozen_titles.py --update    # 建立/更新凍結基準（僅在裁決變更時用）
  python3 scripts/check_frozen_titles.py            # 驗證：exit 0 = 未動；exit 1 = 有頁面被改；exit 2 = 基準檔遺失
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG = REPO / "dist" / "blog"
MANIFEST = REPO / "scripts" / "frozen_titles_S-20261019-03.json"
FREEZE_UNTIL = date(2026, 11, 17)

PAGES = [
    "cape-town-quality-of-life-cost-comparison-en.html",
    "standard-bank-money-market-en.html",
    "south-africa-talent-skills-shortage-2026.html",
    "south-africa-transfer-duty-foreign-buyer-cape-town-tax-guide-2026.html",
    "cape-town-rental-yield-9-49-percent-reality-check-2026-en.html",
    "cape-town-property-investment-rates-net-return-2026-en.html",
]

PATTERNS = {
    "title": r"<title>(.*?)</title>",
    "description": r'<meta\s+name="description"\s+content="(.*?)"',
}


def extract(p: Path) -> dict:
    c = p.read_text(encoding="utf-8")
    out = {}
    for k, pat in PATTERNS.items():
        m = re.search(pat, c, re.S | re.I)
        out[k] = (m.group(1).strip() if m else "")
    out["sha256"] = hashlib.sha256(
        (out["title"] + "\n" + out["description"]).encode("utf-8")
    ).hexdigest()[:16]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    a = ap.parse_args()

    cur = {}
    for f in PAGES:
        p = BLOG / f
        cur[f] = extract(p) if p.exists() else {"title": "(MISSING)", "description": "", "sha256": "MISSING"}

    if a.update:
        MANIFEST.write_text(
            json.dumps(
                {"strategy": "S-20261019-03", "freeze_until": FREEZE_UNTIL.isoformat(),
                 "recorded_at": date.today().isoformat(), "pages": cur},
                ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"✅ 凍結基準已寫入 {MANIFEST}（{len(cur)} 頁）")
        for f, v in cur.items():
            print(f"  {f}\n    title: {v['title']}\n    sha: {v['sha256']}")
        return 0

    if not MANIFEST.exists():
        print(f"❌ 基準檔不存在：{MANIFEST}（先跑 --update）")
        return 2

    base = json.loads(MANIFEST.read_text(encoding="utf-8"))["pages"]
    frozen = date.today() < FREEZE_UNTIL
    changed = []
    for f in PAGES:
        old, new = base.get(f, {}), cur[f]
        if old.get("sha256") != new["sha256"]:
            changed.append(f)
            print(f"{'🔴 VIOLATION' if frozen else 'ℹ️ changed'} {f}")
            print(f"   舊: {old.get('title')}")
            print(f"   新: {new['title']}")

    if not changed:
        print(f"✅ 6 頁 meta 未變動（凍結至 {FREEZE_UNTIL}；今日 {date.today()}）")
        return 0

    if frozen:
        print(f"\n❌ 凍結期內（至 {FREEZE_UNTIL}）有 {len(changed)} 頁 title/desc 被改 —— 請退回，"
              f"或先取得土星人書面解凍。")
        return 1
    print(f"\n✅ 凍結期已過（{FREEZE_UNTIL}），{len(changed)} 頁變動屬預期。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
