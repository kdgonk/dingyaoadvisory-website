# EGM 待審文件：dingyaoadvisory.tw 的 www → 非 www 301（2026-11-10）

**日期**：2026-11-10 | **交付對象**：土星人（裁決／追蹤）＋泰坦人（後續維運）
**審查類型**：技術維運審查（persona A）／SEO 重導向審查（persona B）
**狀態**：已上線（commit `a1323618` → `fb3cb8c0`），EGM 兩隻 goldfish 已跑，Blocker 逐條處置見 §6

---

## 1. 問題陳述（改動前實測）

`www.dingyaoadvisory.tw` 與 `dingyaoadvisory.tw` 都是同一個 Cloudflare Worker（`dingyao`，Workers Static Assets 型）
的 **custom domain**，資產層只依「路徑」比對，不看 hostname，因此 www 子網域是主站的完整鏡像：

| 檢查 | 結果 |
|---|---|
| `curl -sI https://www.dingyaoadvisory.tw/` | `HTTP/2 200`（無 location） |
| 首頁 HTTP size（www / apex） | `114340` / `114340`（完全相同） |
| www `/blog`、`/about`、`/contact`、`/assets-en` | 全部 `200`，無重導向 |
| 對照站 crestlineadvisory.co.za、canvascrest.co.za | www 皆 `301` + 正確 location |

Google Search Console 已對應到「替代頁面（有適當標準標記）14 個」與「這是重複網頁，使用者未選取標準網頁 3 個」。

## 2. 限制條件（決定工法的三個硬條件，均已實測）

1. **主網域行為不可改變**（派工明文）。
2. **本機兩把 Cloudflare token 都無法建立 zone/account 層 redirect 規則**：
   - `GET /zones/{z}/rulesets/phases/http_request_dynamic_redirect/entrypoint` → `request is not authorized`
   - `GET /zones/{z}/pagerules` → `9109`
   - `POST /accounts/{a}/workers/domains`（自訂網域掛載）→ `10405 Method not allowed for this authentication scheme`
   ⇒ 不能用 Redirect Rules / Bulk Redirects / 換 custom domain 綁定的方式做。
3. **Cloudflare `_redirects` 不支援 domain-level 轉址**（官方文件 Advanced redirects 表：Domain-level redirects ❌），
   所以不能在 `dist/_redirects` 寫 `www.example.com/*`。

## 3. 採用的工法

### 3.1 `src/worker.js`：fetch() 最前面加 host 判斷（在任何 /api、/go 分支與 ASSETS 之前）

```js
const reqHost = url.hostname.replace(/\.$/, '');        // 尾點 FQDN 也命中
if (reqHost === 'www.dingyaoadvisory.tw') {
  let p = url.pathname;                                  // 先做 apex 的 html_handling 正規化
  if (p.endsWith('/index.html')) p = p.slice(0, -'/index.html'.length) || '/';
  else if (p.endsWith('.html')) p = p.slice(0, -'.html'.length);
  if (p.length > 1) p = p.replace(/\/+$/, '') || '/';
  const target = 'https://dingyaoadvisory.tw' + p + url.search;
  const status = (request.method === 'GET' || request.method === 'HEAD') ? 301 : 308;
  return new Response(null, { status, headers: {
    'Location': target, 'Cache-Control': 'public, max-age=3600' } });
}
```

設計要點：

- 保留 query string（`url.search` 直接拼接）；pathname 先正規化成 apex 的終點形式，
  **301 的目標必須是終點**。第一版原樣轉發造成 `www/about/` → 301 `apex/about/` → 307 `apex/about`
  （實測 2 跳，且 307 是暫時轉址、Googlebot 每次重爬都要重走）—— 已於 `fb3cb8c0` 修正，實測 13 種變體全部單跳。
- GET/HEAD → `301`；其他方法 → `308`（301 會被瀏覽器改寫成 GET，非 GET 請求會靜默變形）。
- hostname 用完整字串比對（去掉尾點後），不用 `startsWith('www')`，避免誤傷其他子網域。
- 主網域走原本的 `env.ASSETS.fetch(request)` 路徑，未改動。

