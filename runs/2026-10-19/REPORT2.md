# 舊文復活第二批（4 篇）— 改動紀錄與閘門結果

**日期**：2026-10-19 ｜ **執行**：火星人 ｜ **依據**：水星人清單 §三 第 4/5/7/8 節
**狀態**：未部署、未 push、`dist/` 零改動（`git status` 只有 `?? runs/`）

## 檔案（4 篇，全 EN；ZH 對應頁本次指示未列，未動）

| # | 檔案 | 期望增益 | title | desc |
|---|---|---|---|---|
| 1 | `cape-town-property-outlook-2026-en.html` | +1.8 | 49 | 293 |
| 2 | `cape-town-semigration-2026-en.html` | +1.6 | 53 | 271 |
| 3 | `cape-town-rental-yield-9-49-percent-reality-check-2026-en.html` | +1.3 | 54 | 210 |
| 4 | `cape-town-property-investment-rates-net-return-2026-en.html` | +1.2 | 54 | 224 |

---

## 🔴 兩處「報告建議與頁面／來源不符」→ 未照抄（請裁決）

### (A) outlook：報告 title 建議「7.5% Yield, 40% Foreign Buyers」— 兩個數字都無依據
- 該頁**沒有任何 yield 或 median price 數字**；`7.5%` 在頁面出現 1 次，是**葡萄牙對非居民買家的 7.5% 轉讓稅**，與收益率無關。
- `40%` 在頁面是「Q4 2025 international buyer **inquiries** grew over 40% year on year」——詢問量成長，**不是外國買家占比**。（外國買家實際占比應為個位數，Lightstone 2026 全南非口徑。）
- **採用**：`Cape Town Property Outlook 2026: Inquiries Up 40%`（49）——唯一有頁面依據的數字。

### (B) net-return：報告 desc 建議「net 5.8%」— 頁面實測是 7.5%
- 該頁自己的收益率表寫 Sea Point 1 bed R2.6M / R21,000/mo → gross **~9.7%** / net **~7.5%**（差 −2.2pp），全文口徑一致（GPG methodology，gross-to-net gap 1.5–2.0pp）。
- `5.8%` 需扣 −3.9pp，與頁面自身方法論衝突。**採用 7.5%**，desc 開頭直接給結論：`Gross 9.7% becomes about 7.5% net after five cost layers…`（224 字元）。

---

## 逐篇改動

### 1. outlook-en（+1.8，119i／0c／pos 7.1）
- title：`Cape Town Property Outlook 2026: Global Buyer Guide`（51）→ **`Cape Town Property Outlook 2026: Inquiries Up 40%`**（49）
- desc：→ 293 字元（加拿大／澳／紐關門 vs 南非開放 + 40% 詢問成長 + 政策比較／匯率／居留）
- **刪無主詞引號句**（報告指令）：原句「the country's most international city. It is known as the "San Francisco of Africa" or "one of the most beautiful cities in the world,"」→ 改為可驗證句「South Africa's legislative capital and its most-visited city，國際買家詢問 Q4 2025 同比 +40%」
- 內連：+2（`overseas-property-investment-guide-cape-town-2026-en`、`taiwan-wealthy-overseas-allocation-en`），相關閱讀 6 → 8
- **保留**第一批改動（airport 內連、desc 三處同步）

### 2. semigration-en（+1.6，106i／0c／pos 7.1）
- title：`…35% Move to Western Cape`（52）→ **`Cape Town Semigration 2026: 32.4% Choose Western Cape`**（53）
- 🔴 **事實校正：35% 無來源，實際 32.4%**
  - 頁面 3 處 35% 全數校正：`32.4% of interprovincial moves head to the Western Cape (Wise Move 2025)`
  - 來源：Wise Move 2025 Migration Report（17,265 筆實際搬遷）→ 32.4% 目的地占比、15.1% 外流占比（全國保留率最高）、Gauteng→WC 走廊佔 48%
  - 表格註解保留一句「an earlier version cited 35%; the Wise Move 2025 dataset puts the destination share at 32.4%」→ 對讀者與未來校對透明
- **補省際遷移表（8 列，全部有來源）**，置於 H2「What Are the Key Metrics of Cape Town's 2026 Market?」之後：
  - StatsSA 2025 MYPE：WC in-migrants 500,347／net +319,000；Gauteng in-migrants 1,416,204／net +786,000
  - Wise Move 2025：WC 目的地 32.4%／外流 15.1%／Gauteng→WC 走廊 48%
  - Wise Move 2024：Cape Town 7,673 筆移入中 1,601 來自 Gauteng（約 1/5）
  - StatsSA HPI via FNB：WC 2010-01→2025-09 +179.6%（Gauteng +79.7%）
