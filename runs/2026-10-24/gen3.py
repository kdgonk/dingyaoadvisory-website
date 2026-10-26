#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文章 3（舊文優化 patch）：taiwan-parents-choosing-south-africa-private-schools
   不改 slug / URL / title 主關鍵字；補 2026 官方 fee schedule、五年總額、隱藏成本、FAQ、內連。
   輸出至 runs/2026-10-24/（供泰坦人覆蓋 dist/blog/）。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT

REPO = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website"
SLUG = "taiwan-parents-choosing-south-africa-private-schools"
TODAY = "2026-10-24"
FX = "1 南非幣 ≈ 新台幣 1.975 元（2026-10-23 參考匯率，僅供試算）"
FX_EN = "roughly 1 rand = NT$1.975 on 23 October 2026 (illustration only)"

# ─────────────── ZH ───────────────
ZH_OLD_BLOCK = """      <p>學費是台灣家長最關心的因素之一。以下為年學費的概略比較（以新台幣計算）：</p>"""

ZH_NEW_BLOCK = """      <p>學費是台灣家長最關心的因素之一。但「南非私校比較便宜」這句話在 2026 年需要修正：<strong>要看你比的是「學費」還是「學費加寄宿」。</strong>以開普敦 Rondebosch 的 Bishops Diocesan College 為例，2026 年官方 fee schedule 的中學部（Grades 8–11）學費是 <strong>R225,900／年</strong>，寄宿再加 <strong>R160,400／年</strong>，全年合計 <strong>R386,300</strong>。若只看學費，它確實仍低於台灣頂級私校；但若把寄宿算進去，它落在台灣頂級私校的價格帶內，不再是一律「三分之一」。</p>

      <h3>先看官方數字：Bishops 2026 年 fee schedule</h3>
      <table class="comparison-table">
        <thead>
          <tr><th>項目</th><th>每學期</th><th>全年</th><th>每月自動扣款（含 2.9% 附加）</th></tr>
        </thead>
        <tbody>
          <tr><td>College Grades 8–11 學費</td><td>R56,475</td><td><strong>R225,900</strong></td><td>R23,246.24</td></tr>
          <tr><td>College 寄宿</td><td>R40,100</td><td><strong>R160,400</strong></td><td>R16,505.96</td></tr>
          <tr class="highlight-row"><td>學費＋寄宿合計</td><td>R96,575</td><td><strong>R386,300</strong></td><td>R39,752.20</td></tr>
          <tr><td>Grade 12（僅 3 學期）</td><td>R128,767</td><td>R386,300</td><td>—</td></tr>
          <tr><td>Prep（Grades 3–7）學費</td><td>R42,775</td><td>R171,100</td><td>R17,607.05</td></tr>
          <tr><td>Pre-Prep（Grade N–2）學費</td><td>R24,300</td><td>R97,200</td><td>R10,002.37</td></tr>
          <tr><td>資本捐（Capital Levy，自願）</td><td>R1,500</td><td>R6,000</td><td>R600</td></tr>
        </tbody>
      </table>
      <p>（資料來源：Bishops Diocesan College, Fee Structure 2026 官方 PDF, bishops.org.za/Admissions/Fees）</p>
      <p>三個容易被忽略的細節：<strong>①</strong> 年繳可享 <strong>2.5% 折扣</strong>（官方說明以 6.75% 年化等效利率計算，因學費於每學期首日到期）；<strong>②</strong> Grade 12 只收 3 個學期，但全年總額不變；<strong>③</strong> 資本捐是「每戶一次、自願性質」，可開 S18A 抵税收據——不繳不會影響入學，但多數家長會繳。</p>
      <p>這也說明為什麼比較南非私立學校時，第一步一定是把「每學期」與「全年」兩種報價統一換算：多數南非私立學校同時公布這兩種金額，而每學期數字看起來永遠比較小，很容易讓家長低估整年支出。</p>

      <h3>再看全國上限：Hilton College 與 13 所 R350,000 以上學校</h3>
      <p>如果 Bishops 代表開普敦的中位數，Hilton College 就代表全國上限。2026 年 Hilton 的學費加寄宿是 <strong>R441,766／年</strong>，另有一筆 <strong>R110,441.50 的入學費（entry fee），不可退還</strong>，官方說明它「等同一學期學費」。（資料來源：Hilton College, Enrolment Dates and Fees, hiltoncollege.com）</p>
      <p>而 <strong>Hilton 這筆錢還不是全部</strong>。官方頁面另列了一項簡報與多數中文資料都沒提到的：<strong>Foreign Pupil's Deposit</strong>——家庭不住在南非的學生，須繳 <strong>1.5 個學期學費</strong>的押金，用於支應必要時的遣返費用，<strong>可退還</strong>。以 2026 年匯率與學費推算，一學期約 R110,441.50，押金即約 <strong>R165,662</strong>。這筆錢會在開學前就離開你的帳戶，並且要等到孩子離校才回來。</p>

      <h3>五年總額怎麼算：這才是家長該記住的數字</h3>
      <table class="comparison-table">
        <thead>
          <tr><th>學校</th><th>全年學費＋寄宿</th><th>5 年（G8–12）總額</th><th>約合新台幣</th></tr>
        </thead>
        <tbody>
          <tr><td>Bishops Diocesan College（開普敦 Rondebosch）</td><td>R386,300</td><td><strong>R1,931,500</strong></td><td>約 NT$3,815,000</td></tr>
          <tr><td>Hilton College（KZN）</td><td>R441,766</td><td><strong>R2,208,830</strong></td><td>約 NT$4,362,000</td></tr>
        </tbody>
      </table>
      <p>換算基準：%s。學費每年由學校於 11 月檢視調整（資料來源：Bishops Diocesan College, Annual School Fees 頁面, bishops.org.za/Admissions/Fees），上表為 <strong>2026 年公告值</strong>，不是五年固定價；實際支出會隨每年調幅上升，也隨匯率變動。</p>

      <h3>台灣家長最常漏算的五筆錢</h3>
      <ul>
        <li><strong>入學費（entry fee）</strong>：Hilton 為 R110,441.50，<strong>不可退</strong>。這一筆通常在「接受學位」時就要付，與學費分開。</li>
        <li><strong>外籍學生押金</strong>：Hilton 要求 1.5 個學期學費（約 R165,662），可退但會鎖住現金流數年。</li>
        <li><strong>資本捐與一次性費用</strong>：Bishops 資本捐 R6,000／年（自願、可開 S18A 收據）；樂器、運動巡迴、制服另計。</li>
        <li><strong>監護與假期安置</strong>：寄宿學校四個學期之間的長假，學生不能留宿，這段時間的住宿與監護安排是完全獨立的成本。</li>
        <li><strong>機票</strong>：一年 2 到 4 趟，視學校假期與家庭安排而定，這筆錢不會出現在任何 fee schedule 上。</li>
      </ul>
      <p>把這五筆加進來，你就會發現真正的決策問題不是「一年學費多少」，而是<strong>「前兩年要準備多少現金」</strong>——因為入學費、押金與第一年學費往往集中在同一個學期發生。</p>

      <p>年學費的概略比較（以新台幣計算，含寄宿）：</p>"""

