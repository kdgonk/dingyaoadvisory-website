#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""移除 /sandile-mbeko 與 /sandile-mbeko-en 的舊版 Tailwind 第二個 nav（P0，土星人 2026-10-30）

病因：兩頁同時存在
  (a) 舊版：<div class="fixed w-full z-50 …pointer-events-none"><nav aria-label="…" class="max-w-7xl mx-auto bg-white/90 …rounded-3xl …"> … </nav></div>
  (b) 新版：<nav class="navbar" id="navbar">
舊版是 Crestline 時代的藍灰配色（text-blue-900 / #0F172A / #C5A059），且 tailwind.min.css 是預編譯檔，
沒有任意色 class（text-[#0F172A] 等）→ 那些 hex 目前是 no-op（這也是「顏色搭不上」的來源）。

本腳本：
  1. 刪除整個舊版 nav wrapper（div + nav），保留 /css/tailwind.min.css（內容區仍有 248 個 Tailwind class）
  2. 舊 hex → 品牌色： #C5A059 → #C9A84C、#0F172A → #0A0E17
  3. 補一段品牌色 override <style>（任意色 class 沒編進 CSS，必須顯式定義才生效）
  4. Cookie 橫幅藍色（bg-blue-900/text-blue-900/hover:bg-blue-800）改黑金 .by-dark / .by-gold-link / .by-gold-hover
  5. body bg-gray-50 → 米白 .by-cream（#F5F0E8）

用法: python3 scripts/fix_sandile_dup_nav_2026_10_30.py --dry|--apply
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(BASE, "dist")
FILES = ["sandile-mbeko.html", "sandile-mbeko-en.html"]

OLD_DIV = '<div class="fixed w-full z-50 top-4 md:top-6 px-4 pointer-events-none">'

BRAND_CSS = """
/* 2026-10-30 泰坦人：舊版頁面殘留色 → 鼎曜品牌色（#0A0E17 墨黑 / #C9A84C 金 / #F5F0E8 米白）
   注意：tailwind.min.css 是預編譯檔，任意色 class（text-[#xxxxxx]）不在其中，故在此顯式定義 */
.text-\\[\\#0A0E17\\]{color:var(--navy-deep,#0A0E17)}
.text-\\[\\#C9A84C\\]{color:var(--gold,#C9A84C)}
.bg-\\[\\#C9A84C\\]{background-color:var(--gold,#C9A84C)}
.border-\\[\\#C9A84C\\]{border-color:var(--gold,#C9A84C)}
.border-\\[\\#0A0E17\\]{border-color:var(--navy-deep,#0A0E17)}
.by-cream{background-color:var(--warm-white,#F5F0E8)!important}
.by-dark{background-color:var(--navy-deep,#0A0E17)!important;color:var(--warm-white,#F5F0E8)!important}
.by-gold-link{color:var(--navy-deep,#0A0E17)!important;text-decoration:underline;font-weight:700}
.by-gold-hover:hover{border-color:var(--gold,#C9A84C)!important;color:var(--gold,#C9A84C)!important}
"""


def fix(path, apply_changes):
    s = open(path, encoding="utf-8").read()
    orig = s
    report = {}

    # 1) 刪除舊版 nav wrapper
    n_removed = 0
    while True:
        ds = s.find(OLD_DIV)
        if ds == -1:
            break
        ns = s.find("<nav", ds)
        ne = s.find("</nav>", ns)
        if ns == -1 or ne == -1:
            break
        de = s.find("</div>", ne) + len("</div>")
        s = s[:ds] + s[de:]
        n_removed += 1
    report["old_nav_removed"] = n_removed

    # 2) 舊 hex → 品牌 hex（class 名內）
    report["hex_C5A059"] = s.count("#C5A059")
    s = s.replace("#C5A059", "#C9A84C")
    report["hex_0F172A"] = s.count("#0F172A")
    s = s.replace("#0F172A", "#0A0E17")

    # 3) Cookie 橫幅藍色 → 黑金（先處理複合 class，再處理單一）
    report["blue_hover_pair"] = s.count("hover:border-blue-900 hover:text-blue-900")
    s = s.replace("hover:border-blue-900 hover:text-blue-900", "by-gold-hover")
    report["blue_900_text"] = s.count("text-blue-900")
    s = s.replace("text-blue-900", "by-gold-link")
    report["blue_900_bg"] = s.count("bg-blue-900")
    s = s.replace("bg-blue-900", "by-dark")
    report["hover_bg_blue_800"] = s.count("hover:bg-blue-800")
    s = s.replace(" hover:bg-blue-800", "")

    # 4) body 底色 → 米白
    report["body_bg_gray50"] = s.count('class="bg-gray-50 ')
    s = s.replace('class="bg-gray-50 ', 'class="by-cream ')

    # 5) 補品牌色 override（只補一次）
    if ".by-cream{" not in s:
        s = s.replace("</style>", BRAND_CSS + "</style>", 1)
        report["brand_css_injected"] = 1

    report["nav_open"] = len(re.findall(r"<nav\b", s))
    report["nav_close"] = s.count("</nav>")
    report["tailwind_css_link"] = s.count("/css/tailwind.min.css")
    report["residual"] = {t: s.count(t) for t in
                          ("text-blue-", "bg-blue-", "border-blue-", "#0F172A", "#C5A059")}

    if apply_changes and s != orig:
        open(path, "w", encoding="utf-8").write(s)
    return report


def main():
    apply_changes = "--apply" in sys.argv
    for f in FILES:
        r = fix(os.path.join(DIST, f), apply_changes)
        print(f, "→", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
