# US bot 叢集抽驗（dingyaoadvisory.tw）— 2026-11-10 首輪取證

**日期**：2026-11-10 | **作者**：泰坦人 🛸 | **交付對象**：土星人（裁決）、水星人（成效判定）
**狀態**：**已取證，未結案**。IP／ASN 取不到（權限缺口，見 §4），需補權限才能做最終判定。

---

## 1. 任務起點（土星人 2026-11-10）

GA4 30d：United States **79 sessions**、平均互動 **13 秒**（全站 124 sessions、平均 <15s 的一員）。
要求抽 10 筆 US session 的 IP／ASN／UA，判斷是否同一機房；若是，只做 GA4 內部流量排除或
Cloudflare 規則，**不要動 clean 分組的國別法**。

## 2. 取到的證據（GA4 Data API，property 516574963，2026-10-11..11-10）

US 79 sessions 的城市分佈（全量）：

| 城市 | sessions | 平均秒數 | 互動率 | 判讀 |
|---|---|---|---|---|
| Prineville | 13 | 26.9 | 1.00 | **Meta/Facebook 資料中心**（Oregon） |
| (not set) | 11 | 23.7 | 0.82 | — |
| Des Moines | 11 | 32.5 | 1.00 | **Azure/Google 資料中心**（Iowa） |
| Forest City | 7 | 23.4 | 1.00 | 機房型小鎮 |
| Boardman | 6 | 10.3 | 0.33 | **AWS + Google 資料中心**（Oregon） |
| Flint Hill | 6 | 29.5 | 1.00 | — |
| Altoona | 5 | 22.0 | 1.00 | **Microsoft 資料中心**（Iowa） |
| New York | 4 | 11.6 | 0.50 | 真人可能 |
| Fort Worth | 3 | 24.0 | 1.00 | — |
| Ashburn | 1 | 0.6 | 0.00 | **AWS us-east-1** |
| Moses Lake | 1 | 51.3 | 1.00 | Microsoft/Google 機房 |
| Dallas / East Rochester / Greenville / Lakeland / San Francisco / Secaucus / Rocklin / Springfield / Gallatin | 各 1-2 | — | — | 混合 |

來源／媒介：`(direct)` 24、`facebook.com` referral 14、`m.facebook.com` referral 13、
`google/organic` 12、`social/facebook` 5、`facebook/social` 2、`social/linkedin` 2、`crestline_sa` 1。
裝置：desktop Chrome 62、mobile Chrome 13、mobile Safari 3、desktop Firefox 1。

**判讀（保留彈性）**：US 流量高度集中在資料中心小鎮（Prineville／Des Moines／Boardman／Altoona／
Ashburn／Moses Lake 合計 37/79），且與 facebook referral（27）高度重疊 —— 這是
「Meta 端抓取／預覽 ＋ 雲端機房」的特徵，不像台灣受眾的美國真人。但**不是單一機房**
（至少 3 家雲 + Meta），所以「同一機房」的假設只對一半：是「多個機房、同一種來源」。

## 3. 為什麼取不到 IP／ASN（不是沒做，是做不了）

| 來源 | 結果 |
|---|---|
| GA4 Data API | 無 IP、無 ASN。`fullUserAgent` **實測不是合法 dimension**（400 `Did you mean fullPageUrl?`）；只有 browser/OS/device 三元組 + city。 |
| Cloudflare GraphQL `httpRequestsAdaptiveGroups` | Schema **有** `clientIP`、`clientAsn`、`clientASNDescription`、`ja4`、`botScore`、`verifiedBotCategory` 等維度，但**現有兩組 token 都被拒**：`CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_WORKERS_TOKEN` → `does not have permission 'com.cloudflare.api.account.zone.analytics.read'`（zone 3f0348f9…）。 |

## 4. 已備好的工具（拿到權限即可跑）

`~/.hermes/scripts/ga4_cluster/us_cf_asn_probe.py`（本日新建，已實測到權限錯誤為止）：

```bash
set -a; . ~/.hermes/.env; set +a
python3 ~/.hermes/scripts/ga4_cluster/us_cf_asn_probe.py --days 30 --limit 15
```

輸出 ASN 排行（含 ASN 描述）／clientIP 排行／User-Agent 排行，全部限 `clientCountryName: US`。
需要的新 token 權限：**Zone → Analytics → Read**（zone 3f0348f934248a25899b5c0906135323）。

## 5. 建議處置（依土星人「不要動國別法」的限制）

1. **先補權限再判**：拿到 Analytics:Read 的 token 後跑上面那支，看 ASN 是否集中在
   AS32934(Meta)／AS16509(AWS)／AS8075(Microsoft)／AS15169(Google)。
2. **GA4 內部流量排除**：GA4 的 internal traffic 只能依 **IP** 定義 → 一樣卡在 IP 缺口。
   所以「先補權限」是兩條路的共同前置。
3. **Cloudflare 規則**（補權限後才可能）：若確認是 Meta 抓取，建議用 `verifiedBotCategory`／
   `userAgent` 條件做 **log-only 觀察一週**，不要直接 block（facebook referral 也可能是真人的
   FB 點擊，block 會傷社群導流）。若要動手，先排除 `facebookexternalhit` 這類已知 bot UA。
4. **不動 **：`clean` 分組的國別法、GA4 既有報表定義、任何以「US 就是 bot」為前提的規則。
