# 三支柱服務頁 ＋ 四層漏斗 ＋ 白皮書 ＋ LINE 導流｜技術方案

**日期**：2026-10-20 | **交付對象**：土星人（裁決）、火星人（文案／標記）、木星人（產圖）、老闆（兩項決策）
**實作**：泰坦人 🛸

---

## 摘要：這次是真的做完了什麼

不是紙上規劃。以下都是**已經寫好並用真工具驗證過**的成品，放在
`~/Documents/DingYao-Website/dingyaoadvisory-website/runs/2026-10-20-funnel/`：

| 檔案 | 內容 | 驗證結果 |
|---|---|---|
| `dy-funnel.js` | 四層漏斗 dataLayer 實作（11KB） | Chromium 實測 **27/27** |
| `worker-v2.js` | 新增 `/api/whitepaper`（3 欄表單無 email 也能進 CRM） | 單元測試 **25/25** |
| `gen-whitepapers.py` → `build/whitepapers.html` | 白皮書下載頁（nav/footer 與全站 byte-identical） | 端到端 **34/34** |
| `verify-preflight.py` | 上線前驗收（200／404 有 body／不外洩） | 對 live 實測 **35/35**，負向測試通過 |
| `GTM-SETUP.md` | GTM／GA4 逐步設定手冊 | 容器現況已從 gtm.js 取證 |

**未部署、未 commit、未動任何既有頁。** 全部在 `runs/`（git untracked）。

---

## 一、三支柱服務頁

### 1.1 現況實測

| URL | 現況 | 備註 |
|---|---|---|
| `/south-africa-bank-account` | **HTTP 404**（有 body，441KB） | 確認需新建 |
| `/south-africa-property` | **HTTP 404**（有 body，441KB） | 確認需新建 |
| `/education` | **HTTP 200**（96,813 bytes） | 存在，需改造 title/H1 |

### 1.2 樣板：沿用 `dist/residency.html`

不是憑感覺選的。用 md5 比對全站 46 個根層頁面的 nav / footer：

- **nav 主流版型 `9eb32b9e`：17 頁共用**（education / residency / retirement / platform / partners / assets / blog / consultation / contact / about / index…）
- **footer 主流版型 `254c835e`：12 頁共用**
- `residency.html` = `9eb32b9e` + `254c835e` = **與 `/education` 完全相同**

選它而不是 education 的三個理由：

1. **唯一具備完整 4 個 JSON-LD 的服務頁**：`FinancialService`（含 address／contactPoint／sameAs）、`WebSite`、`BreadcrumbList`、`FAQPage`。education.html 只有一個 `WebPage`。新服務頁直接繼承 → 麵包屑與 FAQ 結構化資料不用重做。
2. **結構就是服務頁六段式**：`hero` → `why` → `process`（timeline）→ `compare` → `faq` → `cta`。education 是 9 段內容頁，區塊要刪。
3. **檔案較輕**：66KB vs education 84KB，hero 圖路徑單一。

### 1.3 建置步驟（每頁）

```bash
# 0. 先確認來源頁沒被別人改過（nav/footer 基準）
python3 runs/2026-10-20-funnel/verify-preflight.py https://dingyaoadvisory.tw /residency

# 1. 複製樣板
cp dist/residency.html dist/south-africa-bank-account.html

# 2. 改 head（見 1.4 清單）——這步最容易漏，漏了會跟既有頁搶關鍵字
# 3. 換 6 個 section 內文（火星人提供文案後套版，不改 CSS）
# 4. 每個 CTA 加 data-cta-id / data-cta-location（見 1.6）
# 5. body 加 data-pillar
# 6. <head> 尾端加 <script src="/js/dy-funnel.js" defer></script>
# 7. 本機 preflight → 部署 → purge → live preflight → sitemap → GSC
```

**部署後固定四步**（少一步就會出現「我這邊看得到、別人看不到」）：
```bash
git add dist/south-africa-bank-account.html dist/sitemap.xml
git commit -m "feat(service): /south-africa-bank-account 服務頁"
git push                      # GitHub Actions 自動 wrangler deploy ~30s
# purge Cloudflare zone 3f0348f9…
python3 runs/2026-10-20-funnel/verify-preflight.py https://dingyaoadvisory.tw /south-africa-bank-account
```

### 1.4 head 必須改的 8 項（漏一項就是 SEO 事故）

