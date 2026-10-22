#!/usr/bin/env python3
"""Strict Cape Town share: paragraph chars containing literal '開普敦' / 'Cape Town' only."""
import re, sys, pathlib

RUN = pathlib.Path(__file__).resolve().parent
SLUG = "south-africa-boarding-school-admission-timeline-2026"


def paras(c):
    body = c[c.index("<!-- ARTICLE BODY -->"):c.index("<!-- CTA -->")]
    body = re.sub(r"<table.*?</table>", lambda m: m.group(0), body, flags=re.S)
    out = []
    for m in re.finditer(r"<(p|li|td|h2|h3)(?:\s[^>]*)?>(.*?)</\1>", body, re.S):
        txt = re.sub(r"<[^>]+>", "", m.group(2))
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) > 40:
            out.append(txt)
    return out


def report(path, key):
    c = path.read_text(encoding="utf-8")
    ps = paras(c)
    total = sum(len(p) for p in ps)
    hit = sum(len(p) for p in ps if key in p)
    mentions = len(re.findall(re.escape(key), c))
    body_only = c[c.index("<!-- ARTICLE BODY -->"):c.index("<!-- CTA -->")]
    body_mentions = len(re.findall(re.escape(key), re.sub(r"<[^>]+>", " ", body_only)))
    return dict(path=str(path), paras=len(ps), chars=total, hit_chars=hit,
                pct=hit / total * 100 if total else 0,
                mentions=mentions, body_mentions=body_mentions)


if __name__ == "__main__":
    for f, k in ((SLUG + ".html", "開普敦"), (SLUG + "-en.html", "Cape Town")):
        r = report(RUN / f, k)
        print(f"{f}: pct={r['pct']:.1f}%  chars={r['chars']}  hit={r['hit_chars']}  "
              f"mentions(all)={r['mentions']}  body_mentions={r['body_mentions']}  paras={r['paras']}")
