#!/usr/bin/env python3
"""把 dingyao 全站 JSON-LD 的 legalName 從品牌名改為中文法定全名（2026-11-10）。

為什麼（老闆 2026-11-10 指示）：GBP（Google 商家檔案）名稱是「鼎曜國際顧問有限公司
DingYao Advisory」，但官網 JSON-LD 的 legalName 一直是品牌名「DingYao Advisory」，
Google 搜尋結果因此對首頁／about／contact 標「缺少字詞：有限／有限公司」——兩個實體。

做兩件事：
1. 既有值替換：`"legalName": "DingYao Advisory"` → `"legalName": "鼎曜國際顧問有限公司"`
   （全站 326 處 / 309 檔；Crestline、CanvasCrest 的值不動）
2. 補齊：publisher 內嵌的 DingYao Organization 缺 legalName 者，插在 "name" 之後
   （同一實體的其他 publisher 都有這個欄位，缺的是少數舊文）

不動：name／alternateName／title／meta／其他任何欄位；不碰其他兩站的節點。

驗收不變式（--apply 後自動跑）：
  a. 每個 JSON-LD block 都能 json.loads
  b. 把兩邊的 legalName 全部剝除後，新舊 JSON 必須 deep-equal（＝只動了 legalName）
  c. HTML 的「非 JSON-LD」部分必須位元組完全相同

用法：
  python3 scripts/fix_legalname_zh_2026_11_10.py --dry   # 只報告
  python3 scripts/fix_legalname_zh_2026_11_10.py --apply
"""
import argparse
import glob
import json
import re
import sys

BRAND_ONLY = "DingYao Advisory"
NEW_LEGAL = "鼎曜國際顧問有限公司"
LD_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)


def norm_block(text):
    """把 block 內的 legalName 全部剝除，用來證明「只改了 legalName」。"""

    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if k != "legalName"}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o

    return strip(json.loads(text))


def file_blocks(html):
    return LD_RE.findall(html)


def is_dingyao_org(node):
    name = node.get("name") if isinstance(node.get("name"), str) else ""
    url = node.get("url") if isinstance(node.get("url"), str) else ""
    nid = node.get("@id") if isinstance(node.get("@id"), str) else ""
    return "dingyaoadvisory.tw" in url or "dingyaoadvisory.tw" in nid or (
        "DingYao" in name or "鼎曜" in name
    )


def add_legalname_to_publishers(text):
    """在指名的內嵌 Organization 物件裡補 legalName（缺才補）。

    涵蓋 `publisher`（文章宣告的發布者）與 `mainEntity`（contact 頁的 ContactPage→
    Organization）—— 兩者都是同一個鼎曜實體，缺 legalName 就會讓 Google 看到
    「品牌名」與「法定全名」兩套身分。

    以文字插入實作，保留原檔縮排與排版（不重新序列化整個 block）。
    """
    added = 0
    out = text
    for key in ("publisher", "mainEntity"):
        # 逐一找出 "<indent>"<key>": { 區塊，檢查其後的物件是否含 legalName
        for m in list(re.finditer(r'^([ \t]*)"%s"\s*:\s*\{' % key, out, re.M)):
            start = m.end()
            # 取下一個 key 行的縮排
            nxt = re.compile(r'\n([ \t]*)"').search(out, start)
            if not nxt:
                continue
            inner_indent = nxt.group(1)
            # 物件的結尾（縮排回到外層）
            end_m = re.compile(r'\n' + re.escape(m.group(1)) + r'\}').search(out, start)
            if not end_m:
                continue
            chunk = out[start:end_m.start()]
            if '"legalName"' in chunk:
                continue
            if '"Organization"' not in chunk or 'dingyaoadvisory' not in chunk:
                continue
            # 插在 "@type" 行之後（保持同一縮排）
            type_m = re.compile(r'\n' + re.escape(inner_indent) + r'"@type"\s*:\s*"[^"]*",').search(chunk)
            if not type_m:
                continue
            insert_at = start + type_m.end()
            line = '\n' + inner_indent + '"legalName": "' + NEW_LEGAL + '",'
            out = out[:insert_at] + line + out[insert_at:]
            added += 1
    return out, added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dist", default="dist")
    args = ap.parse_args()

    files = sorted(glob.glob(args.dist + "/**/*.html", recursive=True))
    replaced_total = added_total = 0
    changed_files = 0
    problems = []

    for path in files:
        old = open(path, encoding="utf-8").read()
        old_blocks = file_blocks(old)
        old_rest = LD_RE.sub("<LD/>", old)

        new = old.replace('"legalName": "%s"' % BRAND_ONLY, '"legalName": "%s"' % NEW_LEGAL)
        replaced = old.count('"legalName": "%s"' % BRAND_ONLY)
        new, added = add_legalname_to_publishers(new)

        if new == old:
            continue

        # ---- 不變式 ----
        new_blocks = file_blocks(new)
        if len(new_blocks) != len(old_blocks):
            problems.append((path, "block 數改變 %d→%d" % (len(old_blocks), len(new_blocks))))
            continue
        try:
            pairs = [(json.loads(a), json.loads(b)) for a, b in zip(old_blocks, new_blocks)]
        except Exception as exc:
            problems.append((path, "JSON 解析失敗：%r" % (exc,)))
            continue
        for i, (a, b) in enumerate(pairs):
            if norm_block(json.dumps(a)) != norm_block(json.dumps(b)):
                problems.append((path, "block %d 除 legalName 外有變動" % i))
        if LD_RE.sub("<LD/>", new) != old_rest:
            problems.append((path, "非 JSON-LD 的 HTML 被改動"))

        replaced_total += replaced
        added_total += added
        changed_files += 1
        if args.apply:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)

    print(("套用" if args.apply else "乾跑") + "：變更檔案 %d／%d" % (changed_files, len(files)))
    print("  既有值替換 %d 處、publisher 補欄位 %d 處" % (replaced_total, added_total))
    if problems:
        print("  ❌ 不變式失敗 %d 筆：" % len(problems))
        for p in problems[:20]:
            print("    ", p[0], "→", p[1])
        sys.exit(1)
    print("  ✅ 不變式全過（JSON 合法／只動 legalName／非 JSON-LD 區塊位元組不變）")


if __name__ == "__main__":
    main()
