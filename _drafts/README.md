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
| `blog/cape-town-property-valuation-rates-foreign-buyers-2026.html` | ZH 草稿，未部署（live 404） | 木星人補 hero 圖 → 泰坦人部署；EN 版尚未產生 |