ZH_OLD_CLOSING = """      <p>從表中可以清楚看到，南非頂級私校的學費僅為台灣私校的 <strong>1/3 到 1/2</strong>，更只有英國寄宿學校的 <strong>1/5 到 1/6</strong>。考慮到南非私校提供的全英語授課環境與國際課程認證，其性價比在全球教育市場中極具競爭力。</p>"""

ZH_NEW_CLOSING = """      <p>修正後的正確說法是：<strong>南非頂級私校的「學費」約為台灣頂級私校的 0.5 到 0.75 倍，但「學費加寄宿」會落在台灣頂級私校的價格帶內</strong>；與英國寄宿學校相比，仍只有約 1/3 到 1/2。真正的價值不在「便宜」，而在同樣的預算下，你買到的是全英語授課、IEB／Cambridge 雙軌認證、以及 1:12 的師生比。</p>
      <p>學費數字為 2026 年各校官方公告值，每年 11 月檢視調整、以學校當年度 fee schedule 為準，並非保證金額；匯率換算僅供參考，實際支出隨匯率與學校調幅變動。</p>"""

ZH_NEW_SECTION = """
<div class="section">
  <div class="container">
    <section class="article-body fade-in visible">
      <h2>學費要怎麼從台灣匯過去？與匯款意圖的銜接</h2>
      <p>確認了數字之後，下一個實務問題是「錢怎麼到學校手上」。南非私校通常要求外籍家庭<strong>按年或按學期預繳</strong>（Hilton 官方頁面明文要求 foreign resident parents 以 annual 或 termly in advance 方式繳費），這與台灣家長習慣的月繳完全不同，現金流要提前安排。</p>
      <p>從南非境內帳戶付款給學校相對單純；但若你打算從台灣直接匯入，就會碰到與「南非匯款」相同的分類問題——教育相關的匯入匯出在 BoP 分類裡有對應類別，性質說錯一樣會被退件。這一塊的完整流程，站上另一篇專文有逐步說明。</p>
      <ul>
        <li><a href="/blog/south-africa-interest-remittance-to-taiwan-2026" title="南非幣匯回台灣的 BoP 類別與申報">南非幣匯回台灣的 BoP 類別與申報</a>——反向（匯出南非）的文件邏輯與匯率安排。</li>
        <li><a href="/education" title="南非留學與頂級私校規劃服務">南非留學與頂級私校規劃服務</a>——選校、申請時程與費用試算的顧問服務。</li>
      </ul>
    </section>
  </div>
</div>
"""

