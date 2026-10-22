#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站利率說詞統一「約 7%」（老闆 2026-10-20 定案／土星人最高優先指派）

背景：全站 349 檔中有 111 檔含 6.5%、86 檔含 6.72%、11 檔含 6-7%。
昨天只改服務頁，這次一次清乾淨。

═══ 必須改（我們的南非報價）═══
  6.5% / 6.5% 活存 / 活存利率 6.5%  →  約 7%（EN: about 7%）
  6.72%（有效年利率）              →  併入「約 7%」，不再提複利換算
  6-7% / 6–7%                     →  約 7%

═══ 保留不動（對照組／市場數據）═══
  台灣一年期定存 1.700%
  租金報酬 8-10%、房產增值 8%、SARB prime 10.50%、通膨、CPI
  ★ 6.5-7.0% / 6.0-6.5% / 5.0-5.5% → 租金收益率表格、SARB 政策利率目標（非我們的報價）
     實測：City Bowl 7.5-7.9% 6.5-7.0% 5.5-6.0%（毛/淨收益率表）
           SARB 降息週期目標降至 6.5-7.0%（政策利率）

═══ 衍生數字重算（算術不能矛盾）═══
  R 5,000,000 年利息：R 335,000 → R 350,000（× 7%）
  合計年現金流下限：  R 1,171,000 → R 1,186,000（836,000 + 350,000）
  合計年現金流上限：  R 1,380,000 → R 1,395,000（1,045,000 + 350,000）
  R 16,000,000 月息： R 86,000 → R 93,000（16M × 7% ÷ 12 = 93,333）
  R 16,000,000 日息： R 2,849 → R 3,068（16M × 7% ÷ 365 = 3,068）
  計算機活存利息：    R 347,750 → R 374,500（5,350,000 × 7%）
  計算機年化總收益：  R 2,124,250 → R 2,151,000（836,000 + 374,500 + 940,500）
  計算機 ROI：        13.3% → 13.4%（2,151,000 ÷ 16,000,000）
  slider value="6.5" → value="7"

用法：
  python3 unify_rate_7pct.py --dry    # 只報告
  python3 unify_rate_7pct.py          # 實際套用
