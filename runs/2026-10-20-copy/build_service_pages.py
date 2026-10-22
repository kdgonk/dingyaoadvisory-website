# -*- coding: utf-8 -*-
"""2026-10-20 三支柱服務頁文案：bank-account / property（ZH + EN 1:1 鏡像）
以 dist/residency.html 為樣板（nav/footer/CSS byte-identical），只換 head meta 與 <main>。
輸出到 runs/2026-10-20-copy/，不動 dist/。
"""
import json, re, os, pathlib

ROOT = pathlib.Path.home() / "Documents/DingYao-Website/dingyaoadvisory-website"
DIST = ROOT / "dist"
OUT = ROOT / "runs/2026-10-20-copy"
OUT.mkdir(parents=True, exist_ok=True)

BASE_ZH = DIST / "residency.html"
BASE_EN = DIST / "residency-en.html"

HERO_BG = "https://assets.dingyaoadvisory.tw/redesign/section-hero.webp"
SECTION_BG = "https://assets.dingyaoadvisory.tw/redesign/section-hero.webp"
BANK_WHY_BG = "https://assets.dingyaoadvisory.tw/redesign/section-hero.webp"

ICON = {
    "globe": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10A15.3 15.3 0 0 1 12 2z"/></svg>',
    "shield": '<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "file": '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="12" x2="12" y2="18"/><line x1="9" y1="15" x2="15" y2="15"/></svg>',
}


# ---------------------------------------------------------------- page content
def page_zh_bank():
    return dict(
        slug="south-africa-bank-account",
        lang="zh-Hant",
        title="南非銀行開戶完整指南｜外國人開戶流程與文件｜鼎曜國際顧問",
        desc="南非銀行開戶完整指南：外國人如何準備護照認證、稅務編號與三個月內地址證明，避免退件。台灣一年期定存固定利率 1.700%，南非 Standard Bank Money Market 同期公告 7.10% 至 7.45%，本文逐項說明流程、費用、匯率打平點與稅務注意事項。開戶文件確認與轉交由鼎曜國際顧問協助，簽約主體為 Crestline Advisory。",
        og_title="南非銀行開戶完整指南｜外國人開戶流程與文件｜鼎曜國際顧問",
        h1=("南非銀行開戶", "外國人的流程與文件"),
        badge=("fas fa-university", "Non-Resident Account · Cape Town"),
        hero_sub="台灣一年期定存固定利率 <strong>1.700%</strong>，南非 Standard Bank Money Market 同期公告 <strong class=\"gold-text\">7.10%–7.45%</strong>。真正的門檻不是資格，是文件格式 —— 我們在開普敦逐項幫你核對。",
        why_label="Why Applications Fail",
        why_h2="為什麼台灣人開不了南非銀行帳戶？",
        why_intro="多數退件不是資格不符，而是文件格式與效期。以下三項，是我們在開普敦最常補救的缺口。",
        why_cards=[
            ("file", "護照認證格式",
             "南非銀行要求 certified copy 的指定格式與簽章位置，台灣常見的公證版本常被退件。我們逐頁核對格式與簽章，避免重寄一次多等一個月。"),
            ("globe", "稅務編號與欄位",
             "非居民需以台灣身分證號或稅籍資料對應表格欄位，欄位錯置會被退回重填。這一步沒有對照表，只能靠實際送件經驗。"),
            ("shield", "三個月內地址證明",
             "帳單日期一過期就得重辦，這是實務上排名第一的退件原因。我們會在送件前確認所有文件都還落在有效期內。"),
        ],
        why_note="利差要這樣算才誠實：以新台幣 300 萬元為例，一年期定存固定利率 1.700%，年息約 5.1 萬元；同一筆資金以 7.10% 計息，年息約 21.3 萬元，名目差額約 16.2 萬元。但有兩個變數必須一起看 —— 金額達 500 萬元以上，台灣端大額牌告利率反而降到 0.770%；南非幣一年貶值超過 5.40%，利差就會被匯損完全吃掉。",
        proc_label="Opening Process",
        proc_h2="南非銀行開戶流程：五個步驟",
        proc_intro="從諮詢到帳戶可用，文件齊備後多數案件約 4 至 8 週完成。實際時間取決於銀行的 KYC 補件速度。",
        steps=[
            ("需求與資格確認", "30 分鐘視訊，確認居住地、資金來源、預計金額與用途，判斷適合的帳戶類型與幣別配置。"),
            ("文件準備", "護照認證本、三個月內地址證明、稅務編號、資金來源說明；我們提供逐項清單與範例，照著準備即可。"),
            ("鼎曜文件複核", "檢查認證格式、簽章位置、文件效期與譯本一致性，先把會被退件的原因在送件前排除。"),
            ("轉交 Crestline Advisory", "由 Crestline 與你簽約、送件並對接銀行端 KYC。鼎曜不代收資金，也不代為簽約。"),
            ("帳戶啟用與後續", "網銀開通、首次匯款路徑、利息與稅務文件的取得方式，一次講清楚，避免開完戶不會用。"),
        ],
        cmp_label="Rate Comparison",
        cmp_h2="南非 Money Market 與台灣定存差在哪？",
        cmp_intro="兩邊比的不是同一種東西：一邊是沒有匯率風險的低利，一邊是承擔匯率風險的高利。",
        cmp_rows=[
            ("一年期利率", "1.700%（500 萬元以上 0.770%）", "7.10%–7.45%（資料日 2026-10-02）"),
            ("最低門檻", "新台幣 1 萬元起", "南非幣 100,000"),
            ("計息幣別", "新台幣", "南非幣"),
            ("匯率風險", "無", "有，貶值 5.40% 即打平"),
            ("存款保障", "中央存款保險", "依南非現行機制，上限待確認"),
            ("簽約主體", "往來銀行", "Crestline Advisory"),
        ],
        cmp_h2b="損益兩平點怎麼算？",
        cmp_body=[
            "算法很簡單：7.10% 減 1.700% 等於 5.40 個百分點。南非幣若一年貶值超過 5.40%，利息差會被匯損全部吃掉；若再把換匯價差與跨境匯款費用算進去，真正的打平點會更低。任何只放大年息、不談這件事的比較，都不值得參考。",
            "開普敦的實務經驗是：帳戶開得成不成的關鍵在文件，不在金額。我們看過太多案件卡在認證格式與地址證明效期，重寄一次就是兩到三週，而利率在這段時間並不會停下來等你。",
        ],
        faq_h2="常見問題",
        faq_sub="關於南非銀行開戶與非居民文件準備的常見疑問",
        faqs=[
            ("開南非銀行帳戶需要親自飛到南非嗎？",
             "多數非居民帳戶可遠端完成，但銀行仍可能在 KYC 階段要求面簽或補件。我們會先確認銀行當期要求，再判斷是否需要入境開普敦辦理，避免白跑一趟。"),
            ("從諮詢到帳戶可以使用要多久？",
             "文件齊備後一般約 4 至 8 週。若遇到地址證明過期或認證格式不符，重辦會再多 2 至 3 週，所以我們在送件前一定先做一次格式複核。"),
            ("最低要準備多少錢？",
             "Standard Bank MoneyMarket Select 最低起存為南非幣 100,000。除此之外要另留換匯與跨境匯款費用，也不建議把生活預備金全部轉成南非幣。"),
            ("南非的利息需要繳台灣的稅嗎？",
             "海外利息所得需計入個人基本所得額，是否產生稅負視全年海外所得總額而定；南非端的利息扣繳方式也需依當地規定確認。具體申報請諮詢會計師，本文不構成稅務建議。"),
            ("錢匯得回來嗎？",
             "可以，但南非有外匯管制，須依南非儲備銀行規定與正確的 BOP 類別辦理。利息與本金的匯回有既定程序，文件齊備是關鍵，我們會協助你確認匯出與匯回的文件路徑。"),
            ("7.10% 的利率是保證的嗎？",
             "不是。7.10% 至 7.45% 為 2026-10-02 的公開牌告資料，會隨南非儲備銀行政策與各銀行調整而變動。任何把利率寫成固定保證的說法，都不正確。"),
            ("鼎曜是簽約方嗎？",
             "不是。鼎曜國際顧問協助你確認資料、準備文件並轉交 Crestline Advisory；帳戶與相關合約的簽約主體是 Crestline Advisory，鼎曜不代收資金。"),
        ],
        cta_label="Start Your Application",
        cta_h2=("準備好開立", "你的南非帳戶了嗎？"),
        cta_p="先做一次免費資格評估，我們回覆你三件事：能不能開、缺哪份文件、大概需要多久。評估不收費，也不代表必須開戶。",
        cta_btn="預約免費評估",
        disclaimer="本頁利率為 2026-10-02 公開資料，非保證收益；南非幣兌新台幣匯率可能大幅波動，過去走勢不代表未來。鼎曜國際顧問提供文件確認與轉交服務，帳戶及相關合約之簽約主體為 Crestline Advisory，鼎曜不代收資金。",
        schema_name="鼎曜國際顧問 DingYao Advisory — 南非銀行開戶",
        schema_desc="南非銀行開戶服務：外國人非居民帳戶的文件準備、格式確認與轉交 Crestline Advisory 簽約。",
        hero_alt="南非銀行開戶｜開普敦非居民帳戶文件準備",
        crumb="南非銀行開戶",
        alt_zh="https://dingyaoadvisory.tw/south-africa-bank-account",
        alt_en="https://dingyaoadvisory.tw/south-africa-bank-account-en",
        cta1=("hero_primary", "hero"), cta2=("mid_process", "mid_section"),
        cta3=("faq_consult", "faq"), cta4=("bottom_primary", "bottom_cta"),
        btn_secondary=("了解流程", "#process"),
        icon="fas fa-university",
    )