ZH_OLD_FAQ = """      <h3>南非頂級私校的學費大約多少？</h3>
      <p>南非頂級私校學費約為每年 R 150,000 - R 250,000（約新台幣 25-40 萬），大約是台灣國際學校或英國私校的 1/3。以台灣私校 1/3 的費用，即可享受全英語授課、小班制教學與國際認證的 IEB 和 Cambridge 課程。</p>"""

ZH_NEW_FAQ = """      <h3>南非頂級私校的學費大約多少？</h3>
      <p>依 2026 年各校官方 fee schedule：開普敦 Bishops Diocesan College 中學部（Grades 8–11）學費 R225,900／年，加寄宿 R160,400，全年 R386,300；Prep（Grades 3–7）R171,100；Pre-Prep（Grade N–2）R97,200。全國上限的 Hilton College 為學費加寄宿 R441,766／年，另有不可退還的入學費 R110,441.50。學費每年 11 月檢視調整，以學校當年度公告為準。</p>

      <h3>南非私校一年到底要準備多少現金？</h3>
      <p>不要只看一年學費，要看「第一年要拿出多少」。以開普敦 Bishops 中學部寄宿為例：全年學費加寄宿 R386,300，加上資本捐 R6,000（自願），第一年約 R392,300，約合新台幣 77 萬元。若選 Hilton，第一年還要加上不可退的入學費 R110,441.50，以及外籍學生押金 1.5 個學期學費（約 R165,662，可退）——三筆集中在同一學期發生，第一年現金需求會明顯高於後續年度。</p>"""

ZH_OLD_RELATED = """        <li><a href="/blog/south-africa-passport-free-travel" title="南非護照免簽旅行指南">南非護照免簽旅行指南</a></li>
      </ul>"""

