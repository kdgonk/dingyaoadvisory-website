#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""property 與 education 文案事實修正（土星人 2026-10-20 補派）

五條判準：
① 幣別一律「南非幣／ZAR」，不得出現「蘭特／蘭德」        → 實測 0，不動
② 利率／收益率數字必須帶來源與日期                       → property 25 個 % 全裸，修
③ 不得「保證收益／零風險／穩賺」；南非定存殘留清掉        → 南非定存 0；「非保證收益」是否定式免責，保留
④ 扣繳率／CODI 上限／非居民房貸 LTV 一律「待確認」        → 房貸段落未填數字但沒明寫待確認，補
⑤ property 頁開普敦濃度 ≥60%                             → ZH 65.4% 達標；EN 35.7% 未達標，補

來源（全部取自站內既有文章，不新編）：
- 租金收益率 9.49%（開普敦）／全國 11.53% → Global Property Guide《South Africa Rental Yields》2026 Q2
- 房價年增 11.4% → Lightstone 統計，經 Pam Golding 引用（至 2026-07）
- 轉讓稅 926,856（R10,450,000 物件）→ SARS 公告 Transfer Duty 稅率（2025-04-01 起生效）
- prime 10.75% → REI.co.za（2026-09-23）
"""
import pathlib
import re
import sys

PROP_ZH = "south-africa-property.html"
PROP_EN = "south-africa-property-en.html"

# ══════════════════════════════════════════
# A. 數據來源區塊（插在免責聲明 <p> 之前）
# ══════════════════════════════════════════
SOURCES_ZH = '''<div class="data-sources" style="margin:2rem auto 0;max-width:760px;text-align:left;font-size:0.78rem;line-height:1.9;color:var(--text-muted);border-top:1px solid rgba(201,168,76,.25);padding-top:1.25rem;">
        <p style="margin:0 0 .6rem;color:var(--gold,#C9A84C);font-weight:600;letter-spacing:.5px;">數據來源與基準日</p>
        <ul style="margin:0;padding-left:1.1rem;">
          <li>開普敦毛租金收益率 9.49%、南非全國公寓平均 11.53%：Global Property Guide《South Africa Rental Yields》（2026 Q2）。方法為中位數月租金 × 12 ÷ 中位數房價；該機構註明最新一期更換資料來源，跨期比較需謹慎。</li>
          <li>買入稅費約房價 9.4%–9.7%、轉讓稅約南非幣 926,856（以 R10,450,000 物件計）：依 SARS 公告 Transfer Duty 稅率（2025-04-01 起生效）計算，並加計律師過戶與登記費實務估算。</li>
          <li>淨租金收益率 7.5%–8.0%：由 9.49% 扣除空置期、代管費（月租金 8%–12%）、市政稅、保險與維修後之估算。</li>
          <li>資本利得有效稅率最高約 18%：資本利得的 40% 納入所得課稅後之估算；實際依持有期間、邊際稅率與個案認定。</li>
          <li>開普敦房價年增約 11.4%：Lightstone 統計，經 Pam Golding 引用（至 2026 年 7 月止）。</li>
        </ul>
      </div>
      '''

SOURCES_EN = '''<div class="data-sources" style="margin:2rem auto 0;max-width:760px;text-align:left;font-size:0.78rem;line-height:1.9;color:var(--text-muted);border-top:1px solid rgba(201,168,76,.25);padding-top:1.25rem;">
        <p style="margin:0 0 .6rem;color:var(--gold,#C9A84C);font-weight:600;letter-spacing:.5px;">Data sources and reference dates</p>
        <ul style="margin:0;padding-left:1.1rem;">
          <li>Cape Town gross rental yield 9.49% and the South African national apartment average of 11.53%: Global Property Guide, <em>South Africa Rental Yields</em> (2026 Q2). Method: median monthly rent × 12 ÷ median property price. The publisher notes it changed data source for the latest edition, so cross-period comparison needs care.</li>
          <li>Acquisition costs of about 9.4%–9.7% of price, and transfer duty of about ZAR 926,856 on a ZAR 10,450,000 property: calculated from the SARS Transfer Duty rate table (effective 2025-04-01), plus conveyancing and registration fees estimated from practice.</li>
          <li>Net rental yield of 7.5%–8.0%: 9.49% less vacancy, management fee (8%–12% of monthly rent), municipal rates, insurance and maintenance.</li>
          <li>Effective capital gains tax of up to about 18%: 40% of the capital gain is included in taxable income; the actual figure depends on holding period, marginal rate and individual circumstances.</li>
          <li>Cape Town house price growth of about 11.4%: Lightstone data cited by Pam Golding (to July 2026).</li>
        </ul>
      </div>
      '''

# ══════════════════════════════════════════
# B. 非居民房貸 LTV → 待確認
# ══════════════════════════════════════════
MORTGAGE_ZH_OLD = "非居民房貸存在但條件較嚴，成數與利率加碼依銀行與開普敦物件而異。"
MORTGAGE_ZH_NEW = "非居民房貸存在但條件較嚴，成數（實際 LTV 待確認）與利率加碼依銀行與開普敦物件而異，本頁不列具體數字。"

MORTGAGE_EN_OLD = "Non-resident lending exists but on stricter terms, with loan-to-value and pricing set by the bank and the property."
MORTGAGE_EN_NEW = "Non-resident lending for Cape Town property exists but on stricter terms: the loan-to-value ratio (actual LTV to be confirmed) and pricing are set by the bank and the property, so no figure is quoted here."

# ══════════════════════════════════════════
# C. EN 開普敦濃度補強（18 段未含 → 補 7 段到 60%+）
# ══════════════════════════════════════════
EN_CONC = [
 ("Understand the tax structure first Acquisition costs run about 9.4% to 9.7% of price",
  "Understand the tax structure first Acquisition costs on a Cape Town property run about 9.4% to 9.7% of price"),
 ("Exit is harder than entry Liquidity, repatriation procedures and capital gains tax decide",
  "Exit is harder than entry Selling a Cape Town property is harder than buying one. Liquidity, repatriation procedures and capital gains tax decide"),
 ("How We Work Four stages we walk through with you",
  "How We Work Four stages we walk through with Cape Town buyers"),
 ("Title, levies, rates and maintenance history are verified, with third-party inspections where needed",
  "Cape Town title deeds, levies, rates and maintenance history are verified, with third-party inspections where needed"),
 ("Crestline Advisory signs the agreement; funds are remitted into the attorney's trust account",
  "Crestline Advisory signs the Cape Town sale agreement; funds are remitted into the attorney's trust account"),
 ("Attorneys handle transfer while we attend condition, keys, utilities and the management handover",
  "Cape Town attorneys handle transfer while we attend condition, keys, utilities and the management handover"),
 ("Because gross yield counts rent only. Net yield counts costs:",
  "Because gross yield counts rent only. On a Cape Town property the net figure counts costs:"),
 ("Model the exit as well: 40% of the capital gain is taxable",
  "Model the Cape Town exit as well: 40% of the capital gain is taxable"),
 ("Judge net, not gross. Cape Town's Southern and Northern Suburbs carry lower rates factors",
  "Judge net, not gross. Cape Town's Southern and Northern Suburbs carry lower rates factors"),
]
EN_CONC2 = [
 ("Start with how long the cash flow can carry the holding costs",
  "Start with how long the cash flow on a Cape Town property can carry the holding costs"),
 ("Yes, subject to Reserve Bank rules and the correct BOP category",
  "Yes — Cape Town rental income can be repatriated subject to Reserve Bank rules and the correct BOP category"),
 ("Ask for documents rather than promises: company registration",
  "Ask your Cape Town adviser for documents rather than promises: company registration"),
]


def process_zh(path, dry):
    p = pathlib.Path(path)
    c = p.read_text(encoding="utf-8")
    orig = c
    hits = []

    # A. 來源區塊
    anchor = '<p style="margin:1.75rem auto 0;max-width:760px;font-size:0.78rem;line-height:1.8;color:var(--text-muted);">本頁數字為市場參考區間'
    if "data-sources" not in c and anchor in c:
        c = c.replace(anchor, SOURCES_ZH + anchor, 1)
        hits.append("A. 新增數據來源與基準日區塊（5 條）")

    # B. LTV 待確認
    if MORTGAGE_ZH_OLD in c:
        c = c.replace(MORTGAGE_ZH_OLD, MORTGAGE_ZH_NEW)
        hits.append("B. 非居民房貸：LTV 改「待確認」、不列數字")

    if not dry and c != orig:
        p.write_text(c, encoding="utf-8")
    return hits, c != orig


def process_en(path, dry):
    p = pathlib.Path(path)
    c = p.read_text(encoding="utf-8")
    orig = c
    hits = []

    # A. 來源區塊
    anchor = '<p style="margin:1.75rem auto 0;max-width:760px;font-size:0.78rem;line-height:1.8;color:var(--text-muted);">Figures are market reference ranges'
    if "data-sources" not in c and anchor in c:
        c = c.replace(anchor, SOURCES_EN + anchor, 1)
        hits.append("A. 新增 Data sources 區塊（5 條）")

    # B. LTV
    if MORTGAGE_EN_OLD in c:
        c = c.replace(MORTGAGE_EN_OLD, MORTGAGE_EN_NEW)
        hits.append("B. Non-resident LTV：改 'to be confirmed'、不列數字")

    # C. 開普敦濃度
    n_conc = 0
    for old, new in EN_CONC + EN_CONC2:
        if old in c and old != new:
            c = c.replace(old, new, 1)
            n_conc += 1
    if n_conc:
        hits.append(f"C. 開普敦濃度補強 {n_conc} 段")

    if not dry and c != orig:
        p.write_text(c, encoding="utf-8")
    return hits, c != orig


def concentration(path, kw):
    c = pathlib.Path(path).read_text(encoding="utf-8")
    m = re.search(r"<main.*?</main>", c, re.S)
    main = m.group(0) if m else c
    main = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", main, flags=re.S)
    texts = [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()
        for x in re.findall(r"<p[^>]*>(.*?)</p>", main, re.S)
    ]
    texts = [t for t in texts if len(t) > 40]
    hit = [t for t in texts if kw in t]
    return len(texts), len(hit), 100 * len(hit) / max(1, len(texts))


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    tag = "[DRY] " if dry else ""
    print(f"{tag}ZH property")
    h, ch = process_zh(PROP_ZH, dry)
    for x in h:
        print("   ", x)
    if not h:
        print("    （無變更）")

    print(f"\n{tag}EN property")
    h, ch = process_en(PROP_EN, dry)
    for x in h:
        print("   ", x)
    if not h:
        print("    （無變更）")

    print("\n=== 開普敦濃度 ===")
    for f, kw in [(PROP_ZH, "開普敦"), (PROP_EN, "Cape Town")]:
        tot, hit, pct = concentration(f, kw)
        flag = "✅" if pct >= 60 else "❌"
        print(f"  {flag} {f}: {hit}/{tot} = {pct:.1f}%")
