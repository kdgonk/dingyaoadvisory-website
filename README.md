# 鼎曜國際顧問官網

DingYao Advisory Official Website & Blog

## 架構

- **框架**: Astro 5.x
- **部署**: Cloudflare Pages
- **網域**: dingyaoadvisory.tw

## 結構

```
dingyaoadvisory-website/
├── src/
│   ├── content/
│   │   └── blog/          # 部落格文章 (Markdown)
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── pages/
│   │   ├── index.astro    # 首頁
│   │   ├── about.astro    # 關於我們
│   │   ├── services.astro # 服務項目
│   │   ├── contact.astro  # 聯絡我們
│   │   └── blog/
│   │       ├── index.astro    # 部落格列表
│   │       └── [...slug].astro # 文章頁面
│   └── components/
├── public/
│   └── images/           # 圖片資源
└── dist/                 # 建置輸出
```

## 開發

```bash
npm install
npm run dev     # 本地開發
npm run build   # 建置
npm run preview # 預覽建置結果
```

## 部署

推送到 `main` branch 後，GitHub Actions 自動部署到 Cloudflare Pages。

## 維運 Agent

由土星人團隊的網站維運 Agent 負責：
- 新增/更新文章
- 維護官網結構
- 管理 menu/footer 一致性
- 自動 git commit + push