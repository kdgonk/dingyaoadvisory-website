# 舊文復活第一批（3 篇）— 改動紀錄與閘門結果

**日期**：2026-10-19 ｜ **執行**：火星人 ｜ **依據**：`agent-notes/mercurian/2026-10-19-舊文復活清單.md` §三 1/2/3
**狀態**：未部署、未 push、`dist/` 零改動（`git status` 只有 `?? runs/`）

## 檔案清單（8 檔）

| # | 檔案 | 角色 |
|---|---|---|
| 1 | `sarb-bop-codes-foreign-property-buyers-2026-en.html` | 主改（合併 S-20261019-02） |
| 2 | `cape-town-quality-of-life-cost-comparison-en.html` | 主改 |
| 3 | `cape-town-airport-upgrade-investment-en.html` | 主改 |
| 4 | `sarb-bop-codes-foreign-property-buyers-2026.html` | ZH title/desc 對齊（內文不動） |
| 5 | `cape-town-quality-of-life-cost-comparison.html` | ZH title/desc 對齊 |
| 6 | `cape-town-airport-upgrade-investment.html` | ZH title/desc 對齊 |
| 7 | `cape-town-property-outlook-2026-en.html` | 內連來源（+1 條）＋ desc 三處同步 |
| 8 | `cape-town-infrastructure-investment-corridor-2026.html` | 內連來源（錨文字檢查：已符合，未改） |

---

## 1. BOP（+64.0／90 天，最大增益）

**現況**：4,232i / 63c / 1.49% / pos 6.0（90d）；主詞 `bop code` 88i **pos 14.3**

**改了什麼**
- title：`SARB BOP Codes 2026: What Foreign Property Buyers Must Know`（59）→ **`BOP Code List 2026: 800+ SARB Codes + Property 510 01`**（53）
- desc：→ 244 字元，列出 510 01 / 503 / 103 / 304 / 308 + 3 步檢查 + 5 步流程
- H1 + sr-only H2：→ `SARB BOP Codes 2026: Full List, Property Codes and Remittance Steps`
- **新增速查表**（3 欄：scenario / BOP code / SARB approval，8 列），置於「What BOP Code Do You Use for Goods, Salary and Other Non-Property Flows?」之前
- **新增 H2**「How Do Foreign Buyers Remit Funds Into South Africa Step by Step?」+ 5 步 process-steps，置於 wrong-code 章之後
- EN 頁殘留中文錨文字 4 條 + 中文註解 → 改英文（原第 32/36 項 FAIL）

**沒做的**：報告要求「新增 FAQ 3 問（salary / sale of goods / property）」——**10-16 版已存在這 3 題**（實測 FAQ h3：`What is the BOP code for sale of goods in South Africa?`、`...salary at Standard Bank?`、`Which forex BOP code should a foreign property buyer use?`），不重複添加。

**與 S-20261019-02 的合併處理**：採報告 title 主體（`BOP Code List` + `800+`，對應主詞 pos 14.3）＋ S-02 的 `510 01`（房產代碼，對應「查表」意圖）。S-02 原定的 5 步流程 H2 一併落地，不另開卡。

---

## 2. Quality of Life（+5.2／90 天）

**現況**：612i / 4c / 0.65% / pos 8.1；`cape town quality of life` 33i pos 7.2 **0 點擊**

**改了什麼**
- title：`Cape Town Quality of Life & Cost Compared | DingYao Advisory`（60）→ **`Cape Town Quality of Life 2026: 42nd, Cost 40% of Taipei`**（56）
- desc：→ 262 字元，帶 Mercer 42/230 + R18,000 vs TWD 75,000 + 40% index
- **🔴 主要修復：EN 版 20 段 markdown 殘留 → 10 個真 `<table>`**
  - 原況：EN 版 `<table>` = **0**、`<p>| Rank | City | ...` 純文字殘留 **20 段**（Mercer 排名、成本、租金、餐飲、學費、醫療、交通、娛樂、年度支出全毀）
  - ZH 版同頁有 **10 個真表格** → 這是嚴重的雙語不對稱缺陷，也是 pos 8.1 卻 0.65% CTR 的合理懷疑點（點進去看到管線文字）
  - 轉換結果：Rank 4×14、Dimension 3×10、Expense 6×8、Area 4×5、Dining 5×6、School 5×3、Medical 5×4、Transport 5×4、Leisure 5×6、City 4×7 → **殘留 0 段**
- 加 2 處來源註：Mercer 2026 排名、本文成本表口徑（1 ZAR = TWD 1.92, 2026-10）

