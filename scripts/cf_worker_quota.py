#!/usr/bin/env python3
"""量測 Worker 每日請求數 vs 免費方案上限（100,000 次/日）。

為什麼需要：2026-11-10 把 `run_worker_first` 從 6 條動態前綴放寬成 `"/*"`（排除靜態資產）
才能做 www → non-www 301。這件事讓「HTML 請求」從『不計費的資產層』變成『計入 Worker
請求數』，而免費方案超量會讓**全站**回錯誤。這支腳本就是量這條線。

（`CLOUDFLARE_API_TOKEN` 沒有 zone analytics 權限，但
  `CLOUDFLARE_WORKERS_TOKEN` 可以讀 workersInvocationsAdaptive，用這把。）

用法：
  python3 scripts/cf_worker_quota.py                 # 近 7 日，script=dingyao
  python3 scripts/cf_worker_quota.py --days 14
  python3 scripts/cf_worker_quota.py --script canvascrest

判讀：
  - 這數字只是「進入 Worker 的請求」，不含被排除的靜態資產（css/js/圖片）請求。
  - 佔比 > 30% 就該處理（正解＝改用 zone Redirect Rule 做 www 轉址，然後把
    run_worker_first 收回 6 條動態前綴）。
"""
import argparse
import collections
import datetime as dt
import json
import os
import subprocess
import sys

FREE_PLAN_DAILY_LIMIT = 100_000
ENV_FILE = os.path.expanduser("~/.hermes/.env")


def load_env():
    """從 ~/.hermes/.env 取 token / account（只讀需要的三個鍵）。"""
    vals = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip('"').strip("'")
    for key in ("CLOUDFLARE_WORKERS_TOKEN", "CLOUDFLARE_ACCOUNT_ID"):
        vals[key] = os.environ.get(key) or vals.get(key, "")
    return vals


def graphql(token, query) -> dict:
    proc = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://api.cloudflare.com/client/v4/graphql",
         "-H", "Authorization: Bearer " + token,
         "-H", "Content-Type: application/json",
         "--data-binary", json.dumps({"query": query})],
        capture_output=True, text=True,
    )
    try:
        out = json.loads(proc.stdout)
    except Exception:
        return {"errors": [{"message": "unparseable response: " + proc.stdout[:300]}]}
    return out if isinstance(out, dict) else {"errors": [{"message": "non-object response"}]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="dingyao")
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    env = load_env()
    token, account = env["CLOUDFLARE_WORKERS_TOKEN"], env["CLOUDFLARE_ACCOUNT_ID"]
    if not token or not account:
        sys.exit("缺少 CLOUDFLARE_WORKERS_TOKEN / CLOUDFLARE_ACCOUNT_ID")

    end = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - dt.timedelta(days=args.days)
    query = (
        '{viewer{accounts(filter:{accountTag:"%s"}){workersInvocationsAdaptive('
        'limit:1000,orderBy:[datetimeHour_ASC],filter:{datetime_geq:"%s",datetime_leq:"%s"})'
        '{sum{requests errors} dimensions{scriptName datetimeHour}}}}}'
        % (account, start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ"))
    )
    data = graphql(token, query)
    if data.get("errors") or not data.get("data"):
        print("GraphQL 失敗：", json.dumps(data.get("errors"), ensure_ascii=False))
        sys.exit(2)

    rows = [r for r in data["data"]["viewer"]["accounts"][0]["workersInvocationsAdaptive"]
            if r["dimensions"]["scriptName"] == args.script]
    daily, errors = collections.Counter(), 0
    for r in rows:
        daily[r["dimensions"]["datetimeHour"][:10]] += r["sum"]["requests"]
        errors += r["sum"]["errors"]

    if not daily:
        print(f"{args.script}：{args.days} 日內無 Worker 請求紀錄")
        return

    print(f"=== Worker `{args.script}` 每日請求數（UTC；上限 {FREE_PLAN_DAILY_LIMIT:,}/日）")
    peak = 0
    for day in sorted(daily):
        n = daily[day]
        peak = max(peak, n)
        print(f"  {day}  {n:>8,}  ({n / FREE_PLAN_DAILY_LIMIT * 100:5.2f}%)")
    total = sum(daily.values())
    print(f"  合計 {total:,} / 平均 {total / len(daily):,.0f} 每日 / 峰值 {peak:,}"
          f"（{peak / FREE_PLAN_DAILY_LIMIT * 100:.2f}%）/ errors={errors}")
    if peak / FREE_PLAN_DAILY_LIMIT > 0.3:
        print("  ⚠️ 峰值已超過上限 30%：考慮把 www 轉址改到 zone Redirect Rule，"
              "並把 run_worker_first 收回動態前綴。")


if __name__ == "__main__":
    main()
