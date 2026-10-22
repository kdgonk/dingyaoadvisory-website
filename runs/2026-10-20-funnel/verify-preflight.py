#!/usr/bin/env python3
"""
新頁上線前 preflight 驗收（可重複執行）。

任務指定的三項硬性檢查：
  1. 200 頁：HTTP 200 + 有 body + content-type text/html
  2. 404 頁：HTTP 404（不是 200 假 404）+ 有 body（不是空白頁）
  3. 原始碼不外洩：不得出現 API token / Chatwoot token / secret / 內部路徑

外加（本站在意的）：
  4. nav / footer 與全站主流版型一致（hash 比對）
  5. canonical / hreflang / title / H1 / description 存在且長度合理
  6. 簡體字掃描（避免繁體站破功）

用法：
  python3 verify-preflight.py https://dingyaoadvisory.tw /south-africa-property /education
  python3 verify-preflight.py https://dingyaoadvisory.tw --all-main
"""
import hashlib
import re
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 TitanPreflight/1.0"

# 全站版型基準（2026-10-20 實測 md5 分群）
#   ZH nav 主流 9eb32b9e（17 頁）／EN nav 主流 d0042931（13 頁）
#   ZH footer 主流 254c835e（12 頁）
# EN footer 各頁差異大（education-en d41caa84、index-en 91df32a5、assets-en 338b413d…），
# 因此 EN 頁只驗 footer「存在」，不驗 hash —— 否則會誤報。
EXPECT_NAV_ZH = "9eb32b9e"
EXPECT_NAV_EN = "d0042931"
EXPECT_FOOTER_ZH = "254c835e"
# 保留舊名以相容
EXPECT_NAV_HASH = EXPECT_NAV_ZH
EXPECT_FOOTER_HASH = EXPECT_FOOTER_ZH

LEAK_PATTERNS = [
    (r"api_access_token", "Chatwoot api_access_token"),
    (r"CHATWOOT_API_TOKEN", "Worker secret 名稱"),
    (r"[A-Za-z0-9]{20,}[-_][A-Za-z0-9]{10,}", None),  # 通用長 token 形狀（僅提示）
    (r"GE1kJsMKRMZQJ3EyLgkLsQjR", "Chatwoot website token（GTM 內，頁面不該有）"),
    (r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}", "Bearer token"),
    (r"/Users/[a-z]+/", "本機絕對路徑"),
    (r"C:\\\\Users", "Windows 路徑"),
]

# 只放「繁體文本絕不會出現」的簡體專用『單字』。
# 陷阱（2026-10-20 實測踩過兩次）：若用詞組如「房贷」「价格」「质量」「厂商」，
# 會把 房/格/量/商 這些繁簡同形字一起收進來 → 現有頁面全部誤報。
# 因此下面逐一列單字，且每個都已確認繁體不使用。
SIMPLIFIED_ONLY = set(
    "这个电话时间问题实现发现应该经过认为学习济国际专业产业组织营销质价"
    "开务门处数据网络软体优势机会风险资购买卖贷银证规标义权责厂运输赢脑忆讯"
)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS  " if ok else "FAIL  ") + name + (f"  :: {detail}" if detail else ""))
    return ok


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", errors="ignore"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="ignore"), dict(e.headers)
    except Exception as e:
        return 0, "", {"error": str(e)}


def block_hash(text, tag):
    m = re.search(rf"<{tag}[\s\S]*?</{tag}>", text)
    if not m:
        return None
    return hashlib.md5(m.group(0).encode()).hexdigest()[:8]


def scan_leak(html, label):
    hits = []
    for pat, desc in LEAK_PATTERNS:
        if desc is None:
            continue
        for m in re.finditer(pat, html):
            hits.append(f"{desc}: {m.group(0)[:24]}…")
    return hits


