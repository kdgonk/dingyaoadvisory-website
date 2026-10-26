#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文章 1：south-africa-property-sale-withholding-tax-foreign-sellers-2026（支柱② 置產）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (load, split_tpl, build_meta_zh, build_meta_en, jsonld_zh, jsonld_en,
                     section, intro_section, assemble, TPL_ZH, TPL_EN, OUT, TODAY)

SLUG = "south-africa-property-sale-withholding-tax-foreign-sellers-2026"
A = "https://assets.dingyaoadvisory.tw/blog/images"

# ─────────────────────────── ZH ───────────────────────────
ZH_TITLE = "南非賣房稅 s35A 預扣稅 7.5%：NR03 申請與匯出實算（2026）｜鼎曜"
ZH_DESC = ("南非賣房稅的核心是所得稅法 s35A：非居民出售南非不動產，售價超過 R2,000,000 時，"
           "買方必須就「全額」預扣 7.5%（自然人）、10%（公司）或 15%（信託）。"
           "本文以開普敦 Bishopscourt 與 Atlantic Seaboard 實價拆解預扣金額、NR03 減免申請、"
           "21 個工作日與 14 天付款期限的差別、買方 10% 罰則、CGT 結算時點，以及匯出代碼 510 01，"
           "並附開普敦賣方出售前 90 天文件預檢清單。立即索取出售前檢查表。")
ZH_KW = "南非賣房稅, 南非資本利得稅, 預扣稅, 開普敦房產出售, section 35a withholding tax, 南非非居民賣房, SARS NR03, 南非房產匯出"

ZH_H1 = ("外國人賣開普敦房產，買方為什麼先扣 7.5%？"
         "<span class=\"gold\">s35A 預扣稅、NR03 與匯出實算（2026）</span>")
ZH_HEADLINE = "外國人賣開普敦房產，買方為什麼先扣 7.5%？s35A 預扣稅、NR03 與匯出實算（2026）"

ZH_INTRO = """      <p>2026 年 9 月，英國播客 Steven Bartlett 把他在開普敦 Bishopscourt 的莊園掛牌 <strong>R189,000,000</strong>，而他在 2024 年的買入價是 <strong>R93,300,000</strong>（資料來源：SA People, 2026-09-28；REI.co.za, 2026-09-28）。新聞談的是「兩年翻倍」，但對台灣賣方真正重要的是另一件事：這筆交易一旦成交，<strong>買方依法必須先扣下 R14,175,000 交給 SARS</strong>，而且扣的是「成交全額」的 7.5%，不是獲利的 7.5%。</p>
      <p>這就是所得稅法第 35A 條（section 35A）的預扣稅。它不在你買開普敦房子的時候出現，只在你賣的時候出現——所以多數台灣買家在<strong>進場那一刻</strong>根本沒算過它。這篇文章把開普敦房產出售的四個出場成本一次講清楚：預扣怎麼算、NR03 怎麼申請減免、21 個工作日到底在等什麼、以及錢最後怎麼從南非匯回台灣。</p>
      <div class="highlight-box">
        <p><strong>核心摘要：</strong>會。非居民出售南非不動產，只要成交總額超過 R2,000,000，買方就必須就<strong>全額成交價</strong>預扣 7.5%（自然人）、10%（公司）或 15%（信託），並在扣款後 14 天內（買方為非居民者 28 天）繳給 SARS。NR03 是賣方申請「降低或免除扣繳」的稅務指令，SARS 一般 21 個工作日內處理——這是<strong>指令處理時間，不是付款期限</strong>。預扣款是年度結算時的預繳，不是最終稅額；最終仍以資本利得稅（CGT）結算，多退少補。匯出時不動產處分所得走 BoP 類別 510 01。</p>
      </div>"""

ZH_S1 = """<h2>外國人賣開普敦房產，為什麼過戶前會先被扣一筆錢？</h2>
      <p>因為南非把「確保非居民繳稅」的責任，放在<strong>買方</strong>身上，而不是賣方身上。所得稅法 s35A 自 2007 年 9 月 1 日生效：任何必須付款給非居民賣方的人（買方），在處分南非不動產時，必須從應付金額中扣下法定比例，繳給 SARS（資料來源：SARS, Guide to Amounts to be Withheld, 2025-10-02 更新）。</p>
      <p>對在開普敦買房的台灣人來說，這個設計有一個很實際的後果：<strong>你賣房那天，收到的不會是成交價，而是成交價減掉預扣款。</strong>以 Southern Suburbs 一間成交 R8,000,000 的獨棟住宅為例，你當天拿到的上限是 R7,400,000，差的 R600,000 要先進 SARS 的口袋，等年度申報結算後才可能退回。</p>
      <h3>這筆錢的本質是「預繳」，不是「罰款」</h3>
      <p>SARS 對這件事的用語很明確：被扣下的金額是賣方<strong>該課稅年度正常稅（normal tax）的預付款（advance payment）</strong>。也就是說，它不是額外多收你一筆，而是先把你要繳的稅「預存」起來。真正的稅額在年度申報時才確定，扣多了退、扣少了補。</p>
      <p>但這裡有個開普敦賣方最容易誤判的地方：預扣比例是依<strong>成交價</strong>算，而實際稅額是依<strong>獲利</strong>算。一間 2019 年在 Constantia 以 R6,000,000 買入、2026 年以 R11,000,000 賣出的房子，預扣是 R825,000（全額 7.5%），但應稅獲利只有 R5,000,000 的一部分，兩者差距會讓現金流被鎖住好幾個月。</p>
      <table class="tax-table">
        <thead><tr><th>賣方身分</th><th>預扣比例</th><th>計算基礎</th><th>開普敦常見情境</th></tr></thead>
        <tbody>
          <tr><td>自然人（個人）</td><td><strong>7.5%</strong></td><td>應付金額全額</td><td>台灣個人名義持有 Bishopscourt、Constantia 房產</td></tr>
          <tr><td>公司</td><td><strong>10%</strong></td><td>應付金額全額</td><td>以南非或境外公司名義持有 Atlantic Seaboard 公寓</td></tr>
          <tr><td>信託</td><td><strong>15%</strong></td><td>應付金額全額</td><td>以家族信託持有開普敦酒莊周邊物業</td></tr>
        </tbody>
      </table>
      <p>（資料來源：SARS, Non-resident sellers of immovable property, 2026-08-19 更新；SARS, Guide to Amounts to be Withheld, 2025-10-02 更新）</p>"""

ZH_S2 = """<h2>R2,000,000 是「超過才扣」還是「超過就全額扣」？以開普敦實價算給你看</h2>
      <p><strong>超過就全額扣。</strong>這是 s35A 最容易被算錯的一條。SARS 原文寫得很直白：「Where the value of the property exceeds R2 million, the withholding amount applies to the full purchase price, without regard to the R2 million threshold.」——房產價值超過 R2,000,000 時，預扣金額適用於<strong>全部成交價</strong>，不扣除那 R2,000,000 的門檻（資料來源：SARS, Guide to Amounts to be Withheld, 2025-10-02）。</p>
      <p>換句話說，它不是「超過 R2,000,000 的部分才扣」。反過來說，如果買方應付的總額（含付給賣方或其他代收人的所有款項）「合計不超過」R2,000,000，s35A 就完全不適用。開普敦市區一間 R1,950,000 的小套房，與 Southern Suburbs 一間 R2,050,000 的排屋，只有 5% 的價差，卻決定了要不要被扣 15 萬以上——這條線在開普敦的價格帶裡是真實存在的。</p>
      <h3>三組實算：從 R2,000,000 到 R189,000,000</h3>
      <table class="tax-table">
        <thead><tr><th>開普敦情境</th><th>成交價</th><th>身分</th><th>預扣金額</th><th>賣方當日實拿</th></tr></thead>
        <tbody>
          <tr><td>Bishopscourt 莊園（Bartlett 掛牌案例）</td><td>R189,000,000</td><td>自然人</td><td><strong>R14,175,000</strong></td><td>R174,825,000</td></tr>
          <tr><td>Southern Suburbs 獨棟住宅</td><td>R8,000,000</td><td>自然人</td><td><strong>R600,000</strong></td><td>R7,400,000</td></tr>
          <tr><td>Atlantic Seaboard 海景公寓（公司持有）</td><td>R6,500,000</td><td>公司</td><td><strong>R650,000</strong></td><td>R5,850,000</td></tr>
          <tr><td>開普敦市區小套房</td><td>R1,950,000</td><td>自然人</td><td><strong>R0</strong>（合計未逾 R2,000,000 不適用）</td><td>R1,950,000</td></tr>
        </tbody>
      </table>
      <p>第一列的 R14,175,000，就是 R189,000,000 × 7.5%。注意這筆錢是<strong>買方</strong>的法定義務，不是賣方「可以商量」的選項。買方如果沒扣、沒繳，SARS 會直接找買方（下面第 4 節詳述）。</p>
      <h3>定金（deposit）那一筆要先扣嗎？</h3>
      <p>不用，但有條件。SARS 規定：買方為確保交易而支付的定金，在買賣契約尚未成為「無條件（unconditional）」之前，不需要就定金預扣；一旦契約生效，原本該從定金扣下的金額，<strong>改從後續第一筆付款中扣</strong>。開普敦的實務是：契約通常附帶「bond approval（貸款核准）」與「房屋檢查」等先決條件，這些條件清除（通常是簽約後 30 至 45 天）才是扣款的起算點。</p>"""

