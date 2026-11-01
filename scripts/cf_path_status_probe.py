#!/usr/bin/env python3
"""查 Cloudflare 邊緣對指定路徑的 HTTP 狀態分布（含 Googlebot 切片）。

用途：判斷 Googlebot 是否曾被邊緣回 4xx/5xx（索引退步的技術性排除）。
資料集：httpRequestsAdaptiveGroups（免費方案保留期約 30 天）。
"""
import json
import os
import subprocess
import sys

ZONE = "3f0348f934248a25899b5c0906135323"
PATH = sys.argv[1] if len(sys.argv) > 1 else "/blog/cape-town-safety-guide-foreign-buyers-2026"
START = sys.argv[2] if len(sys.argv) > 2 else "2026-10-26T00:00:00Z"
END = sys.argv[3] if len(sys.argv) > 3 else "2026-11-02T23:59:59Z"

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")


def gql(query):
    p = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            "https://api.cloudflare.com/client/v4/graphql",
            "-H", f"Authorization: Bearer {TOKEN}",
            "-H", "Content-Type: application/json",
            "--data-binary", json.dumps({"query": query}),
        ],
        capture_output=True, text=True,
    )
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"raw": p.stdout[:800], "err": p.stderr[:400]}


def show(title, data):
    print(f"\n=== {title} ===")
    if "errors" in data:
        print("ERRORS:", json.dumps(data["errors"], ensure_ascii=False)[:1500])
    res = (data.get("data") or {}).get("viewer", {}).get("zones") or []
    if not res:
        print("(no zone data)", json.dumps(data, ensure_ascii=False)[:600])
        return
    groups = res[0].get("httpRequestsAdaptiveGroups") or []
    if not groups:
        print("(0 rows — 此期間邊緣無此路徑請求紀錄)")
    for g in groups:
        print(json.dumps(g, ensure_ascii=False, sort_keys=True))


# 1) 全部狀態碼分布（精確路徑）
q1 = f'''{{
  viewer {{
    zones(filter: {{zoneTag: "{ZONE}"}}) {{
      httpRequestsAdaptiveGroups(
        limit: 50,
        filter: {{clientRequestPath: "{PATH}",
                  datetime_geq: "{START}", datetime_leq: "{END}"}},
        orderBy: [count_DESC]
      ) {{
        count
        dimensions {{ edgeResponseStatus clientRequestPath }}
      }}
    }}
  }}
}}'''

# 2) 以日期 × 狀態碼
q2 = f'''{{
  viewer {{
    zones(filter: {{zoneTag: "{ZONE}"}}) {{
      httpRequestsAdaptiveGroups(
        limit: 100,
        filter: {{clientRequestPath: "{PATH}",
                  datetime_geq: "{START}", datetime_leq: "{END}"}},
        orderBy: [date_ASC]
      ) {{
        count
        dimensions {{ date edgeResponseStatus }}
      }}
    }}
  }}
}}'''

# 3) Googlebot 切片（UA 含 Googlebot）
q3 = f'''{{
  viewer {{
    zones(filter: {{zoneTag: "{ZONE}"}}) {{
      httpRequestsAdaptiveGroups(
        limit: 50,
        filter: {{clientRequestPath: "{PATH}",
                  userAgent_like: "%Googlebot%",
                  datetime_geq: "{START}", datetime_leq: "{END}"}},
        orderBy: [count_DESC]
      ) {{
        count
        dimensions {{ edgeResponseStatus date }}
      }}
    }}
  }}
}}'''

show("1) 狀態碼分布（全 UA，10-26~11-02）", gql(q1))
show("2) 日期 × 狀態碼", gql(q2))
show("3) Googlebot UA 切片", gql(q3))
