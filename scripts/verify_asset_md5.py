#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署前 MD5 閘門：live 圖檔必須「逐位元」等於定稿批，才准 push。

為什麼需要（2026-10-28 S-20261028-VALU）：
live 上 7 張圖 HTTP 全 200，但內容是「暖色日光」錯批（hero 4e6938f7／72,564B），
定稿是 out_final 批（hero 1911ee21／64,940B）。**200 不等於正確** ——
只驗狀態碼會把錯圖推上線，所以用 MD5 逐檔比對。

用法：
  python3 scripts/verify_asset_md5.py                      # 用預設 manifest
  python3 scripts/verify_asset_md5.py --manifest scripts/valuation_assets_md5.json
  python3 scripts/verify_asset_md5.py --json               # 只印 JSON（給其他腳本吃）

Exit code：0 = 全部符合（可部署）／1 = 有檔案不符（**不得部署**）／2 = 下載失敗或 manifest 壞掉
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO / "scripts" / "valuation_assets_md5.json"
UA = {"User-Agent": "Mozilla/5.0 TitanMd5Gate/1.0"}


def fetch(url: str, timeout: int = 40):
    """回傳 (bytes, md5)。連線失敗丟例外。"""
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data, hashlib.md5(data).hexdigest()


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    manifest_path = DEFAULT_MANIFEST
    for i, a in enumerate(args):
        if a == "--manifest" and i + 1 < len(args):
            manifest_path = Path(args[i + 1])
        elif a.startswith("--manifest="):
            manifest_path = Path(a.split("=", 1)[1])

    if not manifest_path.exists():
        print(f"❌ manifest 不存在: {manifest_path}")
        return 2
    try:
        man = json.loads(manifest_path.read_text(encoding="utf-8"))
        base = man["base_url"]
        suffix = man.get("suffix", "")
        assets = man["assets"]
    except Exception as e:  # noqa: BLE001
        print(f"❌ manifest 解析失敗: {e}")
        return 2

    rows, bad, dl_err = [], [], []
    for a in assets:
        name = a["name"]
        url = f"{base}{name}{suffix}"
        want = a["md5"].lower()
        try:
            data, got = fetch(url)
        except Exception as e:  # noqa: BLE001
            dl_err.append((name, str(e)[:80]))
            rows.append({"name": name, "url": url, "expected": want, "got": None,
                         "bytes": None, "ok": False, "error": str(e)[:80]})
            continue
        ok = got == want
        if not ok:
            bad.append((name, got, len(data), a.get("bytes")))
        rows.append({"name": name, "url": url, "expected": want, "got": got,
                     "bytes": len(data), "ok": ok})

    if as_json:
        print(json.dumps({"slug": man.get("slug"), "all_ok": not bad and not dl_err, "rows": rows},
                         ensure_ascii=False, indent=2))
        return 0 if (not bad and not dl_err) else (1 if bad else 2)

    print(f"manifest: {manifest_path.name}（slug={man.get('slug')}）")
    for r in rows:
        if r["got"] is None:
            print(f"  ❌ {r['name']:5s} 下載失敗  {r['error']}")
        else:
            mark = "✅" if r["ok"] else "❌"
            extra = ""
            if not r["ok"]:
                extra = f"  期望 {r['expected']} 實得 {r['got']}（{r['bytes']}B）"
            print(f"  {mark} {r['name']:5s} {r['got']} {r['bytes']}B{extra}")
    print()
    if bad:
        print(f"❌ MD5 閘門 FAIL：{len(bad)}/{len(rows)} 張與定稿不符 → **不得部署**")
        print("   寧可延一天，也不要把錯圖／舊批推上線。等木星人重傳 out_final 批並 purge 後重跑。")
        return 1
    if dl_err:
        print(f"❌ MD5 閘門無法判定：{len(dl_err)} 張下載失敗 → 不得部署（連線問題不是通過理由）")
        return 2
    print(f"✅ MD5 閘門 PASS：{len(rows)}/{len(rows)} 張與定稿逐位元相同，可部署")
    return 0


if __name__ == "__main__":
    sys.exit(main())
