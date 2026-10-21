#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署新文章 south-africa-boarding-school-admission-timeline-2026（含 -en）

土星人 2026-10-21 指派：
1. 兩檔上線（已由前置步驟複製到 dist，s4 404 圖位已移除）
2. blog 列表掛新卡片（最新在最前）
3. 反向內連：既有教育文 2 篇（中英各 2）
4. sitemap 更新

用法：python3 deploy_article.py [--dry]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path("dist")
SLUG = "south-africa-boarding-school-admission-timeline-2026"
DATE_ZH = "2026.10.21"
DATE_EN = "2026-10-21"

# ══════════════════════════════════════════
# 卡片
# ══════════════════════════════════════════
CARD_ZH = '''<article class="blog-card fade-in fade-in-delay-1">
        <img src="https://assets.dingyaoadvisory.tw/blog/images/south-africa-boarding-school-admission-timeline-2026-hero.webp" alt="南非寄宿學校怎麼申請？2026 入學時程、監護與簽證" class="blog-card-img" loading="lazy" title="南非寄宿學校怎麼申請？2026 入學時程、監護與簽證">
        <div class="blog-card-body">
          <span class="blog-tag">南非寄宿學校 / 南非私校申請 / 南非留學 / 開普敦國際學校</span>
          <h3>南非寄宿學校怎麼申請？2026 入學時程、監護與簽證</h3>
          <div class="blog-meta">
            <span><i class="far fa-calendar"></i> %s</span>
            <span><i class="far fa-clock"></i> 16 分鐘閱讀</span>
          </div>
          <p>南非寄宿學校的申請不是填表了事：Hilton College、Michaelhouse 這類傳統寄宿學校以 Grade 8 為主要入口、要提前約 18 個月排隊，還牽涉監護人指定、簽證與四個學期的對齊。本文拆解 2026 入學時程的每個節點、寄宿與陪讀的差別、費用結構，以及開普敦走讀國際學校為什麼是另一條路。</p>
          <a href="/blog/%s" class="blog-link" title="Read More">Read More <i class="fas fa-arrow-right"></i></a>
        </div>
      </article>

      ''' % (DATE_ZH, SLUG)

CARD_EN = '''<article class="blog-card fade-in fade-in-delay-1" data-category="education">
        <img src="https://assets.dingyaoadvisory.tw/blog/images/south-africa-boarding-school-admission-timeline-2026-hero.webp" alt="South Africa Boarding School 2026: Admission Timeline" class="blog-card-img" loading="lazy" title="South Africa Boarding School 2026: Admission Timeline">
        <div class="blog-card-body">
          <span class="blog-tag">south africa boarding school / south africa private school application / cape town international school</span>
          <h3>South Africa Boarding School 2026: Admission Timeline</h3>
          <div class="blog-meta">
            <span><i class="far fa-calendar"></i> %s</span>
            <span><i class="far fa-clock"></i> 18 min read</span>
          </div>
          <p>Applying to a South African boarding school is not a form-filling exercise: traditional boarding schools such as Hilton College and Michaelhouse take Grade 8 as the main entry point, require roughly 18 months of lead time, and involve guardian designation, visas and alignment with four school terms. This guide breaks down each 2026 milestone, boarding versus accompanied study, fee structures, and why Cape Town's day international schools are a different path.</p>
          <a href="/blog/%s-en" class="blog-link" title="Read More">Read More <i class="fas fa-arrow-right"></i></a>
        </div>
      </article>

      ''' % (DATE_EN, SLUG)

# ══════════════════════════════════════════
# 反向內連（既有教育文 2 篇 × 中英）
# ══════════════════════════════════════════
# (檔案, 錨點句子, 插入的句子)
BACKLINKS = [
    ("blog/cape-town-international-school-cost-property-investment-2026.html",
     "整個流程，<strong>台灣家庭無需親自飛往南非</strong>",
     None),  # 特殊處理：段落末尾追加
    ("blog/taiwan-parents-choosing-south-africa-private-schools.html",
     "建議提前 6–12 個月開始準備。",
     '若孩子考慮的是寄宿學校，時程與走讀國際學校完全不同——<a href="/blog/%s" title="南非寄宿學校申請時程與監護安排">南非寄宿學校申請時程與監護安排</a>把 18 個月的排隊節點、監護人指定與簽證對齊一次列清楚。' % SLUG),
    ("blog/cape-town-international-school-cost-property-investment-2026-en.html",
     "__PROCESS_END__",
     None),  # 特殊處理
    ("blog/taiwan-parents-choosing-south-africa-private-schools-en.html",
     "Start preparing 6–12 months in advance.",
     'If a boarding school is on the table, the timeline is nothing like a day international school — <a href="/blog/%s-en" title="South Africa Boarding School Admission Timeline">the South Africa boarding school admission timeline</a> lays out every milestone across the 18-month lead time, guardian designation and visa alignment in one place.' % SLUG),
]


