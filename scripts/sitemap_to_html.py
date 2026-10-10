#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sitemap_to_html.py — 由 sitemap.xml 產生「品牌化 sitemap.html」

為何需要：
  Chrome 158（2026-11-17）移除 XSLT，屆時 sitemap.xml 靠 xml-stylesheet
  渲染的表格會失效、退回純 XML 亂碼。本腳本產生獨立的 HTML 版網站地圖
  （不依賴任何 XSLT / JS），作為永久解。

設計原則：
  * 資料來源 ＝ sitemap.xml（唯一真相），不硬寫清單 → 永遠同步、不會 drift
  * 產出純靜態 HTML（無 JS、無 XSLT）
  * 每站依自身品牌色與字型排版

用法：
  python3 sitemap_to_html.py --site dingyao   --sitemap dist/sitemap.xml --out dist
  python3 sitemap_to_html.py --site crestline --sitemap sitemap.xml --out .
  python3 sitemap_to_html.py --site canvascrest --sitemap sitemap.xml --out . --langs en,zh-tw,...

產出：
  單語站 → sitemap.html
  多語站（--langs）→ sitemap.html（第一語言）+ sitemap-{lang}.html（其餘）
"""
import argparse
import html as _html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SM_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'

# --------------------------------------------------------------------------
# 各站品牌設定
# --------------------------------------------------------------------------
SITES = {
    'dingyao': {
        'fonts': ("https://fonts.googleapis.com/css2?"
                  "family=Playfair+Display:wght@500;600;700&"
                  "family=Inter:wght@300;400;500;600&display=swap"),
        'heading_font': "'Playfair Display', Georgia, serif",
        'body_font': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        'bg': '#0A0E17', 'accent': '#C9A84C', 'text': '#F5F0E8',
        'muted': '#8B8FA3', 'line': 'rgba(201,168,76,0.15)',
        'row_line': 'rgba(245,240,232,0.07)',
        'brand': 'DingYao Advisory',
        # 追蹤碼：GTM 容器（內含 GA4 + Clarity）；Plausible 本站為直嵌
        'gtm': 'GTM-PVWHRBWG',
        'plausible': 'dingyaoadvisory.tw',
    },
    'crestline': {
        'fonts': ("https://fonts.googleapis.com/css2?"
                  "family=Playfair+Display:wght@500;600;700&"
                  "family=Inter:wght@300;400;500;600&display=swap"),
        'heading_font': "'Playfair Display', Georgia, serif",
        'body_font': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        'bg': '#0F172A', 'accent': '#C5A059', 'text': '#F8F9FA',
        'muted': '#8B8FA3', 'line': 'rgba(197,160,89,0.15)',
        'row_line': 'rgba(248,249,250,0.07)',
        'brand': 'Crestline Advisory',
        # GTM 容器（內含 GA4 + Clarity + Plausible，故不可在 HTML 重複嵌 Plausible）
        'gtm': 'GTM-TCBK8C73',
    },
    'canvascrest': {
        'fonts': ("https://fonts.googleapis.com/css2?"
                  "family=Playfair+Display:wght@500;600;700&"
                  "family=Inter:wght@300;400;500;600&display=swap"),
        'heading_font': "'Playfair Display', Georgia, serif",
        'body_font': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        'bg': '#0F172A', 'accent': '#C5A059', 'text': '#F8F9FA',
        'muted': '#8B8FA3', 'line': 'rgba(197,160,89,0.15)',
        'row_line': 'rgba(248,249,250,0.07)',
        'brand': 'CanvasCrest Properties',
        # GTM 容器（內含 GA4 + Clarity + Plausible，故不可在 HTML 重複嵌 Plausible）
        'gtm': 'GTM-TKFNCJVZ',
    },
}

# --------------------------------------------------------------------------
# 標籤（標題／說明／表頭／計數／回首頁），依語言
# --------------------------------------------------------------------------
LABELS = {
    'zh-TW': {
        'html_lang': 'zh-Hant',
        'h1': '網站地圖',
        'brand_sub': 'Sitemap',
        'desc': '本站所有頁面的完整清單，點擊任一連結即可開啟該頁面。',
        'th_url': '頁面網址',
        'th_lastmod': '最後更新',
        'count': '共 {n} 個頁面',
        'back': '← 返回首頁',
    },
    'en': {
        'html_lang': 'en',
        'h1': 'Sitemap',
        'brand_sub': '',
        'desc': 'Complete list of every page on this website. Click any link to open that page.',
        'th_url': 'Page URL',
        'th_lastmod': 'Last updated',
        'count': '{n} pages',
        'back': '← Back to home',
    },
    'zh-CN': {
        'html_lang': 'zh-Hans',
        'h1': '网站地图',
        'brand_sub': '',
        'desc': '本站所有页面的完整清单，点击任一链接即可打开该页面。',
        'th_url': '页面网址',
        'th_lastmod': '最后更新',
        'count': '共 {n} 个页面',
        'back': '← 返回首页',
    },
    'zu': {
        'html_lang': 'zu',
        'h1': 'Imephu yesayithi',
        'brand_sub': '',
        'desc': 'Uhlu oluphelele lwazo zonke izikhathi ezikuleli webhusayithi. Chofoza noma isiphi isixhumanisi ukuvula lelo khasi.',
        'th_url': 'Ikheli lekhasi',
        'th_lastmod': 'Kugcine ukubuyekezwa',
        'count': 'amakhasi angu-{n}',
        'back': '← Buyela ekhasini lokuqala',
    },
    'af': {
        'html_lang': 'af',
        'h1': 'Webwerfkaart',
        'brand_sub': '',
        'desc': "Volledige lys van elke bladsy op hierdie webwerf. Klik op enige skakel om daardie bladsy oop te maak.",
        'th_url': 'Bladsy-URL',
        'th_lastmod': 'Laas opgedateer',
        'count': '{n} bladsye',
        'back': '← Terug na tuisblad',
    },
    'fr': {
        'html_lang': 'fr',
        'h1': 'Plan du site',
        'brand_sub': '',
        'desc': 'Liste complète de toutes les pages de ce site. Cliquez sur un lien pour ouvrir la page.',
        'th_url': 'URL de la page',
        'th_lastmod': 'Dernière mise à jour',
        'count': '{n} pages',
        'back': "← Retour à l'accueil",
    },
    'de': {
        'html_lang': 'de',
        'h1': 'Sitemap',
        'brand_sub': '',
        'desc': 'Vollständige Liste aller Seiten dieser Website. Klicken Sie auf einen Link, um die Seite zu öffnen.',
        'th_url': 'Seiten-URL',
        'th_lastmod': 'Zuletzt aktualisiert',
        'count': '{n} Seiten',
        'back': '← Zurück zur Startseite',
    },
}

# 雙語站（dingyao / crestline）用的標籤
BILINGUAL = {
    'dingyao': {
        'html_lang': 'zh-Hant',
        'h1': '網站地圖',
        'brand_sub': 'Sitemap',
        'desc': '本站所有頁面的完整清單，點擊任一連結即可開啟該頁面。Complete list of every page on this website.',
        'th_url': '頁面網址 / Page',
        'th_lastmod': '最後更新 / Last updated',
        'count_zh': '共 {n} 個頁面',
        'count_en': '{n} pages',
        'back': '← 返回首頁',
    },
    'crestline': {
        'html_lang': 'en',
        'h1': 'Sitemap',
        'brand_sub': '網站地圖',
        'desc': 'Complete list of every page on this website. Click any link to open that page. 本站所有頁面的完整清單。',
        'th_url': 'Page URL / 頁面網址',
        'th_lastmod': 'Last updated / 最後更新',
        'count_zh': '共 {n} 個頁面',
        'count_en': '{n} pages',
        'back': '← Back to home',
    },
}


# --------------------------------------------------------------------------
# 解析 sitemap.xml
# --------------------------------------------------------------------------
def parse_sitemap(path: Path) -> list:
    """回傳 [(loc, lastmod), ...]，依 sitemap 原始順序。"""
    raw = path.read_text(encoding='utf-8')
    # 去除 xml-stylesheet PI，避免 ElementTree 抱怨（實測可正常解析，保險起見）
    raw = re.sub(r'<\?xml-stylesheet[^>]*\?>', '', raw)
    root = ET.fromstring(raw)
    out = []
    for url_el in root.findall(f'{{{SM_NS}}}url'):
        loc_el = url_el.find(f'{{{SM_NS}}}loc')
        if loc_el is None or not (loc_el.text or '').strip():
            continue
        loc = loc_el.text.strip()
        lm_el = url_el.find(f'{{{SM_NS}}}lastmod')
        lm = (lm_el.text or '').strip()[:10] if lm_el is not None and lm_el.text else ''
        out.append((loc, lm))
    return out


def _labels_for(lang_id: str) -> dict:
    """語言 id -> 標籤。容錯大小寫（canvascrest 用 zh-tw/zh-cn，標準碼為 zh-TW/zh-CN）。"""
    if lang_id in LABELS:
        return LABELS[lang_id]
    low = lang_id.lower()
    for k, v in LABELS.items():
        if k.lower() == low:
            return v
    raise SystemExit(f'!! 無此語言的標籤定義: {lang_id}（可用: {sorted(LABELS)}）')


def rel_display(loc: str, domain: str) -> str:
    """把絕對 URL 轉成顯示用的相對路徑（首頁 -> /）"""
    if domain and loc.startswith(domain):
        p = loc[len(domain):] or '/'
        return p if p.startswith('/') else '/' + p
    return loc


# --------------------------------------------------------------------------
# HTML 產生
# --------------------------------------------------------------------------
TPL = """<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc_esc}">
<meta name="robots" content="noindex, follow">
{gtm_head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0;
    padding: 48px 24px 64px;
    background: {bg};
    color: {text};
    font-family: {body_font};
    font-size: 15px;
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; }}
  .brand {{
    color: {accent};
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .22em;
    text-transform: uppercase;
    margin: 0 0 14px;
  }}
  h1 {{
    font-family: {heading_font};
    font-weight: 600;
    font-size: 2.6rem;
    line-height: 1.15;
    color: {accent};
    margin: 0 0 6px;
    letter-spacing: .01em;
  }}
  .sub {{
    font-family: {heading_font};
    font-size: 1.05rem;
    color: {muted};
    margin: 0 0 22px;
  }}
  .desc {{ color: {muted}; margin: 0 0 22px; max-width: 68ch; }}
  .meta {{
    display: flex; flex-wrap: wrap; gap: 10px 22px;
    align-items: center;
    border-top: 1px solid {line};
    border-bottom: 1px solid {line};
    padding: 14px 0;
    margin: 0 0 6px;
    font-size: .84rem;
    color: {muted};
  }}
  .count {{ color: {accent}; font-weight: 600; }}
  .meta a {{ color: {accent}; text-decoration: none; }}
  .meta a:hover {{ text-decoration: underline; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }}
  caption {{ caption-side: top; text-align: left; padding: 0 0 10px; }}
  th {{
    text-align: left;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: {accent};
    border-bottom: 1px solid {line};
    padding: 12px 14px;
    white-space: nowrap;
  }}
  td {{
    padding: 13px 14px;
    border-bottom: 1px solid {row_line};
    vertical-align: top;
  }}
  td.u {{ word-break: break-all; }}
  td.u a {{
    color: {text};
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: color .18s, border-color .18s;
  }}
  td.u a:hover {{ color: {accent}; border-bottom-color: {accent}; }}
  td.d {{ color: {muted}; white-space: nowrap; font-variant-numeric: tabular-nums; }}
  th.col-d, td.col-d {{ text-align: right; }}
  footer {{
    margin-top: 34px;
    padding-top: 20px;
    border-top: 1px solid {line};
    color: {muted};
    font-size: .82rem;
    display: flex; flex-wrap: wrap; gap: 10px 22px;
    justify-content: space-between;
  }}
  footer a {{ color: {accent}; text-decoration: none; }}
  footer a:hover {{ text-decoration: underline; }}
  @media (max-width: 640px) {{
    body {{ padding: 32px 16px 48px; font-size: 14px; }}
    h1 {{ font-size: 1.9rem; }}
    td, th {{ padding: 10px 8px; }}
    th.col-d, td.col-d {{ text-align: left; }}
  }}
