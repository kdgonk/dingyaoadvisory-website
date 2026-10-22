# 舊文復活第三批（3 篇）— 改動紀錄與閘門結果

**日期**：2026-10-19 ｜ **執行**：火星人 ｜ **依據**：水星人清單 §三 第 9/10/11 節
**狀態**：未部署、未 push、`dist/` 零改動（`git status` 只有 `?? runs/`）。累計 10 篇。

## 檔案（3 篇目標 + 4 個內連來源頁）

| 角色 | 檔案 |
|---|---|
| 目標 | `overseas-property-investment-guide-cape-town-2026-en.html` |
| 目標 | `international-buyers-cape-town-foreign-property-trends-2026-en.html` |
| 目標 | `imo-2026-south-africa-en.html` |
| 內連來源 | `taiwan-wealthy-overseas-allocation.html`（ZH）、`taiwan-wealthy-overseas-allocation-en.html` |
| 內連來源 | `foreign-buyers-r153bn-cape-town-luxury-10-years-en.html`、`taiwan-parents-choosing-south-africa-private-schools-en.html` |

---

## 1. overseas-property-investment-guide-cape-town-2026-en（+1.2，41i／pos 5.7）

- title：`Overseas Property Guide: Cape Town | DingYao Advisory`（53）→ **`Overseas Property 2026: NT$16M Taipei vs Cape Town Yield`**（56）
- desc：→ 268 字元。**順手修掉既有矛盾**：原 desc 寫「Cape Town yield 7.5-11.4%」，與本站 9.49% 全市平均口徑衝突 → 改為「9.49% vs Taiwan 1.5-2.5%，約 5 倍租金收入」
- **插入 20 年複利表（5 情境，NT$16M 本金）**，置於 H2「Same NT$16M Invested, How Much Difference After 20 Years: Taipei vs Cape Town?」之後：

| 情境 | 年化 | 20 年終值 | 淨增值 |
|---|---|---|---|
| 台北，純房價增值 | 2.0% | NT$23.8M | +NT$7.8M |
| 台北，增值＋租金再投入 | 4.5% | NT$38.6M | +NT$22.6M |
| 開普敦，保守 | 7.0% | NT$61.9M | +NT$45.9M |
| 開普敦，基準 | 9.5% | NT$98.3M | +NT$82.3M |
| 開普敦，樂觀 | 11.0% | NT$129.0M | +NT$113.0M |

  表下註明「annual compounding、收入再投入、匯率不變、未計稅；illustrative arithmetic, not a forecast」
- 來源註：Global Property Guide 2026（9.49% 全市毛收益率）
- 內連：本頁 +1（→ `taiwan-wealthy-overseas-allocation-en`）；來源頁 ZH/EN 各加 1 條回連（解 `q-20261013-004` 舊頁出向 0）

## 2. international-buyers-cape-town-foreign-property-trends-2026-en（+1.1，35i／pos 5.1）

- title：`Foreign Buyers in Cape Town 2026: 40%+ of Luxury`（48）→ **`Foreign Buyers 2026: 40%+ of Cape Town R10M+ Sales`**（51）
- desc：→ 235 字元，把「premium market」換成有來源的口徑（BetterBond：R10M+ 交易 40%+；Lightstone：Atlantic Seaboard 1/3；82% 現金）
- **6 區淨收益表加來源與日期註**：Africanvestor（2026-05，扣管理費／稅／保險後的淨值）＋ 交叉參照 Lightstone deeds（2026-07）與 BetterBond（R10M+ 段）
- 補 2 段市場結構段落（買方結構 vs 租客結構；R10M+ 為全球市場、中段為本地市場），Cape Town 佔比 **64% → 71%**
- 內連：0 → 1（→ `foreign-buyers-r153bn-...-en`）；來源頁加 1 條回連（雙向鏈）

## 3. imo-2026-south-africa-en（+1.0，266i／3c／pos 7.4）

- **title / desc 依報告「投報率最低」不優化**（維持 `South Africa at IMO 2026: Silver, Bronze, 57th Rank`）
- 唯一合規修正：desc 三處原本不同步（156 / 194 / 91 字元）→ 統一為 194 字元版本（技術合規，非 CTR 優化）
- **H2「Implications for South Africa's Investment and Property Market」下補 4 個可查數據點**（報告要 3 個，補到 4 個）：

| 數據點 | 數值 | 來源 |
|---|---|---|
| STEM 畢業生 | 32,141（目標 37,206，短缺 5,065＝−13.6%；工程 −2,541、自然物理 −1,814） | DHET 年報 2023/24 |
| 數理基礎 | 2023 年僅 28,851 名考生數學＋物理皆達 60%；數學考生佔比 53%(2008) → 38.5%(2023) | DBE |
| 外人直接投資 | 2024 流入 US$2.47bn（YoY −28.9%）；存量 US$113bn＝GDP 28.2% | UNCTAD WIR 2025 |
| 人才留存 | 西開普僅佔省際外流 15.1%，全國最高留存率 | Wise Move 2025 |

