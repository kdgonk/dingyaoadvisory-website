# Deploy Log: 2026-07-27

## Article
- **Slug**: cape-town-semigration-2-0-maturing-market-2026
- **Title (ZH)**: Semigration 2.0：開普敦房市進入成熟期 — 三股新流向如何重塑南非房地產格局
- **Title (EN)**: Semigration 2.0: Cape Town's Property Market Enters a Mature Phase — Three New Currents Reshaping South African Real Estate
- **Hero Image**: https://assets.dingyaoadvisory.tw/blog/images/cape-town-semigration-2-0-maturing-market-2026-hero.webp (200 OK)

## Issues Found & Fixed
1. **ZH article had severe dual-structure corruption** — contained old Tailwind winter rental content embedded inside the new template, plus broken HTML (`</html<article>`). Rebuilt the entire ZH article from scratch using the correct semigration 2.0 content extracted from the old Tailwind section.
2. **EN article had HTML syntax errors** — extra `>` on hreflang and og:url meta tags. Fixed both.
3. **CSS brace balance**: Both articles verified clean (180/180 and 179/179).

## Files Deployed
- `dist/blog/cape-town-semigration-2-0-maturing-market-2026.html` (ZH)
- `dist/blog/cape-town-semigration-2-0-maturing-market-2026-en.html` (EN)
- `dist/blog.html` — card added at top
- `dist/blog-en.html` — card added at top
- `dist/sitemap.xml` — bilingual URL entries added
- `dist/llms.txt` — ZH + EN entries added
- `dist/webmcp.json` — articles added at top, last_updated updated

## Git
- Commit: `e3044ff`
- Push: origin main ✅

## GSC
- Sitemap submitted: ✅ (2026-07-27T03:05:11.932Z)

## Cloudflare Cache
- Auto-deploy triggered by git push; no manual purge needed

## Verification Pending
- Live URLs will be verified after Cloudflare Pages deploy (~60-90s)