| 項目 | 從 | 改成 |
|---|---|---|
| `<title>` | 全球身分規劃 \| 鼎曜國際顧問 DingYao Advisory | 見 1.5 |
| `description` | 身分規劃文案 | 該支柱 150–320 字 |
| `canonical` | /residency | 新 URL |
| `og:url` | /residency | 新 URL |
| `og:title` / `og:description` | 同上 | 同步 |
| `og:image` / `twitter:image` | residency hero | 新 hero（木星人產） |
| 3 條 `hreflang`（zh-Hant／en／x-default） | /residency | 新 URL（EN 未上線前 en 版先指向 ZH 或先不加） |
| JSON-LD 內 4 處 `url` / `@id` / breadcrumb `item` | /residency | 新 URL |

> JSON-LD 的 `BreadcrumbList` 一定要改，否則 Google 會把新頁顯示成「首頁 › 全球身分規劃 › 南非銀行開戶」。

### 1.5 關鍵字策略：兩頁處境完全不同（這是本案最需要決策的地方）

我掃了 sitemap 330 個 URL 與全部 blog：

**`/south-africa-bank-account` —— 空白區，可以直接打**
- 全站只有 2 篇 blog 提到「銀行開戶」，且都不是主題（`foreign-capital-sell-tsmc…` 順帶一提、`standard-bank-money-market` 講高利活存）
- **建議 title**：`南非銀行開戶完整指南｜外國人開戶流程與文件｜鼎曜國際顧問`
- H1：`南非銀行開戶`

**`/south-africa-property` —— 紅色警戒區，必須差異化**
- 首頁 title 已是「**南非置產**｜台灣唯一在地直營｜開普敦房產投資顧問」
- **101 個 blog 檔**內文含「南非置產」
- 已有一篇專門文：`blog/cape-town-property-purchase-process-guide` → title 是「**開普敦買房流程**完整指南：外國人從簽約到過戶的七大步驟」
- 若新服務頁 title 再寫「南非置產流程」→ **直接跟首頁 + 101 篇 + 那篇流程文三方對撞**

**建議做法**：服務頁打「服務意圖」，不打「資訊意圖」。
- 首頁、blog 打的是「南非置產是什麼、流程怎麼走」（資訊意圖）
- 服務頁打「誰幫我辦」（服務意圖）
- **建議 title**：`南非置產顧問服務｜在地團隊陪同簽約與過戶｜鼎曜國際顧問`
- H1：`南非置產顧問服務`
- 內文重心放在「我們做什麼」（陪同看屋、律師對接、匯款、稅務申報、交屋後物業管理），
  流程細節**用內連指向** `blog/cape-town-property-purchase-process-guide`，
  這樣是把既有文的權重導過來，而不是互搶。

### 1.6 CTA 標記規範（給火星人寫頁面時照抄）

四層漏斗的 L2 完全依賴這個標記。沒標也能追，但 `cta_id` 會變成 `auto__consultation`，
就分不出是 hero 還是頁尾帶來的。

```html
<!-- hero 主 CTA -->
<a href="/consultation" class="btn-hero"
   data-cta-id="hero_primary" data-cta-location="hero">預約免費評估</a>

<!-- 中段 CTA -->
<a href="/consultation" class="btn-mid"
   data-cta-id="mid_consult" data-cta-location="mid_section">了解我的情況</a>

<!-- 頁尾 CTA -->
<a href="/whitepapers" class="btn-bottom"
   data-cta-id="bottom_whitepaper" data-cta-location="bottom_cta">先下載白皮書</a>
```

`cta_location` 只用這 6 個值，不要自創（GA4 維度會碎掉）：
`hero` / `mid_section` / `bottom_cta` / `sticky_bar` / `nav` / `faq`

### 1.7 需要哪些資產

| 資產 | 規格 | 負責 | 必要性 |
|---|---|---|---|
| `sa-bank-account-hero.avif` | 1920×1080，暗調，≤200KB | 木星人 | 必須（og:image 也用） |
| `sa-property-hero.avif` | 同上 | 木星人 | 必須 |
| 每頁 3–4 張區塊插圖 | webp，≤120KB | 木星人 | 可選，但 `why` 區塊沒圖會很空 |
| 內文文案（6 個 section） | 中文 1200–1800 字／頁 | 火星人 | 必須 |
| FAQ 6–8 題 | 每題 60–120 字 | 火星人 | 必須（JSON-LD FAQPage 要用） |

**hero 圖有硬性檢查**：上線後 `curl -I` 必須 200 且 `content-type: image/avif`。
歷史上踩過 `.jpg` 寫成 `.webp` 的坑，preflight 腳本只驗頁面不驗圖，所以要另外 curl。

