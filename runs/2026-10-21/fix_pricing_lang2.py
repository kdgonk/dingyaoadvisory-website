import re, pathlib, sys

D = pathlib.Path("/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website/dist")
FILES = [
 "blog/fed-fomc-september-2026-rate-hike-cape-town-property-playbook-en.html",
 "blog/fed-september-2026-rate-decision-cape-town-property-strategy-en.html",
 "blog/foreign-buyer-r48m-constantia-sight-unseen-remote-purchase-2026-en.html",
 "blog/rand-below-16-cape-town-property-opportunity-2026-en.html",
 "blog/south-africa-fuel-price-hike-september-2026-cape-town-living-costs-en.html",
 "blog/us-cpi-august-2026-fed-hike-rand-cape-town-property-en.html",
 "blog-en.html",
]

# ordered: longest / most specific first
RULES = [
 # titles & headings (Title Case)
 ("Cheaper in TWD Terms", "TWD Entry Price Improves"),
 ("Cheaper in TWD", "TWD Entry Price Improves"),
 ("Why Cape Town Property Gets Cheaper", "Why the TWD Entry Price Improves"),
 ("Cape Town Property Gets Cheaper", "Cape Town Property: TWD Entry Price Improves"),
 ("Get Cheaper", "Improve the TWD Entry Price"),
 ("How Much Cheaper Is Cape Town's International Education When You Buy Property?",
  "What Does the Same Budget Buy in Cape Town's International Education?"),
 # sentence level
 ("making South African assets cheaper in TWD terms", "improving the TWD entry price for South African assets"),
 ("making South African assets cheaper in TWD", "improving the TWD entry price for South African assets"),
 ("making Cape Town property cheaper in TWD terms", "improving the TWD entry price for Cape Town property"),
 ("making Cape Town property cheaper in TWD", "improving the TWD entry price for Cape Town property"),
 ("Cape Town property effectively gets cheaper in Taiwan-dollar terms",
  "the TWD entry price for Cape Town property improves"),
 ("Cape Town property actually gets cheaper for foreign buyers in their home-currency terms",
  "the TWD entry price for Cape Town property improves for foreign buyers"),
 ("Cape Town property actually gets cheaper", "the TWD entry price for Cape Town property improves"),
 ("the same property is roughly 6% cheaper in dollar terms",
  "the same property's dollar price is roughly 6% lower"),
 ("a weaker rand means cheaper exchange rates and a lower effective cost for a Cape Town property",
  "a weaker rand means a better exchange rate and a lower TWD entry price for a Cape Town property"),
 ("gets cheaper for foreign buyers", "the TWD entry price improves for foreign buyers"),
 ("gets cheaper in Taiwan dollars", "the TWD entry price improves"),
 ("gets cheaper in TWD terms", "the TWD entry price improves"),
 ("gets cheaper in TWD", "the TWD entry price improves"),
 ("gets cheaper", "the TWD entry price improves"),
 ("becomes cheaper in TWD terms", "the TWD entry price improves"),
 ("become cheaper in TWD terms", "the TWD entry price improves"),
 ("becomes cheaper in TWD", "the TWD entry price improves"),
 ("become cheaper in TWD", "the TWD entry price improves"),
 ("South African assets cheaper in TWD terms", "a better TWD entry price for South African assets"),
 ("South African assets cheaper in TWD", "a better TWD entry price for South African assets"),
 ("South African assets get cheaper in TWD Terms", "the TWD entry price for South African assets improves"),
 ("Cape Town property cheaper in TWD terms", "Cape Town property: the TWD entry price improves"),
 ("Cape Town property cheaper in TWD", "Cape Town property: the TWD entry price improves"),
 ("is cheaper in TWD, Western Cape prices", "has a better TWD entry price, Western Cape prices"),
 ("cheaper in TWD terms", "the TWD entry price improves"),
 ("cheaper in TWD", "the TWD entry price improves"),
 # misc
 ("Cheaper in TWD, window to enter in tranches", "TWD entry price improves — window to enter in tranches"),
 ("cheaper financing", "lower borrowing costs"),
 ('"stronger rand = cheaper"', '"stronger rand = lower TWD entry price"'),
 ("cheaper than Taipei's TWD 1,350", "below Taipei's TWD 1,350"),
 ("cheaper-yielding assets abroad", "higher-yielding assets abroad"),
 ('"the property got cheaper"', '"the property\'s TWD entry price improved"'),
]

for rel in FILES:
    p = D / rel
    t = p.read_text(encoding="utf-8")
    before = len(re.findall("cheaper", t, re.I))
    n_total = 0
    for old, new in RULES:
        n = t.count(old)
        if n:
            t = t.replace(old, new); n_total += n
    p.write_text(t, encoding="utf-8")
    after = len(re.findall("cheaper", t, re.I))
    print(f"{before:3d} -> {after:3d}   replacements {n_total:3d}   {rel}")
    if after:
        for m in re.finditer("cheaper", t, re.I):
            print("     LEFT:", re.sub(r"\s+", " ", t[max(0, m.start()-120):m.end()+90]))
