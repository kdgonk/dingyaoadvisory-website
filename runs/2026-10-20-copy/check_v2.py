# -*- coding: utf-8 -*-
"""驗收：土星人 2026-10-20 服務頁驗收標準逐項實測。"""
import json, re, pathlib, hashlib

ROOT = pathlib.Path.home() / "Documents/DingYao-Website/dingyaoadvisory-website"
import sys
OUT = ROOT / "runs/2026-10-20-copy" / (sys.argv[1] if len(sys.argv) > 1 else "")
DIST = ROOT / "dist"

EXPECT = {
    "south-africa-bank-account.html": dict(
        title="南非銀行開戶完整指南｜外國人開戶流程與文件｜鼎曜國際顧問",
        canonical="https://dingyaoadvisory.tw/south-africa-bank-account",
        alt_zh="https://dingyaoadvisory.tw/south-africa-bank-account",
        alt_en="https://dingyaoadvisory.tw/south-africa-bank-account-en",
        base="residency.html", lang="zh",
        must_h2=["南非幣", "南非銀行開戶流程"],
        must_faq=["南非幣現在適合進場嗎", "飛南非開戶要待幾天"],
        h1_kw=["南非幣", "開戶"]),
    "south-africa-bank-account-en.html": dict(
        title="South Africa Bank Account for Foreigners | DingYao Advisory",
        canonical="https://dingyaoadvisory.tw/south-africa-bank-account-en",
        alt_zh="https://dingyaoadvisory.tw/south-africa-bank-account",
        alt_en="https://dingyaoadvisory.tw/south-africa-bank-account-en",
        base="residency-en.html", lang="en",
        must_h2=[], must_faq=[], h1_kw=[]),
    "south-africa-property.html": dict(
        title="南非置產顧問服務｜在地團隊陪同簽約與過戶｜鼎曜國際顧問",
        canonical="https://dingyaoadvisory.tw/south-africa-property",
        alt_zh="https://dingyaoadvisory.tw/south-africa-property",
        alt_en="https://dingyaoadvisory.tw/south-africa-property-en",
        base="residency.html", lang="zh",
        must_h2=["開普敦房產的租金報酬", "南非投資"],
        must_faq=["哪一區租金報酬最好"],
        h1_kw=["南非置產", "開普敦"]),
    "south-africa-property-en.html": dict(
        title="South Africa Property Advisory Services | DingYao Advisory",
        canonical="https://dingyaoadvisory.tw/south-africa-property-en",
        alt_zh="https://dingyaoadvisory.tw/south-africa-property",
        alt_en="https://dingyaoadvisory.tw/south-africa-property-en",
        base="residency-en.html", lang="en",
        must_h2=[], must_faq=[], h1_kw=[]),
}

ALLOWED_LOC = {"hero", "mid_section", "bottom_cta", "sticky_bar", "nav", "faq"}
SIMPLIFIED = "这们个银币户资产证转让汇额际开关门问题说应该为种经济风险选择购买卖价钱贷帐国内时间单价权税费"
CJK = re.compile(r"[\u4e00-\u9fff]")

rows = []
fails = []


def chk(cond, label, detail=""):
    rows.append(("PASS" if cond else "FAIL", label, detail))
    if not cond:
        fails.append(f"{label} — {detail}")


