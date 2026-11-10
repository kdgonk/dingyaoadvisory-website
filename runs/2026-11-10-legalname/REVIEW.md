# EGM 待審文件：dingyao 全站 JSON-LD legalName 改為中文法定全名（2026-11-10）

**日期**：2026-11-10 | **交付對象**：土星人（裁決／追蹤）
**審查類型**：結構化資料正確性（persona A）／品牌命名一致性（persona B）
**狀態**：已上線（commit `8616ab49`，GH Actions run `42753429844` success，已 purge）

---

## 1. 問題（老闆 2026-11-10 實測）

- **GBP（Google 商家檔案）名稱**＝「鼎曜國際顧問有限公司 DingYao Advisory」。
- **官網 JSON-LD 的 legalName** 在此之前一直是品牌名 `"DingYao Advisory"`，全站沒有任何節點寫出「有限公司」。
- Google 搜尋結果因此對 `首頁`、`/about`、`/contact` 標「缺少字詞：有限」／「缺少字詞：有限公司」——
  官網與 GBP 被當成兩個實體，品牌信心與 AI 搜尋辨識都受影響。

## 2. 改動內容（只動 legalName 一個欄位）

| # | 動作 | 處數 |
|---|---|---|
| 1 | 既有值替換：`"legalName": "DingYao Advisory"` → `"legalName": "鼎曜國際顧問有限公司"` | **326**（331 檔） |
| 2 | 補欄位：文章 `publisher` 內嵌 DingYao Organization 缺 legalName | **22** |
| 3 | 補欄位：`/contact`、`/contact-en` 的 `ContactPage.mainEntity` Organization（原本完全沒有 legalName） | **2** |

- 合計變更 331 檔、350 插入 / 326 刪除；`git diff` 中**每一條變動行都含 legalName**（0 條例外）。
- **未動**：`name`、`alternateName`、`title`、`meta`、其他任何 schema 欄位；Crestline 與 CanvasCrest 的節點。
- 英文法定全名 `DingYao International Advisory Ltd.` **仍未進 JSON-LD**（維持只出現在隱私權／免責聲明的「法律當事人」欄位）。
- 改動腳本：`scripts/fix_legalname_zh_2026_11_10.py`（可重跑、idempotent，內建三條不變式）。

## 3. 驗證（改動後，本機 + live）

本機（腳本內建不變式，`--apply` 每次都跑）：

- 376 檔、**1453 個 JSON-LD block 全部 `json.loads` 通過，0 錯誤**。
- 把兩邊的 `legalName` 全部剝除後新舊 JSON **deep-equal** ⇒ 只動了 legalName。
- 非 JSON-LD 的 HTML 區塊**位元組完全相同**。
- legalName 值分佈：`鼎曜國際顧問有限公司` 350 / `Crestline Advisory (Pty) Ltd` 17 / `CanvasCrest Properties (Pty) Ltd` 17；舊值殘留 **0**。

Live（purge 後實測）：

```
$ curl -s https://dingyaoadvisory.tw/ | grep -o "legalName[^,]*"
legalName": "鼎曜國際顧問有限公司"        ← block 0（FinancialService+Organization）
legalName": "鼎曜國際顧問有限公司"        ← block 4（@graph 的 Organization）
legalName": "Crestline Advisory (Pty) Ltd"
legalName": "CanvasCrest Properties (Pty) Ltd"

$ /about    → 鼎曜國際顧問有限公司 ×2、Crestline ×1、CanvasCrest ×1
$ /contact  → 鼎曜國際顧問有限公司 ×1（mainEntity）
```

Python 解析 live 三頁：`/` 5 blocks parsed_ok=5、`/about` 5/5、`/contact` 4/4，全部 `json.loads` 不報錯。

## 4. 已知的口徑衝突與範圍決定（請審查者判斷是否 Blocker）

1. **本改動覆蓋土星人 2026-10-30 的舊決議**（當時定「三站 JSON-LD 的 legalName 只准三種值，鼎曜＝`DingYao Advisory`」）。
   本次改成登記全名，依據是：①schema.org 對 `legalName` 的定義就是「官方登記名稱」；
   ②老闆 2026-11-10 明確指示補中文全名；③GSC 已出現實體不一致的症狀。已在 commit message 寫明覆蓋關係。
2. **EN 頁面也用中文法定全名**（`/about-en`、`/contact-en`、308 篇英文文章的 publisher）。
   理由：登記事實只有一份（比照既有做法：英文頁也寫中文登記地址）。若要改英文全名，會違反
   2026-10-29「英文法定全名只進法律當事人欄」的決議。
3. **同一個 `@id`（`https://dingyaoadvisory.tw/#organization`）在首頁兩個 block 的 `name` 不一致**：
   block 0 是 `DingYao Advisory`、block 4 是 `鼎曜國際顧問`。這是**改動前就存在**的狀況，
   依「不改動其他欄位」未處理。GBP 名稱是「鼎曜國際顧問有限公司 DingYao Advisory」，三種寫法並存。
