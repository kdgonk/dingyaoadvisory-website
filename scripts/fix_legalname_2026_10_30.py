#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三站 JSON-LD legalName 修正（P1，天秤人覆核 2026-10-29／土星人 2026-10-30 派工）

① 鼎曜   "DingYao International Advisory Ltd." / "…Ltd" → "DingYao Advisory"
   依據：老闆 2026-10-29 口徑 —— 對外一律 DingYao Advisory，法定全名只用在「法律當事人」欄位
        （HTML 內文），不得進 JSON-LD 的 name／alternateName／legalName。
② CanvasCrest "CanvasCrest Properties" → "CanvasCrest Properties (Pty) Ltd"
   依據：CIPC 後綴 /07 為私人公司，Companies Act 71 of 2008 s11(3)(c) 強制 (Pty) Ltd。
③ Crestline "Crestline Advisory (Pty) Ltd" 已正確，不動。

做法：只改 JSON-LD <script> 區塊內 legalName 的字串值（不重新序列化，避免整份 JSON 重排），
      以 key 為錨點，可重複執行（idempotent）。

用法: python3 scripts/fix_legalname_2026_10_30.py --dry|--apply
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
BLOCK_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

RE_DYAO = re.compile(r'"legalName"\s*:\s*"DingYao International Advisory Ltd\.?"')
RE_CC = re.compile(r'"legalName"\s*:\s*"CanvasCrest Properties"')
RE_CC_BAD_SUFFIX = re.compile(r'"legalName"\s*:\s*"CanvasCrest Properties \(Pty\) Ltd"')

FIX_DYAO = '"legalName": "DingYao Advisory"'
FIX_CC = '"legalName": "CanvasCrest Properties (Pty) Ltd"'


def fix_block(body, acc):
    n1 = len(RE_DYAO.findall(body))
    n2 = len(RE_CC.findall(body))
    if not n1 and not n2:
        return None
    body = RE_DYAO.sub(FIX_DYAO, body)
    body = RE_CC.sub(FIX_CC, body)
    acc["dingyao"] += n1
    acc["canvascrest"] += n2
    # 驗證仍是合法 JSON
    json.loads(body)
    return body


def main():
    apply_changes = "--apply" in sys.argv
    acc = {"dingyao": 0, "canvascrest": 0, "files": 0}
    per_site = {}
    for site, root in ROOTS:
        for dp, _dn, fn in os.walk(root):
            rel = os.path.relpath(dp, root)
            parts = [] if rel == "." else rel.split(os.sep)
            if any(p.startswith((".", "_")) for p in parts):
                continue
            for f in sorted(fn):
                if not f.endswith(".html"):
                    continue
                path = os.path.join(dp, f)
                src = open(path, encoding="utf-8").read()
                out, last, changed = [], 0, False
                for m in BLOCK_RE.finditer(src):
                    new = fix_block(m.group(2), acc)
                    if new is None:
                        continue
                    out.append(src[last:m.start()])
                    out.append(m.group(1) + new + m.group(3))
                    last = m.end()
                    changed = True
                if changed:
                    out.append(src[last:])
                    acc["files"] += 1
                    per_site[site] = per_site.get(site, 0) + 1
                    if apply_changes:
                        open(path, "w", encoding="utf-8").write("".join(out))
    print(("APPLY" if apply_changes else "DRY"), json.dumps(acc, ensure_ascii=False),
          "| files per site:", json.dumps(per_site, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
