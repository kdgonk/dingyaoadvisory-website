#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4 booking_confirmed 真實觸發驗證。

不是「檔案裡有字串」就算過。Cal.com embed.js 的分發機制是：
    window.addEventListener("message", e => parseAction(e.data.fullType) → actionsManagers[ns][action])
所以我們用真實的 postMessage 模擬 Cal.com iframe 送出 bookingSuccessful，
讓頁面上真正註冊的 callback 被呼叫，再檢查 dataLayer 實際收到的 payload。

通過條件：
  - dataLayer 真的多出一筆 event=booking_confirmed
  - pillar / booking_source / booking_uid / funnel_l4 等欄位正確
  - 非 bookingSuccessful 的訊息不會誤觸發（防誤報）
"""
import json
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8899"
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
    results.append((bool(cond), name, str(detail)[:130]))


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        for f, pillar, lang in CASES:
            print(f"\n{'='*70}\n{f}  (pillar={pillar})\n{'='*70}")
            pg = b.new_page(viewport={"width": 1440, "height": 1000})
            pg.goto(f"{BASE}/{f}", wait_until="domcontentloaded", timeout=45000)

            # 等 Cal 初始化完成（callback 註冊在 ui 之後）
            try:
                pg.wait_for_function("typeof window.Cal === 'function' && !!window.Cal.ns", timeout=20000)
            except Exception:
                check("Cal 初始化", False, "timeout")
            pg.wait_for_timeout(6000)

            # 在頁面內掛攔截器，然後用 Cal 真正的 message 通道觸發
            out = pg.evaluate(
                """async () => {
                    window.dataLayer = window.dataLayer || [];
                    const cap = [];
                    const orig = window.dataLayer.push.bind(window.dataLayer);
                    window.dataLayer.push = function (o) { cap.push(o); return orig(o); };

                    // 先送一則無關訊息，確認不會誤觸發
                    window.postMessage({ fullType: "CAL:dingyao:__notABookingEvent", data: {} }, "*");
                    await new Promise(r => setTimeout(r, 400));
                    const afterNoise = cap.length;

                    // 用 Cal 真實通道模擬 bookingSuccessful
                    window.postMessage({
                        fullType: "CAL:dingyao:bookingSuccessful",
                        data: { uid: "test-uid-abc123", bookingId: 4242, title: "30 min consultation" }
                    }, "*");

                    // 等 callback 執行
                    for (let i = 0; i < 40 && cap.length === afterNoise; i++) {
                        await new Promise(r => setTimeout(r, 100));
                    }

                    const ev = cap.find(x => x && x.event === "booking_confirmed");
                    return { afterNoise: afterNoise, total: cap.length, ev: ev || null };
                }"""
            )

            check("無關訊息不會誤觸發 booking_confirmed", out["afterNoise"] == 0, f"noise 觸發 {out['afterNoise']} 筆")

            ev = out["ev"]
            check("bookingSuccessful 真的 push 出事件", ev is not None, f"cap={out['total']}")
            if ev:
                print("  dataLayer payload: " + json.dumps(ev, ensure_ascii=False))
                check("event 名稱正確", ev.get("event") == "booking_confirmed")
                check("event_category=funnel_l4", ev.get("event_category") == "funnel_l4")
                check(f"pillar={pillar}", ev.get("pillar") == pillar, ev.get("pillar"))
                check("booking_source=cal_inline", ev.get("booking_source") == "cal_inline")
                check("booking_uid 有取到", ev.get("booking_uid") == "test-uid-abc123", ev.get("booking_uid"))
                check("page_path 有值", bool(ev.get("page_path")), ev.get("page_path"))
                check("language 正確", ev.get("language") == lang, ev.get("language"))
                for k in ("utm_source", "utm_medium", "utm_campaign", "funnel_session_id"):
                    check(f"欄位 {k} 存在", k in ev, list(ev.keys())[:9])

            pg.close()
        b.close()
    return results


if __name__ == "__main__":
    run()
    passed = sum(1 for r in results if r[0])
    total = len(results)
    print(f"\n{'='*70}")
    if passed != total:
        print("未通過：")
        for ok, n, d in results:
            if not ok:
                print(f"  ✗ {n} :: {d}")
    print(f"{passed}/{total} 通過")
    print("=" * 70)
    sys.exit(0 if passed == total else 1)