### 1.8 預計工作量

| 項目 | 工時 | 前提 |
|---|---|---|
| 樣板複製 + head/JSON-LD 8 項改寫 | 1.0 h／頁 | — |
| 內文套版（6 section） | 2.5 h／頁 | 火星人文案到位 |
| CTA 標記 + dy-funnel 掛載 | 0.3 h／頁 | — |
| 部署 + purge + sitemap + GSC + preflight | 1.0 h／頁 | — |
| **兩頁小計** | **≈ 9.6 h（1.2 人天）** | 不含文案撰寫與產圖 |
| `/education` 改造 | 2.0 h | 見第二節 |

---

## 二、`/education` 改造（不新建）

### 2.1 現況（實測）

- title：`教育留學 — DYA Ding Yao Advisory APAC Hub`（37 字）
- H1：`菁英教育<br><span class="gold">入場券</span>`
- description：154 字（長度合格）
- JSON-LD：只有 `WebPage`

### 2.2 問題

1. **title 用的是舊格式**（`— DYA … APAC Hub`）。全站主流已是 `| 鼎曜國際顧問 DingYao Advisory`（residency / assets / overseas-buyers 都是）。同一站兩種品牌格式會讓 SERP 看起來像兩個網站。
2. **H1 完全沒有關鍵字**。「菁英教育入場券」不含「南非」「留學」「私校」—— 這是三個支柱裡 SEO 最弱的一頁。
3. 只有 `WebPage` schema，缺 `BreadcrumbList` 與 `FAQPage`（頁面明明有 FAQ）。

### 2.3 建議改法（保留視覺設計，只換字）

```diff
- <title>教育留學 — DYA Ding Yao Advisory APAC Hub</title>
+ <title>南非留學與頂級私校規劃 | 鼎曜國際顧問</title>

- <h1 class="hero-title ...">菁英教育<br><span class="gold">入場券</span></h1>
+ <h1 class="hero-title ...">南非留學<br><span class="gold">頂級私校入場券</span></h1>
```

- H1 兩個字都保留原本的 `<br>` + `<span class="gold">` 結構 → **CSS 完全不用動**
- 補 `BreadcrumbList` + `FAQPage` schema（可直接從 residency 抄結構改內容）
- `description` 不動（154 字已合格，且含「南非」「留學」）
- **EN 版 `education-en.html` 同步改**，兩版 title 不一致會讓 hreflang 配對品質下降

**不要改 URL。** 改 URL 等於要重做 301 + 重等收錄，而且 `/education` 已累積排名。

---

## 三、四層漏斗 GTM event

### 3.1 容器現況：從 `gtm.js` 反解取得（不是猜的）

```
GET https://www.googletagmanager.com/gtm.js?id=GTM-PVWHRBWG   → 369,146 bytes
解析 var data.resource：
  tags: 4   ├ __googtag  → GA4 設定標籤 G-4H4T55YXB0
            ├ __cvt_MQDKZ → Microsoft Clarity yefp1ui9nf
            ├ __html     → Ahrefs analytics
            └ __html     → Chatwoot SDK
  predicates: 3  → 只有 gtm.init / gtm.js / gtm.load（GTM 內建）
  GA4 事件 tag (__gaawe): 0 個
  Custom Event trigger:   0 個
```

**⇒ 四層漏斗是完全從零建置：4 個 Custom Event trigger + 4 個 GA4 Event tag + 6 個 Data Layer Variable + 6 個 GA4 自訂維度。**

⚠️ **我沒有 GTM API 憑證**（本機 `gcloud auth list` → `No credentialed accounts`），
所以 **tag 必須在 GTM 後台手動建**，我無法用程式寫進去。
但 dataLayer 那一半（真正容易出錯的部分）我已經寫完並實測。

完整逐步設定在 **`GTM-SETUP.md`**（含每個 tag 的參數表、每步的畫面位置）。
重點三個：

1. **Data Layer Variable 一定要選 Version 2**（V1 會留殘值）
2. **GA4 後台必須註冊 6 個自訂維度**，否則事件進來了但探索報表拉不到 `pillar` — 這步最多人漏，而且要等 24h 生效、不回溯
3. **L4 要勾「標記為重要事件」**，才能直接看轉換數

### 3.2 dataLayer 實測輸出（真 Chromium）

