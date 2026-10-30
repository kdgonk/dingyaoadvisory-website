#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三站 founder 歸屬更正（土星人 2026-10-30 v3，覆蓋 v2 的「三站都掛 Scott」）

事實（老闆 2026-10-30）：
  DingYao Advisory    → 黃慶興 = Scott Huang（既有，不動）
  Crestline Advisory  → 紀達成 Ta-Cheng Chi（對外亦用 Dragon Chi）
  CanvasCrest         → Ta-Cheng Chi ＋ Muzi Tembe 共同創立

做法：
  crestline   + Crestline Organization.founder = Ta-Cheng Chi（Person，Founder & Director）
              − 移除 Scott Huang Person（頁面無其內容；組織層合作關係已由 affiliation 表達）
              （canvascrest 的 Crestline 摘要節點不加 founder，避免與 crestline 站權威節點重複）
  canvascrest + RealEstateAgent.founder = [Ta-Cheng Chi, Muzi Tembe]（@id 參照既有 Person，不重複建）
              + Ta-Cheng Chi 補 alternateName ["紀達成","Dragon Chi"]
              − 移除 Scott Huang（DingYao 節點的 founder）
  dingyao     不動（Scott 為鼎曜創辦人，2026-10-30 v2 已正確）

用法: python3 scripts/fix_schema_2026_10_30c.py --dry|--apply
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIB = os.path.dirname(BASE)
CR_ROOT = os.path.join(SIB, "crestline-advisory-site")
CC_ROOT = os.path.join(SIB, "canvascrest-site")

DYAO_ID = "https://dingyaoadvisory.tw/#organization"
SCOTT_ID = "https://dingyaoadvisory.tw/scott#person"
CREST_ID = "https://crestlineadvisory.co.za/#organization"
CC_ID = "https://canvascrest.co.za/#organization"
CR_PERSON = "https://crestlineadvisory.co.za/#person-ta-cheng-chi"
CC_PERSON_TC = "https://canvascrest.co.za/#person-ta-cheng-chi"
CC_PERSON_MUZI = "https://canvascrest.co.za/#person-muzi-tembe"
ALT_TC = ["紀達成", "Dragon Chi"]

CREST_FOUNDER = {
    "@type": "Person",
    "@id": CR_PERSON,
    "name": "Ta-Cheng Chi",
    "alternateName": ALT_TC,
    "sameAs": ["https://www.linkedin.com/in/kdgonk/"],
    "jobTitle": "Founder & Director",
    "worksFor": {"@id": CREST_ID},
}
CC_FOUNDER_REFS = [{"@id": CC_PERSON_TC}, {"@id": CC_PERSON_MUZI}]

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


def strip_scott(o):
    """從 dict/list 中移除 Scott 的 Person 節點與 DingYao 節點上的 founder，回傳移除數。"""
    n = 0
    if isinstance(o, dict):
        for k in list(o.keys()):
            v = o[k]
            if isinstance(v, dict) and v.get("@id") == SCOTT_ID:
                del o[k]
                n += 1
            elif isinstance(v, list):
                keep = [x for x in v if not (isinstance(x, dict) and x.get("@id") == SCOTT_ID)]
                if len(keep) != len(v):
                    n += len(v) - len(keep)
                    o[k] = keep
        # DingYao 節點上的 founder（若指向 scott）
        if o.get("@id") == DYAO_ID and isinstance(o.get("founder"), dict) and o["founder"].get("@id") == SCOTT_ID:
            del o["founder"]
            n += 1
        for v in o.values():
            n += strip_scott(v)
    elif isinstance(o, list):
        for v in o:
            n += strip_scott(v)
    return n


def process_block(body, site, acc):
    data = json.loads(body)
    nodes = walk_dicts(data, [])
    changed = False

    n_scott = strip_scott(data)
    if n_scott:
        acc["scott_removed"] += n_scott
        changed = True

    for n in nodes:
        if (site == "crestline" and n.get("@id") == CREST_ID and len(n) > 1
                and ("foundingDate" in n or "description" in n)):
            if n.get("founder") != CREST_FOUNDER:
                n["founder"] = json.loads(json.dumps(CREST_FOUNDER, ensure_ascii=False))
                acc["crestline_founder_set"] += 1
                changed = True
        if site == "canvascrest":
            if n.get("@id") == CC_ID and n.get("@type") == "RealEstateAgent" and len(n) > 1:
                if n.get("founder") != CC_FOUNDER_REFS:
                    n["founder"] = json.loads(json.dumps(CC_FOUNDER_REFS, ensure_ascii=False))
                    acc["canvascrest_founder_set"] += 1
                    changed = True
            if n.get("@id") == CC_PERSON_TC and n.get("alternateName") != ALT_TC:
                n["alternateName"] = ALT_TC
                acc["ta_cheng_alt_set"] += 1
                changed = True

    if not changed:
        return None
    dump = json.dumps(data, indent=2, ensure_ascii=False)
    lead = body[:len(body) - len(body.lstrip())]
    trail = body[len(body.rstrip()):]
    return lead + dump + trail


def process_file(path, site, acc, apply_changes):
    src = open(path, encoding="utf-8").read()
    out, last, changed = [], 0, False
    for m in BLOCK_RE.finditer(src):
        new = process_block(m.group(2), site, acc)
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
    acc = {k: 0 for k in ("scott_removed", "crestline_founder_set",
                          "canvascrest_founder_set", "ta_cheng_alt_set")}
    n_files = 0
    for site, root in (("crestline", CR_ROOT), ("canvascrest", CC_ROOT)):
        for dp, _dn, fn in os.walk(root):
            rel = os.path.relpath(dp, root)
            parts = [] if rel == "." else rel.split(os.sep)
            if any(p.startswith((".", "_")) for p in parts):
                continue
            for f in sorted(fn):
                if not f.endswith(".html"):
                    continue
                if process_file(os.path.join(dp, f), site, acc, apply_changes):
                    n_files += 1
    print(("APPLY" if apply_changes else "DRY"), json.dumps(acc, ensure_ascii=False), "files:", n_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
