#!/usr/bin/env python3
"""P0: Remove duplicate/non-canonical project-phase1 entries from sitemap.xml.
Keep primary self-canonical pages (project-phase1, project-phase1-en).
Remove: project-phase1-new, project-phase1-new-en, project-phase1-old (dupes/legacy).
Dry-run unless --apply.
"""
import re, sys

SITEMAP = "dist/sitemap.xml"
KEEP = ["/project-phase1", "/project-phase1-en"]  # primary self-canonical
REMOVE_SUBSTR = ["project-phase1-new", "project-phase1-old"]  # legacy/dup slugs

def main():
    apply = "--apply" in sys.argv
    xml = open(SITEMAP, encoding="utf-8").read()
    # split into <url>...</url> blocks
    blocks = re.findall(r"<url>.*?</url>", xml, re.S)
    print(f"Total url blocks: {len(blocks)}")
    removed = []
    kept_phase1 = []
    for b in blocks:
        loc = re.search(r"<loc>([^<]*)</loc>", b).group(1)
        if "project-phase1" in loc:
            if any(s in loc for s in REMOVE_SUBSTR) or loc.rstrip("/") not in ["https://dingyaoadvisory.tw/project-phase1", "https://dingyaoadvisory.tw/project-phase1-en"]:
                removed.append(loc)
            else:
                kept_phase1.append(loc)
    print("To REMOVE:", removed)
    print("To KEEP  :", kept_phase1)
    if apply:
        for b in blocks:
            loc = re.search(r"<loc>([^<]*)</loc>", b).group(1)
            if "project-phase1" in loc:
                if any(s in loc for s in REMOVE_SUBSTR) or loc.rstrip("/") not in ["https://dingyaoadvisory.tw/project-phase1", "https://dingyaoadvisory.tw/project-phase1-en"]:
                    xml = xml.replace(b, "", 1)
        open(SITEMAP, "w", encoding="utf-8").write(xml)
        # verify
        v = re.findall(r"<loc>([^<]*project-phase1[^<]*)</loc>", open(SITEMAP).read())
        print("After apply, project-phase1 locs:", v)

if __name__ == "__main__":
    main()
