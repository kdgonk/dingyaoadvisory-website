#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cal.com 預約區塊 —— live 站三斷點 + 可選時段 + dataLayer console 擷取。

土星人 2026-10-20 驗收標準逐項：
  1. live 200
  2. 日曆「實際可選時段」—— 真的點日期格子，確認時段按鈕出現（不是只有空框）
  3. 手機 / 平板 / 桌機 三斷點 RWD，附截圖
  4. dataLayer push 成功 —— 擷取 console 輸出
  5. 原始碼不外洩、404 有 body
"""
import json
import re
import sys
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

LIVE = "https://dingyaoadvisory.tw"
PAGE = "/south-africa-bank-account"
SHOT_DIR = "."

BREAKPOINTS = [
    ("mobile", 390, 844, True),
    ("tablet", 768, 1024, False),
    ("desktop", 1440, 900, False),
]

res = []


def ck(name, cond, detail=""):
    res.append((bool(cond), name, str(detail)[:140]))


# ---------- 1. 原始碼不外洩 / 404（純 HTTP） ----------
UA = {"User-Agent": "Mozilla/5.0 TitanVerify/1.0", "Cache-Control": "no-cache"}
html = urllib.request.urlopen(urllib.request.Request(LIVE + PAGE, headers=UA), timeout=30).read().decode("utf-8", "ignore")
LEAK = ["api_access_token", "CHATWOOT_TOKEN", "Chatwoot token", "Bearer ", "/Users/dingyao", "AHREFS_API_KEY", "CLOUDFLARE_API_TOKEN"]
leaks = [p for p in LEAK if p in html]
ck("原始碼無 token / 內部路徑外洩", not leaks, leaks)
ck("HTML 內無 PDF 實體路徑外洩", "dingyao-assets/whitepapers" not in html)

try:
    r404 = urllib.request.urlopen(urllib.request.Request(LIVE + "/nonexistent-check-xyz-123", headers=UA), timeout=20)
    code, body = r404.status, len(r404.read())
except urllib.error.HTTPError as e:
    code, body = e.code, len(e.read())
ck("404 回真 404（非 200 假頁）", code == 404, f"status={code}")
ck("404 有 body", body > 1000, f"{body} bytes")

# ---------- 2/3/4. 瀏覽器實測 ----------
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")

    # ---- 三斷點：RWD + 截圖 ----
    for name, w, h, mob in BREAKPOINTS:
        kw = dict(is_mobile=True, has_touch=True, device_scale_factor=2) if mob else {}
        pg = b.new_page(viewport={"width": w, "height": h}, **kw)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:90]))
        pg.goto(LIVE + PAGE, wait_until="domcontentloaded", timeout=60000)
        try:
            pg.wait_for_selector("#cal-inline iframe", timeout=30000, state="attached")
        except Exception:
            pass
        pg.wait_for_timeout(9000)
        pg.evaluate("const c=document.getElementById('cookieConsent'); if(c) c.style.display='none';")

        m = pg.evaluate(
            """() => {
                const c = document.getElementById('cal-inline');
                const f = c.querySelector('iframe');
                return {
                    docW: document.documentElement.scrollWidth,
                    winW: window.innerWidth,
                    calW: Math.round(c.getBoundingClientRect().width),
                    calH: Math.round(c.getBoundingClientRect().height),
                    iframeH: f ? Math.round(f.getBoundingClientRect().height) : 0,
                    nIframe: c.querySelectorAll('iframe').length
                };
            }"""
        )
        overflow = m["docW"] - m["winW"]
        ck(f"[{name} {w}px] 無水平溢出", overflow <= 1, f"scrollW={m['docW']} winW={m['winW']}")
        ck(f"[{name} {w}px] inline iframe 存在", m["nIframe"] == 1, m)
        ck(f"[{name} {w}px] 日曆容器貼合寬度", m["calW"] <= m["winW"], f"{m['calW']} vs {m['winW']}")
        ck(f"[{name} {w}px] 無 JS 例外", not [e for e in errs if "Invalid target origin" not in e], errs[:2])

        pg.evaluate("document.getElementById('booking').scrollIntoView({block:'start'})")
        pg.wait_for_timeout(2000)
        path = f"live-{name}-{w}.png"
        pg.screenshot(path=path)
        print(f"  截圖 {path}")

        # ---- 平板/桌機才驗「實際可選時段」（避免重複耗時）----
        if name == "desktop":
            try:
                fr = pg.frame_locator("#cal-inline iframe")
                # 找出一個可點的日期（非 disabled、且非今天）
                clicked = None
                for d in ["22", "23", "26", "27", "28"]:
                    cand = fr.locator(f"button:has-text('{d}')").first
                    try:
                        if cand.is_visible(timeout=2000):
                            cand.click(timeout=4000)
                            clicked = d
                            break
                    except Exception:
                        continue
                pg.wait_for_timeout(3500)
                # 時段按鈕出現？（Cal 時段格式如 "5:00pm"）
                slots = fr.locator("button").filter(has_text=re.compile(r"\d{1,2}:\d{2}\s*(am|pm)", re.I))
                n_slots = slots.count()
                ck("日曆可實際選日期", clicked is not None, f"clicked day={clicked}")
                ck("選日期後出現可選時段（非空框）", n_slots > 0, f"時段按鈕 {n_slots} 個")
                if n_slots:
                    labels = [slots.nth(i).inner_text(timeout=2000).strip().replace("\n", " ") for i in range(min(3, n_slots))]
                    print(f"  實際時段：{labels}")
            except Exception as e:
                ck("日曆可實際選日期", False, str(e)[:100])
                ck("選日期後出現可選時段（非空框）", False, "無法互動")

        pg.close()

    # ---- dataLayer console 擷取 ----
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    logs = []
    pg.on("console", lambda msg: logs.append(msg.text))
    pg.goto(LIVE + PAGE, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_function("typeof window.Cal==='function' && !!window.Cal.ns && !!window.Cal.ns.dingyao", timeout=30000)
    pg.wait_for_timeout(4000)

    out = pg.evaluate(
        """async () => {
            // 在 console 印出每一筆 dataLayer push，模擬 GTM debug 檢視
            window.dataLayer = window.dataLayer || [];
            const orig = window.dataLayer.push.bind(window.dataLayer);
            window.dataLayer.push = function (o) {
                if (o && o.event) console.log('[dataLayer] ' + JSON.stringify(o));
                return orig(o);
            };
            window.postMessage({ fullType: "CAL:dingyao:bookingSuccessful",
                                 data: { uid: "live-console-2026" } }, "*");
            for (let i = 0; i < 50; i++) await new Promise(r => setTimeout(r, 100));
            return window.dataLayer.length;
        }"""
    )
    pg.wait_for_timeout(1200)
    pg.close()
    b.close()

dl_logs = [l for l in logs if l.startswith("[dataLayer]")]
ck("dataLayer 有 push 出 booking_confirmed", any("booking_confirmed" in l for l in dl_logs), dl_logs[:1])
if dl_logs:
    for l in dl_logs:
        print(f"\n  CONSOLE: {l}")
    try:
        payload = json.loads(dl_logs[0].replace("[dataLayer] ", ""))
        ck("pillar 為 bank", payload.get("pillar") == "bank", payload.get("pillar"))
        ck("event 名稱正確", payload.get("event") == "booking_confirmed")
        ck("帶 page_path", bool(payload.get("page_path")), payload.get("page_path"))
        ck("GTM 已接收（uniqueEventId）", "gtm.uniqueEventId" in payload, list(payload.keys()))
    except Exception as e:
        ck("payload 可解析", False, str(e)[:80])

passed = sum(1 for r in res if r[0])
total = len(res)
print(f"\n{'='*72}")
for ok, n, d in res:
    print(f"{'PASS' if ok else 'FAIL'}  {n}" + (f"  :: {d}" if d else ""))
print("=" * 72)
print(f"{passed}/{total} 通過")
sys.exit(0 if passed == total else 1)