L1：
```js
{ event:'view_service_page', event_category:'funnel_l1', pillar:'property',
  service_pillar:'property', page_path:'/south-africa-property', page_lang:'zh',
  dy_session_id:'s_mvg9ki2w_upgpxk', dy_funnel_version:'1.0.0',
  utm_source:'line', utm_campaign:'2026q4_property', liff_id:'1657000000-abcdefg' }
```

L2：
```js
{ event:'cta_click', event_category:'funnel_l2', cta_id:'hero_primary',
  cta_location:'hero', cta_text:'預約免費評估', pillar:'property',
  utm_source:'line', dy_session_id:'s_...' }
```

L3：
```js
{ event:'lead_submit', event_category:'funnel_l3', lead_type:'whitepaper',
  asset_name:'whitepaper_property_2026', form_id:'wpForm', pillar:'property',
  first_submit_in_session:1, pillar:'property', utm_source:'line' }
```

L4（由 L3 繼承 pillar 與來源）：
```js
{ event:'booking_confirmed', event_category:'funnel_l4', pillar:'property',
  booking_ref:'BK-2026-0042', booking_source:'confirmation_page',
  booking_slot:'2026-10-28T14:00', origin_asset:'whitepaper_property_2026' }
```

### 3.3 三個設計決定（都有理由）

| 決定 | 理由 |
|---|---|
| L1 同 session 同 pillar **只送一次** | 使用者按上一頁再進來不該被算成兩次 L1，否則 L1→L2 轉換率會被低估一半 |
| L2 用 **capture phase + 同步 push**，不延遲導航 | 追蹤碼絕不可以讓使用者等。實測點 CTA 後事件在導航前已進 dataLayer |
| L4 **必須有 `booking=1` 才送** | 直接開 `/booking-confirmed` 不帶參數不會送（已寫測試）—— 否則分享連結或爬蟲就會製造假預約 |

### 3.4 怎麼看「每支柱 L1→L4 轉換率」

GA4 → 探索 → **漏斗探索**，4 步（view_service_page → cta_click → lead_submit → booking_confirmed），
細分維度選 `pillar`，漏斗類型選「封閉漏斗」。

### 3.5 必須先跟老闆講的一件事：數字會偏低

站上 `gtag('consent','default', {analytics_storage:'denied'})`。
未按「同意」的使用者，事件不進標準報表。所以：

- **轉換率（比率）可信** —— 分子分母都少同一批人，比值還算穩
- **絕對數字會偏低** —— L1 可能少 30–50%
- **L4 最嚴重** —— 營收級事件不能只靠前端

**第二階段建議**：預約成立由 n8n／Chatwoot webhook 打 **GA4 Measurement Protocol**，
伺服器端送出不受 consent 影響。這件事不做，L4 永遠只是「有同意者的抽樣」。

---

## 四、白皮書下載頁

### 4.1 已完成：`build/whitepapers.html`（21KB，可部署）

- nav / footer **與全站 byte-identical**（`9eb32b9e` / `254c835e`，md5 驗證 MATCH）
- 4 張白皮書卡（開戶／置產／教育／稅務）
- **3 欄表單**：稱呼、WhatsApp 或手機、想了解哪一塊
- 前端驗證：空值／電話格式／未勾同意都在前端擋掉、**不呼叫 API**（實測過）
- 送出成功才顯示下載按鈕
- 375px 無水平溢出（實測 overflow=0px）

### 4.2 關鍵阻礙：`/api/lead` 強制要 email

實測（對 production）：
```
POST /api/lead  {"name":"test","custom_attributes":{"source":"lead_magnet"}}
→ HTTP 400 {"ok":false,"error":"Valid email required"}
```

而老闆定案的 3 欄表單**沒有 email**。三個選項：

| 方案 | 做法 | 評價 |
|---|---|---|
| A. 加第 4 欄 email | 改需求為 4 欄 | 違反老闆定案，且多一欄會掉轉換 |
| B. 放寬 `/api/lead` 的 email 驗證 | 改既有端點 | **不可**，會動到既有 8 頁的既有行為 |
| **C. 新增 `/api/whitepaper`** ✅ | 獨立端點，email 選填 | 已實作並測完（25/25） |

**選 C。** 沒有 email 時用 `wa+886912345678@lead.dingyaoadvisory.tw` 當識別值：
- `lead.dingyaoadvisory.tw` 是保留的假域名，**永遠不會誤發信**
- 同一支手機在 Chatwoot 會是同一筆聯絡人（可去重）
- 一眼看出是 WhatsApp lead

### 4.3 名單落到哪裡：Chatwoot（不建議 Brevo / Google Sheet）

