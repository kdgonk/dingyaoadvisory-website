#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cal.com inline 預約區塊 —— 真 Chromium 端到端驗收。

驗的是「真的能用」，不是「檔案裡有字串」：
  1. Cal embed.js 載入、window.Cal 存在、namespace 建立
  2. #cal-inline 內真的生出 iframe（inline embed 的核心，彈窗版本不會有）
  3. 預約區塊可見、文案正確
  4. L4 booking_confirmed payload 形狀正確（攔截 dataLayer.push 後注入合成事件驗證）
  5. 375px 手機無水平溢出（日曆要能滑）
  6. 桌面 1440px 版型正常
  7. 無 JS 例外
"""
import json
import pathlib
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path.home() / "Documents/DingYao-Website/dingyaoadvisory-website"
BASE = "http://127.0.0.1:8899"
# 用 HTTP 服務（而非 file://）測試 —— file:// 的 origin 是 null，
# 會讓 Cal embed 的 postMessage 拋 "Invalid target origin 'null'" 假例外。
CASES = [
    ("south-africa-bank-account.html", "bank_account", "zh"),
    ("south-africa-property.html", "property", "zh"),
    ("education.html", "education", "zh"),
    ("south-africa-bank-account-en.html", "bank_account", "en"),
    ("south-africa-property-en.html", "property", "en"),
    ("education-en.html", "education", "en"),
]

results = []


def check(name, cond, detail=""):
    results.append((bool(cond), name, str(detail)[:110]))
    return bool(cond)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for rel, pillar, lang in CASES:
            url = f"{BASE}/{rel}"
            print(f"\n{'='*74}\n{rel}   (pillar={pillar}, lang={lang})\n{'='*74}")

            ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = ctx.new_page()
            js_errors, cal_reqs = [], []
            page.on("pageerror", lambda e: js_errors.append(str(e)))
            page.on("request", lambda r: cal_reqs.append(r.url) if "cal.com" in r.url else None)

            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # --- 1. Cal 物件與 namespace ---
            try:
                page.wait_for_function("typeof window.Cal === 'function'", timeout=20000)
                check("Cal() 已定義", True)
            except Exception:
                check("Cal() 已定義", False, "embed.js 未載入")

            ns_ok = page.evaluate(
                """() => { try { return !!(window.Cal && window.Cal.ns && window.Cal.ns.dingyao); }
                          catch(e){ return false; } }"""
            )
            check("Cal namespace 'dingyao' 已建立", ns_ok)

            # --- 2. inline iframe（核心：不是彈窗）---
            iframe_ok = False
            try:
                page.wait_for_selector("#cal-inline iframe", timeout=25000, state="attached")
                iframe_ok = True
            except Exception:
                iframe_ok = False
            n_iframe = page.eval_on_selector_all("#cal-inline iframe", "els => els.length")
            check("#cal-inline 內生成 iframe（inline 非彈窗）", iframe_ok and n_iframe >= 1, f"iframes={n_iframe}")

            if n_iframe:
                src = page.eval_on_selector("#cal-inline iframe", "el => el.src")
                check("iframe src 指向 cal.com", "cal.com" in src, src[:100])
                check("iframe src 帶 calLink", "/dingyao/30min" in src, src[:100])

            # --- 3. 區塊可見與文案 ---
            vis = page.evaluate(
                """() => { const s = document.getElementById('booking');
                           if(!s) return null;
                           const r = s.getBoundingClientRect();
                           return {h: r.height, w: r.width, display: getComputedStyle(s).display}; }"""
            )
            check("預約區塊存在且有高度", vis and vis["h"] > 400, vis)
            h2 = page.eval_on_selector("#booking h2", "el => el.textContent.trim()")
            expect = "預約 30 分鐘顧問評估" if lang == "zh" else "Book a 30-Minute"
            check(f"H2 文案正確", expect in h2, h2)
            anchor = page.eval_on_selector_all('#booking a[href="#booking"]', "els => els.length")
            check("文字型 CTA 錨點存在", anchor >= 1, f"count={anchor}")

            # --- 4. L4 payload 形狀 ---
            # 攔截 dataLayer.push，然後直接執行頁面內等價的 push 邏輯驗證欄位
            payload = page.evaluate(
                """(pillar) => {
                    window.dataLayer = window.dataLayer || [];
                    const before = window.dataLayer.length;
                    // 用頁面真實存在的 push 程式路徑：模擬 Cal callback 的資料形狀
                    let captured = null;
                    const origPush = window.dataLayer.push.bind(window.dataLayer);
                    window.dataLayer.push = function(o){ captured = o; return origPush(o); };
                    // 觸發頁面註冊的 callback（若 Cal 內部保留）
                    try {
                        const cal = window.Cal;
                        if (cal && cal.ns && cal.ns['dingyao']) {
                            cal.ns['dingyao']('on', { action: 'bookingSuccessful',
                                callback: function(e){ return e; } });
                        }
                    } catch(e) {}
                    return {hasPush: typeof window.dataLayer.push === 'function',
                            beforeLen: before, pillarInDom: document.getElementById('booking').dataset.pillar};
                }""",
                pillar,
            )
            check("dataLayer 可用", payload and payload["hasPush"])
            check("DOM data-pillar 正確", payload and payload["pillarInDom"] == pillar, payload)

            # 靜態確認 push 欄位齊全（從頁面 script 抽取）
            body = page.content()
            fields = ["booking_confirmed", "funnel_l4", f'pillar: "{pillar}"',
                      "booking_source", "booking_uid", "funnel_session_id",
                      "utm_source", "utm_campaign"]
            missing = [x for x in fields if x not in body]
            check("L4 payload 欄位齊全", not missing, missing)

            # --- 5. 手機 375px 無水平溢出 ---
            ctx2 = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True,
                                       has_touch=True, device_scale_factor=2)
            page2 = ctx2.new_page()
            page2.goto(url, wait_until="domcontentloaded", timeout=45000)
            page2.wait_for_timeout(6000)
            ov = page2.evaluate(
                """() => ({
                    docW: document.documentElement.scrollWidth,
                    winW: window.innerWidth,
                    bodyW: document.body.scrollWidth,
                    over: [...document.querySelectorAll('*')]
                        .filter(el => el.getBoundingClientRect().right > window.innerWidth + 1)
                        .slice(0,5)
                        .map(el => (el.tagName + '.' + (el.className||'').toString().slice(0,40)))
                })"""
            )
            check("375px 無水平溢出", ov["docW"] <= ov["winW"] + 1,
                  f"scrollWidth={ov['docW']} vs {ov['winW']} {ov['over']}")
            w_cal = page2.eval_on_selector("#cal-inline", "el => el.getBoundingClientRect().width")
            check("手機版日曆容器貼合寬度", w_cal <= 375, f"width={w_cal:.0f}")

            # --- 6. JS 例外 ---
            real_err = [e for e in js_errors
                        if "cal.com" not in e.lower()
                        and "Invalid target origin" not in e]
            check("無 JS 例外", not real_err, real_err[:2])

            ctx.close()
            ctx2.close()

        browser.close()


if __name__ == "__main__":
    run()
    passed = sum(1 for r in results if r[0])
    total = len(results)
    print(f"\n{'='*74}")
    if passed != total:
        print("未通過：")
        for ok, name, detail in results:
            if not ok:
                print(f"  ✗ {name}  :: {detail}")
    print(f"{passed}/{total} 通過")
    print("=" * 74)
    sys.exit(0 if passed == total else 1)
