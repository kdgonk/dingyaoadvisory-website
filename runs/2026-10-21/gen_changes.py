import re, subprocess, difflib, pathlib

REPO = pathlib.Path("/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website")
files = [f for f in subprocess.run(["git","diff","--name-only"], cwd=REPO, capture_output=True, text=True).stdout.split()
         if f.startswith("dist/")]

def text_of(html):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    h = re.sub(r"(?s)<head>.*?</head>", " ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&quot;", '"'), ("&#39;", "'")):
        h = h.replace(a, b)
    return re.sub(r"\s+", " ", h).strip()

def sents(t):
    return [p.strip() for p in re.split(r"(?<=[。！？!?])\s*|(?<=\.)\s+(?=[A-Z“\"])", t) if p.strip()]

def focus(a, b, pad=70):
    """Return only the differing window of two long strings."""
    if len(a) < 160 and len(b) < 160:
        return a, b
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    if not ops:
        return a[:160], b[:160]
    i1 = max(0, min(o[1] for o in ops) - pad); i2 = min(len(a), max(o[2] for o in ops) + pad)
    j1 = max(0, min(o[3] for o in ops) - pad); j2 = min(len(b), max(o[4] for o in ops) + pad)
    return ("…" + a[i1:i2] + "…"), ("…" + b[j1:j2] + "…")

rows = []
for f in files:
    old = subprocess.run(["git","show","HEAD:"+f], cwd=REPO, capture_output=True, text=True).stdout
    new = (REPO/f).read_text(encoding="utf-8")
    so, sn = sents(text_of(old)), sents(text_of(new))
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, so, sn, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        o = " ".join(so[i1:i2]).strip(); n = " ".join(sn[j1:j2]).strip()
        if "Main navigation" in o + n or "DYA DingYao Advisory APAC HUB" in o + n:
            continue
        if not o and not n:
            continue
        o2, n2 = focus(o, n)
        rows.append((f, o2, n2))

lines = []
cur = None
for f, o, n in rows:
    if f != cur:
        lines.append(f"\n#### `{f}`\n")
        cur = f
    if not o:
        lines.append(f"- 新增：{n}")
    elif not n:
        lines.append(f"- 刪除：{o}")
    else:
        lines.append(f"- 原句：{o}\n  - 新句：{n}")
out = "\n".join(lines)
(REPO/"runs/2026-10-21/pricing-lang-changes.md").write_text(out, encoding="utf-8")
print(f"{len(rows)} rows, {len(out)} chars")
