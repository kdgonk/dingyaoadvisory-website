#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文章 2：south-africa-interest-remittance-to-taiwan-2026（支柱① 高利息帳戶）
   鐵律：不得與 BOP-EN 自噬 —— 英文主軸＝Taiwan-side repatriation；代碼上限 4 組。"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (load, split_tpl, build_meta_zh, build_meta_en, jsonld_zh, jsonld_en,
                     section, intro_section, assemble, TPL_ZH, TPL_EN, OUT)

SLUG = "south-africa-interest-remittance-to-taiwan-2026"
A = "https://assets.dingyaoadvisory.tw/blog/images"

ZH_TITLE = "南非幣匯回台灣完整流程：BOP 類別、匯率與申報（2026）｜鼎曜"
ZH_DESC = ("南非幣匯回台灣不是填一張表就好：利息、本金、賣房款是三種不同性質的錢，走三組不同 BoP 類別與文件。"
           "本文整理 SARB 2026-08-11 上路的 SADC 調和版分類、非居民匯出自身資金走哪一組代碼、一次匯回與分批匯回的匯率與手續費差異、"
           "南非端 15% 利息扣繳的豁免邊界（所得稅法 s50D），以及台灣端海外所得計入基本所得額的申報邏輯。附匯出前六項文件檢查。立即索取匯出檢查表。")
ZH_KW = "南非幣匯回台灣, 南非匯款, 南非外匯管制, 南非定存利息, BOP 類別, 南非非居民帳戶, 南非 BoP 510 01, 海外所得申報"

ZH_H1 = ("南非幣匯回台灣怎麼做？<span class=\"gold\">利息、本金、賣房款的三組 BoP 類別與申報實務（2026）</span>")
ZH_HEADLINE = "南非幣匯回台灣怎麼做？利息、本金、賣房款的三組 BoP 類別與申報實務（2026）"

ZH_INTRO = """      <p>錢在南非賺到，跟錢回到台灣，是兩件難度完全不同的事。2026 年 10 月，Standard Bank 的南非幣貨幣市場帳戶名目利率仍在 7% 以上（2026 年 10 月初報價約 7.10–7.45%，級距制、非保證收益），但真正讓台灣投資人卡住的，通常不是利率，而是<strong>第一次要把錢匯回來的那通電話</strong>——銀行問你「這筆錢的性質是什麼」，你答不出來，整筆就停住。</p>
      <p>這篇文章只處理「匯回」這一段：南非幣利息、本金、賣房款分別屬於三種不同的資金性質，對應三組不同的 BoP 類別與文件；2026 年 8 月 11 日上路的新分類改了什麼；一次匯回與分批匯回的差別；以及台灣端海外所得要不要申報。開戶與利率比較，站上已有專文，本文把它們放在「下一步」。</p>
      <div class="highlight-box">
        <p><strong>核心摘要：</strong>南非幣匯回台灣的第一步不是填匯款單，而是<strong>確認這筆錢的性質</strong>。利息、本金、賣房款是三種不同的錢：利息走投資收益類（如 313 00 或 309 08），本金走資本撤回類（如 510 02），非居民賣房後的價金走 510 01。南非儲備銀行自 <strong>2026-08-11</strong> 起實施 SADC 調和版 BoP 分類，最終代碼由銀行的授權外匯部門認定。南非端利息扣繳 15%，但銀行支付給外國人的利息在所得稅法 s50D 下屬豁免範圍；台灣端海外所得須計入基本所得額，申報門檻以當年度財政部公告為準。</p>
      </div>"""

ZH_S1 = """<h2>南非幣利息要匯回台灣，第一步該分清楚的是哪三種錢？</h2>
      <p><strong>先把「利息」、「本金」與「賣房款」分開，因為它們在南非的分類系統裡是三個不同的東西。</strong>這一步沒做，後面填什麼單都會被退回。開普敦與約翰尼斯堡的銀行在受理非居民匯出時，第一個問題永遠是「這筆錢的來源性質」，不是「金額多少」。</p>
      <table class="tax-table">
        <thead><tr><th>錢的性質</th><th>怎麼產生</th><th>南非端文件</th><th>匯出時的分類邏輯</th></tr></thead>
        <tbody>
          <tr><td><strong>利息</strong></td><td>南非幣定存、貨幣市場帳戶按月或按季入帳</td><td>銀行對帳單、利息通知單</td><td>投資收益類（income on financial assets）</td></tr>
          <tr><td><strong>本金</strong></td><td>當初從台灣匯入南非的原始資金</td><td>當初的匯入紀錄、外匯申報文件</td><td>資本撤回類（disinvestment – other）</td></tr>
          <tr><td><strong>賣房款</strong></td><td>出售開普敦不動產後的價金</td><td>買賣契約、過戶證明、SARS 預扣繳款收據</td><td>非居民不動產處分（510 01）</td></tr>
        </tbody>
      </table>
      <p>為什麼要分這麼細？因為南非的出口申報是<strong>逐筆按性質</strong>登錄的。把利息申報成本金，或把本金申報成投資收益，不會讓你多繳稅，但會讓這筆錢在銀行的合規審查裡「說不通」——而說不通的匯款，處理時間會從 3 個工作日變成 3 到 6 週。這是開普敦非居民帳戶最常見的延誤來源。</p>
      <h3>同一個帳戶裡的錢，可能同時是三種</h3>
      <p>一個典型的台灣投資人帳戶長這樣：2024 年從台灣匯入 R1,000,000（本金），兩年下來累積利息 R140,000（利息），2026 年再從開普敦賣掉一間小套房拿到 R1,800,000（賣房款）。這三筆在同一個帳戶餘額裡，但匯出時是三張不同的申報、三組不同的文件。銀行不會幫你分，你必須自己分。</p>"""

ZH_S2 = """<h2>SARB 在 2026 年 8 月 11 日改了什麼？為什麼舊的代碼表已經不能照抄？</h2>
      <p><strong>南非儲備銀行（SARB）自 2026 年 8 月 11 日起實施新的國際收支（BoP）分類，採 SADC 調和版代碼，並納入 IMF 第七版國際收支手冊（BPM7）架構。</strong>南非銀行的實施日明確訂在 2026-08-11（資料來源：Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08；SARB Quarterly Bulletin, Box 2, 2026-09）。</p>
      <p>這件事對台灣投資人的實際影響，不是「稅變了」，而是<strong>「你以前存下來的那份代碼表可能對不上」</strong>。Nedbank 的指南開頭就寫明：部分類別「完全改變（changed completely）」，並要求客戶重新確認每一筆交易對應的類別。中文圈流傳的許多南非匯款代碼清單，是在 2026 年 8 月之前整理的。</p>
      <h3>三件沒有變的事</h3>
      <ul>
        <li><strong>分類的責任在銀行，不在你。</strong>最終代碼由銀行的授權外匯部門（authorised dealer）依實際交易性質認定，你能做的是「把性質說清楚、文件備齊」。</li>
        <li><strong>南非的申報是逐筆的。</strong>每一筆跨境支付都要有類別，不存在「合併申報」這條路。</li>
        <li><strong>分類錯誤不是稅務問題，是流程問題。</strong>它會讓你重填、等待、再送件，但不會直接產生稅負。</li>
      </ul>
      <h3>那為什麼大家還是很緊張？</h3>
      <p>因為南非這幾年的外匯管制確實在放寬，方向卻容易讓人誤讀。2026 年預算案把<strong>居民個人的年度自主額度（Single Discretionary Allowance）由 R1,000,000 提高到 R2,000,000</strong>，夫妻合計 R4,000,000，且無須事先取得稅務合規狀態碼（TCS Pin – AIT）；投資額度（Investment Allowance）維持 R10,000,000（資料來源：SARS, Budget 2026 Frequently Asked Questions, 2026-03-20）。</p>
      <p>但那是<strong>居民</strong>的額度。非居民匯出自己的資金，走的是另一條路徑——不是「你的額度還剩多少」，而是「這筆錢的性質與來源證明」。這就是為什麼開普敦的銀行對非居民的提問方式完全不同：他們問的是<strong>出處</strong>，不是<strong>額度</strong>。把這兩件事分清楚，你就不會被網路上「南非外匯管制已經取消」這類說法誤導。</p>"""