def page_zh_property():
    return dict(
        slug="south-africa-property",
        lang="zh-Hant",
        title="南非置產顧問服務｜在地團隊陪同簽約與過戶｜鼎曜國際顧問",
        desc="南非置產顧問服務：開普敦在地團隊陪同選屋、盡職調查、簽約與過戶。買入稅費約佔房價 9.4% 至 9.7%，毛租金收益率約 9.49%、扣除持有成本後淨值約 7.5% 至 8.0%，退出時資本利得有效稅率最高約 18%。本文說明我們在各階段負責什麼，以及外國買家最容易漏算的三段成本。",
        og_title="南非置產顧問服務｜在地團隊陪同簽約與過戶｜鼎曜國際顧問",
        h1=("南非置產顧問服務", "從選屋到過戶的在地陪同"),
        badge=("fas fa-map-marked-alt", "Cape Town Advisory · 陪同簽約與過戶"),
        hero_sub="買房只是開始。真正的成本在稅費、持有與退出 —— 我們在<strong>開普敦</strong>陪你把每一筆算清楚，再決定要不要簽。",
        why_label="Why Local Advisory",
        why_h2="為什麼南非置產需要在地顧問？",
        why_intro="外國買家最容易低估的不是房價，是稅費與流程。以下三件事沒有在地人陪同，代價很高。",
        why_cards=[
            ("file", "稅費逐項算給你",
             "轉讓稅、過戶費、市政稅、管理費、資本利得稅，全部列進現金流模型。我們不用「大概」帶過，因為差一個百分點就是幾十萬。"),
            ("globe", "文件與資金路徑",
             "外國買家需完成 FICA 與資金來源證明，並依南非儲備銀行規定辦理匯入。順序錯了要重來，時間成本遠高於手續費。"),
            ("shield", "過戶與交屋陪同",
             "過戶由開普敦在地律師與代書執行，我們陪同確認每個節點與費用，讓你不必在異地追進度、追文件、追人。"),
        ],
        why_note="以開普敦一戶南非幣 10,450,000 的房產為例，轉讓稅約 926,856，加計律師過戶費與登記費後，買入階段的稅費合計約佔房價 9.4% 至 9.7%。這筆錢不在房價裡，卻是現金流模型最常被漏掉的一塊。",
        proc_label="How We Work",
        proc_h2="我們陪你走的四個階段",
        proc_intro="過戶的七大步驟與文件細節，我們整理在既有的流程指南裡；這裡只說明我們在各階段負責什麼、你會拿到什麼。",
        steps=[
            ("需求與區位", "依預算、用途（自住、出租、子女就學）與持有年限，把範圍縮小到開普敦兩到三個區塊，而不是丟一堆物件讓你自己篩。"),
            ("物件與盡職調查", "產權、管理費、市政稅、修繕紀錄逐項確認，必要時安排第三方驗屋，先找出會影響轉售與出租的瑕疵。"),
            ("簽約與資金", "由 Crestline Advisory 與你簽約；資金依規定匯入律師信託帳戶，我們確認文件、時程與匯入路徑都對得上。"),
            ("過戶與交屋", "律師辦理過戶，我們陪同確認交屋狀態、鑰匙、水電與代管交接，避免交屋後才發現缺漏。"),
        ],
        proc_link=("完整的過戶七大步驟與文件清單，請看〈開普敦買房流程完整指南：外國人從簽約到過戶的七大步徑〉。",
                   "/blog/cape-town-property-purchase-process-guide",
                   "開普敦買房流程完整指南"),
        cmp_label="Three-Stage Cost",
        cmp_h2="買入、持有、退出：三段成本一起看",
        cmp_intro="只看租金收益率會高估報酬。開普敦毛租金收益率約 9.49%，扣完成本後的淨值約 7.5% 至 8.0%。",
        cmp_rows=[
            ("主要成本", "轉讓稅、過戶費、登記費", "市政稅、管理費、保險、維修", "資本利得稅"),
            ("金額或比率", "約房價 9.4%–9.7%", "市政稅率 0.004–0.011；管理費每月南非幣 2,500–8,000", "淨利得 40% 納入，有效最高約 18%"),
            ("誰執行", "律師與代書（Crestline 協調）", "代管團隊", "會計師與律師"),
            ("外國買家注意", "資金須先完成 FICA 與匯入程序", "空置期是現金流最大變數", "持有期與改良憑證影響稅基"),
        ],
        cmp_h2b="淨收益率為什麼會從 9.49% 掉到 7.5%？",
        cmp_body=[
            "因為毛值只算租金，淨值要算成本。9.49% 扣掉空置、代管費 8% 到 12%、市政稅、保險與維修後，落在 7.5% 至 8.0%。用毛值做決策，等於一開始就高估報酬近兩個百分點。",
            "退出也要先算：資本利得 40% 納入所得、有效稅率最高約 18%。持有期間的裝修與改良憑證要留好，它會直接影響你退出那一天的稅基。開普敦的物件不是不能買，是要用淨值買。",
        ],
        faq_h2="常見問題",
        faq_sub="關於南非置產、稅費與過戶陪同的常見疑問",
        faqs=[
            ("外國人可以在開普敦買房嗎？",
             "一般住宅，包含永久產權與分層產權，外國人可以購買；農地與礦權相關不動產另有管制。實際限制依現行法規與物件性質而定，我們會在盡職調查階段先確認。"),
            ("一定要親自到開普敦看房嗎？",
             "不一定要，但我們建議至少在過戶前實地或委託第三方驗屋。若採遠端交易，授權文件與視訊看屋紀錄要備齊，否則日後爭議很難主張。"),
            ("買一戶要準備多少現金？",
             "除了房價，還要加計約 9.4% 至 9.7% 的買入稅費與過戶費用。以開普敦均價南非幣 2,600,000 起算，實務門檻明顯高於房價本身，這點必須先講清楚。"),
            ("外國人可以辦房貸嗎？",
             "非居民房貸存在但條件較嚴，成數與利率加碼依銀行與物件而異，需個案評估。多數客戶採現金購買，避免審核期與匯率形成雙重風險。"),
            ("租金可以匯回台灣嗎？",
             "可以，需依南非儲備銀行的外匯規定與正確的 BOP 類別辦理，並備妥租約與稅務文件。代管團隊通常會協助年度對帳與匯出文件，這部分不能省。"),
            ("代管費用怎麼算？",
             "市場行情約為月租金 8% 至 12%，服務範圍與是否含招租、修繕協調差異很大。簽約前要確認包含項目與不包含項目，不要只看百分比數字。"),
            ("鼎曜是簽約主體嗎？",
             "不是。鼎曜國際顧問提供區位資訊、文件準備與流程陪同；置產交易的簽約主體為 Crestline Advisory，鼎曜不代收購屋款，也不代為簽約。"),
        ],
        cta_label="Start With Your Budget",
        cta_h2=("先看你的預算", "在開普敦買得到什麼"),
        cta_p="預約一對一評估，我們依你的預算列出可選區塊、完整稅費與五年現金流試算，再決定要不要進到看屋與簽約。",
        cta_btn="預約免費評估",
        disclaimer="本頁數字為市場參考區間與公開資料整理，非保證收益，亦不構成投資建議。稅費與稅率依南非現行法規及個案條件而異，實際金額以律師、會計師與正式文件為準。置產交易之簽約主體為 Crestline Advisory，鼎曜國際顧問協助區位資訊、文件準備與流程陪同。",
        schema_name="鼎曜國際顧問 DingYao Advisory — 南非置產顧問服務",
        schema_desc="南非置產顧問服務：開普敦選屋、盡職調查、稅費試算、陪同簽約與過戶，簽約主體為 Crestline Advisory。",
        hero_alt="南非置產顧問服務｜開普敦在地團隊陪同簽約與過戶",
        crumb="南非置產顧問服務",
        alt_zh="https://dingyaoadvisory.tw/south-africa-property",
        alt_en="https://dingyaoadvisory.tw/south-africa-property-en",
        cta1=("hero_primary", "hero"), cta2=("mid_process", "mid_section"),
        cta3=("faq_consult", "faq"), cta4=("bottom_primary", "bottom_cta"),
        btn_secondary=("了解流程", "#process"),
        icon="fas fa-map-marked-alt",
    )