### 3.2 `wrangler.jsonc`：`run_worker_first` 由 6 條動態前綴改為 `["/*", 排除靜態資產]`

```
"/*",
"!/css/*", "!/js/*", "!/blog/images/*",
"!/*.jpg", "!/*.jpeg", "!/*.png", "!/*.webp", "!/*.avif", "!/*.svg", "!/*.ico", "!/*.gif"
```

**為什麼一定要改這一行（否則 3.1 完全無效）**：Workers Static Assets 預設「先服務資產，Worker 不執行」，
而 www 的 `/`、`/blog`、`/about`、`/contact` 全都有實體檔 → Worker 永遠不會被叫到。

實測證據（改動前，www 隨機缺頁）：
```
HTTP/2 404
cache-control: public, max-age=0, must-revalidate
cf-cache-status: HIT
```
→ 資產層產生的 404；Worker 內的 404 `no-store` 覆寫沒生效，證明 Worker 沒有執行。

**排除清單的覆蓋率（已量）**：dist 內 376 個 html、3 個 css、2 個 js、約 370 張圖片。
圖片只存在於 `dist/blog/images/**`（343+28 個子目錄檔）與 dist 根目錄 23 檔 → 全部被排除樣式涵蓋。
驗證方式用 `cf-cache-status: HIT`（＝資產層回應），**不能用 `200`**（Worker 轉發也是 200）。

**為什麼不排除 `.xml` / `.txt` / `.json` / `.webmanifest` / `.vcf` / `.xsl`**：
這些在 www 上也必須 301（`sitemap.xml`、`sitemap-news.xml`、`robots.txt`、`llms.txt`、`webmcp.json`、
`site.webmanifest`、`scott.vcf`、`sitemap.xsl`、`.well-known/ai.json`），否則 www 會繼續供應第二份索引檔。
實測這 7 條現在全部 301。

## 4. 部署與驗收

部署路徑：`git push main` → GitHub Actions `Deploy with Wrangler` → 完成後 `purge_everything` → 驗。
- commit `a1323618`，run `42745704774` success
- commit `fb3cb8c0`，run `42746560154` success（正規化＋配額腳本）

| 驗收項 | 結果 |
|---|---|
| `curl -sI https://www.dingyaoadvisory.tw/` | `301`，`location: https://dingyaoadvisory.tw/` |
| `https://www.dingyaoadvisory.tw/blog` | `301`，`location: https://dingyaoadvisory.tw/blog` |
| `/about`、`/contact`、`/assets-en`、`/sitemap.xml`、`/robots.txt` | 全部 `301`，location 正確 |
| `/blog/?utm_source=line&utm_medium=oa` | `301`，query string 完整保留 |
| `/about/`、`/about.html` | `301` 直達 `https://dingyaoadvisory.tw/about`（`hops=1`） |
| 尾點 FQDN `www.dingyaoadvisory.tw./blog` | `301`（本機 harness 驗） |
| Chrome UA + `Accept: text/html` 同一批路徑 | 全部 `301` |
| Googlebot UA `www/blog` | `301` |
| `https://dingyaoadvisory.tw/` | `200`，`114340` bytes（與改動前相同） |
| 主網域 `/blog`、`/about`、`/contact`、`/assets-en` | `200`，bytes 與改動前相同 |
| 主網域 `/api/health` | `200 {"ok":true,"chatwoot_token_configured":true}` |
| 主網域 `/go/bank`、`/l/bank` | `302` + 原本 UTM 目標不變 |
| 主網域缺頁 | `404` + body `446505B` + `cache-control: no-store` |
| `dist/_redirects` 抽樣 4 條（sarb-july… 系列） | 仍 `301` → 正確目標（Worker 先跑不影響） |
| 301 目標端 `curl -L` | 所有抽樣路徑最終 `200`，`hops=1` |
| 靜態資產 `www/css/tailwind.min.css` | `200` 且 `cf-cache-status: HIT`（＝確實沒進 Worker） |
| `http://www/` | `301 → https://www/ → 301 → apex`（2 跳，因 CF Always Use HTTPS 先插手） |