| 選項 | 現況 | 判斷 |
|---|---|---|
| **Chatwoot** ✅ | **已在用、token 已配、Worker proxy 已通**（`/api/health` → `chatwoot_token_configured: true`） | 零新增成本；業務能直接在同一個後台回覆 WhatsApp |
| Brevo | **本機無任何 Brevo 憑證**（grep `.env` / `config.yaml` 皆無） | 要新開帳號、重新談方案、做 double opt-in，多一週 |
| Google Sheet | 需 service account + 無法自動化跟進 | 只適合當備份 |

**建議：Chatwoot 為主要落點。** 若之後要做 email 行銷（白皮書第 2、3 章自動寄），
再由 n8n 從 Chatwoot 同步到 Brevo —— 這樣不用改網站。

名單自動帶入的欄位：`source=whitepaper_download`、`pillar`、`asset_name`、
`lead_channel=whitepaper_form`、`utm_source`／`utm_campaign`／`liff_id`／`landing_page`。

### 4.4 PDF 放哪裡：R2（已驗證可寫可讀）

- bucket：`dingyao-assets`，對外 `https://assets.dingyaoadvisory.tw/`
- 實測：上傳 `whitepapers/r2probe.txt` → `HTTP 200`，測試後已刪除
- ⚠️ **rclone 必須加 `--s3-no-check-bucket`**，否則會嘗試 CreateBucket 被 403 打回：
  ```
  rclone copy wp-property.pdf dingyao-r2:dingyao-assets/whitepapers/ --s3-no-check-bucket
  ```

### 4.5 防直接抓檔（做不到 100%，但做到三層）

1. **PDF 路徑不寫進 HTML／JS。** 只有 `/api/whitepaper` 驗證通過才回 `download_url`。
   實測：`".pdf" not in HTML` → PASS。
2. **檔名帶 8 位隨機後綴**（`wp-property-2026-b84e1d06.pdf`），無法靠猜測掃描。
3. **`noindex, follow`** —— 下載頁不進 Google 索引，避免 PDF 被爬蟲直接找到。
   （這頁是轉換頁，不是內容頁，本來就不該進 sitemap。）

**誠實說明**：檔案一旦給瀏覽器，使用者就能另存或轉傳，任何前端手法都擋不住。
真要擋只能「不給檔案、改用 LINE 或 email 發送」——那就是第二階段要做的事。
第一階段用上述三層，擋掉「看原始碼就抓到連結」這種 90% 的隨手行為。

### 4.6 第二階段：接 LINE 官方帳號（待老闆建帳號）

改動很小，因為第一階段已預埋：
- 移除表單的「立即下載」，改成「加 LINE 取得檔案」按鈕
- 加 LIFF SDK，登入後把 `line_user_id` 一起送 `/api/whitepaper`
- 後端用 Messaging API 推 PDF 連結給該 `line_user_id`

---

## 五、LINE 導流追蹤預埋（已實作，帳號上線後不用回頭改頁面）

### 5.1 已預留的 URL 參數（`dy-funnel.js` 第一秒就抓並存 sessionStorage）

| 參數 | 用途 | 範例 |
|---|---|---|
| `utm_source` | 來源 | `line` |
| `utm_medium` | 媒介 | `oa` / `broadcast` / `richmenu` |
| `utm_campaign` | 活動 | `2026q4_property` |
| `utm_content` | 素材／圖文位置 | `richmenu_bottom` |
| `utm_term` | 關鍵字（少用） | — |
| `liff_id` | **LIFF App ID 佔位** | `1657000000-abcdefg` |
| `line_oa_id` | **官方帳號 ID 佔位** | `@dingyao` |
| `ref_pillar` | 這條連結指向哪個支柱 | `property` |
| `ref_asset` | 指向哪份白皮書 | `whitepaper_property_2026` |
| `gclid` / `fbclid` | Google／Meta 點擊 ID | — |

**為什麼要在落地頁第一秒存**：LINE 的 in-app browser 與 LIFF 重導會把 query string 吃掉，
等到 L3 表單送出時 URL 已經沒有 `utm_*`。先存 sessionStorage，L1–L4 每一層都帶同一組值。

### 5.2 建議的連結格式（火星人／太陽人放連結時照這個寫）

```
https://dingyaoadvisory.tw/south-africa-property
  ?utm_source=line&utm_medium=oa&utm_campaign=2026q4_property
  &utm_content=richmenu_bottom&ref_pillar=property
  &liff_id=<待老闆建帳號後填入>&line_oa_id=@dingyao
```