ZH_NEW_RELATED = """        <li><a href="/blog/south-africa-passport-free-travel" title="南非護照免簽旅行指南">南非護照免簽旅行指南</a></li>
        <li><a href="/blog/south-africa-boarding-school-admission-timeline-2026" title="南非寄宿學校申請時程與監護安排">南非寄宿學校申請時程與監護安排</a>——提前多久開始申請、監護人與學生簽證怎麼排。</li>
        <li><a href="/blog/south-africa-interest-remittance-to-taiwan-2026" title="南非幣匯回台灣的 BoP 類別與申報">南非幣匯回台灣的 BoP 類別與申報</a>——學費與資金的跨境申報邏輯。</li>
        <li><a href="/education" title="南非留學與頂級私校規劃服務">南非留學與頂級私校規劃服務</a>——選校清單、申請時程與費用試算。</li>
      </ul>"""

ZH_OLD_CTA = """      <h2>開啟孩子的 <span class="gold">南非國際教育</span> 之旅</h2>
      <p>全英語授課、世界級課程、合理學費 — 南非頂級私校為您的孩子打開通往全球頂尖大學的大門。立即預約諮詢，獲取完整的學校評估與申請規劃。</p>
      <a href="/consultation" class="btn btn-primary" title="預約諮詢">預約諮詢 <i class="fas fa-arrow-right"></i></a>"""

ZH_NEW_CTA = """      <h2>先把 <span class="gold">五年現金流</span> 算清楚，再談選校</h2>
      <p>全英語授課、IEB 與 Cambridge 雙軌認證、1:12 師生比——這些是南非頂級私校的價值。但錄取之後真正要面對的，是入學費、押金與四個學期學費集中在同一年的現金流。告訴我們孩子的年齡、目標入學年級與是否住宿，我們會提供開普敦與西開普主要私校的 2026 官方學費對照、五年總額試算、隱藏成本清單，以及學費匯出南非的文件與時程安排。</p>
      <a href="/education" class="btn btn-primary" title="了解南非留學服務">了解南非留學服務 <i class="fas fa-arrow-right"></i></a>"""

ZH_DESC = ("南非頂級私校 2026 年官方學費公布：開普敦 Bishops 中學部學費 R225,900 加寄宿 R160,400，"
           "全年 R386,300；Hilton College 全年 R441,766、入學費 R110,441.50 不可退，外籍學生另須 1.5 個學期押金。"
           "台灣家長最常漏算的是五年總額與前置現金，不是一年學費。本文整理開普敦與西開普主要私校的官方 fee schedule、"
           "五年現金流試算、隱藏成本清單與學費匯出安排。立即索取 2027 學費試算表。")

# ─────────────── EN ───────────────
EN_OLD_BLOCK = """      <p>Tuition is one of the most important factors for Taiwanese parents. Below is an approximate annual tuition comparison (in NTD):</p>"""

