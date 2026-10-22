#!/usr/bin/env python3
"""產生 dist/l/<key>.html —— /l/* 的實體靜態雙保險（2026-10-22）。

為什麼要實體檔：`wrangler.jsonc` 的 `not_found_handling: "404-page"` 會讓
「不存在於 dist 的路徑」回 404.html，而那個 404 帶 `cache-control: public`，
會被 Cloudflare 邊緣快取（依 Accept 分流）。路徑只要有實體檔，就永遠不會
產生 404，也就永遠不會有「快取 404」可被命中。

每個檔：noindex,nofollow + meta refresh 0 → 目標（含 UTM）+ 手動點擊 fallback。
"""
import html
import pathlib

UTM = "utm_source=line&utm_medium=oa"
ASSET = "https://assets.dingyaoadvisory.tw/whitepapers/"

LINKS = [
    ("wb-bank", ASSET + "dingyao-bank-vs-taiwan-whitepaper-2026-zh.pdf", "whitebook", "bank", "銀行開戶白皮書"),
    ("wb-prop", ASSET + "dingyao-property-whitepaper-2026-zh.pdf", "whitebook", "prop", "房產投資白皮書"),
    ("wb-edu", ASSET + "dingyao-education-whitepaper-2026-zh.pdf", "whitebook", "edu", "教育規劃白皮書"),
    ("wb-rent", ASSET + "dingyao-rental-management-whitepaper-2026-zh.pdf", "whitebook", "rent", "包租代管白皮書"),
    ("bank", "https://dingyaoadvisory.tw/south-africa-bank-account", "menu", "bank", "南非銀行開戶"),
    ("prop", "https://dingyaoadvisory.tw/south-africa-property", "menu", "prop", "南非房產投資"),
    ("edu", "https://dingyaoadvisory.tw/education", "menu", "edu", "南非教育規劃"),
    ("book", "https://cal.com/dingyao/30min", "booking", "human", "預約 30 分鐘諮詢"),
    ("consult", "https://dingyaoadvisory.tw/consultation", "menu", "consult", "預約顧問諮詢"),
    ("line", "https://dingyaoadvisory.tw/", "menu", "home", "鼎曜國際顧問官網"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="refresh" content="0;url={target_attr}">
<title>前往{label} | 鼎曜國際顧問 DingYao Advisory</title>
<link rel="canonical" href="{target_attr}">
<meta name="theme-color" content="#0A0E17">
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
         background:#0A0E17; color:#F5F1E8; font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;
         padding:24px; }}
  .card {{ max-width:520px; width:100%; border:1px solid rgba(198,168,106,.35); border-radius:16px;
          padding:36px 28px; text-align:center; background:rgba(255,255,255,.02); }}
  .mark {{ font-size:13px; letter-spacing:.28em; color:#C6A86A; text-transform:uppercase; }}
  h1 {{ font-size:20px; font-weight:500; margin:18px 0 10px; line-height:1.5; }}
  p {{ font-size:14px; color:#9AA4B2; line-height:1.8; margin:0 0 22px; }}
  a.btn {{ display:inline-block; background:#C6A86A; color:#0A0E17; text-decoration:none;
          font-weight:700; padding:13px 26px; border-radius:999px; font-size:15px; }}
  .url {{ margin-top:18px; font-size:11px; color:#5A6473; word-break:break-all; }}
</style>
</head>
<body>
  <main class="card">
    <div class="mark">DingYao Advisory</div>
    <h1>正在前往「{label}」</h1>
    <p>若沒有自動跳轉，請點下方按鈕繼續。</p>
    <a class="btn" href="{target_attr}" rel="noopener">前往{label}</a>
    <div class="url">{target_text}</div>
  </main>
  <noscript><p style="text-align:center;color:#9AA4B2">請點選上方連結繼續。</p></noscript>
</body>
</html>
"""


def main():
    out = pathlib.Path(__file__).resolve().parents[2] / "dist" / "l"
    out.mkdir(parents=True, exist_ok=True)
    for key, base, campaign, content, label in LINKS:
        sep = "&" if "?" in base else "?"
        target = f"{base}{sep}{UTM}&utm_campaign={campaign}&utm_content={content}"
        (out / f"{key}.html").write_text(
            TEMPLATE.format(
                target_attr=html.escape(target, quote=True),
                target_text=html.escape(target),
                label=label,
            ),
            encoding="utf-8",
        )
        print(f"{out / (key + '.html')}  ->  {target}")


if __name__ == "__main__":
    main()