### 5.3 帳號上線後要補的（不用改頁面）

1. 在 `dy-funnel.js` 的 `PARAM_MAP` 已含 `liff_id` / `line_oa_id` → **不用改**
2. 白皮書頁加 LIFF SDK 後，把 `line_user_id` 塞進 `window.dyFunnel.lead({line_user_id})` 即可
3. 若 LIFF 自動帶 `liff.state` 參數，需在 `captureAttribution` 加一行解析 —— **這是唯一可能要改的地方**，屆時 5 分鐘

---

## 六、上線前驗收（工具已建，對 live 實測 35/35）

```bash
cd ~/Documents/DingYao-Website/dingyaoadvisory-website
python3 runs/2026-10-20-funnel/verify-preflight.py https://dingyaoadvisory.tw \
        /south-africa-bank-account /south-africa-property /education /whitepapers
```

任務指定的三項硬性檢查，全部有對應：

| 任務要求 | 腳本檢查項 | live 實測 |
|---|---|---|
| 200 | HTTP 200 + body > 5KB + content-type text/html | PASS |
| 404 有 body | 對不存在路徑驗 HTTP **404**（非 200 假頁）+ body > 1KB + 有 404 語意 | PASS（440,735 bytes） |
| 原始碼不外洩 | `api_access_token` / `CHATWOOT_API_TOKEN` / `GE1kJsMKRMZQJ3EyLgkLsQjR` / `Bearer …` / `/Users/…` 正則掃描 | PASS |

另外順帶檢查：nav/footer hash 一致性、title 10–60 字、description 80–320 字、H1 恰好 1 個、
canonical、hreflang ≥2、**簡體字**、GTM 存在、**consent default 必須在 GTM 之前**。

工具本身做過負向測試（故意注入簡體字／token，確認會 FAIL），不是橡皮章。

---

## 七、需要老闆／土星人決定的 3 件事

1. **`/south-africa-property` 的 title 用哪個？**
   我建議避開「南非置產流程」（跟首頁 + 101 篇 blog + 既有流程文對撞），
   改用「南非置產**顧問服務**」。這會決定火星人的文案角度。

2. **白皮書名單落點確認 Chatwoot？**（我認為是，因為 token 已在、業務可直接回覆）
   若要 Brevo，需要老闆提供帳號與 API key，工期 +1 週。

3. **`/education` 的 H1 是否同意改？**
   現況「菁英教育入場券」沒有關鍵字，是全站三支柱裡最弱的一頁。

---

## 八、總工作量

| 階段 | 內容 | 工時 |
|---|---|---|
| ✅ 已完成 | dy-funnel.js + 測試、`/api/whitepaper` + 測試、白皮書頁 + 測試、preflight 工具、GTM 手冊 | **~6 h（本次）** |
| 待火星人 | 2 頁文案 + 8 份 FAQ + 4 份白皮書內容 | 另案 |
| 待木星人 | 2 張 hero + 6 張插圖 | 另案 |
| 待執行 | 2 頁建置（套版／head／CTA） | 9.6 h |
| 待執行 | `/education` 改造 | 2.0 h |
| 待執行 | GTM 後台建 4 tag + 4 trigger + 6 DLV + GA4 6 維度 + 2 報表 | 3.5 h |
| 待執行 | 白皮書頁上線（PDF 上傳 R2 + 文案替換 + Worker 部署） | 3.0 h |
| **合計（不含文案與產圖）** | | **≈ 18 h / 2.3 人天** |

---

## 附錄：檔案清單

```
runs/2026-10-20-funnel/
├── dy-funnel.js              ← 四層漏斗（待放 dist/js/）
├── test-funnel.py            ← 27 項實測
├── worker-v2.js              ← 含 /api/whitepaper（待覆蓋 src/worker.js）
├── test-worker.mjs           ← 25 項單元測試
├── gen-whitepapers.py        ← 白皮書頁產生器（nav/footer 自動抽自 residency）
├── build/whitepapers.html    ← 產生結果（可直接部署）
├── test-whitepapers.py       ← 34 項端到端
├── verify-preflight.py       ← 上線前驗收（可重複用）
├── GTM-SETUP.md              ← GTM／GA4 逐步手冊
└── TECHNICAL-PLAN.md         ← 本文件
```

**全部未 commit、未部署。** `runs/` 目前在 `git status` 是 `?? runs/`（untracked），
不會被 GitHub Actions 帶上線。