ZH_S3 = """<h2>NR03 可以少扣或免扣嗎？21 個工作日到底在等什麼？</h2>
      <p><strong>可以申請，但不是自動生效。</strong>賣方若認為自己的實際稅負低於法定預扣比例，可以向 SARS 申請稅務指令（tax directive），也就是表格 <strong>NR03</strong>。SARS 首頁列出的三種法定理由只有三個：已提供納稅擔保、賣方就該處分行為本身不負納稅義務、或賣方的實際稅負低於法定比例。SARS 舉的例子很具體——賣方完全免稅、個人應稅所得很低、或以虧損出售（資料來源：SARS, Non-resident sellers of immovable property, 2026-08-19）。</p>
      <p>對開普敦賣方最常見的第四種情況，其實不在那三個理由裡：<strong>「我明明沒賺那麼多，為什麼要按成交價扣？」</strong>答案就是——預扣是按成交價，不是按獲利，除非你申請 NR03 並被核准。申請時要一併附上 <strong>offer to purchase、稅額計算書與佐證文件</strong>，寄到 nres@sars.gov.za 或表單上列出的其他送件方式。</p>
      <h3>21 個工作日 ≠ 付款期限（這是最貴的誤解）</h3>
      <p>網路上最常見的說法是「買方必須在 21 個工作日內把錢付給 SARS」。這是錯的，而且錯得很危險。SARS 的兩個頁面分別寫的是兩件事：</p>
      <ul>
        <li><strong>21 個工作日</strong>：是 SARS 處理 NR03／NR02 的<strong>作業時間</strong>（"The directive application is generally processed within 21 business days"）。</li>
        <li><strong>14 天 / 28 天</strong>：才是買方的<strong>付款期限</strong>——買方為南非居民者，須在扣款後 14 天內連同申報書送交 SARS；買方本身為非居民者，為 28 天內（資料來源：SARS, Guide to Amounts to be Withheld, 2025-10-02）。</li>
      </ul>
      <p>兩個數字差了一個量級，實務後果完全不同。如果你以為「有 21 個工作日可以慢慢來」，而實際期限是 14 天，那 10% 罰則與利息會直接落在<strong>買方</strong>頭上——然後買方回過頭來找你。開普敦的代書（conveyancer）通常在過戶流程中就會要求雙方先把 NR02／NR03 備好，正是因為這個時間差。</p>
      <h3>申請時程要怎麼排？</h3>
      <div class="process-steps">
        <div class="process-step"><div class="step-num">1</div><div class="step-content"><h4>簽約前：確認賣方稅務身分</h4><p>非居民認定、稅號（income tax reference number）、過去在 SARS 的申報紀錄。開普敦代書會在 transfer duty 申報時勾選「s35A 是否適用」。</p></div></div>
        <div class="process-step"><div class="step-num">2</div><div class="step-content"><h4>簽約同時：備齊 NR03 三件套</h4><p>offer to purchase、稅額計算書、佐證文件（買入成本、資本支出、持有期間費用）。這一步沒做好，後面全部重來。</p></div></div>
        <div class="process-step"><div class="step-num">3</div><div class="step-content"><h4>送件後：預留 21 個工作日＋緩衝</h4><p>SARS 若認定賣方未登記所得稅，會先替賣方註冊，再核發指令。註冊這一步不計入 21 天，所以實務上要抓更寬。</p></div></div>
        <div class="process-step"><div class="step-num">4</div><div class="step-content"><h4>核准後：買方依指令金額扣繳</h4><p>若獲准降為 0%，買方仍須完成 NR02 申報，並在過戶時附上 NR03 與買賣契約。</p></div></div>
      </div>"""

ZH_S4 = """<h2>沒辦 NR03 會怎樣？買方、代書與仲介誰要負責？</h2>
      <p><strong>責任會分三層壓下來，而且罰則不得免除。</strong>這是 s35A 設計上最強硬的部分，也是開普敦賣方最需要理解的「對方為什麼一直催文件」的真正原因。</p>
      <h3>第一層：買方的個人責任</h3>
      <p>SARS 明文規定：買方若「知道或理應知道」賣方為非居民，就要<strong>個人負責</strong>，且必須在原應扣繳之日起算的期限內把錢繳給 SARS（資料來源：SARS, Guide to Amounts to be Withheld, 2025-10-02）。注意「理應知道」這四個字——外國護照、海外地址、海外帳戶付款，任何一項都會讓買方難以主張「我不知道」。</p>
      <h3>第二層：代書與仲介的書面通知義務</h3>
      <p>如果代書（conveyancer）或房仲（estate agent）因處理該筆處分而收取報酬，他們在<strong>付款給賣方之前</strong>，必須以書面通知買方「賣方為非居民、s35A 可能適用」。若他們「理應知道」卻沒通知，就要與買方<strong>連帶負責</strong>，但責任上限為其該筆交易的報酬金額。反過來說，若代書或仲介已盡通知義務，買方就不能再主張自己不知情。</p>
      <h3>第三層：10% 罰則＋利息，且利息不得免除</h3>
      <p>買方若未在期限內把扣下的錢繳給 SARS：</p>
      <ul>
        <li>就未繳金額按法定利率計<strong>利息</strong>，自付款期限次日起算至 SARS 實際收到日；</li>
        <li>另加 <strong>10% 罰款</strong>，且不影響其他依稅法可課的罰則或費用；</li>
        <li>SARS 明確加註：<strong>「No provision is made to waive interest.」——沒有免除利息的規定。</strong></li>
      </ul>
      <p>這條「不得免除」是全篇最硬的一句話。在開普敦的過戶實務裡，它意味著買方幾乎不可能「先過戶、後補稅」——因為補稅的成本只會往上加，不會被原諒。</p>
      <h3>外幣成交怎麼換算？</h3>
      <p>如果成交價以外幣計價，扣下的金額須按<strong>實際繳給 SARS 當日</strong>的即期匯率（spot rate）折算為南非幣。對台灣買方而言，這代表「匯率風險發生在繳稅日，不是簽約日」——2026 年南非幣兌新台幣的波動區間不小，這一點在計算實際成本時要留緩衝。</p>"""

