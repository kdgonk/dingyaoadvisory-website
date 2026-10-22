#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quality gate for south-africa-boarding-school-admission-timeline-2026 (ZH+EN).
Implements dingyao-quality-gate Gate 1 (24+ items) + article-protocol iron laws.
Run: python3 runs/2026-10-21/gate.py
"""
import json, re, sys, pathlib
from html.parser import HTMLParser

REPO = pathlib.Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "2026-10-21"
SLUG = "south-africa-boarding-school-admission-timeline-2026"
ZH = RUN / (SLUG + ".html")
EN = RUN / (SLUG + "-en.html")
zh = ZH.read_text(encoding="utf-8")
en = EN.read_text(encoding="utf-8")

results = []
def chk(no, name, ok, detail=""):
    results.append((no, name, bool(ok), detail))

# 1 Tailwind
TAIL = r'border-l-4|text-yellow-400|bg-white/|border-gray-700|pl-6 mb-6|text-gray-300|rounded-lg|backdrop-blur-xl'
chk(1, "Tailwind class = 0", not re.search(TAIL, zh) and not re.search(TAIL, en),
    f"ZH {len(re.findall(TAIL, zh))} / EN {len(re.findall(TAIL, en))}")

# 2 Font Awesome integrity
FA = 'sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA=='
chk(2, "Font Awesome integrity format", FA + '" crossorigin' in zh and FA + '" crossorigin' in en)

# 3/4 Nav: 實站 2026-10-20 起改為三支柱下拉 nav。驗「與現行模板 nav 區塊逐字相同」+ 9 個目的地存在。
def navblk(c):
    s = c.index('<nav class="navbar"')
    return c[s:c.index('</nav>', s) + 6]
def main_style(c):
    m = re.search(r'<style>(.*?)</style>', c, re.S)
    return m.group(1) if m else ""
ZH_TPL_TXT = (REPO / "dist/blog/taiwan-parents-choosing-south-africa-private-schools.html").read_text(encoding="utf-8")
EN_TPL_TXT = (REPO / "dist/blog/taiwan-parents-choosing-south-africa-private-schools-en.html").read_text(encoding="utf-8")
nav_zh_ok = navblk(zh) == navblk(ZH_TPL_TXT)
nav_en_ok = navblk(en) == navblk(EN_TPL_TXT)
dest_zh = ['/south-africa-bank-account', '/south-africa-property', '/education', '/platform',
           '/assets', '/overseas-buyers', '/retirement', '/residency', '/tour', '/blog', '/consultation']
dest_en = ['/south-africa-bank-account-en', '/south-africa-property-en', '/education-en', '/platform-en',
           '/assets-en', '/overseas-buyers-en', '/retirement-en', '/residency-en', '/tour-en', '/blog-en', '/consultation-en']
miss_zh = [d for d in dest_zh if f'href="{d}"' not in navblk(zh)]
miss_en = [d for d in dest_en if f'href="{d}"' not in navblk(en)]
chk(3, "Nav ZH == live template + 11 real destinations", nav_zh_ok and not miss_zh, f"identical={nav_zh_ok} miss={miss_zh}")
chk(4, "Nav EN == live template + 11 real destinations", nav_en_ok and not miss_en, f"identical={nav_en_ok} miss={miss_en}")

# 5 social icons
ICONS = ['fab fa-facebook-f','fab fa-instagram','fab fa-x-twitter','fab fa-linkedin-in','fab fa-threads','fab fa-youtube']
chk(5, "Footer 6 social icons", all(i in zh for i in ICONS) and all(i in en for i in ICONS))

# 6 CSS braces
chk(6, "CSS braces balanced", zh.count('{')==zh.count('}') and en.count('{')==en.count('}'),
    f"ZH {zh.count('{')}/{zh.count('}')} EN {en.count('{')}/{en.count('}')}")

# 7 hero slug consistency (4-5 places)
def hero_refs(c):
    return {
      'hero img': re.findall(r'<img src="([^"]+)"[^>]*class="hero-bg-img"', c),
      'og:image': re.findall(r'property="og:image" content="([^"]+)"', c),
      'twitter:image': re.findall(r'name="twitter:image" content="([^"]+)"', c),
      'jsonld image': re.findall(r'"image":\s*"([^"]+)"', c),
    }
_refs = [(k, x) for c in (zh, en) for k, v in hero_refs(c).items() for x in v]
ok7 = bool(_refs) and all(SLUG + "-hero.webp" in x for _, x in _refs) and len(_refs) == 8
chk(7, "Hero slug consistent (img/og/twitter/jsonld)", ok7)

# 8 og:image webp
chk(8, "og:image is .webp", all('.webp' in u for u in re.findall(r'property="og:image" content="([^"]+)"', zh+en)))

# 9 EN DOM mirror: main <style> block identical
zs, es = main_style(zh), main_style(en)
chk(9, "EN mirror: same <style> count & main block", zh.count('<style')==en.count('<style') and zs==es,
    f"style tags ZH {zh.count('<style')} EN {en.count('<style')}; main-block equal={zs==es}")

# 10 publisher name
okzh = bool(re.search(r'"publisher":\s*\{[^}]*"name":\s*"鼎曜國際顧問 DingYao Advisory"', zh, re.S))
oken = bool(re.search(r'"publisher":\s*\{[^}]*"name":\s*"DingYao Advisory"', en, re.S))
chk(10, "JSON-LD publisher name per language", okzh and oken)

# 11 FAQ blocks
chk(11, "FAQ block both languages", '<h2>常見問題 FAQ</h2>' in zh and '<h2>FAQ</h2>' in en)

# 12 FAQPage schema
chk(12, "FAQPage schema both", zh.count('FAQPage')>=1 and en.count('FAQPage')>=1,
    f"ZH {zh.count('FAQPage')} EN {en.count('FAQPage')}")

# 13 H2 question ratio (exclude FAQ / related)
def h2_ratio(c, qmark, exclude):
    h2 = re.findall(r'<h2[^>]*>(.*?)</h2>', c, re.S)
    body = [re.sub(r'<[^>]+>','',x).strip() for x in h2]
    content = [x for x in body if x not in exclude and '主導覽' not in x]
    q = [x for x in content if qmark in x]
    return len(q), len(content), content
zq, zt, zlist = h2_ratio(zh, '？', {'常見問題 FAQ','相關閱讀','為什麼要透過 Crestline Advisory 協助？'})
eq, et, elist = h2_ratio(en, '?', {'FAQ','Related reading','Why Handle This Through Crestline Advisory?'})
chk(13, "H2 questionized >=60%", zq/zt>=0.6 and eq/et>=0.6, f"ZH {zq}/{zt}, EN {eq}/{et}")

# 14 footer bottom links
fb_zh = re.search(r'<div class="footer-bottom-links">(.*?)</div>', zh, re.S)
fb_en = re.search(r'<div class="footer-bottom-links">(.*?)</div>', en, re.S)
z_need = ['/overseas-buyers','/partners','/sitemap','/privacy','/terms']
e_need = ['/overseas-buyers-en','/partners-en','/sitemap','/privacy-en','/terms-en']
chk(14, "Footer bottom links ZH 5/5", fb_zh and all(x in fb_zh.group(1) for x in z_need),
    fb_zh.group(1)[:120] if fb_zh else "block missing")
chk(15, "Footer bottom links EN 5/5", fb_en and all(x in fb_en.group(1) for x in e_need),
    fb_en.group(1)[:120] if fb_en else "block missing")

# 16-19
chk(16, "footer-cta-row", 'footer-cta-row' in zh and 'footer-cta-row' in en)
chk(17, "line-icon used, no fab fa-line", 'line-icon' in zh and 'fab fa-line' not in zh)
chk(18, "Google 4-colour SVG", 'fill="#EA4335"' in zh and 'fab fa-google' not in zh)
chk(19, "publisher.js manual mode", 'preferred-sources-control="manual"' in zh and 'preferred-sources-control="manual"' in en)

# 20 JSON-LD parse
errs = []
for name, c in (("ZH",zh),("EN",en)):
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', c, re.S)
    for i,b in enumerate(blocks):
        try: json.loads(b.strip())
        except Exception as e: errs.append(f"{name}#{i}: {e}")
chk(20, "JSON-LD parses (all blocks)", not errs, str(errs))

# 21 guarantee wording (context aware)
GUAR = ['保證收益','資金絕對安全','保本','穩賺','零風險','終身被動收入','實際收益可能更高']
g_hits = [g for g in GUAR if g in zh]
en_g = re.findall(r'(?<!not )guaranteed (?:yield|rental|return)', en, re.I)
chk(21, "No guarantee claims", not g_hits and not en_g, f"ZH {g_hits} EN {en_g}")

# 22 broker words (context aware)
BROKER = ['帶看','斡旋','媒合','居間','代銷','建案代理']
b_hits = []
for w in BROKER:
    for m in re.finditer(w, zh):
        ctx = zh[max(0,m.start()-25):m.end()+25]
        if '不從事' in ctx or '不經手' in ctx: continue
        b_hits.append(f"{w}: {ctx}")
chk(22, "No broker-service wording (non-negated)", not b_hits, str(b_hits[:3]))

# 23/24 disclaimer
chk(23, "Disclaimer block ZH/EN", '合規與免責聲明' in zh and 'Disclaimer' in en)
chk(24, "Disclaimer fine-print spec", 'font-size:0.72rem;line-height:1.62;opacity:0.62' in zh
    and 'font-size:0.85rem;line-height:1.8' not in zh
    and 'font-size:0.76rem!important' in zh)

# 25 range wording present
chk(25, "Figures given as ranges + caveat",
    ('非保證' in zh or '市場參考' in zh or '公告值' in zh) and ('not a guarantee' in en or 'roughly' in en))

# 26 currency wording
chk(26, "No 蘭特/蘭德", '蘭特' not in zh and '蘭德' not in zh)
chk(26.5, "No NTD conversion of ZAR", '台幣' not in zh and 'NT$' not in zh)

# interest-rate discipline (土星人 🟡 rule)
bad_rate = [x for x in ['定存','7.72','8.15','8.75','4.0-6.05','7.10-7.45','6.5%'] if x in zh+en]
chk("R", "No deposit-rate claims", not bad_rate, str(bad_rate))

# 27 related links real block
def related(c, h2):
    m = re.search(r'<h2[^>]*>\s*%s\s*</h2>(.*?)(?=<h2|</article|</main>|$)' % re.escape(h2), c, re.S)
    if not m: return 0
    return len(re.findall(r'href="/blog/', m.group(1)))
zn, enn = related(zh,'相關閱讀'), related(en,'Related reading')
chk(27, "Related-reading real block >=3 links", zn>=3 and enn>=3, f"ZH {zn} EN {enn}")

# 28 target keywords verbatim
zh_kw = ['南非寄宿學校','南非私立學校','南非留學','南非國際學校']
en_kw = ['south africa boarding school','south africa private school fees','hilton college','michaelhouse']
zmiss = [k for k in zh_kw if k not in zh.lower()]
emiss = [k for k in en_kw if k not in en.lower()]
chk(28, "Target keywords verbatim", not zmiss and not emiss, f"ZH miss {zmiss} EN miss {emiss}")

# 29 Cape Town focus (loose + strict)
def focus(c, keys, start='<!-- ARTICLE BODY -->', end='<!-- CTA -->', strict=False):
    body = c[c.index(start):c.index(end)]
    pat = r'<p(?:\s[^>]*)?>(.*?)</p>' if strict else r'<p[^>]*>(.*?)</p>'
    paras = [re.sub(r'<[^>]+>','',p).strip() for p in re.findall(pat, body, re.S)]
    paras = [p for p in paras if len(p) > 40]
    w = sum(len(p) for p in paras)
    hit = sum(len(p) for p in paras if any(k in p for k in keys))
    return hit/w*100 if w else 0
z_loose = focus(zh, ('開普敦','南非','西開普'))
e_loose = focus(en, ('Cape Town','South Africa','Western Cape'))
z_strict = focus(zh, ('開普敦','南非','西開普'), strict=True)
e_strict = focus(en, ('Cape Town','South Africa','Western Cape'), strict=True)
chk(29, "Cape Town/SA focus >=70% (loose+strict)", min(z_loose,e_loose)>=70 and min(z_strict,e_strict)>=70,
    f"ZH {z_loose:.1f}/{z_strict:.1f}  EN {e_loose:.1f}/{e_strict:.1f}")

# 30 HTMLParser tag pairing
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr','path','svg','circle','g'}
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack=[]; self.err=[]
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        self.stack.append((tag, self.getpos()))
    def handle_endtag(self, tag):
        if tag in VOID: return
        if not self.stack: self.err.append(f'stray </{tag}>'); return
        if self.stack[-1][0] != tag:
            self.err.append(f'mismatch </{tag}> expected </{self.stack[-1][0]}> at {self.getpos()}')
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]; return
        else:
            self.stack.pop()
ok30 = True; det30 = []
for name, c in (("ZH",zh),("EN",en)):
    p = P(); p.feed(c)
    if p.err or p.stack:
        ok30 = False; det30.append(f"{name}: err={p.err[:3]} unclosed={[t for t,_ in p.stack][:5]}")
chk(30, "HTML tag pairing", ok30, " | ".join(det30))

# 31 malformed tail
chk(31, "No inherited malformed tail", '</section>\n</div>\n</section>\n</main>' not in zh
    and '</section>\n</div>\n</section>\n</main>' not in en)

# 32 EN CJK = 0 (whole file incl. head)
cjk = re.findall(r'[\u4e00-\u9fff]', en)
chk(32, "EN file contains zero CJK", not cjk, "".join(sorted(set(cjk)))[:40])

# 33 meta description
def descs(c):
    d = re.search(r'<meta name="description" content="([^"]*)"', c)
    o = re.search(r'property="og:description" content="([^"]*)"', c)
    t = re.search(r'name="twitter:description" content="([^"]*)"', c)
    return [x.group(1) if x else None for x in (d,o,t)]
zd, ed = descs(zh), descs(en)
chk(33, "Meta desc 150-320 & 3 places identical",
    all(x and 150 <= len(x) <= 320 for x in zd) and all(x and 150 <= len(x) <= 320 for x in ed)
    and zd[0]==zd[1]==zd[2] and ed[0]==ed[1]==ed[2],
    f"ZH {[len(x or '') for x in zd]} EN {[len(x or '') for x in ed]}")
chk("33b", "EN canonical has no .html", not re.search(r'canonical" href="[^"]*\.html"', en))

# 34 inline sources
def src_split(c, patt):
    head, body = c.split("</head>", 1)
    return c.count(patt), head.count(patt), body.count(patt)
zs_ = src_split(zh, "資料來源："); es_ = src_split(en, "(Source:")
chk(34, "Inline sources >=3 per language (body)", zs_[2]>=3 and es_[2]>=3, f"ZH {zs_} EN {es_}")

# 35 simplified chars (conservative list: never valid in Traditional)
SIMP = set("护层筛独选产质经营销设备关发络讯报线间样们这个为来对时说过还进没现实体")
body_zh = zh.split("</head>",1)[1]
bad35 = sorted({c for c in body_zh if c in SIMP} | {c for c in zh.split("</head>",1)[0] if c in SIMP})
chk(35, "No simplified characters (ZH)", not bad35, "".join(bad35))

# 36 Chinese HTML comments
cmts = re.findall(r'<!--[^>]{0,200}[\u4e00-\u9fff]', zh)
chk(36, "No Chinese HTML comments", not cmts, str([c[:40] for c in cmts[:3]]))

# 37 title lengths
zt = re.search(r'<title>(.*?)</title>', zh, re.S).group(1)
et = re.search(r'<title>(.*?)</title>', en, re.S).group(1)
chk(37, "EN title <=60 chars, ZH present", len(et) <= 60 and len(zt) <= 60, f"ZH {len(zt)} EN {len(et)}")

# 38 language-law 0.11 pricing framing
BAD011 = re.findall(r'雖然.{0,6}費用.{0,6}高|費用.{0,4}不便宜|價格.{0,4}偏高|比台灣便宜|便宜很多|不妨試試|可以試試|試試看', zh)
BAD011e = re.findall(r'(?i)although (the )?(fee|cost|price) is high|not cheap|on the expensive side|much cheaper than|far cheaper|give it a try|you can try', en)
chk(38, "Pricing-language framing (iron law 0.11)", not BAD011 and not BAD011e, f"{BAD011} {BAD011e}")

# 39 Crestline assist block
chk(39, "Crestline assist block (>=3 mentions + id)", zh.count('Crestline')>=3 and en.count('Crestline')>=3
    and 'crestline-assist' in zh and 'crestline-assist' in en,
    f"ZH {zh.count('Crestline')} EN {en.count('Crestline')}")

# 40 hreflang bidirectional
hre_ok = all(f'hreflang="{l}" href="https://dingyaoadvisory.tw/blog/{SLUG}{s}"' in zh
             for l,s in (('zh-TW',''),('en','-en'),('x-default',''))) and \
         all(f'hreflang="{l}" href="https://dingyaoadvisory.tw/blog/{SLUG}{s}"' in en
             for l,s in (('zh-TW',''),('en','-en'),('x-default','')))
chk(40, "hreflang bidirectional (zh-TW/en/x-default)", hre_ok)

# 41 no .html internal links
chk(41, "No .html in internal links", not re.search(r'href="/[^"]*\.html"', zh+en))

# 42 table count
chk(42, "Data tables (tax-table) >=1", zh.count('<table class="tax-table">')>=2 and en.count('<table class="tax-table">')>=2,
    f"ZH {zh.count('tax-table')} EN {en.count('tax-table')}")

# 43 H1 uniqueness
chk(43, "H1 unique", zh.count('<h1')==1 and en.count('<h1')==1)

# 44 direct-answer summary
chk(44, "Direct-answer highlight box", '核心摘要' in zh and 'Key summary' in en)


# 45 template residue (old slug / old title) = 0
OLD_SLUG = "taiwan-parents-choosing-south-africa-private-schools"
res = []
for c in (zh, en):
    for m in re.finditer(re.escape(OLD_SLUG), c):
        if c[max(0, m.start()-6):m.start()] != "/blog/":   # only legitimate internal links may cite the old slug
            res.append(c[max(0, m.start()-40):m.end()])
    for t in ("為什麼越來越多的台灣家長選擇南非頂級私校", "Why Taiwanese Parents Choose SA Private Schools"):
        if t in c:
            res.append(t)
chk(45, "No template residue (old slug only as internal link)", not res, str(res))

# 46 sr-only outline H2 == new H1 (a11y outline must not carry old topic)
sr_zh = re.search(r'<h2 class="sr-only">(.*?)</h2>', zh)
sr_en = re.search(r'<h2 class="sr-only">(.*?)</h2>', en)
zh_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', zh, re.S).group(1)
en_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', en, re.S).group(1)
chk(46, "sr-only outline H2 matches H1", sr_zh and sr_en and sr_zh.group(1) == zh_h1 and sr_en.group(1) == en_h1,
    f"ZH={sr_zh.group(1)[:30] if sr_zh else None} EN={sr_en.group(1)[:30] if sr_en else None}")

# 47 BreadcrumbList last item name == H1
def bc(c):
    m = re.search(r'"@type": "BreadcrumbList".*?\]', c, re.S)
    if not m: return None
    names = re.findall(r'"name": "([^"]+)"', m.group(0))
    return names[-1] if names else None
chk(47, "Breadcrumb name == H1", bc(zh) == zh_h1 and bc(en) == en_h1, f"ZH={bc(zh)} EN={bc(en)}")


# 48 cross-language leak: EN article must not link to ZH blog/static URLs (footer bottom links除外)
body_en = en[en.index('<!-- ARTICLE BODY -->'):en.index('<!-- CTA -->')]
bad48 = [u for u in re.findall(r'href="(/blog/[^"#]+)"', body_en) if not u.endswith(("-en",))]
bad48 += [u for u in re.findall(r'href="(/education)"', body_en)]
chk(48, "EN article links only EN targets", not bad48, str(bad48))

# 49 ZH article must not link to -en targets
body_zh = zh[zh.index('<!-- ARTICLE BODY -->'):zh.index('<!-- CTA -->')]
bad49 = [u for u in re.findall(r'href="(/[^"#]+)"', body_zh) if u.endswith("-en") or "/blog/" in u and "-en" in u]
chk(49, "ZH article links only ZH targets", not bad49, str(bad49))

# report
fails = [r for r in results if not r[2]]
for no, name, ok, detail in results:
    print(f"{'✅' if ok else '❌'} [{no}] {name}" + (f"  — {detail}" if detail else ""))
print()
print(f"TOTAL {len(results)} checks | PASS {len(results)-len(fails)} | FAIL {len(fails)}")
sys.exit(1 if fails else 0)
