#!/usr/bin/env python3
"""
產生白皮書下載頁（/whitepapers）。

設計約束：
  1. nav / footer 直接從 dist/residency.html 原樣抽出 → 保證與全站主流版型
     (nav 9eb32b9e / footer 254c835e) byte-identical，不靠人工複製。
  2. PDF 路徑不寫進 HTML：表單送出成功才由 /api/whitepaper 回傳 download_url。
  3. 不引入任何外部新依賴（沿用站上既有 CSS 變數與字型）。
  4. 預埋 dy-funnel.js 的 UTM / LIFF 讀取：表單送出時把 attribution 一併帶給 API。
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
DIST = ROOT / "dist"
OUT = pathlib.Path(__file__).parent / "build"
OUT.mkdir(exist_ok=True)


def extract(source_file: str):
    c = (DIST / source_file).read_text(encoding="utf-8")
    nav = re.search(r"<nav[\s\S]*?</nav>", c).group(0)
    footer = re.search(r"<footer[\s\S]*?</footer>", c).group(0)
    return nav, footer


NAV, FOOTER = extract("residency.html")
NAV_HASH = hashlib.md5(NAV.encode()).hexdigest()[:8]
FOOTER_HASH = hashlib.md5(FOOTER.encode()).hexdigest()[:8]

WHITEPAPERS = [
    {
        "asset": "whitepaper_bank_account_2026",
        "pillar": "bank_account",
        "tag": "銀行開戶",
        "title": "南非銀行開戶完整指南",
        "desc": "外國人如何在南非開立個人與公司帳戶、所需文件、KYC 流程與常見退件原因。",
        "pages": "28 頁",
    },
    {
        "asset": "whitepaper_property_2026",
        "pillar": "property",
        "tag": "置產",
        "title": "開普敦置產 2026 決策手冊",
        "desc": "外國買家可購產權類型、過戶稅與規費試算、持有成本、出租報酬與退出機制。",
        "pages": "42 頁",
    },
    {
        "asset": "whitepaper_education_2026",
        "pillar": "education",
        "tag": "教育",
        "title": "南非頂級私校入學規劃",
        "desc": "Hilton College 等名校的申請時程、入學測驗、寄宿安排與家長陪讀簽證。",
        "pages": "31 頁",
    },
    {
        "asset": "whitepaper_tax_residency_2026",
        "pillar": "multi",
        "tag": "稅務",
        "title": "稅務居民身分與資產申報",
        "desc": "南非稅務居民認定、台斐租稅協定、海外資產申報義務與常見誤區。",
        "pages": "36 頁",
    },
]

CARDS = "\n".join(
    f"""                <article class="wp-card" data-asset="{w['asset']}">
                    <div class="wp-tag">{w['tag']}</div>
                    <h3>{w['title']}</h3>
                    <p>{w['desc']}</p>
                    <div class="wp-meta"><span>{w['pages']}</span><span>PDF</span></div>
                    <button type="button" class="wp-pick" data-asset="{w['asset']}" data-pillar="{w['pillar']}">免費取得這份</button>
                </article>"""
    for w in WHITEPAPERS
)

OPTIONS = "\n".join(
    f'                        <option value="{w["pillar"]}">{w["tag"]}｜{w["title"]}</option>' for w in WHITEPAPERS
)

HTML = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>南非投資白皮書免費下載 | 鼎曜國際顧問 DingYao Advisory</title>
<meta name="description" content="四份南非投資白皮書免費下載：銀行開戶、開普敦置產、頂級私校入學、稅務居民申報。填寫稱呼與 WhatsApp 即可取得完整 PDF。">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="https://dingyaoadvisory.tw/whitepapers">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:url" content="https://dingyaoadvisory.tw/whitepapers">
<meta property="og:title" content="南非投資白皮書免費下載 | 鼎曜國際顧問">
<meta property="og:description" content="四份南非投資白皮書免費下載：銀行開戶、開普敦置產、頂級私校入學、稅務居民申報。">
<meta property="og:type" content="website">
<meta property="og:image" content="https://assets.dingyaoadvisory.tw/og-image.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
:root {{
  --navy-deep: #0A0E17; --navy-dark: #0C1B33; --navy-mid: #1E3A5F;
  --gold: #C9A84C; --gold-pale: #E8D5A3; --warm-white: #F5F0E8;
  --text-muted: #8B8FA3; --card-bg: rgba(15, 23, 42, 0.8);
  --card-border: rgba(201, 168, 76, 0.15); --max-width: 1200px;
  --font-heading: 'Playfair Display', Georgia, serif;
  --font-body: 'Inter', -apple-system, sans-serif;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: var(--font-body); background: var(--navy-deep);
  color: var(--warm-white); line-height: 1.7; -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: var(--max-width); margin: 0 auto; padding: 0 24px; }}
.page-hero {{ padding: 140px 0 60px; text-align: center;
  background: radial-gradient(ellipse at top, rgba(30,58,95,.55), transparent 65%); }}
.page-hero h1 {{ font-family: var(--font-heading); font-size: clamp(1.9rem, 4vw, 3rem);
  font-weight: 700; margin-bottom: 18px; }}
.page-hero h1 em {{ color: var(--gold); font-style: normal; }}
.page-hero p {{ color: var(--text-muted); max-width: 620px; margin: 0 auto; font-size: 1.02rem; }}
.wp-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 22px; padding: 20px 0 60px; }}
.wp-card {{ background: var(--card-bg); border: 1px solid var(--card-border);
  border-radius: 16px; padding: 26px 24px; display: flex; flex-direction: column;
  transition: transform .3s ease, border-color .3s ease; }}
.wp-card:hover {{ transform: translateY(-4px); border-color: rgba(201,168,76,.4); }}
.wp-tag {{ display:inline-block; font-size: .72rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--gold); border: 1px solid rgba(201,168,76,.35);
  border-radius: 999px; padding: 3px 12px; margin-bottom: 14px; align-self: flex-start; }}
.wp-card h3 {{ font-family: var(--font-heading); font-size: 1.22rem; margin-bottom: 10px; line-height: 1.4; }}
.wp-card p {{ color: var(--text-muted); font-size: .92rem; flex: 1; margin-bottom: 16px; }}
.wp-meta {{ display:flex; justify-content:space-between; font-size:.78rem;
  color: rgba(139,143,163,.8); margin-bottom: 16px; }}
.wp-pick {{ width:100%; padding: 12px; border-radius: 10px; border: 1px solid rgba(201,168,76,.45);
  background: transparent; color: var(--gold); font-family: inherit; font-size: .92rem;
  font-weight: 600; cursor: pointer; transition: all .25s ease; }}
.wp-pick:hover, .wp-pick:focus-visible {{ background: var(--gold); color: var(--navy-deep); }}
.form-section {{ padding: 20px 0 100px; }}
.form-box {{ max-width: 620px; margin: 0 auto; background: var(--card-bg);
  border: 1px solid var(--card-border); border-radius: 20px; padding: 40px 36px; }}
.form-box h2 {{ font-family: var(--font-heading); font-size: 1.6rem; margin-bottom: 6px; }}
.form-box .sub {{ color: var(--text-muted); font-size: .9rem; margin-bottom: 26px; }}
.field {{ margin-bottom: 20px; }}
.field label {{ display:block; font-size:.86rem; font-weight:600; margin-bottom:8px; }}
.field label span {{ color: var(--gold); }}
.field input, .field select {{ width:100%; padding: 13px 15px; border-radius: 10px;
  border: 1px solid rgba(201,168,76,.22); background: rgba(10,14,23,.7);
  color: var(--warm-white); font-family: inherit; font-size: .95rem; }}
.field input:focus, .field select:focus {{ outline: none;
  border-color: var(--gold); box-shadow: 0 0 0 3px rgba(201,168,76,.12); }}
.field .hint {{ display:block; font-size:.76rem; color:var(--text-muted); margin-top:6px; }}
.consent-row {{ display:flex; gap:10px; align-items:flex-start; margin-bottom:22px;
  font-size:.82rem; color:var(--text-muted); }}
.consent-row input {{ width:16px; height:16px; margin-top:3px; flex-shrink:0; accent-color: var(--gold); }}
.consent-row a {{ color: var(--gold); text-decoration: underline; }}
.btn-submit {{ width:100%; padding: 15px; border:none; border-radius: 12px;
  background: linear-gradient(135deg, var(--gold), #b8942f); color: var(--navy-deep);
  font-family: inherit; font-size: 1rem; font-weight: 700; cursor: pointer;
  transition: opacity .25s ease, transform .25s ease; }}
.btn-submit:hover:not(:disabled) {{ transform: translateY(-2px); }}
.btn-submit:disabled {{ opacity: .6; cursor: not-allowed; }}
.form-error {{ display:none; margin-top:16px; padding:12px 14px; border-radius:10px;
  background: rgba(220,53,69,.12); border:1px solid rgba(220,53,69,.35); color:#ff9aa2; font-size:.86rem; }}
#wpSuccess {{ display:none; text-align:center; }}
#wpSuccess .icon {{ font-size: 2.6rem; color: var(--gold); margin-bottom: 14px; }}
#wpSuccess h3 {{ font-family: var(--font-heading); font-size: 1.5rem; margin-bottom: 10px; }}
#wpSuccess p {{ color: var(--text-muted); font-size: .92rem; margin-bottom: 20px; }}
.btn-download {{ display:inline-block; padding: 13px 30px; border-radius: 10px;
  background: var(--gold); color: var(--navy-deep); text-decoration:none; font-weight:700; }}
.trust {{ margin-top: 22px; font-size: .78rem; color: rgba(139,143,163,.75);
  display:flex; gap:16px; justify-content:center; flex-wrap:wrap; }}
@media (max-width: 640px) {{
  .page-hero {{ padding: 110px 0 40px; }}
  .form-box {{ padding: 30px 22px; }}
}}
</style>
</head>
<body data-pillar="multi">
{NAV}

<main>
  <section class="page-hero">
    <div class="wrap">
      <h1>南非投資<em>白皮書</em>免費下載</h1>
      <p>四份實戰文件，涵蓋開戶、置產、教育與稅務。填寫稱呼與聯絡方式即可取得完整 PDF，我們也會依你关心的項目提供對應章節。</p>
    </div>
  </section>

  <section class="wrap">
    <div class="wp-grid">
{CARDS}
    </div>
  </section>

  <section class="form-section">
    <div class="wrap">
      <div class="form-box">
        <h2>取得完整白皮書</h2>
        <p class="sub">三個欄位，30 秒完成。PDF 立即下載，不寄廣告信。</p>

        <form id="wpForm" novalidate>
          <div class="field">
            <label for="wpName">稱呼 <span>*</span></label>
            <input type="text" id="wpName" name="name" placeholder="例：陳先生 / Michelle" autocomplete="name" required maxlength="60">
          </div>

          <div class="field">
            <label for="wpPhone">WhatsApp 或手機 <span>*</span></label>
            <input type="tel" id="wpPhone" name="phone" placeholder="+886 912 345 678" autocomplete="tel" required maxlength="30">
            <small class="hint">請含國碼，方便我們用 WhatsApp 傳送後續章節。</small>
          </div>

          <div class="field">
            <label for="wpPillar">想了解哪一塊 <span>*</span></label>
            <select id="wpPillar" name="pillar" required>
                        <option value="">請選擇</option>
{OPTIONS}
            </select>
          </div>

          <label class="consent-row">
            <input type="checkbox" id="wpConsent" required>
            <span>我同意鼎曜國際顧問依 <a href="/privacy" target="_blank" rel="noopener">隱私政策</a> 使用上述資料與我聯繫。我不會收到未經同意的行銷群發。</span>
          </label>

          <button type="submit" class="btn-submit" id="wpSubmit">立即取得白皮書</button>
          <div class="form-error" id="wpError" role="alert"></div>
        </form>

        <div id="wpSuccess" role="status">
          <div class="icon"><i class="fas fa-circle-check"></i></div>
          <h3>已為你準備好</h3>
          <p id="wpSuccessText">點擊下方按鈕下載 PDF。若連結失效，請直接回覆我們的 WhatsApp。</p>
          <a class="btn-download" id="wpDownload" href="#" target="_blank" rel="noopener">下載白皮書 PDF</a>
        </div>

        <div class="trust">
          <span><i class="fas fa-lock"></i> 資料僅供顧問聯繫</span>
          <span><i class="fas fa-user-shield"></i> 不轉售名單</span>
        </div>
      </div>
    </div>
  </section>
</main>

{FOOTER}

<script src="/js/dy-funnel.js" defer></script>
<script>
(function () {{
  'use strict';
  var form = document.getElementById('wpForm');
  var submitBtn = document.getElementById('wpSubmit');
  var errBox = document.getElementById('wpError');
  var successBox = document.getElementById('wpSuccess');
  var currentAsset = 'whitepaper_property_2026'; // 預設；點卡片會換

  // 卡片「免費取得這份」→ 選定 asset + 捲到表單
  document.querySelectorAll('.wp-pick').forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      currentAsset = btn.getAttribute('data-asset');
      var pillar = btn.getAttribute('data-pillar');
      var sel = document.getElementById('wpPillar');
      if (pillar && sel) sel.value = pillar;
      var title = btn.closest('.wp-card').querySelector('h3').textContent;
      document.querySelector('.form-box h2').textContent = '取得：' + title;
      document.querySelector('.form-box').scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      document.getElementById('wpName').focus({{ preventScroll: true }});
    }});
  }});

  function showError(msg) {{
    errBox.textContent = msg;
    errBox.style.display = 'block';
  }}

  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    errBox.style.display = 'none';

    var name = document.getElementById('wpName').value.trim();
    var phone = document.getElementById('wpPhone').value.trim();
    var pillar = document.getElementById('wpPillar').value;
    var consent = document.getElementById('wpConsent').checked;

    if (!name) return showError('請填寫稱呼。');
    if (!/^[+\\d][\\d\\s()-]{{7,}}$/.test(phone)) return showError('請填寫有效的 WhatsApp 或手機號碼（含國碼）。');
    if (!pillar) return showError('請選擇想了解的項目。');
    if (!consent) return showError('請先勾選同意隱私政策。');

    // 取得 dy-funnel 保存的 attribution（UTM / LIFF 佔位）
    var utm = {{}};
    try {{
      if (window.dyFunnel && window.dyFunnel.attr) utm = window.dyFunnel.attr() || {{}};
    }} catch (err) {{ utm = {{}}; }}

    submitBtn.disabled = true;
    var original = submitBtn.textContent;
    submitBtn.textContent = '傳送中…';

    fetch('/api/whitepaper', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        name: name,
        phone: phone,
        pillar: pillar,
        asset_name: currentAsset,
        utm: utm
      }})
    }})
      .then(function (res) {{ return res.json().then(function (d) {{ return {{ ok: res.ok, data: d }}; }}); }})
      .then(function (r) {{
        if (!r.ok || !r.data.ok) throw new Error((r.data && r.data.error) || '送出失敗');

        // L3：白皮書表單送出成功
        // pillar 用「使用者選的那一個」，不是頁面的 multi —— GA4 才能按支柱算 L3 轉換
        if (window.dyFunnel && window.dyFunnel.lead) {{
          window.dyFunnel.lead({{
            lead_type: 'whitepaper',
            asset_name: currentAsset,
            form_id: 'wpForm',
            pillar: pillar
          }});
        }}

        form.style.display = 'none';
        successBox.style.display = 'block';
        var dl = document.getElementById('wpDownload');
        if (r.data.download_url) {{
          dl.href = r.data.download_url;
        }} else {{
          // 後端沒有對應檔案 → 不給假連結，改成人工跟進
          dl.style.display = 'none';
          document.getElementById('wpSuccessText').textContent =
            '我們已收到你的需求，顧問會透過 WhatsApp 把檔案傳給你。';
        }}
      }})
      .catch(function (err) {{
        submitBtn.disabled = false;
        submitBtn.textContent = original;
        showError('送出失敗，請稍後再試，或直接 WhatsApp 聯絡我們。');
      }});
  }});
}})();
</script>
</body>
</html>
"""

out_file = OUT / "whitepapers.html"
out_file.write_text(HTML, encoding="utf-8")

# 驗證 nav/footer 與來源 byte-identical
written = out_file.read_text(encoding="utf-8")
w_nav = re.search(r"<nav[\s\S]*?</nav>", written).group(0)
w_footer = re.search(r"<footer[\s\S]*?</footer>", written).group(0)

print(f"wrote {out_file} ({len(HTML)} bytes)")
print(f"nav    source={NAV_HASH} output={hashlib.md5(w_nav.encode()).hexdigest()[:8]} "
      f"{'MATCH' if w_nav == NAV else 'MISMATCH'}")
print(f"footer source={FOOTER_HASH} output={hashlib.md5(w_footer.encode()).hexdigest()[:8]} "
      f"{'MATCH' if w_footer == FOOTER else 'MISMATCH'}")
