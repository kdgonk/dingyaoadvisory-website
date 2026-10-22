#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Menu 三支柱改版 ＋ LOGO 白金版（土星人 2026-10-20 第 5 批，老闆已確認 mockup）。

LOGO：dist/dya-mark-whitegold.svg（D 白 / Y 金 #C5A059 / A 白，透明底）
Menu：6 項主選單，三個三支柱各帶 hover 下拉

  南非開戶 ▾   南非置產 ▾   教育留學 ▾   商業考察   鼎曜觀點   [預約諮詢]

不動：lang 切換器結構（含英文頁 logo → /index-en 的 JS）、.btn-nav 樣式。

用法：
    python3 rebuild_nav.py --dry <html...>
    python3 rebuild_nav.py <html...>
"""
import pathlib
import re
import sys
from collections import Counter

# ── LOGO（規格逐字照土星人給的，14.5/11.5px 比例不可改）──
LOGO_CSS = """.nav-logo{display:flex;align-items:center;gap:14px;text-decoration:none;margin-bottom:0}
.nav-mark{width:46px;height:36px;display:block;flex-shrink:0}
.nav-wordmark{display:flex;flex-direction:column;line-height:1.15}
.nav-w1{font-family:Cinzel,serif;font-size:14.5px;font-weight:600;letter-spacing:1.6px;color:#fff}
.nav-w2{font-size:11.5px;letter-spacing:2.4px;color:#C9A84C;font-weight:600;margin-top:2px}
"""

# ── 下拉選單 ──
DD_CSS = """.nav-item{position:relative}
.nav-links>.nav-item>a{display:inline-flex;align-items:center;gap:5px}
.nav-dd{position:absolute;top:calc(100% + 14px);left:50%;transform:translateX(-50%) translateY(6px);
  background:rgba(10,14,23,.98);backdrop-filter:blur(20px);border:1px solid rgba(201,168,76,.22);
  border-radius:8px;padding:8px;min-width:236px;opacity:0;visibility:hidden;transition:opacity .22s,transform .22s,visibility .22s;
  box-shadow:0 16px 44px rgba(0,0,0,.55);z-index:120}
.nav-item.has-dd:hover .nav-dd,.nav-item.has-dd:focus-within .nav-dd{opacity:1;visibility:visible;transform:translateX(-50%) translateY(0)}
.nav-dd a{display:flex;flex-direction:column;gap:1px;padding:9px 13px;border-radius:5px;white-space:nowrap;transition:background .2s}
.nav-dd a:hover{background:rgba(201,168,76,.1)}
.nav-dd a::after{display:none}
.nav-dd strong{font-size:13.5px;font-weight:600;color:#F5F0E8;letter-spacing:.3px}
.nav-dd .nd-sub{font-size:11px;color:#F5F0E899;letter-spacing:.2px}
"""

DD_MOBILE_CSS = """@media(max-width:768px){
  .nav-links{align-items:stretch}
  .nav-links>a,.nav-links>.nav-item{text-align:left}
  .nav-links>.nav-item{width:100%}
  .nav-links>.nav-item>a{width:100%;justify-content:space-between}
  .nav-links>.btn-nav{text-align:center;justify-content:center}
  .nav-dd{position:static;transform:none;opacity:1;visibility:visible;background:rgba(255,255,255,.03);
    border:none;border-left:2px solid rgba(201,168,76,.3);border-radius:0;padding:4px 0 4px 14px;margin:4px 0 2px;
    box-shadow:none;min-width:0;backdrop-filter:none}
  .nav-item.has-dd:hover .nav-dd{transform:none}
  .nav-dd a{padding:7px 10px}
  .nav-dd strong{font-size:13px}
  .nav-dd .nd-sub{font-size:10.5px}
}
"""

# ── 選單資料 ──
ZH_NAV = [
    ("dd", "南非開戶", "/south-africa-bank-account", [
        ("南非開戶服務", "Standard Bank 非居民帳戶", "/south-africa-bank-account"),
        ("數位服務", "數位資產平台", "/platform"),
        ("精選資產", "資產配置標的", "/assets"),
    ]),
    ("dd", "南非置產", "/south-africa-property", [
        ("南非置產服務", "開普敦房產顧問", "/south-africa-property"),
        ("海外買家流程", "交付與過戶", "/overseas-buyers"),
        ("退休生活", "退休移居方案", "/retirement"),
        ("身分規劃", "永久居留 PR", "/residency"),
    ]),
    ("dd", "教育留學", "/education", [
        ("教育留學總覽", "", "/education"),
        ("貴族寄宿學校", "", "/education#schools"),
        ("學費與生活成本", "", "/education#cost"),
    ]),
    ("link", "商業考察", "/tour", None),
    ("link", "鼎曜觀點", "/blog", None),
    ("btn", "預約諮詢", "/consultation", None),
]

EN_NAV = [
    ("dd", "Bank Account", "/south-africa-bank-account-en", [
        ("SA Bank Account Service", "Standard Bank Non-Resident Account", "/south-africa-bank-account-en"),
        ("Digital Services", "Digital Asset Platform", "/platform-en"),
        ("Featured Assets", "Asset Allocation", "/assets-en"),
    ]),
    ("dd", "SA Property", "/south-africa-property-en", [
        ("SA Property Advisory", "Cape Town Property Advisory", "/south-africa-property-en"),
        ("Overseas Buyer Process", "Delivery & Transfer", "/overseas-buyers-en"),
        ("Retirement", "Retirement Relocation", "/retirement-en"),
        ("Residency", "Permanent Residency", "/residency-en"),
    ]),
    ("dd", "Education", "/education-en", [
        ("Education Overview", "", "/education-en"),
        ("Top Boarding Schools", "", "/education-en#schools"),
        ("Fees and Living Costs", "", "/education-en#cost"),
    ]),
    ("link", "Business Tour", "/tour-en", None),
    ("link", "Insights", "/blog-en", None),
    ("btn", "Consultation", "/consultation-en", None),
]

LANG_SCRIPT = """<div class="nav-lang" id="langSwitcher">
  <a href="#" class="active" id="langTw" title="TW">TW</a><span>/</span><a href="#" id="langEn" title="EN">EN</a>
</div>
<script>
(function(){
  var path = window.location.pathname;
  var tw = document.getElementById('langTw');
  var en = document.getElementById('langEn');
  var logo = document.getElementById('navLogo');
  if (path.endsWith('-en')) { tw.href = path.slice(0, -3) || '/'; } else { tw.href = path; }
  if (path === '/') { en.href = '/index-en'; }
  else if (path.endsWith('-en')) { en.href = path; }
  else { en.href = path + '-en'; }
  if (path.endsWith('-en')) {
    en.classList.add('active'); tw.classList.remove('active');
    if (logo) logo.href = '/index-en';
  } else {
    tw.classList.add('active'); en.classList.remove('active');
    if (logo) logo.href = 'https://dingyaoadvisory.tw';
  }
})();
</script>"""


def build_menu(items, is_en):
    out = []
    for kind, label, href, sub in items:
        if kind == "dd":
            rows = []
            for s_label, s_sub, s_href in sub:
                sub_html = f'<span class="nd-sub">{s_sub}</span>' if s_sub else ""
                rows.append(f'          <a href="{s_href}"><strong>{s_label}</strong>{sub_html}</a>')
            out.append(
                f'      <div class="nav-item has-dd">\n'
                f'        <a href="{href}" title="{label}">{label} ▾</a>\n'
                f'        <div class="nav-dd">\n' + "\n".join(rows) + "\n        </div>\n"
                f'      </div>'
            )
        elif kind == "btn":
            out.append(f'      <a href="{href}" class="btn-nav" title="{label}">{label}</a>')
        else:
            out.append(f'      <a href="{href}" title="{label}">{label}</a>')
    return "\n".join(out)


def build_nav(is_en):
    items = EN_NAV if is_en else ZH_NAV
    logo_href = "/index-en" if is_en else "https://dingyaoadvisory.tw"
    aria = "Main navigation" if is_en else "主導覽"
    sr = "Main navigation" if is_en else "主導覽"
    return f"""<nav class="navbar" id="navbar" aria-label="{aria}">
<h2 class="sr-only">{sr}</h2>
  <div class="container">
    <a href="{logo_href}" class="nav-logo" id="navLogo">
      <img src="/dya-mark-whitegold.svg" alt="DYA" class="nav-mark" width="46" height="36">
      <span class="nav-wordmark">
        <span class="nav-w1">DingYao Advisory</span>
        <span class="nav-w2">APAC HUB</span>
      </span>
    </a>
    <div class="nav-links" id="navLinks">
{build_menu(items, is_en)}
      {LANG_SCRIPT}
    </div>
    <button class="nav-toggle" id="navToggle" aria-label="Menu"><i class="fas fa-bars"></i></button>
  </div>
</nav>"""


def strip_old_css(css):
    """清掉舊 .nav-logo 規則（土星人指定第 3、4 點）。"""
    css = re.sub(r'\.nav-logo\{[^}]*\}\n?', '', css)
    css = re.sub(r'\.nav-logo span\{[^}]*\}\n?', '', css)
    return css


def process(path: pathlib.Path, dry: bool):
    try:
        c = path.read_text(encoding="utf-8")
    except Exception:
        return "SKIP", "讀取失敗"
    if '<nav class="navbar"' not in c:
        return "SKIP", "無 nav"

    # 語系以 <html lang> 為準（最可靠）。實測 341 檔中有 4 檔的既有 nav 語系是錯的：
    #   404.html / platform.html → lang=zh-TW 卻裝英文 nav
    #   兩篇 -en 文章 → lang=en 卻裝中文 nav
    # 用 aria-label 或 /platform-en 判斷會把錯誤沿用下來。
    lang_m = re.search(r'<html[^>]*\slang="([^"]*)"', c)
    if lang_m:
        is_en = lang_m.group(1).lower().startswith("en")
    else:
        is_en = bool(re.search(r'<nav class="navbar"[^>]*aria-label="Main navigation"', c)) or "/platform-en" in c

    # ── 1. 換 nav ──
    m = re.search(r'<nav class="navbar".*?</nav>', c, re.S)
    if not m:
        return "FAIL", "nav 無法定位"
    new_nav = build_nav(is_en)
    new = c[:m.start()] + new_nav + c[m.end():]

    # ── 2. 清舊 CSS + 加新 CSS（在最後一個 </style> 前）──
    k = new.rfind("</style>")
    if k < 0:
        return "FAIL", "找不到 </style>"
    head = new[:k]
    # 只清 <style> 之後的內容不對；改為對整個 head 做替換
    head_clean = strip_old_css(head)
    css_block = "\n/* ===== nav LOGO 白金版 + 三支柱下拉（2026-10-20） ===== */\n" + \
                LOGO_CSS + DD_CSS + DD_MOBILE_CSS
    new = head_clean + css_block + "\n" + new[k:]

    # ── 3. 驗證 ──
    nm = re.search(r'<nav class="navbar".*?</nav>', new, re.S).group(0)
    if 'dya-mark-whitegold.svg' not in nm:
        return "FAIL", "LOGO 未進入 nav"
    if 'DingYao Advisory' not in nm or 'DingYao Advisory'.replace('Yao', ' Yao') in nm:
        return "FAIL", "wordmark 格式錯（須 DingYao 連寫）"
    dd_count = nm.count('class="nav-item has-dd"')
    if dd_count != 3:
        return "FAIL", "下拉數=%d（應 3）" % dd_count
    if 'class="btn-nav"' not in nm:
        return "FAIL", "btn-nav 遺失"
    if 'id="langSwitcher"' not in nm:
        return "FAIL", "lang 切換器遺失"
    if '.nav-logo span{' in new:
        return "FAIL", "舊 .nav-logo span 規則未清"

    if not dry:
        path.write_text(new, encoding="utf-8")
    return "OK", "en" if is_en else "zh"


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = [pathlib.Path(a) for a in args]
    stats = Counter()
    fails = []
    for f in files:
        st, note = process(f, dry)
        stats[st] += 1
        if st == "FAIL":
            fails.append((f, note))
    print(f"{'[DRY] ' if dry else ''}結果（{len(files)} 檔）：")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    if fails:
        print(f"\n❌ {len(fails)}：")
        for f, n in fails[:10]:
            print(f"   {f}: {n}")
        sys.exit(1)


if __name__ == "__main__":
    main()