def page_en_bank():
    return dict(
        slug="south-africa-bank-account-en",
        lang="en",
        title="South Africa Bank Account for Foreigners | Opening Process & Documents | DingYao Advisory",
        desc="A practical guide to opening a South African bank account as a foreigner: passport certification format, tax number fields and a utility bill dated within three months. Taiwan one-year fixed deposits pay 1.700%, while Standard Bank Money Market Select published 7.10% to 7.45% on 2 October 2026. DingYao Advisory checks and forwards your documents; the contracting party is Crestline Advisory.",
        og_title="South Africa Bank Account for Foreigners | Opening Process & Documents | DingYao Advisory",
        h1=("South Africa Bank Account", "for Foreigners: Process & Documents"),
        badge=("fas fa-university", "Non-Resident Account · Cape Town"),
        hero_sub="A one-year fixed deposit in Taiwan pays <strong>1.700%</strong>. Standard Bank Money Market Select published <strong class=\"gold-text\">7.10%–7.45%</strong> on 2 October 2026. The real barrier is not eligibility — it is document format, and we check every page with you in Cape Town.",
        why_label="Why Applications Fail",
        why_h2="Why do most Taiwanese applications get rejected?",
        why_intro="Rejections are rarely about eligibility. They are about document format and expiry dates. These are the three gaps we fix most often in Cape Town.",
        why_cards=[
            ("file", "Passport certification format",
             "South African banks require certified copies in a specific format and signature position. The notarised version commonly used in Taiwan is often rejected, and each resubmission costs about a month."),
            ("globe", "Tax number and field mapping",
             "Non-residents must map a Taiwan ID or tax reference onto specific form fields. A misplaced field means the form is returned, and there is no public guide for this step."),
            ("shield", "Proof of address under three months",
             "Once a utility bill passes the three-month mark it must be reissued. This is the single most common reason applications stall, so we verify every document is still valid before submission."),
        ],
        why_note="Do the arithmetic honestly. On NT$3,000,000, a one-year fixed deposit at 1.700% earns about NT$51,000; the same amount at 7.10% earns about NT$213,000 — a nominal gap of roughly NT$162,000. Two variables matter: deposits of NT$5,000,000 or more fall to a large-amount board rate of 0.770% in Taiwan, and if the rand weakens by more than 5.40% in a year, the entire interest advantage is wiped out.",
        proc_label="Opening Process",
        proc_h2="Opening a South African bank account: five steps",
        proc_intro="From first call to an active account typically takes four to eight weeks once documents are complete. Bank KYC turnaround is the variable.",
        steps=[
            ("Eligibility review", "A 30-minute video call covering residency, source of funds, intended amount and purpose, so we can match you to the right account type."),
            ("Document preparation", "Certified passport, proof of address under three months, tax number and a source-of-funds statement. We provide the checklist and samples."),
            ("DingYao document review", "We check certification format, signature position, validity dates and translation consistency before anything is submitted."),
            ("Handover to Crestline Advisory", "Crestline signs the engagement, submits the file and liaises with the bank's KYC team. DingYao does not hold client funds."),
            ("Account activation", "Online banking, first remittance route, and how to obtain interest and tax documents afterwards — explained before you need them."),
        ],
        cmp_label="Rate Comparison",
        cmp_h2="How does a South African money market account compare?",
        cmp_intro="These are not the same product: one is a low rate with no currency risk, the other a higher rate that carries currency risk.",
        cmp_rows=[
            ("One-year rate", "1.700% (0.770% above NT$5,000,000)", "7.10%–7.45% (data as of 2 Oct 2026)"),
            ("Minimum", "NT$10,000", "ZAR 100,000"),
            ("Currency", "New Taiwan dollar", "South African rand"),
            ("Currency risk", "None", "Yes — break-even at 5.40% depreciation"),
            ("Deposit protection", "Central Deposit Insurance", "Per South African scheme; cap to be confirmed"),
            ("Contracting party", "Your bank", "Crestline Advisory"),
        ],
        cmp_h2b="Where is the break-even point?",
        cmp_body=[
            "Simple arithmetic: 7.10% minus 1.700% equals 5.40 percentage points. If the rand weakens by more than 5.40% over the year, the interest advantage disappears entirely. Add FX spread and cross-border transfer fees and the real break-even is lower still. Any comparison that only quotes the headline rate is not worth reading.",
            "In practice, whether an account gets opened depends on documents, not on the amount. We regularly see files stall on certification format or an expired utility bill, and a resubmission costs two to three weeks while the rate keeps moving.",
        ],
        faq_h2="Frequently asked questions",
        faq_sub="Common questions about South African accounts and non-resident documentation",
        faqs=[
            ("Do I need to fly to South Africa to open an account?",
             "Most non-resident accounts can be opened remotely, but banks may still require a face-to-face signature or extra documents at the KYC stage. We confirm the bank's current requirement first, then advise whether travel to Cape Town is necessary."),
            ("How long does the process take?",
             "Typically four to eight weeks once documents are complete. An expired proof of address or a non-compliant certification adds two to three weeks, which is why we run a format review before submission."),
            ("What is the minimum deposit?",
             "Standard Bank MoneyMarket Select requires a minimum of ZAR 100,000. You should also budget for FX spread and cross-border transfer fees, and we do not recommend converting your entire emergency reserve."),
            ("Is the interest taxable in Taiwan?",
             "Overseas interest income counts toward your annual basic income total, and whether tax applies depends on the aggregate amount. South African withholding also applies under local rules. Please consult an accountant; this page is not tax advice."),
            ("Can the money be repatriated?",
             "Yes, subject to South African exchange control and the correct BOP category. Interest and principal follow an established process where complete documentation is the deciding factor, and we help you confirm the outbound and inbound document trail."),
            ("Is the 7.10% rate guaranteed?",
             "No. The 7.10% to 7.45% range reflects published rates as of 2 October 2026 and moves with Reserve Bank policy and individual bank pricing. Any claim that a rate is fixed and guaranteed is inaccurate."),
            ("Is DingYao the contracting party?",
             "No. DingYao Advisory confirms and prepares your documents and forwards them to Crestline Advisory. The contracting party for the account and related agreements is Crestline Advisory, and DingYao does not collect client funds."),
        ],
        cta_label="Start Your Application",
        cta_h2=("Ready to open", "your South African account?"),
        cta_p="Start with a free eligibility review. We will tell you three things: whether you qualify, which document is missing, and roughly how long it takes. The review is free and carries no obligation.",
        cta_btn="Book a free assessment",
        disclaimer="Rates on this page are public data as of 2 October 2026 and are not guaranteed. The rand may move significantly against the New Taiwan dollar and past performance is not indicative of future results. DingYao Advisory provides document review and handover services; the contracting party for accounts and related agreements is Crestline Advisory, and DingYao does not collect client funds.",
        schema_name="DingYao Advisory — South Africa Bank Account Opening",
        schema_desc="South Africa bank account opening support for foreign nationals: document preparation, format review and handover to Crestline Advisory.",
        hero_alt="South Africa bank account for foreigners — document preparation in Cape Town",
        crumb="South Africa Bank Account",
        alt_zh="https://dingyaoadvisory.tw/south-africa-bank-account",
        alt_en="https://dingyaoadvisory.tw/south-africa-bank-account-en",
        cta1=("hero_primary", "hero"), cta2=("mid_process", "mid_section"),
        cta3=("faq_consult", "faq"), cta4=("bottom_primary", "bottom_cta"),
        btn_secondary=("See the process", "#process"),
        icon="fas fa-university",
    )


