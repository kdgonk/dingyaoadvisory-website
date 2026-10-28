# _drafts/ — 未部署草稿隔離區

**用途**：放「已寫完但還沒上線」的頁面，避免 `dist/` 裡出現 live 404 的檔案。

## 為什麼存在（2026-10-28）

2026-10-27 曾把 `dist/blog/cape-town-property-valuation-rates-foreign-buyers-2026.html`
（ZH 草稿，尚未部署）留在 `dist/blog/`：

1. `scripts/update_sitemap.py` 只認「檔案存在」→ 把它寫進 sitemap（328 筆）並送 IndexNow
   → Google 收到一個 live 404。
2. 任何 agent 跑 `git add -A` 都會把該檔一起 push 上線（Worker assets = `./dist`）。

## 規則

- **草稿 → `_drafts/`，不要放 `dist/`。** Worker 只服務 `./dist`，`_drafts/` 不會被部署。
- `_drafts/` 已列入 `.gitignore`，不會被 `git add -A` 帶進 commit。
- 上線流程：圖文齊備 → `mv _drafts/blog/<slug>.html dist/blog/` → 部署 → 跑
  `python3 scripts/update_sitemap.py`（現在會做 live 200 過濾）→ GSC 提交。

## 目前內容

| 檔案 | 狀態 | 待辦 |
|---|---|---|
| `blog/cape-town-property-valuation-rates-foreign-buyers-2026.html` | ZH 草稿，未部署（live 404） | 木星人補 hero 圖 → 泰坦人部署 |
| `blog/cape-town-property-valuation-rates-foreign-buyers-2026-en.html` | EN 草稿，未部署（live 404，2026-10-28 14:06 由火星人寫出，同日移入） | 同上；兩版一起部署 |

**圖檔狀態（2026-10-28 14:20 實測）**：hero／s1~s6 共 7 張 webp 在
`https://assets.dingyaoadvisory.tw/blog/images/cape-town-property-valuation-rates-foreign-buyers-2026-*.webp`
**7/7 全部 404（木星人尚未上傳）** → 現在部署會是破圖，維持隔離。

**S-20261028-VALU 排程（土星人 2026-10-28 裁決）**
- 日期已統一：ZH／EN 兩檔 `datePublished`＋`dateModified` 全部 = **2026-10-31**（4 欄位已驗）。
- 部署時點：`0 11 * * 1,3,6` 發布 cron 的 **2026-10-31（六）11:00** 班；該 job 的 prompt 已內建
  「S-20261028-VALU」專屬區塊（硬性日期閘門 → `deploy_article_pair.py` → 恢復 fx-tracker 內連 → 驗證）。
- 🔴 **禁止提前**：即使 7 張圖提早到齊，也**不得**在 10-28／29／30 部署。`datePublished` 已鎖 2026-10-31，
  提前 live 會變「未來日期」，Google 會 clamp 到發現日、news sitemap 48h 窗口對不上。圖先到就放著。
- 硬性閘門：`python3 scripts/check_assets_ready.py <draft> --expect=7`（或 `deploy_article_pair.py` 內建的預檢），
  **7 張圖全 200 才准 push**；任一 404 就停手回報（上線破圖比延後一天更糟）。
- 部署用 `python3 scripts/deploy_article_pair.py --slug <slug> --publish-date 2026-10-31`（一條指令跑完
  gate → 日期 → 卡片 → sitemap → news → purge → live 驗證；exit 2 = 圖未就緒且什麼都沒動）。
- 上線後用 `python3 scripts/restore_commented_block.py ... --marker "2026-10-28 titan"` 還原
  `fx-tracker` ZH/EN 被註解的相關閱讀連結（已驗：還原後與註解前 byte-identical）。
