# Deploy Log: 2026-07-21

## Article
- **Slug**: foreign-buyers-r153bn-cape-town-luxury-10-years
- **Title (ZH)**: 外國買家十年砸 R1,530 億搶進開普敦豪宅：Lightstone 數據揭示的投資趨勢與機會
- **Title (EN)**: Foreign Buyers Spent R153 Billion on Cape Town Luxury Homes in 10 Years: Lightstone Data Reveals Investment Trends
- **Category**: 置產投資 / Property Investment
- **Author**: Scott Huang

## Deployment Steps
1. ✅ Article files copied to production repo
2. ✅ Hero image verified on CDN (HTTP 200)
3. ✅ Blog list pages updated (ZH: blog.html, EN: blog-en.html)
4. ✅ Sitemap updated with bilingual entries
5. ✅ llms.txt updated
6. ✅ webmcp.json updated
7. ✅ Git commit + push to origin main
8. ✅ Live URLs verified (ZH: 200, EN: 200)
9. ✅ GSC sitemap submitted (errors=0)
10. ✅ Cloudflare cache: auto-deploy handles invalidation

## Verification
- ZH live: https://dingyaoadvisory.tw/blog/foreign-buyers-r153bn-cape-town-luxury-10-years → 200
- EN live: https://dingyaoadvisory.tw/blog/foreign-buyers-r153bn-cape-town-luxury-10-years-en → 200
- Hero image: https://assets.dingyaoadvisory.tw/blog/images/foreign-buyers-r153bn-cape-town-luxury-10-years-hero.webp → 200
- Sitemap submitted: 2026-07-21T03:04:37Z, errors=0

## Notes
- webmcp.json was corrupted by patch() — had to rewrite entire file
- GSC uses service account auth (not OAuth token)
- Cloudflare cache purge not needed (auto-deploy handles it)
