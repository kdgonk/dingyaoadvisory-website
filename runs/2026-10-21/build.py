#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build ZH + EN article for slug south-africa-boarding-school-admission-timeline-2026
Base templates: live dist/blog/taiwan-parents-choosing-south-africa-private-schools{,-en}.html
Run: python3 runs/2026-10-21/build.py
"""
import json, re, pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
RUN = REPO / "runs" / "2026-10-21"
SLUG = "south-africa-boarding-school-admission-timeline-2026"
OLD = "taiwan-parents-choosing-south-africa-private-schools"
BASE = "https://dingyaoadvisory.tw/blog/"
IMG = "https://assets.dingyaoadvisory.tw/blog/images/"

ZH_TPL = REPO / "dist/blog" / (OLD + ".html")
EN_TPL = REPO / "dist/blog" / (OLD + "-en.html")

ZH_TITLE = "南非寄宿學校怎麼申請？2026 入學時程、監護與簽證 | 鼎曜國際顧問 DingYao Advisory"
ZH_H1 = "南非寄宿學校怎麼申請？頂級私校入學時程、監護安排與費用結構（2026）"
ZH_DESC = ("南非寄宿學校申請要提前約 18 個月：Hilton College 2028 年 Grade 8 註冊最晚在 Grade 6 開學前完成，"
           "Michaelhouse 2027 年入學已於 2026 年 1 月 31 日截止。本文整理頂級私校入學時程表、未成年學生簽證與在地監護人安排，"
           "以及寄宿費用的五個層次。立即預約免費評估，取得孩子的申請時程表。")
ZH_KW = ("南非寄宿學校, 南非私立學校, 南非留學, 南非國際學校, Hilton College, Michaelhouse, "
         "南非私校申請, 南非學生簽證, 南非監護人, 寄宿學校費用")

EN_TITLE = "South Africa Boarding School 2026: Admission Timeline"
EN_H1 = "How to Apply to a South Africa Boarding School: Admission Timeline, Guardianship and Fees (2026)"
EN_DESC = ("South Africa boarding school applications open 18 months ahead. Hilton College wants Grade 8 "
           "done by Grade 6. Get the timeline, guardian and visa steps.")

ZH_FAQ = [
    ("南非寄宿學校的註冊截止日是什麼時候？",
     "各校不同，但通則是 Grade 6 學年結束前。Hilton College 要求在 Grade 6 學年開始前完成線上註冊，整個流程約 18 個月；Michaelhouse 的 2027 年 Grade 8 註冊在 2026 年 1 月 31 日截止，之後一律進入候補名單。建議以入學年度往回推 18 個月作為自己的死線。"),
    ("申請南非寄宿學校需要考試或面試嗎？",
     "需要面試，部分學校另有評量。Michaelhouse 的 Grade 8 入學看過往學業表現、與 Rector 或 Deputy Rector 的個人面談、最近一份成績單，以及現任校長的機密推薦信；Hilton College 則設有僅限邀請的 Merit Award Assessment。面談通常在孩子 Grade 6 那年、家長陪同到校時進行。"),
    ("孩子在南非讀書，一定要有監護人嗎？",
     "法律上的監護權在父母身上，不會因住校轉移；但簽證端要求證明孩子在南非由誰負責照顧，並附住宿證明。實務上有三種做法：父或母陪讀（家長端需另行處理自己的停留身分）、經公證授權的在地親友、或學校認可的第三方監護服務。宿舍舍監負責生活管理，不是法律監護人。"),
    ("未成年學生的學生簽證需要哪些文件？",
     "除了一般學生簽證的錄取信、財力證明、醫療保險、體檢與 X 光報告、18 歲以上且停留超過 90 天者的警察紀錄證明之外，未成年人另需完整出生證明、雙方父母同意書、在地負責人與住宿證明。若一方父母失聯或已故，須以法院命令或死亡證明替代同意書。"),
    ("學生簽證要多久前申請？",
     "建議在入學前一年的 9 至 10 月送件。簽證必須早於第一學期開學日（南非學年 1 月中旬開始）核發，而簽證又必須先有學校錄取信；錄取通知多在入學前一年的 2 至 4 月發出，中間還留有文件公證、體檢與補件的時間。"),
    ("寄宿學校一年總花費大概多少？",
     "依兩校 2026 學年公告，年度學費加寄宿合計約 ZAR 417,000 至 441,766（2026 學年公告值，非保證未來年度相同）。但這只是第三層，還要加上不可退的註冊費與錄取費、外籍生押金（約一個半學期費用、可退），以及書籍、制服、保險與交通等外加項。完整比較請見文末內連。"),
]

EN_FAQ = [
    ("When is the registration deadline for a South Africa boarding school?",
     "It varies by school, but the rule of thumb is before the end of Grade 6. Hilton College asks for online registration to be complete before the Grade 6 year begins, with a process lasting about 18 months. Michaelhouse closed Grade 8 registration for 2027 entry on 31 January 2026, with later applications going to a waitlist. Work backwards 18 months from the intended entry year and treat that as your own deadline."),
    ("Do applicants need an exam or an interview?",
     "An interview, yes, and some schools add an assessment. Michaelhouse bases Grade 8 entry on previous academic performance, a personal interview with the Rector or Deputy Rector, the most recent school report and a confidential recommendation from the current headmaster. Hilton College runs an invitation-only Merit Award Assessment. The interview normally happens during the child's Grade 6 year, on the visit with parents."),
    ("Does a child studying in South Africa need a local guardian?",
     "Legal guardianship stays with the parents and does not move because the child boards, but the visa side requires evidence of who is responsible for the child in South Africa plus proof of accommodation. In practice: a parent accompanying the child (whose own permission to stay is a separate matter), a notarised authorisation to a relative or friend, or a school-approved third-party guardianship service. The housemaster manages boarding life, not legal guardianship."),
    ("What documents does a minor need for a study visa?",
     "Beyond the standard study visa pack (acceptance letter, proof of funds, medical scheme cover, medical and X-ray reports, and police clearance for applicants 18 and over staying beyond 90 days), a minor needs an unabridged birth certificate, consent from both parents, and evidence of the responsible adult and accommodation. If a parent is unreachable or deceased, a court order or death certificate replaces that consent."),
    ("How early should the study visa be lodged?",
     "September or October of the year before entry. The visa must be issued before Term 1 starts in mid-January, and it cannot be lodged without the school's acceptance letter; offers are typically released between February and April of the year before entry, leaving time for notarisation, medicals and any request for further documents."),
    ("What does a year at a boarding school cost in total?",
     "Based on the two schools' published 2026 figures, annual tuition plus boarding totals roughly ZAR 417,000 to 441,766 (2026 published rates, not a guarantee of future years). That is only the third layer: add the non-refundable registration and acceptance fees, the refundable foreign pupil's deposit of about one and a half terms, and extras such as books, uniform, insurance and travel. See the linked articles for the full comparison."),
]

# ---------------------------------------------------------------- crestline
ZH_CREST = """<section class="crestline-assist" id="crestline-assist">
  <div class="ca-inner">
    <h2>為什麼要透過 <span>Crestline Advisory</span> 協助？</h2>
    <p>南非學校與簽證端的要求每年都在調整，而且調整的往往是「格式」而不是「資格」—— 一樣的出生證明、一樣的同意書，格式不對就是退回。</p>
    <h3>自己辦最常卡住的三件事</h3>
    <ul>
      <li><strong>完整出生證明（unabridged）沒有先辦</strong>：只列一方父母的簡式版本通常不被接受，補辦要等原發證機關，而簽證其他文件全部引用這一份，順序錯了整包都要重排。</li>
      <li><strong>雙方父母同意書沒有公證</strong>：只簽名不公證是最常見的退件原因；一方父母在境外、失聯或已故時，必須改用法院命令或死亡證明，這一項沒有替代寫法。</li>
      <li><strong>監護人地址與宿舍地址對不上</strong>：兩者分屬不同省分時，要能說明學期中短假與 12 月長假孩子在哪裡，否則簽證端一定要求補件。</li>
    </ul>
    <p>透過我們的合作夥伴 Crestline Advisory（南非在地執行）協助，這些環節會在送件前先確認到位：</p>
    <ul>
      <li>文件格式逐項預檢，避免退回重送（一趟往返就是 2 到 4 週）</li>
      <li>依當期要求確認監護文件的公證與授權範圍寫法</li>
      <li>學校申請時程與簽證送件日先對齊，避免錄取後才發現來不及</li>
      <li>送件後由在地團隊追蹤進度，不用自己跨時區打電話</li>
    </ul>
    <p>鼎曜在台灣端負責確認你的資料與文件正確性，確認後轉交 Crestline Advisory 執行。你不會拿到一份「自己看著辦」的清單。</p>
    <div class="ca-cta"><a href="/consultation" class="btn btn-primary" title="預約 30 分鐘顧問評估">預約 30 分鐘顧問評估 <i class="fas fa-arrow-right"></i></a></div>
  </div>