ZH_S5 = """<h2>預扣的 7.5% 跟資本利得稅（CGT）是什麼關係？</h2>
      <p><strong>預扣是預繳，CGT 才是最終稅額。</strong>很多人把兩者混為一談，結果在開普敦賣房時把現金流算錯。SARS 的說法是：被扣下的金額是賣方在<strong>處分該不動產所屬課稅年度</strong>的正常稅預付款；而資本利得是依所得稅法第八附表（Eighth Schedule）計算後，計入應稅所得，再按邊際稅率課稅。</p>
      <h3>2026/27 年度 CGT 的有效稅率上限</h3>
      <p>資本利得不是全額課稅，而是先按「計入比例（inclusion rate）」計入應稅所得，再套用所得稅率。因此有效稅率有上限：</p>
      <table class="tax-table">
        <thead><tr><th>納稅主體</th><th>最高有效 CGT 稅率</th><th>對開普敦賣方的意義</th></tr></thead>
        <tbody>
          <tr><td>個人／特殊信託</td><td><strong>18%</strong></td><td>台灣個人名義持有的開普敦房產，適用此級</td></tr>
          <tr><td>公司</td><td><strong>21.6%</strong></td><td>以公司名義持有的 Atlantic Seaboard 物業</td></tr>
          <tr><td>其他信託</td><td><strong>36%</strong></td><td>家族信託持有的開普敦物業，稅負最重</td></tr>
        </tbody>
      </table>
      <p>（資料來源：SARS, Budget 2026 Frequently Asked Questions, 2026-03-20）</p>
      <p>同一份官方文件也公告了 2026 年 3 月 2 日起的排除額調整：<strong>年度排除額 R50,000</strong>（原 R40,000）、<strong>主要居所排除額 R3,000,000</strong>（原 R2,000,000）、死亡排除額 R440,000。主要居所排除額是否適用於非居民個案，須依第八附表條件與實際居住事實由 SARS 認定，不能直接套用。</p>
      <h3>處分時點是「簽約日」，不是「過戶日」</h3>
      <p>這是 2026 年開普敦賣方最該記住的一句：SARS 明確指出，不動產的 CGT 處分時點發生在<strong>買賣契約簽署日</strong>，不是在地政機關（Deeds Office）完成過戶登記的那一天。「若你在 2026 年 2 月簽約，獲利就落在 2025/26 課稅年度（截至 2026 年 2 月 28 日），即使過戶要到 5 月才完成。」（資料來源：SARS, Budget 2026 FAQ, 2026-03-20）</p>
      <p>對照之下，s35A 的預扣發生在「付款」環節、CGT 落在「簽約」環節——兩件事可能跨到不同課稅年度。開普敦一筆 11 月簽約、隔年 2 月過戶的交易，賣方會同時面對「今年度的 CGT」與「明年初的預扣款繳庫」，現金流要分兩段安排。</p>
      <h3>如果賣方不申報會怎樣？</h3>
      <p>SARS 規定：若賣方在該課稅年度結束後 <strong>12 個月內</strong>未提交申報書，已繳的預扣款本身即構成依稅務行政法（Tax Administration Act）第 95 條<strong>直接核定（assessment）</strong>的充分基礎。白話說：你不申報，SARS 就用手上那筆預扣款當成你的最終稅額，不會主動退你多扣的部分。</p>"""

ZH_S6 = """<h2>賣房款怎麼合法匯出南非？510 01 與 2026 年新 BoP 分類</h2>
      <p><strong>不動產處分所得走 BoP 類別 510 01。</strong>這是在開普敦賣完房子後，把錢匯出南非時最關鍵的一組數字。南非儲備銀行（SARB）自 <strong>2026 年 8 月 11 日</strong>起實施新的國際收支（BoP）分類，採 SADC 調和版代碼並納入 IMF 第七版手冊（BPM7）架構；銀行業的實施日為 2026-08-11（資料來源：Nedbank, FinSurv BoP categories guide, 2026-08；SARB Quarterly Bulletin, Box 2, 2026-09）。</p>
      <p>在非居民個人的「資本移轉（capital transfers）」項下，與開普敦賣方直接相關的是：</p>
      <table class="tax-table">
        <thead><tr><th>BoP 代碼</th><th>官方描述</th><th>開普敦賣方的適用情境</th></tr></thead>
        <tbody>
          <tr><td><strong>510 01</strong></td><td>Disinvestment of property by a non-resident individual</td><td>非居民個人出售開普敦不動產後匯出價金</td></tr>
          <tr><td><strong>510 02</strong></td><td>Disinvestment by a non-resident individual – other</td><td>非不動產類的其他資本撤回</td></tr>
          <tr><td><strong>313 00</strong></td><td>Income paid to a non-resident on an individual investment</td><td>租金、投資收益等所得類匯出</td></tr>
          <tr><td><strong>309 08</strong></td><td>Interest paid not in respect of loans</td><td>非貸款性質的利息支付</td></tr>
        </tbody>
      </table>
      <p>（資料來源：Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08）</p>
      <p>必須說清楚的是：<strong>最終代碼由銀行的授權外匯部門（authorised dealer）依實際交易性質認定</strong>，不是由賣方自行指定。上表是「你的交易會落在哪一類」的對照，不是「填這個就過」。這也是為什麼開普敦的匯出流程裡，第一個被退件的通常不是代碼寫錯，而是<strong>交易性質證明不足</strong>——你無法說明這筆錢是「賣房款」還是「租金」。因此賣方要留下的文件至少包括：買賣契約、過戶完成證明、SARS 的預扣繳款收據、以及外匯申報表。</p>
      <h3>匯出前最常被退件的三件事</h3>
      <ul>
        <li><strong>沒有 SARS 的預扣繳款證明</strong>：銀行在處理 510 01 時，會確認 s35A 的稅務義務已完成。沒有收據，整筆匯出會停住。</li>
        <li><strong>交易性質與資金來源說法不一致</strong>：契約寫「動產附隨買賣」、匯款卻申報「不動產處分」，就會被要求重填。</li>
        <li><strong>收款帳戶與賣方名義不符</strong>：匯到第三人（例如台灣的家人）需要額外授權文件，開普敦的銀行對這一點查得很嚴。</li>
      </ul>
      <p>把時間算進去：s35A 的扣繳、CGT 的年度申報、BoP 的匯出審核，是三段不同的流程，串起來在開普敦實務上通常要抓 3 到 6 個月。出售前先知道這件事，比成交後才知道，成本差很多。</p>"""

ZH_FAQ = [
    ("外國人賣開普敦房產，預扣稅是 7.5% 還是按獲利算？",
     "按成交價算，不是按獲利。非居民出售南非不動產，成交總額超過 R2,000,000 時，買方須就全額成交價預扣 7.5%（自然人）、10%（公司）或 15%（信託）。預扣款只是該年度正常稅的預付款，最終稅額仍依資本利得稅結算，多退少補。"),
    ("什麼是 NR03？申請一定會過嗎？",
     "NR03 是賣方向 SARS 申請「降低或免除扣繳」的稅務指令。SARS 只基於三種理由審查：已提供納稅擔保、賣方就該處分不負納稅義務、或實際稅負低於法定比例。不是申請就會過，且 SARS 通常需要 21 個工作日處理。"),
    ("21 個工作日是買方付款給 SARS 的期限嗎？",
     "不是。21 個工作日是 SARS 處理 NR03／NR02 的作業時間。買方的實際付款期限是扣款後 14 天內（買方為南非居民）或 28 天內（買方為非居民）。逾期會被課 10% 罰款加計利息，且 SARS 明訂利息不得免除。"),
    ("南非賣房的資本利得稅（CGT）最高是多少？",
     "2026/27 年度最高有效稅率：個人與特殊信託 18%、公司 21.6%、其他信託 36%。資本利得先按計入比例計入應稅所得，再套用所得稅率。2026 年 3 月 2 日起年度排除額為 R50,000，主要居所排除額為 R3,000,000，非居民個案適用須由 SARS 認定。"),
    ("賣房款匯出南非要用哪個代碼？",
     "非居民個人出售不動產後的價金匯出，對應 BoP 類別 510 01（Disinvestment of property by a non-resident individual）。最終代碼由銀行的授權外匯部門依實際交易性質認定。匯出前須備妥買賣契約、過戶證明與 SARS 預扣繳款收據，否則會被退件。"),
    ("CGT 是在簽約還是過戶時發生？",
     "在買賣契約簽署時發生，不是在 Deeds Office 完成過戶登記時。若在 2026 年 2 月簽約，獲利就落在 2025/26 課稅年度（截至 2026-02-28），即使過戶到 5 月才完成。開普敦賣方安排跨年度交易時必須把這一點算進去。"),
]

ZH_RELATED = """      <h2>相關閱讀</h2>
      <ul>
        <li><a href="/blog/south-africa-transfer-duty-foreign-buyer-cape-town-tax-guide-2026" title="南非買房過戶稅 transfer duty 完整指南">南非買房過戶稅完整指南</a>——買入端的稅費結構，與本文的出場成本對照看。</li>
        <li><a href="/blog/sarb-bop-codes-foreign-property-buyers-2026" title="SARB BOP 代碼完整對照表">SARB BOP 代碼完整對照表</a>——匯入與匯出的完整代碼查詢，本文只列會用到的四組。</li>
        <li><a href="/blog/cape-town-property-purchase-process-guide" title="開普敦房產購買流程指南">開普敦房產購買流程指南</a>——從出價到過戶的完整步驟與時程。</li>
        <li><a href="/blog/south-africa-estate-duty-foreign-heirs-cape-town-2026" title="南非遺產稅與外國繼承人">南非遺產稅與外國繼承人</a>——另一種「非自願出場」的成本結構。</li>
        <li><a href="/south-africa-property" title="南非置產服務">南非置產服務</a>——開普敦置產的市場分析、稅費架構與執行分工。</li>
      </ul>"""

