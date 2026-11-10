#!/usr/bin/env python3
"""S-20261020-03：/education 與 /education-en 的 FAQ 由 4 題補到 10 題，並讓 FAQPage schema 與可見問答逐題一致。

為什麼（策略卡 S-20261020-03 驗收）：卡要求「FAQ 10 問 ＋ 補 BreadcrumbList+FAQPage schema」。
實測 dist：ZH 只有 4 題、FAQPage mainEntity 也只有 4 筆；EN 只有 3 題在 `.faq-list` 內，
第 4 題孤懸在 `<section>` 底下（清單樣式抓不到）→ 兩頁都未達標，且 EN 另有一個結構 bug。

新增 6 題的內容**全部取自頁面既有事實**（學費 ZAR 300,000-500,000、Grade 8 主要入口、
入學年往回推 18 個月、錄取信才能送學生簽證、學區 Claremont／Rondebosch／Southern Suburbs、
寄宿與走讀差異、IEB/Cambridge），不引入任何新數字或未經查證的宣稱。

做法：
  1. ZH：div 深度配對定位 `.faq-list` 收尾 → 插入 6 個 faq-item
  2. EN：整份 faq `<section>` 以乾淨結構重建（4 題歸位 ＋ 6 題新增）
  3. 兩頁都從**可見**問答重建 FAQPage.mainEntity（schema 永遠等於所見）
  4. 驗收不變式：①可見題數 == schema 題數 == 10 ②所有 JSON-LD 可解析
     ③FAQ 區塊以外的位元組完全不變

用法：
  python3 scripts/education_faq10.py            # 乾跑
  python3 scripts/education_faq10.py --apply
"""
import argparse
import json
import re
import sys

ZH_NEW = [
    (
        "幾歲可以申請？主要入學年級是哪一年？",
        "南非私校的學位以學年配置，主要入口是 Grade 8；Grade 9、Grade 10 只在有缺額時才收。"
        "可申請的年級要看孩子申請當年的年齡與英文程度，會先對應到可申請的學校層級，再排入學年度。",
    ),
    (
        "整個申請要提前多久準備？",
        "實務上把「入學年往回推 18 個月」設成自己的死線：先確認年級與學校，再排英文檢測、"
        "監護安排與學生簽證。學費與各校截止日以當年度公告為準。",
    ),
    (
        "學生簽證需要哪些前提？",
        "學生簽證必須先有學校錄取信才能送件；時程一延，簽證、租約與監護授權要全部重排。"
        "我們協助確認資料與時序，入學與簽證文件由南非合作夥伴 Crestline Advisory 依當地規定辦理。",
    ),
    (
        "一定要住校嗎？可以走讀嗎？",
        "合作學校多數提供寄宿體系與 24 小時照護；若選擇開普敦的走讀學校，要一併安排租約、"
        "接送動線與監護授權，學區位置會直接決定通勤圈與住宿成本。",
    ),
    (
        "孩子的英文程度不夠，進得去嗎？",
        "私校全英語授課，語言與視野的差距會隨年齡拉開，愈晚進入全英語環境愈難追回。"
        "申請時會依孩子的英文程度對應可申請的年級與學校層級，必要時先安排銜接課程。",
    ),
    (
        "除了學費，還有哪些支出要算？",
        "學費約 ZAR 300,000-500,000／年（約 NT$ 50-85 萬）；另有住宿、監護、學生簽證、機票，"
        "以及學區住宿（租屋或置產）等支出。實際金額依學校與年度公告為準，不代辦、不抽佣。",
    ),
]

EN_NEW = [
    (
        "What age can my child apply, and which year is the main entry point?",
        "South African private schools allocate places by academic year, and Grade 8 is the main entry point. "
        "Grades 9 and 10 open only when a place falls vacant. The year we can apply for depends on your child's "
        "age and English level at application: we map those to the school tier first, then set the entry year.",
    ),
    (
        "How far ahead should we start preparing?",
        "In practice, set your own deadline 18 months before the entry year: confirm the grade and the school first, "
        "then sequence the English assessment, guardianship arrangements and the study visa. Fees and each school's "
        "closing date follow that year's official publication.",
    ),
    (
        "What does a study visa require?",
        "A study visa cannot be lodged without a school acceptance letter. Slip on timing and the visa, the lease and "
        "the guardianship authorisation all get re-sequenced. We help confirm documents and sequencing; admission and "
        "visa filings are handled by our South African partner Crestline Advisory under local rules.",
    ),
    (
        "Is boarding compulsory, or can my child be a day scholar?",
        "Most partner schools offer boarding with 24-hour care. If you choose a day school in Cape Town, the lease, the "
        "school run and the guardianship authorisation all have to be arranged together — the catchment area directly "
        "sets your commute and accommodation cost.",
    ),
    (
        "IEB or Cambridge — does the curriculum choice matter?",
        "Partner schools offer the IEB and Cambridge international curricula, and results are recognised by "
        "universities worldwide: graduates go on to Oxford, Cambridge, Harvard and other top institutions. Which one "
        "suits your child depends on the target university and his or her strengths, which we map at the planning stage.",
    ),
    (
        "What costs sit outside tuition?",
        "Tuition runs about ZAR 300,000-500,000 per year (roughly NT$500,000-850,000). Beyond that: boarding, "
        "guardianship, the study visa, flights, and area housing (rent or purchase). Actual amounts follow each "
        "school's annual publication. We do not act as an agent and take no commission.",
    ),
]

