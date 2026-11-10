# GSC 遞送佇列新增「急件優先層」（學制頁兩語索引異常）— 2026-11-10

**日期**：2026-11-10 | **作者**：泰坦人 🛸 | **交付對象**：土星人（11-13 複驗）
**變更檔**：`~/.hermes/profiles/titan/scripts/gsc_index_submit_queue.py`（不在 repo；skill 副本已同步）
**狀態**：已上線（cron `e99bdf25a719`，每日 09:10），本日已實跑一次並遞送成功。

---

## 1. 起點（土星人 2026-11-10，急件／今日已先止血）

| URL | GSC coverageState（土星人回報） | lastCrawlTime |
|---|---|---|
| `/blog/south-africa-school-curriculum-caps-ieb-cambridge-2026` | Google 無法辨識的網址 | never |
| 同頁 `-en` | 已找到－目前尚未建立索引 | never |

兩頁實測 HTTP 200、都在 `sitemap.xml` 與 `sitemap-news.xml`，土星人已手動 publish（Indexing API ×2）
＋重送兩份 sitemap。交付要求：加進輪播、**每日重 ping 直到不再是 unknown／未索引，最多到 11-18**。

## 2. 我的基線實測（URL Inspection API，2026-11-10 20:0x）

```
/blog/south-africa-school-curriculum-caps-ieb-cambridge-2026    | Discovered - currently not indexed | verdict=NEUTRAL | lastCrawl=(never)
/blog/south-africa-school-curriculum-caps-ieb-cambridge-2026-en | Discovered - currently not indexed | verdict=NEUTRAL | lastCrawl=(never)
```

⚠️ 與土星人回報的差異：**ZH 已從「URL is unknown to Google」前進到「Discovered - currently not indexed」**
（＝Google 已經發現這個 URL，只是還沒排到爬取）。這是土星人手動 publish ＋重送 sitemap 的即時效果，
不是資料不一致。EN 與回報一致。

`sitemap-news.xml` 現況實測：只有 2 個 `<loc>`，就是這兩頁；兩頁 JSON-LD `datePublished` 都是
`2026-11-09`，與 sitemap lastmod 相符 → **目前沒有 10-26 那種「datePublished 偏移」**。

## 3. 改了什麼（兩層架構，不動既有行為）

- 新增 `PRIORITY` 清單：每筆含 `cooldown_days: 1`、`until: "2026-11-18"`，兩頁都列入。
- 每次執行順序：① PRIORITY（先跑 URL Inspection）→ ② QUEUE（原本 6 頁輪播，2 頁/日、冷卻 3 天，**未改**）。
- 畢業機制：`verdict == PASS` → 寫 `state.priority_done` 並跳過遞送（不浪費配額）；隔天起不再 pings。
- 到期機制：`today > until` → 摘要印「⚠️ 需人工確認 GSC」，不再遞送。
- 摘要（cron 訊息）同時輸出兩層，含當次 coverageState：
  `索引遞送 2026-11-10：…｜優先佇列：<slug> 已送（Discovered - currently not indexed）`
- **不 bump lastmod**：重 ping 不是內容變更，bump 會製造假 lastmod（2026-10-28 事故）。

## 4. 驗證

實跑一次（先備份 `~/.hermes/state/gsc_index_submit_state.json` → `/tmp/gsc_state_backup_20261110_2011.json`）：

```
索引遞送 2026-11-10：送出 0/0 頁 → 無（ok=0，fail=0；lastmod bumped 0）
｜優先佇列：…-2026 已送（Discovered - currently not indexed）；…-2026-en 已送（Discovered - currently not indexed）
```

state／log 證據：

```
last_submitted: south-africa-school-curriculum-caps-ieb-cambridge-2026    = 2026-11-10
last_submitted: south-africa-school-curriculum-caps-ieb-cambridge-2026-en = 2026-11-10
priority_done: {}
log: 2026-11-10 20:11:38 | priority inspect | … | Discovered - currently not indexed | verdict=NEUTRAL | lastCrawl=(never)
log: 2026-11-10 20:11:39 | priority submit OK | … | {'urlNotificationMetadata': {...}}
```

分支邏輯（以 import + monkeypatch 驗，不燒 API 額度）：

| 情境 | 結果 |
|---|---|
| `verdict=PASS`（已索引） | `INDEXED` → 寫 priority_done、**不遞送** ✅ |
| `today=11-19`（超過 until） | `EXPIRED` → 不遞送、印需人工確認 ✅ |
| 當日已送過 | `COOLDOWN` → 不重複送 ✅ |
| 隔日 | 會再送（fake service 故意回 FAIL 以證明有嘗試）✅ |

## 5. 給 11-13 複驗的檢查點

1. `python3 ~/.hermes/profiles/titan/scripts/gsc_index_submit_queue.py --status` → 看兩頁是否已畢業。
2. `~/.hermes/logs/gsc_submit_queue.log` → 每天 `priority inspect` 的 coverageState 變化
   （`Discovered` → `Crawled` → `Submitted and indexed` 是正常軌跡）。
3. 若 ZH 在 11-13 仍停在 **unknown to Google**（退回原狀）→ 依土星人指示查 `sitemap-news.xml`
   的 `datePublished` 是否偏移（10-26 前例：偏移 2 天造成 48h 空窗）。今天實測未偏移。
4. 11-18 到期後若仍未索引 → 佇列會自動停送並印 ⚠️，需人工決定是否續期或改內容策略。
