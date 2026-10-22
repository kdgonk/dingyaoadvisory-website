#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 6 批修正 1-3（土星人 2026-10-20）：

1. footer brand 脫離 .nav-logo（改用 .footer-logo + SVG mark + 兩行 wordmark），
   並修復既有 CSS 錯字：`.footer-brand .footer-brand p` → `.footer-brand p`
   （這條規則從來沒生效過，所以 footer 描述文字一直是 body 的 17.28px 而非 13.6px）
2. nav LOGO 尺寸 46x36 → 42x32（與兩行文字塊總高 ~32px 對齊）
3. 兩行 wordmark 置中對齊（align-items:center + text-align:center）

footer brand 有 5 種 href/id 變體，全部保留原 href 與 id：
  ZH 149 檔 href=dingyaoadvisory.tw id=navLogo
  EN 133 檔 href=/index-en        id=navLogo
  ZH  48 檔 href=dingyaoadvisory.tw id=navLogo2
  ZH  12 檔 href=dingyaoadvisory.tw 無 id
  EN   2 檔 href=/index-en        id=navLogo2
"""
import pathlib
import re
import sys
from collections import Counter

FOOTER_CSS = """.footer-logo{display:flex;align-items:center;gap:12px;text-decoration:none;margin-bottom:18px}
.footer-mark{width:38px;height:30px;display:block;flex-shrink:0}
.footer-wordmark{display:flex;flex-direction:column;line-height:1.15}
.footer-w1{font-family:Cinzel,serif;font-size:13px;font-weight:600;letter-spacing:1.4px;color:#F5F0E8}
.footer-w2{font-size:10px;letter-spacing:2px;color:#C9A84C;font-weight:600;margin-top:2px}
.footer-brand p{font-size:0.85rem;color:#F5F0E877;line-height:1.8;max-width:320px}
"""

FOOTER_LOGO_RE = re.compile(
    r'<a href="([^"]+)" class="nav-logo"(?: id="(navLogo2?)")? title="DYA DING YAO ADVISORY APAC HUB">'
    r'DYA<span>DING YAO ADVISORY APAC HUB</span></a>'
)


def build_footer_logo(href, id_attr):
    id_part = f' id="{id_attr}"' if id_attr else ""
    return (
        f'<a href="{href}" class="footer-logo"{id_part} title="DingYao Advisory">\n'
        f'          <img src="/dya-mark-whitegold.svg" alt="DYA" class="footer-mark" width="38" height="30">\n'
        f'          <span class="footer-wordmark">\n'
        f'            <span class="footer-w1">DingYao Advisory</span>\n'
        f'            <span class="footer-w2">APAC HUB</span>\n'
        f'          </span>\n'
        f'        </a>'
    )


def process(path: pathlib.Path, dry: bool):
    try:
        c = path.read_text(encoding="utf-8")
    except Exception:
        return "SKIP", "讀取失敗"

    orig = c
    notes = []

    # ── 項 1：footer brand（只在 <footer> 區段內處理）──
    fi = c.find("<footer")
    fe = c.find("</footer>", fi) if fi >= 0 else -1
    if fi >= 0 and fe > fi:
        ft = c[fi:fe]
        new_ft, n = FOOTER_LOGO_RE.subn(lambda m: build_footer_logo(m.group(1), m.group(2)), ft)
        if n:
            c = c[:fi] + new_ft + c[fe:]
            notes.append(f"footer-logo x{n}")
        elif "footer-logo" in ft:
            notes.append("footer-blog 已有")

    # ── 修既有 CSS 錯字（.footer-brand .footer-brand p）──
    bad_sel = ".footer-brand .footer-brand p{"
    if bad_sel in c:
        c = c.replace(bad_sel, ".footer-brand p{")
        notes.append("修 footer-brand p 選擇器")

    # ── 項 2 + 3：nav LOGO 尺寸與置中 ──
    # img 屬性
    c2 = c.replace(
        '<img src="/dya-mark-whitegold.svg" alt="DYA" class="nav-mark" width="46" height="36">',
        '<img src="/dya-mark-whitegold.svg" alt="DYA" class="nav-mark" width="42" height="32">'
    )
    if c2 != c:
        notes.append("nav img 42x32")
        c = c2
    # CSS
    c2 = c.replace(".nav-mark{width:46px;height:36px;", ".nav-mark{width:42px;height:32px;")
    if c2 != c:
        notes.append("nav-mark CSS 42x32")
        c = c2

    # wordmark 置中
    old_wm = ".nav-wordmark{display:flex;flex-direction:column;line-height:1.15}"
    new_wm = ".nav-wordmark{display:flex;flex-direction:column;line-height:1.15;align-items:center;text-align:center}"
    if old_wm in c:
        c = c.replace(old_wm, new_wm)
        notes.append("wordmark 置中")

    # ── 插入 footer CSS（若尚未有 .footer-logo 規則）──
    if ".footer-logo{" not in c:
        k = c.rfind("</style>")
        if k < 0:
            return "FAIL", "找不到 </style>"
        c = c[:k] + "\n/* ===== footer brand 獨立結構（2026-10-20 第 6 批） ===== */\n" + FOOTER_CSS + c[k:]
        notes.append("加 footer CSS")

    # ── 驗證 ──
    if "<footer" in c:
        fi2 = c.find("<footer"); fe2 = c.find("</footer>", fi2)
        ft2 = c[fi2:fe2]
        if 'class="nav-logo"' in ft2:
            return "FAIL", "footer 仍有 nav-logo"
        if "footer-mark" not in ft2 and "footer-logo" not in ft2:
            return "FAIL", "footer brand 未更新"
    if ".footer-brand .footer-brand p" in c:
        return "FAIL", "CSS 錯字未修"
    if c == orig:
        return "ALREADY", "無變化"

    if not dry:
        path.write_text(c, encoding="utf-8")
    return "OK", ",".join(notes)


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = [pathlib.Path(a) for a in args]
    stats = Counter()
    fails = []
    for f in files:
        st, note = process(f, dry)
        stats[st] += 1
        if st == "FAIL":
            fails.append((f, note))
    print(f"{'[DRY] ' if dry else ''}結果（{len(files)} 檔）：")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    if fails:
        print(f"\n❌ {len(fails)}：")
        for f, n in fails[:10]:
            print(f"   {f}: {n}")
        sys.exit(1)


if __name__ == "__main__":
    main()
