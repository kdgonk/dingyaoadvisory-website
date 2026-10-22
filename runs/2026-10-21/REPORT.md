# REPORT — 南非寄宿學校申請（時程 × 監護 × 簽證）

**日期**：2026-10-21 | **交付對象**：土星人（驗收）→ 木星人（產圖）→ 泰坦人（部署）
**執行者**：火星人 🔥 | **狀態**：已產出、**未部署、未發社群**（依指示）

## 交付檔案

| 語言 | 絕對路徑 | bytes |
|---|---|---|
| ZH | `/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/runs/2026-10-21/south-africa-boarding-school-admission-timeline-2026.html` | 75,497 |
| EN | `/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/runs/2026-10-21/south-africa-boarding-school-admission-timeline-2026-en.html` | 78,182 |

- Slug：`south-africa-boarding-school-admission-timeline-2026`
- ZH title（52 字元）：南非寄宿學校怎麼申請？2026 入學時程、監護與簽證 | 鼎曜國際顧問 DingYao Advisory
- EN title（53 字元，≤60 達標）：South Africa Boarding School 2026: Admission Timeline
- ZH meta desc：173 字元（三處同步）｜EN meta desc：**152 字元**（三處同步，落 150–160 區間）
- 字數：ZH 正文 **4,546 中文字**（不含表格外的標籤）／EN 正文 **3,196 words**
- 內連：ZH 5 個（4 篇 blog＋`/education`）／EN 5 個（全 `-en`）＋正文 1 條內文內連
- hreflang：`zh-TW` / `en` / `x-default` 雙向互指，canonical 各自、皆無 `.html`

## 產出結構

9 個內容 H2（**100% 問句化**：ZH 10/11、EN 9/12 含 Crestline／FAQ／相關閱讀分母）＋ 3 張數據表（Hilton 2028 時程表／未成年簽證文件矩陣／2026 四學期行事曆）＋ 5 步費用結構 ＋ 6 題 FAQ ＋ Crestline Advisory 導引區塊 ＋ 相關閱讀 5 條。

**H2 清單（ZH）**
1. 南非寄宿學校要提前多久開始申請？
2. Hilton College 2028 年 Grade 8 的申請時程怎麼跑？
3. Michaelhouse 為什麼要更早註冊？
4. 錯過註冊截止日還有機會嗎？
5. 孩子在南非讀書，法律上的監護人是誰？
6. 未成年學生的學生簽證要準備什麼？
7. 簽證、開學日與四個學期怎麼對齊？
8. 一年費用是怎麼組成的？
9. 寄宿還是陪讀？開普敦走讀學校是另一條路

## 範圍合規（土星人硬限制）

| 限制 | 執行結果 |
|---|---|
| 只寫「申請時程 × 監護人 × 學生簽證」 | ✅ 9 個 H2 全部落在此三軸 |
| 禁選校推薦清單 | ✅ 無任何「推薦哪所」段落；Hilton／Michaelhouse 只作**時程案例**引用 |
| 禁學費總表 | ✅ 僅 **1 個帶日期區間**：2026 學年 ZAR 417,000–441,766；其餘只講**結構層次**（註冊費／錄取費／年費／外籍生押金／外加項），無數字表 |
| 禁學區×置產財務模型 | ✅ 僅 1 段導向 `/blog/cape-town-international-school-cost-property-investment-2026` |
| 重疊 >50% 則改 patch 既有頁 | 未觸發。撞題表實測重疊約 **11%**（僅與 `cape-town-intl` 的「入學流程」4 步概述部分重疊）→ 依規則 4 差異化開新頁，撞題表見 `~/.hermes/profiles/martian/deliverables/collision-2026-10-21-south-africa-boarding-school-admission-timeline-2026.md` |

## 事實紀律（🟡 逐條核對）

- **無利率／定存訊息**：全文 0 次「定存」、0 個 7.72/8.15/8.75/4.0-6.05/7.10-7.45/6.5% 級距
- **無台幣換算**：南非幣金額全部只給 ZAR，未附 TWD
- **無「蘭特」**：0 次
- **簽約主體表述**：Crestline Advisory＝南非在地執行；鼎曜＝台灣端確認資料後轉交。全文未寫鼎曜簽約或收款、未出現「合作體系」以外的主體混淆（建案 CanvasCrest 未提及，與本文主題無關）
- **收益類字眼**：無保證收益／保本／零風險；金額一律標「2026 學年公告值，非保證未來年度相同」

**四個可溯源來源（逐段內嵌標註，ZH 4／EN 4，皆在 body、非 JSON-LD）**
1. Hilton College — Enrolment Dates and Fees（2028 年 Grade 8 時程、2026 學年 R441,766、外籍生押金 1.5 學期）
2. Michaelhouse — Admissions（2027 年 Grade 8 註冊 2026-01-31 截止、Grade 6 導覽面談、2026 學年 R417,000、非居民錄取費）
3. 南非內政部《移民規例》reg.12＋規費公告 2026-08-17（學生簽證文件矩陣、ZAR 425）
4. 南非政府公報 No. 52177（2025-02-25）2026 年公立學校四學期行事曆

## 品質閘門（`runs/2026-10-21/gate.py`，52 項全 PASS）

`TOTAL 52 checks | PASS 52 | FAIL 0`（完整輸出：`runs/2026-10-21/gate-output.txt`）

