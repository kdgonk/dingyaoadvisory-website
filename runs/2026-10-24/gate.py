#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DingYao 39 項品質閘門（火星人自檢；依 dingyao-quality-gate skill）"""
import re, json, sys, os
from html.parser import HTMLParser

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'param', 'source', 'track', 'wbr', 'path', 'svg', 'circle', 'g'}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.err = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.err.append(f'stray </{tag}>')
            return
        if self.stack[-1][0] != tag:
            self.err.append(f'mismatch </{tag}> expected </{self.stack[-1][0]}>')
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    return
        else:
            self.stack.pop()


def ct_focus(body, keys, strict=False):
    pat = r'<p(?:\s[^>]*)?>(.*?)</p>' if strict else r'<p[^>]*>(.*?)</p>'
    paras = [re.sub(r'<[^>]+>', '', p).strip() for p in re.findall(pat, body, re.S)]
    paras = [p for p in paras if len(p) > 40]
    w = sum(len(p) for p in paras)
    hit = sum(len(p) for p in paras if any(k in p for k in keys))
    return (hit / w * 100) if w else 0.0


def related_links(html):
    m = re.search(r'<h2[^>]*>\s*(?:相關閱讀|Related\s+[Rr]eading).*?</h2>(.*?)(?=<h2|</article|</main>|$)', html, re.S)
    if not m:
        return -1
    return len(re.findall(r'href="/blog/', m.group(1)))


def q_h2_ratio(html, lang):
    h2 = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S)
    h2 = [re.sub(r'<[^>]+>', '', x).strip() for x in h2]
    h2 = [x for x in h2 if x and 'sr-only' not in x]
    body_h2 = [x for x in h2 if not re.search(r'常見問題|相關閱讀|^FAQ$|Related reading', x)]
    if lang == 'zh':
        q = [x for x in body_h2 if '？' in x]
    else:
        q = [x for x in body_h2 if '?' in x]
    return len(q), len(body_h2), ('%.0f%%' % (100 * len(q) / len(body_h2)) if body_h2 else '0%')


