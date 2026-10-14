#!/usr/bin/env python3
"""產生 dist/_worker.js（Pages advanced mode）— 讓缺頁回設計好的 404 頁。

為什麼要把 404 頁「內嵌」進 worker，而不是 runtime 去 env.ASSETS 取檔：
  production 的 ASSETS binding 對 '/404' 不做 extensionless 解析（回 404），
  而 '/404.html' 會被 Pages 路由以 307／308 重導（取不到 200 body）→
  兩條路都取不到檔案，worker 只能回退成平台原生的空 404（body=0）。
  故改由本腳本在 build 時把 dist/404.html 內容內嵌，行為 100% 確定。

用法：python3 scripts/gen_worker_404.py   （改過 dist/404.html 後重跑，CI 前也建議跑）
驗證：本機 `npx wrangler@4.81.1 pages dev dist` → 缺頁應回 404 + 404 頁內容。
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "dist" / "404.html"
OUT = ROOT / "dist" / "_worker.js"

TEMPLATE = """/**
 * Pages advanced-mode worker（由 scripts/gen_worker_404.py 產生，請勿手改）
 * 目的：缺頁回「設計好的 404 頁」並維持 404 狀態碼（本專案 Pages Functions 未被編譯，
 *       平台 fallback 亦失效 → 缺頁 body=0，故由 worker 接管）。
 * 來源頁面：dist/404.html（{src_bytes} bytes，內嵌快照）
 * 被動式：非 404 一律原樣返回（_redirects 的 301／200 由 env.ASSETS 一併沿用）。
 */
const NOT_FOUND_HTML = {payload};

export default {{
  async fetch(request, env) {{
    const res = await env.ASSETS.fetch(request);
    if (res.status !== 404) {{
      // 讓「worker 是否真的在跑」可被外部驗證（無害標頭）
      const h = new Headers(res.headers);
      h.set('x-titan-worker', 'gen404-v3');
      return new Response(res.body, {{ status: res.status, statusText: res.statusText, headers: h }});
    }}
    return new Response(NOT_FOUND_HTML, {{
      status: 404,
      headers: {{
        'content-type': 'text/html; charset=utf-8',
        'cache-control': 'no-cache',
        'x-titan-worker': 'gen404-v3',
      }},
    }});
  }},
}};
"""


def main() -> int:
    if not SRC.exists():
        print(f"✗ 找不到 {SRC}", file=sys.stderr)
        return 1
    html = SRC.read_text(encoding="utf-8")
    payload = json.dumps(html, ensure_ascii=True)
    OUT.write_text(
        TEMPLATE.format(payload=payload, src_bytes=len(html.encode("utf-8"))),
        encoding="utf-8",
    )
    print(f"✅ 寫出 {OUT}（{len(OUT.read_text(encoding='utf-8'))} chars，內嵌 {len(html.encode('utf-8'))} bytes HTML）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