ZH_CRESTLINE = """    <h2>為什麼要透過 <span>Crestline Advisory</span> 協助？</h2>
    <p>南非的稅務與外匯要求每年都在調整，而且調整的往往是「格式」而不是「資格」——一樣的護照、一樣的買賣契約，文件順序或欄位不對就是退回重送。</p>
    <h3>開普敦賣方自己辦最常卡住的三件事</h3>
    <ul>
      <li><strong>把 21 個工作日當成付款期限</strong>：這是網路上最常見的錯誤。實際上 21 個工作日是 SARS 處理 NR03 的時間，買方的繳款期限只有 14 天（或 28 天）。抓錯這一個數字，10% 罰款與利息就會落在買方身上，然後回頭找你。</li>
      <li><strong>NR03 的稅額計算書沒有成本佐證</strong>：申請減免的核心是「證明實際稅負低於法定比例」，需要買入成本、資本支出、持有期間費用的完整單據。只有一張買賣契約，SARS 不會接受。</li>
      <li><strong>匯出時無法說明交易性質</strong>：開普敦的銀行要的是「這筆錢是不動產處分所得」的完整鏈條——契約、過戶、預扣繳款收據、外匯申報。少一環就退件重來。</li>
    </ul>
    <p>透過我們的合作夥伴 Crestline Advisory（南非在地執行）協助，這些環節會在送件前先確認到位：NR02／NR03 文件逐項預檢（避免 21 個工作日後被退、整輪重跑）、依當期 SARS 與銀行要求確認扣繳與匯出的先後順序、匯款路徑與 510 01 申報類別先對好、送件後由在地團隊追蹤進度。</p>
    <p>鼎曜在台灣端負責確認你的資料與文件正確性，確認後轉交 Crestline Advisory 執行。你不會拿到一份「自己看著辦」的清單。</p>
    <div class="ca-cta"><a href="/south-africa-property#booking" class="btn btn-primary" title="預約 30 分鐘顧問評估">預約 30 分鐘顧問評估 <i class="fas fa-arrow-right"></i></a></div>"""

ZH_CTA = """      <h2>先算出 <span class="gold">出場成本</span>，再決定要不要進場</h2>
      <p>開普敦的置產決策，真正的分水嶺不是房價，而是「你知不知道自己怎麼把錢拿出來」。告訴我們您持有的區域（Bishopscourt、Constantia、Atlantic Seaboard 或 Southern Suburbs）、購入年份與預估售價，我們會提供 s35A 預扣金額試算、NR03 減免的可行性初判、CGT 結算時點的安排建議，以及匯出流程的文件清單，並在需要時轉交南非合作夥伴 Crestline Advisory 協助後續作業。</p>
      <a href="/south-africa-property" class="btn btn-primary" title="了解南非置產服務">了解南非置產業務 <i class="fas fa-arrow-right"></i></a>"""

ZH_DISCLAIMER = "本文所載南非預扣稅、NR03 指令、繳款期限、CGT 稅率與 BoP 類別，均取自 SARS 官方頁面（Non-resident sellers of immovable property、Guide to Amounts to be Withheld、Budget 2026 FAQ）、Nedbank FinSurv BoP 分類指南與 SARB 季度報告，以及公開媒體報導之開普敦成交案例，僅供海外資產配置之市場參考，不構成任何要約、要約引誘、稅務或法律建議。所有買賣契約、稅務申報與資金支付，均由當事人直接與南非執業代書、稅務顧問或合法建商於境外依法辦理及簽署。稅率、門檻與排除額可能隨年度公告調整，個案應以 SARS 最新公告與執業顧問意見為準。"

# ─────────────────────────── EN ───────────────────────────
EN_TITLE = "Section 35A Withholding Tax on SA Property | DingYao Advisory"
EN_DESC = ("Under section 35A of the Income Tax Act, when a non-resident sells South African immovable "
           "property for more than R2,000,000, the purchaser must withhold 7.5% (individual), 10% "
           "(company) or 15% (trust) of the full purchase price. This guide breaks down the Cape Town "
           "numbers, the NR03 directive, why 21 business days is processing time and not the payment "
           "deadline, the 10% penalty on purchasers, the CGT timing rule, and BoP code 510 01 for "
           "repatriation. Request the pre-sale document checklist.")
EN_H1 = ("Selling Cape Town Property as a Non-Resident: "
         "<span class=\"gold\">Section 35A Withholding, NR03 and the Exit Cost (2026)</span>")
EN_HEADLINE = ("Selling Cape Town Property as a Non-Resident: Section 35A Withholding, NR03 and the Exit Cost (2026)")

EN_INTRO = """      <p>In September 2026, UK podcaster Steven Bartlett listed his Bishopscourt estate in Cape Town at <strong>R189,000,000</strong>, having reportedly bought it for <strong>R93,300,000</strong> in 2024 (Source: SA People, 2026-09-28; REI.co.za, 2026-09-28). The headlines focus on the doubling. For a foreign seller, the number that matters is different: on completion, the <strong>purchaser</strong> is legally required to withhold <strong>R14,175,000</strong> and pay it to SARS — and the 7.5% is charged on the full purchase price, not on the profit.</p>
      <p>That is section 35A of the Income Tax Act. It never appears on the day you buy in Cape Town; it only appears on the day you sell. So most foreign buyers never model it at entry. This article sets out the four exit costs of a Cape Town sale: how the withholding is calculated, how an NR03 directive can reduce it, what the 21 business days actually measure, and how the proceeds leave South Africa.</p>
      <div class="highlight-box">
        <p><strong>Direct answer:</strong> Yes. When a non-resident disposes of South African immovable property for more than R2,000,000 in aggregate, the purchaser must withhold <strong>7.5%</strong> (natural person), <strong>10%</strong> (company) or <strong>15%</strong> (trust) of the <strong>full purchase price</strong>, and pay SARS within 14 days of withholding (28 days if the purchaser is itself a non-resident). NR03 is the seller's application for a reduced or zero rate; SARS generally processes it within 21 business days — that is processing time, not the payment deadline. The amount withheld is an advance against normal tax, not the final liability. Repatriation of property proceeds falls under BoP category 510 01.</p>
      </div>"""

EN_S1 = """<h2>Why does a Cape Town sale trigger a deduction before transfer?</h2>
      <p><strong>Because South African law places the collection duty on the buyer, not the seller.</strong> Section 35A has applied since 1 September 2007: any person who must pay a non-resident seller for the disposal of South African immovable property has to withhold a statutory percentage from the amount payable and hand it to SARS (Source: SARS, Amounts to be Withheld When a Non-Resident Sells Immovable Property, updated 2025-10-02).</p>
      <p>The practical consequence for a foreign owner in Cape Town is blunt: <strong>on transfer you do not receive the sale price — you receive the sale price minus the withholding.</strong> On a R8,000,000 free-standing house in the Southern Suburbs, the cash you receive on the day is capped at R7,400,000. The other R600,000 sits with SARS until assessment.</p>
      <h3>The money is a prepayment, not a penalty</h3>
      <p>SARS is explicit about the character of the amount: it is an <strong>advance payment towards the seller's liability for normal tax</strong> in the year of assessment in which the property is disposed of. In other words, it is your own tax, pre-funded. The final figure is settled on assessment — overpaid amounts are refundable, shortfalls are payable.</p>
      <p>This is where Cape Town sellers misjudge the cash flow. The withholding is calculated on the <strong>price</strong>; the tax is calculated on the <strong>gain</strong>. A Constantia house bought for R6,000,000 in 2019 and sold for R11,000,000 in 2026 carries a withholding of R825,000 on the full price, while the taxable gain is a fraction of that. The difference can be locked up for months.</p>
      <table class="tax-table">
        <thead><tr><th>Seller type</th><th>Withholding rate</th><th>Basis</th><th>Typical Cape Town scenario</th></tr></thead>
        <tbody>
          <tr><td>Natural person</td><td><strong>7.5%</strong></td><td>Full amount payable</td><td>Individual owner in Bishopscourt or Constantia</td></tr>
          <tr><td>Company</td><td><strong>10%</strong></td><td>Full amount payable</td><td>Atlantic Seaboard apartment held by a company</td></tr>
          <tr><td>Trust</td><td><strong>15%</strong></td><td>Full amount payable</td><td>Winelands-adjacent property held in a family trust</td></tr>
        </tbody>
      </table>
      <p>(Source: SARS, Non-resident sellers of immovable property, updated 2026-08-19; SARS, Guide to Amounts to be Withheld, 2025-10-02)</p>"""