ZH_S3 = """<h2>利息、本金、賣房款各走哪一組 BoP 類別？</h2>
      <p><strong>四組會用到的類別，其餘全部查既有對照表。</strong>依 Nedbank 公布的 SARB 分類（2026-08 版），與台灣投資人直接相關的匯出類別如下——注意這是「你的交易會落在哪一類」的對照，不是可以自行指定的欄位。</p>
      <table class="tax-table">
        <thead><tr><th>BoP 類別</th><th>官方描述</th><th>對應你的哪一筆錢</th></tr></thead>
        <tbody>
          <tr><td><strong>313 00</strong></td><td>Income paid to a non-resident on an individual investment</td><td>帳戶利息、投資收益匯出</td></tr>
          <tr><td><strong>309 08</strong></td><td>Interest paid not in respect of loans</td><td>非貸款性質的利息支付</td></tr>
          <tr><td><strong>510 02</strong></td><td>Disinvestment by a non-resident individual – other</td><td>原始本金撤回（非不動產）</td></tr>
          <tr><td><strong>510 01</strong></td><td>Disinvestment of property by a non-resident individual</td><td>出售不動產後的價金匯出</td></tr>
        </tbody>
      </table>
      <p>（資料來源：南非 Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08）</p>
      <h3>利息到底走 313 00 還是 309 08？</h3>
      <p>這是實務上最常被問的一題，也是本文最需要誠實回答的一題：<strong>兩者的界線在於「這筆利息是不是因為一筆借款而支付」。</strong>309 系列在官方分類裡是「interest paid（paid to a non-resident in respect of loans / not in respect of loans）」，也就是圍繞借貸關係設計的；313 00 則是「非居民個人投資所產生的所得」。南非幣定存與貨幣市場帳戶的利息，性質上屬於後者（投資收益），不是借貸利息。</p>
      <p>但我不會告訴你「填 313 00 就對了」——因為<strong>最終認定權在銀行的授權外匯部門</strong>，而不同銀行對「定存利息」的內部歸類慣例並不完全一致。你能做對的事是：把利息通知單、帳戶對帳單與當初的匯入紀錄一起帶去，讓銀行有一個清楚的事實基礎去歸類。這比在網路上找一份「標準答案」有用得多。</p>
      <h3>不要在本文找完整代碼表</h3>
      <p>本文刻意只列四組。完整的 SARB BoP 對照表（含匯入端、各類服務貿易與資本移轉）已在站上另一篇專文整理，用那裡查代碼、用本文排流程——兩篇是互補的，不是重複的。</p>"""

ZH_S4 = """<h2>一次匯回還是分批匯回？匯率與手續費怎麼算？</h2>
      <p><strong>沒有標準答案，但有可計算的取捨。</strong>這個問題在開普敦的非居民帳戶裡最常被問，答案取決於三件事：金額級距、你對南非幣走勢的判斷、以及你何時需要這筆台幣。</p>
      <h3>先看成本結構：三筆固定成本＋一筆比例成本</h3>
      <table class="tax-table">
        <thead><tr><th>成本項目</th><th>性質</th><th>一次匯回</th><th>分三次匯回</th></tr></thead>
        <tbody>
          <tr><td>匯出電匯手續費</td><td>固定（每筆）</td><td>付 1 次</td><td>付 3 次</td></tr>
          <tr><td>中轉行費用</td><td>固定（每筆，視路徑）</td><td>付 1 次</td><td>付 3 次</td></tr>
          <tr><td>台灣端解款手續費</td><td>固定（每筆）</td><td>付 1 次</td><td>付 3 次</td></tr>
          <tr><td>匯差（spread）</td><td>比例（約成交金額的固定百分比）</td><td>集中在一天</td><td>分散在三天</td></tr>
        </tbody>
      </table>
      <p>結構很清楚：<strong>分批匯回是用「三次固定手續費」換「匯率分散」。</strong>金額小的時候，固定成本占比高，分批不划算；金額大的時候，匯率波動的期望損失可能遠大於手續費總額。</p>
      <h3>用實際數字感覺一下</h3>
      <p>以 2026 年 10 月 23 日的參考匯率 1 南非幣 ≈ 新台幣 1.975 元計算（僅供試算，實際以交易當日銀行牌告為準）：R1,500,000 的南非幣，在 1.975 的價位約合新台幣 2,962,500 元。若匯率在三個月內從 1.975 走到 1.88（約 -4.8%），同一筆 R1,500,000 只能換到約新台幣 2,820,000 元，差額超過 14 萬台幣——這個量級遠大於三筆電匯手續費的總和。</p>
      <p>反過來說，若你在三個月內分三次匯出，平均成本會落在區間中間，不會是最差、也不會是最好的價位。這是分批的核心價值：<strong>把「猜匯率」變成「接受平均」。</strong></p>
      <h3>實務上的第三種做法</h3>
      <p>多數在開普敦有非居民帳戶的台灣投資人，最後採用的是「<strong>利息先匯、本金留著</strong>」：南非端帳戶的利息按季或半年匯回台灣支應現金流，本金繼續以南非幣計價賺取利差。這樣做的好處是每次匯出金額小、固定成本占比可預期，而且不需要對匯率下大注。缺點是本金持續暴露在南非幣的匯率風險裡——這一點必須自己清楚，不能只看名目利率。</p>
      <p>無論選哪一種，都要記得一件事：南非端帳戶的利息是<strong>市場參考區間、非保證收益</strong>，過往水準不代表未來表現，實際收益將隨南非央行政策、銀行公告與南非幣匯率變動。</p>"""