def page_en_property():
    return dict(
        slug="south-africa-property-en",
        lang="en",
        title="South Africa Property Advisory Services | DingYao Advisory",
        desc="Cape Town property advisory for foreign buyers: area shortlisting, due diligence, tax modelling, and accompaniment through signing and transfer. Acquisition costs run about 9.4% to 9.7% of the purchase price, gross rental yield is around 9.49% and net yield about 7.5% to 8.0% after costs, with capital gains tax at an effective maximum of roughly 18%. The contracting party is Crestline Advisory.",
        og_title="South Africa Property Advisory Services | DingYao Advisory",
        h1=("South Africa Property Advisory", "From shortlisting to transfer, on the ground"),
        badge=("fas fa-map-marked-alt", "Cape Town Advisory · Signing & Transfer"),
        hero_sub="Buying is only the beginning. The real cost sits in taxes, holding costs and exit — we work through every line with you in <strong>Cape Town</strong> before you sign anything.",
        why_label="Why Local Advisory",
        why_h2="Why does South Africa property need a local adviser?",
        why_intro="Foreign buyers rarely underestimate the price. They underestimate the taxes and the process. These three gaps are expensive without someone on the ground.",
        why_cards=[
            ("file", "Taxes modelled line by line",
             "Transfer duty, conveyancing fees, municipal rates, levies and capital gains tax all go into the cash-flow model. We do not use the word 'roughly' — one percentage point here is a six-figure sum."),
            ("globe", "Documents and funding route",
             "Foreign buyers must complete FICA and source-of-funds checks and remit under South African Reserve Bank rules. Get the sequence wrong and you start over, which costs far more than the fees."),
            ("shield", "Accompanied transfer and handover",
             "Transfer is executed by Cape Town attorneys and conveyancers. We attend each milestone and cost so you are not chasing progress, paperwork and people from another country."),
        ],
        why_note="Take a Cape Town property at ZAR 10,450,000. Transfer duty alone is about ZAR 926,856; add conveyancing and registration fees and acquisition costs reach roughly 9.4% to 9.7% of the price. That money is not in the purchase price, yet it is the line most often missing from a cash-flow model.",
        proc_label="How We Work",
        proc_h2="Four stages we walk through with you",
        proc_intro="The seven transfer steps and document detail are covered in our existing process guide. Here we only explain what we own at each stage and what you receive.",
        steps=[
            ("Brief and shortlisting", "Budget, use case (own use, rental, schooling) and hold period narrow the search to two or three Cape Town areas, rather than sending you a list to filter yourself."),
            ("Property and due diligence", "Title, levies, municipal rates and maintenance history are verified, with third-party inspections where needed, so defects that affect resale or letting surface early."),
            ("Signing and funding", "Crestline Advisory signs the agreement; funds are remitted into the attorney's trust account under the applicable rules, and we confirm documents, timing and the remittance route."),
            ("Transfer and handover", "Attorneys handle transfer while we attend the handover: condition, keys, utilities and the management handover, so nothing is discovered after the fact."),
        ],
        proc_link=("For the full seven transfer steps and document checklist, read our guide: Cape Town Property Purchase Process for Foreign Buyers.",
                   "/blog/cape-town-property-purchase-process-guide",
                   "Cape Town property purchase process guide"),
        cmp_label="Three-Stage Cost",
        cmp_h2="Acquisition, holding and exit: three cost stages",
        cmp_intro="Looking only at rental yield overstates the return. Gross yield in Cape Town is around 9.49%, falling to roughly 7.5% to 8.0% net of costs.",
        cmp_rows=[
            ("Main costs", "Transfer duty, conveyancing, registration", "Municipal rates, levies, insurance, maintenance", "Capital gains tax"),
            ("Amount or rate", "About 9.4%–9.7% of price", "Rates factor 0.004–0.011; levies ZAR 2,500–8,000 per month", "40% inclusion, effective maximum about 18%"),
            ("Executed by", "Attorneys and conveyancers (coordinated by Crestline)", "Managing agent", "Accountant and attorney"),
            ("Foreign buyer note", "FICA and remittance must be completed first", "Vacancy is the biggest cash-flow variable", "Hold period and improvement records set the tax base"),
        ],
        cmp_h2b="Why does 9.49% become 7.5%?",
        cmp_body=[
            "Because gross yield counts rent only. Net yield counts costs: 9.49% less vacancy, a management fee of 8% to 12%, municipal rates, insurance and maintenance lands at 7.5% to 8.0%. Deciding on the gross figure overstates the return by almost two percentage points before you start.",
            "Model the exit as well: 40% of the capital gain is included in taxable income, with an effective rate of up to about 18%. Keep the invoices for improvements during the hold period, because they set the tax base on the day you sell. Cape Town property is not a bad buy — it just has to be bought on net numbers.",
        ],
        faq_h2="Frequently asked questions",
        faq_sub="Common questions on South Africa property, taxes and accompanied transfer",
        faqs=[
            ("Can foreigners buy property in Cape Town?",
             "Yes for ordinary residential property, including freehold and sectional title. Agricultural land and mineral-rights related property are restricted. The applicable limits depend on current legislation and the nature of the property, and we confirm this at due diligence."),
            ("Do I have to view the property in person?",
             "Not necessarily, but we recommend an inspection in person or through a third party before transfer. For remote purchases, powers of attorney and video viewing records must be complete, otherwise disputes are hard to pursue."),
            ("How much cash should I prepare?",
             "Beyond the price, budget roughly 9.4% to 9.7% for acquisition taxes and conveyancing. With Cape Town's average price starting around ZAR 2,600,000, the practical threshold is clearly above the headline price, and we say so upfront."),
            ("Can foreigners obtain a mortgage?",
             "Non-resident lending exists but on stricter terms, with loan-to-value and pricing depending on the bank and the property. Most of our clients buy in cash to avoid the double risk of a long approval and currency movement."),
            ("Can rental income be repatriated?",
             "Yes, subject to South African Reserve Bank rules and the correct BOP category, with the lease and tax documents available. Managing agents normally support the annual reconciliation and the outward remittance paperwork."),
            ("How is the management fee calculated?",
             "Market practice is 8% to 12% of monthly rent, and scope varies widely — whether letting, inspections and repairs are included changes the value entirely. Confirm inclusions and exclusions before signing, not just the percentage."),
            ("Is DingYao the contracting party?",
             "No. DingYao Advisory provides area information, document preparation and process accompaniment. The contracting party for property transactions is Crestline Advisory, and DingYao does not collect purchase funds or sign on your behalf."),
        ],
        cta_label="Start With Your Budget",
        cta_h2=("See what your budget", "buys in Cape Town"),
        cta_p="Book a one-to-one assessment. We map your budget to available areas, the full tax cost and a five-year cash-flow projection before you move to viewings or signing.",
        cta_btn="Book a free assessment",
        disclaimer="Figures on this page are market reference ranges and public data. They are not guaranteed returns and do not constitute investment advice. Taxes and rates depend on current South African legislation and individual circumstances; final amounts are determined by attorneys, accountants and formal documents. The contracting party for property transactions is Crestline Advisory; DingYao Advisory provides area information, document preparation and process accompaniment.",
        schema_name="DingYao Advisory — South Africa Property Advisory Services",
        schema_desc="Cape Town property advisory for foreign buyers: shortlisting, due diligence, tax modelling and accompanied signing and transfer. Contracting party: Crestline Advisory.",
        hero_alt="South Africa property advisory services in Cape Town",
        crumb="South Africa Property Advisory",
        alt_zh="https://dingyaoadvisory.tw/south-africa-property",
        alt_en="https://dingyaoadvisory.tw/south-africa-property-en",
        cta1=("hero_primary", "hero"), cta2=("mid_process", "mid_section"),
        cta3=("faq_consult", "faq"), cta4=("bottom_primary", "bottom_cta"),
        btn_secondary=("See how we work", "#process"),
        icon="fas fa-map-marked-alt",
    )