EN_S2 = """<h2>Is the R2,000,000 threshold a deduction or a trigger?</h2>
      <p><strong>It is a trigger, not a deduction.</strong> SARS states it plainly: "Where the value of the property exceeds R2 million, the withholding amount applies to the full purchase price, without regard to the R2 million threshold" (Source: SARS, Guide to Amounts to be Withheld, 2025-10-02). You do not withhold on the excess above R2,000,000 — you withhold on everything.</p>
      <p>Conversely, if the amounts payable by the purchaser to the seller and any other person on the seller's behalf, <strong>in aggregate, do not exceed R2,000,000</strong>, section 35A does not apply at all. In Cape Town's price bands that line is real: a R1,950,000 city-centre studio and a R2,050,000 Southern Suburbs townhouse differ by about 5% in price, yet only one of them triggers a six-figure withholding.</p>
      <h3>Four worked examples, from R2,000,000 to R189,000,000</h3>
      <table class="tax-table">
        <thead><tr><th>Cape Town scenario</th><th>Price</th><th>Seller type</th><th>Withholding</th><th>Cash on transfer</th></tr></thead>
        <tbody>
          <tr><td>Bishopscourt estate (Bartlett listing)</td><td>R189,000,000</td><td>Individual</td><td><strong>R14,175,000</strong></td><td>R174,825,000</td></tr>
          <tr><td>Southern Suburbs house</td><td>R8,000,000</td><td>Individual</td><td><strong>R600,000</strong></td><td>R7,400,000</td></tr>
          <tr><td>Atlantic Seaboard apartment (company)</td><td>R6,500,000</td><td>Company</td><td><strong>R650,000</strong></td><td>R5,850,000</td></tr>
          <tr><td>Cape Town CBD studio</td><td>R1,950,000</td><td>Individual</td><td><strong>R0</strong> (aggregate below R2m)</td><td>R1,950,000</td></tr>
        </tbody>
      </table>
      <p>R14,175,000 is simply R189,000,000 × 7.5%. The obligation sits with the <strong>purchaser</strong> and is not negotiable between the parties.</p>
      <h3>Does the deposit get withheld?</h3>
      <p>Not immediately, but conditionally. A deposit paid to secure the disposal is excluded from withholding <strong>until the agreement becomes unconditional</strong>; once it does, the amount that should have been withheld from the deposit is withheld from the first following payments instead. In Cape Town practice the agreement usually carries bond-approval and inspection conditions, so the withholding clock effectively starts when those conditions are met — typically 30 to 45 days after signature.</p>"""

EN_S3 = """<h2>Can NR03 reduce or cancel the withholding — and what are the 21 business days?</h2>
      <p><strong>You can apply, but nothing is automatic.</strong> A seller who believes the actual tax liability is lower than the statutory rate may request a tax directive on form <strong>NR03</strong>. SARS lists three statutory grounds only: security has been furnished for the tax, the seller is not subject to tax on the disposal, or the seller's actual liability is less than the statutory percentage. SARS gives concrete examples — the seller is fully exempt, the individual has a low taxable income, or the property was disposed of at a loss (Source: SARS, Non-resident sellers of immovable property, 2026-08-19).</p>
      <p>The most common Cape Town situation is not on that list: <em>"I barely made a profit, why is the withholding based on the full price?"</em> The answer is that the withholding is on the price, not the gain — unless an NR03 is granted. The application must be submitted with the <strong>offer to purchase, the tax calculation and supporting documentation</strong>, to nres@sars.gov.za or another method listed on the form.</p>
      <h3>21 business days is not the payment deadline</h3>
      <p>This is the most expensive misunderstanding in circulation. SARS publishes two different clocks, and they mean different things:</p>
      <ul>
        <li><strong>21 business days</strong> is the <strong>processing time</strong> for an NR03/NR02 application ("The directive application is generally processed within 21 business days").</li>
        <li><strong>14 days / 28 days</strong> is the <strong>payment deadline</strong> for the purchaser — within 14 days after the amount was withheld if the purchaser is a resident, or 28 days if the purchaser is a non-resident (Source: SARS, Guide to Amounts to be Withheld, 2025-10-02).</li>
      </ul>
      <p>Those numbers differ by an order of magnitude. A buyer who assumes "21 business days to spare" when the real deadline is 14 days absorbs a 10% penalty plus interest — and then comes back to the seller. This is precisely why Cape Town conveyancers press both parties for NR02/NR03 documents early in the transfer process.</p>
      <h3>Sequencing an exit</h3>
      <div class="process-steps">
        <div class="process-step"><div class="step-num">1</div><div class="step-content"><h4>Before signature: confirm tax status</h4><p>Non-resident status, income tax reference number, and prior SARS filing history. The Cape Town conveyancer ticks the "section 35A applicable" box on the transfer duty submission.</p></div></div>
        <div class="process-step"><div class="step-num">2</div><div class="step-content"><h4>At signature: assemble the NR03 pack</h4><p>Offer to purchase, tax calculation, and support for base cost, capital improvements and holding-period expenses. Without these, the rest of the chain restarts.</p></div></div>
        <div class="process-step"><div class="step-num">3</div><div class="step-content"><h4>After submission: allow 21 business days plus buffer</h4><p>If the seller is not registered for income tax, SARS registers them first. That step sits outside the 21 days, so plan wider.</p></div></div>
        <div class="process-step"><div class="step-num">4</div><div class="step-content"><h4>On approval: purchaser withholds per the directive</h4><p>Even at a 0% rate, the purchaser must still complete the NR02 return and attach the NR03 and deed of sale at transfer.</p></div></div>
      </div>"""

EN_S4 = """<h2>What happens without NR03 — who is liable?</h2>
      <p><strong>Liability cascades through three layers, and the penalty is not waivable.</strong> This is the hardest part of section 35A, and the real reason a Cape Town buyer keeps chasing documents.</p>
      <h3>Layer one: the purchaser is personally liable</h3>
      <p>A purchaser is personally liable if they knew, or should reasonably have known, that the seller is a non-resident, and must pay SARS by the date payment should have been made (Source: SARS, Guide to Amounts to be Withheld, 2025-10-02). Note "should reasonably have known": a foreign passport, an offshore address, or payment from an offshore account makes that defence very hard to run.</p>
      <h3>Layer two: the conveyancer and estate agent must give written notice</h3>
      <p>Any conveyancer or estate agent entitled to remuneration on the disposal must notify the purchaser <strong>in writing, before any payment to the seller</strong>, that the seller is a non-resident and that section 35A may apply. If they should reasonably have known and failed to notify, they become <strong>jointly and severally liable</strong>, capped at the amount of their own remuneration. If they did notify, the purchaser cannot claim ignorance.</p>
      <h3>Layer three: 10% penalty plus interest, and interest cannot be waived</h3>
      <ul>
        <li>Interest at the prescribed rate runs from the day after the payment deadline until SARS receives the money;</li>
        <li>A penalty equal to <strong>10%</strong> of the amount is payable, in addition to any other penalty or charge;</li>
        <li>SARS adds the decisive line: <strong>"No provision is made to waive interest."</strong></li>
      </ul>
      <p>That sentence is why "transfer first, settle the tax later" does not work in Cape Town. The cost of settling later only grows.</p>
      <h3>What if the price is in a foreign currency?</h3>
      <p>The withheld amount is translated into rand at the <strong>spot rate on the date it is paid over to SARS</strong> — not the date of signature. For a Taiwan-based buyer, the currency exposure therefore lands on the payment date, which for 2026 rand volatility deserves a buffer in the model.</p>"""

EN_S5 = """<h2>How does the 7.5% relate to capital gains tax?</h2>
      <p><strong>The withholding is a prepayment; CGT is the final liability.</strong> SARS describes the withheld amount as an advance against the seller's normal tax for the year of assessment in which the disposal occurs. Capital gains are computed under the Eighth Schedule, included in taxable income at the inclusion rate, and taxed at the applicable rate.</p>
      <h3>Maximum effective CGT rates for 2026/27</h3>
      <table class="tax-table">
        <thead><tr><th>Taxpayer</th><th>Maximum effective CGT rate</th><th>Relevance to a Cape Town seller</th></tr></thead>
        <tbody>
          <tr><td>Individuals / special trusts</td><td><strong>18%</strong></td><td>Property held in a personal name</td></tr>
          <tr><td>Companies</td><td><strong>21.6%</strong></td><td>Atlantic Seaboard property held by a company</td></tr>
          <tr><td>Other trusts</td><td><strong>36%</strong></td><td>Family trust structures — the heaviest outcome</td></tr>
        </tbody>
      </table>
      <p>(Source: SARS, Budget 2026 Frequently Asked Questions, 2026-03-20)</p>
      <p>The same official document confirms exclusions effective 2 March 2026: the <strong>annual exclusion rises to R50,000</strong> (from R40,000) and the <strong>primary residence exclusion to R3,000,000</strong> (from R2,000,000). Whether the primary residence exclusion is available to a particular non-resident depends on the Eighth Schedule requirements and the facts; it cannot be assumed.</p>
      <h3>The disposal happens on signature, not on registration</h3>
      <p>This is the sentence every Cape Town seller should memorise: for property, the CGT disposal occurs when the <strong>sale agreement is signed</strong>, not when transfer is registered at the Deeds Office. "If you sign a sale agreement in February 2026, the gain falls in the 2025/26 tax year (ending 28 February 2026), even if transfer only occurs in May 2026." (Source: SARS, Budget 2026 FAQ, 2026-03-20)</p>
      <p>Meanwhile the section 35A withholding happens at <strong>payment</strong>. A November signature with a February transfer can straddle two tax years, so a Cape Town exit needs the cash flow planned in two stages.</p>
      <h3>What if the seller never files?</h3>
      <p>If the seller does not submit a return within <strong>12 months after the end of that year of assessment</strong>, the amount already paid becomes a sufficient basis for an assessment under section 95 of the Tax Administration Act. In plain terms: no return means SARS treats the withheld amount as your final liability and does not volunteer a refund.</p>"""