ZH_S5 = """<h2>台灣端要不要申報？海外所得怎麼計入基本所得額？</h2>
      <p><strong>要，而且申報邏輯跟一般所得完全不同。</strong>這是從南非匯回台灣時，最容易因為「不知道」而出錯的一段。台灣的個人海外所得不是併入綜合所得稅，而是計入<strong>基本所得額</strong>，適用最低稅負制（Alternative Minimum Tax）另行計算。</p>
      <h3>四個關鍵概念</h3>
      <div class="info-grid">
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-layer-group"></i></div>
          <h4>基本所得額</h4>
          <p>海外所得不是加進「綜合所得淨額」，而是加進「基本所得額」這個獨立的計算基礎。兩者分開算，再比較哪一個稅額較高。</p>
        </div>
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-percent"></i></div>
          <h4>免稅額與扣除額</h4>
          <p>基本所得額有免稅額，海外所得本身也有一個「應計入」的門檻。具體金額依《納稅者權利保護法》每兩年公告調整，<strong>以當年度財政部公告為準</strong>，本文不引用固定數字。</p>
        </div>
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-calculator"></i></div>
          <h4>與綜所稅的比較</h4>
          <p>基本稅額與一般綜所稅額比較，取較高者繳納。也就是說，海外所得不一定讓你多繳稅——但如果金額大，補稅的機率就高。</p>
        </div>
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-file-invoice"></i></div>
          <h4>申報義務</h4>
          <p>符合條件者須辦理申報，不是「有繳稅才要報」。漏報的處罰依《所得基本稅額條例》規定，與一般所得漏報不同。</p>
        </div>
      </div>
      <p>為什麼本文不寫出具體的免稅額與門檻數字？因為<strong>那兩個數字會隨公告變動，寫死會害人算錯。</strong>正確做法是：每年 5 月報稅前，以當年度財政部公告的免稅額與扣除額為準，或直接請教台灣端的記帳士。我在開普敦看過太多「用三年前的數字估算」的案例，差一個門檻，結果是補稅加罰。</p>
      <h3>哪些海外所得要算進來？</h3>
      <p>對南非投資人來說，至少三類：<strong>南非幣定存的利息所得</strong>、<strong>出售南非不動產的財產交易所得</strong>、以及<strong>其他海外投資收益</strong>。這與本文第 1 節的「三種錢」剛好對應——同一組分類，在南非是匯出申報，在台灣是所得申報。兩邊都要對得上。</p>
      <h3>南非端已經扣的稅，能不能抵？</h3>
      <p>可以，但條件嚴格。台灣與南非之間沒有生效的全面性所得稅協定，因此無法直接適用協定下的稅額扣抵；實務上須依《所得基本稅額條例》與相關解釋，就「已依外國法律繳納的所得稅」在限額內扣抵，並提出納稅證明。這一點務必由台灣端熟悉海外所得的記帳士或會計師處理，不要自行判斷——這正是本文反覆強調「文件要留」的原因：匯出時用的文件，報稅時還要再用一次。</p>"""

ZH_S6 = """<h2>匯回前該準備哪六份文件？</h2>
      <p><strong>六份，缺一不行。</strong>這份清單是依南非銀行的授權外匯部門實際會要求的項目整理的，順序也照實際送件順序排。事先備齊，可以省下 2 到 4 週的往返。</p>
      <div class="process-steps">
        <div class="process-step"><div class="step-num">1</div><div class="step-content"><h4>身分與稅務身分</h4><p>護照、南非稅號（income tax reference number）。若在 SARS 未登記所得稅，銀行會先要求註冊，這一步會多花時間。</p></div></div>
        <div class="process-step"><div class="step-num">2</div><div class="step-content"><h4>資金來源證明</h4><p>利息：銀行對帳單與利息通知單；本金：當初從台灣匯入的紀錄與外匯申報文件；賣房款：買賣契約與過戶完成證明。三者不可互相替代。</p></div></div>
        <div class="process-step"><div class="step-num">3</div><div class="step-content"><h4>南非端的稅務結清證明</h4><p>賣房款須附 SARS 的 s35A 預扣繳款收據。這是匯出 510 01 時最常缺的一份，也是最常導致退件的一份。</p></div></div>
        <div class="process-step"><div class="step-num">4</div><div class="step-content"><h4>匯出申報表與類別</h4><p>依實際交易性質填寫，由銀行審核歸類。不要自行指定代碼後再回頭找理由。</p></div></div>
        <div class="process-step"><div class="step-num">5</div><div class="step-content"><h4>收款帳戶與名義一致性</h4><p>匯入帳戶須為本人名下。若匯給配偶或家人，需額外授權文件，開普敦的銀行對這一點查得很嚴。</p></div></div>
        <div class="process-step"><div class="step-num">6</div><div class="step-content"><h4>台灣端的申報準備</h4><p>保留完整水單、匯率、手續費明細。這些是隔年 5 月申報海外所得時的原始憑證，南非端給了、台灣端還要再用一次。</p></div></div>
      </div>
      <h3>時間要怎麼抓？</h3>
      <p>南非端從送件到入帳，實務上抓 <strong>2 到 4 週</strong>是合理的；若涉及不動產處分（需要 SARS 預扣收據與產權文件），抓 <strong>6 到 10 週</strong>更安全。分批匯回時，不要把三筆排在「需要錢的前一個月」——把第一筆提前三個月啟動，是開普敦非居民帳戶最實用的一條經驗。</p>"""

ZH_FAQ = [
    ("南非幣利息匯回台灣，第一個要決定的是什麼？",
     "先決定這筆錢的性質，不是先選代碼。利息、本金、賣房款是三個不同的分類與三組不同文件。把利息申報成本金、或把本金申報成投資收益，不會多繳稅，但會讓匯款在銀行的合規審查裡說不通，處理時間可能從 3 個工作日變成 3 到 6 週。"),
    ("南非 2026 年 8 月改了什麼？舊的代碼表還能用嗎？",
     "南非儲備銀行自 2026 年 8 月 11 日起實施 SADC 調和版 BoP 分類，並納入 IMF BPM7 架構。部分類別完全改變，因此 2026 年 8 月前整理的中文代碼清單可能對不上。最終類別由銀行的授權外匯部門依交易性質認定。"),
    ("南非定存的利息要繳 15% 的扣繳稅嗎？",
     "南非對非居民的利息扣繳稅率為 15%（最終稅），但依所得稅法 s50D，南非銀行支付給外國人的利息屬豁免範圍。依 SARS Budget 2026 官方說明，利息扣繳「exempt if payable by SA government or bank」。實務上仍以銀行當期作業與個案事實為準，並須注意 s50D(2) 的 back-to-back 安排與 s50D(3) 的停留天數條款。"),
    ("匯回台灣的海外所得一定要申報嗎？",
     "符合條件者須辦理申報，不是「有繳稅才要報」。台灣的個人海外所得計入基本所得額，適用最低稅負制，與綜合所得稅分開計算後取較高者。免稅額與扣除額每兩年依公告調整，必須以當年度財政部公告為準，不可沿用舊數字。"),
    ("一次匯回比較好，還是分批匯回？",
     "取決於金額級距與你對南非幣的判斷。分批是用「多付幾筆固定手續費」換「匯率分散」，金額小時候不划算，金額大時匯率波動的期望損失通常遠大於手續費總和。實務上常見第三種做法是「利息先匯、本金留著」，把固定成本占比控制在可預期範圍。"),
    ("南非匯款到台灣通常要多久？",
     "單純利息匯出抓 2 到 4 週是合理估計；若涉及不動產處分、需附 SARS 預扣繳款收據與產權文件，抓 6 到 10 週更安全。分批匯回時，建議第一筆提前三個月啟動，不要排在需要用錢的前一個月。"),
]

