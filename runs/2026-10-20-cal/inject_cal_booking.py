#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cal.com inline 預約區塊 + L4 booking_confirmed 事件注入器（冪等）。

用法：
    python3 inject_cal_booking.py <html 檔> <pillar> <lang>
    pillar ∈ bank_account | property | education
    lang   ∈ zh | en

設計原則：
  1. 冪等 —— 已注入過就跳過（偵測 INJECT_MARKER），可重複執行不產生重複區塊
  2. 不彈窗 —— 用 Cal.com inline embed（data-cal-link + embed.js），訪客不跳站
  3. 金黑風格 —— brandColor #C9A84C、深底 #0A0E17、theme dark
  4. 手機不溢出 —— 容器 width:100% + overflow-x:hidden + iframe max-width:100%
  5. L4 事件 —— 監聽 Cal bookingSuccessful 後 push dataLayer，帶 pillar 供 GA4 分支柱計轉換率
"""
import re
import sys
import pathlib

MARKER = "<!-- cal-booking-inline-v1 -->"

# ---------------------------------------------------------------- 文案
COPY = {
    ("zh", "bank"): dict(
        label="Book a Consultation",
        h2="預約 30 分鐘顧問評估",
        sub="先確認你的南非幣部位適合哪一種帳戶，再談文件。<br>30 分鐘，不推銷商品。",
        bullet=[
            "確認你手上的南非幣目前放在哪（保單／基金／外幣定存）",
            "核對 FICA 文件、地址證明、稅務編號是否符合格式",
            "試算三個情境：匯率不變、貶 5.40%、貶 15%",
        ],
        note="預約後你會收到 Google 行事曆邀請與線上會議連結。時區自動換算成你所在時區。",
        text_cta="想先確認能不能開戶？<a href=\"#booking\" data-cta-id=\"inline_to_booking\" data-cta-location=\"body_text\">直接選時段預約 30 分鐘評估</a>",
    ),
    ("zh", "property"): dict(
        label="Book a Consultation",
        h2="預約 30 分鐘顧問評估",
        sub="先把淨報酬、稅費與退場算清楚，再談看房。<br>30 分鐘，不帶看、不推案。",
        bullet=[
            "釐清你的持有年限、租金期待與退場方式",
            "試算淨報酬（扣掉稅費、管理費、空置期）",
            "說明外國人持有南非房產的稅務與匯出限制",
        ],
        note="預約後你會收到 Google 行事曆邀請與線上會議連結。時區自動換算成你所在時區。",
        text_cta="想先算清楚淨報酬？<a href=\"#booking\" data-cta-id=\"inline_to_booking\" data-cta-location=\"body_text\">直接選時段預約 30 分鐘評估</a>",
    ),
    ("zh", "education"): dict(
        label="Book a Consultation",
        h2="預約 30 分鐘顧問評估",
        sub="先確認孩子適合哪一條升學路徑、哪一個學區。<br>30 分鐘，不代辦、不抽佣。",
        bullet=[
            "依孩子的年齡與英文程度，對應可申請的學校層級",
            "說明學費、住宿、監護與簽證的實際支出結構",
            "評估學區置產與純租屋的差別",
        ],
        note="預約後你會收到 Google 行事曆邀請與線上會議連結。時區自動換算成你所在時區。",
        text_cta="想先確認孩子適合哪條路徑？<a href=\"#booking\" data-cta-id=\"inline_to_booking\" data-cta-location=\"body_text\">直接選時段預約 30 分鐘評估</a>",
    ),
    ("en", "bank"): dict(
        label="Book a Consultation",
        h2="Book a 30-Minute Consultation",
        sub="First find out which account fits your Rand position — then we talk documents.<br>30 minutes, no product pitch.",
        bullet=[
            "Where your Rand currently sits (policy, fund, or FX deposit)",
            "Whether your FICA documents, proof of address and tax number are in the right format",
            "Three scenarios modelled: flat FX, -5.40%, -15%",
        ],
        note="You will receive a Google Calendar invite and the meeting link. Times are shown in your own timezone.",
        text_cta="Want to check eligibility first?<a href=\"#booking\" data-cta-id=\"inline_to_booking\" data-cta-location=\"body_text\">Pick a slot for a 30-minute assessment</a>",
    ),
    ("en", "property"): dict(
        label="Book a Consultation",
        h2="Book a 30-Minute Consultation",
        sub="Get net returns, taxes and exit clear before you view anything.<br>30 minutes, no viewings, no listings.",
        bullet=[
            "Clarify your holding period, rental expectation and exit route",
            "Model net returns after taxes, levies and vacancy",
            "Explain tax treatment and profit repatriation for foreign owners",
        ],
        note="You will receive a Google Calendar invite and the meeting link. Times are shown in your own timezone.",
        text_cta="Want the net return modelled first?<a href=\"#booking\" data-cta-id=\"inline_to_booking\" data-cta-location=\"body_text\">Pick a slot for a 30-minute assessment</a>",
    ),
    ("en", "education"): dict(
        label="Book a Consultation",
        h2="Book a 30-Minute Consultation",
        sub="Find the right school tier and the right catchment for your child.<br>30 minutes, no agency fees.",
        bullet=[
            "Match school tier to your child's age and English level",
            "Break down fees, boarding, guardianship and visa costs",
            "Compare buying in a catchment vs. renting",
        ],
        note="You will receive a Google Calendar invite and the meeting link. Times are shown in your own timezone.",
        text_cta="Want to find the right path first?<a href=\"#booking\" data-cta-id=\"inline_to_booking\" data-cta-location=\"body_text\">Pick a slot for a 30-minute assessment</a>",
    ),
}

CSS = """
<style id="cal-booking-css">
/* Cal.com 預約區塊（金黑風格） */
.booking-section{
  position:relative;padding:5rem 0 5.5rem;background:#0A0E17;overflow:hidden;
  border-top:1px solid rgba(201,168,76,.12);
}
.booking-section::before{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(900px 380px at 50% 0%,rgba(201,168,76,.10),transparent 70%);
}
.booking-section .container{position:relative;z-index:1}
.booking-head{text-align:center;max-width:760px;margin:0 auto 2.25rem}
.booking-head h2{
  font-size:clamp(1.6rem,3.4vw,2.35rem);line-height:1.35;margin:.55rem 0 1rem;color:#F5F0E8;
}
.booking-head p{color:rgba(245,240,232,.72);font-size:1rem;line-height:1.85;margin:0}
.booking-points{
  list-style:none;padding:0;margin:1.75rem auto 0;max-width:620px;text-align:left;
}
.booking-points li{
  position:relative;padding:0 0 0 1.6rem;margin:.6rem 0;
  color:rgba(245,240,232,.86);font-size:.94rem;line-height:1.75;
}
.booking-points li::before{
  content:"";position:absolute;left:0;top:.62em;width:8px;height:8px;
  border-radius:50%;background:#C9A84C;box-shadow:0 0 0 3px rgba(201,168,76,.16);
}
.booking-wrap{
  max-width:1000px;margin:0 auto;padding:1.5rem;
  background:linear-gradient(180deg,rgba(22,28,40,.92),rgba(10,14,23,.96));
  border:1px solid rgba(201,168,76,.20);border-radius:18px;
  box-shadow:0 24px 60px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.04);
}
#cal-inline{
  width:100%;height:660px;min-height:660px;
  overflow:hidden;border-radius:12px;background:transparent;
}
#cal-inline iframe{max-width:100%!important;border-radius:12px!important}
.booking-note{
  max-width:760px;margin:1.5rem auto 0;text-align:center;
  font-size:.8rem;line-height:1.8;color:rgba(245,240,232,.5);
}
.booking-text-cta{
  max-width:820px;margin:2.25rem auto 0;padding:1.1rem 1.35rem;text-align:center;
  border:1px solid rgba(201,168,76,.22);border-radius:12px;
  background:rgba(201,168,76,.05);font-size:.95rem;line-height:1.8;color:rgba(245,240,232,.85);
}
.booking-text-cta a{color:#C9A84C;text-decoration:underline;text-underline-offset:3px;font-weight:600}
.booking-text-cta a:hover{color:#E4C876}
@media(max-width:768px){
  .booking-section{padding:3.25rem 0 3.75rem}
  .booking-wrap{padding:.85rem;border-radius:14px}
  #cal-inline{height:1000px;min-height:1000px;overflow-y:auto;-webkit-overflow-scrolling:touch;border-radius:10px}
  .booking-head{margin-bottom:1.5rem}
  .booking-points li{font-size:.9rem}
}
@media(max-width:400px){
  #cal-inline{height:980px;min-height:980px}
  .booking-wrap{padding:.6rem}
}
</style>
"""


def build_section(pillar: str, lang: str) -> str:
    c = COPY[(lang, pillar)]
    bullets = "\n".join(f"        <li>{b}</li>" for b in c["bullet"])
    return f"""{MARKER}
{CSS}
<section class="section booking-section" id="booking" data-pillar="{pillar}">
  <div class="container">
    <div class="booking-head fade-in">
      <span class="section-label">{c['label']}</span>
      <h2>{c['h2']}</h2>
      <p>{c['sub']}</p>
      <ul class="booking-points">
{bullets}
      </ul>
    </div>
    <div class="booking-wrap fade-in">
      <div id="cal-inline"></div>
    </div>
    <p class="booking-note">{c['note']}</p>
    <div class="booking-text-cta">{c['text_cta']}</div>
  </div>
</section>
"""


def build_script(pillar: str, lang: str) -> str:
    ns = "dingyao"
    return f"""
<script>
/* Cal.com inline embed + L4 booking_confirmed（pillar={pillar}） */
(function (C, A, L) {{
  var p = function (a, ar) {{ a.q.push(ar); }};
  var d = C.document;
  C.Cal = C.Cal || function () {{
    var cal = C.Cal, ar = arguments;
    if (!cal.loaded) {{
      cal.ns = {{}}; cal.q = cal.q || [];
      d.head.appendChild(d.createElement("script")).src = A;
      cal.loaded = true;
    }}
    if (ar[0] === L) {{
      var api = function () {{ p(api, arguments); }};
      var namespace = ar[1];
      api.q = api.q || [];
      if (typeof namespace === "string") {{
        cal.ns[namespace] = cal.ns[namespace] || api;
        p(cal.ns[namespace], ar); p(cal, ["initNamespace", namespace]);
      }} else p(cal, ar);
      return;
    }}
    p(cal, ar);
  }};
}})(window, "https://app.cal.com/embed/embed.js", "init");

Cal("init", "{ns}", {{ origin: "https://cal.com" }});

Cal.ns.{ns}("inline", {{
  elementOrSelector: "#cal-inline",
  calLink: "dingyao/30min",
  config: {{ layout: "month_view", theme: "dark" }},
  styles: {{ branding: {{ brandColor: "#C9A84C" }} }}
}});

Cal.ns.{ns}("ui", {{
  theme: "dark",
  layout: "month_view",
  hideEventTypeDetails: false,
  styles: {{ branding: {{ brandColor: "#C9A84C" }} }},
  cssVarsPerTheme: {{
    dark: {{ "cal-brand": "#C9A84C", "cal-bg": "#0A0E17", "cal-bg-emphasis": "#141A26" }}
  }}
}});

/* L4：預約成立 */
Cal.ns.{ns}("on", {{
  action: "bookingSuccessful",
  callback: function (e) {{
    window.dataLayer = window.dataLayer || [];
    var d = (e && e.detail && e.detail.data) || {{}};
    function ss(k) {{ try {{ return sessionStorage.getItem(k) || ""; }} catch (x) {{ return ""; }} }}
    var qs = new URLSearchParams(location.search);
    function utm(k) {{ return qs.get(k) || ss("dy_" + k) || ""; }}
    window.dataLayer.push({{
      event: "booking_confirmed",
      event_category: "funnel_l4",
      pillar: "{pillar}",
      booking_source: "cal_inline",
      booking_uid: d.uid || d.bookingUid || "",
      booking_event_type: "30min",
      page_path: location.pathname,
      language: "{lang}",
      funnel_session_id: ss("dy_funnel_sid") || "",
      utm_source: utm("utm_source"),
      utm_medium: utm("utm_medium"),
      utm_campaign: utm("utm_campaign")
    }});
  }}
}});

/* 容器高度跟隨 Cal iframe。
   Cal 用 __dimensionChanged 把 iframe.style.height 設成內容高度（平板 1260px），
   但容器固定高度 + overflow:hidden 會把下方時段裁掉。這裡同步容器高度，
   同時消掉桌機原本的底部留白（iframe 534 vs 容器 660）。 */
(function () {
  var tries = 0;
  var timer = setInterval(function () {
    var c = document.getElementById("cal-inline");
    var f = c && c.querySelector("iframe");
    if (!f) { if (++tries > 80) clearInterval(timer); return; }
    clearInterval(timer);
    function sync() {
      var h = Math.round(f.getBoundingClientRect().height);
      if (h > 200 && Math.abs(h - c.getBoundingClientRect().height) > 2) {
        c.style.height = h + "px";
      }
    }
    if (window.ResizeObserver) { new ResizeObserver(sync).observe(f); }
    sync();
  }, 250);
})();
</script>
"""


def inject(path: pathlib.Path, pillar: str, lang: str) -> str:
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return f"SKIP（已注入）  {path.name}"
    if "cal.com/embed/embed.js" in html:
        return f"SKIP（已有 cal embed，但非本注入器）  {path.name}"

    block = build_section(pillar, lang)
    script = build_script(pillar, lang)

    # 插入點：</main> 之前（若無 </main> 則 </footer> 之前）
    m = re.search(r"</main>", html)
    if not m:
        m = re.search(r"<footer", html)
    if not m:
        raise SystemExit(f"找不到插入點：{path}")

    html = html[: m.start()] + block + "\n" + html[m.start():]

    # 腳本插在 </body> 前
    mb = re.search(r"</body>", html)
    if not mb:
        raise SystemExit(f"找不到 </body>：{path}")
    html = html[: mb.start()] + script + "\n" + html[mb.start():]

    path.write_text(html, encoding="utf-8")
    return f"OK  {path.name}  (+{len(html)} bytes, pillar={pillar}, lang={lang})"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    f = pathlib.Path(sys.argv[1])
    pillar, lang = sys.argv[2], sys.argv[3]
    if (lang, pillar) not in COPY:
        raise SystemExit(f"不支援的組合：lang={lang} pillar={pillar}")
    print(inject(f, pillar, lang))
