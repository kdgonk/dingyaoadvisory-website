#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「暫時註解掉」的 HTML 區塊還原（取消註解）。

為什麼需要（2026-10-28 S-20261028-VALU）：
valuation 頁上線前，fx-tracker ZH/EN 的「相關閱讀」有一條指向它的內連是 live 404，
先用 `<!-- 2026-10-28 titan：... -->` 包起來止血。valuation 上線後必須「確定性」還原，
不能靠人記得或靠 LLM 手動改（容易多刪一個標籤）。

用法：
  python3 scripts/restore_commented_block.py <file> [<file> ...] --marker "2026-10-28 titan"
  python3 scripts/restore_commented_block.py <file> --marker ... --check     # 只檢查，不改檔

行為：
- 找到「開頭為 `<!--` 且含 marker」的那一行，以及其後第一個 `-->` 結尾行
- 只刪掉這兩行包裝，中間內容原樣保留（＝取消註解）
- --check：只回報「還有幾處被註解」，exit 0=已還原 / 1=仍有註解

驗證（呼叫端請自行再 grep href 數）：
  grep -c 'href="/blog/<slug>"' <file>   # 還原後應 >= 1
"""
import sys
from pathlib import Path


def find_blocks(lines, marker):
    """回傳 [(start_idx, end_idx)]，指涉 `<!--` 與 `-->` 兩行。"""
    blocks, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if "<!--" in ln and marker in ln:
            j = i + 1
            while j < len(lines) and "-->" not in lines[j]:
                j += 1
            if j < len(lines):
                blocks.append((i, j))
                i = j + 1
                continue
        i += 1
    return blocks


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    marker = None
    files = []
    it = iter(args)
    for a in it:
        if a == "--marker":
            marker = next(it, None)
        elif a.startswith("--marker="):
            marker = a.split("=", 1)[1]
        elif a in ("--check",):
            continue
        else:
            files.append(a)
    if not marker or not files:
        print("用法: restore_commented_block.py <file...> --marker '文字' [--check]")
        return 2

    total_blocks = 0
    rc = 0
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"❌ 找不到檔案: {f}")
            rc = 2
            continue
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        blocks = find_blocks(lines, marker)
        total_blocks += len(blocks)
        if not blocks:
            print(f"  ✅ {p.name}：已無 marker「{marker}」註解")
            continue
        if check:
            print(f"  ⚠️  {p.name}：仍有 {len(blocks)} 處被註解（--check 未改檔）")
            rc = 1
            continue
        # 由後往前刪，避免索引位移
        for start, end in reversed(blocks):
            del lines[end]
            del lines[start]
        p.write_text("".join(lines), encoding="utf-8")
        print(f"  ✅ {p.name}：已還原 {len(blocks)} 處註解")

    print()
    if check:
        print(f"檢查完成：仍有 {total_blocks} 處註解")
    else:
        print(f"還原完成：共處理 {total_blocks} 處（原本已是開啟狀態則為 0）")
    return rc


if __name__ == "__main__":
    sys.exit(main())