ZH_RELATED = """      <h2>相關閱讀</h2>
      <ul>
        <li><a href="/blog/standard-bank-non-resident-account-2026" title="Standard Bank 非居民帳戶開戶完整手冊">Standard Bank 非居民帳戶開戶完整手冊</a>——文件清單、profiling 四題與退件原因，匯回之前先把戶開好。</li>
        <li><a href="/blog/sarb-bop-codes-foreign-property-buyers-2026" title="SARB BOP 代碼完整對照表">SARB BOP 代碼完整對照表</a>——本文只列四組，完整代碼在這裡查。</li>
        <li><a href="/blog/standard-bank-money-market" title="Standard Bank 貨幣市場帳戶利率">Standard Bank 貨幣市場帳戶利率</a>——南非幣高利活存的級距、報價與非保證收益說明。</li>
        <li><a href="/blog/south-africa-property-sale-withholding-tax-foreign-sellers-2026" title="南非賣房稅 s35A 預扣稅與匯出實算">南非賣房稅 s35A 預扣稅與匯出實算</a>——賣房款匯出前的稅務結清流程。</li>
        <li><a href="/south-africa-bank-account" title="南非開戶服務">南非開戶服務</a>——非居民帳戶的文件規格、profiling 準備與匯款路徑規劃。</li>
      </ul>"""

ZH_CRESTLINE = """    <h2>為什麼要透過 <span>Crestline Advisory</span> 協助？</h2>
    <p>南非的匯出要求每年都在調整，而且調整的往往是「分類與文件順序」而不是「資格」——一樣的護照、一樣的帳戶，性質說不清楚就是退件。</p>
    <h3>匯回時自己辦最常卡住的三件事</h3>
    <ul>
      <li><strong>把三種錢混成一筆申報</strong>：利息、本金、賣房款的分類與文件完全不同。用一個「個人匯款」的名義打包匯出，銀行會要求拆開重報，一趟往返就是 2 到 4 週。</li>
      <li><strong>缺少 SARS 的稅務結清證明</strong>：賣房款匯出時必須附 s35A 預扣繳款收據。這一張最常被漏掉，也最常導致整筆退件。</li>
      <li><strong>收款帳戶名義與匯款人不一致</strong>：匯給配偶或家人需要額外授權文件，開普敦的銀行對受益人審查很嚴，臨時補件往往趕不上既定時間表。</li>
    </ul>
    <p>透過我們的合作夥伴 Crestline Advisory（南非在地執行）協助，這些環節會在送件前先確認到位：資金性質與對應類別逐筆核對（避免用錯類別後重送）、依當期銀行要求確認文件格式與是否需要本人臨櫃、匯款路徑與中轉行先確認、以及送件後由在地團隊追蹤進度。</p>
    <p>鼎曜在台灣端負責確認你的資料與文件正確性，確認後轉交 Crestline Advisory 執行。你不會拿到一份「自己看著辦」的清單。</p>
    <div class="ca-cta"><a href="/south-africa-bank-account#booking" class="btn btn-primary" title="預約 30 分鐘顧問評估">預約 30 分鐘顧問評估 <i class="fas fa-arrow-right"></i></a></div>"""

ZH_CTA = """      <h2>先確認 <span class="gold">錢的性質與路徑</span>，再談匯率</h2>
      <p>匯回這件事，順序錯了成本最高。告訴我們您在南非的帳戶型態（定存、貨幣市場或活存）、資金來源（利息、本金或房產處分）與預計匯回的金額級距，我們會提供南非端的類別對照、文件清單、分批與一次匯回的成本比較，以及台灣端海外所得的申報方向，並在需要時轉交南非合作夥伴 Crestline Advisory 協助後續作業。</p>
      <a href="/south-africa-bank-account" class="btn btn-primary" title="了解南非開戶服務">了解南非開戶與匯款服務 <i class="fas fa-arrow-right"></i></a>"""

ZH_DISCLAIMER = "本文所載南非 BoP 分類、匯出流程、利息扣繳與稅務規定，取自南非儲備銀行（SARB）季度報告、南非 Nedbank FinSurv BoP 分類指南、SARS 官方頁面與 Budget 2026 說明文件；台灣端海外所得與最低稅負制之說明取自財政部現行公告架構，僅供海外資產配置之市場參考，不構成任何要約、要約引誘、稅務或法律建議。所有匯款、開戶契約與稅務申報，均由當事人直接與南非金融機構、台灣端記帳士或會計師依法辦理。匯率與利率均為市場參考值、非保證，實際以交易當日牌告與銀行公告為準。免稅額、扣除額與申報門檻每年度公告調整，個案應以當年度主管機關公告及執業顧問意見為準。"

# ─────────────────────────── EN ───────────────────────────
EN_TITLE = "Remit Money from South Africa to Taiwan Guide | DingYao"
EN_DESC = ("Interest, capital and sale proceeds are three different kinds of money and they leave South Africa "
           "under different BoP categories. This guide covers the SARB categories implemented on 11 August 2026, "
           "the four codes a Taiwan investor actually needs, the cost trade-off between a single transfer and "
           "staged transfers, the section 50D exemption for bank interest paid to non-residents, and how Taiwan "
           "treats the proceeds under its alternative minimum tax. Request the six-document export checklist.")
EN_H1 = ("How to Remit Money from South Africa to Taiwan: "
         "<span class=\"gold\">Three Kinds of Money, Four BoP Categories and the Reporting Rules (2026)</span>")
EN_HEADLINE = "How to Remit Money from South Africa to Taiwan: Three Kinds of Money, Four BoP Categories and the Reporting Rules (2026)"

EN_INTRO = """      <p>Earning money in South Africa and getting it back to Taiwan are two very different problems. In October 2026, a rand-denominated money market account at Standard Bank was still quoted above 7% nominal (around 7.10–7.45% in early October 2026, tiered and not a guaranteed return). But what stops most Taiwan-based investors is not the rate — it is <strong>the first phone call to move the money out</strong>, when the bank asks what the funds represent and there is no clean answer.</p>
      <p>This article deals only with the repatriation leg. Interest, capital and sale proceeds are three different kinds of money, mapped to different BoP categories and different paperwork. Here is what changed when the new categories took effect on 11 August 2026, the practical steps to transfer money from South Africa to Taiwan, the trade-off between one transfer and several, and how Taiwan taxes the proceeds. Account opening and rate comparison are covered separately.</p>
      <div class="highlight-box">
        <p><strong>Direct answer:</strong> The first step is not a remittance form — it is <strong>classifying the money</strong>. Interest, capital and property proceeds are separate: interest falls under investment income (such as 313 00 or 309 08), capital withdrawal under 510 02, and a non-resident's property sale proceeds under 510 01. The South African Reserve Bank's SADC-harmonised BoP categories took effect for industry on <strong>11 August 2026</strong>, and the final code is assigned by the bank's authorised dealer. South Africa applies a 15% final withholding on interest, but interest paid by a South African bank to a foreign person falls within the section 50D exemption; in Taiwan the amount is included in the basic income for alternative minimum tax purposes, with thresholds set by the Ministry of Finance for the year.</p>
      </div>"""