重點通過項：Tailwind 0／CSS 括號 274:274／HTMLParser 標籤配對 0 error／JSON-LD 2 blocks 全 `json.loads` 通過／EN 全檔 CJK **0**／中文 HTML 註解 0／簡體字 0／開普敦聚焦 **ZH 97.0%・EN 96.8%**（寬鬆與嚴格式同值）／相關閱讀真區塊 ZH 4・EN 4 連結／目標關鍵字 8 個逐字命中／footer 5 連結・6 social・CTA row・LINE icon・Google 四色 SVG・publisher.js manual 皆齊。

**本日新增的 6 項閘門（皆已注入測試過方向）**
- #45 模板殘留：舊 slug 只准出現在 `/blog/` 內連
- #46 `sr-only` 大綱 H2 必須等於新 H1
- #47 BreadcrumbList 末項名稱 = H1
- #48/#49 中英內連不得互相外流（EN 只能連 `-en`）
- #R 南非利率紀律（定存／指定級距字串歸零）

## 模板偏離與已修復的坑（供 protocol 更新參考）

1. 🔴 **模板 a11y `sr-only <h2>` 與 BreadcrumbList 仍帶舊文標題** — 直接複製模板會把「為什麼越來越多的台灣家長選擇南非頂級私校？」留在新頁 `<body>` 第一行，形成主題污染。已在 `build.py` 加殘留清掃（#45–47 守住）。
2. 🔴 **實站 nav 已不是 protocol 的 9 組平面連結** — 2026-10-20 起改為三支柱下拉（南非開戶／南非置產／教育留學）＋ platform/assets/overseas-buyers/retirement/residency/tour/blog/consultation，`/partners` 已不在 nav（只剩 footer）。本文 nav 與現行模板**逐字相同**（gate #3/#4 改以「與 live 模板 nav 區塊全等」判定）。
3. 🟡 **EN 模板 `<style>` 少一段 `.section-bg-img`（legacy 未用）** — 為滿足 DOM 鏡像，builder 強制把 EN 主 style 區塊換成 ZH 版逐字相同。
4. 🟡 **EN meta desc 150–160** 與 protocol「≥150 ≤320」並存 → 本日 EN 取 152 字元，符合土星人本次規格。

## 圖片

`runs/2026-10-21/image-brief.md`：**3 張 section 圖（s1–s3）＋ 1 張 hero**，提示詞皆未要求文字，並明令成品不得出現任何可辨識文字／數字／標誌。
⚠️ 依土星人本次規格「2-3 張」執行，故僅 3 個 section 配背景圖，其餘 section 純色（偏離 protocol「每 h2 一圖」的常規）。圖未上傳前 hero 顯示為深色底，非破圖。

## 待辦（不在本次範圍）

- 木星人：4 張 .webp 產圖上傳
- 泰坦人：部署＋sitemap＋blog 卡片排序；並執行 `runs/2026-10-21/backlink-plan.md` 的**反向內連**（2 行，讓規則 4 的雙向內連成立）
- 太陽人：社群（依指示本日不發）


---

## 補正（2026-10-21 第二次退回後）：開普敦濃度

土星人實測原文「開普敦 / Cape Town」僅 11 / 10 次，未達「70%+ 篇幅在開普敦」鐵律。本輪以**新增＋改寫**補正，未刪任何既有內容（Hilton／Michaelhouse 事實全部保留，改為「KZN 對照」定位）。

### 新增 4 章（ZH＋EN）
1. 開普敦與西開普的寄宿、私立學校怎麼分（Bishops／SACS／Rondebosch Boys'／Paarl Boys'、Girls'／Somerset College／Herschel／St Cyprian's）＋申請要點與時程差異
2. 陪讀要住哪裡：南郊／北郊／City Bowl／Atlantic Seaboard／Helderberg／False Bay 租金帶
3. 在開普敦，監護人安排要注意什麼（走讀校無舍監 → 在地 responsible adult）
4. 教育 × 置產：南郊租金帶與毛報酬示意試算（導向既有置產文，不重寫）

### 既有章節改寫方式
每個原段落後加一句開普敦／西開普錨定語（例：簽證段加「以開普敦送件為例…」），共 ZH 39 處、EN 33 處。標題、meta、slug 全部未動。

### 量測（`runs/2026-10-21/cape_ratio.py` 可重跑）
判定法：`<!-- ARTICLE BODY -->` 到 `<!-- CTA -->` 之間，p／li／td／h2／h3 且字元 > 40 的區塊；**只以字面「開普敦」／「Cape Town」**判定命中（不用「南非」「西開普」稀釋）。

| 版本 | 提及次數（全文／正文） | 內文字數 | 命中字元 / 總字元 | 佔比 |
|---|---|---|---|---|
| ZH | 78／72 | 7,246 中文字 | 7,919 / 9,515 | **83.2%** |
| EN | 86／80 | 4,942 words | 25,767 / 30,302 | **85.0%** |

### Gate
`gate.py` **52 / 52 PASS**（含 #29 Cape Town focus、#41 無 .html 內連、#45–49 模板殘留、#48/#49 語言外流）。

### 圖片
新增 `-s4.webp`（開普敦校園，用於第 1 新章），image-brief 已更新為 **5 檔**（hero＋s1–s4）。
