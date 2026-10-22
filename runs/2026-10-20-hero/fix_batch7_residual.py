#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 7 批遺漏修正（2026-10-20 第二輪）

發現兩類問題：

A. 「7.10–約 7%」殘缺
   原文「7.10–7.45%」是 Standard Bank Money Market 的**活存浮動利率級距**。
   第 7 批只把「7.45%」換成「約 7%」，留下「7.10–約 7%」這種矛盾寫法。
   → 整段換成「約 7%」（符合老闆「全站統一活存 7%」）

B. 台灣定存被誤改成活存
   老闆只要求「南非」定存改活存，台灣定存是對比基準。
   通用「定存→活存」誤傷：「台灣一年期活存 1.700%」（台灣是定存，不是活存）、
   「台灣端是活存（約定期間內不能動用）」（活存不會有約定期間，明顯矛盾）
   → 還原為「定存」
"""
import pathlib
import re
import sys

FIXES_CN = [
    # A. 7.10–約 7% 殘缺（含 en dash / hyphen / 波浪號變體）
    ("7.10–約 7%", "約 7%"),
    ("7.10-約 7%", "約 7%"),
    ("7.10~約 7%", "約 7%"),
    ("7.10 – 約 7%", "約 7%"),
    ("7.10–7.45%", "約 7%"),
    ("7.10-7.45%", "約 7%"),
    ("7.10%~7.45%", "約 7%"),
    # B. 台灣定存被誤改
    ("台灣一年期活存", "台灣一年期定存"),
    ("台灣 1 年期活存", "台灣 1 年期定存"),
    ("活存固定利率 1.700%", "定存固定利率 1.700%"),
    ("活存固定利率 1.7%", "定存固定利率 1.7%"),
    ("台灣端是活存", "台灣端是定存"),
    ("台灣銀行南非幣活存", "台灣銀行南非幣定存"),
    ("台灣目前一年期活存", "台灣目前一年期定存"),
    ("台灣銀行業的活存與活存利率", "台灣銀行業的定存與活存利率"),
    ("台灣銀行業的活存與活存", "台灣銀行業的定存與活存"),
    ("台灣多數活存", "台灣多數定存"),
    ("台灣的活存利率", "台灣的定存利率"),
    ("台灣活存利率僅", "台灣定存利率僅"),
    # 語意重複清理
    ("約 約 7%", "約 7%"),
    ("定存定存", "定存"),
]

FIXES_EN = [
    ("7.10–about 7%", "about 7%"),
    ("7.10-about 7%", "about 7%"),
    ("7.10 to about 7%", "about 7%"),
    ("7.10–7.45%", "about 7%"),
    ("7.10-7.45%", "about 7%"),
    ("Taiwan one-year call account", "Taiwan one-year fixed deposit"),
    ("Taiwan's one-year call account", "Taiwan's one-year fixed deposit"),
    ("Taiwan call account rates", "Taiwan fixed deposit rates"),
    ("Taiwanese call account", "Taiwanese fixed deposit"),
    ("about about 7%", "about 7%"),
]

SKIP_DIRS = {"blog/images"}


def main():
    dry = "--dry" in sys.argv
    root = pathlib.Path(".")
    files = [f for f in root.rglob("*.html")]
    total = {}
    changed = 0
    for f in files:
        try:
            c = f.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = c
        is_en = bool(re.search(r'<html[^>]*\slang="en"', c))
        rules = (FIXES_EN + FIXES_CN) if is_en else FIXES_CN
        for old, new in rules:
            n = c.count(old)
            if n:
                c = c.replace(old, new)
                total[old] = total.get(old, 0) + n
        if c != orig:
            changed += 1
            if not dry:
                f.write_text(c, encoding="utf-8")
    print("%s%d 檔，變更 %d 檔，替換 %d 處" % (
        "[DRY] " if dry else "", len(files), changed, sum(total.values())))
    for k, v in sorted(total.items(), key=lambda x: -x[1]):
        print("  %3dx %s" % (v, k))

    # 驗證
    print("\n=== 殘留檢查 ===")
    bad = []
    for f in files:
        c = f.read_text(encoding="utf-8")
        for pat in [r'7\.10[–\-~]?約 7%', r'7\.10[–\-~]?about 7%', r'7\.10[–\-~]7\.45%',
                    r'台灣一年期活存', r'台灣端是活存', r'活存固定利率 1\.700%',
                    r'台灣目前一年期活存', r'台灣多數活存', r'台灣銀行業的活存與活存']:
            if re.search(pat, c):
                bad.append((str(f), pat))
                break
    if bad:
        for f, p in bad[:8]:
            print("  ⚠️ %s  ← %s" % (f, p))
    else:
        print("  ✅ 全部清零")


if __name__ == "__main__":
    main()
