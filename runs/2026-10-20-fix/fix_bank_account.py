#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""土星人 2026-10-20 修正派工：/south-africa-bank-account 五處文案事實修正。

原則：
  1. 同一段文字同時存在於「HTML 內文」與「JSON-LD FAQPage」→ 兩邊同步改，
     否則 schema 與頁面不一致（Google 視為違規）。
  2. meta description / og / twitter 含錯誤事實（簽約主體）→ 一併修，replace_all。
  3. 每項替換都驗證命中次數，沒命中就報錯（不靜默跳過）。
"""
import pathlib
import sys

P = pathlib.Path("dist/south-africa-bank-account.html")
c = P.read_text(encoding="utf-8")
orig = c

EDITS = []


def sub(old, new, expect, label, all_=False):
    """expect: 預期命中次數；all_=True 表示全部替換"""
    EDITS.append((old, new, expect, label, all_))


# ══════════ 【1】利率階梯 → 移除級距，只留約 7% + 最低門檻 ══════════
sub(
    "Standard Bank Money Market Select 於 2026-10-02 公告 7.10% 至 7.45%，台灣一年期定存固定利率 1.700%，但南非幣貶值超過 5.40% 利差即歸零。",
    "Standard Bank Money Market Select 約 7%（2026-10-02 牌告 7.10% 至 7.45%），最低開戶金額 R100,000 起（約新台幣 17 萬元）；台灣一年期定存固定利率 1.700%。",
    3, "meta description ×3（利率+門檻）", True,
)

sub(
    "當地 Money Market Select 於 2026-10-02 公告 7.10% 至 7.45%。差距要看你往來銀行的牌告與額度限制，不是固定倍數，也不是換銀行就能解決。",
    "當地 Money Market Select 約 7%（2026-10-02 牌告 7.10% 至 7.45%），最低開戶金額 R100,000 起（約新台幣 17 萬元）。差距要看你往來銀行的牌告與額度限制，不是固定倍數，也不是換銀行就能解決。",
    2, "FAQ 內文「利率差多少」（JSON-LD + HTML）",
)

sub(
    "不是。7.10% 至 7.45% 是 2026-10-02 的公開牌告資料，會隨南非儲備銀行政策與各銀行資金成本調整而變動。",
    "不是。7% 是約略值，牌告區間為 7.10% 至 7.45%（2026-10-02），會隨南非儲備銀行政策與各銀行資金成本調整而變動。",
    2, "FAQ「利率是保證的嗎」（JSON-LD + HTML）",
)

sub(
    '南非 Money Market 公告 <strong class="gold-text">7.10%–7.45%</strong>。',
    '南非 Money Market <strong class="gold-text">約 7%</strong>，最低開戶 <strong>R100,000</strong>（約新台幣 17 萬元）。',
    1, "hero 統計卡",
)

sub(
    "<td>7.10%（ZAR 10 萬）／7.45%（ZAR 100 萬以上）</td>",
    "<td>約 7%（2026-10-02 牌告 7.10%–7.45%）</td>",
    1, "比較表「利率水準」級距 → 單一約略值",
)

# ══════════ 【2】簽約主體：Crestline → Standard Bank ══════════
sub(
    "不是。鼎曜國際顧問在開普敦協助你確認資料、準備文件並轉交 Crestline Advisory；帳戶與相關合約的簽約主體是 Crestline Advisory，鼎曜不代收資金、不代為簽約，也不經手任何一筆匯款。",
    "不是。鼎曜提供文件確認與轉交；帳戶及開戶合約之簽約主體為 Standard Bank（南非標準銀行），Crestline Advisory 是協助你完成開戶流程的顧問方，鼎曜與 Crestline 均不代收你的資金。",
    2, "FAQ「誰簽約」（JSON-LD + HTML）", 
)

sub(
    "<tr><td>簽約主體</td><td>台灣的銀行</td><td>Crestline Advisory</td></tr>",
    "<tr><td>簽約主體</td><td>台灣的銀行</td><td>Standard Bank（南非標準銀行）</td></tr>",
    1, "比較表「簽約主體」",
)

sub(
    "<p>由 Crestline 在開普敦與你簽約、送件並對接銀行 KYC。鼎曜不代收資金，也不代為簽約。</p>",
    "<p>由 Crestline 在開普敦協助你送件並對接銀行 KYC；開戶合約的簽約主體是 Standard Bank（南非標準銀行）。鼎曜與 Crestline 均不代收你的資金。</p>",
    1, "流程卡「轉交 Crestline」",
)

sub(
    "南非銀行開戶服務：南非幣高利帳戶的利率比較、FICA 文件準備、格式複核與轉交 Crestline Advisory 簽約。",
    "南非銀行開戶服務：南非幣高利帳戶的利率比較、FICA 文件準備、格式複核，與協助轉交 Crestline Advisory 完成開戶流程。",
    1, "JSON-LD description",
)

sub(
    "開戶文件由鼎曜協助確認並轉交 Crestline Advisory 簽約。",
    "開戶文件由鼎曜協助確認並轉交 Crestline Advisory；帳戶簽約主體為 Standard Bank。",
    3, "meta description ×3（簽約主體）", True,
)

# ══════════ 【3】存款保障：待確認 → CODI ══════════
sub(
    "<tr><td>存款保障</td><td>台灣中央存保（外幣依規定）</td><td>南非機制，上限待確認</td></tr>",
    "<tr><td>存款保障</td><td>中央存保，上限 NT$300 萬</td><td>CODI，每人每家銀行 R100,000</td></tr>",
    1, "比較表「存款保障」",
)

# ══════════ 【4】定存 vs 活存：南非端是活存 ══════════
sub(
    "<p>台灣銀行賣的是外幣牌告利率，不是南非當地利率，價差與額度限制都藏在牌告裡。同樣叫定存，兩邊不是同一個價格。</p>",
    "<p>台灣銀行賣的是外幣牌告利率，不是南非當地利率，價差與額度限制都藏在牌告裡。台灣端是定存（約定期間內不能動用），南非端 Money Market Select 是活存（可隨時動用、無鎖期）—— 南非活存不只利率更高，資金也更靈活，這兩件事經常被混為一談。</p>",
    1, "why-card「同樣叫定存」→ 明示定存/活存差異",
)

sub(
    "<tr><td>利率性質</td><td>銀行自訂外幣牌告</td><td>當地貨幣市場利率，隨央行政策變動</td></tr>",
    "<tr><td>利率性質</td><td>銀行自訂外幣牌告</td><td>當地貨幣市場利率，隨央行政策變動</td></tr>\n          <tr><td>資金動用</td><td>定存，約定期間內動用會減息</td><td>活存，可隨時動用、無鎖期</td></tr>",
    1, "比較表新增「資金動用」列",
)

# ══════════ 【5】匯率吃掉利差 → 整段重寫（對比式） ══════════
sub(
    '<p style="margin:0;color:var(--cream);line-height:1.9;">最壞情況先算：300 萬台幣換成南非幣，若一年後貶 15%，本金剩約 255 萬，加上 7.10% 利息約 21.3 萬，合計約 276.3 萬，仍低於原本的 300 萬。7.10% 減 1.700% 等於 5.40 個百分點，貶超過 5.40% 利差歸零 —— 這是開普敦客戶最常忽略的一段。</p>',
    '<p style="margin:0;color:var(--cream);line-height:1.9;">同樣一筆南非幣，放台灣定存和放南非活存，匯率貶值時的結果完全不同：</p>\n'
    '      <ul style="margin:.85rem 0 0;padding-left:1.25rem;color:var(--cream);line-height:1.9;">\n'
    '        <li style="margin-bottom:.5rem;"><strong>台灣銀行南非幣定存（一年期約 1.70%）</strong>：貶 5.40% 時，1.70% − 5.40% = 實質 <strong style="color:#e0785f;">−3.70%</strong>，本金倒賠。</li>\n'
    '        <li><strong>南非 Standard Bank 活存（約 7.10%）</strong>：貶 5.40% 時，7.10% − 5.40% = 實質 <strong class="gold-text">+1.70%</strong>，仍是正報酬。</li>\n'
    '      </ul>\n'
    '      <p style="margin:.85rem 0 0;color:var(--text-muted);font-size:.9rem;line-height:1.8;">同樣的匯率貶幅，一邊倒賠、一邊仍正報酬 —— 差別在利率夠不夠厚。這是開普敦客戶最常忽略的一段。</p>',
    1, "匯率吃掉利差整段重寫",
)

# ══════════ 執行 ══════════
fail = 0
for old, new, expect, label, all_ in EDITS:
    n = c.count(old)
    if n != expect:
        print(f"FAIL  {label}  預期 {expect} 次，實際 {n} 次")
        fail += 1
        continue
    c = c.replace(old, new)
    print(f"OK    {label}  ({n} 次)")

if fail:
    print(f"\n❌ {fail} 項未命中，未寫檔")
    sys.exit(1)

P.write_text(c, encoding="utf-8")
print(f"\n✅ 已寫入 {P}（{len(orig)} → {len(c)} bytes）")
