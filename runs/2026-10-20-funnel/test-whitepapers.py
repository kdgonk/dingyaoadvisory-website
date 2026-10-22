#!/usr/bin/env python3
"""
白皮書下載頁端到端實測（真 Chromium）：
  - 頁面可渲染、零 JS 例外
  - 3 欄表單存在、驗證邏輯生效
  - 送出 → /api/whitepaper → 顯示真實 download_url
  - L3 lead_submit 有進 dataLayer
  - 手機 375px 無水平溢出
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
HTML = (HERE / "build" / "whitepapers.html").read_text(encoding="utf-8")
JS = (HERE / "dy-funnel.js").read_text(encoding="utf-8")

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS  " if cond else "FAIL  ") + name + (f"  :: {detail}" if detail else ""))


MOCK_OK = {
    "ok": True,
    "contact": {"id": 123},
    "pillar": "property",
    "asset_name": "whitepaper_property_2026",
    "download_url": "https://assets.dingyaoadvisory.tw/whitepapers/wp-property-2026-b84e1d06.pdf",
}


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        errors, console_errs, api_calls = [], [], []

        def on_api(route):
            body = json.loads(route.request.post_data) if route.request.post_data else {}
            api_calls.append(body)
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_OK))

        page.on("pageerror", lambda e: errors.append(str(e)))
        IGNORE = ("ERR_FAILED", "ERR_BLOCKED_BY_CLIENT", "ERR_ABORTED")
        page.on("console", lambda m: console_errs.append(m.text)
                if m.type == "error" and not any(x in m.text for x in IGNORE) else None)

        page.route("**/js/dy-funnel.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=JS))
        page.route("**/api/whitepaper", on_api)
        page.route("**/whitepapers**", lambda r: r.fulfill(status=200, content_type="text/html", body=HTML))
        # 外部資源不打真網路，避免拖慢/失敗
        page.route("**://fonts.googleapis.com/**", lambda r: r.abort())
        page.route("**://fonts.gstatic.com/**", lambda r: r.abort())
        page.route("**://cdnjs.cloudflare.com/**", lambda r: r.abort())
        page.route("**://plausible.dingyaoadvisory.tw/**", lambda r: r.abort())

        page.goto("http://dy.test/whitepapers?utm_source=line&utm_campaign=wp_launch&liff_id=1657-zzz")
        page.wait_for_timeout(500)

        # --- 基本渲染 ---
        check("頁面 title 正確", "白皮書" in page.title(), page.title())
        check("H1 存在", page.locator("h1").count() >= 1, page.locator("h1").first.inner_text()[:40])
        check("渲染後無 JS 例外", len(errors) == 0, errors[:2])
        check("無 console error", len(console_errs) == 0, console_errs[:2])

        # --- nav / footer ---
        check("nav 存在", page.locator("nav#navbar").count() == 1)
        check("footer 存在", page.locator("footer").count() == 1)
        check("nav 連結數與全站一致 (11)", page.locator("nav#navbar .nav-links a").count() == 11,
              page.locator("nav#navbar .nav-links a").count())

        # --- 4 張白皮書卡 ---
        check("4 份白皮書卡片", page.locator(".wp-card").count() == 4, page.locator(".wp-card").count())

        # --- 3 欄表單 ---
        check("表單有 3 個必填欄", page.locator("#wpName, #wpPhone, #wpPillar").count() == 3)
        check("pillar 選項 4 個", page.locator("#wpPillar option").count() == 5,  # 含「請選擇」
              page.locator("#wpPillar option").count())
        check("無 email 欄位（依老闆 3 欄定案）", page.locator('input[type="email"], #wpEmail').count() == 0)

        # --- L1 不該在 noindex 下載頁觸發（pillar=multi） ---
        l1 = page.evaluate("() => (window.dataLayer||[]).filter(e => e && e.event === 'view_service_page')")
        check("下載頁不送 L1（pillar=multi 非支柱頁）", len(l1) == 0, len(l1))

        # --- 空送出應被前端擋下 ---
        page.click("#wpSubmit")
        page.wait_for_timeout(200)
        check("空送出顯示錯誤", page.locator("#wpError").is_visible(), page.locator("#wpError").inner_text()[:40])
        check("空送出未呼叫 API", len(api_calls) == 0, len(api_calls))

        # --- 電話格式錯誤應被擋 ---
        page.fill("#wpName", "陳先生")
        page.fill("#wpPhone", "123")
        page.select_option("#wpPillar", "property")
        page.click("#wpSubmit")
        page.wait_for_timeout(200)
        check("電話太短被擋", "WhatsApp" in page.locator("#wpError").inner_text(), page.locator("#wpError").inner_text()[:40])
        check("電話錯誤時仍未呼叫 API", len(api_calls) == 0, len(api_calls))

        # --- 未勾同意應被擋 ---
        page.fill("#wpPhone", "+886 912 345 678")
        page.click("#wpSubmit")
        page.wait_for_timeout(200)
        check("未勾同意被擋", "隱私" in page.locator("#wpError").inner_text(), page.locator("#wpError").inner_text()[:40])
        check("未同意時仍未呼叫 API", len(api_calls) == 0, len(api_calls))

        # --- 正常送出 ---
        page.check("#wpConsent")
        page.click("#wpSubmit")
        page.wait_for_timeout(600)

        check("成功後呼叫 API 一次", len(api_calls) == 1, len(api_calls))
        if api_calls:
            a = api_calls[0]
            check("送出 name", a.get("name") == "陳先生", a.get("name"))
            check("送出 phone", a.get("phone") == "+886 912 345 678", a.get("phone"))
            check("送出 pillar", a.get("pillar") == "property", a.get("pillar"))
            check("送出 asset_name", a.get("asset_name") == "whitepaper_property_2026", a.get("asset_name"))
            check("送出 utm_source（LIFF/UTM 預埋生效）", a.get("utm", {}).get("utm_source") == "line", a.get("utm"))
            check("送出 liff_id 佔位", a.get("utm", {}).get("liff_id") == "1657-zzz", a.get("utm"))

        check("成功後表單隱藏", not page.locator("#wpForm").is_visible())
        check("成功區塊顯示", page.locator("#wpSuccess").is_visible())
        href = page.get_attribute("#wpDownload", "href")
        check("下載連結 = API 回的 download_url", href == MOCK_OK["download_url"], href)

        # --- L3 事件 ---
        l3 = page.evaluate("() => (window.dataLayer||[]).filter(e => e && e.event === 'lead_submit')")
        check("L3 lead_submit 有送出", len(l3) == 1, len(l3))
        if l3:
            check("L3 asset_name", l3[0].get("asset_name") == "whitepaper_property_2026", l3[0].get("asset_name"))
            check("L3 lead_type=whitepaper", l3[0].get("lead_type") == "whitepaper", l3[0].get("lead_type"))
            check("L3 pillar = 表單選的 property（非頁面 multi）", l3[0].get("pillar") == "property", l3[0].get("pillar"))

        # --- HTML 原始碼不得含 PDF 路徑 ---
        check("HTML 原始碼不含 .pdf 路徑", ".pdf" not in HTML, ".pdf" in HTML)

        # --- RWD 375px 無水平溢出 ---
        page2 = ctx.new_page()
        page2.set_viewport_size({"width": 375, "height": 812})
        page2.route("**/js/dy-funnel.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=JS))
        page2.route("**/api/whitepaper", on_api)
        page2.route("**/whitepapers**", lambda r: r.fulfill(status=200, content_type="text/html", body=HTML))
        page2.route("**://fonts.googleapis.com/**", lambda r: r.abort())
        page2.route("**://fonts.gstatic.com/**", lambda r: r.abort())
        page2.route("**://cdnjs.cloudflare.com/**", lambda r: r.abort())
        page2.route("**://plausible.dingyaoadvisory.tw/**", lambda r: r.abort())
        page2.goto("http://dy.test/whitepapers")
        page2.wait_for_timeout(400)
        overflow = page2.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check("375px 無水平溢出", overflow <= 1, f"overflow={overflow}px")

        browser.close()

    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    print(f"\n===== {passed}/{total} passed =====")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run())
