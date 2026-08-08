# Deploy Log — 2026-08-07

## Article
- **Slug**: `foreign-buyers-atlantic-seaboard-1-3-cape-town-r6bn-2026`
- **ZH Title**: 開普敦 Atlantic Seaboard 1/3 被外國人買走：R60 億成交背後的高端置產密碼
- **EN Title**: Foreign Buyers Now Control One-Third of Cape Town's Atlantic Seaboard: Inside the R6bn Deeds Data
- **Category**: 置產投資 / Property Investment

## URLs
- ZH: https://dingyaoadvisory.tw/blog/foreign-buyers-atlantic-seaboard-1-3-cape-town-r6bn-2026 (200)
- EN: https://dingyaoadvisory.tw/blog/foreign-buyers-atlantic-seaboard-1-3-cape-town-r6bn-2026-en (200)

## Quality Gate
- Gate 1 (Mars 10-item self-check): ✅ PASS
- Gate 2 (Jupiterian images): ✅ hero + s1-s6 all 200 on CDN
- Gate 3 (Titan pre-deploy 12-item): ✅ PASS
  - No Tailwind remnants, no broken HTML, CSS braces balanced (174/174)
  - Hero slug matches, og:image is .webp
  - Nav ZH 9 links, EN 9 links correct
  - Footer 6 social icons
  - JSON-LD publisher correct (ZH: 鼎曜國際顧問 / EN: DingYao Advisory)
  - No commit hash residue
  - No duplicate cards introduced (pre-existing dups in HEAD unchanged)

## Deployment
- Copied ZH + EN HTML to `dist/blog/`
- Updated `dist/blog.html` + `dist/blog-en.html` (new card at top)
- Regenerated `dist/sitemap.xml` via `gen_sitemap.py` → 222 URLs, submitted to GSC (0 errors)
- Updated `dist/llms.txt` (Last updated: 2026-08-07)
- Updated `dist/webmcp.json` (72 articles, last_updated 2026-08-07)
- Git commit `a0ec4b9` → pushed to origin/main
- Cloudflare Pages auto-deploy confirmed (ZH/EN both 200 after ~135s)

## GSC
- Sitemap submitted via `sc-domain:dingyaoadvisory.tw` format
- Status: 0 errors, 0 warnings
- Submitted: 2026-08-07T03:01:18.657Z

## Notes
- Also committed pending semigration section-bg refactor (2 files) from prior session
- Removed stale `.bak-20260807-0614/` backup directory from staging