EN_S1 = """<h2>Before you remit, which three kinds of money must be separated?</h2>
      <p><strong>Interest, capital and sale proceeds — because South Africa's reporting system treats them as three different things.</strong> Get this wrong and no form will be right. If you hold a South Africa non resident bank account, the first question has nothing to do with how much you are sending: what is the nature of these funds?</p>
      <table class="tax-table">
        <thead><tr><th>Nature of funds</th><th>How it arises</th><th>South African evidence</th><th>Classification logic on exit</th></tr></thead>
        <tbody>
          <tr><td><strong>Interest</strong></td><td>Rand fixed deposit or money market account, credited monthly or quarterly</td><td>Bank statements, interest advices</td><td>Income on financial assets</td></tr>
          <tr><td><strong>Capital</strong></td><td>The original funds you transferred into South Africa</td><td>Original inward remittance record and exchange control declaration</td><td>Disinvestment – other</td></tr>
          <tr><td><strong>Sale proceeds</strong></td><td>Price received on selling Cape Town immovable property</td><td>Sale agreement, transfer evidence, SARS withholding receipt</td><td>Non-resident property disinvestment (510 01)</td></tr>
        </tbody>
      </table>
      <p>Why does the distinction matter so much? Because every cross-border payment is reported <strong>item by item, by nature</strong>. Declaring interest as capital, or capital as investment income, does not create extra tax — but it makes the payment unexplainable inside the bank's compliance review, and an unexplainable payment takes three to six weeks instead of three working days. That is the single most common source of delay in Cape Town non-resident accounts.</p>
      <h3>One account can hold all three at once</h3>
      <p>A typical Taiwan investor's account looks like this: R1,000,000 transferred in from Taiwan in 2024 (capital), R140,000 of accumulated interest (interest), and R1,800,000 received in 2026 from selling a small Cape Town apartment (sale proceeds). All three sit in one balance. On exit they require three different declarations and three different document sets. The bank will not split them for you.</p>"""

EN_S2 = """<h2>What changed on 11 August 2026 — and why old code lists no longer work?</h2>
      <p><strong>The South African Reserve Bank introduced new balance-of-payments categories effective 11 August 2026 for industry, adopting SADC-harmonised codes and the IMF's BPM7 framework.</strong> The implementation date is explicit: "The industry implementation date for the new BoP categories is 11 August 2026" (Source: Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08; SARB Quarterly Bulletin, Box 2, 2026-09).</p>
      <p>The practical effect for a Taiwan investor is not "the tax changed". It is that <strong>the code list you saved may no longer map</strong>. The Nedbank guide states plainly that some categories "have changed completely" and asks clients to re-confirm each transaction's category. Much of the Chinese-language material circulating online was compiled before August 2026.</p>
      <h3>Three things that did not change</h3>
      <ul>
        <li><strong>Classification is the bank's job, not yours.</strong> The final code is determined by the authorised dealer from the actual nature of the transaction. Your job is to make the nature provable.</li>
        <li><strong>Reporting is per payment.</strong> There is no consolidated declaration for cross-border payments out of South Africa.</li>
        <li><strong>A wrong code is a process problem, not a tax problem.</strong> It causes resubmission and delay, not an immediate liability.</li>
      </ul>
      <h3>So why does everyone sound nervous?</h3>
      <p>Because South Africa foreign exchange control has genuinely been relaxing, and the direction is easy to misread. Budget 2026 doubled the <strong>Single Discretionary Allowance for resident individuals from R1,000,000 to R2,000,000 per year</strong> (R4,000,000 for a married couple) without requiring a Tax Compliance Status Pin – Approved International Transfer; the Investment Allowance remains R10,000,000 (Source: SARS, Budget 2026 Frequently Asked Questions, 2026-03-20).</p>
      <p>Those are <strong>resident</strong> allowances. A non-resident remitting their own funds follows a different path: the question is not how much allowance remains, but what the money is and whether you can prove its origin. That is why a Cape Town bank asks a non-resident about <strong>source</strong>, never about <strong>quota</strong>. Keeping those two concepts apart is the best defence against the online claim that "South African exchange control is gone".</p>"""

EN_S3 = """<h2>Which BoP category applies to interest, capital and sale proceeds?</h2>
      <p><strong>Four categories cover the realistic cases; everything else belongs in the reference table.</strong> Under the SARB categories published by Nedbank (2026-08 version), the outward codes relevant to a Taiwan investor are below. These describe where your transaction belongs — they are not fields you may assign yourself.</p>
      <table class="tax-table">
        <thead><tr><th>BoP category</th><th>Official description</th><th>Which of your funds it covers</th></tr></thead>
        <tbody>
          <tr><td><strong>313 00</strong></td><td>Income paid to a non-resident on an individual investment</td><td>Account interest and investment income remitted abroad</td></tr>
          <tr><td><strong>309 08</strong></td><td>Interest paid not in respect of loans</td><td>Interest payments not arising from a loan relationship</td></tr>
          <tr><td><strong>510 02</strong></td><td>Disinvestment by a non-resident individual – other</td><td>Withdrawal of original capital (non-property)</td></tr>
          <tr><td><strong>510 01</strong></td><td>Disinvestment of property by a non-resident individual</td><td>Proceeds from a property disposal</td></tr>
        </tbody>
      </table>
      <p>(Source: South African bank Nedbank, FinSurv BoP categories guide, Version 20250622/v003, 2026-08)</p>
      <h3>Interest: 313 00 or 309 08?</h3>
      <p>This is the question we are asked most often, and it deserves an honest answer: <strong>the dividing line is whether the interest arises from a loan.</strong> The 309 series in the official schedule is built around lending relationships ("interest paid to a non-resident in respect of loans / not in respect of loans"); 313 00 covers income paid to a non-resident on an individual investment. Rand fixed-deposit and money market interest is investment income, not loan interest.</p>
      <p>What we will not tell you is "just use 313 00". The final determination sits with the bank's authorised dealer, and internal mapping habits for deposit interest differ between banks. What you can control is the factual base you hand over: the interest advice, the account statements, and the original inward remittance record. That is worth more than any "standard answer" found online.</p>
      <h3>Deliberately not a full code table</h3>
      <p>This article lists four categories on purpose. The complete SARB BoP schedule — inward payments, services trade and capital transfers — is maintained in a separate reference article. Use that one to look up a code; use this one to sequence a repatriation. They are complementary, not duplicates.</p>"""