</section>"""

EN_CREST = """<section class="crestline-assist" id="crestline-assist">
  <div class="ca-inner">
    <h2>Why Handle This Through <span>Crestline Advisory</span>?</h2>
    <p>South African school and visa requirements change every year — and what changes is usually the format, not the eligibility. Same birth certificate, same consent letter, wrong format, rejection.</p>
    <h3>The three most common failure points</h3>
    <ul>
      <li><strong>The unabridged birth certificate was not ordered first</strong>: An abridged version naming one parent is usually refused, and replacing it means waiting on the issuing authority — while every other visa document references it, so a wrong order resets the whole pack.</li>
      <li><strong>Parental consent was signed but not notarised</strong>: This is the single most common refusal reason. Where a parent is abroad, unreachable or deceased, a court order or death certificate must stand in — there is no substitute wording.</li>
      <li><strong>The guardian's address does not match the boarding house</strong>: When the two sit in different provinces, the child's location during mid-term breaks and the December holiday has to be explained, or the visa officer will request further documents.</li>
    </ul>
    <p>Working through our partner Crestline Advisory (on-the-ground execution in South Africa) means these are checked before submission:</p>
    <ul>
      <li>Document format pre-screened item by item (a round trip costs 2-4 weeks)</li>
      <li>Current notarisation and scope-of-authority wording confirmed for guardian documents</li>
      <li>School milestones aligned with the visa lodgement date, before an offer exposes a gap</li>
      <li>Progress tracked locally after submission, so you are not calling across time zones</li>
    </ul>
    <p>DingYao verifies your documents on the Taiwan side and hands over to Crestline Advisory for execution. You do not receive a checklist and left to figure it out alone.</p>
    <div class="ca-cta"><a href="/consultation-en" class="btn btn-primary" title="Book a 30-minute assessment">Book a 30-minute assessment <i class="fas fa-arrow-right"></i></a></div>
  </div>