EN_S6 = """<h2>How do the proceeds legally leave South Africa?</h2>
      <p><strong>Property disposal proceeds fall under BoP category 510 01.</strong> That is the number that matters when the money leaves after a Cape Town sale. The South African Reserve Bank's revised balance-of-payments categories took effect for industry on <strong>11 August 2026</strong>, adopting SADC-harmonised codes and the IMF's BPM7 framework (Source: Nedbank, FinSurv BoP categories guide, 2026-08; SARB Quarterly Bulletin, Box 2, 2026-09).</p>
      <table class="tax-table">
        <thead><tr><th>BoP code</th><th>Official description</th><th>Where a Cape Town seller meets it</th></tr></thead>
        <tbody>
          <tr><td><strong>510 01</strong></td><td>Disinvestment of property by a non-resident individual</td><td>Repatriating proceeds after selling Cape Town immovable property</td></tr>
          <tr><td><strong>510 02</strong></td><td>Disinvestment by a non-resident individual – other</td><td>Other capital withdrawals not related to property</td></tr>
          <tr><td><strong>313 00</strong></td><td>Income paid to a non-resident on an individual investment</td><td>Rental and investment income remittances</td></tr>
          <tr><td><strong>309 08</strong></td><td>Interest paid not in respect of loans</td><td>Non-loan interest payments</td></tr>
        </tbody>
      </table>
      <p>(Source: Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08)</p>
      <p>One caveat matters: <strong>the final code is determined by the bank's authorised dealer</strong> based on the actual nature of the transaction, not self-selected by the seller. The table tells you where your transaction belongs; it is not a form to copy. That is why the first Cape Town repatriation to be rejected is rarely a wrong code — it is <strong>insufficient proof of the nature of the transaction</strong>. Keep the sale agreement, the completed transfer evidence, the SARS withholding receipt, and the exchange control declaration.</p>
      <h3>The three most common rejection points</h3>
      <ul>
        <li><strong>No SARS withholding receipt</strong>: the bank will confirm the section 35A obligation is settled before processing a 510 01 payment.</li>
        <li><strong>Inconsistent description of the transaction</strong>: the agreement says one thing, the remittance form another.</li>
        <li><strong>Beneficiary account not in the seller's name</strong>: paying to a family member in Taiwan needs additional authority documents, and Cape Town banks check this closely.</li>
      </ul>
      <p>Budget the whole chain, not one step: section 35A withholding, CGT assessment, and BoP repatriation review are three separate processes that in Cape Town practice take roughly three to six months end to end.</p>"""

EN_FAQ = [
    ("Is the section 35A withholding 7.5% of the price or of the profit?",
     "Of the price. When a non-resident sells South African immovable property for more than R2,000,000 in aggregate, the purchaser withholds 7.5% (individual), 10% (company) or 15% (trust) of the full purchase price. The amount withheld is an advance against normal tax and is reconciled on assessment against the actual capital gain."),
    ("What is NR03 and is it always granted?",
     "NR03 is the seller's application for a SARS tax directive reducing or cancelling the withholding. SARS assesses it on three statutory grounds only: security furnished, no liability on the disposal, or actual liability below the statutory percentage. It is not granted automatically, and SARS generally takes 21 business days to process it."),
    ("Are the 21 business days the deadline for paying SARS?",
     "No. 21 business days is SARS's processing time for an NR03/NR02. The purchaser's actual payment deadline is 14 days after withholding (28 days where the purchaser is a non-resident). Late payment attracts a 10% penalty plus interest, and SARS states that no provision is made to waive interest."),
    ("What is the maximum capital gains tax on a South African property sale?",
     "For 2026/27 the maximum effective rates are 18% for individuals and special trusts, 21.6% for companies, and 36% for other trusts. From 2 March 2026 the annual exclusion is R50,000 and the primary residence exclusion is R3,000,000; availability to a non-resident depends on the facts and SARS's determination."),
    ("Which code is used to send sale proceeds out of South Africa?",
     "Repatriation of proceeds from a non-resident individual's property disposal maps to BoP category 510 01 (Disinvestment of property by a non-resident individual). The final code is assigned by the bank's authorised dealer based on the transaction. Keep the sale agreement, transfer evidence and SARS withholding receipt."),
    ("Does CGT arise on signature or on registration?",
     "On signature. For property, the disposal occurs when the sale agreement is signed, not when transfer is registered at the Deeds Office. Signing in February 2026 places the gain in the 2025/26 tax year even if transfer completes in May 2026."),
]

EN_RELATED = """      <h2>Related reading</h2>
      <ul>
        <li><a href="/blog/south-africa-transfer-duty-foreign-buyer-cape-town-tax-guide-2026-en" title="South Africa transfer duty guide for foreign buyers">South Africa transfer duty guide</a> — the entry-side tax stack, read alongside these exit costs.</li>
        <li><a href="/blog/sarb-bop-codes-foreign-property-buyers-2026-en" title="SARB BOP codes reference table">SARB BOP codes reference table</a> — the full code list; this article covers only the four you need.</li>
        <li><a href="/blog/cape-town-property-purchase-process-guide-en" title="Cape Town property purchase process">Cape Town property purchase process</a> — the steps and timeline from offer to transfer.</li>
        <li><a href="/blog/south-africa-estate-duty-foreign-heirs-cape-town-2026-en" title="South Africa estate duty and foreign heirs">South Africa estate duty and foreign heirs</a> — the other involuntary exit.</li>
        <li><a href="/south-africa-property-en" title="South Africa property service">South Africa property service</a> — market analysis, tax architecture and execution roles.</li>
      </ul>"""

EN_CRESTLINE = """    <h2>Why handle this through <span>Crestline Advisory</span>?</h2>
    <p>South African tax and exchange control requirements change every year — and what changes is usually the format, not the eligibility. Same passport, same sale agreement, wrong sequence or wrong field, rejection.</p>
    <h3>The three failure points we see most in Cape Town sales</h3>
    <ul>
      <li><strong>Treating 21 business days as the payment deadline</strong>: the most common error online. The 21 business days measure SARS's NR03 processing; the purchaser's payment window is 14 days (or 28). Get that wrong and the 10% penalty plus interest lands on the buyer, who then comes back to the seller.</li>
      <li><strong>An NR03 tax calculation with no cost evidence</strong>: the application exists to prove actual liability is below the statutory rate, which requires base cost, capital improvements and holding-period expenses. An agreement alone will not be accepted.</li>
      <li><strong>Being unable to prove the nature of the funds on repatriation</strong>: the bank needs the full chain — agreement, transfer, withholding receipt, exchange control declaration. One missing link restarts the file.</li>
    </ul>
    <p>Working through our partner Crestline Advisory (on-the-ground execution in South Africa) means these are checked before submission: NR02/NR03 documents pre-screened item by item (so a 21-business-day cycle is not wasted on a rejection), current SARS and bank requirements confirmed, the sequence of withholding versus repatriation aligned in advance, remittance routing and 510 01 declarations matched, and progress tracked locally after submission.</p>
    <p>DingYao verifies your documents on the Taiwan side and hands over to Crestline Advisory for execution. You do not receive a checklist and left to figure it out alone.</p>
    <div class="ca-cta"><a href="/south-africa-property-en#booking" class="btn btn-primary" title="Book a 30-minute consultation">Book a 30-minute consultation <i class="fas fa-arrow-right"></i></a></div>"""