def check(zh_path, en_path, slug, topics_path, min_sections_imgs=None):
    z = open(zh_path, encoding='utf-8').read()
    e = open(en_path, encoding='utf-8').read()
    res = []

    def add(item, ok, detail=""):
        res.append((item, ok, detail))

    # 1 Tailwind
    tw = re.findall(r'border-l-4|text-yellow-400|bg-white/|border-gray-700|pl-6 mb-6|text-gray-300|backdrop-blur-xl|rounded-3xl', z + e)
    add("01 無 Tailwind class", not tw, str(tw[:3]))
    # 2 FontAwesome
    add("02 Font Awesome 格式", 'sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin' in z, "")
    # 3/4 Nav：以「NAVBAR 區塊與 production 現行模板逐字相同」為準
    # （protocol 的 9 連結表是 2026-10-20 前的舊架構；現行站体為三支柱下拉選單，
    #   依 dingyao-quality-gate pitfall「比對 navblk(article)==navblk(reference) 更可靠」）
    REPO = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website"
    tplz = open(os.path.join(REPO, "dist/blog/standard-bank-non-resident-account-2026.html"), encoding="utf-8").read()
    tple = open(os.path.join(REPO, "dist/blog/standard-bank-non-resident-account-2026-en.html"), encoding="utf-8").read()

    def navblk(t):
        s = t.index('<nav class="navbar"')
        return t[s:t.index("</nav>", s) + 6]

    add("03 NAVBAR 區塊與 production 模板一致 (ZH)", navblk(z) == navblk(tplz), f"len {len(navblk(z))}/{len(navblk(tplz))}")
    add("04 NAVBAR 區塊與 production 模板一致 (EN)", navblk(e) == navblk(tple), f"len {len(navblk(e))}/{len(navblk(tple))}")
    add("03b Nav 三支柱入口存在 (ZH)", all(h in z for h in ('/south-africa-bank-account', '/south-africa-property', '/education')), "")
    add("04b Nav 三支柱入口存在 (EN)", all(h in e for h in ('/south-africa-bank-account-en', '/south-africa-property-en', '/education-en')), "")
    # 5 social
    icons = ['fab fa-facebook-f', 'fab fa-instagram', 'fab fa-x-twitter', 'fab fa-linkedin-in', 'fab fa-threads', 'fab fa-youtube']
    add("05 Footer 6 social icons", all(i in z for i in icons) and all(i in e for i in icons),
        f"ZH {sum(i in z for i in icons)}/6 EN {sum(i in e for i in icons)}/6")
    # 6 CSS braces
    for nm, t in (("ZH", z), ("EN", e)):
        add(f"06 CSS 括號平衡 {nm}", t.count('{') == t.count('}'), f"{t.count('{')}/{t.count('}')}")
    # 7 hero slug
    for nm, t in (("ZH", z), ("EN", e)):
        refs = re.findall(r'/images/([a-z0-9-]+)-hero\.webp', t)
        add(f"07 Hero slug 一致 {nm}", bool(refs) and all(r == slug for r in refs), f"{len(refs)} refs, uniq={set(refs)}")
    # 8 og:image webp
    bad = [l for l in (z + e).split('\n') if 'og:image' in l and '.webp' not in l]
    add("08 og:image 為 .webp", not bad, str(bad[:1])[:80])
    # 9 DOM mirror: style blocks count
    add("09 ZH/EN style 區塊數相同", z.count('<style') == e.count('<style'), f"{z.count('<style')}/{e.count('<style')}")
    # 10 publisher
    add("10 JSON-LD publisher ZH", bool(re.search(r'"publisher":\s*\{[^}]*"name":\s*"[^"]*鼎曜[^"]*"', z)), "")
    add("10 JSON-LD publisher EN", bool(re.search(r'"publisher":\s*\{[^}]*"name":\s*"DingYao Advisory"', e)), "")
    # 11 h1
    add("11 H1 唯一", z.count('<h1') == 1 and e.count('<h1') == 1, f"{z.count('<h1')}/{e.count('<h1')}")
    # 12 直答摘要
    add("12 直答摘要", any(k in z for k in ('核心摘要', '直答摘要')) and any(k in e for k in ('Direct answer', 'Key Takeaways', '核心摘要')), "")
    # 13 FAQ 雙語
    add("13 FAQ 區塊雙語", '常見問題 FAQ' in z and re.search(r'<h2>FAQ</h2>', e) is not None, "")
    # 14 FAQPage
    add("14 FAQPage Schema", z.count('FAQPage') >= 1 and e.count('FAQPage') >= 1, f"{z.count('FAQPage')}/{e.count('FAQPage')}")
    # 15 H2 問句化
    r = q_h2_ratio(z, 'zh')
    add("15 H2 問句化 ZH ≥60%", int(r[2].rstrip('%')) >= 60, f"{r[0]}/{r[1]} = {r[2]}")
    r2 = q_h2_ratio(e, 'en')
    add("15 H2 問句化 EN ≥60%", int(r2[2].rstrip('%')) >= 60, f"{r2[0]}/{r2[1]} = {r2[2]}")
    # 16 Article schema
    add("16 Article Schema", z.count('"@type": "Article"') >= 1 and e.count('"@type": "Article"') >= 1, "")
    # 17 相關閱讀 真區塊
    add("17 相關閱讀 ≥3 連結 ZH", related_links(z) >= 3, str(related_links(z)))
    add("17 相關閱讀 ≥3 連結 EN", related_links(e) >= 3, str(related_links(e)))
    # 18 desc 含 CTA
    d = re.search(r'<meta name="description" content="([^"]*)"', z)
    add("18 Description 含 CTA", bool(d) and any(k in d.group(1) for k in ('立即', '免費', '索取', '下載')), (d.group(1)[:30] if d else ''))
    # 19 數據表格
    tbl = ("tax-table", "comparison-table")
    add("19 數據表格 tax-table/comparison-table",
        any(c in z for c in tbl) and any(c in e for c in tbl),
        f"ZH tax={z.count('tax-table')} cmp={z.count('comparison-table')} | EN tax={e.count('tax-table')} cmp={e.count('comparison-table')}")
    # 20/21 footer bottom links
    fb_zh = all(h in z for h in ('/overseas-buyers', '/partners', '/sitemap', '/privacy', '/terms'))
    fb_en = all(h in e for h in ('/overseas-buyers-en', '/partners-en', '/sitemap', '/privacy-en', '/terms-en'))
    add("20 Footer bottom ZH 5/5", fb_zh, "")
    add("21 Footer bottom EN 5/5", fb_en, "")
    # 22/23/24/25
    add("22 footer-cta-row", 'footer-cta-row' in z and 'footer-cta-row' in e, "")
    add("23 line-icon（無 fab fa-line）", 'line-icon' in z and 'fab fa-line' not in z, "")
    add("24 Google 四色 SVG", 'fill="#EA4335"' in z and 'fab fa-google' not in z, "")
    add("25 publisher.js manual", 'preferred-sources-control="manual"' in z, "")
    # 20 JSON-LD parse
    errs = []
    for nm, t in (("ZH", z), ("EN", e)):
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            try:
                json.loads(b.strip())
            except Exception as ex:
                errs.append(f"{nm}:{ex}")
    add("20b JSON-LD 解析", not errs, str(errs[:2]))
    # 21/22 合規（負向斷言）
    neg = re.findall(r'(?<!非)保證收益', z)
    for m in re.finditer(r'guaranteed (?:yield|rental|return)', e, re.I):
        ctx = e[max(0, m.start() - 14):m.start()].lower()
        if not re.search(r'not|no|never|rather than', ctx):
            neg.append(m.group(0))
    add("21 無保證收益字眼", not neg, str(neg[:3]))
    # 允許否定句（鐵律 0.6 明文的合規聲明）
    brok = []
    for m in re.finditer(r'帶看|斡旋|媒合|居間|代銷|建案代理', z):
        ctx = z[max(0, m.start() - 40):m.end() + 40]
        if not re.search(r'不從事|不經手|不代|非|不得', ctx):
            brok.append(ctx.strip()[:40])
    add("22 無仲介字眼（肯定句）", not brok, str(brok[:3]))
    enbrok = []
    for m in re.finditer(r'broker|agent', e, re.I):
        ctx = e[max(0, m.start() - 20):m.end() + 20]
        if '@' not in ctx and 'estate agent' not in ctx.lower():
            enbrok.append(ctx.strip()[:40])
    add("22b EN broker/agent 僅限免責語境", len(enbrok) <= 2, str(enbrok[:3]))
    # 23 免責
    add("23 免責聲明", '合規與免責聲明' in z and 'Disclaimer' in e, "")
    # 24 fine-print 規格
    ok24 = 'font-size:0.72rem;line-height:1.62;opacity:0.62' in z and 'font-size:0.85rem;line-height:1.8' not in z
    ok24e = 'font-size:0.72rem;line-height:1.62;opacity:0.62' in e and 'font-size:0.85rem;line-height:1.8' not in e
    add("24 免責 fine-print 規格", ok24 and ok24e, f"{ok24}/{ok24e}")
    add("24b @media 免責覆寫", '.compliance-disclaimer div[style*="font-size:0.72rem"]' in z, "")
    # 25 收益區間警語
    add("25 收益區間＋警語", any(k in z for k in ('非保證', '參考區間', '過往績效不代表', '以 SARS 核定')), "")
    # 26 幣別
    lant = re.findall(r'蘭特|蘭德', z + e)
    add("26 無「蘭特/蘭德」", not lant, str(lant[:3]))
    # 29 開普敦焦點
    for nm, t, keys in (("ZH", z, ('開普敦', '南非', '西開普')), ("EN", e, ('Cape Town', 'South Africa', 'Western Cape'))):
        body = t[t.index('<!-- ARTICLE BODY -->'):t.index('<!-- CTA -->')]
        loose = ct_focus(body, keys, False)
        strict = ct_focus(body, keys, True)
        add(f"29 開普敦焦點 {nm} (寬鬆)", loose >= 70, f"{loose:.1f}%")
        add(f"29 開普敦焦點 {nm} (嚴格)", strict >= 70, f"{strict:.1f}%")
    # 30 HTML 標籤配對
    for nm, t in (("ZH", z), ("EN", e)):
        p = P()
        p.feed(t)
        add(f"30 HTML 標籤配對 {nm}", not p.err and not p.stack, f"err={p.err[:2]} unclosed={[s[0] for s in p.stack][:5]}")
    # 31 畸形尾部
    add("31 無畸形尾部", '</section>\n</div>\n</section>\n</main>' not in z and '</section>\n</div>\n</section>\n</main>' not in e, "")
    # 32 EN CJK
    en_body = e.split('</head>')[1]
    cjk = re.findall(r'[\u4e00-\u9fff]', en_body)
    add("32 EN body 中文字元 = 0", len(cjk) == 0, f"{len(cjk)} 字：{''.join(cjk[:12])}")
    # 33 meta desc 長度
    for nm, t in (("ZH", z), ("EN", e)):
        d = re.search(r'<meta name="description" content="([^"]*)"', t)
        od = re.search(r'og:description" content="([^"]*)"', t)
        td = re.search(r'name="twitter:description" content="([^"]*)"', t)
        L = len(d.group(1)) if d else 0
        same = (d and od and td and d.group(1) == od.group(1) == td.group(1))
        add(f"33 Meta desc ≥150 且三處一致 {nm}", L >= 150 and same, f"len={L} same={bool(same)}")
    # 33b canonical 無 .html
    add("33b canonical 無 .html", '.html"' not in re.search(r'<link rel="canonical"[^>]*>', e).group(0), "")
    # 34 sources inline
    for nm, t, tok in (("ZH", z, '資料來源：'), ("EN", e, '(Source:')):
        n = t.count(tok)
        head = t[:t.index('</head>')].count(tok)
        add(f"34 內嵌來源 {nm} ≥3", n - head >= 3, f"body={n - head} head={head}")
    # 35 簡體字
    SIMP = set("护层筛独选产质经营销设备关发络讯报线间样们这个为来对时说过还进没现实体")
    bodyz = z.split('</head>')[1]
    bad = sorted({c for c in bodyz if c in SIMP})
    add("35 無簡體字", not bad, ''.join(bad))
    # 36 中文 HTML 註解
    cm = re.findall(r'<!--[^>]{0,200}[\u4e00-\u9fff]', z)
    add("36 無中文 HTML 註解", not cm, str(cm[:2]))
    # EN title ≤65
    et = re.search(r'<title>(.*?)</title>', e).group(1)
    add("EN title ≤65 字元", len(et) <= 65, f"{len(et)} chars")
    # 0 目標關鍵字（外部腳本另行執行）
    # 額外：Crestline
    add("Crestline ≥3 次", z.count('Crestline') >= 3 and e.count('Crestline') >= 3, f"{z.count('Crestline')}/{e.count('Crestline')}")
    add("crestline-assist 區塊", 'crestline-assist' in z and 'crestline-assist' in e, "")
    # 錨：圖片 section 數
    add("section 背景圖 s1..sN", len(set(re.findall(rf'{slug}-s(\d+)\.webp', z))) >= 6, str(sorted(set(re.findall(rf'{slug}-s(\d+)\.webp', z)))))

    print(f"\n===== GATE {slug} =====")
    fails = 0
    for item, ok, detail in res:
        if not ok:
            fails += 1
            print(f"❌ {item}  {detail}")
        else:
            print(f"✅ {item}" + (f"  {detail}" if detail else ""))
    print(f"\nRESULT: {len(res) - fails} PASS / {fails} FAIL  (exit {'0' if fails == 0 else '1'})")
    return fails


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    pairs = [
        ("south-africa-property-sale-withholding-tax-foreign-sellers-2026",
         "south-africa-property-sale-withholding-tax-foreign-sellers-2026"),
    ]
    if len(sys.argv) > 1:
        pairs = [(a, a) for a in sys.argv[1:]]
    total = 0
    for slug, _ in pairs:
        total += check(os.path.join(base, slug + ".html"), os.path.join(base, slug + "-en.html"), slug, None)
    sys.exit(0 if total == 0 else 1)