def strip_tags(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


for name, exp in EXPECT.items():
    p = OUT / name
    if not p.exists():
        print(f"\n----- {name}: 不在 {OUT}，略過 -----")
        continue
    h = p.read_text(encoding="utf-8")
    print(f"\n===== {name}  ({len(h):,} bytes) =====")

    # 1 title 逐字相同
    t = re.search(r"<title>(.*?)</title>", h, re.S).group(1)
    chk(t == exp["title"], "title 逐字相同", t)
    if exp["lang"] == "en":
        chk(len(t) <= 60, "EN title ≤60 字元", f"{len(t)}")
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    if exp["lang"] == "en":
        chk(150 <= len(desc) <= 160, "EN description 150–160 字元", f"{len(desc)}")
        od = re.search(r'property="og:description" content="([^"]*)"', h).group(1)
        td = re.search(r'name="twitter:description" content="([^"]*)"', h).group(1)
        chk(od == desc and td == desc, "EN description 三處同步", f"{len(od)}/{len(td)}")
    t2 = re.search(r'property="og:title" content="([^"]*)"', h).group(1)
    chk(t2 == exp["title"], "og:title 同步", t2[:40])
    tw = re.search(r'name="twitter:title" content="([^"]*)"', h).group(1)
    chk(tw == exp["title"], "twitter:title 同步", tw[:40])

    # 2 H1 恰好 1 個
    h1 = [strip_tags(x) for x in re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)]
    chk(len(h1) == 1, "H1 恰好 1 個", f"{len(h1)} → {h1}")

    # 3 六段 + H2 數
    main = h[h.index("<main"):h.index("</main>")]
    secs = re.findall(r'<section class="[^"]*" id="([a-z_]+)"', main)
    core = ["hero", "why", "process", "compare", "faq", "cta"]
    extra = [s for s in secs if s not in core]
    chk(secs[:6] == core and set(extra) <= {"booking"},
        "六段順序 hero→why→process→compare→faq→cta（允許泰坦人追加 booking）", str(secs))
    h2 = [strip_tags(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", main, re.S)]
    chk(len(h2) in (6, 7) and sum(1 for x in h2 if "Consultation" not in x) == 6,
        "H2 共 6 個（booking 區塊另計）", f"{len(h2)}：{h2}")

    # 4 內文字數
    txt = strip_tags(main)
    cjk = len(CJK.findall(txt))
    words = len(re.findall(r"[A-Za-z][A-Za-z'-]+", txt))
    if exp["lang"] == "zh":
        chk(1200 <= cjk <= 1800, "中文字數 1200–1800", f"{cjk} 字")
    else:
        chk(700 <= words <= 1400, "EN 對等篇幅（700–1400 words）", f"{words} words / {cjk} CJK")

    # 5 CTA
    ctas = re.findall(r"<a\b[^>]*href=\"/consultation\"[^>]*>", main)
    locs, ids, bad = [], [], []
    for c in ctas:
        i = re.search(r'data-cta-id="([^"]*)"', c)
        l = re.search(r'data-cta-location="([^"]*)"', c)
        if i:
            ids.append(i.group(1))
        if l:
            locs.append(l.group(1))
            if l.group(1) not in ALLOWED_LOC:
                bad.append(l.group(1))
    chk(len(ctas) >= 3, "CTA 三處以上", f"{len(ctas)} 處")
    chk(len(ids) == len(ctas) and len(locs) == len(ctas), "每個 CTA 都有 id + location", f"ids={ids} locs={locs}")
    chk(not bad, "location 值合法", str(bad))
    chk(len(set(locs)) == len(locs), "location 不重複（分得出位置）", str(locs))

    # 6 FAQ
    faq_block = main[main.index('class="faq-list"'):main.index('id="cta"')]
    qs = [strip_tags(x) for x in re.findall(r"<span>(.*?)</span>", faq_block, re.S)]
    ans = [strip_tags(x) for x in re.findall(r'<div class="faq-answer">\s*<p>(.*?)</p>', faq_block, re.S)]
    chk(6 <= len(qs) <= 8, "FAQ 6–8 題", f"{len(qs)} 題")
    chk(len(qs) == len(ans), "每題都有答案", f"{len(qs)} Q / {len(ans)} A")
    lens = [len(CJK.findall(a)) for a in ans]
    if exp["lang"] == "zh":
        badlen = [(q[:12], n) for q, n in zip(qs, lens) if not (60 <= n <= 120)]
        chk(not badlen, "每題答案 60–120 中文字", str(lens) + (f" 超出：{badlen}" if badlen else ""))

    # 7 JSON-LD 與頁面一致
    lds = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            lds.append(json.loads(m.group(1)))
        except Exception as e:
            chk(False, "JSON-LD 可解析", str(e))
    types = [x.get("@type") for x in lds]
    chk(all(k in types for k in ("FinancialService", "WebSite", "BreadcrumbList", "FAQPage")), "4 個 JSON-LD 齊全", str(types))
    faqld = next(x for x in lds if x.get("@type") == "FAQPage")["mainEntity"]
    chk(len(faqld) == len(qs), "JSON-LD 題數 = 頁面題數", f"{len(faqld)} vs {len(qs)}")
    mismatch = []
    for a, (q, aa) in zip(faqld, zip(qs, ans)):
        if a["name"].strip() != q.strip() or a["acceptedAnswer"]["text"].strip() != aa.strip():
            mismatch.append(q[:16])
    chk(not mismatch, "JSON-LD 問答逐字等於頁面", str(mismatch))

    # 8 canonical / hreflang
    can = re.search(r'<link rel="canonical" href="([^"]*)"', h).group(1)
    chk(can == exp["canonical"], "canonical 正確", can)
    hl = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h))
    chk(hl.get("zh-Hant") == exp["alt_zh"] and hl.get("en") == exp["alt_en"]
        and hl.get("x-default") == exp["alt_zh"], "hreflang 三條對稱", json.dumps(hl, ensure_ascii=False))
    chk(".html" not in can and ".html" not in "".join(hl.values()), "canonical/hreflang 無 .html", "")

    # 9 簡體 / 蘭特
    bad_s = sorted({c for c in h if c in SIMPLIFIED})
    chk(not bad_s, "無簡體字", "".join(bad_s))
    chk("蘭特" not in h, "無「蘭特」", "")

    # 10 關鍵字覆蓋
    for kw in exp["must_h2"]:
        chk(any(kw in x for x in h2), f"H2 覆蓋「{kw}」", str([x for x in h2 if kw in x]))
    for kw in exp["must_faq"]:
        chk(any(kw in q for q in qs), f"FAQ 覆蓋「{kw}」", "")
    for kw in exp["h1_kw"]:
        chk(kw in h1[0], f"H1 含「{kw}」", h1[0])
    if exp["lang"] == "zh":
        ct = len(re.findall("開普敦", txt))
        chk(ct >= 8, "開普敦（Cape Town）出現 ≥8 次", f"{ct} 次")
        paras = [strip_tags(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", main, re.S)]
        paras = [x for x in paras if len(x) > 25]
        ct_p = sum(1 for x in paras if "開普敦" in x)
        ratio = ct_p / max(1, len(paras))
        chk(ratio >= 0.40, "含開普敦的段落占比 ≥40%", f"{ct_p}/{len(paras)} = {ratio:.0%}")

    # 11 nav/footer 與樣板 byte-identical
    src = (DIST / exp["base"]).read_text(encoding="utf-8")
    for tag in ("header", "footer"):
        a = re.search(rf"<{tag}\b.*?</{tag}>", h, re.S).group(0)
        b = re.search(rf"<{tag}\b.*?</{tag}>", src, re.S).group(0)
        chk(hashlib.md5(a.encode()).hexdigest() == hashlib.md5(b.encode()).hexdigest(),
            f"{tag} 與樣板 byte-identical", hashlib.md5(a.encode()).hexdigest()[:8])

    # 12 內連存在
    links = re.findall(r'href="(/[^"#]*)"', main)
    missing = []
    for l in set(links):
        if l.startswith("/blog/"):
            if not (DIST / "blog" / (l.split("/blog/")[1] + ".html")).exists():
                missing.append(l)
        elif l == "/consultation":
            pass
        elif not (DIST / (l.strip("/") + ".html")).exists() and not (DIST / l.strip("/")).exists():
            missing.append(l)
    chk(not missing, "內連目標存在（無 404）", str(missing))

    # 13 無 Tailwind 污染
    tw = re.findall(r'class="[^"]*\b(?:text-(?:center|left|xl|sm)|px-\d|py-\d|mt-\d|mb-\d|grid-cols-\d|flex\b|justify-|items-)[^"]*"', main)
    chk(not tw, "無 Tailwind class 污染", str(tw[:3]))

print("\n" + "=" * 60)
print(f"總計 {len(rows)} 項：PASS {sum(1 for r in rows if r[0]=='PASS')} / FAIL {len(fails)}")
if fails:
    print("\nFAIL 明細：")
    for f in fails:
        print(" -", f)
else:
    print("\n全部通過 ✅")
for st, lab, det in rows:
    if st == "FAIL":
        print(f"{st} | {lab} | {det}")