EN_S4 = """<h2>One transfer or several — and how do the costs actually compare?</h2>
      <p><strong>There is no universal answer, but the trade-off is calculable.</strong> The decision turns on three things: the size of the amount, your view on the rand, and when you actually need the Taiwan dollars.</p>
      <h3>The cost structure: three fixed costs and one proportional cost</h3>
      <table class="tax-table">
        <thead><tr><th>Cost item</th><th>Type</th><th>Single transfer</th><th>Three transfers</th></tr></thead>
        <tbody>
          <tr><td>Outward telegraphic transfer fee</td><td>Fixed per payment</td><td>Paid once</td><td>Paid three times</td></tr>
          <tr><td>Correspondent bank charges</td><td>Fixed per payment, route dependent</td><td>Paid once</td><td>Paid three times</td></tr>
          <tr><td>Taiwan receiving bank fee</td><td>Fixed per payment</td><td>Paid once</td><td>Paid three times</td></tr>
          <tr><td>Exchange spread</td><td>Proportional to amount</td><td>Concentrated on one day</td><td>Averaged over three days</td></tr>
        </tbody>
      </table>
      <p>The structure is simple: <strong>staging buys currency diversification with additional fixed fees.</strong> For small amounts the fixed costs dominate and staging does not pay. For large amounts, the expected cost of currency movement usually dwarfs the fees.</p>
      <h3>What it looks like in numbers</h3>
      <p>Using the reference rate of roughly 1 rand = NT$1.975 on 23 October 2026 (illustration only; the bank's rate on the transaction date governs): R1,500,000 is about NT$2,962,500. If the rate moved from 1.975 to 1.88 over three months (about −4.8%), the same R1,500,000 would convert to roughly NT$2,820,000 — a difference above NT$140,000, far more than three sets of wire fees.</p>
      <p>Conversely, three transfers spread over three months land near the middle of the range — never the best price, never the worst. That is the real value of staging: <strong>it converts "guessing the rate" into "accepting the average".</strong></p>
      <h3>The third option most people end up using</h3>
      <p>Most Taiwan investors with a Cape Town non-resident account settle on <strong>remitting interest, retaining capital</strong>: interest is sent back quarterly or half-yearly to fund cash flow in Taiwan, while the capital stays rand-denominated to earn the differential. Each transfer is small, the fixed-cost ratio is predictable, and no large currency bet is required. The cost is continued rand exposure on the capital — which must be understood, not ignored in favour of the headline rate.</p>
      <p>Whichever route you take, remember that rand deposit rates are a <strong>market reference range, not a guaranteed return</strong>; past levels do not indicate future performance, and actual returns will move with SARB policy, bank pricing and the rand.</p>"""

EN_S5 = """<h2>Does Taiwan tax it — and how does it enter the basic income?</h2>
      <p><strong>Yes, and the mechanics are entirely different from ordinary income.</strong> This is the segment most often missed when money arrives from South Africa. Taiwan does not add overseas income to the consolidated income tax calculation; it is included in the <strong>basic income</strong> and assessed separately under the alternative minimum tax.</p>
      <h3>Four concepts that matter</h3>
      <div class="info-grid">
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-layer-group"></i></div>
          <h4>Basic income</h4>
          <p>Overseas income is added to a separate base, not to net consolidated income. The two are computed independently and the higher tax amount is payable.</p>
        </div>
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-percent"></i></div>
          <h4>Exemption and deduction</h4>
          <p>The basic income exemption and the threshold above which overseas income must be included are adjusted by public announcement, generally every two years. The amounts for the year govern; this article deliberately quotes no fixed figure.</p>
        </div>
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-calculator"></i></div>
          <h4>Comparison with ordinary tax</h4>
          <p>The basic tax amount is compared with the ordinary consolidated tax amount and the higher is paid. Overseas income does not automatically increase your bill — but at larger amounts it usually does.</p>
        </div>
        <div class="info-card">
          <div class="ic-icon"><i class="fas fa-file-invoice"></i></div>
          <h4>Filing duty</h4>
          <p>Those who meet the conditions must file, not merely those who owe tax. Penalties for omission fall under the separate statute and differ from ordinary income omissions.</p>
        </div>
      </div>
      <p>Why no absolute thresholds here? Because those figures change by announcement, and hard-coding them causes real errors. Confirm the exemption and deduction for the filing year with Taiwan's Ministry of Finance, or with a local accountant. In Cape Town we have seen too many cases costed on figures three years out of date — one threshold off, and the outcome is tax plus penalty.</p>
      <h3>Which overseas income counts?</h3>
      <p>For a South Africa investor, at least three streams: <strong>rand deposit interest</strong>, <strong>gain on the disposal of South African immovable property</strong>, and <strong>other offshore investment returns</strong>. Note that these map exactly onto the "three kinds of money" in section one — the same classification that drives South African export reporting also drives Taiwanese income reporting. Both sides must reconcile.</p>
      <h3>Can South African tax already paid be credited?</h3>
      <p>In principle yes, but the conditions are strict. There is no comprehensive income tax treaty in force between Taiwan and South Africa, so treaty relief is unavailable; in practice a credit for foreign income tax paid is claimed within statutory limits under the alternative minimum tax regime, supported by proof of payment. Have a Taiwan accountant experienced in overseas income handle this. It is also the reason this article keeps insisting on paperwork: the documents used to remit are the same documents used to file.</p>"""

EN_S6 = """<h2>Which six documents should be ready before you remit?</h2>
      <p><strong>Six, and none is optional.</strong> The list follows what a South African authorised dealer actually asks for, in the order the file is assembled. Having it ready saves two to four weeks of round trips.</p>
      <div class="process-steps">
        <div class="process-step"><div class="step-num">1</div><div class="step-content"><h4>Identity and tax status</h4><p>Passport and South African income tax reference number. If you are not registered with SARS, the bank will require registration first, which adds time.</p></div></div>
        <div class="process-step"><div class="step-num">2</div><div class="step-content"><h4>Proof of the source of funds</h4><p>Interest: statements and interest advices. Capital: the original inward remittance record and exchange control declaration. Sale proceeds: agreement and completed transfer evidence. These are not interchangeable.</p></div></div>
        <div class="process-step"><div class="step-num">3</div><div class="step-content"><h4>South African tax clearance evidence</h4><p>Property proceeds require the SARS section 35A withholding receipt. This is the most frequently missing item and the most frequent cause of rejection on a 510 01 payment.</p></div></div>
        <div class="process-step"><div class="step-num">4</div><div class="step-content"><h4>The export declaration and category</h4><p>Complete it according to the actual nature of the transaction and let the bank classify it. Do not pick a code and then look for a justification.</p></div></div>
        <div class="process-step"><div class="step-num">5</div><div class="step-content"><h4>Beneficiary name consistency</h4><p>The receiving account must be in your own name. Paying a spouse or family member requires additional authority documents, and Cape Town banks review beneficiaries closely.</p></div></div>
        <div class="process-step"><div class="step-num">6</div><div class="step-content"><h4>Taiwan filing preparation</h4><p>Keep the remittance advice, the rate and the fee breakdown. These are the source documents for the overseas income filing the following May — used once in South Africa and again in Taiwan.</p></div></div>
      </div>
      <h3>How long should you allow?</h3>
      <p>From submission to credit, <strong>two to four weeks</strong> is a reasonable planning assumption for an interest remittance. Where a property disposal is involved and SARS clearance plus title documents must be attached, allow <strong>six to ten weeks</strong>. If you are staging transfers, do not schedule the first one a month before you need the money — start it three months ahead.</p>"""

