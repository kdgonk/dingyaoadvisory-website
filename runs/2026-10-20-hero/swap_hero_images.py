#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""4 頁服務頁 hero + section-bg 換成正式配圖（木星人 15 檔 R2 素材）

來源：/mnt/DingYao/app-data/agent-notes/TO-jovian/2026-10-20-服務頁配圖-完整URL.md
基址：https://assets.dingyaoadvisory.tw/blog/images/

每頁 6 個 <picture>，全部指向 redesign/section-hero.webp（佔位）：
  [1] hero（loading=eager）      → sa-{pillar}-hero.avif + -16x9.webp（1920×1080）
  [2]-[6] section-bg（lazy）     → sa-{pillar}-s1..s4.webp（1792×1024，不足則循環）

og:image / twitter:image → sa-{pillar}-hero-16x9.webp（1600×900）

★ 必須加 width/height（土星人驗收：CLS 尺寸屬性存在）
★ CDN 根目錄必 404 是正常（圖在 blog/images/ 前綴下）
"""
import pathlib
import re
import sys

BASE = "https://assets.dingyaoadvisory.tw/blog/images/"
OLD = "https://assets.dingyaoadvisory.tw/redesign/section-hero.webp"

PAGES = {
    "south-africa-bank-account.html":     ("sa-bank-account", 3),
    "south-africa-bank-account-en.html":  ("sa-bank-account", 3),
    "south-africa-property.html":         ("sa-property", 4),
    "south-africa-property-en.html":      ("sa-property", 4),
}

HERO_W, HERO_H = 1920, 1080
SEC_W, SEC_H = 1792, 1024


def build_hero(pillar, inner):
    """inner = 原 <img> 的屬性（保留 alt/title/loading）"""
    alt = re.search(r'alt="([^"]*)"', inner)
    title = re.search(r'title="([^"]*)"', inner)
    alt_s = alt.group(1) if alt else ""
    title_s = title.group(1) if title else alt_s
    return (
        '<picture>\n'
        f'        <source srcset="{BASE}{pillar}-hero.avif" type="image/avif">\n'
        f'        <img src="{BASE}{pillar}-hero-16x9.webp"\n'
        f'             width="{HERO_W}" height="{HERO_H}"\n'
        f'             alt="{alt_s}" title="{title_s}"\n'
        '             loading="eager" fetchpriority="high" decoding="async">\n'
        '      </picture>'
    )


def build_section(pillar, idx, inner):
    alt = re.search(r'alt="([^"]*)"', inner)
    title = re.search(r'title="([^"]*)"', inner)
    alt_s = alt.group(1) if alt else ""
    title_s = title.group(1) if title else alt_s
    n = (idx % (PAGES_N[pillar] if False else 1)) + 1  # placeholder, replaced below
    return ""


def process(path, pillar, n_sections, dry=False):
    c = pathlib.Path(path).read_text(encoding="utf-8")
    orig = c
    stats = {"hero": 0, "section": 0, "og": 0}

    pics = list(re.finditer(r'<picture[^>]*>.*?</picture>', c, re.S))
    if len(pics) != 6:
        return None, f"預期 6 個 picture，實際 {len(pics)}"

    # 由後往前替換，避免位移
    for i in range(len(pics) - 1, -1, -1):
        m = pics[i]
        inner = m.group(0)
        img_m = re.search(r'<img([^>]*)>', inner)
        img_attrs = img_m.group(1) if img_m else ""
        alt = re.search(r'alt="([^"]*)"', img_attrs)
        title = re.search(r'title="([^"]*)"', img_attrs)
        alt_s = alt.group(1) if alt else ""
        title_s = title.group(1) if title else alt_s

        if i == 0:
            new = (
                '<picture>\n'
                f'        <source srcset="{BASE}{pillar}-hero.avif" type="image/avif">\n'
                f'        <img src="{BASE}{pillar}-hero-16x9.webp"\n'
                f'             width="{HERO_W}" height="{HERO_H}"\n'
                f'             alt="{alt_s}" title="{title_s}"\n'
                '             loading="eager" fetchpriority="high" decoding="async">\n'
                '      </picture>'
            )
            stats["hero"] += 1
        else:
            # section-bg：s1..sN 循環
            n = ((i - 1) % n_sections) + 1
            new = (
                '<picture>'
                f'<source srcset="{BASE}{pillar}-s{n}.webp" type="image/webp">'
                f'<img src="{BASE}{pillar}-s{n}.webp" width="{SEC_W}" height="{SEC_H}"'
                f' alt="{alt_s}" title="{title_s}" loading="lazy" decoding="async">'
                '</picture>'
            )
            stats["section"] += 1
        c = c[:m.start()] + new + c[m.end():]

    # og:image / twitter:image
    new_og = f"{BASE}{pillar}-hero-16x9.webp"
    for attr in ['property="og:image"', 'name="twitter:image"']:
        pat = re.compile(r'(<meta\s+' + re.escape(attr) + r'\s+content=")[^"]*(")')
        c, n = pat.subn(lambda m: m.group(1) + new_og + m.group(2), c)
        stats["og"] += n

    # CSS 內的 background-image（hero 圖層 fallback），用 16:9 WebP
    pat_css = re.compile(r"(background-image:\s*url\(')" + re.escape(OLD) + r"('\))")
    c, n_css = pat_css.subn(lambda m: m.group(1) + new_og + m.group(2), c)
    stats["css"] = n_css
    # 其他殘留（單引號/雙引號變體）
    c = c.replace("'" + OLD + "'", "'" + new_og + "'")
    c = c.replace('"' + OLD + '"', '"' + new_og + '"')
    # og:image:width/height/type（若存在則同步）
    c = re.sub(r'(<meta\s+property="og:image:width"\s+content=")[^"]*(")',
               r'\g<1>1600\g<2>', c)
    c = re.sub(r'(<meta\s+property="og:image:height"\s+content=")[^"]*(")',
               r'\g<1>900\g<2>', c)

    if not dry and c != orig:
        pathlib.Path(path).write_text(c, encoding="utf-8")
    return {"changed": c != orig, "stats": stats, "remain_old": c.count(OLD)}, None


PAGES_N = {"sa-bank-account": 3, "sa-property": 4}

if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for f, (pillar, n) in PAGES.items():
        r, err = process(f, pillar, n, dry)
        if err:
            print(f"  ❌ {f}: {err}")
        else:
            print(f"  {'[DRY] ' if dry else ''}OK {f}  hero={r['stats']['hero']} "
                  f"section={r['stats']['section']} og={r['stats']['og']} "
                  f"殘留={r['remain_old']}  changed={r['changed']}")