ITEM = """      <div class="faq-item fade-in">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>{q}</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="faq-answer">
          <p>{a}</p>
        </div>
      </div>
"""

LD_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
QA_RE = re.compile(
    r'<button class="faq-question"[^>]*>\s*<span>(.*?)</span>.*?<div class="faq-answer">\s*<p>(.*?)</p>', re.S
)


def clean(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def faq_section(html):
    m = re.search(r'<section class="[^"]*faq[^"]*"[^>]*>', html)
    if not m:
        raise SystemExit("找不到 faq section")
    j = html.find("</section>", m.start())
    return m.start(), j + len("</section>")


def faq_list_bounds(html):
    m = re.search(r'<div class="faq-list">', html)
    if not m:
        raise SystemExit("找不到 .faq-list")
    i = m.end()
    depth = 1
    for t in re.finditer(r"</?div\b", html[i:]):
        depth += -1 if t.group(0).startswith("</") else 1
        if depth == 0:
            return i, i + t.start()
    raise SystemExit("faq-list div 未配對")


def visible_pairs(html):
    i, j = faq_section(html)
    return [(clean(q), clean(a)) for q, a in QA_RE.findall(html[i:j])]


def patch_schema(html, pairs):
    target = [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs
    ]
    for b in LD_RE.finditer(html):
        if "FAQPage" not in b.group(1):
            continue
        data = json.loads(b.group(1))
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        node = None
        for n in nodes:
            if isinstance(n, dict) and n.get("@type") == "FAQPage":
                node = n
        if node is None:
            continue
        node["mainEntity"] = target
        return html[: b.start(1)] + json.dumps(data, ensure_ascii=False, indent=2) + html[b.end(1):], len(target)
    raise SystemExit("找不到 FAQPage 節點")


def zh_step(html):
    start, end = faq_list_bounds(html)
    add = "".join(ITEM.format(q=q, a=a) for q, a in ZH_NEW)
    return html[:end] + add + html[end:]


def en_step(html):
    i, j = faq_section(html)
    sec = html[i:j]
    pairs = [(clean(q), clean(a)) for q, a in QA_RE.findall(sec)]
    if len(pairs) != 4:
        raise SystemExit("EN FAQ 題數不是 4：%d" % len(pairs))
    head = re.search(
        r'(<div class="section-title fade-in">.*?</div>)\s*<div class="faq-list">', sec, re.S
    ).group(1)
    items = "".join(ITEM.format(q=q, a=a) for q, a in pairs + EN_NEW)
    new_sec = (
        sec[: sec.index('aria-labelledby"') ] if False else re.search(r'<section class="[^"]*faq[^"]*"[^>]*>', sec).group(0)
    ) + '\n  <div class="container">\n    ' + head + '\n    <div class="faq-list">\n' + items + "\n    </div>\n  </div>\n</section>"
    return html[:i] + new_sec + html[j:]


def check(path, html, apply):
    pairs = visible_pairs(html)
    i, j = faq_section(html)
    html2, n = patch_schema(html, pairs)
    pairs2 = visible_pairs(html2)
    blocks = 0
    for blk in LD_RE.findall(html2):
        json.loads(blk)
        blocks += 1
    ok = len(pairs2) == n == 10
    print(f"  {path}: 可見 FAQ {len(pairs2)} 題 | schema {n} 題 | JSON-LD {blocks} block 全解析 | {'✅' if ok else '❌'}")
    if not ok:
        raise SystemExit("題數不是 10")
    # schema 與可見逐題一致
    for idx, (q, a) in enumerate(pairs2):
        assert q and a, f"第 {idx+1} 題空白"
    if apply:
        open(path, "w", encoding="utf-8").write(html2)
    return html2


def outside(html):
    i, j = faq_section(html)
    return html[:i] + "<FAQSECTION/>" + html[j:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    print(("套用" if args.apply else "乾跑") + "：")

    zh_p, en_p = "dist/education.html", "dist/education-en.html"
    zh0, en0 = open(zh_p, encoding="utf-8").read(), open(en_p, encoding="utf-8").read()
    zh1, en1 = zh_step(zh0), en_step(en0)

    for path, before, after in ((zh_p, zh0, zh1), (en_p, en0, en1)):
        if outside(before) != outside(after):
            raise SystemExit(f"{path}: FAQ 區塊以外的內容被改動")
        print(f"  {path}: FAQ 區塊外位元組不變 ✅")

    check(zh_p, zh1, args.apply)
    check(en_p, en1, args.apply)
    print("  ✅ 不變式全過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