EN_NEW_BLOCK = """      <p>Tuition is one of the most important factors for Taiwanese parents. But the familiar line that "South African private schools are cheaper" needs correcting for 2026: <strong>it depends whether you are comparing tuition alone or tuition plus boarding.</strong> At Bishops Diocesan College in Rondebosch, Cape Town, the official 2026 fee schedule puts College (Grades 8–11) tuition at <strong>R225,900 per year</strong>, with boarding adding <strong>R160,400</strong> — <strong>R386,300</strong> all in. Tuition alone remains below Taiwan's top private schools; tuition plus boarding lands inside the Taiwanese price band, and is no longer uniformly "one third".</p>

      <h3>The official numbers: Bishops 2026 fee schedule</h3>
      <table class="comparison-table">
        <thead>
          <tr><th>Item</th><th>Per term</th><th>Per annum</th><th>Monthly debit order (incl. 2.9%)</th></tr>
        </thead>
        <tbody>
          <tr><td>College Grades 8–11 tuition</td><td>R56,475</td><td><strong>R225,900</strong></td><td>R23,246.24</td></tr>
          <tr><td>College boarding</td><td>R40,100</td><td><strong>R160,400</strong></td><td>R16,505.96</td></tr>
          <tr class="highlight-row"><td>Tuition plus boarding</td><td>R96,575</td><td><strong>R386,300</strong></td><td>R39,752.20</td></tr>
          <tr><td>Grade 12 (3 terms only)</td><td>R128,767</td><td>R386,300</td><td>—</td></tr>
          <tr><td>Prep (Grades 3–7) tuition</td><td>R42,775</td><td>R171,100</td><td>R17,607.05</td></tr>
          <tr><td>Pre-Prep (Grade N–2) tuition</td><td>R24,300</td><td>R97,200</td><td>R10,002.37</td></tr>
          <tr><td>Capital levy (voluntary)</td><td>R1,500</td><td>R6,000</td><td>R600</td></tr>
        </tbody>
      </table>
      <p>(Source: Bishops Diocesan College, Fee Structure 2026 official PDF, bishops.org.za/Admissions/Fees)</p>
      <p>Three details that are easy to miss: <strong>(1)</strong> annual settlement earns a <strong>2.5% rebate</strong> (the school explains it on an annual-equivalent call rate of 6.75%, because fees fall due on the first day of term); <strong>(2)</strong> Grade 12 is billed over three terms but the annual total is unchanged; <strong>(3)</strong> the capital levy is one per family, voluntary, and carries an S18A tax receipt — not paying it does not affect admission, but most families do.</p>
      <p>That is also why any comparison of <strong>South Africa private school fees</strong> has to begin by putting per-term and per-annum quotes on the same basis. <strong>Cape Town boarding school</strong> costs in particular are published both ways, and the per-term figure always looks smaller. Published <strong>South Africa school fees</strong> therefore need normalising before you compare schools — the discipline that makes <strong>choosing a school in South Africa</strong> a like-for-like exercise rather than an apples-to-oranges one.</p>

      <h3>The national ceiling: Hilton College and 13 schools above R350,000</h3>
      <p>If Bishops is the Cape Town midpoint, Hilton College is the national ceiling. For 2026 its tuition and boarding is <strong>R441,766 per annum</strong>, plus a <strong>R110,441.50 entrance fee that is non-refundable</strong> — the school describes it as the equivalent of one term's fees. (Source: Hilton College, Enrolment Dates and Fees, hiltoncollege.com)</p>
      <p>And that is still not the whole number. The official page lists an item that most Chinese-language material omits: a <strong>Foreign Pupil's Deposit</strong> of <strong>one and a half terms' fees</strong> for boys whose families live outside South Africa, held to cover repatriation if required and <strong>refundable</strong>. At 2026 fees one term is about R110,441.50, so the deposit is roughly <strong>R165,662</strong> — money that leaves your account before term starts and returns only when your son leaves the school.</p>

      <h3>The five-year total: the number parents should actually remember</h3>
      <table class="comparison-table">
        <thead>
          <tr><th>School</th><th>Annual tuition + boarding</th><th>Five years (G8–12)</th><th>Approx. NT$</th></tr>
        </thead>
        <tbody>
          <tr><td>Bishops Diocesan College (Rondebosch, Cape Town)</td><td>R386,300</td><td><strong>R1,931,500</strong></td><td>about NT$3,815,000</td></tr>
          <tr><td>Hilton College (KwaZulu-Natal)</td><td>R441,766</td><td><strong>R2,208,830</strong></td><td>about NT$4,362,000</td></tr>
        </tbody>
      </table>
      <p>Conversion basis: %s. Fees are reviewed by each school every November (Source: Bishops Diocesan College, Annual School Fees page, bishops.org.za/Admissions/Fees); the table shows <strong>2026 published figures</strong>, not a five-year fixed price. Actual spend rises with each annual increase and moves with the exchange rate.</p>

      <h3>The five costs Taiwanese parents most often miss</h3>
      <ul>
        <li><strong>Entrance fee</strong>: R110,441.50 at Hilton, <strong>non-refundable</strong>, payable on acceptance and separate from tuition.</li>
        <li><strong>Foreign pupil's deposit</strong>: Hilton requires one and a half terms' fees (about R165,662). Refundable, but it ties up cash for years.</li>
        <li><strong>Capital levy and one-off costs</strong>: Bishops charges a voluntary R6,000 capital levy per year with an S18A receipt; instruments, sports tours and uniforms are additional.</li>
        <li><strong>Guardianship and holiday placement</strong>: boarding houses close during the long breaks between the four terms, so holiday accommodation and guardianship are a separate cost line.</li>
        <li><strong>Flights</strong>: two to four trips a year depending on term dates and family arrangements — a cost that appears on no fee schedule.</li>
      </ul>
      <p>Add those five and the real question stops being "what is the annual fee" and becomes <strong>"how much cash do I need in the first two years"</strong> — because the entrance fee, the deposit and the first year's tuition tend to land in the same term.</p>

      <p>An approximate annual comparison (NTD, including boarding):</p>"""