- 內連：本頁建相關閱讀 3 條；來源頁 `taiwan-parents-choosing-south-africa-private-schools-en` 加 1 條回連（教育主題唯一相關頁）

---

## 🔴 判定「報告建議不可用／需調整」的 3 處

1. **#10 title「40%+ of Cape Town Luxury」→ 改為「40%+ of Cape Town R10M+ Sales」**
   40%+ 有據（BetterBond），但那是 **R10M+ 價格帶**；Lightstone deeds（The Star 2026-07-03）同期口徑是 **Atlantic Seaboard 全部交易 1/3**。若寫「Luxury」會把兩個口徑混成一個，讀者與 Google 都無法分辨。改為 R10M+ 後兩組數字都成立且互補。

2. **#10 建議的「5 區淨收益率表」（Atlantic Seaboard／City Bowl／Southern Suburbs／Northern Suburbs／False Bay）→ 不採用**
   頁面已有 **6 區實測淨收益表**（City Bowl／Sea Point／Rondebosch／Century City／Woodstock／Muizenberg，Africanvestor 2026-05）。報告的 5 區分法在頁面與來源中都找不到對應數據（尤其 Atlantic Seaboard、False Bay 缺淨收益數字）。若照做只能編造 → **保留原 6 區表，改為補上來源與日期註**（報告的核心要求「每區標來源與日期」已達成）。

3. **#11 建議的「3 個數據點」→ 做 4 個**
   報告列「人才留存率／STEM 畢業生數／外商投資額」。查證後三者皆有官方來源，另補「數理考生基礎」（DBE）作為第 4 點，因為這是解釋「為何 STEM 畢業生不足」的直接前因，比單獨列畢業生數更能支撐「人才供給是瓶頸」的結論。

---

## 閘門 1 結果

| 檔案 | 通過 | 剩餘 FAIL | 性質 |
|---|---|---|---|
| imo-en | 29/31 | footer links、Sources 0/3 | 既有 |
| international-buyers-en | 28/31 | footer links、HTML 配對、Sources 1/3 | 既有（實測 dist 同錯） |
| overseas-guide-en | 26/31 | Nav 9/9 缺、H2 問句 56%、footer、HTML 配對、Sources 2/3 | 全部既有 |

**逐一驗證「剩餘 FAIL 是否本次造成」**

1. **footer links**：`/overseas`、`/overseas-en` → 你已實測 301 正常，依指示**不動**。
2. **Nav（overseas-guide 9 項全缺）**：實測 `dist/` 原檔同樣 9 項全缺 → 該頁是舊版型（沒有標準導覽）。屬版面結構，依「不改 nav」未動；建議泰坦人另案（這頁是全批最舊的模板）。
3. **H2 問句 56%（overseas-guide）**：本次未新增或改寫任何 H2（只加段落與表格）→ `dist/` 原檔即 56%。
4. **HTML 配對**：overseas-guide `dist` err=4、`runs` err=4；international-buyers `dist` err=2、`runs` err=2 → **數量完全相同，皆為既有畸形**（`</article>`／`</div>` 錯位），依「不改版面」未動。
5. **Sources**：只補可指認者（GPG 2026、BetterBond、Lightstone via The Star 2026-07-03、Africanvestor 2026-05、DHET 2023/24、DBE、UNCTAD WIR 2025、Wise Move 2025），**未編造**。imo 頁本身無任何可指認外部數據（純賽事內容＋敘事推論）→ 仍 0，需水星人提供來源清單。
6. **desc 三處同步（imo）**：已修（156/194/91 → 全部 194）。

**其餘全 PASS**：JSON-LD 可解析、CSS 括號平衡、EN CJK=0、無簡體／中文註解、開普敦 ≥70%（intl 71%）、相關閱讀 ≥3、desc 150–320、canonical 無 `.html`。

---

## 預期效果（90 天）

| 頁 | 現況 | 增益 | 機制 |
|---|---|---|---|
| overseas-guide | 41i／pos 5.7 | +1.2 | 標題放金額（NT$16M）與比較對象；20 年複利表把敘事變成可引用算術；修掉 7.5-11.4% 口徑矛盾 |
| international-buyers | 35i／pos 5.1 | +1.1 | 標題把模糊的「Luxury」換成有據的「R10M+ Sales」；desc 帶 40%+/1/3/82% 三個數字；0→1 內連 |
| imo | 266i／3c／pos 7.4 | +1.0 | 依報告不投 CTR；改為「南非人才敘事落地頁」，4 個官方數據點可被 AI 摘要引用 |
| **合計** | — | **+3.3／90 天** | — |

> 三批累計：**10 篇，預期 +82.3 點擊／90 天**（第一批 +73.1、第二批 +5.9、第三批 +3.3）。