# ---------------------------------------------------------------- renderers
def render_main(d):
    zh = d["lang"] == "zh-Hant"
    cta = lambda key, cls="btn btn-primary": (
        f'<a href="/consultation" class="{cls}" data-cta-id="{key[0]}" '
        f'data-cta-location="{key[1]}" title="{d["cta_btn"]}">{d["cta_btn"]} '
        f'<i class="fas fa-arrow-right"></i></a>')

    h = []
    h.append('<main id="main-content">')
    # ---- hero
    h.append(f'''
<section class="hero" id="hero">
  <div class="hero-bg">
    <picture>
      <source srcset="{HERO_BG}" type="image/webp">
      <img src="{HERO_BG}" alt="{d["hero_alt"]}" loading="eager" title="{d["hero_alt"]}">
    </picture>
    <div class="hero-overlay"></div>
    <div class="gradient-1"></div>
    <div class="grid-overlay"></div>
  </div>
  <div class="hero-content">
    <div class="hero-badge">
      <i class="{d["badge"][0]}"></i>
      {d["badge"][1]}
    </div>
    <h1>
      {d["h1"][0]}
      <span class="gold-text">{d["h1"][1]}</span>
    </h1>
    <p class="hero-subtitle">
      {d["hero_sub"]}
    </p>
    <div class="hero-actions">
      {cta(d["cta1"])}
      <a href="{d["btn_secondary"][1]}" class="btn btn-outline" title="{d["btn_secondary"][0]}">
        {d["btn_secondary"][0]} <i class="fas fa-chevron-right"></i>
      </a>
    </div>
  </div>
  <div class="hero-scroll">
    <span>{"探索" if zh else "Explore"}</span>
    <i class="fas fa-chevron-down"></i>
  </div>
</section>''')

    # ---- why
    cards = "\n".join(f'''      <div class="why-card">
        <div class="w-icon">{ICON[c[0]]}</div>
        <h3>{c[1]}</h3>
        <p>{c[2]}</p>
      </div>''' for c in d["why_cards"])
    why_bg = BANK_WHY_BG if d["slug"].startswith("south-africa-bank") else SECTION_BG
    h.append(f'''
<section class="section why" id="why">
  <div class="section-bg">
    <picture><source srcset="{why_bg}" type="image/webp"><img src="{why_bg}" alt="{d["why_h2"]}" loading="lazy" title="{d["why_h2"]}"></picture>
    <div class="section-bg-overlay"></div>
  </div>
  <div class="container">
    <div class="section-title fade-in">
      <span class="section-label">{d["why_label"]}</span>
      <h2>{d["why_h2"]}</h2>
      <p>{d["why_intro"]}</p>
    </div>
    <div class="why-grid stagger-children">
{cards}
    </div>
    <div class="fade-in" style="max-width:900px;margin:2.5rem auto 0;padding:1.75rem 2rem;background:var(--card-bg);border:1px solid var(--card-border);border-left:3px solid var(--gold);border-radius:10px;">
      <p style="margin:0;color:var(--cream);line-height:1.9;">{d["why_note"]}</p>
    </div>
  </div>
</section>''')

    # ---- process
    steps = "\n".join(f'''      <div class="timeline-item fade-in">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <div class="step-num">STEP 0{i+1}</div>
          <h3>{s[0]}</h3>
          <p>{s[1]}</p>
        </div>
      </div>''' for i, s in enumerate(d["steps"]))
    link_html = ""
    if d.get("proc_link"):
        txt, url, anchor = d["proc_link"]
        if zh:
            link_html = (f'<p class="fade-in" style="max-width:820px;margin:2rem auto 0;text-align:center;color:var(--text-muted);line-height:1.9;">'
                         f'{txt.split("〈")[0]}<a href="{url}" style="color:var(--gold);text-decoration:underline;">{anchor}</a>。</p>')
        else:
            link_html = (f'<p class="fade-in" style="max-width:820px;margin:2rem auto 0;text-align:center;color:var(--text-muted);line-height:1.9;">'
                         f'For the full seven transfer steps and document checklist, read our guide: '
                         f'<a href="{url}" style="color:var(--gold);text-decoration:underline;">{anchor}</a>.</p>')
    h.append(f'''
<section class="section timeline" id="process">
  <div class="section-bg">
    <picture><source srcset="{SECTION_BG}" type="image/webp"><img src="{SECTION_BG}" alt="{d["proc_h2"]}" loading="lazy" title="{d["proc_h2"]}"></picture>
    <div class="section-bg-overlay"></div>
  </div>
  <div class="container">
    <div class="section-title fade-in">
      <span class="section-label">{d["proc_label"]}</span>
      <h2>{d["proc_h2"]}</h2>
      <p>{d["proc_intro"]}</p>
    </div>
    <div class="timeline-track">
{steps}
    </div>
    {link_html}
    <div class="fade-in" style="text-align:center;margin-top:2.75rem;">
      {cta(d["cta2"])}
    </div>
  </div>
</section>''')

    # ---- compare
    rows = "\n".join("          <tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in d["cmp_rows"])
    head_cells = "".join(f"<th>{x}</th>" for x in d["cmp_head"])
    body = "".join(f'      <p style="margin:0 0 1rem;color:var(--cream);line-height:1.95;">{p}</p>' for p in d["cmp_body"])
    links_html = ""
    if d.get("links"):
        lis = "".join(
            f'<li style="margin:.35rem 0;"><a href="{u}" style="color:var(--gold);text-decoration:underline;">{t}</a></li>'
            for t, u in d["links"])
        links_html = (
            '<div class="fade-in" style="max-width:900px;margin:1.5rem auto 0;padding:1.25rem 1.5rem;'
            'background:var(--card-bg);border:1px solid var(--card-border);border-radius:10px;">'
            f'<p style="margin:0 0 .5rem;font-size:.85rem;letter-spacing:.08em;color:var(--gold);">'
            f'{"延伸閱讀" if zh else "Further reading"}</p>'
            f'<ul style="margin:0;padding-left:1.1rem;font-size:.9rem;color:var(--cream);line-height:1.8;">{lis}</ul>'
            '</div>')
    h.append(f'''
<section class="section comparison" id="compare">
  <div class="section-bg">
    <picture><source srcset="{SECTION_BG}" type="image/webp"><img src="{SECTION_BG}" alt="{d["cmp_h2"]}" loading="lazy" title="{d["cmp_h2"]}"></picture>
    <div class="section-bg-overlay"></div>
  </div>
  <div class="container">
    <div class="section-title fade-in">
      <span class="section-label">{d["cmp_label"]}</span>
      <h2>{d["cmp_h2"]}</h2>
      <p>{d["cmp_intro"]}</p>
    </div>
    <div class="comparison-table-wrap fade-in">
      <table class="comparison-table">
        <thead>
          <tr>{head_cells}</tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <div class="section-title fade-in" style="margin-top:3.5rem;">
      <h2>{d["cmp_h2b"]}</h2>
    </div>
    <div class="fade-in" style="max-width:900px;margin:0 auto;">
{body}
    </div>
    {links_html}
  </div>
</section>''')

    # ---- faq
    faqs = "\n".join(f'''      <div class="faq-item fade-in">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>{q}</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="faq-answer">
          <p>{a}</p>
        </div>
      </div>''' for q, a in d["faqs"])
    h.append(f'''
<section class="section faq" id="faq">
  <div class="section-bg">
    <picture><source srcset="{SECTION_BG}" type="image/webp"><img src="{SECTION_BG}" alt="{d["faq_h2"]}" loading="lazy" title="{d["faq_h2"]}"></picture>
    <div class="section-bg-overlay"></div>
  </div>
  <div class="container">
    <div class="section-title fade-in">
      <span class="section-label">Frequently Asked Questions</span>
      <h2>{d["faq_h2"]}</h2>
      <p>{d["faq_sub"]}</p>
    </div>
    <div class="faq-list">
{faqs}
    </div>
    <div class="fade-in" style="text-align:center;margin-top:2.5rem;">
      {cta(d["cta3"])}
    </div>
  </div>
</section>''')

    # ---- cta
    h.append(f'''
<section class="section cta-section" id="cta">
  <div class="section-bg">
    <picture><source srcset="{SECTION_BG}" type="image/webp"><img src="{SECTION_BG}" alt="{d["cta_h2"][0]}{d["cta_h2"][1]}" loading="lazy" title="{d["cta_h2"][0]}{d["cta_h2"][1]}"></picture>
    <div class="section-bg-overlay"></div>
  </div>
  <div class="container">
    <div class="cta-card fade-in">
      <span class="section-label">{d["cta_label"]}</span>
      <h2>{d["cta_h2"][0]}<br>{d["cta_h2"][1]}</h2>
      <p>{d["cta_p"]}</p>
      {cta(d["cta4"])}
      <p style="margin:1.75rem auto 0;max-width:760px;font-size:0.78rem;line-height:1.8;color:var(--text-muted);">{d["disclaimer"]}</p>
    </div>
  </div>
</section>

</main>''')
    return "\n".join(h)


def jsonld(d):
    site = {
        "@context": "https://schema.org", "@type": "WebSite",
        "name": "鼎曜國際顧問 DingYao Advisory" if d["lang"] == "zh-Hant" else "DingYao Advisory",
        "url": "https://dingyaoadvisory.tw",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint",
                       "urlTemplate": "https://dingyaoadvisory.tw/blog?q={search_term_string}"},
            "query-input": "required name=search_term_string",
        },
    }
    fin = {
        "@context": "https://schema.org", "@type": "FinancialService",
        "name": d["schema_name"], "description": d["schema_desc"],
        "url": d["alt_zh"] if d["lang"] == "zh-Hant" else d["alt_en"],
        "areaServed": [{"@type": "Country", "name": "South Africa"},
                       {"@type": "City", "name": "Cape Town"},
                       {"@type": "Country", "name": "Taiwan"}],
        "address": {"@type": "PostalAddress", "addressLocality": "台中市",
                    "addressRegion": "西屯區", "addressCountry": "TW"},
        "contactPoint": {"@type": "ContactPoint", "email": "info@dingyaoadvisory.tw",
                         "contactType": "customer service"},
        "sameAs": ["https://www.facebook.com/DingYaoAdvisory/",
                   "https://www.instagram.com/dingyaoadvisory",
                   "https://x.com/dingyaoadvisory",
                   "https://www.linkedin.com/company/dingyaoadvisory/"],
    }
    crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1,
             "name": "首頁" if d["lang"] == "zh-Hant" else "Home",
             "item": "https://dingyaoadvisory.tw/"},
            {"@type": "ListItem", "position": 2, "name": d["crumb"],
             "item": d["alt_zh"] if d["lang"] == "zh-Hant" else d["alt_en"]},
        ],
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in d["faqs"]],
    }
    return "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n</script>'
                     for x in (fin, site, crumb, faq))


