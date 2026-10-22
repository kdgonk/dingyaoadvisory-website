#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 7 批：全站移除南非定存訊息，只講活存 7%（老闆 2026-10-20 指示）

老闆原文：「我不要有『南非1年定存 7.72%』這類定存的訊息。我目前全站都要講活存 7% 就好。」

★★ 語系必須分流：中文用「約 7%」、英文用「about 7%」
   （第一版寫死中文，導致英文檔混入 37 處中文，已修正）

★ 絕對保護：
   - 租金收益率 7.5-11.4%（不是定存）
   - 台灣定存 / 台幣定存 / 美元定存（對比基準，老闆只說南非）
   - 倍數 5-8 倍（不是利率）
   - URL slug（fixed-deposit 保留，避免 404）
"""
import pathlib
import re
import sys
from collections import Counter

# ══════════════════════════════════════════
# P1：完整片語（含數字）—— 中文
# ══════════════════════════════════════════
CN_PHRASES = [
    # 8.15%
    ("南非高息定存最高 8.15%", "南非高利活存 約 7%"),
    ("南非 ZAR 定存最高 8.15%", "南非 ZAR 活存 約 7%"),
    ("南非高息定存最高可達 8.15%", "南非高利活存 約 7%"),
    ("12 個月定存利率最高可達 8.15%（如 Standard Bank）", "活存利率 約 7%（如 Standard Bank Money Market Select）"),
    ("12個月定存利率最高可達 8.15%（如 Standard Bank）", "活存利率 約 7%（如 Standard Bank Money Market Select）"),
    ("12 個月定存利率最高可達 8.15%", "活存利率 約 7%"),
    ("12個月期定存最高約 8.75%", "活存利率 約 7%"),
    ("12 個月期定存最高約 8.75%", "活存利率 約 7%"),
    ("南非 ZAR 定存最高", "南非 ZAR 活存"),
    ("南非高息定存最高", "南非高利活存"),
    # 4.0-6.05%
    ("南非主要銀行的 12 個月定存利率約在 4.0%-6.05% 之間", "南非主要銀行的活存利率約 7%"),
    ("南非主要銀行的 12 個月定存利率約在 4.0-6.05% 之間", "南非主要銀行的活存利率約 7%"),
    ("南非主要銀行的定存利率約在 4.0%-6.05% 之間", "南非主要銀行的活存利率約 7%"),
    ("南非高息定存 4.0-6.05%", "南非高利活存 約 7%"),
    ("南非高息定存 4.0%-6.05%", "南非高利活存 約 7%"),
    ("南非高息定存（4.0-6.05%）", "南非高利活存（約 7%）"),
    ("南非高息定存（4.0%-6.05%）", "南非高利活存（約 7%）"),
    ("ZAR 定存 4.0-6.05%", "ZAR 活存 約 7%"),
    ("ZAR 定存 4.0%-6.05%", "ZAR 活存 約 7%"),
    ("南非高息定存：第二引擎（ZAR 定存 4.0-6.05%）", "南非高利活存：第二引擎（ZAR 活存 約 7%）"),
    ("南非高息定存：第二引擎（ZAR 定存 4.0%-6.05%）", "南非高利活存：第二引擎（ZAR 活存 約 7%）"),
    # 7-8%
    ("南非定存利率 7-8%", "南非活存利率 約 7%"),
    ("南非定存 7-8%", "南非活存 約 7%"),
    ("南非高息定存 7-8%", "南非高利活存 約 7%"),
    ("南非定存利率約 7-8%", "南非活存利率 約 7%"),
    ("南非定存利率 約 7-8%", "南非活存利率 約 7%"),
    ("南非定存約 7-8%", "南非活存 約 7%"),
    # 7-11%
    ("南非高息定存 約 7-11%", "南非高利活存 約 7%"),
    ("南非高息定存約 7-11%", "南非高利活存 約 7%"),
    ("南非定存 7-11%", "南非活存 約 7%"),
    # 8% / 級距
    ("南非銀行約 8% 的浮動定存利率", "南非銀行約 7% 的活存利率"),
    ("南非銀行約 8% 浮動定存利率", "南非銀行約 7% 活存利率"),
    ("約 8% 的浮動定存利率", "約 7% 的活存利率"),
    ("Standard Bank Wealth 活存級距 6.5%-7.30%", "Standard Bank 活存約 7%"),
    # 語意去重
    ("約 約 7%", "約 7%"),
    ("最高約 約 7%", "約 7%"),
    ("約 7%，部分方案最高可達 <strong>約 7%</strong>", "約 7%"),
    ("約 7%，部分方案最高可達 約 7%", "約 7%"),
    ("最高可達 <strong>約 7%</strong>", "約 7%"),
    ("最高可達 約 7%", "約 7%"),
    ("（部分方案約 7%）", ""),
    # standard-bank 內文段落的殘留定存描述（表格列已由 TR_DELETES 刪除）
    ("、Fixed Deposit 最高 9.75%（原註：Rate at Maturity for Deposit below R100,000）", ""),
    ("、Fixed Deposit 最高 9.75%", ""),
    ("Fixed Deposit 最高 9.75%", "活存約 7%"),
    # 中文語意順化（原「7-11%」→「約 7%」後接「變成」不順）
    ("活存族", "定存族"),  # 修回過度替換：「定存族」指台灣投資人，不是南非產品
    ("變成 約 7%", "變成 7%"),
    ("變成約 7%", "變成 7%"),
    ("達到 約 7%", "達到 7%"),
    ("創造 約 7%", "創造 7%"),
    # 排版：中文之間不需要空格
    ("活存 約 7%", "活存約 7%"),
    ("利率 約 7%", "利率約 7%"),
    ("最高 約 7%", "最高約 7%"),
    ("帳戶 約 7%", "帳戶約 7%"),
]

EN_PHRASES = [
    ("South African fixed deposit rates", "South African high-yield call account rates"),
    ("South African fixed deposits", "South African high-yield call accounts"),
    ("South African fixed deposit", "South African high-yield call account"),
    ("SA fixed deposit rates", "SA high-yield call account rates"),
    ("SA fixed deposit", "SA high-yield call account"),
    ("SA Deposits", "SA Call Accounts"),
    ("ZAR fixed deposit", "ZAR high-yield call account"),
    ("fixed deposit rates", "high-yield call account rates"),
    ("fixed deposit rate", "high-yield call account rate"),
    ("Fixed Deposit rates", "High-yield call account rates"),
    ("Fixed deposit rates", "High-yield call account rates"),
    ("Fixed Deposit", "High-yield call account"),
    ("Fixed deposit", "High-yield call account"),
    ("fixed deposit", "high-yield call account"),
    ("FIXED DEPOSIT", "HIGH-YIELD CALL ACCOUNT"),
    ("12-month fixed deposit", "call account"),
    ("12 month fixed deposit", "call account"),
    ("1-year fixed deposit", "call account"),
    ("time deposit", "call account"),
    ("Time Deposit", "Call Account"),
    ("high-yield call account rates are only", "call account rates are only"),
    # 語意修正（"High-Interest Fixed Deposit" → 換名後變成重複）
    ("High-Interest High-yield call account", "High-Yield Call Account"),
    ("High-interest high-yield call account", "High-yield call account"),
    ("High-Interest high-yield call account", "High-Yield Call Account"),
    ("High-Yield High-yield call account", "High-Yield Call Account"),
    ("high-interest high-yield call account", "high-yield call account"),
    ("(some products up to about 7%)", ""),
    ("up to about 7%", "about 7%"),
]

# ══════════════════════════════════════════
# 純數字規則（依語系決定 approx 詞）
# ══════════════════════════════════════════
NUM_PATTERNS = [
    "4.0%-6.05%", "4.0-6.05%", "4.0%–6.05%",
    "6.5%-7.30%", "6.5%~7.30%", "6.5-7.30%",
    "7.10%-7.45%", "7.10%~7.45%", "7.10%／7.45%",
    "7.30%", "7.45%", "7.10%",
    "8.15%", "8.75%", "7.72%",
    "7-8%", "7~8%",
    "7-11%", "7~11%",
]

# ══════════════════════════════════════════
# P2：名詞替換（中文）
# ══════════════════════════════════════════
CN_NOUNS = [
    ("南非高息定存", "南非高利活存"),
    ("南非高利定存", "南非高利活存"),
    ("南非幣定存", "南非幣活存"),
    ("南非 ZAR 定存", "南非 ZAR 活存"),
    ("南非定存", "南非活存"),
    ("ZAR 高息定存", "ZAR 高利活存"),
    ("ZAR 定存", "ZAR 活存"),
    ("高息定存", "高利活存"),
    ("一年定存", "活存"),
    ("1年定存", "活存"),
    ("12個月期定存", "活存"),
    ("12 個月期定存", "活存"),
    ("12個月定存", "活存"),
    ("12 個月定存", "活存"),
    ("定存利率對照", "活存利率對照"),
    ("定存利率目前是多少", "活存利率目前是多少"),
    ("定存利率", "活存利率"),
    ("定存帳戶", "活存帳戶"),
    ("定存產品", "活存產品"),
    ("存入定存", "存入活存"),
    ("定存保底", "活存保底"),
    ("開定存", "開活存"),
    ("南非的定存", "南非的活存"),
    ("定存的優勢", "活存的優勢"),
    ("定存", "活存"),
]

# ══════════════════════════════════════════
# 保護
# ══════════════════════════════════════════
PROTECT = [
    "7.5-11.4%", "7.5%-11.4%", "7.5–11.4%",
    "台灣定存", "台幣定存", "台灣的定存", "台灣 1 年定存", "台灣1年定存",
    "Taiwan fixed deposit", "Taiwanese fixed deposit", "Taiwan time deposit",
    "Taiwan deposits", "Taiwanese deposits",
    "USD fixed deposit", "美元定存", "美元 fixed deposit",
    "TWD/USD fixed deposit", "TWD fixed deposit",
    "人民幣定存", "日圓定存", "歐元定存", "外幣定存", "澳幣定存",
    "定存族",  # 指習慣定存的台灣投資人，非南非產品
    "fixed-deposit",  # URL slug
    "5-8 倍", "5-8倍", "5-8 times",
    # 資料來源書名（引用外部文章標題，不可改）
    "Best Fixed Deposit Rates South Africa",
    "Best Fixed Deposit",
]

# 整列刪除：真正的定存產品列（土星人規則 C）
TR_DELETES = [
    re.compile(r'\s*<tr><td>Standard Bank Fixed Deposit</td>.*?</tr>', re.S),
    re.compile(r'\s*<tr><td>[^<]*Fixed Deposit[^<]*</td>.*?</tr>', re.S),
]


def apply(text, is_en=False):
    stats = Counter()
    approx = "about " if is_en else "約 "

    # 1. 保護
    placeholders = {}
    for i, p in enumerate(PROTECT):
        if p in text:
            ph = f"\x00PROT{i}\x00"
            placeholders[ph] = p
            text = text.replace(p, ph)

    # 1b. 刪除真正的定存產品列（規則 C）
    for rx in TR_DELETES:
        text, n = rx.subn("", text)
        if n:
            stats["TR_DELETE"] += n

    # 2. 片語（依語系）
    phrases = (EN_PHRASES if is_en else []) + (CN_PHRASES if not is_en else [])
    # 英文檔也需處理中文片語殘留（少數），但只用不含中文輸出的
    for old, new in phrases:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            stats[old[:26]] += n

    # 3. 純數字（依語系 approx）
    for pat in NUM_PATTERNS:
        n = text.count(pat)
        if n:
            text = text.replace(pat, approx + "7%")
            stats["NUM:" + pat] += n

    # 4. 中文名詞（只在中文檔；英文檔不該有中文名詞）
    if not is_en:
        for old, new in CN_NOUNS:
            n = text.count(old)
            if n:
                text = text.replace(old, new)
                stats[old] += n
    else:
        # 英文檔殘留的中文名詞也清掉（避免混雜）
        for old, new in CN_NOUNS:
            n = text.count(old)
            if n:
                text = text.replace(old, new)
                stats["EN殘留:" + old] += n

    # 5. 去重
    for _ in range(2):
        text = text.replace(approx + approx + "7%", approx + "7%")
        text = text.replace("最高可達 " + approx + "7%", approx + "7%")
        text = text.replace("最高約 " + approx + "7%", approx + "7%")

    # 5b. 最終修正：P2 的通用「定存→活存」會把「定存族」也改掉，
    #     必須在 P2 之後才修回（「定存族」指台灣投資人）
    if not is_en:
        text = text.replace("活存族", "定存族")

    # 6. 還原
    for ph, p in placeholders.items():
        text = text.replace(ph, p)
    return text, stats


STILL = re.compile(
    r'(南非[^。，,\n<>]{0,10}(?<!台)定存|南非幣定存|ZAR 定存|高息定存|高利定存'
    r'|(?<!台灣)(?<!台)1年定存|12個月?期?定存'
    r'|(?<!Taiwan )(?<!Taiwanese )(?<!TWD/)(?<!TWD )(?<!USD )(?<!Best )(?<!Money)[Ff]ixed[\s][Dd]eposit'
    r'|time deposit)', re.I
)


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = [pathlib.Path(a) for a in args]
    total = Counter()
    residual = []
    changed = 0
    en_mixed = []
    for f in files:
        try:
            c = f.read_text(encoding="utf-8")
        except Exception:
            continue
        is_en = bool(re.search(r'<html[^>]*\slang="en"', c))
        new, st = apply(c, is_en)
        if new != c:
            changed += 1
            if not dry:
                f.write_text(new, encoding="utf-8")
        total.update(st)
        # 英文檔混入中文檢查
        if is_en and "約 7%" in new:
            en_mixed.append((f, new.count("約 7%")))
        res = [m.group(0) for m in STILL.finditer(new)]
        if res:
            residual.append((f, Counter(res)))
    print(f"{'[DRY] ' if dry else ''}{len(files)} 檔，變更 {changed} 檔，替換 {sum(total.values())} 處")
    print("\n=== 替換 TOP 15 ===")
    for k, v in total.most_common(15):
        print(f"  {v:4}x {k}")
    if en_mixed:
        print(f"\n=== ❌ 英文檔混入中文 {len(en_mixed)} 檔 ===")
        for f, n in en_mixed[:8]:
            print(f"  {n:3}x {f}")
    if residual:
        print(f"\n=== ⚠️ 殘留 {len(residual)} 檔 ===")
        for f, cnt in sorted(residual, key=lambda x: -sum(x[1].values()))[:12]:
            print(f"  {sum(cnt.values()):3}x {f}  {dict(cnt.most_common(2))}")
    if not residual and not en_mixed:
        print("\n=== ✅ 無殘留、無語系混雜 ===")


if __name__ == "__main__":
    main()