**⚠️ 口徑不一致（需裁決）**：報告 title 建議「Cost 35% of Taipei」，但該頁表格是 **40%（monthly basket）**，35% 是另一段「annual spending」口徑。本次 EN title 採 **40%**（與表格一致），ZH 採 **35%**（與 ZH 內文一致）。兩語目前各自頁內自洽，但跨語不一致 → 建議下一輪統一為單一口徑。

---

## 3. Airport（+3.9／90 天）

**現況**：129i / 0c / pos 5.9；`acsa vision 2030 airport upgrades` 僅 1i pos 11

**改了什麼**
- title：`Cape Town Airport Upgrade: R10bn, 8-10% Yields`（46）→ **`Cape Town Airport R10bn Upgrade 2026: 3 Suburbs to Watch`**（56）
- desc：→ 292 字元，帶 R10.1bn / R6.39bn / R2.39bn / R863m / 2027-04 開工
- **新增 ACSA 分期表**（5 列）：realigned 3,500m Code F runway R6.39bn（2026-12 任命承包商）／國內到港 R2.39bn／國內離港 R0.50bn（2027-04 開工）／國際航廈 R863m／合計 R10.1bn（四項合計 10.143bn）
- **🔴 事實校正**：原文寫「main runway extend to 4,500 metres」「January 2026 公布」「2025 開工」→ ACSA 2026-02 官方口徑為**realigned 3,500m × 60m Code F**、**2026 年 2 月**公布、國內航廈 **2027-04** 開工。表格下方已加註「earlier commentary referring to a 4,500 m extension is superseded by the official programme」，未刪原文（遵守「只插入」限制）。
- 補 2 段（時序論述 + Cape Town 租金反應），Cape Town 佔比 63% → **75.7%**
- 補相關閱讀 3 條（原頁 **0 內連**）
- 內連：`cape-town-property-outlook-2026-en` 加 1 條（錨文字 `Cape Town airport R10bn upgrade`）；`cape-town-infrastructure-investment-corridor-2026` 已有該連結，錨文字已是「開普敦機場 R100 億升級：對周邊房產的實際影響」，符合要求 → 未改動

---

## 閘門 1（36 項）結果

| 檔案 | 通過 | 剩餘 FAIL |
|---|---|---|
| bop-en | 30/31 | footer links（既有） |
| bop-zh | 30/31 | footer links（既有） |
| qol-en | 29/31 | footer links、Sources 2/3 |
| qol-zh | 29/31 | footer links、Sources 0 |
| airport-en | 29/31 | footer links、Sources 1/3 |
| airport-zh | 29/31 | footer links、Sources 0 |
| outlook-en | 29/31 | footer links、Sources 0 |
| infrastructure-corridor-zh | 30/31 | footer links |

**兩類剩餘 FAIL 的性質（都不是本次改動造成的）**

1. **footer bottom links（8/8 檔）**：這些舊文用 `/overseas`（實站為 `/overseas-buyers`）、EN 用 `/overseas-en`（已知 404）。**老闆明令「不改 nav/footer」** → 未修，需泰坦人批次處理。
2. **Sources ≥3（5 檔）**：這些 2025-2026 舊文原本就沒有 inline 來源標註（body 實測 0–2 處）。我只補了**可指認的來源**（ACSA 官方、Mercer 2026、本文表格口徑），**沒有為了過閘門而編造來源**。QOL／airport 的房價、收益率數字原始來源不明，需水星人補來源清單才能達 3 處。

**其他全部 PASS**：JSON-LD 可解析、HTML 標籤配對、CSS 括號平衡、EN CJK=0、無簡體、無中文註解、H2 問句 ≥60%、開普敦焦點 ≥70%（airport 75.7%）、相關閱讀 ≥3、meta desc 150–320 且三處同步、canonical 無 `.html`。

---

## 預期效果（引用報告增益，90 天）

| 頁面 | 現況 | 預期增益 | 主要機制 |
|---|---|---|---|
| BOP | 4,232i / 63c / 1.49% / pos 6.0 | **+64.0** | 標題從「房產買家」放寬為「800+ 完整清單」，接住 pos 11–17 的 goods/salary 變體；速查表 + 5 步流程把意圖收進頁內 |
| QOL | 612i / 4c / 0.65% / pos 8.1 | **+5.2** | 標題帶 42nd + 40% 數字；**表格從純文字殘留變成 10 個真表格**（可讀性與 AI 提取） |
| Airport | 129i / 0c / pos 5.9 | **+3.9** | 標題補年份/地名/承諾；ACSA 分期表提供獨有內容；首次建立內連（原 0） |
| 合計 | — | **+73.1／90 天 ≈ +24.4／月** | — |

> 報告已註明：這 3 頁佔 44 頁可拿增益的 72%（+73.1 / +100.8）。
