# 四層漏斗 GTM／GA4 設定手冊

**日期**：2026-10-20 | **交付對象**：土星人（裁決）、泰坦人（執行）

容器：`GTM-PVWHRBWG`｜GA4 測量 ID：`G-4H4T55YXB0`（從 gtm.js 容器設定解析取得，非猜測）

---

## 0. 容器現況（2026-10-20 實測取證）

直接把 `https://www.googletagmanager.com/gtm.js?id=GTM-PVWHRBWG` 的容器 JSON 解析出來：

| 項目 | 數量 | 內容 |
|---|---|---|
| Tag | 4 | `__googtag` → GA4 設定 `G-4H4T55YXB0`；`__cvt_MQDKZ` → Microsoft Clarity `yefp1ui9nf`；`__html` → Ahrefs analytics；`__html` → Chatwoot SDK `GE1kJsMKRMZQJ3EyLgkLsQjR` |
| Trigger | 3 | 只有 GTM 內建 `gtm.init` / `gtm.js` / `gtm.load` |
| GA4 事件 tag | **0** | 搜尋 `__gaawe` 型別：無 |
| Custom Event trigger | **0** | 無 |

**結論：四層漏斗是完全從零建置 —— 4 個 Custom Event trigger + 4 個 GA4 Event tag + 6 個 Data Layer Variable。**
目前站上唯一的自訂事件是 `generate_lead`（9 處，直接 `gtag('event',...)` 或 dataLayer push），沒有分層。

> ⚠️ 沒有 GTM API 憑證（本機 gcloud 無 credentialed account），所以 tag 必須在 GTM 後台手動建。
> 本站 dataLayer 端已由 `dist/js/dy-funnel.js` 完成並實測（27/27 通過）。

---

## 1. 第一步：先建 Data Layer Variable（6 個）

GTM → 變數 → 新增 → **資料層變數**，版本選 **Version 2**：

| 變數名稱 | Data Layer Variable Name |
|---|---|
| `DLV - pillar` | `pillar` |
| `DLV - cta_id` | `cta_id` |
| `DLV - cta_location` | `cta_location` |
| `DLV - asset_name` | `asset_name` |
| `DLV - lead_type` | `lead_type` |
| `DLV - utm_source` | `utm_source` |

> 版本一定要 Version 2。Version 1 對巢狀物件與 undefined 的行為不同，會出現殘值。

---

## 2. 第二步：4 個 Custom Event Trigger

GTM → 觸發條件 → 新增 → **自訂事件**：

| Trigger 名稱 | 事件名稱 | 觸發時機 |
|---|---|---|
| `CE - view_service_page` | `view_service_page` | 所有自訂事件 |
| `CE - cta_click` | `cta_click` | 所有自訂事件 |
| `CE - lead_submit` | `lead_submit` | 所有自訂事件 |
| `CE - booking_confirmed` | `booking_confirmed` | 所有自訂事件 |

---

## 3. 第三步：4 個 GA4 Event Tag

GTM → 代碼 → 新增 → **Google Analytics：GA4 事件**

共同設定：
- 評估 ID：`G-4H4T55YXB0`
- 「傳送產品資料」不用勾

### 3.1 `GA4 - L1 view_service_page`

- 事件名稱：`view_service_page`
- 參數：

| 參數名稱 | 值 |
|---|---|
| `pillar` | `{{DLV - pillar}}` |
| `page_path` | `{{Page Path}}` |
| `funnel_layer` | `L1` |

- 觸發條件：`CE - view_service_page`

### 3.2 `GA4 - L2 cta_click`

- 事件名稱：`cta_click`
- 參數：

| 參數名稱 | 值 |
|---|---|
| `pillar` | `{{DLV - pillar}}` |
| `cta_id` | `{{DLV - cta_id}}` |
| `cta_location` | `{{DLV - cta_location}}` |
| `funnel_layer` | `L2` |

- 觸發條件：`CE - cta_click`

### 3.3 `GA4 - L3 lead_submit`