def build(d, base_path, out_name):
    src = base_path.read_text(encoding="utf-8")
    i_head = src.index("<header")
    i_head_end = src.index("</header>") + len("</header>")
    i_main = src.index("<main")
    i_main_end = src.index("</main>") + len("</main>")
    pre, nav, tail = src[:i_head], src[i_head:i_head_end], src[i_main_end:]

    def sub1(pattern, repl, s, flags=re.S):
        new, n = re.subn(pattern, repl, s, count=1, flags=flags)
        assert n == 1, f"pattern not found: {pattern[:60]}"
        return new

    h = pre
    h = sub1(r"<title>.*?</title>", f"<title>{d['title']}</title>", h)
    h = sub1(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + d["desc"] + m.group(2), h)
    h = sub1(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + d["og_title"] + m.group(2), h)
    h = sub1(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + d["desc"] + m.group(2), h)
    h = sub1(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + d["alt_zh"] + m.group(2), h)
    h = sub1(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + d["og_title"] + m.group(2), h)
    h = sub1(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + d["desc"] + m.group(2), h)
    h = sub1(r'(<link rel="canonical" href=")[^"]*(")',
             lambda m: m.group(1) + (d["alt_zh"] if d["lang"] == "zh-Hant" else d["alt_en"]) + m.group(2), h)
    h = sub1(r'(<link rel="alternate" hreflang=")(?:zh-Hant|zh-TW)(" href=")[^"]*(")',
             lambda m: m.group(1) + "zh-Hant" + m.group(2) + d["alt_zh"] + m.group(3), h)
    h = sub1(r'(<link rel="alternate" hreflang="en" href=")[^"]*(")',
             lambda m: m.group(1) + d["alt_en"] + m.group(2), h)
    h = sub1(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")',
             lambda m: m.group(1) + d["alt_zh"] + m.group(2), h)
    # images: og / twitter -> webp hero
    h = re.sub(r'(<meta property="og:image" content=")[^"]*(")', r"\g<1>" + HERO_BG + r"\g<2>", h)
    h = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', r"\g<1>" + HERO_BG + r"\g<2>", h)
    # drop inherited JSON-LD, inject ours before </head>
    h = re.sub(r'\n?<script type="application/ld\+json">.*?</script>', "", h, flags=re.S)
    h = h.replace("</head>", jsonld(d) + "\n</head>", 1)

    html = h + nav + rnd_main_hack(d) + tail
    (OUT / out_name).write_text(html, encoding="utf-8")
    return OUT / out_name