4. **未補的節點（刻意）**：另有 406 個內嵌的 DingYao Organization 參照（`affiliation` 陣列成員、
   `WebSite`／`Blog` 節點）沒有 legalName。這些是參照用的精簡物件，不是實體主節點；
   `WebSite` 也不該有 legalName。依「範圍紀律」不擴散。
5. 站上**沒有 LocalBusiness 節點**（@type 實測：Organization 72、FinancialService 14、
   LegalService 17、BankOrCreditUnion 17、RealEstateListing 6，無 LocalBusiness）⇒ 派工第 3 條不適用。

---

## 5. EGM 審查處置（2 隻 goldfish：結構化資料正確性 A、品牌命名一致性 B）

### 5.1 結構化資料審查（A）

| # | Blocker | 處置 |
|---|---|---|
| A-B1 | 同一 `@id` 在一頁被兩個 block 以不同 `name` 宣告（實測 `DingYao Advisory` 320／`鼎曜國際顧問` 35／`鼎曜國際顧問 DingYao Advisory` 2） | **不修（超出派工範圍）**：派工第 2 條明文「name 維持不變（老闆已定案）」。**澄清審查者推論**：兩個 block 的 `legalName` 現在同值，不會因 `name` 衝突被丟。列 P1 提案（需老闆裁決是否把 `name` 統一為 GBP 字串「鼎曜國際顧問有限公司 DingYao Advisory」） |
| A-B2 | `/contact`、`/contact-en` 的 `mainEntity` Organization 無 `@id`（匿名節點，與主實體斷鏈） | **接受風險**：加 `@id` 會把第三種 `name` 併入主實體，需先裁決 name 口徑；且屬「改動其他欄位」。一行修法已寫進提案 |
| A-B3 | 8 篇 blog 的 `publisher` 無 `@id`、無 `logo`（Article 富媒體 publisher 要求） | **不修，列提案**：本次只被要求補 legalName；補 `@id`/`logo` 另案處理（影響 Article 增強呈現） |
| A-B4 | `legalName` 非 Google 實體對齊主訊號；`sameAs` 放的是 `maps/search?q=` 查詢 URL；`telephone` 全站 0 次 | **接受並列為 P0 提案**：這三項都是老闆定案／既有欄位，不屬「補 legalName」。真正的 GBP 對齊要靠 `name`／`telephone`／`address`／`sameAs`（真 `maps/place` 或 `cid` URL） |

### 5.2 品牌命名審查（B）

| # | Blocker | 處置 |
|---|---|---|
| B-B1 | 同一 `@id` 三種 `name` 並存，本次把三重身分「合法化」 | 同 A-B1（不修，列 P1 提案） |
| B-B2 | `terms.html` 對同一法人給兩個英文名（`鼎曜國際顧問有限公司（DingYao Advisory）` vs `本公司（DingYao International Advisory Ltd）`）；`privacy.html` 指認後者 | **不在本次範圍（法律文本）→ 列 P0 給天秤人**。匯款／KYC／南非合約會被引錯名，屬實質風險，但非 schema 可修 |
| B-B3 | 驗收只驗機制、沒驗原症狀；`/`、`/about`、`/contact` 可見文字「有限公司」仍 0 次 | **接受，已在回報明寫**。JSON-LD 是輔助訊號；Google 站名（Sitelinks／搜尋結果顯示）來源是 `WebSite.name`／`Organization.name`／`og:site_name`，這三個都依老闆指示未動。折衷可行方案（不動 name 欄位）：頁尾加登記全名＋統編，或把 `og:site_name` 加上全名 → 提案 |
| B-B4 | `legalName` 值沒有登記出處 | **不成立（已舉證）**：值來自老闆 2026-10-29 提供的經濟部商工登記資料（統一編號 60330590），且與 GBP 名稱逐字相同；站上 `privacy`／`terms`／`project-phase1` 的可見文字早已使用「鼎曜國際顧問有限公司」 |

建議處置：🟡1 repo 非 `dist` 舊值（`redesign/consultation-cta-mockup.html`、`runs/2026-11-07/*.orig.html`）確認**不會上線**（`assets.directory = ./dist`），已在回報註明；
🟡3 `WebSite.name` 兩套（`鼎曜國際顧問 DingYao Advisory` 201／`DingYao Advisory` 154）**正是 Google 站名來源** → P1 提案；
🟡5 `https://dingyaoadvisory.tw/scott.vcf`（live 200、孤兒檔，`ORG:DingYao International Advisory` 第五種寫法）→ P2 提案（下架或改名）；
🟡6 決議覆蓋紀錄 → **已完成**：Mnemosyne 舊口徑已 invalidate 並以新記憶取代、skill `dingyao-site-infrastructure` §6f 改為現行口徑、NAS 交件匣留檔。