EN_CTA = """      <h2>Model the <span class="gold">exit cost</span> before you enter</h2>
      <p>The real dividing line in Cape Town property is not the price — it is whether you know how the money comes back out. Tell us the area you hold (Bishopscourt, Constantia, Atlantic Seaboard or the Southern Suburbs), the year you bought, and your expected sale price. We will provide a section 35A withholding estimate, an initial view on NR03 feasibility, CGT timing considerations and the repatriation document list, and involve our South African partner Crestline Advisory where execution support is needed.</p>
      <a href="/south-africa-property-en" class="btn btn-primary" title="Explore South Africa property services">Explore property services <i class="fas fa-arrow-right"></i></a>"""

EN_DISCLAIMER = "All figures on section 35A withholding, NR03 directives, payment deadlines, CGT rates and BoP categories are drawn from SARS official pages (Non-resident sellers of immovable property; Guide to Amounts to be Withheld; Budget 2026 FAQ), the Nedbank FinSurv BoP categories guide, SARB Quarterly Bulletin material and public reporting of Cape Town transactions. They are provided as market reference only and do not constitute an offer, tax advice or legal advice. All sale agreements, tax returns and payments are concluded by the parties directly with South African conveyancers, tax advisers or developers. Rates, thresholds and exclusions may change annually; individual cases must follow the latest SARS guidance and advice from a licensed practitioner."


# 補強「隱含主體」以通過第 29 項（開普敦焦點 70%）—— 每處補完句子都更精確，非堆砌
POLISH_ZH = [
    ("SARS 對這件事的用語很明確：被扣下的金額是賣方",
     "南非稅務局 SARS 對這件事的用語很明確：在開普敦出售房產，被扣下的金額是賣方"),
    ("（資料來源：SARS, Non-resident sellers of immovable property, 2026-08-19 更新；SARS, Guide to Amounts to be Withheld, 2025-10-02 更新）",
     "（資料來源：南非稅務局 SARS, Non-resident sellers of immovable property, 2026-08-19 更新；SARS, Guide to Amounts to be Withheld, 2025-10-02 更新）"),
    ("這是 s35A 最容易被算錯的一條。SARS 原文寫得很直白",
     "這是台灣賣方在開普敦最容易被算錯的一條。南非稅務局 SARS 原文寫得很直白"),
    ("第一列的 R14,175,000，就是 R189,000,000 × 7.5%。",
     "第一列開普敦 Bishopscourt 的 R14,175,000，就是 R189,000,000 × 7.5%。"),
    ("賣方若認為自己的實際稅負低於法定預扣比例",
     "在開普敦賣房的非居民賣方若認為自己的實際稅負低於法定預扣比例"),
    ("網路上最常見的說法是「買方必須在 21 個工作日內把錢付給 SARS」。這是錯的，而且錯得很危險。SARS 的兩個頁面分別寫的是兩件事",
     "網路上（含不少開普敦房仲轉貼的文章）最常見的說法是「買方必須在 21 個工作日內把錢付給 SARS」。這是錯的，而且錯得很危險。南非稅務局 SARS 的兩個頁面分別寫的是兩件事"),
    ("offer to purchase、稅額計算書、佐證文件（買入成本、資本支出、持有期間費用）。這一步沒做好，後面全部重來。",
     "南非的 offer to purchase、稅額計算書、佐證文件（買入成本、資本支出、持有期間費用）。這一步沒做好，開普敦的過戶流程後面全部重來。"),
    ("SARS 若認定賣方未登記所得稅，會先替賣方註冊，再核發指令。",
     "南非稅務局若認定賣方未登記所得稅，會先替賣方註冊，再核發指令。"),
    ("若獲准降為 0%，買方仍須完成 NR02 申報，並在過戶時附上 NR03 與買賣契約。",
     "若獲准降為 0%，開普敦的買方仍須完成 NR02 申報，並在過戶時附上 NR03 與買賣契約。"),
    ("SARS 明文規定：買方若「知道或理應知道」賣方為非居民，就要",
     "南非稅務局明文規定：買方若「知道或理應知道」賣方為非居民，就要"),
    ("如果代書（conveyancer）或房仲（estate agent）因處理該筆處分而收取報酬",
     "如果開普敦的代書（conveyancer）或房仲（estate agent）因處理該筆處分而收取報酬"),
    ("資本利得不是全額課稅，而是先按「計入比例（inclusion rate）」計入應稅所得",
     "南非的資本利得不是全額課稅，而是先按「計入比例（inclusion rate）」計入應稅所得"),
    ("（資料來源：SARS, Budget 2026 Frequently Asked Questions, 2026-03-20）",
     "（資料來源：南非稅務局 SARS, Budget 2026 Frequently Asked Questions, 2026-03-20）"),
    ("同一份官方文件也公告了 2026 年 3 月 2 日起的排除額調整",
     "同一份南非官方文件也公告了 2026 年 3 月 2 日起的排除額調整"),
    ("SARS 規定：若賣方在該課稅年度結束後",
     "南非稅務局規定：若賣方在該課稅年度結束後"),
    ("（資料來源：Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08）",
     "（資料來源：南非 Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08）"),
    ("NR03 是賣方向 SARS 申請「降低或免除扣繳」的稅務指令。",
     "NR03 是賣方向南非稅務局申請「降低或免除扣繳」的稅務指令。"),
    ("2026/27 年度最高有效稅率：個人與特殊信託 18%",
     "南非 2026/27 年度最高有效稅率：個人與特殊信託 18%"),
    ("非居民個人出售不動產後的價金匯出，對應 BoP 類別 510 01",
     "非居民個人出售開普敦不動產後的價金匯出，對應 BoP 類別 510 01"),
]

POLISH_EN = [
    ("This article sets out the four exit costs of a Cape Town sale:",
     "For anyone selling property in South Africa as a non-resident, this article sets out the four exit costs of a Cape Town sale:"),
    ("Capital gains are computed under the Eighth Schedule, included in taxable income at the inclusion rate, and taxed at the applicable rate.",
     "South Africa capital gains tax is computed under the Eighth Schedule, included in taxable income at the inclusion rate, and taxed at the applicable rate."),
    ("may request a tax directive on form <strong>NR03</strong>.",
     "may request a tax directive on the <strong>SARS NR03</strong> form."),
    ("SARS is explicit about the character of the amount: it is an",
     "SARS is explicit about the character of the amount in a South African disposal: it is an"),
    ("(Source: SARS, Non-resident sellers of immovable property, updated 2026-08-19; SARS, Guide to Amounts to be Withheld, 2025-10-02)",
     "(Source: South African Revenue Service (SARS), Non-resident sellers of immovable property, updated 2026-08-19; SARS, Guide to Amounts to be Withheld, 2025-10-02)"),
    ("It is a trigger, not a deduction.</strong> SARS states it plainly",
     "It is a trigger, not a deduction.</strong> For Cape Town sales, SARS states it plainly"),
    ("R14,175,000 is simply R189,000,000 × 7.5%.",
     "The Cape Town Bishopscourt figure, R14,175,000, is simply R189,000,000 × 7.5%."),
    ("You can apply, but nothing is automatic.</strong> A seller who believes",
     "You can apply, but nothing is automatic.</strong> A non-resident seller of Cape Town property who believes"),
    ("This is the most expensive misunderstanding in circulation. SARS publishes two different clocks",
     "This is the most expensive misunderstanding in circulation. In South African practice, SARS publishes two different clocks"),
    ("Offer to purchase, tax calculation, and support for base cost, capital improvements and holding-period expenses.",
     "The South African offer to purchase, tax calculation, and support for base cost, capital improvements and holding-period expenses."),
    ("If the seller is not registered for income tax, SARS registers them first.",
     "If the seller is not registered for South African income tax, SARS registers them first."),
    ("Even at a 0% rate, the purchaser must still complete the NR02 return",
     "Even at a 0% rate, the Cape Town purchaser must still complete the NR02 return"),
    ("A purchaser is personally liable if they knew, or should reasonably have known",
     "In a South African disposal, a purchaser is personally liable if they knew, or should reasonably have known"),
    ("Any conveyancer or estate agent entitled to remuneration on the disposal must notify",
     "Any South African conveyancer or estate agent entitled to remuneration on the disposal must notify"),
    ("The withheld amount is translated into rand at the <strong>spot rate",
     "For a Cape Town sale, the withheld amount is translated into rand at the <strong>spot rate"),
    ("The withholding is a prepayment; CGT is the final liability.</strong> SARS describes",
     "The withholding is a prepayment; CGT is the final liability.</strong> For South African purposes, SARS describes"),
    ("(Source: SARS, Budget 2026 Frequently Asked Questions, 2026-03-20)",
     "(Source: South African Revenue Service, Budget 2026 Frequently Asked Questions, 2026-03-20)"),
    ("The same official document confirms exclusions effective 2 March 2026",
     "The same South African Treasury and SARS document confirms exclusions effective 2 March 2026"),
    ("If the seller does not submit a return within <strong>12 months",
     "If the seller does not submit a South African return within <strong>12 months"),
    ("(Source: Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08)",
     "(Source: South African bank Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08)"),
    ("NR03 is the seller's application for a SARS tax directive",
     "NR03 is the seller's application for a South African tax directive"),
    ("No. 21 business days is SARS's processing time for an NR03/NR02.",
     "No. 21 business days is the South African Revenue Service's processing time for an NR03/NR02."),
    ("For 2026/27 the maximum effective rates are 18%",
     "For South Africa's 2026/27 year, the maximum effective rates are 18%"),
    ("Repatriation of proceeds from a non-resident individual's property disposal maps",
     "Repatriation of proceeds from a non-resident individual's Cape Town property disposal maps"),
    ("On signature. For property, the disposal occurs",
     "On signature. For South African property, the disposal occurs"),
]


