#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""土星人三件修復（2026-10-21）

① 舊文 slug：savings-65-percent → savings-7-percent（含 301）
   注意：R2 圖片資產路徑 `blog/images/...-65-percent-hero.webp` 是實體檔名，
         不可改（42 處），只改 URL 路徑（37 處）。
② /assets 投資試算滑桿：updateCalculator() 函式不存在 → 補上
③ dual-engine 文章 `logo is not defined` → 第二個 IIFE 內補宣告

用法：python3 fix3.py [--dry]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path("dist")
OLD = "cape-town-dual-engine-income-rental-savings-65-percent"
NEW = "cape-town-dual-engine-income-rental-savings-7-percent"

# ══════════════════════════════════════════
# ② 計算機 JS
#    比例常數由既有初始值反推，確保初始顯示與修前完全一致：
#      房產配置 10,450,000 / 16,000,000 = 0.653125
#      活存配置  5,350,000 / 16,000,000 = 0.334375
#    驗算：8% × 10,450,000 = 836,000；7% × 5,350,000 = 374,500；
#          9% × 10,450,000 = 940,500；合計 2,151,000；ROI 13.44% → 13.4%
# ══════════════════════════════════════════
CALC_JS = """
<script>
/* ROI calculator（2026-10-21 補上：原本只有 oninput="updateCalculator()" 呼叫，
   函式從未定義，滑桿完全沒反應） */
function updateCalculator() {
  var $ = function (id) { return document.getElementById(id); };
  var amount = parseFloat($('investAmount').value);
  var appr   = parseFloat($('appreciation').value);
  var intr   = parseFloat($('interest').value);
  var rent   = parseFloat($('rental').value);

  var PROP_PCT = 0.653125;   // 房產配置比（由 10,450,000 / 16,000,000 反推）
  var SAV_PCT  = 0.334375;   // 活存配置比（由  5,350,000 / 16,000,000 反推）

  var prop = Math.round(amount * PROP_PCT);
  var sav  = Math.round(amount * SAV_PCT);

  var apprRet = Math.round(prop * appr / 100);
  var intrRet = Math.round(sav * intr / 100);
  var rentRet = Math.round(prop * rent / 100);
  var total   = apprRet + intrRet + rentRet;
  var roi     = amount > 0 ? (total / amount * 100) : 0;

  var fmt = function (n) { return 'R ' + n.toLocaleString('en-US'); };

  $('investAmountDisplay').textContent = fmt(amount);
  $('appreciationDisplay').textContent = appr + '%';
  $('interestDisplay').textContent     = intr + '%';
  $('rentalDisplay').textContent       = rent + '%';

  $('propertyAllocation').textContent = fmt(prop);
  $('savingsAllocation').textContent  = fmt(sav);
  $('appreciationReturn').textContent = '+' + fmt(apprRet);
  $('interestReturn').textContent     = '+' + fmt(intrRet);
  $('rentalReturn').textContent       = '+' + fmt(rentRet);
  $('totalReturn').textContent        = fmt(total);
  $('totalROI').textContent           = roi.toFixed(1) + '%';
}

document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('investAmount')) updateCalculator();
});
</script>
"""

# ══════════════════════════════════════════
# ③ logo 未定義：第二個 IIFE 內補宣告
# ══════════════════════════════════════════
LOGO_FIX_OLD = """// Language switcher
(function(){
  var path = window.location.pathname;
  var isEn = path.endsWith('-en') || path.endsWith('-en/');"""
LOGO_FIX_NEW = """// Language switcher
(function(){
  var path = window.location.pathname;
  var isEn = path.endsWith('-en') || path.endsWith('-en/');
  var logo = document.getElementById('navLogo');   // 2026-10-21 補：原本未宣告 → logo is not defined"""


def fix_slug(dry):
    """改檔名 + 全站 URL 引用（不含 R2 圖片資產）"""
    log = []
    # 改檔名
    for suf in ["", "-en"]:
        src = ROOT / "blog" / (OLD + suf + ".html")
        dst = ROOT / "blog" / (NEW + suf + ".html")
        if src.exists():
            log.append(f"rename {src.name} -> {dst.name}")
            if not dry:
                src.rename(dst)
        elif dst.exists():
            log.append(f"already renamed {dst.name}")

    # 全站引用（排除 images/ 路徑）
    url_pat = re.compile(r"(?<!images/)(?<![\w-])" + re.escape("blog/" + OLD))
    n_files = 0
    n_hits = 0
    for f in ROOT.rglob("*"):
        if f.suffix.lower() not in (".html", ".xml", ".txt", ".json") and f.name != "_redirects":
            continue
        try:
            c = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        new_c, k = url_pat.subn("blog/" + NEW, c)
        if k:
            n_files += 1
            n_hits += k
            if not dry:
                f.write_text(new_c, encoding="utf-8")
    log.append(f"URL 引用：{n_files} 檔 / {n_hits} 處")
    return log


def add_redirects(dry):
    p = ROOT / "_redirects"
    c = p.read_text(encoding="utf-8")
    lines = []
    for suf in ["", "-en"]:
        src = "/blog/" + OLD + suf
        dst = "/blog/" + NEW + suf
        if src not in c:
            lines.append(f"{src} {dst} 301")
    if not lines:
        return ["_redirects 已有規則"]
    if not dry:
        # 插在檔案最前面（Cloudflare 由上而下匹配，越前面優先）
        p.write_text("\n".join(lines) + "\n\n" + c, encoding="utf-8")
    return ["_redirects 新增：" + " ｜ ".join(lines)]


def inject_calc(dry):
    log = []
    for name in ["assets.html", "assets-en.html"]:
        p = ROOT / name
        if not p.exists():
            log.append(f"{name} 不存在")
            continue
        c = p.read_text(encoding="utf-8")
        if "function updateCalculator" in c:
            log.append(f"{name} 已有函式，略過")
            continue
        if "updateCalculator()" not in c:
            log.append(f"{name} 無呼叫，略過")
            continue
        if not dry:
            p.write_text(c.replace("</body>", CALC_JS + "</body>", 1), encoding="utf-8")
        log.append(f"{name} 注入 updateCalculator ✅")
    return log


def fix_logo(dry):
    log = []
    for name in [OLD + ".html", OLD + "-en.html"]:
        p = ROOT / "blog" / name
        if not p.exists():
            log.append(f"{name} 不存在")
            continue
        c = p.read_text(encoding="utf-8")
        if "var logo = document.getElementById('navLogo');   // 2026-10-21" in c:
            log.append(f"{name} 已修")
            continue
        # 已宣告過就略過（EN 版第二個 IIFE 本來就有 var logo）
        if LOGO_FIX_OLD in c:
            if not dry:
                p.write_text(c.replace(LOGO_FIX_OLD, LOGO_FIX_NEW, 1), encoding="utf-8")
            log.append(f"{name} 補 var logo ✅")
        else:
            log.append(f"{name} 結構不同，已有宣告或無此區塊（略過）")
    return log


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    tag = "[DRY] " if dry else ""
    print(f"{tag}③ logo（先修，因為 ① 會改檔名）")
    for x in fix_logo(dry):
        print("   ", x)
    print(f"\n{tag}② 計算機")
    for x in inject_calc(dry):
        print("   ", x)
    print(f"\n{tag}① slug 改名")
    for x in fix_slug(dry):
        print("   ", x)
    print(f"\n{tag}① _redirects")
    for x in add_redirects(dry):
        print("   ", x)