EN_OLD_CLOSING = """      <p>The table clearly shows that South Africa's top private school tuition is only <strong>one-third to one-half</strong> of Taiwanese private schools, and just <strong>one-fifth to one-sixth</strong> of UK boarding schools. Considering the full English immersion environment and international curriculum certification, the value proposition is highly competitive in the global education market.</p>"""

EN_NEW_CLOSING = """      <p>The accurate formulation is narrower: <strong>tuition alone at a top South African private school runs at roughly 0.5 to 0.75 times a top Taiwanese private school, but tuition plus boarding lands inside the Taiwanese band</strong>; against UK boarding schools it remains about one third to one half. The value is not "cheap" — it is what the same budget buys: full English instruction, dual IEB and Cambridge certification, and a 1:12 student-teacher ratio.</p>
      <p>Fee figures are the 2026 published values of each school, reviewed every November and governed by the current year's fee schedule; they are not guaranteed amounts. Currency conversions are indicative and move with the exchange rate and each school's annual increase.</p>"""

EN_NEW_SECTION = """
<div class="section">
  <div class="container">
    <section class="article-body fade-in visible">
      <h2>How do you actually pay the fees from Taiwan?</h2>
      <p>Once the numbers are clear, the next practical question is how the money reaches the school. South African private schools generally require foreign families to <strong>pay annually or termly in advance</strong> — Hilton states this explicitly for foreign resident parents — which is nothing like the monthly pattern Taiwanese parents are used to, so the cash flow has to be arranged ahead of time.</p>
      <p>Paying from a rand account inside South Africa is comparatively simple. Paying directly from Taiwan runs into the same classification problem as any cross-border payment to South Africa: education-related flows have their own BoP categories, and describing the nature incorrectly triggers rejection. The full procedure is covered in a separate guide.</p>
      <ul>
        <li><a href="/blog/south-africa-interest-remittance-to-taiwan-2026-en" title="BoP categories and reporting for remitting rand to Taiwan">BoP categories and reporting for remitting rand to Taiwan</a> — the document logic and currency timing.</li>
        <li><a href="/education-en" title="South Africa education and private school planning">South Africa education and private school planning</a> — school selection, application timing and fee modelling.</li>
      </ul>
    </section>
  </div>
</div>
"""

EN_OLD_FAQ = """      <h3>What is the tuition for South Africa's top private schools?</h3>
      <p>Annual tuition at South Africa's top private schools ranges from ZAR 150,000–300,000 (approximately NTD 250,000–500,000), which is only one-third of Taiwan's top private schools and one-fifth of UK boarding schools.</p>"""

