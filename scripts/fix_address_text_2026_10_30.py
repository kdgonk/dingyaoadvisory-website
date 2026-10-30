#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dingyao 可見文字地址同步（土星人 2026-10-30 v2 配套）

schema 已改用公司登記地址（台中市龍井區），但頁尾/聯絡區的可見文字仍寫「台中市西屯區」，
會與 JSON-LD 自相矛盾。此腳本只換區名（西屯區→龍井區 / Xitun District→Longjing District），
不動版型、不塞入完整門牌（門牌只存在於 schema 的 streetAddress）。

用法: python3 scripts/fix_address_text_2026_10_30.py --dry|--apply
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, "dist")
PAIRS = [("台中市西屯區", "台中市龍井區"), ("Xitun District", "Longjing District")]


def main():
    apply_changes = "--apply" in sys.argv
    n_files = n_hits = 0
    for dp, _dn, fn in os.walk(ROOT):
        for f in sorted(fn):
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding="utf-8").read()
            hits = sum(s.count(a) for a, _b in PAIRS)
            if not hits:
                continue
            n_files += 1
            n_hits += hits
            if apply_changes:
                for a, b in PAIRS:
                    s = s.replace(a, b)
                open(p, "w", encoding="utf-8").write(s)
    print(("APPLY" if apply_changes else "DRY"), f"files={n_files} replacements={n_hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
