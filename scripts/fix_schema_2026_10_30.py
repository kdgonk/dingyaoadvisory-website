#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三站 schema 修正（土星人 2026-10-30 派工）

1. dingyao 首頁 Organization address addressLocality/addressRegion 對調
   （台中市/西屯區、以及英文版 Taichung City/Xitun District 同型錯誤）
2. 三站鼎曜節點 foundingDate 2026-02-13 -> 2024，並在 description 末尾補
   「品牌自 2024 年起於台灣營運，2026 年 2 月完成公司設立登記（統一編號 60330590）。」
   無 description 的節點補上標準描述 + 該句（entity 描述一致）
3. Crestline 節點的 sameAs LinkedIn → 改用 Crestline 自己的公司頁
   https://www.linkedin.com/company/crestlineadvisory

做法：以 JSON 解析後修改再重新序列化（indent=2）。實測含鼎曜節點的 299 個
block 全部 round-trip byte-identical，因此只改語意、不動排版。
canvascrest 的權威來源是 _src/build.py（已同步修正），這裡只補產物。

用法: python3 scripts/fix_schema_2026_10_30.py --dry|--apply
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIB = os.path.dirname(BASE)                       # DingYao-Website/
ROOTS = [
    ("dingyao", os.path.join(BASE, "dist")),
    ("crestline", os.path.join(SIB, "crestline-advisory-site")),
    ("canvascrest", os.path.join(SIB, "canvascrest-site")),
]

DYAO_ID = "https://dingyaoadvisory.tw/#organization"
CREST_ID = "https://crestlineadvisory.co.za/#organization"
OLD_DATE = "2026-02-13"
SENT = "品牌自 2024 年起於台灣營運，2026 年 2 月完成公司設立登記（統一編號 60330590）。"
END_PUNCT = ("。", "．", ".", "！", "!", "？", "?")
CANON_DESC = ("鼎曜國際顧問是台灣的南非置產顧問公司，為南非 Crestline Advisory "
              "在亞太區的合作推廣夥伴，提供諮詢、不向客戶收費、不經手客戶資金。")
OLD_LI = "https://www.linkedin.com/company/dingyaoadvisory"
NEW_LI = "https://www.linkedin.com/company/crestlineadvisory"
ADDR_SWAP = {("台中市", "西屯區"): ("西屯區", "台中市"),
             ("Taichung City", "Xitun District"): ("Xitun District", "Taichung City")}

BLOCK_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def join_desc(desc):
    d = desc.rstrip()
    if not d.endswith(END_PUNCT):
        d += "。"
    return d + SENT


def walk_dicts(o, acc):
    if isinstance(o, dict):
        acc.append(o)
        for v in o.values():
            walk_dicts(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk_dicts(v, acc)
    return acc


def has_id(o, target):
    if isinstance(o, dict):
        if o.get("@id") == target:
            return True
        return any(has_id(v, target) for v in o.values())
    if isinstance(o, list):
        return any(has_id(v, target) for v in o)
    return False


def fix_sameas(o, acc):
    """只改 Crestline 節點（@id = crestlineadvisory.co.za/#organization）底下的
    LinkedIn 字串；鼎曜自己節點的 sameAs 指向鼎曜 LinkedIn 是正確的，不動。"""
    if isinstance(o, dict):
        if o.get("@id") == CREST_ID and len(o) > 1:
            _replace_li(o, acc)
            return
        for v in o.values():
            fix_sameas(v, acc)
    elif isinstance(o, list):
        for v in o:
            fix_sameas(v, acc)


def _replace_li(o, acc):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if isinstance(v, str) and v.rstrip("/") == OLD_LI:
                o[k] = NEW_LI
                acc["sameAs_linkedin_fixed"] += 1
            else:
                _replace_li(v, acc)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str) and v.rstrip("/") == OLD_LI:
                o[i] = NEW_LI
                acc["sameAs_linkedin_fixed"] += 1
            else:
                _replace_li(v, acc)


def process_block_body(body, acc):
    data = json.loads(body)
    if not (has_id(data, DYAO_ID) or has_id(data, CREST_ID)):
        return None
    li_before = acc["sameAs_linkedin_fixed"]
    fix_sameas(data, acc)
    n_li = acc["sameAs_linkedin_fixed"] - li_before
    n_addr = n_date = n_app = n_add = n_ok = 0
    for d in walk_dicts(data, []):
        if d.get("@id") != DYAO_ID or "foundingDate" not in d or len(d) == 1:
            continue
        if d["foundingDate"] == OLD_DATE:
            d["foundingDate"] = "2024"
            n_date += 1
        desc = d.get("description")
        if desc and SENT in desc:
            n_ok += 1
        elif desc:
            d["description"] = join_desc(desc)
            n_app += 1
        else:
            d["description"] = CANON_DESC + SENT
            n_add += 1
        a = d.get("address")
        if isinstance(a, dict):
            key = (a.get("addressLocality"), a.get("addressRegion"))
            if key in ADDR_SWAP:
                a["addressLocality"], a["addressRegion"] = ADDR_SWAP[key]
                n_addr += 1
    acc["address_fixed_nodes"] += n_addr
    acc["foundingDate_2024"] += n_date
    acc["desc_appended"] += n_app
    acc["desc_added"] += n_add
    acc["already_ok"] += n_ok
    if not (n_addr or n_date or n_app or n_add or n_li):
        return None
    dump = json.dumps(data, indent=2, ensure_ascii=False)
    lead = body[:len(body) - len(body.lstrip())]
    trail = body[len(body.rstrip()):]
    return lead + dump + trail


def process_file(path, acc, apply_changes):
    src = open(path, encoding="utf-8").read()
    out, last, changed = [], 0, False
    for m in BLOCK_RE.finditer(src):
        new = process_block_body(m.group(2), acc)
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
    acc = {k: 0 for k in ("address_fixed_nodes", "foundingDate_2024", "desc_appended",
                          "desc_added", "sameAs_linkedin_fixed", "already_ok")}
    changed = []
    for _name, root in ROOTS:
        for dp, _dn, fn in os.walk(root):
            rel = os.path.relpath(dp, root)
            parts = [] if rel == "." else rel.split(os.sep)
            if any(p.startswith((".", "_")) for p in parts):
                continue
            for f in sorted(fn):
                if not f.endswith(".html"):
                    continue
                p = os.path.join(dp, f)
                if process_file(p, acc, apply_changes):
                    changed.append(os.path.relpath(p, SIB))
    print(("APPLY" if apply_changes else "DRY"), json.dumps(acc, ensure_ascii=False))
    print("changed files:", len(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
