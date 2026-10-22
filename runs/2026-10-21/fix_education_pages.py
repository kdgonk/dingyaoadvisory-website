import re, pathlib

D = pathlib.Path("/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist")

def patch(fn, pairs, must=True):
    p = D / fn; t = p.read_text(encoding="utf-8"); ok = 0
    for old, new in pairs:
        c = t.count(old)
        if c == 0 and must:
            print(f"   !! MISS {fn}: {old[:70]}")
        t = t.replace(old, new); ok += c
    p.write_text(t, encoding="utf-8")
    print(f"   {fn}: {ok} replacements")

# ---------------- ZH ----------------
zh_stats = [
 ('<span class="num danger-num">47%</span>\n            <span class="label">傳統白領職位將在 2030 年前被 AI 取代或重塑</span>',
  '<span class="num danger-num">AI</span>\n            <span class="label">入門級白領工作正被 AI 逐步重塑，重複性高的職務最先受影響</span>'),
 ('<span class="num">3.2×</span>\n            <span class="label">具國際教育背景者，全球頂尖企業錄取率高出 3.2 倍</span>',
  '<span class="num">視野</span>\n            <span class="label">國際學歷與跨文化經驗，是跨國企業篩選人才的實質加分項</span>'),
 ('<span class="num danger-num">85%</span>\n            <span class="label">亞洲家長承認孩子的英語能力不足以應付國際職場</span>',
  '<span class="num danger-num">門檻</span>\n            <span class="label">英語已從加分項變成基本門檻，不夠用時連面試都進不去</span>'),
 ('<span class="num">12 歲</span>\n            <span class="label">最佳留學起點年齡 — 錯過黃金期，語言與視野差距將難以追趕</span>',
  '<span class="num">愈早</span>\n            <span class="label">語言與視野的差距隨年齡拉開，愈晚進入全英語環境愈難追回</span>'),
 ('2026 年的今天，AI 已經取代了大量傳統白領工作。未來十年，只會考試、沒有國際視野、缺乏跨文化競爭力的孩子，將面臨前所未有的職場淘汰壓力。',
  '2026 年的今天，AI 正在快速重塑入門級白領工作。未來十年，只會考試、沒有國際視野、缺乏跨文化協作能力的孩子，會發現可選的路比上一代窄得多。'),
 ('<a href="#" class="btn btn-primary" title="立即預約教育諮詢">立即預約教育諮詢 <i class="fas fa-arrow-right"></i></a>',
  '<a href="/consultation?pillar=education" class="btn btn-primary" title="立即預約教育諮詢" data-cta-id="education-urgency" data-cta-location="bottom_cta">立即預約教育諮詢 <i class="fas fa-arrow-right"></i></a>'),
 ('<a href="#" class="btn-outline-danger" title="了解黃金留學時機">了解黃金留學時機 <i class="fas fa-clock"></i></a>',
  '<a href="#cost" class="btn-outline-danger" title="了解學費與申請時程">先看學費與申請時程 <i class="fas fa-clock"></i></a>'),
]

zh_cta = '''
<!-- EDUCATION MID CTA (2026-10-21) -->
<section class="section" id="cost-cta" style="padding-top:0">
  <div class="container">
    <div class="text-center fade-in" style="max-width:780px;margin:0 auto">
      <div class="gold-line"></div>
      <h2 class="section-title">把<span class="gold">學費與時程</span>對到你的孩子</h2>
      <p class="section-subtitle">上面是制度與費用結構；實際要排的，是你孩子的年齡對應哪個入學年度、哪幾所學校還在收件。</p>
      <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:24px">
        <a href="/consultation?pillar=education" class="btn btn-primary" data-cta-id="education-cost" data-cta-location="mid_section" title="預約 30 分鐘教育評估">預約 30 分鐘教育評估 <i class="fas fa-arrow-right"></i></a>
        <a href="/consultation?pillar=education" class="btn btn-outline" data-cta-id="education-leadmagnet" data-cta-location="mid_section" data-leadmagnet="fees-timeline" title="索取學費與申請時程表">索取《學費與申請時程表》 <i class="fas fa-file-lines"></i></a>
      </div>
      <p style="font-size:0.8rem;color:#F5F0E877;margin-top:14px">時程表依孩子年齡與目標入學年度整理；學費與各校截止日以當年度公告為準，不代辦、不抽佣。</p>
    </div>
  </div>
</section>
'''

