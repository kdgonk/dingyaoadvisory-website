#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-18 泰坦人（第二階段）：補回 nav / CTA 的「狀態規則」

為什麼需要這一步：
土星人提供的 /tmp/missing_navfooter.css 只涵蓋 30 條靜態 selector，
少了 4 條狀態規則 —— 其中最致命的是 `.nav-item.has-dd:hover .nav-dd{opacity:1;visibility:visible;…}`。
只補前 30 條 → 下拉選單永遠 visibility:hidden（量測「hidden」看起來 PASS，實際滑鼠移上去不會展開，
選單變成完全不能用）。這 4 條一律從基準檔逐字取出，不手寫：

  1. .nav-item.has-dd:hover .nav-dd,.nav-item.has-dd:focus-within .nav-dd{opacity:1;visibility:visible;…}
  2. .nav-dd a:hover{background:rgba(201,168,76,.1)}
  3. .nav-dd a::after{display:none}
  4. .crestline-assist li::before{…}   ← 清單圓點；只有完全沒有 crestline CSS 的檔需要

插點：`/* ===== nav LOGO` 這行之前（即 nav 群組的最前面）。
理由：nav 群組本身含 `@media(max-width:768px)` 會覆寫 transform，狀態規則必須排在該 media 之前，
否則手機版下拉會被 translateX(-50%) 位移。

用法：python3 scripts/fix_missing_navfooter_css_2026_11_18b.py [--dry-run]
"""
import os
import re
import sys
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(BASE, "dist", "blog")
BASELINE = "foreign-buyers-atlantic-seaboard-1-3-cape-town-r6bn-2026.html"
MARKER = "/* ===== nav LOGO"

TARGETS = [
    "south-africa-fixed-deposit-rate-comparison-taiwan-banks-2026",
    "south-africa-fixed-deposit-rate-comparison-taiwan-banks-2026-en",
    "south-africa-school-curriculum-caps-ieb-cambridge-2026",
    "south-africa-school-curriculum-caps-ieb-cambridge-2026-en",
]

# (規則全文, 冪等探針) —— 全文必須能在基準檔內逐字找到，否則中止
SUPPLEMENT = [
    (".nav-item.has-dd:hover .nav-dd,.nav-item.has-dd:focus-within .nav-dd"
     "{opacity:1;visibility:visible;transform:translateX(-50%) translateY(0)}",
     ".nav-item.has-dd:focus-within .nav-dd"),
    (".nav-dd a:hover{background:rgba(201,168,76,.1)}", ".nav-dd a:hover"),
    (".nav-dd a::after{display:none}", ".nav-dd a::after"),
    (".crestline-assist li::before"
     "{content:'';position:absolute;left:0;top:.72em;width:6px;height:6px;border-radius:50%;background:#C9A84C}",
     ".crestline-assist li::before"),
]


def main(apply=True):
    baseline = open(os.path.join(BLOG, BASELINE), encoding="utf-8").read()
    for rule, _ in SUPPLEMENT:
        if rule not in baseline:
            raise SystemExit("中止：基準檔找不到這條規則（規則可能已改寫）→ " + rule[:60])

    stat = {"baseline": BASELINE, "files": {}}
    for name in TARGETS:
        path = os.path.join(BLOG, name + ".html")
        html = open(path, encoding="utf-8").read()
        need = []
        for rule, probe in SUPPLEMENT:
            if probe in html:
                continue
            # crestline 規則只在該檔完全沒有 crestline CSS 時才需要（否則原有 ::before 已存在）
            need.append(rule)
        if not need:
            stat["files"][name] = "already ok"
            continue

        i = html.find(MARKER)
        if i < 0:
            raise SystemExit(f"中止：{name} 找不到 nav 群組標記，請人工確認插點")
        # 對齊標記所在行的縮排（這些檔標記都在行首）
        chunk = "\n".join(need) + "\n"
        html = html[:i] + chunk + html[i:]
        if apply:
            open(path, "w", encoding="utf-8").write(html)
        stat["files"][name] = [r.split("{")[0] for r in need]
    print(json.dumps(stat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main("--dry-run" not in sys.argv)
