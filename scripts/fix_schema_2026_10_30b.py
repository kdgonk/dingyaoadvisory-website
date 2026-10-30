#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三站 schema 修正 v2（土星人 2026-10-30 追加指示，覆蓋 v1 第 1 項）

1. dingyao 鼎曜節點 address 改用公司登記地址：
   streetAddress 新庄里中沙路新庄仔巷11號1樓 / locality 龍井區 / region 台中市
   / postalCode 434 / country TW（不再出現西屯區）
2. 三站 Scott Huang Person 補 alternateName ["黃慶興", "Huang Ching-Hsing"]，保留 jobTitle
3. crestline / canvascrest 的鼎曜節點（原本沒有 founder）補 founder Person（同一 @id，
   不另建第二個 Person）

用法: python3 scripts/fix_schema_2026_10_30b.py --dry|--apply
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIB = os.path.dirname(BASE)
ROOTS = [
    ("dingyao", os.path.join(BASE, "dist")),
    ("crestline", os.path.join(SIB, "crestline-advisory-site")),
    ("canvascrest", os.path.join(SIB, "canvascrest-site")),
]

DYAO_ID = "https://dingyaoadvisory.tw/#organization"
SCOTT_ID = "https://dingyaoadvisory.tw/scott#person"
REG_ADDRESS = {
    "@type": "PostalAddress",
    "streetAddress": "新庄里中沙路新庄仔巷11號1樓",
    "addressLocality": "龍井區",
    "addressRegion": "台中市",
    "postalCode": "434",
    "addressCountry": "TW",
}
ALT = ["黃慶興", "Huang Ching-Hsing"]
FOUNDER = {
    "@type": "Person",
    "@id": SCOTT_ID,
    "name": "Scott Huang",
    "alternateName": ALT,
    "jobTitle": "創辦人 / 首席顧問",
    "url": "https://dingyaoadvisory.tw/scott",
    "worksFor": {"@id": DYAO_ID},
}

BLOCK_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def walk_dicts(o, acc):
    if isinstance(o, dict):
        acc.append(o)
        for v in o.values():
            walk_dicts(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk_dicts(v, acc)
    return acc


def process_block_body(body, acc, site):
    data = json.loads(body)
    nodes = walk_dicts(data, [])
    n_addr = n_alt = n_founder = 0

    for n in nodes:
        # (2) Scott Huang Person：補 alternateName（各種寫法都收斂到同一口徑）
        if n.get("name") == "Scott Huang" and (n.get("@type") == "Person" or
                                              (isinstance(n.get("@type"), list) and "Person" in n["@type"])):
            if n.get("alternateName") != ALT:
                n["alternateName"] = ALT
                n_alt += 1

        # 只處理完整的鼎曜節點（有 foundingDate，不是 {"@id": …} 參照）
        if n.get("@id") != DYAO_ID or "foundingDate" not in n or len(n) <= 1:
            continue

        # (1) 登記地址：只改「本來就有 address」的節點（沒有 address 的不新增，避免全站灌位址）
        if "address" in n and n.get("address") != REG_ADDRESS:
            n["address"] = dict(REG_ADDRESS)
            n_addr += 1

        # (3) crestline / canvascrest 的「主」鼎曜節點（有 description、原本沒有 founder）補 founder
        if site != "dingyao" and "founder" not in n and "description" in n:
            n["founder"] = json.loads(json.dumps(FOUNDER, ensure_ascii=False))
            n_founder += 1

    if not (n_addr or n_alt or n_founder):
        return None
    acc["address_registered"] += n_addr
    acc["person_alternateName"] += n_alt
    acc["founder_added"] += n_founder

    dump = json.dumps(data, indent=2, ensure_ascii=False)
    lead = body[:len(body) - len(body.lstrip())]
    trail = body[len(body.rstrip()):]
    return lead + dump + trail


def process_file(path, acc, site, apply_changes):
    src = open(path, encoding="utf-8").read()
    out, last, changed = [], 0, False
    for m in BLOCK_RE.finditer(src):
        new = process_block_body(m.group(2), acc, site)
        if new is None:
            continue
        out.append(src[last:m.start()])
        out.append(m.group(1) + new + m.group(3))
        last = m.end()
        changed = True
    if not changed:
        return False
    out.append(src[last:])
    if apply_changes:
        open(path, "w", encoding="utf-8").write("".join(out))
    return True


def main():
    apply_changes = "--apply" in sys.argv
    acc = {k: 0 for k in ("address_registered", "person_alternateName", "founder_added")}
    changed = []
    for name, root in ROOTS:
        for dp, _dn, fn in os.walk(root):
            rel = os.path.relpath(dp, root)
            parts = [] if rel == "." else rel.split(os.sep)
            if any(p.startswith((".", "_")) for p in parts):
                continue
            for f in sorted(fn):
                if not f.endswith(".html"):
                    continue
                if process_file(os.path.join(dp, f), acc, name, apply_changes):
                    changed.append(os.path.relpath(os.path.join(dp, f), SIB))
    print(("APPLY" if apply_changes else "DRY"), json.dumps(acc, ensure_ascii=False))
    print("changed files:", len(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
