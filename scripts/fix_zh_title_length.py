#!/usr/bin/env python3
"""DEPRECATED（2026-11-04）：已被 scripts/normalize_zh_blog_titles.py 取代。

為什麼廢掉：
  舊版 MAX=65、品牌用「鼎曜國際顧問 DingYao Advisory」，而且最致命的
  `return content  # bare content (should be <=60)` —— 品牌塞不下時直接
  **丟掉品牌**，正是 2026-11-04「title 沒有品牌／品牌被截」的結構性風險。

本檔保留僅為回溯相容：執行時直接委派給 normalize_zh_blog_titles.py
（同一套 BRAND/MAX 規則、絕不丟品牌、超長必須人工裁決）。
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(REPO, "scripts", "normalize_zh_blog_titles.py")

if __name__ == "__main__":
    print("⚠️  fix_zh_title_length.py 已棄用 → 轉呼叫 scripts/normalize_zh_blog_titles.py")
    os.execv(sys.executable, [sys.executable, TARGET, *sys.argv[1:]])