zh_faq_item = '''
      <div class="faq-item fade-in">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>錯過申請時程會怎樣？</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="faq-answer">
          <p>南非學校的學位以「學年」為單位配置，主要入口是 Grade 8；錯過當年度通常要等下一學年，Grade 9、Grade 10 只在有缺額時才收。連帶影響三件事：學生簽證必須先有學校錄取信才能送件，時程一延，簽證、租約與監護授權要全部重排；開普敦的走讀學校還要重談租約與接送動線。實務上把「入學年往回推 18 個月」設成自己的死線，比盯著學校截止日有效。</p>
        </div>
      </div>
'''

zh_faq_json = ''',
    {
      "@type": "Question",
      "name": "錯過申請時程會怎樣？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "南非學校的學位以學年為單位配置，主要入口是 Grade 8，錯過當年度通常要等下一學年，Grade 9 與 Grade 10 只在有缺額時才收。學生簽證必須先有學校錄取信才能送件，因此時程一延，簽證、租約與監護授權都要重排。實務上建議把入學年往回推 18 個月設成自己的死線。"
      }
    }'''

print("== ZH education.html")
patch("education.html", zh_stats)
t = (D/"education.html").read_text(encoding="utf-8")
# insert mid CTA right before the alumni section
anchor = '<!-- ALUMNI NETWORK -->'
assert anchor in t, "alumni anchor missing"
t = t.replace(anchor, zh_cta + "\n\n" + anchor, 1)
# append FAQ item before closing of faq-list
faq_close = '''      </div>
    </div>
  </div>
</section>

<!-- cal-booking-inline-v1 -->'''
assert faq_close in t, "faq close anchor missing"
t = t.replace(faq_close, '''      </div>
''' + zh_faq_item + '''    </div>
  </div>
</section>

<!-- cal-booking-inline-v1 -->''', 1)
# extend JSON-LD FAQPage
j = t.find('"@type": "FAQPage"')
end = t.find(']', j)
t = t[:end] + zh_faq_json + t[end:]
(D/"education.html").write_text(t, encoding="utf-8")
print("   CTA/FAQ/JSON-LD inserted")

# ---------------- EN ----------------
en_stats = [
 ('<span class="num danger-num">47%</span>\n            <span class="label">Traditional white-collar jobs will be replaced or reshaped by AI by 2030</span>',
  '<span class="num danger-num">AI</span>\n            <span class="label">Entry-level white-collar work is being reshaped by AI, starting with repetitive tasks</span>'),
 ('<span class="num">3.2×</span>\n            <span class="label">Students with international education backgrounds have 3.2× higher admission rates to top global companies</span>',
  '<span class="num">Outlook</span>\n            <span class="label">An international qualification plus cross-cultural experience is a real differentiator in global hiring</span>'),
 ('<span class="num danger-num">85%</span>\n            <span class="label">Asian parents admit their children\'s English proficiency is insufficient for the international workplace</span>',
  '<span class="num danger-num">Baseline</span>\n            <span class="label">English has moved from an advantage to a basic requirement — without it the interview stage is out of reach</span>'),
 ('<span class="num">Age 12</span>\n            <span class="label">Optimal starting age for studying abroad — miss the golden window and language and perspective gaps become difficult to close</span>',
  '<span class="num">Earlier</span>\n            <span class="label">Language and perspective gaps widen with age; the later a child enters an all-English environment, the harder they are to close</span>'),
 ('For the next decade, children who can only take exams, with no international perspective and no cross-cultural competitiveness, will face unprecedented workplace pressure.',
  'Over the next decade, children who can only sit exams — with no international perspective and no cross-cultural experience — will find their options narrower than their parents\' generation.'),
]
print("== EN education-en.html")
p = D/"education-en.html"; t = p.read_text(encoding="utf-8")
for old, new in en_stats:
    if old in t:
        t = t.replace(old, new)
    else:
        print("   !! MISS stat:", old[:60])