- 內連：**0 → 3**（rental-yield、outlook、net-return）

### 3. rental-yield-en（+1.3，44i／0c／**pos 5.1**）
- title：`…9.49% Not 11.53%`（46）→ **`Cape Town Rental Yields 2026: 9.49% vs the 11.53% Myth`**（54）
- **插入 R2.6M 五層成本試算表**（H2「How far do gross and net yields diverge…」之前）：

| 成本層 | 年金額 (R) | 佔毛租金 | 影響 |
|---|---|---|---|
| Vacancy 1 個月 | 19,739 | 8.0% | −0.76 pp |
| 市政稅 | 9,870 | 4.0% | −0.38 pp |
| 管理費 levies | 7,402 | 3.0% | −0.28 pp |
| 維修 | 6,169 | 2.5% | −0.24 pp |
| 呆帳 | 3,701 | 1.5% | −0.14 pp |
| **合計** | **46,881** | **19.0%** | **−1.80 pp** |
| **淨收益率** | **199,859** | — | **7.69%** |

  → 9.49% × R2.6M = R246,740；淨 7.69% **落在頁面既有 7.5–8.0% 區間**（不製造新矛盾）；表下註明「各層 % 為作者估計、GPG 口徑 gap 1.5–2.0pp、跨境另扣 0.5–1.0pp 匯損」
- 內連：+1（sectional-title 指南），現 9

### 4. net-return-en（+1.2，40i／0c／**pos 4.5** 全批最好）
- title：`Cape Town Property Investment Rates 2026 | DingYao Advisory`（59）→ **`Cape Town Net Rental Return 2026: 9.7% Gross, 7.5% Net`**（54）
- desc：203 → **224 字元**，開頭直接給結論（原本開頭是問句、Google 截斷後看不到承諾）
- **插入五層成本金額表**（H2「Which five cost layers…」之後）：vacancy R20,176／levies R7,566／rates R10,088／insurance+repairs R10,088／remittance+FX R3,783 → 合計 R51,701（20.5%）→ **9.7% − 2.00pp = 7.71%**，與頁面 7.5% 市場參考值一致（誤差 <0.2pp，已註明）
- 內連：+1（sectional-title），現 8

---

## 閘門 1 結果

| 檔案 | 通過 | 剩餘 FAIL |
|---|---|---|
| net-return-en | 30/31 | footer links（既有） |
| semigration-en | 29/31 | footer links、Sources 1/3 |
| outlook-en | 29/31 | footer links、Sources 0/3 |
| rental-yield-en | 28/31 | footer links、Sources 1/3、**HTML 配對（既有畸形）** |

**三類剩餘 FAIL 的性質（皆非本次造成）**

1. **footer links**：`/overseas`、`/overseas-en`。你已實測 301 正常 → 依指示**不動**。（我的閘門腳本仍按 `/overseas-buyers` 字面判定，故顯示 FAIL；這是儀器與政策的落差，不是頁面缺陷。）
2. **Sources ≥3**：4 篇舊文 body 原本 0–1 處 inline 來源。本次只補可指認者（StatsSA 2025 MYPE、Wise Move 2025、GPG methodology、FNB/StatsSA HPI），**未編造**。outlook 頁無任何可指認外部數據，故仍 0 → 需水星人給來源清單才能補。
3. **HTML 配對（rental-yield）**：`</article>` 提早於 CTA 前閉合、尾部多 2 個 `</div>` —— **實測 `dist/` 原檔同樣 2 個錯誤**（`dist` err=2，`runs` err=2），是既有畸形。屬版面結構，依「不改版面」未動，建議泰坦人另一輪修。

**其餘全 PASS**：JSON-LD 可解析、CSS 括號平衡、EN CJK=0、無簡體／中文註解、H2 問句 ≥60%、開普敦佔比 ≥70%、相關閱讀 ≥3、desc 150–320 且三處同步、canonical 無 `.html`。

---

## 預期效果（90 天）

| 頁 | 現況 | 增益 | 機制 |
|---|---|---|---|
| outlook | 119i / pos 7.1 | +1.8 | 標題從抽象指南改為可驗證的 40% 詢問成長；移除無主詞引號句；+2 內連 |
| semigration | 106i / pos 7.1 | +1.6 | 標題數字有據（32.4%）＋8 列獨有遷移數據表＋0→3 內連 |
| rental-yield | 44i / pos 5.1 | +1.3 | pos 5 卻 0 點擊 → 標題放「打假」承諾；R2.6M 淨收益試算表（全批最接近前三） |
| net-return | 40i / pos 4.5 | +1.2 | pos 4.5 但描述開頭無結論 → 改為 gross 9.7% → net 7.5%；金額化 5 層表 |
| **合計** | — | **+5.9／90 天** | — |