</section>"""

ZH_CTA = """<section class="section cta-section">
  <div class="container">
    <div class="cta-content fade-in">
      <h2>為孩子排一張 <span class="gold">入學時間表</span></h2>
      <p>從註冊日往回推 18 個月，簽證、監護文件與住宿決策才來得及。立即預約諮詢，取得孩子的申請時程表與文件清單。</p>
      <a href="/consultation" class="btn btn-primary" title="預約諮詢">預約諮詢 <i class="fas fa-arrow-right"></i></a>
    </div>
  </div>
</section>"""

EN_CTA = """<section class="section cta-section">
  <div class="container">
    <div class="cta-content fade-in">
      <h2>Put Your Child's <span class="gold">Admission Timeline</span> on Paper</h2>
      <p>Work backwards 18 months from registration and the visa, guardian documents and accommodation decisions all still fit. Book a consultation for your child's timeline and document checklist.</p>
      <a href="/consultation-en" class="btn btn-primary" title="Book a consultation">Book a consultation <i class="fas fa-arrow-right"></i></a>
    </div>
  </div>
</section>"""


def jsonld(headline, desc, lang, faq):
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": desc,
        "image": IMG + SLUG + "-hero.webp",
        "author": {"@type": "Person", "name": "Scott Huang"},
        "publisher": {
            "@type": "Organization",
            "name": "鼎曜國際顧問 DingYao Advisory" if lang == "zh" else "DingYao Advisory",
            "url": "https://dingyaoadvisory.tw",
        },
        "datePublished": "2026-10-21",
        "dateModified": "2026-10-21",
        "mainEntityOfPage": {"@type": "WebPage", "@id": BASE + (SLUG if lang == "zh" else SLUG + "-en")},
    }
    faqpage = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq
        ],
    }
    return ('<script type="application/ld+json">\n' + json.dumps(article, ensure_ascii=False, indent=2) +
            '\n</script>\n\n<script type="application/ld+json">\n' +
            json.dumps(faqpage, ensure_ascii=False, indent=2) + '\n</script>\n\n')


def sub1(pattern, repl, text, flags=re.S):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    assert n == 1, f"pattern not matched: {pattern[:60]}"
    return new


def clean_comments(c):
    """Remove/strip CJK from HTML + CSS comments (gate 36 / EN CJK gate)."""
    def h(m):
        body = m.group(0)
        return "" if re.search(r'[\u4e00-\u9fff]', body) else body
    def s(m):
        body = m.group(0)
        return "" if re.search(r'[\u4e00-\u9fff]', body) else body
    # specific replacements keep intent visible
    c = c.replace("<!-- Crestline Advisory 導引（土星人 2026-10-20 政策） -->",
                  "<!-- Crestline Advisory guidance section -->")
    c = c.replace("/* ===== nav LOGO 白金版 + 三支柱下拉（2026-10-20） ===== */",
                  "/* ===== nav logo + three-pillar dropdown (2026-10-20) ===== */")
    c = c.replace("/* ===== footer brand 獨立結構（2026-10-20 第 6 批） ===== */",
                  "/* ===== footer brand block (2026-10-20, batch 6) ===== */")
    c = re.sub(r'<!--.*?-->', h, c, flags=re.S)
    c = re.sub(r'/\*.*?\*/', s, c, flags=re.S)
    return c


def align_css(en_html, zh_html):
    """Force EN main <style> block to be byte-identical to ZH (gate 9 DOM mirror)."""
    zs = re.search(r'<style>(.*?)</style>', zh_html, re.S).group(1)
    out, n = re.subn(r'<style>.*?</style>', lambda m: '<style>' + zs + '</style>',
                     en_html, count=1, flags=re.S)
    assert n == 1
    return out


def build(tpl_path, lang, title, desc, h1, keywords, body_parts, crest, cta, faq):
    src = tpl_path.read_text(encoding="utf-8")
    src = src.replace(OLD + "-en", SLUG + "-en").replace(OLD, SLUG)  # canonical/og:url/hero img
    src = src.replace(h1 if False else "\x00", "")  # no-op guard

    head, sep, tail = src.partition("<!-- ARTICLE HERO -->")
    assert sep, "hero marker missing"
    rest = sep + tail
    body_marker = "<!-- CTA -->"
    idx = rest.index(body_marker)
    tpl_body, tpl_tail = rest[:idx], rest[idx:]

    # --- head: title / desc / keywords / og / twitter
    head = sub1(r"<title>.*?</title>", f"<title>{title}</title>", head)
    head = sub1(r'<meta name="description" content="[^"]*">',
                f'<meta name="description" content="{desc}">', head)
    if lang == "zh":
        head = sub1(r'<meta name="keywords" content="[^"]*">',
                    f'<meta name="keywords" content="{keywords}">', head)
    else:
        head = re.sub(r'\s*<meta name="keywords" content="[^"]*">', "", head, count=1)
    head = sub1(r'<meta property="og:title" content="[^"]*">',
                f'<meta property="og:title" content="{h1}">', head)
    head = sub1(r'<meta property="og:description" content="[^"]*">',
                f'<meta property="og:description" content="{desc}">', head)
    head = sub1(r'<meta name="twitter:title" content="[^"]*">',
                f'<meta name="twitter:title" content="{h1}">', head)
    head = sub1(r'<meta name="twitter:description" content="[^"]*">',
                f'<meta name="twitter:description" content="{desc}">', head)
    # --- head: replace both JSON-LD blocks with new ones
    head = sub1(r'<script type="application/ld\+json">.*?</script>\s*\n\n(?=<link rel="preconnect")',
                lambda m: jsonld(h1, desc, lang, faq), head)

    # --- body
    body = "".join(p.read_text(encoding="utf-8") for p in body_parts)
    # --- tail: crestline + cta replacements
    tail = sub1(r'<section class="crestline-assist" id="crestline-assist">.*?</section>',
                lambda m: crest, tpl_tail)
    tail = sub1(r'<section class="section cta-section">.*?</section>',
                lambda m: cta, tail)

    return head + body + tail


def main():
    zh_parts = [RUN / "parts/zh-body-a.html", RUN / "parts/zh-body-c.html", RUN / "parts/zh-body-b.html"]
    en_parts = [RUN / "parts/en-body-a.html", RUN / "parts/en-body-c.html", RUN / "parts/en-body-b.html"]

    zh = build(ZH_TPL, "zh", ZH_TITLE, ZH_DESC, ZH_H1, ZH_KW, zh_parts, ZH_CREST, ZH_CTA, ZH_FAQ)
    en = build(EN_TPL, "en", EN_TITLE, EN_DESC, EN_H1, "", en_parts, EN_CREST, EN_CTA, EN_FAQ)

    zh = clean_comments(zh)
    en = align_css(clean_comments(en), zh)

    # residue sweep: template's a11y sr-only <h2> and BreadcrumbList still carry the old title
    for old, new in (
        ("為什麼越來越多的台灣家長選擇南非頂級私校？", ZH_H1),
        ("Why More Taiwanese Parents Are Choosing South Africa's Top Private Schools", EN_H1),
        ("Why Taiwanese Parents Choose SA Private Schools", EN_H1),
    ):
        zh = zh.replace(old, new)
        en = en.replace(old, new)

    # fix simplified typo found in ZH draft
    zh = zh.replace("必须先講清楚", "必須先講清楚")

    zp = RUN / (SLUG + ".html")
    ep = RUN / (SLUG + "-en.html")
    zp.write_text(zh, encoding="utf-8")
    ep.write_text(en, encoding="utf-8")
    print("ZH", zp, len(zh.encode()))
    print("EN", ep, len(en.encode()))


if __name__ == "__main__":
    main()