## 5. 索引層證據（SEO 審查要求的四項，全部為 0 筆）

| 檢查 | 指令 | 結果 |
|---|---|---|
| dist 內任何 `www.dingyaoadvisory.tw` 字串 | `search_files pattern='www\.dingyaoadvisory\.tw' path=dist` | **0** |
| canonical 指向 www | 同上（canonical 全為 `https://dingyaoadvisory.tw/...`） | **0** |
| hreflang 指向 www | 同上 | **0** |
| `og:url` 指向 www | 同上 | **0** |
| sitemap 內 www `<loc>` | `grep -c` on `dist/sitemap.xml` | **0**（331 筆全 apex） |
| robots.txt 的 `Sitemap:` | `grep -i sitemap dist/robots.txt` | 兩行皆 `https://dingyaoadvisory.tw/...` |
| apex `/blog/` vs `/blog` | `curl -sI` | `/blog/` → `307` → `/blog`（單一 canonical 形式，無同 host 重複） |

sitemap `lastmod` 最新為 `2026-11-09`，**本次刻意不 bump**：內容沒變、只是加轉址，
bump lastmod 會製造「內容已更新」的假訊號（既有鐵則）。

## 6. EGM 審查處置（2 隻 goldfish：技術維運 A、SEO 重導向 B）

### 6.1 技術維運審查（A）

| # | Blocker | 處置 |
|---|---|---|
| A-B1 | 404 由資產層改為 Worker 產生後不再被邊緣快取，掃描流量會計入 Worker 請求數（免費 100k/日），body 446KB | **接受風險（已量化）**。新增 `scripts/cf_worker_quota.py` 實測：改動前 dingyao Worker 每日 **6~33 次**（僅 /api /go /l），2026-11-10 含本次驗證流量 **115 次＝上限 0.11%**。446KB 之謎已查清＝**Cloudflare Fonts 在邊緣注入 `/cf-fonts/` @font-face**（`dist/404.html` 51,473B → live 446,505B，live 內含 `cf-fonts`），與本次改動無關。**正解**：改用 zone Redirect Rule（需 dashboard 權限），之後把 `run_worker_first` 收回動態前綴。觸發門檻：`cf_worker_quota.py` 峰值 > 30% 就處理 |
| A-B2 | 全文沒有配額數字、沒有回滾程序 | **已補**：配額數字見上；回滾步驟見 §7 |
| A-B3 | `www/about/`、`www/about.html` 產生 2 跳（301→307） | **已修**（`fb3cb8c0`）：301 直接導到正規化終點，實測 `hops=1` |
| A-B4 | `_redirects` 100+ 條現在位於 Worker→ASSETS 之間，驗收沒抽樣 | **已驗＋已加註**：抽樣 4 條仍 301；`src/worker.js` 在 `env.ASSETS.fetch` 前加「不得吞掉非 200 資產回應」的註解 |

技術維運建議：①§5 措辭矛盾 → 已改寫為「301 進瀏覽器近乎永久，rollback 需清快取」；
②「webmcp.json 等仍 200」→ **實測全部 301，該指稱不成立**；③改正向白名單 → **不採用**（extensionless 頁面無法用 glob 正向表達，且 `/*` 已被 wrangler 判定與舊前綴互斥）；
④OPTIONS 308 → 接受（www 上沒有任何頁面會發 preflight；改 204 反而讓 stale www 頁的 POST 靜默失敗）；
⑦purge 太粗 → 本次 host 層改動用 `purge_everything` 一次，之後例行改動改 by-prefix；
⑧「用 200 證明沒進 Worker」方法錯誤 → **已改用 `cf-cache-status: HIT`**。

### 6.2 SEO 重導向審查（B）

