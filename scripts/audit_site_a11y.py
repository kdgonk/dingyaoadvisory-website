#!/usr/bin/env python3
"""全站 a11y 屬性缺口盤點（第二階段評估用）：section aria-labelledby / h2 id / img title / a title。

用法：python3 audit_site_a11y.py <root_dir>
輸出：總計 + 每頁明細（只印有缺口的頁）+ 缺口分布
"""
import re
import sys
from collections import Counter
from pathlib import Path

SEC = re.compile(r"<section\b[^>]*>")
H2 = re.compile(r"<h2\b[^>]*>")
IMG = re.compile(r"<img\b[^>]*>")
A = re.compile(r"<a\b[^>]*>")


def main(root):
    root = Path(root)
    files = sorted(root.rglob("*.html"))
    tot = Counter()
    per = []
    dist = Counter()
    for f in files:
        try:
            c = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "<html" not in c[:4000].lower():
            continue
        s = SEC.findall(c)
        h = H2.findall(c)
        i = IMG.findall(c)
        a = A.findall(c)
        m = {
            "section": sum("aria-labelledby" not in x and "aria-label=" not in x for x in s),
            "h2": sum("id=" not in x for x in h),
            "img": sum("title=" not in x for x in i),
            "a": sum("title=" not in x for x in a),
        }
        if any(m.values()):
            per.append((str(f.relative_to(root)), m, len(s), len(h), len(i), len(a)))
        for k, v in m.items():
            tot[k] += v
            if v:
                dist[k] += 1

    print(f"root={root}")
    print(f"HTML 檔數（含 <html）: {sum(1 for _ in per)} 有缺口 / 總計掃描 {len(files)}")
    print("\n=== 缺口總計 ===")
    for k in ("img", "a", "h2", "section"):
        print(f"  {k:<8} 缺 {tot[k]:>6}　（分布於 {dist[k]} 頁）")
    print("\n=== 前 15 個缺口最多的頁 ===")
    for path, m, ns, nh, ni, na in sorted(per, key=lambda x: -sum(x[1].values()))[:15]:
        print(f"  {sum(m.values()):>5}  {path}  "
              f"(sec {m['section']}/{ns} h2 {m['h2']}/{nh} img {m['img']}/{ni} a {m['a']}/{na})")
    return tot


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dist")