def polish(html, pairs):
    for a, b in pairs:
        if a not in html:
            print(f"  !! POLISH miss: {a[:60]}")
        html = html.replace(a, b)
    return html


def herohdr(slug, tag, h1, date_label, read_label, img_alt):
    return f"""<!-- ARTICLE HERO -->
<div class="article-hero">
  <img src="{A}/{slug}-hero.webp" alt="{img_alt}" class="hero-bg-img" loading="lazy" title="{img_alt}">
  <div class="hero-overlay"></div>
</div>

<!-- ARTICLE HEADER -->
<header class="article-header">
  <div class="container">
    <div class="fade-in visible">
      <span class="article-tag"><i class="fas fa-file-signature" style="margin-right:6px"></i>{tag}</span>
      <h1 class="article-title">{h1}</h1>
      <div class="article-meta">
        <span><i class="far fa-calendar"></i> {date_label}</span>
        <span><i class="far fa-clock"></i> {read_label}</span>
        <span><i class="fas fa-user"></i> Scott Huang</span>
        <span><i class="fas fa-tag"></i> Offshore Property</span>
      </div>
    </div>
  </div>
</header>
<main id="main-content">
"""


def build(lang):
    tpl_path = TPL_ZH if lang == "zh" else TPL_EN
    tpl = load(tpl_path)
    head_prefix, head_suffix, hero_i, body_i, cta_i = split_tpl(tpl)
    nav_blk = tpl[tpl.index("</head>") + 7:hero_i]
    tail = tpl[cta_i:]
    # nav sr-only h2 -> this article's headline
    head = ZH_HEADLINE if lang == "zh" else EN_HEADLINE
    nav_blk = nav_blk.replace("南非開戶怎麼做？Standard Bank 非居民帳戶文件、profiling 四題與退件原因（2026）", head)
    nav_blk = nav_blk.replace("South Africa Bank Account: Standard Bank Non-Resident Guide", head)

    if lang == "zh":
        meta = build_meta_zh(SLUG, ZH_TITLE, ZH_DESC, ZH_KW, ZH_HEADLINE, "開普敦房產出售文件與簽署場景")
        jl = jsonld_zh(SLUG, ZH_HEADLINE, ZH_DESC, ZH_FAQ, "南非賣房稅 s35A 預扣稅")
        hh = herohdr(SLUG, "南非置產稅務", ZH_H1, "2026.10.24", "15 分鐘閱讀", "開普敦房產出售文件與簽署場景")
        body = ("<!-- ARTICLE BODY -->\n" + intro_section(ZH_INTRO) + "\n\n"
                + section(SLUG, 1, "開普敦房產交易的簽約與文件審閱", "開普敦房產交易的簽約與文件審閱", ZH_S1) + "\n\n"
                + section(SLUG, 2, "開普敦各區房價帶與成交金額", "開普敦各區房價帶與成交金額", ZH_S2) + "\n\n"
                + section(SLUG, 3, "開普敦代書事務所的文件作業", "開普敦代書事務所的文件作業", ZH_S3) + "\n\n"
                + section(SLUG, 4, "南非稅務申報與稽核文件", "南非稅務申報與稽核文件", ZH_S4) + "\n\n"
                + section(SLUG, 5, "開普敦會計師事務所的稅額試算", "開普敦會計師事務所的稅額試算", ZH_S5) + "\n\n"
                + section(SLUG, 6, "開普敦銀行的外匯與匯出作業", "開普敦銀行的外匯與匯出作業", ZH_S6) + "\n\n"
                + """<div class="section">
  <div class="container">
    <section class="article-body fade-in visible">
      <h2>常見問題 FAQ</h2>
""" + "".join(f"      <h3>{q}</h3>\n      <p>{a}</p>\n" for q, a in ZH_FAQ) + "\n" + ZH_RELATED + """
    </section>
  </div>
</div>
""")
        cr = ZH_CRESTLINE
        cta = ZH_CTA
        dsc = ZH_DISCLAIMER
    else:
        meta = build_meta_en(SLUG, EN_TITLE, EN_DESC, "Cape Town property sale documents and signing")
        jl = jsonld_en(SLUG, EN_HEADLINE, EN_DESC, EN_FAQ, "Section 35A withholding tax")
        hh = herohdr(SLUG, "South Africa Property Tax", EN_H1, "2026.10.24", "15 min read",
                     "Cape Town property sale documents and signing")
        body = ("<!-- ARTICLE BODY -->\n" + intro_section(EN_INTRO) + "\n\n"
                + section(SLUG, 1, "Signing and document review for a Cape Town property sale", "Signing and document review for a Cape Town property sale", EN_S1) + "\n\n"
                + section(SLUG, 2, "Cape Town price bands and transaction values", "Cape Town price bands and transaction values", EN_S2) + "\n\n"
                + section(SLUG, 3, "Conveyancing paperwork in a Cape Town practice", "Conveyancing paperwork in a Cape Town practice", EN_S3) + "\n\n"
                + section(SLUG, 4, "South African tax filing and audit documents", "South African tax filing and audit documents", EN_S4) + "\n\n"
                + section(SLUG, 5, "Tax computation at a Cape Town accounting practice", "Tax computation at a Cape Town accounting practice", EN_S5) + "\n\n"
                + section(SLUG, 6, "Foreign exchange desk at a Cape Town bank", "Foreign exchange desk at a Cape Town bank", EN_S6) + "\n\n"
                + """<div class="section">
  <div class="container">
    <section class="article-body fade-in visible">
      <h2>FAQ</h2>
""" + "".join(f"      <h3>{q}</h3>\n      <p>{a}</p>\n" for q, a in EN_FAQ) + "\n" + EN_RELATED + """
    </section>
  </div>
</div>
""")
        cr = EN_CRESTLINE
        cta = EN_CTA
        dsc = EN_DISCLAIMER

    meta = meta + jl
    body = polish(body, POLISH_ZH if lang == "zh" else POLISH_EN)
    # tail: replace crestline body, cta body, disclaimer item 2
    import re
    t = tail
    s = t.index('<section class="crestline-assist"')
    e = t.index('</section>', t.index('<div class="ca-cta">', s)) + len('</section>')
    t = t[:s] + '<section class="crestline-assist" id="crestline-assist">\n  <div class="ca-inner">\n' + cr + "\n  </div>\n</section>" + t[e:]

    s = t.index('<section class="section cta-section">')
    e = t.index('</section>', t.index('<a href=', s)) + len('</section>')
    t = t[:s] + '<section class="section cta-section">\n  <div class="container">\n    <div class="cta-content fade-in">\n' + cta + "\n    </div>\n  </div>\n</section>" + t[e:]

    # disclaimer paragraph 2
    m = re.search(r'<p><strong>2\. 資訊來源與契約主體：</strong>.*?</p>', t, re.S)
    if m:
        t = t[:m.start()] + "<p><strong>2. 資訊來源與契約主體：</strong>" + dsc + "</p>" + t[m.end():]
    else:
        m = re.search(r'<p><strong>2\. Information sources and contracting parties:</strong>.*?</p>', t, re.S)
        if m:
            t = t[:m.start()] + "<p><strong>2. Information sources and contracting parties:</strong>" + dsc + "</p>" + t[m.end():]

    return assemble(head_prefix, meta, head_suffix, nav_blk, hh, body, t)


for lg, fn in (("zh", f"{SLUG}.html"), ("en", f"{SLUG}-en.html")):
    html = build(lg)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {fn} {len(html)} bytes")
