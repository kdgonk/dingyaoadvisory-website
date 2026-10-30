#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9 篇 blog 加 1 條文內錨文字連回 /overseas-buyers.html（土星人 2026-10-30 派工）

規則
  1. 只處理清單內 9 檔（title／h1 含「海外置產」那 9 篇）
  2. 已含 /overseas-buyers.html 連結者跳過
  3. 插在「第一個內容 h2」（排除 sr-only）之後的第一個 <p> 內、句尾
     —— 若該 <p> 不足 80 字或以「：」結尾（清單引導句），改用下一個 h2
  4. 9 個錨文字互不相同，皆含「海外置產」
  5. 不動 nav／footer／CSS／版型

用法
  python3 scripts/add_overseas_hub_links_2026_10_30.py --dry
  python3 scripts/add_overseas_hub_links_2026_10_30.py --apply
"""
import argparse
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(REPO, 'dist', 'blog')
HUB = '/overseas-buyers.html'

# (檔名, 錨文字, 插入句)
PLAN = [
    ('cape-town-foreshore-rockefeller-overseas-investment.html',
     '海外置產完整流程',
     '若你正在評估這類服務式公寓，先看一遍<a href="%s">海外置產完整流程</a>，從選屋、議價到交屋與匯款的步驟都整理在裡面。'),
    ('cape-town-rental-occupancy-2026.html',
     '海外置產前該知道的事',
     '出租率只是其中一環，<a href="%s">海外置產前該知道的事</a>把持有成本、稅費與匯出流程一併列清楚。'),
    ('cape-town-tech-semigration-2026.html',
     '海外置產怎麼開始',
     '科技業租客帶來的穩定現金流，正是<a href="%s">海外置產怎麼開始</a>時最常被問到的一題，我們把判斷步驟整理成一頁。'),
    ('cape-town-uppers-luxury-property-investment-2026.html',
     '海外置產的持有成本',
     '成交價之外，<a href="%s">海外置產的持有成本</a>（市政稅、管理費、匯款手續）才是決定淨報酬的關鍵。'),
    ('cape-town-waterfront-infrastructure-sea-point-investment.html',
     '海外置產標的怎麼挑',
     '同樣的公共建設題材，<a href="%s">海外置產標的怎麼挑</a>提供了更完整的判斷順序：區位、租金供給、退場流動性。'),
    ('overseas-property-investment-guide-cape-town-2026.html',
     '海外置產完整指南',
     '這篇談的是報酬率；若你要看的是整個流程與文件，<a href="%s">海外置產完整指南</a>把選屋、資金、稅務放在同一頁。'),
    ('south-africa-remote-work-visa-cape-town-property-demand-2026.html',
     '海外置產的簽證與居留配套',
     '簽證只是起點，<a href="%s">海外置產的簽證與居留配套</a>整理了居留路徑與置產順序該怎麼排。'),
    ('taiwan-landlord-vs-cape-town-passive-income-2026.html',
     '海外置產 vs 台灣收租',
     '把兩邊的稅費與空置率放在一起看，<a href="%s">海外置產 vs 台灣收租</a>的差異才會清楚。'),
    ('taiwan-wealthy-overseas-allocation.html',
     '海外置產的配置順序',
     '順序比標的更重要，<a href="%s">海外置產的配置順序</a>把五種工具的先後與比例整理成一頁。'),
]


def content_h2s(html):
    return [m for m in re.finditer(r'<h2([^>]*)>', html) if 'sr-only' not in m.group(1)]


def pick_paragraph(html):
    """回傳可插入的 <p> 的 (start, end)；找不到回 None。"""
    hs = content_h2s(html)
    for h in hs[:3]:
        end = html.find('</h2>', h.start())
        if end < 0:
            continue
        seg_start = end + 5
        # 只看這個 h2 到下一個 h2 之間
        nxt = html.find('<h2', seg_start)
        seg = html[seg_start:nxt if nxt > 0 else seg_start + 4000]
        pm = re.search(r'<p[^>]*>(.*?)</p>', seg, re.S)
        if not pm:
            continue
        inner = re.sub(r'<[^>]+>', '', pm.group(1)).strip()
        if len(inner) < 80 or inner.endswith('：') or inner.endswith(':'):
            continue
        s = seg_start + pm.start(1)
        e = seg_start + pm.end(1)
        return s, e
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    mode = 'apply' if a.apply else 'dry'
    for fn, anchor, sent in PLAN:
        p = os.path.join(BLOG, fn)
        html = open(p, encoding='utf-8').read()
        if not os.path.exists(p):
            print(f'  ❌ MISSING {fn}')
            continue
        if HUB in html:
            print(f'  ⏭  SKIP  {fn}（已有 {HUB} 連結）')
            continue
        pos = pick_paragraph(html)
        if not pos:
            print(f'  ❌ NO-PARAGRAPH {fn}')
            continue
        s, e = pos
        add = sent % HUB
        new = html[:e] + add + html[e:]
        assert new.count(HUB) == html.count(HUB) + 1
        if mode == 'apply':
            open(p, 'w', encoding='utf-8').write(new)
        print(f'  ✅ {mode:5s} {fn}\n       錨文字：{anchor}\n       插入位置：offset {e}')

if __name__ == '__main__':
    main()
