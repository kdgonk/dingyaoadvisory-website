#!/usr/bin/env python3
"""
建立 dingyao LINE 短網址 Bulk Redirects（20 條：/go/<key> + /l/<key>）。

為什麼需要這支腳本：本機現有的兩把 token（CLOUDFLARE_API_TOKEN /
CLOUDFLARE_WORKERS_TOKEN）只有 Workers Scripts + Cache Purge 權限，
呼叫 account 層的 /rules/lists 與 /rulesets 一律回
  {"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}
所以下列 API 動作在泰坦人這邊無法執行。任何持有下列權限的 token 直接跑本腳本即可：

  Account → Account Filter Lists → Edit
  Account → Account Rulesets → Edit
  （選用）Zone → Zone → Read

用法：
  export CF_TOKEN=<有上面權限的 token>
  python3 bulk_redirects.py            # 建立 list + items + account ruleset
  python3 bulk_redirects.py --dry-run  # 只印 payload

冪等：list 已存在（同名）就沿用並補 items（upsert 會覆蓋同 source_url）；
      ruleset 已存在就 PUT 更新 entrypoint（保留其他既有 rule）。
"""
import json
import os
import sys
import urllib.error
import urllib.request

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "af169f51e2e3e92a7ab7e51e1936f06a")
TOKEN = os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN", "")
LIST_NAME = "dingyao_line_shortlinks"
API = "https://api.cloudflare.com/client/v4"

UTM = "utm_source=line&utm_medium=oa"
ASSET = "https://assets.dingyaoadvisory.tw/whitepapers/"

# key -> (target, campaign, content)
LINKS = {
    "wb-bank": (ASSET + "dingyao-bank-vs-taiwan-whitepaper-2026-zh.pdf", "whitebook", "bank"),
    "wb-prop": (ASSET + "dingyao-property-whitepaper-2026-zh.pdf", "whitebook", "prop"),
    "wb-edu": (ASSET + "dingyao-education-whitepaper-2026-zh.pdf", "whitebook", "edu"),
    "wb-rent": (ASSET + "dingyao-rental-management-whitepaper-2026-zh.pdf", "whitebook", "rent"),
    "bank": ("https://dingyaoadvisory.tw/south-africa-bank-account", "menu", "bank"),
    "prop": ("https://dingyaoadvisory.tw/south-africa-property", "menu", "prop"),
    "edu": ("https://dingyaoadvisory.tw/education", "menu", "edu"),
    "book": ("https://cal.com/dingyao/30min", "booking", "human"),
    "consult": ("https://dingyaoadvisory.tw/consultation", "menu", "consult"),
    "line": ("https://dingyaoadvisory.tw/", "menu", "home"),
}


def target_url(key):
    base, campaign, content = LINKS[key]
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{UTM}&utm_campaign={campaign}&utm_content={content}"


def build_items():
    items = []
    for prefix in ("go", "l"):
        for key in LINKS:
            items.append({
                "redirect": {
                    "source_url": f"https://dingyaoadvisory.tw/{prefix}/{key}",
                    "target_url": target_url(key),
                    "status_code": 302,
                    "preserve_query_string": False,
                }
            })
    return items


RULE = {
    "action": "redirect",
    "action_parameters": {
        "from_list": {"name": LIST_NAME, "key": "http.request.full_uri"},
        "status_code": 302,          # 一定 302，不可 301（LINE 內建瀏覽器會硬記 301）
        "preserve_query_string": False,
    },
    "expression": f"http.request.full_uri in ${LIST_NAME}",
    "description": "LINE shortlinks: /go/<key> + /l/<key> -> 302 (utm_source=line&utm_medium=oa)",
    "enabled": True,
}


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def main():
    items = build_items()
    print(f"共 {len(items)} 條 items（10 key × go+l）")

    if "--dry-run" in sys.argv:
        print(json.dumps({"items": items, "rule": RULE}, ensure_ascii=False, indent=2))
        return

    if not TOKEN:
        sys.exit("CF_TOKEN / CLOUDFLARE_API_TOKEN 未設定")

    # 1) list
    found = None
    res = call("GET", f"/accounts/{ACCOUNT_ID}/rules/lists")
    for lst in (res.get("result") or []):
        if lst.get("name") == LIST_NAME:
            found = lst["id"]
            break
    if found:
        print(f"[1] list 已存在 id={found}")
    else:
        res = call("POST", f"/accounts/{ACCOUNT_ID}/rules/lists", {
            "kind": "host",
            "name": LIST_NAME,
            "description": "dingyao LINE shortlinks (see runs/2026-10-22-line-shortlinks)",
        })
        if not res.get("success"):
            sys.exit(f"[1] 建立 list 失敗: {res}")
        found = res["result"]["id"]
        print(f"[1] list 已建立 id={found}")

    # 2) items
    res = call("POST", f"/accounts/{ACCOUNT_ID}/rules/lists/{found}/items", {"items": items})
    if not res.get("success"):
        sys.exit(f"[2] 寫入 items 失敗: {res}")
    print(f"[2] items 寫入成功 operation_id={res['result'].get('operation_id')}")

    # 3) account ruleset (http_request_dynamic_redirect) — 排在 Cache Lookup 之前
    res = call("GET", f"/accounts/{ACCOUNT_ID}/rulesets/phases/http_request_dynamic_redirect/entrypoint")
    rs = res.get("result")
    if rs and rs.get("id"):
        rules = [r for r in (rs.get("rules") or []) if r.get("description") != RULE["description"]]
        rules.append(RULE)
        res = call("PUT", f"/accounts/{ACCOUNT_ID}/rulesets/{rs['id']}", {"rules": rules})
    else:
        res = call("POST", f"/accounts/{ACCOUNT_ID}/rulesets", {
            "name": "default",
            "kind": "root",
            "phase": "http_request_dynamic_redirect",
            "rules": [RULE],
        })
    if not res.get("success"):
        sys.exit(f"[3] 建立/更新 redirect ruleset 失敗: {res}")
    print(f"[3] redirect ruleset OK id={res['result'].get('id')} version={res['result'].get('version')}")
    print("完成。接著 purge_everything 再驗證 curl。")


if __name__ == "__main__":
    main()