def rnd_main_hack(d):
    return render_main(d)


CANON = {
    "一年期利率": ("One-year rate", "計息幣別", "Currency", "主要成本", "Main costs"),
}


def with_heads(d):
    """cmp_rows 第一欄是列名 → 補上 thead（模板需要 thead）"""
    if d["slug"].startswith("south-africa-bank"):
        d["cmp_head"] = (["比較項目", "台灣一年期定存", "南非 Money Market"] if d["lang"] == "zh-Hant"
                         else ["Item", "Taiwan 1-year deposit", "South Africa money market"])
    else:
        d["cmp_head"] = (["成本項目", "買入階段", "持有階段（每年）", "退出階段"] if d["lang"] == "zh-Hant"
                         else ["Cost item", "Acquisition", "Holding (annual)", "Exit"])
    for r in d["cmp_rows"]:
        assert len(r) == len(d["cmp_head"]), (d["slug"], len(r), len(d["cmp_head"]))
    return d


if __name__ == "__main__":
    jobs = [
        (page_zh_bank, BASE_ZH, "south-africa-bank-account.html"),
        (page_en_bank, BASE_EN, "south-africa-bank-account-en.html"),
        (page_zh_property, BASE_ZH, "south-africa-property.html"),
        (page_en_property, BASE_EN, "south-africa-property-en.html"),
    ]
    for fn, base, name in jobs:
        d = with_heads(fn())
        p = build(d, base, name)
        print(f"wrote {p.name}  {p.stat().st_size:,} bytes")
