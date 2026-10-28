#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署前資產閘門：確認文章引用的 CDN 圖檔真的存在（全 200）才准 push。

為什麼需要（2026-10-28，S-20261028-VALU）：
valuation 頁的草稿寫好了、圖還沒上 R2，若照常部署 → 上線即破圖。
「破圖上線」比「延後一天」更糟，所以把檢查做成機械閘門，不靠人記得。

用法：
  python3 scripts/check_assets_ready.py _drafts/blog/<slug>.html
  python3 scripts/check_assets_ready.py dist/blog/<slug>.html --retries 2
  python3 scripts/check_assets_ready.py <slug> --expect 7      # 額外要求圖檔數 == 7

行為：
- 從 HTML 抓出所有 assets.dingyaoadvisory.tw 的 src（含 <img>、srcset、JSON-LD image）
- 對每個 URL 做 HEAD（失敗改 GET，某些 CDN 不支援 HEAD）
- 全部 200 → exit 0；任一非 200／連線失敗 → exit 1（呼叫端必須停手、不 push）
- --expect N：圖檔去重後數量必須等於 N，用來抓「少傳一張」這種靜默缺圖
"""
import http.client
import re
import sys
import time
import urllib.parse
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 TitanAssetGate/1.0"}
ASSET_HOST = "assets.dingyaoadvisory.tw"


def extract_urls(html: str) -> list:
    """抓出 HTML 內所有 CDN 資源 URL（src／srcset／JSON-LD image 皆涵蓋）。

    用白名單字元集，避免跳脫字元把字元類別吃掉（2026-10-28 踩過：0 命中誤判）。
    """
    urls = set()
    pat = r"https://" + re.escape(ASSET_HOST) + r"/[A-Za-z0-9_\-./%]+"
    for m in re.finditer(pat, html):
        urls.add(m.group(0).rstrip(".,;"))
    return sorted(urls)


def head(url: str, retries: int = 1, timeout: int = 20):
    last = ("ERR", "")
    for attempt in range(retries + 1):
        for method in ("HEAD", "GET"):
            try:
                p = urllib.parse.urlparse(url)
                conn = http.client.HTTPSConnection(p.netloc, timeout=timeout)
                path = (p.path or "/") + (("?" + p.query) if p.query else "")
                conn.request(method, path, headers=UA)
                r = conn.getresponse()
                r.read()
                code = r.status
                conn.close()
                if code in (403, 405):  # 某些 CDN 擋 HEAD
                    continue
                return code, ""
            except Exception as e:  # noqa: BLE001
                last = ("ERR", str(e)[:60])
        if attempt < retries:
            time.sleep(0.8 * (attempt + 1))
    return last[0], last[1]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = [a for a in sys.argv[1:] if a.startswith("--")]
    if not args:
        print("用法: check_assets_ready.py <html 檔或 dist 相對路徑> [--expect N] [--retries N]")
        return 2

    target = Path(args[0])
    if not target.exists():
        # 允許只給 slug，自動找 _drafts/blog 與 dist/blog
        slug = args[0]
        for cand in (Path("_drafts/blog") / f"{slug}.html", Path("dist/blog") / f"{slug}.html"):
            if cand.exists():
                target = cand
                break
        else:
            print(f"❌ 找不到檔案: {args[0]}")
            return 2

    expect = None
    retries = 1
    for o in opts:
        if o.startswith("--expect="):
            expect = int(o.split("=", 1)[1])
        elif o.startswith("--retries="):
            retries = int(o.split("=", 1)[1])

    html = target.read_text(encoding="utf-8", errors="ignore")
    urls = extract_urls(html)
    print(f"檔案: {target}")
    print(f"CDN 資源數（去重）: {len(urls)}")

    bad = []
    for u in urls:
        code, note = head(u, retries=retries)
        mark = "✅" if code == 200 else "❌"
        print(f"  {mark} {code}  {u}" + (f"  ({note})" if note else ""))
        if code != 200:
            bad.append((u, code))

    problems = []
    if bad:
        problems.append(f"{len(bad)}/{len(urls)} 個 CDN 資源非 200")
    if expect is not None and len(urls) != expect:
        problems.append(f"資源數 {len(urls)} != 預期 {expect}")

    print()
    if problems:
        print("❌ 資產閘門 FAIL：")
        for p in problems:
            print("   " + p)
        print("   → 不要 push。圖沒到齊就上線＝破圖，比延後更糟。")
        return 1
    print(f"✅ 資產閘門 PASS：{len(urls)}/{len(urls)} 全部 200")
    return 0


if __name__ == "__main__":
    sys.exit(main())