# buttons
btns = [
 ('<a href="#" class="btn btn-primary" title="Book Education Consultation Now">',
  '<a href="/consultation-en?pillar=education" class="btn btn-primary" title="Book Education Consultation Now" data-cta-id="education-urgency" data-cta-location="bottom_cta">'),
 ('<a href="#" class="btn-outline-danger" title="Learn About the Golden Window">',
  '<a href="#cost" class="btn-outline-danger" title="See fees and application timeline" data-cta-id="education-cost-link" data-cta-location="nav">'),
]
for old, new in btns:
    if old in t:
        t = t.replace(old, new); print("   btn fixed:", old[:50])
    else:
        print("   !! MISS btn:", old[:60])
p.write_text(t, encoding="utf-8")

en_cta = '''
<!-- EDUCATION MID CTA (2026-10-21) -->
<section class="section" id="cost-cta" style="padding-top:0">
  <div class="container">
    <div class="text-center fade-in" style="max-width:780px;margin:0 auto">
      <div class="gold-line"></div>
      <h2 class="section-title">Match the <span class="gold">fees and timeline</span> to your child</h2>
      <p class="section-subtitle">The table above is the structure. What you actually have to sequence is which entry year your child's age maps to — and which schools are still taking applications.</p>
      <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:24px">
        <a href="/consultation-en?pillar=education" class="btn btn-primary" data-cta-id="education-cost" data-cta-location="mid_section" title="Book a 30-minute education assessment">Book a 30-minute education assessment <i class="fas fa-arrow-right"></i></a>
        <a href="/consultation-en?pillar=education" class="btn btn-outline" data-cta-id="education-leadmagnet" data-cta-location="mid_section" data-leadmagnet="fees-timeline" title="Request the fees and application timeline">Request “Fees &amp; Application Timeline” <i class="fas fa-file-lines"></i></a>
      </div>
      <p style="font-size:0.8rem;color:#F5F0E877;margin-top:14px">The timeline sheet is organised by the child's age and target entry year. Fees and closing dates follow each school's current-year publication. We do not act as agents and do not take commission.</p>
    </div>
  </div>
</section>
'''

en_faq_item = '''
      <div class="faq-item fade-in">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>What happens if we miss the application window?</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="faq-answer">
          <p>South African schools allocate places by academic year, and Grade 8 is the main entry point. Miss the year and the usual outcome is waiting for the next one; Grades 9 and 10 open only when a place falls vacant. Three things cascade: a study visa cannot be lodged without an acceptance letter, so a slip in timing means the visa, the lease and the guardianship authorisation all get re-sequenced — and in Cape Town, day schools also mean renegotiating the lease and the school run. In practice, set your own deadline 18 months before the entry year rather than watching the school's closing date.</p>
        </div>
      </div>
'''

en_faq_json = ''',
    {
      "@type": "Question",
      "name": "What happens if we miss the application window?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Places are allocated by academic year and Grade 8 is the main entry point, so a missed year usually means waiting for the next one; Grades 9 and 10 open only when a vacancy appears. A study visa cannot be lodged without an acceptance letter, so a timing slip forces the visa, lease and guardianship authorisation to be re-sequenced. Setting your own deadline 18 months before the entry year is the practical safeguard."
      }
    }'''

t = p.read_text(encoding="utf-8")
# find alumni anchor in EN
m = re.search(r'<!--\s*ALUMNI', t)
print("   alumni anchor:", bool(m))
if m:
    t = t[:m.start()] + en_cta + "\n\n" + t[m.start():]
# FAQ item: insert before the closing of the faq list (last faq-item's closing div sequence)
idx = t.rfind('<div class="faq-item')
close = t.find('</div>', t.find('</div>', t.find('</div>', idx)+6)+6)
# simpler: find the faq section end marker
faqend = t.find('</section>', idx)
t = t[:faqend] + en_faq_item + t[faqend:]
# JSON-LD
j = t.find('"@type": "FAQPage"')
if j > 0:
    end = t.find(']', j)
    t = t[:end] + en_faq_json + t[end:]
p.write_text(t, encoding="utf-8")
print("   EN CTA/FAQ/JSON-LD inserted")