def add_cards(dry):
    out = []
    for fname, card in [("blog.html", CARD_ZH), ("blog-en.html", CARD_EN)]:
        p = ROOT / fname
        c = p.read_text(encoding="utf-8")
        if SLUG in c:
            out.append(f"{fname}：已有卡片")
            continue
        # 找第一張卡片
        m = re.search(r'<article class="blog-card', c)
        if not m:
            out.append(f"{fname}：★找不到卡片錨點")
            continue
        c2 = c[:m.start()] + card + c[m.start():]
        if not dry:
            p.write_text(c2, encoding="utf-8")
        out.append(f"{fname}：已插入第一張卡片")
    return out


def add_backlinks(dry):
    out = []
    for fname, anchor, sentence in BACKLINKS:
        p = ROOT / fname
        if not p.exists():
            out.append(f"{fname}：★不存在")
            continue
        c = p.read_text(encoding="utf-8")
        if SLUG in c:
            out.append(f"{fname}：已有內連")
            continue

        if anchor == "__PROCESS_END__":
            # EN 版：H2 "What Is the Complete Process..." 區塊最後一個 <p>
            i = c.find("What Is the Complete Process from School Evaluation to Enrolment?")
            if i < 0:
                out.append(f"{fname}：★找不到 H2")
                continue
            j = c.find("</section>", i)
            seg = c[i:j]
            ps = list(re.finditer(r'<p>(.*?)</p>', seg, re.S))
            if not ps:
                out.append(f"{fname}：★H2 區塊無段落")
                continue
            last = ps[-1]
            # 在最後段落末尾（</p> 前）追加
            add = ' If a boarding school is under consideration, the lead time and milestones are entirely different — <a href="/blog/%s-en" title="South Africa Boarding School Admission Timeline">the boarding school admission timeline</a> breaks down the 18-month queue, guardian designation and visa alignment.' % SLUG
            newseg = seg[:last.end(1)] + add + seg[last.end(1):]
            c2 = c[:i] + newseg + c[j:]
            if not dry:
                p.write_text(c2, encoding="utf-8")
            out.append(f"{fname}：已加內連（H2 區塊末段）")
            continue

        if sentence is None:
            # ZH cape-town-intl：最後一段末尾追加
            i = c.find(anchor)
            if i < 0:
                out.append(f"{fname}：★找不到錨點")
                continue
            j = c.find("</p>", i)
            add = '若孩子考慮的是寄宿學校，時程與走讀國際學校完全不同——<a href="/blog/%s" title="南非寄宿學校申請時程與監護安排">南非寄宿學校申請時程與監護安排</a>把 18 個月的排隊節點、監護人指定與簽證對齊一次列清楚。' % SLUG
            c2 = c[:j] + add + c[j:]
            if not dry:
                p.write_text(c2, encoding="utf-8")
            out.append(f"{fname}：已加內連（末段）")
            continue

        # 一般：把句子插在錨點之後
        i = c.find(anchor)
        if i < 0:
            out.append(f"{fname}：★找不到錨點「{anchor[:30]}」")
            continue
        pos = i + len(anchor)
        c2 = c[:pos] + sentence + c[pos:]
        if not dry:
            p.write_text(c2, encoding="utf-8")
        out.append(f"{fname}：已加內連")
    return out


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    tag = "[DRY] " if dry else ""
    print(f"{tag}卡片")
    for x in add_cards(dry):
        print("   ", x)
    print(f"\n{tag}反向內連")
    for x in add_backlinks(dry):
        print("   ", x)
