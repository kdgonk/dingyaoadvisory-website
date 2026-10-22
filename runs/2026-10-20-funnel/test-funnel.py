#!/usr/bin/env python3
"""
四層漏斗 dataLayer 實測 — 用真 Chromium 跑，不是靜態檢查。
驗證 L1→L2→L3→L4 實際 push 的 payload 內容與去重邏輯。
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
JS = (HERE / "test-js" / "dy-funnel.js").read_text(encoding="utf-8")

# CTA 用 javascript:void(0) 是為了測試腳本能連點多個而不導航；
# 最後一個 fallback_cta 保留真 href，用來測「真導航前事件仍已 push」。
SERVICE_PAGE = """<!DOCTYPE html><html lang="zh-TW"><head><meta charset="utf-8">
<title>南非置產</title></head>
<body data-pillar="property">
<h1>南非置產</h1>
<a href="javascript:void(0)" data-cta-id="hero_primary" data-cta-location="hero">預約免費評估</a>
<a href="javascript:void(0)" data-cta-id="bottom_cta" data-cta-location="bottom_cta">立即諮詢</a>
<a href="/consultation" id="fallbackCta">未標記 CTA</a>
<div id="lmSuccess" style="display:none">已送出</div>
<script src="/js/dy-funnel.js"></script>
</body></html>"""

BOOKING_PAGE = """<!DOCTYPE html><html lang="zh-TW"><head><meta charset="utf-8">
<title>預約完成</title></head><body>
<h1>預約已成立</h1>
<script src="/js/dy-funnel.js"></script>
</body></html>"""

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), str(detail)))
    print(("PASS  " if cond else "FAIL  ") + name + ("  :: " + str(detail) if detail else ""))


def events(page):
    raw = page.evaluate(
        "() => (window.dataLayer||[]).map(function(x){ try {return JSON.parse(JSON.stringify(x));} catch(e){return null;} })"
    )
    return [d for d in raw if isinstance(d, dict) and d.get("event")]


def wire(ctx, errors):
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("**/js/dy-funnel.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=JS))
    page.route("**/south-africa-property**", lambda r: r.fulfill(status=200, content_type="text/html", body=SERVICE_PAGE))
    page.route("**/booking-confirmed**", lambda r: r.fulfill(status=200, content_type="text/html", body=BOOKING_PAGE))
    page.route("**/about**", lambda r: r.fulfill(status=200, content_type="text/html",
                                                 body="<html><body><h1>About</h1><script src='/js/dy-funnel.js'></script></body></html>"))
    return page


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        errors = []
        page = wire(ctx, errors)

        # ---------- L1 ----------
        page.goto("http://dy.test/south-africa-property?utm_source=line&utm_medium=oa&utm_campaign=2026q4_property&liff_id=1657000000-abcdefg")
        page.wait_for_timeout(300)
        l1 = [e for e in events(page) if e["event"] == "view_service_page"]
        check("L1 view_service_page 有送出", len(l1) == 1, f"count={len(l1)}")
        if l1:
            check("L1 pillar=property", l1[0].get("pillar") == "property", l1[0].get("pillar"))
            check("L1 帶 utm_source=line", l1[0].get("utm_source") == "line", l1[0].get("utm_source"))
            check("L1 帶 utm_campaign", l1[0].get("utm_campaign") == "2026q4_property", l1[0].get("utm_campaign"))
            check("L1 帶 liff_id 佔位", l1[0].get("liff_id") == "1657000000-abcdefg", l1[0].get("liff_id"))
            check("L1 有 dy_session_id", str(l1[0].get("dy_session_id", "")).startswith("s_"), l1[0].get("dy_session_id"))
            check("L1 標 event_category=funnel_l1", l1[0].get("event_category") == "funnel_l1", l1[0].get("event_category"))

        # ---------- L1 去重 ----------
        page.reload()
        page.wait_for_timeout(300)
        l1b = [e for e in events(page) if e["event"] == "view_service_page"]
        check("L1 同 session 去重（重載不再送）", len(l1b) == 0, f"count={len(l1b)}")

        # ---------- L2 ----------
        page.click('[data-cta-id="hero_primary"]')
        page.wait_for_timeout(150)
        l2 = [e for e in events(page) if e["event"] == "cta_click"]
        check("L2 cta_click 有送出", len(l2) == 1, f"count={len(l2)}")
        if l2:
            check("L2 cta_id=hero_primary", l2[0].get("cta_id") == "hero_primary", l2[0].get("cta_id"))
            check("L2 cta_location=hero", l2[0].get("cta_location") == "hero", l2[0].get("cta_location"))
            check("L2 pillar=property", l2[0].get("pillar") == "property", l2[0].get("pillar"))
            check("L2 帶 utm_source（跨頁保存成功）", l2[0].get("utm_source") == "line", l2[0].get("utm_source"))

        page.click('[data-cta-id="bottom_cta"]')
        page.wait_for_timeout(150)
        ids = [e.get("cta_id") for e in events(page) if e["event"] == "cta_click"]
        check("L2 兩個 CTA 可區分", ids == ["hero_primary", "bottom_cta"], ids)

        # ---------- L2 fallback（未標記 data-cta-id 仍要能追） ----------
        page.evaluate("() => { document.getElementById('fallbackCta').addEventListener('click', function(e){ e.preventDefault(); }); }")
        page.click("#fallbackCta")
        page.wait_for_timeout(150)
        auto = [e for e in events(page) if e["event"] == "cta_click" and str(e.get("cta_id", "")).startswith("auto_")]
        check("L2 未標記 CTA 走 fallback 選擇器", len(auto) == 1, auto[0].get("cta_id") if auto else "none")

        # ---------- L3 ----------
        page.evaluate("() => window.dyFunnel.lead({lead_type:'whitepaper', asset_name:'whitepaper_property_2026', form_id:'wpForm'})")
        page.wait_for_timeout(150)
        l3 = [e for e in events(page) if e["event"] == "lead_submit"]
        check("L3 lead_submit 有送出", len(l3) == 1, f"count={len(l3)}")
        if l3:
            check("L3 asset_name 正確", l3[0].get("asset_name") == "whitepaper_property_2026", l3[0].get("asset_name"))
            check("L3 pillar 繼承", l3[0].get("pillar") == "property", l3[0].get("pillar"))
            check("L3 保留 utm_source", l3[0].get("utm_source") == "line", l3[0].get("utm_source"))

        # ---------- L4（L3 之後導向確認頁，pillar/asset 要繼承） ----------
        page.goto("http://dy.test/booking-confirmed?booking=1&ref=BK-2026-0042&slot=2026-10-28T14:00")
        page.wait_for_timeout(300)
        l4 = [e for e in events(page) if e["event"] == "booking_confirmed"]
        check("L4 booking_confirmed 有送出", len(l4) == 1, f"count={len(l4)}")
        if l4:
            check("L4 booking_ref 正確", l4[0].get("booking_ref") == "BK-2026-0042", l4[0].get("booking_ref"))
            check("L4 pillar 由 L3 繼承=property", l4[0].get("pillar") == "property", l4[0].get("pillar"))
            check("L4 origin_asset 繼承", l4[0].get("origin_asset") == "whitepaper_property_2026", l4[0].get("origin_asset"))

        # ---------- L4 防誤判 ----------
        page2 = wire(ctx, errors)
        page2.goto("http://dy.test/booking-confirmed")
        page2.wait_for_timeout(250)
        check("L4 無 booking=1 不送（防誤判）",
              len([e for e in events(page2) if e["event"] == "booking_confirmed"]) == 0)

        # ---------- 非支柱頁不送 L1 ----------
        page3 = wire(ctx, errors)
        page3.goto("http://dy.test/about")
        page3.wait_for_timeout(200)
        check("非支柱頁不送 L1", len([e for e in events(page3) if e["event"] == "view_service_page"]) == 0)

        # ---------- consent 前置存在時不報錯（模擬站上既有 consent script） ----------
        page4 = ctx.new_page()
        page4.on("pageerror", lambda e: errors.append(str(e)))
        page4.route("**/js/dy-funnel.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=JS))
        page4.route("**/education**", lambda r: r.fulfill(status=200, content_type="text/html", body="""<html><head><script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{ad_storage:'denied',analytics_storage:'denied'});
</script></head><body data-pillar="education"><h1>教育</h1>
<script src="/js/dy-funnel.js"></script></body></html>"""))
        page4.goto("http://dy.test/education")
        page4.wait_for_timeout(250)
        edu = [e for e in events(page4) if e["event"] == "view_service_page"]
        check("education 頁 L1 pillar=education", len(edu) == 1 and edu[0].get("pillar") == "education",
              edu[0].get("pillar") if edu else "none")

        check("全程無 JS 例外", len(errors) == 0, errors[:3])

        browser.close()

    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n===== {passed}/{total} passed =====")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run())