- 事件名稱：`lead_submit`
- 參數：

| 參數名稱 | 值 |
|---|---|
| `pillar` | `{{DLV - pillar}}` |
| `asset_name` | `{{DLV - asset_name}}` |
| `lead_type` | `{{DLV - lead_type}}` |
| `funnel_layer` | `L3` |

- 觸發條件：`CE - lead_submit`

### 3.4 `GA4 - L4 booking_confirmed`

- 事件名稱：`booking_confirmed`
- 參數：

| 參數名稱 | 值 |
|---|---|
| `pillar` | `{{DLV - pillar}}` |
| `funnel_layer` | `L4` |

- 觸發條件：`CE - booking_confirmed`
- **建議另勾「將此事件標記為重要事件」(key event)** —— 這是營收級轉換，要能直接看轉換數。

---

## 4. 第四步：GA4 後台註冊自訂維度（不做這步，報表看不到 pillar 切分）

GA4 → 管理 → **自訂定義** → 建立自訂維度（範圍一律選 **事件**）：

| 維度名稱 | 事件參數 |
|---|---|
| 服務支柱 (pillar) | `pillar` |
| CTA 編號 (cta_id) | `cta_id` |
| CTA 位置 (cta_location) | `cta_location` |
| 白皮書名稱 (asset_name) | `asset_name` |
| 名單類型 (lead_type) | `lead_type` |
| 漏斗層級 (funnel_layer) | `funnel_layer` |

> 這是最常漏的一步。沒有註冊，事件照樣進來，但探索報表拉不到這個維度。
> 註冊後要等 **24 小時**才生效，且只對「註冊之後」的資料回溯，舊資料不會補。

---

## 5. 第五步：按支柱看 L1→L4 轉換率

GA4 → **探索** → 建立新探索 → 選「**漏斗探索**」

設定：
- 漏斗步驟 4 步，每步「步驟名稱 + 條件 = 事件名稱」：
  1. `L1 進入服務頁` → 事件 `view_service_page`
  2. `L2 點主 CTA` → 事件 `cta_click`
  3. `L3 留下名單` → 事件 `lead_submit`
  4. `L4 預約成立` → 事件 `booking_confirmed`
- 「細分」維度：`pillar`
- 漏斗類型：**封閉漏斗**（必須依序完成）／想看寬鬆歸因改「開放漏斗」

另建一個「**任意形式**」探索表，把 `pillar` 放維度、`事件名稱` 放列，
一次看到三個支柱每一層的人數與層間轉換率。

### 預期可回答的問題
- 銀行開戶 / 置產 / 教育 哪個支柱的 L2→L3 掉最多？
- 哪個 `cta_location`（hero / bottom_cta）帶來的 L3 最多？
- 白皮書下載（`asset_name`）帶來的 L4 佔比？

---

## 6. Consent Mode v2 的影響（必讀，否則數字會偏低）

站上已設定 `gtag('consent','default', {... analytics_storage:'denied' ...})`，
使用者未按「同意」前 GA4 不寫 cookie。影響：

1. **未同意者的事件不會計入標準報表** → L1/L2 會比實際流量低。
2. GA4 會用 **行為模擬（behavioral modeling）** 估算，但只在流量足夠時才有。
3. **L4 是營收級事件，不能只靠前端**。第二階段建議：
   - 預約成立後由 n8n / Chatwoot webhook 送 **GA4 Measurement Protocol**，
     伺服器端送出不受 consent 影響（有正當利益基礎），數字才準。
   - 這一階段沒有做之前，L4 只能看「有同意者的前端訊號」，會明顯低估。

**建議先向老闆說明：第一階段 L1→L4 的絕對數字會偏低，比率（轉換率）比絕對值可信。**

---

## 7. dataLayer 實際寫法（已實作於 `js/dy-funnel.js`）

