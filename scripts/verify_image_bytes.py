#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_image_bytes.py — CDN 圖片「位元組數」逐檔核對（HTTP 200 不算通過）

為什麼：木星人交付單給的是 bytes；CDN 回 200 但內容可能是舊版/另一張圖。
本工具對每張圖取 content-length（必要時 GET 實測），與交付單 bytes 逐檔比對。

用法：
  python3 scripts/verify_image_bytes.py \
      --manifest runs/2026-10-31/image-manifest-bytes.json \
      --prefix taiwan-high-dividend-etf-vs-south-africa-deposit-2026

  # 不給 --manifest 時，自動找最近一份 runs/*/image-manifest-bytes.json
Exit：0 全部相符 / 2 有缺檔或位元組不符
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ASSETS = "https://assets.dingyaoadvisory.tw/blog/images/"
REPO = Path(__file__).resolve().parent.parent


def probe(url: str, timeout: int = 30):
    """回傳 (status, content_length, content_type)；HEAD 無長度時用 GET 實測"""
    def _once(method: str):
        req = urllib.request.Request(url, method=method,
                                     headers={"User-Agent": "titan-bytecheck/1.0", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cl = r.headers.get("content-length")
            if method == "GET":
                raw = r.read()
                return r.status, int(cl) if cl and cl.isdigit() else len(raw), (r.headers.get("content-type") or "")
            return r.status, int(cl) if cl and cl.isdigit() else 0, (r.headers.get("content-type") or "")

    try:
        st, size, ct = _once("HEAD")
    except urllib.error.HTTPError as e:
        return e.code, 0, (e.headers.get("content-type") if e.headers else "") or ""
    except Exception as e:
        return 0, 0, f"ERR:{e}"
    if st == 200 and size == 0:  # HEAD 無 content-length → GET 實測
        try:
            st, size, ct = _once("GET")
        except Exception as e:
            return 0, 0, f"ERR:{e}"
    return st, size, ct


def find_manifest() -> Path | None:
    cands = sorted(REPO.glob("runs/*/image-manifest-bytes.json"))
    return cands[-1] if cands else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=None, help="交付單 JSON（[{file,bytes}, …] 或 {file: bytes}）")
    ap.add_argument("--prefix", default=None, help="只驗檔名以此開頭的圖（用 slug 過濾）")
    args = ap.parse_args()

    mp = Path(args.manifest) if args.manifest else find_manifest()
    if not mp or not mp.exists():
        print(f"🛑 找不到交付單 manifest: {mp}")
        return 2
    data = json.loads(mp.read_text(encoding="utf-8"))
    rows = []
    if isinstance(data, dict):
        for k, v in data.items():
            rows.append({"file": k, "bytes": v.get("bytes") if isinstance(v, dict) else v})
    else:
        rows = data
    if args.prefix:
        rows = [r for r in rows if str(r.get("file", "")).startswith(args.prefix)]
    if not rows:
        print(f"🛑 manifest 內沒有符合 prefix={args.prefix} 的圖")
        return 2

    print(f"manifest: {mp}")
    print(f"待驗 {len(rows)} 檔（prefix={args.prefix or '(全部)'}）\n")
    bad, total_expected, total_actual = [], 0, 0
    for r in rows:
        name = r["file"]
        exp = int(r["bytes"])
        st, size, ct = probe(ASSETS + name)
        ok = st == 200 and size == exp
        total_expected += exp
        total_actual += size
        if not ok:
            bad.append((name, st, exp, size))
        print(f"  {'✅' if ok else '❌'} {name}  HTTP {st}  {ct.split(';')[0]}  bytes {size:,} / 預期 {exp:,}"
              + ("" if ok else f"  ← 差 {size - exp:+,}"))

    print(f"\n相符 {len(rows) - len(bad)}/{len(rows)}｜bytes 合計 實際 {total_actual:,} / 預期 {total_expected:,}")
    if bad:
        print("\n🛑 未通過（不得部署，請木星人重傳或 purge 後重試）：")
        for name, st, exp, size in bad:
            print(f"   - {name}: HTTP {st}, {size:,} ≠ {exp:,}")
        return 2
    print("✅ 全部逐檔位元組相符（HTTP 200 之外還比對了 content-length）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
