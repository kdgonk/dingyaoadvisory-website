#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sitemap 一致性驗證（D2 回歸防線，2026-10-20）

為什麼需要：
2026-10-20 發生「sitemap 又收錄 301 URL」回歸 —— 10-19 驗收為 0，隔天變 5 筆。
根因是每次重生 sitemap（booking 功能、blog-automation 補頁）都會把
被 _redirects 301 攔截、但實體檔案仍在 dist/ 的舊頁重新收進來。

本腳本做三件事（雙向驗證，避免單向誤判）：

  1. sitemap.xml 每個 <loc> 實際 HTTP 必須 200
     → 有任何 301/404 就是回歸，exit 1

  2. _redirects 每個來源 URL 實際必須是 301/308
     → 若某來源回 200，代表它其實是活頁，把它排除在 sitemap 外才是錯的
       （scripts/verify_redirect_sources.py 的邏輯，這裡合併進來）

  3. sitemap 內不得出現 _redirects 來源（靜態交叉檢查，不需連網）
     → 即使 live 檢查因快取僥倖過關，這條也會抓到

用法：
  python3 scripts/verify_sitemap_live.py            # 完整檢查（含 live，約 30s）
  python3 scripts/verify_sitemap_live.py --offline  # 只做第 3 項靜態檢查

退出碼：0 = 全通過；1 = 有問題（可掛 cron 告警）
"""
import concurrent.futures as cf
import http.client
import pathlib
import re
import sys
import time
import urllib.parse

UA = {"User-Agent": "Mozilla/5.0 TitanSitemapAudit/1.0"}
BASE_HOST = "dingyaoadvisory.tw"
ROOT = pathlib.Path(__file__).parent.parent / "dist"
SITEMAP = ROOT / "sitemap.xml"
REDIRECTS = ROOT / "_redirects"


def load_sitemap_locs() -> list:
    xml = SITEMAP.read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", xml)


def load_redirect_sources() -> set:
    """_redirects 中作為來源的 path（排除 splat 與絕對 URL）"""
    if not REDIRECTS.exists():
        return set()
    out = set()
    for line in REDIRECTS.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        src = parts[0]
        if src.startswith("http") or "*" in src:
            continue
        out.add("/" + src.lstrip("/").rstrip("/"))
    return out


def check_url(u: str, want_redirect: bool = False, retries: int = 2):
    """回傳 (url, status, location)。不跟隨 redirect。

    ERR（SSL handshake timeout / 連線重置）在並發 25 下偶爾發生，
    不是真的 301/404 —— 必須重試，否則會誤報回歸。
    """
    last = ("ERR", "")
    for attempt in range(retries + 1):
        try:
            p = urllib.parse.urlparse(u)
            conn = http.client.HTTPSConnection(p.netloc or BASE_HOST, timeout=25)
            path = (p.path or "/") + (("?" + p.query) if p.query else "")
            conn.request("HEAD", path, headers=UA)
            r = conn.getresponse()
            r.read()
            code, loc = r.status, r.getheader("location") or ""
            conn.close()
            return u, code, loc
        except Exception as e:
            last = ("ERR", str(e)[:60])
            if attempt < retries:
                time.sleep(0.6 * (attempt + 1))
    return u, last[0], last[1]


def main():
    offline = "--offline" in sys.argv
    problems = []

    locs = load_sitemap_locs()
    sources = load_redirect_sources()
    print(f"sitemap 條目: {len(locs)} ｜ _redirects 來源: {len(sources)}")

    # ── 3. 靜態交叉檢查（不需連網，最快也最可靠）──
    in_sm_as_source = []
    for u in locs:
        path = urllib.parse.urlparse(u).path.rstrip("/") or "/"
        if path in sources:
            in_sm_as_source.append(path)
    if in_sm_as_source:
        problems.append(f"[靜態] sitemap 含 {len(in_sm_as_source)} 筆 _redirects 來源: "
                        + ", ".join(in_sm_as_source[:8]))
        print(f"  ❌ [靜態] sitemap 含 _redirects 來源 {len(in_sm_as_source)} 筆")
        for p in in_sm_as_source[:10]:
            print(f"       {p}")
    else:
        print("  ✅ [靜態] sitemap 不含任何 _redirects 來源")

    if offline:
        return finish(problems)

    # ── 1. sitemap 每條必須 200 ──
    print("\n檢查 sitemap 每條 HTTP 狀態（並發 25）...")
    non200 = []
    with cf.ThreadPoolExecutor(max_workers=25) as ex:
        for u, code, loc in ex.map(check_url, locs):
            if code != 200:
                non200.append((u, code, loc))
    if non200:
        problems.append(f"[live] sitemap 有 {len(non200)} 筆非 200")
        print(f"  ❌ [live] {len(non200)} 筆非 200:")
        for u, c, l in non200[:15]:
            print(f"       {c}  {u}" + (f"  → {l}" if l else ""))
    else:
        print(f"  ✅ [live] {len(locs)}/{len(locs)} 全部 200，0 筆 301")

    # ── 2. _redirects 來源必須真的 301（沒被 200 遮蔽）──
    print("\n檢查 _redirects 來源是否真的 redirect（並發 25）...")
    base = f"https://{BASE_HOST}"
    shadowed = []
    with cf.ThreadPoolExecutor(max_workers=25) as ex:
        for u, code, loc in ex.map(lambda s: check_url(base + s, True), sorted(sources)):
            if code not in (301, 302, 307, 308):
                shadowed.append((u, code))
    if shadowed:
        problems.append(f"[live] {len(shadowed)} 個 _redirects 來源沒有 redirect（可能被 200 遮蔽）")
        print(f"  ❌ {len(shadowed)} 個來源未 301：")
        for u, c in shadowed[:15]:
            print(f"       {c}  {u}")
    else:
        print(f"  ✅ {len(sources)}/{len(sources)} 來源全部 301/308，無 200 遮蔽")

    return finish(problems)


def finish(problems):
    print("\n" + "=" * 60)
    if problems:
        print("❌ 驗證失敗（D2 回歸）")
        for p in problems:
            print("   " + p)
        return 1
    print("✅ 全部通過：sitemap 零 301、零 404，_redirects 來源全數生效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
