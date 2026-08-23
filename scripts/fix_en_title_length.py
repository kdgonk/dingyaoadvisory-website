#!/usr/bin/env python3
"""P0: Truncate EN article <title> to <=65 chars (SEO guard).
Strategy: drop brand suffix if over; truncate headline at word boundary.
Dry-run (no write) unless --apply.
"""
import glob, re, sys, os

BRAND = "DingYao Advisory"
MAX = 65
MAX_CONTENT = 60  # leaves room for brand

def truncate_title(raw):
    """Return best-effort title <= MAX chars."""
    raw = raw.strip()
    # 1. split off brand suffix if present
    content = raw
    brand = ""
    for b in (BRAND, "DingYao"):
        if content.endswith("| " + b):
            content = content[: -len("| " + b)].rstrip()
            brand = b
            break
    content = content.strip()

    # 2. if full (content + brand) fits, keep brand
    full = content + " | " + brand if brand else content
    if len(full) <= MAX:
        return full

    # 3. truncate content to MAX_CONTENT at word boundary
    if len(content) > MAX_CONTENT:
        cut = content[:MAX_CONTENT]
        # back off to last space
        sp = cut.rfind(" ")
        if sp > 30:
            cut = cut[:sp]
        cut = cut.rstrip(" ,;:-") + "…"
        content = cut

    # 4. re-attach brand if it fits
    full = content + " | " + brand if brand else content
    if len(full) <= MAX:
        return full
    return content  # bare content (should be <=60)


def main():
    apply = "--apply" in sys.argv
    files = sorted(glob.glob("dist/blog/*-en.html"))
    changed = 0
    over = 0
    for f in files:
        html = open(f, encoding="utf-8").read()
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        if not m:
            continue
        old = m.group(1).strip()
        if len(old) <= MAX:
            continue
        over += 1
        new = truncate_title(old)
        if new == old or len(new) > MAX:
            print(f"⚠️ SKIP {os.path.basename(f)}: cannot reduce {len(old)}->{len(new)}")
            print(f"   OLD: {old[:80]}")
            continue
        if apply:
            html = html[: m.start()] + "<title>" + new + "</title>" + html[m.end():]
            open(f, "w", encoding="utf-8").write(html)
        print(f"{'✓' if apply else '·'} {os.path.basename(f)}: {len(old)}→{len(new)}")
        print(f"   OLD: {old[:75]}")
        print(f"   NEW: {new[:75]}")
        changed += 1
    print(f"\nOver-limit titles: {over} | Fixed: {changed} | Mode: {'APPLY' if apply else 'DRY-RUN'}")

if __name__ == "__main__":
    main()