</style>
</head>
<body>
{gtm_body}
<div class="wrap">
  <p class="brand">{brand}</p>
  <h1>{h1}</h1>
  {sub_html}
  <p class="desc">{desc}</p>
  <div class="meta">
    <span class="count">{count}</span>
    <a href="{home}">{back}</a>
  </div>
  <table>
    <thead>
      <tr><th scope="col">{th_url}</th><th scope="col" class="col-d">{th_lastmod}</th></tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
  <footer>
    <span>{brand}</span>
    <span><a href="{home}">{back}</a></span>
  </footer>
</div>
</body>
</html>
"""


def render(site: str, entries: list, labels: dict, domain: str, title: str) -> str:
    cfg = SITES[site]
    rows = []
    for loc, lm in entries:
        disp = rel_display(loc, domain)
        rows.append(
            '      <tr>\n'
            f'        <td class="u"><a href="{_html.escape(loc, quote=True)}">{_html.escape(disp)}</a></td>\n'
            f'        <td class="d col-d">{_html.escape(lm)}</td>\n'
            '      </tr>'
        )
    n = len(entries)
    if 'count' in labels:
        count = labels['count'].format(n=n)
    else:
        count = labels['count_zh'].format(n=n) + ' · ' + labels['count_en'].format(n=n)
    sub = labels.get('brand_sub', '')
    sub_html = f'  <p class="sub">{_html.escape(sub)}</p>' if sub else ''

    # 追蹤碼：GTM 容器（各站自己的容器）。dingyao 另加直嵌 Plausible；
    # crestline / canvascrest 的 Plausible 由 GTM 容器注入，不可在 HTML 重複（會重複計數）。
    gtm_id = cfg.get('gtm', '')
    gtm_head = gtm_body = ''
    if gtm_id:
        gtm_head = (
            '<!-- Google Tag Manager -->\n'
            "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
            "f.parentNode.insertBefore(j,f);})"
            f"(window,document,'script','dataLayer','{gtm_id}');</script>\n"
            '<!-- End Google Tag Manager -->'
        )
        gtm_body = (
            '<!-- Google Tag Manager (noscript) -->\n'
            f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}"'
            ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
            '<!-- End Google Tag Manager (noscript) -->'
        )
    plaus = cfg.get('plausible', '')
    if plaus:
        snip = (f'<script defer data-domain="{plaus}" '
                'src="https://plausible.dingyaoadvisory.tw/js/script.js"></script>')
        gtm_head = f'{gtm_head}\n{snip}' if gtm_head else snip

    return TPL.format(
        html_lang=labels.get('html_lang', 'en'),
        title=_html.escape(title),
        desc=_html.escape(labels['desc']),
        desc_esc=_html.escape(labels['desc'], quote=True),
        fonts=cfg['fonts'],
        body_font=cfg['body_font'],
        heading_font=cfg['heading_font'],
        bg=cfg['bg'], accent=cfg['accent'], text=cfg['text'],
        muted=cfg['muted'], line=cfg['line'], row_line=cfg['row_line'],
        brand=_html.escape(cfg['brand']),
        h1=_html.escape(labels['h1']),
        sub_html=sub_html,
        count=count,
        home=domain + '/',
        back=_html.escape(labels['back']),
        th_url=_html.escape(labels['th_url']),
        th_lastmod=_html.escape(labels['th_lastmod']),
        rows='\n'.join(rows),
        gtm_head=gtm_head,
        gtm_body=gtm_body,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', required=True, choices=sorted(SITES))
    ap.add_argument('--sitemap', required=True, help='sitemap.xml 路徑（讀取來源）')
    ap.add_argument('--out', required=True, help='輸出目錄')
    ap.add_argument('--domain', default=None, help='網站網域（預設由 sitemap 首個 loc 推斷）')
    ap.add_argument('--langs', default=None,
                    help='逗號分隔語言 id（多語站，順序同 sitemap 語序；第一語言寫成 sitemap.html）')
    ap.add_argument('--title-suffix', default=None, help='<title> 附加字串，例如 "CanvasCrest Properties"')
    args = ap.parse_args()

    sm_path = Path(args.sitemap)
    if not sm_path.exists():
        print(f'!! 找不到 {sm_path}', file=sys.stderr)
        return 1
    entries = parse_sitemap(sm_path)
    if not entries:
        print(f'!! {sm_path} 解析不到任何 <loc>', file=sys.stderr)
        return 1

    domain = args.domain
    if not domain:
        m = re.match(r'(https?://[^/]+)', entries[0][0])
        domain = m.group(1) if m else ''

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f' — {args.title_suffix}' if args.title_suffix else ''

    if args.langs:
        langs = [x.strip() for x in args.langs.split(',') if x.strip()]
    else:
        langs = None

    written = []
    if langs:
        # 多語站：第一語言 -> sitemap.html，其餘 -> sitemap-{lang}.html
        for i, lg in enumerate(langs):
            labels = _labels_for(lg)
            title = f'{labels["h1"]}{suffix}'
            fn = 'sitemap.html' if i == 0 else f'sitemap-{lg}.html'
            (out_dir / fn).write_text(render(args.site, entries, labels, domain, title), encoding='utf-8')
            written.append((fn, len(entries), labels['h1']))
    else:
        labels = BILINGUAL.get(args.site) or LABELS['en']
        title = f'{labels["h1"]}{suffix}'
        fn = 'sitemap.html'
        (out_dir / fn).write_text(render(args.site, entries, labels, domain, title), encoding='utf-8')
        written.append((fn, len(entries), labels['h1']))

    print(f'sitemap.xml : {sm_path}  ({len(entries)} entries)')
    print(f'domain      : {domain}')
    for fn, n, h1 in written:
        print(f'  -> {out_dir / fn}  ({n} rows, h1="{h1}")')
    return 0


if __name__ == '__main__':
    sys.exit(main())