"""
import pathlib
import re
import sys

ROOT = pathlib.Path("dist")

# ══════════════════════════════════════════
# 1. 組合句式（最長優先，含 6.72% 的括號整段處理）
# ══════════════════════════════════════════
PHRASES = [
    # ── 中文：6.5% + 有效年利率 6.72% 的各種括號寫法 ──
    ("6.5% 日結月付複利（有效年利率約 6.72%）", "約 7% 日結月付複利"),
    ("6.5% 日結月付複利（有效年利率 6.72%）", "約 7% 日結月付複利"),
    ("6.5% 日結月付複利（有效年利率約6.72%）", "約 7% 日結月付複利"),
    ("6.5% 日結月付複利（有效年利率 6.72%)", "約 7% 日結月付複利"),
    ("6.5%日結月付複利（有效年利率約 6.72%）", "約 7% 日結月付複利"),
    ("6.5% 活存利率（有效年利率 6.72%）", "約 7% 活存利率"),
    ("6.5% 活存利率（有效年利率6.72%）", "約 7% 活存利率"),
    ("6.5%活存利率（有效年利率6.72%）", "約 7% 活存利率"),
    ("6.5% 日結月付複利，有效年利率約 6.72%", "約 7% 日結月付複利"),
    ("6.5% 日結月付複利，有效年利率約6.72%", "約 7% 日結月付複利"),
    ("6.5% 日結月付複利）", "約 7% 日結月付複利）"),
    ("6.5% 日結月付複利", "約 7% 日結月付複利"),
    ("6.5%日結月付複利", "約 7% 日結月付複利"),
    # ── 英文對應 ──
    ("6.5% daily compound, monthly pay", "about 7% daily compound, monthly pay"),
    ("6.5% daily-compounded, paid monthly (effective annual rate approx. 6.72%)", "about 7% daily-compounded, paid monthly"),
    ("6.5% daily-compounded, paid monthly (effective annual rate ~6.72%)", "about 7% daily-compounded, paid monthly"),
    ("6.5% compounded daily, paid monthly (effective annual rate approx. 6.72%)", "about 7% compounded daily, paid monthly"),
    ("6.5% daily-compounded, paid monthly", "about 7% daily-compounded, paid monthly"),
    ("6.5% compounded daily and paid monthly", "about 7% compounded daily and paid monthly"),
    ("6.5% daily-accrued, monthly-compounded", "about 7% daily-accrued, monthly-compounded"),
    ("a 6.5% call-account rate (6.72% effective annual rate)", "an about 7% call-account rate"),
    ("6.5% call-account rate (6.72% effective annual rate)", "about 7% call-account rate"),
    ("6.5% Call-Account Rate", "about 7% Call-Account Rate"),
    ("6.5% call-account rate", "about 7% call-account rate"),
    ("6.5% annual interest, compounded", "about 7% annual interest, compounded"),
    # ── 6-7% 浮動 ──
    ("6-7% 浮動優利活存", "約 7% 浮動優利活存"),
    ("6–7% 浮動優利活存", "約 7% 浮動優利活存"),
    ("6-7% 年化浮動利率", "約 7% 年化浮動利率"),
    ("6–7% 年化浮動利率", "約 7% 年化浮動利率"),
    ("（房產 + 6-7% 浮動優利活存）", "（房產 + 約 7% 浮動優利活存）"),
    ("a 6-7% floating high-yield deposit", "an about 7% floating high-yield deposit"),
    ("a 6-7% annual floating rate", "an about 7% annual floating rate"),
    ("6-7% floating high-yield deposit", "about 7% floating high-yield deposit"),
]

# ══════════════════════════════════════════
# 2. 衍生數字
# ══════════════════════════════════════════
NUM_RULES = [
    ("335,000", "350,000"),
    ("1,171,000", "1,186,000"),
    ("1,380,000", "1,395,000"),
    ("86,000", "93,000"),
    ("2,849", "3,068"),
    ("347,750", "374,500"),
    ("2,124,250", "2,151,000"),
]

# ⚠️ 數字邊界：不能用 str.replace —— 「86,000」是「11,286,000」的子字串，
#    會把資產表 R 11,286,000 誤改成 R 11,293,000。
#    規則：前面不可接數字或逗號，後面不可接數字。
NUM_PATTERNS = [
    (re.compile(r"(?<![\d,])" + re.escape(old) + r"(?!\d)"), new, old)
    for old, new in NUM_RULES
]

# ══════════════════════════════════════════
# 3. 殘留的裸 6.5% / 6.72% / 6-7%（最後清）
#    用語系決定中文「約 7%」或英文「about 7%」
# ══════════════════════════════════════════
RESIDUAL = [
    (re.compile(r"6\.72\s?%"), None),          # 由語系決定
    (re.compile(r"6\.5\s?%"), None),
    (re.compile(r"6\s?[-–]\s?7\s?%"), None),
]


def is_en(c: str) -> bool:
    m = re.search(r'<html[^>]*\blang="([^"]+)"', c)
    if m:
        return m.group(1).lower().startswith("en")
    return False


def process(path: pathlib.Path, dry: bool):
    c = path.read_text(encoding="utf-8", errors="ignore")
    orig = c
    log = {}

    # 1. 組合句式
    n_phrase = 0
    for old, new in PHRASES:
        k = c.count(old)
        if k:
            c = c.replace(old, new)
            n_phrase += k
    if n_phrase:
        log["組合句式"] = n_phrase

    # 2. slider value
    k = c.count('id="interest" min="3" max="10" value="6.5"')
    if k:
        c = c.replace('id="interest" min="3" max="10" value="6.5"',
                      'id="interest" min="3" max="10" value="7"')
        log["slider value"] = k
    k = c.count('id="interestDisplay">6.5%')
    if k:
        c = c.replace('id="interestDisplay">6.5%', 'id="interestDisplay">7%')
        log["slider 顯示"] = k

    # 3. ROI 13.3% → 13.4%（只改計算機那兩處）
    k = c.count('id="totalROI">13.3%')
    if k:
        c = c.replace('id="totalROI">13.3%', 'id="totalROI">13.4%')
        log["ROI"] = k

    # 4. 衍生數字（用 regex 邊界，避免誤傷 11,286,000 之類）
    n_num = {}
    for pat, new, old in NUM_PATTERNS:
        c, k = pat.subn(new, c)
        if k:
            n_num[old] = k
    if n_num:
        log["衍生數字"] = n_num

    # 5. 殘留裸利率（語系分流）
    en = is_en(c)
    rep = "about 7%" if en else "約 7%"
    n_res = 0
    for pat, _ in RESIDUAL:
        c, k = pat.subn(rep, c)
        n_res += k
    if n_res:
        log["殘留裸利率"] = n_res

    # 6. 語意順化：避免「約 約 7%」「about about 7%」
    fix = [
        ("約 約 7%", "約 7%"), ("約約 7%", "約 7%"),
        ("約 7%%", "約 7%"), ("about about 7%", "about 7%"),
        ("about  about 7%", "about 7%"),
        ("an about 7%", "about 7%"),
        ("a about 7%", "a 7%"),
        ("約 7% 的 約 7%", "約 7%"),
    ]
    n_fix = 0
    for old, new in fix:
        k = c.count(old)
        if k:
            c = c.replace(old, new)
            n_fix += k
    if n_fix:
        log["語意順化"] = n_fix

    if not dry and c != orig:
        path.write_text(c, encoding="utf-8")
    return log, c != orig


def main():
    dry = "--dry" in sys.argv
    tag = "[DRY] " if dry else ""
    files = sorted(ROOT.rglob("*.html"))
    changed = []
    for f in files:
        log, ch = process(f, dry)
        if log:
            changed.append((str(f.relative_to(ROOT)), log))

    print(f"{tag}掃描 {len(files)} 檔，需變更 {len(changed)} 檔\n")
    for name, log in changed:
        parts = []
        for k, v in log.items():
            if isinstance(v, dict):
                parts.append(k + ":" + ",".join(f"{a}->{b}x{n}" for a, b, n in
                                                [(a, dict(NUM_RULES)[a], n) for a, n in v.items()]))
            else:
                parts.append(f"{k}x{v}")
        print(f"  {name}")
        print(f"      {' | '.join(parts)}")

    # 驗證殘留
    print("\n=== 殘留檢查 ===")
    left = {}
    for f in files:
        c = f.read_text(encoding="utf-8", errors="ignore")
        for pat, nm in [(r"6\.5\s?%", "6.5%"), (r"6\.72\s?%", "6.72%"), (r"6\s?[-–]\s?7\s?%", "6-7%")]:
            k = len(re.findall(pat, c))
            if k:
                left.setdefault(nm, 0)
                left[nm] += k
    if left:
        print("  ⚠️ 仍有殘留:", left)
    else:
        print("  ✅ 6.5% / 6.72% / 6-7% 全部 0")


if __name__ == "__main__":
    main()