EN_NEW_FAQ = """      <h3>What is the tuition for South Africa's top private schools?</h3>
      <p>Per the 2026 official fee schedules: Bishops Diocesan College in Cape Town charges R225,900 per year for College (Grades 8–11) tuition plus R160,400 boarding, R386,300 all in; Prep (Grades 3–7) is R171,100 and Pre-Prep (Grade N–2) R97,200. At the national ceiling, Hilton College charges R441,766 for tuition and boarding plus a non-refundable R110,441.50 entrance fee. Fees are reviewed each November; the current year's schedule governs.</p>

      <h3>How much cash should a family actually prepare for one year?</h3>
      <p>Look at the first year, not the annual fee. For Bishops College boarding in Cape Town: R386,300 tuition and boarding plus a voluntary R6,000 capital levy, about R392,300 in year one — roughly NT$775,000. At Hilton, year one adds a non-refundable R110,441.50 entrance fee and a foreign pupil's deposit of one and a half terms (about R165,662, refundable). Those three items tend to fall in the same term, so the first-year cash requirement is materially higher than later years.</p>"""

EN_OLD_RELATED = """        <li><a href="/blog/south-africa-passport-free-travel-en" title="South Africa Passport-Free Travel Guide">South Africa Passport-Free Travel Guide</a></li>"""


EN_NEW_RELATED = """        <li><a href="/blog/south-africa-passport-free-travel-en" title="South Africa Passport-Free Travel Guide">South Africa Passport-Free Travel Guide</a></li>
        <li><a href="/blog/south-africa-boarding-school-admission-timeline-2026-en" title="Boarding school admission timeline and guardianship">Boarding school admission timeline and guardianship</a> — how far ahead to apply, and how guardianship and study visas fit together.</li>
        <li><a href="/blog/south-africa-interest-remittance-to-taiwan-2026-en" title="BoP categories and reporting for remitting rand to Taiwan">BoP categories and reporting for remitting rand to Taiwan</a> — the cross-border reporting logic for school fees.</li>
        <li><a href="/education-en" title="South Africa education and private school planning">South Africa education and private school planning</a> — school lists, application timing and fee modelling.</li>"""

EN_OLD_CTA = """      <h2>Start Your Child's <span class="gold">South Africa Education</span> Journey</h2>
      <p>Full English instruction, world-class curricula, affordable tuition — South Africa's top private schools open the door to the world's leading universities. Book a consultation today for a complete school assessment and application plan.</p>
      <a href="/consultation-en" class="btn btn-primary" title="Book Now">Book Now <i class="fas fa-arrow-right"></i></a>"""

EN_NEW_CTA = """      <h2>Model the <span class="gold">five-year cash flow</span> before you choose a school</h2>
      <p>Full English instruction, dual IEB and Cambridge certification, a 1:12 ratio — that is the value of a top South African private school. What follows an offer, though, is the entrance fee, the foreign pupil's deposit and four terms of tuition landing in the same year. Tell us your child's age, target entry grade and whether boarding is intended, and we will provide the 2026 official fee comparison for Cape Town and Western Cape schools, a five-year total, the hidden-cost list, and the documentation and timing for remitting fees to South Africa.</p>
      <a href="/education-en" class="btn btn-primary" title="Explore South Africa education services">Explore education services <i class="fas fa-arrow-right"></i></a>"""

EN_DESC = ("Bishops in Cape Town charges R225,900 tuition plus R160,400 boarding \u2014 R386,300 a year. "
           "Hilton College charges R441,766 plus a non-refundable R110,441.50 entrance fee. The five-year total and "
           "the upfront cash matter more than the annual fee. Request the 2027 fee worksheet.")


def sub(t, old, new, label):
    if old not in t:
        print(f"  !! MISS [{label}] {old[:70]}")
        return t
    if t.count(old) > 1:
        print(f"  !! MULTI [{label}] x{t.count(old)}")
    return t.replace(old, new)


