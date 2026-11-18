#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-18 泰坦人：補回 4 個文章檔缺漏的 nav / footer / CTA CSS

背景：老闆回報 MENU / FOOTER / CTA 排版壞掉。實測只有 4 檔（兩篇文章的中英版）
缺 30 條 selector，其餘 308 檔正常。缺的內容由土星人抽好放在
/tmp/missing_navfooter.css（3,591 字元），本腳本只負責「按組插入」，不重寫任何 CSS。

分組（以註解為界）：
  crestline  → 檔案內沒有 `.crestline-assist{` 才插
  nav        → 檔案內沒有 `.nav-dd{` 才插
  footer     → 檔案內沒有 `.footer-wordmark{` 才插
插點：該檔「第一個 <style> 區塊」的 </style> 之前（與既有多條規則不衝突；
      若某組規則已存在則整組跳過，避免同一份 CSS 出現兩次）。
"""
import os
import sys
import glob
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(BASE, "dist", "blog")
CSS_SRC = sys.argv[sys.argv.index("--css") + 1] if "--css" in sys.argv else "/tmp/missing_navfooter.css"

TARGETS = [
    "south-africa-fixed-deposit-rate-comparison-taiwan-banks-2026",
    "south-africa-fixed-deposit-rate-comparison-taiwan-banks-2026-en",
    "south-africa-school-curriculum-caps-ieb-cambridge-2026",
    "south-africa-school-curriculum-caps-ieb-cambridge-2026-en",
]


def split_groups(css: str):
    """用註解把 CSS 切成 crestline / nav / footer 三組。"""
    lines = css.splitlines()
    nav_i = next((i for i, l in enumerate(lines) if l.startswith("/*") and "nav LOGO" in l), None)
    foot_i = next((i for i, l in enumerate(lines) if l.startswith("/*") and "footer brand" in l), None)
    if nav_i is None or foot_i is None:
        raise SystemExit("CSS 切點註解找不到（nav LOGO / footer brand）")
    return {
        "crestline": "\n".join(lines[:nav_i]).strip() + "\n",
        "nav": "\n".join(lines[nav_i:foot_i]).strip() + "\n",
        "footer": "\n".join(lines[foot_i:]).strip() + "\n",
    }


TRIGGER = {
    "crestline": ".crestline-assist{",
    "nav": ".nav-dd{",
    "footer": ".footer-wordmark{",
}


def insert_into_first_style(html: str, chunk: str) -> str:
    """插到第一個 <style> 區塊的 </style> 之前（沿用該區塊尾端換行狀態）。"""
    i = html.find("<style")
    if i < 0:
        raise SystemExit("找不到 <style>")
    j = html.find("</style>", i)
    head = html[:j]
    if not head.endswith("\n"):
        head += "\n"
    return head + chunk + html[j:]


def main(apply=True):
    groups = split_groups(open(CSS_SRC, encoding="utf-8").read())
    stat = {"css_file": CSS_SRC,
            "css_chars": sum(len(v) for v in groups.values()),
            "groups": {k: len(v) for k, v in groups.items()},
            "files": {}}
    for name in TARGETS:
        path = os.path.join(BLOG, name + ".html")
        html = open(path, encoding="utf-8").read()
        added = []
        for g in ("crestline", "nav", "footer"):
            if TRIGGER[g] in html:
                continue
            html = insert_into_first_style(html, groups[g])
            added.append(g)
        if added and apply:
            open(path, "w", encoding="utf-8").write(html)
        stat["files"][name] = added
    print(json.dumps(stat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main("--dry-run" not in sys.argv)