### L1 進入服務頁（自動）
頁面載入時，若 pillar 屬於三支柱之一：
```js
dataLayer.push({
  event: 'view_service_page',
  event_category: 'funnel_l1',
  pillar: 'property',              // bank_account | property | education
  service_pillar: 'property',
  page_path: '/south-africa-property',
  page_lang: 'zh',
  dy_session_id: 's_mvg9ki2w_upgpxk',
  dy_funnel_version: '1.0.0',
  utm_source: 'line',              // 有才帶
  utm_campaign: '2026q4_property',
  liff_id: '1657000000-abcdefg'
});
```
- 同 session 同 pillar 只送一次（重整不重複計數）

### L2 點主 CTA（自動，事件委派）
頁面標記方式：
```html
<a href="/consultation" data-cta-id="hero_primary" data-cta-location="hero">預約免費評估</a>
```
推送：
```js
dataLayer.push({
  event: 'cta_click',
  event_category: 'funnel_l2',
  cta_id: 'hero_primary',
  cta_location: 'hero',
  cta_text: '預約免費評估',
  pillar: 'property',
  utm_source: 'line',
  dy_session_id: 's_...'
});
```
- 沒標 `data-cta-id` 的 CTA 會走 fallback（`a[href*="consultation"]`），
  `cta_id` 自動變成 `auto__consultation`，`cta_location=untagged` → 可用來稽核「哪些 CTA 忘了標」
- capture phase 同步 push，不延遲導航

### L3 留下名單（手動呼叫，表單成功後）
```js
window.dyFunnel.lead({
  lead_type: 'whitepaper',            // whitepaper | calculator | form
  asset_name: 'whitepaper_property_2026',
  form_id: 'wpForm',
  pillar: 'property'                  // 選填；不填用頁面推導
});
```
推送 `event: 'lead_submit'`，含 pillar / asset_name / lead_type / form_id。
同時寫入 sessionStorage 供 L4 回溯來源。

既有 `lm-form.js`（首頁／assets／部分 blog 在用）**不用改**：
`dy-funnel.js` 用 MutationObserver 偵測 `#lmSuccess` 變 `display:block` 後自動補送 L3。

### L4 預約成立
預約完成後導向：
```
/booking-confirmed?booking=1&ref=BK-2026-0042&slot=2026-10-28T14:00
```
`dy-funnel.js` 偵測到路徑 + `booking=1` 才送：
```js
dataLayer.push({
  event: 'booking_confirmed',
  event_category: 'funnel_l4',
  pillar: 'property',                 // 由 L3 的 meta 繼承
  booking_ref: 'BK-2026-0042',
  booking_source: 'confirmation_page',
  booking_slot: '2026-10-28T14:00',
  origin_asset: 'whitepaper_property_2026',
  dy_session_id: 's_...'
});
```
- **沒有 `booking=1` 就不送** —— 防止直接開頁面被誤計成預約成立（已實測）
- 若預約走 Calendly / Chatwoot 而無法導頁，改由 widget 回呼 `window.dyFunnel.booking({...})`

---

## 8. 實測結果（真 Chromium，非靜態檢查）

`runs/2026-10-20-funnel/test-funnel.py`：**27/27 通過**

涵蓋：L1 四個參數齊備、同 session 去重、L2 兩個 CTA 可區分、L2 未標記走 fallback、
L3 asset/pillar/UTM 繼承、L4 由 L3 繼承 pillar 與 origin_asset、L4 無確認參數不送、
非支柱頁不送 L1、全程零 JS 例外。

複跑：`python3 runs/2026-10-20-funnel/test-funnel.py`

---

## 9. 建置順序建議

1. 先上 `js/dy-funnel.js` + 服務頁（此時 dataLayer 已在推，GTM 還沒有 tag → 不影響任何東西）
2. GTM 建 6 個 DLV → 4 個 trigger → 4 個 tag
3. **用 GTM 預覽模式**在服務頁走一遍，逐一確認 4 個事件都有觸發、參數有值
4. 發布容器
5. GA4 註冊 6 個自訂維度（等 24h）
6. 建漏斗探索報表

> 順序不能顛倒。先建 tag 再上 JS，會有一段時間 tag 收不到事件，容易被誤判成「壞了」。