def verify_page(base, path):
    url = base.rstrip("/") + path
    print(f"\n{'='*70}\n{url}\n{'='*70}")
    status, html, hdrs = fetch(url)
    ctype = hdrs.get("Content-Type", "")

    ok_status = status == 200
    check("HTTP 200", ok_status, f"status={status}")
    if not ok_status:
        return
    check("有 body", len(html) > 5000, f"{len(html)} bytes")
    check("content-type text/html", "text/html" in ctype, ctype)

    # 原始碼不外洩
    leaks = scan_leak(html, path)
    check("原始碼無 token / 內部路徑外洩", len(leaks) == 0, leaks[:3])

    # nav / footer 一致性（依語系判定基準）
    is_en = path.rstrip("/").endswith("-en") or path.rstrip("/").endswith("/index-en")
    nh, fh = block_hash(html, "nav"), block_hash(html, "footer")
    exp_nav = EXPECT_NAV_EN if is_en else EXPECT_NAV_ZH
    check(f"nav 與全站{'EN' if is_en else 'ZH'}版型一致 ({exp_nav})", nh == exp_nav, f"got={nh}")
    if is_en:
        check("footer 存在（EN 版各頁差異大，不驗 hash）", fh is not None, f"got={fh}")
    else:
        check(f"footer 與全站一致 ({EXPECT_FOOTER_ZH})", fh == EXPECT_FOOTER_ZH, f"got={fh}")

    # SEO 基本
    t = re.search(r"<title>([^<]*)</title>", html)
    title = t.group(1) if t else ""
    check("title 存在且 10-60 字", 10 <= len(title) <= 60, f"len={len(title)} | {title[:50]}")

    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = d.group(1) if d else ""
    check("description 存在且 80-320 字", 80 <= len(desc) <= 320, f"len={len(desc)}")

    h1s = re.findall(r"<h1[^>]*>([\s\S]*?)</h1>", html)
    check("H1 恰好 1 個", len(h1s) == 1, f"count={len(h1s)}")
    if h1s:
        h1txt = re.sub(r"<[^>]+>", "", h1s[0]).strip()
        print(f"        H1 = {h1txt[:60]}")

    check("canonical 存在", 'rel="canonical"' in html)
    hreflang = len(re.findall(r'rel="alternate"', html))
    check("hreflang >= 2", hreflang >= 2, f"count={hreflang}")

    # 簡體字（單字集合比對，已排除繁簡同形字）
    simp = sorted({ch for ch in html if ch in SIMPLIFIED_ONLY})
    check("無簡體字", len(simp) == 0, "".join(simp[:12]))

    # GTM + consent 順序
    gtmi = html.find("GTM-PVWHRBWG")
    check("GTM 容器存在", gtmi > -1)
    if gtmi > -1:
        ci = html.find("gtag('consent','default'")
        check("consent default 在 GTM 之前", 0 < ci < gtmi, f"consent@{ci} gtm@{gtmi}")
        check("GTM noscript 存在", "ns.html?id=GTM-PVWHRBWG" in html)


def verify_404(base):
    print(f"\n{'='*70}\n404 / 缺頁處理\n{'='*70}")
    status, html, hdrs = fetch(base.rstrip("/") + "/this-page-should-not-exist-xyz-987")
    check("不存在的頁回 HTTP 404（不是 200 假頁）", status == 404, f"status={status}")
    check("404 有 body", len(html) > 1000, f"{len(html)} bytes")
    check("404 是 text/html", "text/html" in hdrs.get("Content-Type", ""), hdrs.get("Content-Type", ""))
    low = html.lower()
    check("404 頁沒有 noindex 以外的錯誤（可索引頁不該用 404）", "404" in low or "找不到" in html or "迷路" in html,
          "404 語意文字存在")
    leaks = scan_leak(html, "404")
    check("404 頁無 token 外洩", len(leaks) == 0, leaks[:3])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    base = sys.argv[1]
    paths = sys.argv[2:]

    if "--all-main" in paths:
        paths = ["/", "/education", "/residency", "/retirement", "/assets", "/platform",
                 "/partners", "/overseas-buyers", "/consultation", "/contact", "/about", "/blog"]

    for p in paths:
        verify_page(base, p)
    verify_404(base)

    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    print(f"\n{'='*70}\n{passed}/{total} 通過")
    fails = [n for n, ok in results if not ok]
    if fails:
        print("未通過：")
        for f in fails:
            print("  - " + f)
    print("=" * 70)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