| # | Blocker | 處置 |
|---|---|---|
| B-B1 | 未驗 canonical／og:url 指向 | **已驗，0 筆指向 www**（§5） |
| B-B2 | 未驗 hreflang | **已驗，0 筆含 www**（§5） |
| B-B3 | 未驗 apex HTML 內 www 絕對連結 | **已驗，dist 全站 0 筆**（含 nav/footer/JSON-LD） |
| B-B4 | 未驗 apex sitemap 內容 | **已驗：331 筆全 apex、0 筆 www**；lastmod 未 bump（刻意） |
| B-B5 | 沒有 GSC 基線與觀察排程 | **部分接受**：基線＝GSC 現值（替代頁面 14／重複網頁 3）。觀察點 T+7／T+14／T+30 檢查「頁面有重新導向」「替代頁面」「重複網頁」三類計數是否收斂。**同一 zone 內的 www→apex 不適用「變更網址」工具**（審查者正確指出） |
| B-B6 | 「圖片不進 Worker」缺直接證據、負向樣式可能覆蓋不全 | **已驗**：圖片僅存在 `dist/blog/images/**` 與 dist 根目錄，全被排除；`www/css/tailwind.min.css` 回 `cf-cache-status: HIT` 為證 |
| B-B7 | `/blog` vs `/blog/` 是否同 host 重複 | **已驗**：apex `/blog/` → `307` → `/blog`，單一形式 |

SEO 建議：`/go`、`/l` 在 www 用 301 → **接受**（301 的目標是 apex 的固定路徑，活動換目標改的是 apex 的 302，不會被瀏覽器快取卡住）；
`http://www` 2 跳 → **接受並記錄**（CF Always Use HTTPS 先插手，只有 zone Redirect Rule 能併成 1 跳）；
圖片仍 200 → 接受（HTML 已 301，不會有頁面引用 www 圖片）。

## 7. 回滾（runbook）

1. `git revert <sha>`（`fb3cb8c0`、`a1323618`）→ push main，等 `Deploy with Wrangler` success。
   - 只回滾 worker.js 的轉址區塊、保留 `run_worker_first` 也可以，但**不可只回滾 `run_worker_first`**：
     轉址寫在 Worker 裡，收回 `"/*"` 會讓 301 對有實體檔的路徑失效（變成 200 鏡像）。
2. `purge_everything`（host 層改動，逐 URL purge 不實際）→ 等 4~5 秒。
3. 驗 `curl -sI https://dingyaoadvisory.tw/` = 200、`https://www.dingyaoadvisory.tw/` = 200。
4. ⚠️ 已進瀏覽器的 301 是**語意上的永久**：曾訪問過 www 的使用者需自行清該站資料。
5. 判定門檻（何時該回滾）：apex 出現非預期 5xx、`cf_worker_quota.py` 峰值 > 30%、或 apex 首頁 bytes 與 `dist/index.html` 明顯不符。

## 8. 待決事項（不在本次範圍）

1. **原始碼外洩（建議獨立開票，P1）**：`dist/` 內的 `.py`／`.sh`／`.md`（`ahrefs-repair.py`、`add-geo-tags.sh`、
   `update_all*.py`、`SEO-AUDIT-REPORT.md`、`SITEMAP-REPORT.md`）live 全部 `200`。
   已檢查**無硬編碼憑證**，洩漏的是內部工具與報告內容。修法：`dist/.assetsignore` 加 `*.py|*.pyc|*.sh|*.md`。
2. **永久解（建議向老闆提案）**：用 dashboard 建一條 zone Single Redirect Rule
   （`http.host eq "www.dingyaoadvisory.tw"` → `concat("https://dingyaoadvisory.tw", http.request.uri.path)`，301、保留 query），
   然後把 `run_worker_first` 收回 6 條動態前綴。好處：1 跳（含 http→https）、404 回歸邊緣快取、Worker 額度歸零。
   現行 Worker 方案是「無 dashboard 權限下唯一可 git push 部署」的解法。
3. **watchdog（建議）**：每日抽驗 6 條 www 路徑必須 301 且 location 正確，失敗告警 —
   因為整套修法只靠 `wrangler.jsonc` 一行，任何人改回動態前綴就會靜默失效，而 GSC 要數週才看得出來。
