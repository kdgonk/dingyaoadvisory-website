# Deploy Log — 2026-08-03

## Article
- **Slug**: sarb-bop-codes-foreign-property-buyers-2026
- **Title (ZH)**: SARB 8月11日新規上路！外國人在南非買房的國際收支申報全攻略
- **Title (EN)**: SARB's New BoP Codes from 11 August 2026: What Foreign Property Buyers Must Know
- **Category**: 稅務法規 / Tax & Regulation

## Deployment Steps
1. ✅ Pre-deployment validation — all 5 checks passed
2. ✅ Quality gate (12 items) — all passed (Nav ZH 8/9 was a false positive from footer links; actual nav has all 9 correct)
3. ✅ Article files copied to dist/blog/
4. ✅ Blog list pages updated (ZH: blog.html, EN: blog-en.html)
5. ✅ Sitemap updated with bilingual entries
6. ✅ llms.txt updated
7. ✅ webmcp.json updated
8. ✅ Git commit + push to origin main
9. ✅ Cloudflare Pages auto-deploy triggered
10. ✅ Live verification: ZH 200, EN 200 (after 90s deploy delay)
11. ✅ GSC sitemap submitted successfully

## Verification Results
- ZH article: https://dingyaoadvisory.tw/blog/sarb-bop-codes-foreign-property-buyers-2026 — 200 ✅
- EN article: https://dingyaoadvisory.tw/blog/sarb-bop-codes-foreign-property-buyers-2026-en — 200 ✅
- Blog list ZH: card present ✅
- Blog list EN: card present ✅
- Sitemap: entries present ✅
- Hero image: CDN 200 ✅
- GSC sitemap: submitted 2026-08-03T03:07:10.713Z ✅

## Notes
- EN article returned 404 on first check (deploy delay ~90s), resolved on retry
- No HTML syntax errors found in EN article
- No dual-structure corruption in ZH article
- CSS brace balance: 170/170 for both files