EN_FAQ = [
    ("What is the first decision when remitting rand interest to Taiwan?",
     "Classifying the money — not choosing a code. Interest, capital and sale proceeds carry different categories and different document sets. Mis-declaring does not create extra tax, but it makes the payment unexplainable in compliance review and can stretch processing from three working days to three to six weeks."),
    ("What changed in August 2026 and can I still use older code lists?",
     "The South African Reserve Bank's SADC-harmonised BoP categories took effect for industry on 11 August 2026, incorporating the IMF's BPM7 framework. Some categories changed completely, so Chinese-language lists compiled before August 2026 may not map. The final category is assigned by the bank's authorised dealer."),
    ("Is South African deposit interest subject to 15% withholding tax?",
     "South Africa applies a 15% final withholding on interest paid to non-residents, but under section 50D interest paid by a South African bank to a foreign person falls within the exemption. SARS's Budget 2026 guidance states interest is exempt if payable by the SA government or a bank. Confirm with the bank's current practice, and note the section 50D(2) back-to-back and 50D(3) day-count provisos."),
    ("Must overseas income be declared in Taiwan?",
     "Those meeting the conditions must file — filing is not limited to those who owe tax. Overseas income enters the basic income under the alternative minimum tax and is compared with ordinary consolidated tax, with the higher amount payable. Exemption and deduction amounts are adjusted by announcement every two years, so use the current year's figures."),
    ("Is one transfer better than several?",
     "It depends on the amount and your view on the rand. Staging exchanges extra fixed fees for currency averaging; it does not pay for small amounts, while for large amounts expected currency cost usually exceeds total fees. Many investors use a third route — remit interest, retain capital — keeping the fixed-cost ratio predictable."),
    ("How long does a transfer from South Africa to Taiwan take?",
     "Allow two to four weeks for a straightforward interest remittance. Where a property disposal is involved and SARS withholding receipts and title documents must be attached, allow six to ten weeks. For staged transfers, start the first one three months before you need the funds."),
]

EN_RELATED = """      <h2>Related reading</h2>
      <ul>
        <li><a href="/blog/standard-bank-non-resident-account-2026-en" title="Standard Bank non-resident account guide">Standard Bank non-resident account guide</a> — documents, the four profiling questions and rejection reasons.</li>
        <li><a href="/blog/sarb-bop-codes-foreign-property-buyers-2026-en" title="SARB BOP codes reference table">SARB BOP codes reference table</a> — the full schedule; this article lists only four categories.</li>
        <li><a href="/blog/standard-bank-money-market-en" title="Standard Bank money market rates">Standard Bank money market rates</a> — tiers, quotations and the non-guaranteed nature of the return.</li>
        <li><a href="/blog/south-africa-property-sale-withholding-tax-foreign-sellers-2026-en" title="Section 35A withholding tax on a Cape Town sale">Section 35A withholding tax on a Cape Town sale</a> — the tax clearance step before property proceeds can leave.</li>
        <li><a href="/south-africa-bank-account-en" title="South Africa bank account service">South Africa bank account service</a> — document standards, profiling preparation and remittance routing.</li>
      </ul>"""

EN_CRESTLINE = """    <h2>Why handle this through <span>Crestline Advisory</span>?</h2>
    <p>South African remittance requirements change every year — and what changes is usually the classification and the document order, not the eligibility. Same passport, same account, unexplainable nature of funds, rejection.</p>
    <h3>The three failure points we see most on repatriation</h3>
    <ul>
      <li><strong>Bundling three kinds of money into one declaration</strong>: interest, capital and sale proceeds have different categories and different documents. Sending them under a single "personal transfer" label gets the file split and resubmitted — a two to four week round trip.</li>
      <li><strong>Missing SARS tax clearance evidence</strong>: property proceeds require the section 35A withholding receipt. It is the most commonly omitted document and the most common reason a 510 01 payment stalls entirely.</li>
      <li><strong>Beneficiary name not matching the remitter</strong>: paying a spouse or relative needs extra authority documents, and Cape Town banks review beneficiaries closely, so ad-hoc fixes rarely meet the timetable.</li>
    </ul>
    <p>Working through our partner Crestline Advisory (on-the-ground execution in South Africa) means these are checked before submission: each tranche's nature and category verified line by line, current bank requirements on document format and in-person attendance confirmed, remittance routing and correspondent banks settled in advance, and progress tracked locally after submission.</p>
    <p>DingYao verifies your documents on the Taiwan side and hands over to Crestline Advisory for execution. You do not receive a checklist and left to figure it out alone.</p>
    <div class="ca-cta"><a href="/south-africa-bank-account-en#booking" class="btn btn-primary" title="Book a 30-minute consultation">Book a 30-minute consultation <i class="fas fa-arrow-right"></i></a></div>"""

EN_CTA = """      <h2>Fix the <span class="gold">nature and the route</span> before you argue about the rate</h2>
      <p>In repatriation, sequence drives cost. Tell us your account type in South Africa (fixed deposit, money market or call), the source of the funds (interest, capital or a property disposal) and the amount band, and we will set out the category mapping, the document list, a cost comparison between a single and staged transfer, and the direction of the Taiwan filing — involving our South African partner Crestline Advisory where execution support is needed.</p>
      <a href="/south-africa-bank-account-en" class="btn btn-primary" title="Explore South Africa bank account services">Explore account and remittance services <i class="fas fa-arrow-right"></i></a>"""

EN_DISCLAIMER = "All statements on South African BoP categories, remittance procedure, interest withholding and tax rules are drawn from South African Reserve Bank quarterly bulletin material, the Nedbank FinSurv BoP categories guide, SARS official pages and the Budget 2026 guidance. Taiwan-side statements on overseas income and the alternative minimum tax reflect the current framework published by the Ministry of Finance. The content is market reference only and does not constitute an offer, tax advice or legal advice. All remittances, account agreements and tax filings are concluded by the parties directly with South African financial institutions and Taiwan accountants. Exchange rates and interest rates are market references, not guarantees, and are governed by the bank's quotation on the transaction date. Exemption amounts, deductions and filing thresholds are adjusted annually; individual cases must follow the current year's official announcements."