def patch(lang):
    fn = SLUG + (".html" if lang == "zh" else "-en.html")
    t = open(os.path.join(REPO, "dist/blog", fn), encoding="utf-8").read()
    orig_len = len(t)

    if lang == "zh":
        t = sub(t, "南非頂級私校以台灣私校 <strong>1/3 的學費</strong>，提供了足以媲美英國、瑞士的教育品質。",
                "南非頂級私校以<strong>低於台灣頂級私校的學費</strong>（不含寄宿），提供足以媲美英國、瑞士的教育品質。", "intro-claim")
        t = sub(t, "平均師生比 1:12，年學費約新台幣 25–50 萬元。",
                "平均師生比 1:12；以開普敦 Bishops 2026 年官方公告為例，中學部學費加寄宿全年 R386,300（約新台幣 76 萬元），Hilton College 為 R441,766。",
                "summary-box")
        t = sub(t, ZH_OLD_BLOCK, ZH_NEW_BLOCK, "fee-block")
        t = sub(t, ZH_OLD_CLOSING, ZH_NEW_CLOSING, "fee-closing")
        t = sub(t, ZH_OLD_FAQ, ZH_NEW_FAQ, "faq")
        t = sub(t, ZH_OLD_RELATED, ZH_NEW_RELATED, "related")
        t = sub(t, ZH_OLD_CTA, ZH_NEW_CTA, "cta")
        # 新增 section 插在 FAQ 之前
        anchor = '      <h2>常見問題 FAQ</h2>'
        t = sub(t, anchor, ZH_NEW_SECTION.strip() + "\n\n" + anchor, "new-section")
        desc = ZH_DESC
    else:
        t = sub(t, "offer an education quality comparable to the UK and Switzerland at just <strong>one-third the cost</strong> of Taiwanese private schools.",
                "offer an education quality comparable to the UK and Switzerland at <strong>a lower tuition cost than Taiwan's top private schools</strong> (tuition only, excluding boarding).", "intro-claim")
        t = sub(t, "with an average student-to-teacher ratio of 1:12 and annual tuition of approximately NTD 250,000\u2013500,000.",
                "with an average student-to-teacher ratio of 1:12. At Bishops in Cape Town the official 2026 schedule puts College tuition plus boarding at R386,300 a year (about NT$763,000); Hilton College charges R441,766.", "summary-box")
        t = sub(t, EN_OLD_BLOCK, EN_NEW_BLOCK, "fee-block")
        t = sub(t, EN_OLD_CLOSING, EN_NEW_CLOSING, "fee-closing")
        t = sub(t, EN_OLD_RELATED, EN_NEW_RELATED, "related")
        t = sub(t, EN_OLD_CTA, EN_NEW_CTA, "cta")
        # EN FAQ：以官方 2026 數字取代舊的粗略區間，並新增「第一年現金」題
        t = sub(t, EN_OLD_FAQ, EN_NEW_FAQ, "en-faq")
        anchor = '      <h2>FAQ</h2>'
        t = sub(t, anchor, EN_NEW_SECTION.strip() + "\n\n" + anchor, "new-section")
        desc = EN_DESC

    # meta description 三處同步（description / og:description / twitter:description）
    for pat in (r'(<meta name="description" content=")[^"]*(")',
                r'(<meta property="og:description" content=")[^"]*(")',
                r'(<meta name="twitter:description" content=")[^"]*(")'):
        t = re.sub(pat, lambda m: m.group(1) + desc + m.group(2), t, count=1)
    # dateModified bump
    t = t.replace('"dateModified": "2026-06-15"', f'"dateModified": "{TODAY}"')
    t = t.replace('"dateModified":"2026-06-15"', f'"dateModified":"{TODAY}"')
    if lang == "zh":
        t = t.replace('2026.06.15', '2026.10.24')

    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(t)
    print(f"patched {fn}: {orig_len} -> {len(t)} chars (+{len(t) - orig_len})")


patch("zh")
patch("en")
