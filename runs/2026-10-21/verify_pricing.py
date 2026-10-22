import re, json, pathlib, subprocess
from html.parser import HTMLParser

REPO = pathlib.Path("/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website")
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr','path','circle','g','line','rect','polyline','use','stop'}

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.stack=[]; s.err=[]
    def handle_starttag(s,tag,a):
        if tag not in VOID: s.stack.append(tag)
    def handle_endtag(s,tag):
        if tag in VOID: return
        if s.stack and s.stack[-1]==tag: s.stack.pop()
        else: s.err.append(tag)

files = subprocess.run(["git","diff","--name-only"], cwd=REPO, capture_output=True, text=True).stdout.split()
files = [f for f in files if f.startswith("dist/")]
print(f"{len(files)} modified files\n")
bad = 0
for f in files:
    t = (REPO/f).read_text(encoding="utf-8")
    p = P(); p.feed(t)
    jsons = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    jerr = []
    for i, js in enumerate(jsons):
        try: json.loads(js)
        except Exception as e: jerr.append(f"[{i}]{e}")
    ch = len(re.findall("cheaper", t, re.I))
    forbidden = [x for x in ("定存","7.72","8.15","8.75","4.0-6.05","7.10-7.45","6.5%") if x in t]
    flag = ""
    if p.stack or p.err or jerr or forbidden:
        flag = "  <<< CHECK"; bad += 1
    print(f"  cheaper={ch:2d} tags={'OK' if not p.stack and not p.err else (p.stack[:2], p.err[:2])} "
          f"jsonld={len(jsons)}{jerr if jerr else ''} forb={forbidden}  {f}{flag}")
print("\nproblem files:", bad)

# education specific
for f in ("dist/education.html","dist/education-en.html"):
    t=(REPO/f).read_text(encoding="utf-8")
    print(f"\n{f}: 47%={t.count('47%')} 3.2×={t.count('3.2×')} 85%={t.count('85%')} "
          f"faq={len(re.findall(r'class=.faq-item',t))} Q_schema={t.count(chr(34)+'@type'+chr(34)+': '+chr(34)+'Question'+chr(34))} "
          f"cta_consult={len(re.findall(r'href=./consultation',t))} leadmagnet={t.count('data-leadmagnet')}")
