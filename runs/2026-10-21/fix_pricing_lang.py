import re, pathlib, sys

D = pathlib.Path("/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist")
log = []

def apply(rel, pairs, regex=False):
    p = D / rel
    t = p.read_text(encoding="utf-8")
    before = len(re.findall("cheaper", t, re.I))
    hits = 0
    for old, new in pairs:
        if regex:
            t, n = re.subn(old, new, t)
        else:
            n = t.count(old)
            t = t.replace(old, new)
        if n == 0:
            print(f"   !! MISS  {rel}: {old[:70]}")
        hits += n
    p.write_text(t, encoding="utf-8")
    after = len(re.findall("cheaper", t, re.I))
    log.append((rel, before, after, hits))
    print(f"   {rel}: cheaper {before} -> {after}  (replacements {hits})")

# ---------- ZH: items 6, 7, 10 ----------
print("== ZH pricing sentences")
apply("blog/south-africa-fuel-price-hike-september-2026-cape-town-living-costs.html", [
 ("開普敦租金收益率 7.5-11.4%，市中心兩房租金 R15,000（約 TWD 27,000），與台北相當但房價更低。",
  "開普敦租金收益率 7.5-11.4%，市中心兩房租金 R15,000（約 TWD 27,000）；同樣的租金水準，在開普敦對應的是含車位、近學區的兩房。同樣的預算，在 Northern Suburbs 可以買到含泳池與花園的獨棟別墅，土地持分完整——這是全球主要英語城市裡少見的價格帶。"),
 ("南非幣維持 16.1 弱勢區間，台幣計價成本低。南非幣弱勢使南非資產對台灣投資人相對便宜。",
  "南非幣維持 16.1 弱勢區間。南非幣弱勢使同樣的台幣預算，在開普敦能對應到更大的坪數與更好的區位。"),
 ("而是『開普敦生活成本在國際比較中還是不是相對便宜』——答案依然是肯定的。",
  "而是『開普敦的生活品質，對應到什麼樣的預算』——答案仍然很有競爭力。"),
])
apply("blog/south-africa-high-interest-rate-advantage-cape-town-property.html", [
 ("<li>**進場成本更低**：同樣的 R 16,000,000，現在比歷史均值時期便宜約 16%</li>",
  "<li><strong>同樣的 R 16,000,000，現在對應到的資產規格高於歷史均值時期約 16%</strong>：匯率折扣反映在可取得的坪數與區位上</li>"),
 ("<li>**退出收益更高**：未來南非幣回升時，匯兌收益將疊加在投資回報之上</li>",
  "<li><strong>退出時的匯兌空間</strong>：未來南非幣回升時，匯兌收益將疊加在投資回報之上</li>"),
 ("<li>**雙重保護**：高利率收益 + 匯率回升潛力</li>",
  "<li><strong>兩層支撐</strong>：高利率收益 + 匯率回升潛力</li>"),
])

# ---------- EN group 16: template block in 7 files ----------
print("== EN group 16 (7 files)")
G16 = [
 "financial-freedom-cape-town-passive-income-2026-en",
 "jingzhiqiong-passive-income-cape-town-2026-en",
 "minimum-wage-cape-town-property-passive-income-2026-en",
 "south-africa-fixed-deposit-vs-cape-town-property-yield-2026-en",
 "south-africa-foreign-buyer-mortgage-guide-2026-en",
 "south-africa-inflation-cools-4-3-percent-cape-town-property-2026-en",
 "taiwan-stock-market-record-high-cape-town-passive-income-2026-en",
]
NEW_STRONG = "the same TWD capital converts into more rand at today's rate — and the same budget maps to a higher tier of {}"
for s in G16:
    rel = f"blog/{s}.html"
    t = (D/rel).read_text(encoding="utf-8")
    pairs = []
    for old, obj in [
        ('<strong>the same TWD capital can buy more rands and thus "cheaper" Cape Town property</strong>', "Cape Town property"),
        ('<strong>the same TWD capital can be exchanged for more Rand, buying "cheaper" Cape Town property</strong>', "Cape Town property"),
        ('<strong>the same TWD capital can buy more rands and purchase "cheaper" Cape Town property</strong>', "Cape Town property"),
        ('<strong>the same TWD capital can be exchanged for more rands, buying "cheaper" South African deposits and Cape Town property</strong>', "South African deposits and Cape Town property"),
        ('The same TWD capital buys more rand and relatively "cheaper" Cape Town property.', NEW_STRONG.format("Cape Town property").capitalize() + "."),
    ]:
        if old in t:
            pairs.append((old, f"<strong>{NEW_STRONG.format(obj)}</strong>" if old.startswith("<strong>") else NEW_STRONG.format(obj).capitalize() + "."))
    # bullets
    pairs += [
        ("<li><strong>Relatively strong TWD</strong> — enhanced overseas purchasing power</li>",
         "<li><strong>A stronger TWD</strong> — buys more rand at today's rate</li>"),
        ("<li><strong>Relatively strong TWD</strong> — higher overseas purchasing power</li>",
         "<li><strong>A stronger TWD</strong> — buys more rand at today's rate</li>"),
        ("<li><strong>Relatively strong TWD</strong> — increased overseas purchasing power</li>",
         "<li><strong>A stronger TWD</strong> — buys more rand at today's rate</li>"),
        ("<li><strong>TWD relatively strong</strong> — higher overseas purchasing power</li>",
         "<li><strong>A stronger TWD</strong> — buys more rand at today's rate</li>"),
        ("<li><strong>Relatively weak ZAR</strong> — Cape Town property relatively cheaper</li>",
         "<li><strong>The same budget</strong> — maps to a higher tier of Cape Town property</li>"),
        ("<li><strong>Rand relatively weak</strong> — Cape Town property relatively cheaper</li>",
         "<li><strong>The same budget</strong> — maps to a higher tier of Cape Town property</li>"),
        ("<li><strong>Relatively weak ZAR</strong> — Cape Town property is relatively cheaper</li>",
         "<li><strong>The same budget</strong> — maps to a higher tier of Cape Town property</li>"),
        ("<li><strong>Relatively weak ZAR</strong> — South African deposits and property are relatively cheaper</li>",
         "<li><strong>The same budget</strong> — maps to a higher tier of South African deposits and Cape Town property</li>"),
        ("<li><strong>Relatively weak rand</strong> — Cape Town property is relatively cheaper, lowering entry cost</li>",
         "<li><strong>The same budget</strong> — maps to a higher tier of Cape Town property</li>"),
        ("<li><strong>Dual exchange-rate advantage</strong> — amplifies actual investment returns</li>",
         "<li><strong>Timing, not quality</strong> — the gap is a timing variable, not a quality signal</li>"),
        ("<li><strong>Dual currency advantage</strong> — amplifies actual investment returns</li>",
         "<li><strong>Timing, not quality</strong> — the gap is a timing variable, not a quality signal</li>"),
    ]
    apply(rel, pairs)

print("\n== summary")
for rel, b, a, h in log:
    print(f"  {b:3d} -> {a:3d}  {rel}")
sys.exit(0 if all(a == 0 for _, _, a, _ in log) else 1)