POLISH_EN = [
    ("The practical effect for a Taiwan investor is not \"the tax changed\".",
     "The practical effect for a Taiwan investor remitting from a Cape Town account is not \"the tax changed\"."),
    ("everything else belongs in the reference table.</strong> Under the SARB categories published by Nedbank",
     "everything else belongs in the reference table.</strong> Under the South African Reserve Bank categories published by Nedbank"),
    ("This is the question we are asked most often, and it deserves an honest answer",
     "This is the question we are asked most often about South African accounts, and it deserves an honest answer"),
    ("The final determination sits with the bank's authorised dealer",
     "The final determination sits with the South African bank's authorised dealer"),
    ("This article lists four categories on purpose. The complete SARB BoP schedule",
     "This Cape Town remittance article lists four categories on purpose. The complete SARB BoP schedule"),
    ("<strong>There is no universal answer, but the trade-off is calculable.</strong> The decision turns",
     "<strong>For a South African repatriation there is no universal answer, but the trade-off is calculable.</strong> The decision turns"),
    ("The structure is simple: <strong>staging buys currency diversification",
     "For a South Africa-to-Taiwan payment the structure is simple: <strong>staging buys currency diversification"),
    ("Using the reference rate of roughly 1 rand = NT$1.975 on 23 October 2026",
     "Using the reference rate for the South African rand of roughly 1 rand = NT$1.975 on 23 October 2026"),
    ("Conversely, three transfers spread over three months land near the middle of the range",
     "Conversely, three transfers out of South Africa spread over three months land near the middle of the range"),
    ("remember that rand deposit rates are a <strong>market reference range",
     "remember that South African rand deposit rates are a <strong>market reference range"),
    ("Overseas income is added to a separate base, not to net consolidated income.",
     "In the Taiwan filing, overseas income from South Africa is added to a separate base, not to net consolidated income."),
    ("The basic income exemption and the threshold above which overseas income must be included",
     "The basic income exemption and the threshold above which overseas income from South Africa must be included"),
    ("The basic tax amount is compared with the ordinary consolidated tax amount",
     "The basic tax amount on the South African income is compared with the ordinary consolidated tax amount"),
    ("Those who meet the conditions must file, not merely those who owe tax. Penalties for omission",
     "Those who meet the conditions must file — including on South African interest and property gains — not merely those who owe tax. Penalties for omission"),
    ("<p>Interest: statements and interest advices. Capital: the original inward remittance record",
     "<p>For a South African account: interest needs statements and interest advices; capital needs the original inward remittance record"),
    ("Property proceeds require the SARS section 35A withholding receipt.",
     "Cape Town property proceeds require the SARS section 35A withholding receipt."),
    ("let the bank classify it. Do not pick a code",
     "let the South African bank classify it. Do not pick a code"),
    ("From submission to credit, <strong>two to four weeks</strong> is a reasonable planning assumption for an interest remittance.",
     "For a South African interest remittance, <strong>two to four weeks</strong> from submission to credit is a reasonable planning assumption."),
    ("Classifying the money — not choosing a code.",
     "Classifying the money — not choosing a South African code."),
    ("Those meeting the conditions must file — filing is not limited to those who owe tax.",
     "Those meeting the conditions must file with Taiwan's tax authority — filing is not limited to those who owe tax, and South African interest and property gains both count."),
    ("It depends on the amount and your view on the rand.",
     "It depends on the amount and your view on the South African rand."),
    ("Allow two to four weeks for a straightforward interest remittance.",
     "Allow two to four weeks for a straightforward South African interest remittance."),
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
      <span class="article-tag"><i class="fas fa-money-bill-transfer" style="margin-right:6px"></i>{tag}</span>
      <h1 class="article-title">{h1}</h1>
      <div class="article-meta">
        <span><i class="far fa-calendar"></i> {date_label}</span>
        <span><i class="far fa-clock"></i> {read_label}</span>
        <span><i class="fas fa-user"></i> Scott Huang</span>
        <span><i class="fas fa-tag"></i> Offshore Banking</span>
      </div>
    </div>
  </div>
</header>
<main id="main-content">
"""


def build(lang):
    tpl = load(TPL_ZH if lang == "zh" else TPL_EN)
    head_prefix, head_suffix, hero_i, body_i, cta_i = split_tpl(tpl)
    nav_blk = tpl[tpl.index("</head>") + 7:hero_i]
    tail = tpl[cta_i:]
    head = ZH_HEADLINE if lang == "zh" else EN_HEADLINE
    nav_blk = nav_blk.replace("南非開戶怎麼做？Standard Bank 非居民帳戶文件、profiling 四題與退件原因（2026）", head)
    nav_blk = nav_blk.replace("South Africa Bank Account: Standard Bank Non-Resident Guide", head)

    caps_zh = ["開普敦非居民帳戶的匯款作業窗口", "南非幣帳戶的對帳單與利息通知", "開普敦銀行的外匯申報文件",
               "南非幣與新台幣的匯率看板", "台灣端海外所得的申報資料", "匯出前的六項文件檢查"]
    caps_en = ["Remittance desk at a Cape Town non-resident account",
               "Statements and interest advices on a rand account",
               "Exchange control declaration documents at a Cape Town bank",
               "Rand to Taiwan dollar exchange rate board",
               "Taiwan overseas income filing paperwork",
               "Six-document checklist before a South African remittance"]

    if lang == "zh":
        meta = build_meta_zh(SLUG, ZH_TITLE, ZH_DESC, ZH_KW, ZH_HEADLINE, "開普敦非居民帳戶的匯款作業窗口")
        jl = jsonld_zh(SLUG, ZH_HEADLINE, ZH_DESC, ZH_FAQ, "南非幣匯回台灣")
        hh = herohdr(SLUG, "南非開戶與匯款", ZH_H1, "2026.10.24", "14 分鐘閱讀", "開普敦非居民帳戶的匯款作業窗口")
        secs = [ZH_S1, ZH_S2, ZH_S3, ZH_S4, ZH_S5, ZH_S6]
        faqs, related, cr, cta, dsc, faqh = ZH_FAQ, ZH_RELATED, ZH_CRESTLINE, ZH_CTA, ZH_DISCLAIMER, "常見問題 FAQ"
        intro = ZH_INTRO
        caps = caps_zh
    else:
        meta = build_meta_en(SLUG, EN_TITLE, EN_DESC, "Cape Town non-resident account remittance desk")
        jl = jsonld_en(SLUG, EN_HEADLINE, EN_DESC, EN_FAQ, "Remitting funds to Taiwan")
        hh = herohdr(SLUG, "Offshore Banking", EN_H1, "2026.10.24", "14 min read", "Cape Town non-resident account remittance desk")
        secs = [EN_S1, EN_S2, EN_S3, EN_S4, EN_S5, EN_S6]
        faqs, related, cr, cta, dsc, faqh = EN_FAQ, EN_RELATED, EN_CRESTLINE, EN_CTA, EN_DISCLAIMER, "FAQ"
        intro = EN_INTRO
        caps = caps_en

    body = "<!-- ARTICLE BODY -->\n" + intro_section(intro) + "\n\n"
    for n, s in enumerate(secs, 1):
        body += section(SLUG, n, caps[n - 1], caps[n - 1], s) + "\n\n"
    body += """<div class="section">
  <div class="container">
    <section class="article-body fade-in visible">
      <h2>""" + faqh + "</h2>\n"
    body += "".join(f"      <strong>{q}</strong>\n      <h3>{q}</h3>\n      <p>{a}</p>\n" if False else f"      <h3>{q}</h3>\n      <p>{a}</p>\n" for q, a in faqs)
    body += "\n" + related + """
    </section>
  </div>
</div>
"""

    meta = meta + jl
    body = polish(body, POLISH_EN) if lang == "en" else body
    t = tail
    s = t.index('<section class="crestline-assist"')
    e = t.index('</section>', t.index('<div class="ca-cta">', s)) + len('</section>')
    t = t[:s] + '<section class="crestline-assist" id="crestline-assist">\n  <div class="ca-inner">\n' + cr + "\n  </div>\n</section>" + t[e:]

    s = t.index('<section class="section cta-section">')
    e = t.index('</section>', t.index('<a href=', s)) + len('</section>')
    t = t[:s] + '<section class="section cta-section">\n  <div class="container">\n    <div class="cta-content fade-in">\n' + cta + "\n    </div>\n  </div>\n</section>" + t[e:]

    for pat in (r'<p><strong>2\. 資訊來源與契約主體：</strong>.*?</p>',
                r'<p><strong>2\. Information sources and contracting parties:</strong>.*?</p>'):
        m = re.search(pat, t, re.S)
        if m:
            label = "2. 資訊來源與契約主體：" if '資訊來源' in pat else "2. Information sources and contracting parties:"
            t = t[:m.start()] + f"<p><strong>{label}</strong>" + dsc + "</p>" + t[m.end():]
            break

    return assemble(head_prefix, meta, head_suffix, nav_blk, hh, body, t)


for lg, fn in (("zh", f"{SLUG}.html"), ("en", f"{SLUG}-en.html")):
    html = build(lg)
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {fn} {len(html)} bytes")
