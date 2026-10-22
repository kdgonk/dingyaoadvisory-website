#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站 footer 統一：舊版「合作體系 / Partner Network」→ 標準版「戰略生態系 / Strategic Ecosystem」。

土星人 2026-10-20 第 3 批規格（實測 349 HTML）：
  ZH 標準版 5 / EN 標準版 5 / ZH 舊版 169 / EN 舊版 161 / 無 footer 6 / 無夥伴欄 3

舊版問題
  1. 位置錯：在 footer-grid 收合之後、footer-bottom 之前
  2. 只有 2 個夥伴（缺 Standard Bank、Garlicke & Bousfield）
  3. 帶 UTM 參數（標準版沒有）
標準版位置：footer-grid 內部第二欄，social 之後、核心服務之前

實作要點
  - 標準版區塊從實檔抽取，不硬編碼（byte-identical）
  - 舊版區塊用「<div> 括號配對」精確切出，不用貪婪 regex
    （英文舊版 </ul> 之後還有一個 <a>，regex .*?</ul>\\s*</div> 會漏）

用法：
    python3 unify_footer.py --dry     # 只報告
    python3 unify_footer.py           # 實際寫入
"""
import pathlib
import re
import sys
from collections import Counter

DIST = pathlib.Path("dist")
STD_CN = "dist/blog/standard-bank-non-resident-account-2026.html"
STD_EN = "dist/blog/standard-bank-non-resident-account-2026-en.html"

TAG_RE = re.compile(r"<div\b[^>]*>|</div>")


def div_span(text: str, mark_pos: int):
    """回傳包住 mark_pos 的最內層 <div>…</div> 的 (start, end)。"""
    start = text.rfind("<div", 0, mark_pos)
    if start < 0:
        return None
    depth = 0
    for m in TAG_RE.finditer(text, start):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return start, m.end()
        else:
            depth += 1
    return None


def extract_block(path, h4_text):
    c = pathlib.Path(path).read_text(encoding="utf-8")
    k = c.find(f"<h4>{h4_text}</h4>")
    if k < 0:
        raise SystemExit(f"❌ 標準版找不到 <h4>{h4_text}</h4>：{path}")
    span = div_span(c, k)
    if not span:
        raise SystemExit(f"❌ 無法配對 div：{path}")
    return c[span[0]:span[1]], c, span


def normalize_indent(block: str, indent: str = "      ") -> str:
    """把抽取的區塊重新縮排到 footer-grid 子元素層級。"""
    lines = block.split("\n")
    if len(lines) == 1:                      # 單行
        return indent + block.strip()
    out = [indent + lines[0].strip()]
    for ln in lines[1:]:
        out.append(indent + ln.strip() if ln.strip() else "")
    # 區塊內 ul/li 需要比 div 多一層
    result = []
    for ln in out:
        if ln.strip().startswith(("<ul>", "<li>", "</ul>")):
            result.append("  " + ln)
        else:
            result.append(ln)
    return "\n".join(result)


def process(path: pathlib.Path, blocks: dict, dry: bool):
    try:
        c = path.read_text(encoding="utf-8")
    except Exception:
        return "SKIP", "讀取失敗"
    if "<footer" not in c:
        return "SKIP", "無 footer"

    is_en = path.stem.endswith("-en")
    std_mark = "Strategic Ecosystem" if is_en else "戰略生態系"
    old_mark = "Partner Network" if is_en else "合作體系"
    anchor_h4 = "Core Services" if is_en else "核心服務"

    i = c.find("<footer")
    j = c.find("</footer>", i)
    if i < 0 or j < 0:
        return "SKIP", "footer 不完整"
    foot = c[i:j]

    # ── 依 footer 實際內容校正語系（13 檔英文頁用 <h4>Services</h4>；
    #    article-template.html 是中英混合模板，不能只看檔名）────────────
    h4s = re.findall(r"<h4>(.*?)</h4>", foot)
    has_cn_old = "合作體系" in foot
    has_en_old = "Partner Network" in foot
    if has_cn_old and not has_en_old:
        other = [h for h in h4s if "合作體系" not in h]
        cjk = sum(1 for h in other if re.search(r"[\u4e00-\u9fff]", h))
        is_en = cjk < len(other)          # 其他欄多為英文 → 用英文區塊
    elif has_en_old and not has_cn_old:
        other = [h for h in h4s if "Partner Network" not in h]
        cjk = sum(1 for h in other if re.search(r"[\u4e00-\u9fff]", h))
        is_en = cjk < len(other)

    std_mark = "Strategic Ecosystem" if is_en else "戰略生態系"
    old_mark = "Partner Network" if is_en else "合作體系"
    if has_cn_old and not has_en_old:
        old_mark_candidates = ["合作體系", "Partner Network"]
    else:
        old_mark_candidates = ["Partner Network", "合作體系"]
    anchor_candidates = ["Core Services", "Services", "核心服務"]

    has_std = f"<h4>{std_mark}</h4>" in foot
    has_old = any(f"<h4>{m}</h4>" in foot for m in old_mark_candidates)

    if has_std and not has_old:
        return "ALREADY", "已是標準版"
    if not has_std and not has_old:
        return "NOPARTNER", "footer 內無夥伴欄"

    new = c
    notes = []

    # ① 先刪舊版（用 div 配對）
    if has_old:
        old_mark = next(m for m in old_mark_candidates if f"<h4>{m}</h4>" in foot)
        k = new.find(f"<h4>{old_mark}</h4>", i)
        span = div_span(new, k)
        if not span:
            return "FAIL", "舊版 div 無法配對"
        # 連同前面的換行一起吃掉，避免留下空行
        s, e = span
        while s > 0 and new[s - 1] in "\n\r":
            s -= 1
        new = new[:s] + new[e:]
        notes.append("移除舊版")

    # ② 插入標準版到核心服務之前
    if not has_std:
        a = -1
        for cand in anchor_candidates:
            a = new.find(f"<h4>{cand}</h4>", i)
            if a >= 0:
                break
        if a < 0:
            return "FAIL", f"找不到錨點 {anchor_candidates}"
        anchor_span = div_span(new, a)
        if not anchor_span:
            return "FAIL", "核心服務 div 無法配對"
        block = normalize_indent(blocks["en" if is_en else "zh"])
        new = new[:anchor_span[0]] + block + "\n" + new[anchor_span[0]:]
        notes.append("插入標準版")

    # ③ 驗證
    ni = new.find("<footer")
    nj = new.find("</footer>", ni)
    nfoot = new[ni:nj]
    if f"<h4>{std_mark}</h4>" not in nfoot:
        return "FAIL", "驗證失敗：標準版未出現"
    if f"<h4>{old_mark}</h4>" in nfoot:
        return "FAIL", "驗證失敗：舊版殘留"

    if not dry:
        path.write_text(new, encoding="utf-8")
    return "OK", " + ".join(notes)


def main():
    dry = "--dry" in sys.argv
    print("=" * 70)
    zh_block, _, _ = extract_block(STD_CN, "戰略生態系")
    en_block, _, _ = extract_block(STD_EN, "Strategic Ecosystem")
    print(f"標準版區塊：ZH {len(zh_block)}B / EN {len(en_block)}B")
    print("=" * 70)

    blocks = {"zh": zh_block, "en": en_block}
    stats = Counter()
    fails = []

    for f in sorted(DIST.rglob("*.html")):
        status, note = process(f, blocks, dry)
        stats[status] += 1
        if status == "FAIL":
            fails.append((f, note))

    print(f"\n{'[DRY RUN] ' if dry else ''}結果：")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    if fails:
        print(f"\n❌ 失敗 {len(fails)} 檔：")
        for f, n in fails[:15]:
            print(f"   {f}: {n}")
        sys.exit(1)
    print("\n✅ 全部處理完成")


if __name__ == "__main__":
    main()
