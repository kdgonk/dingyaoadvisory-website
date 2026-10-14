/**
 * Pages「Advanced Mode」_worker.js — 讓缺頁回設計好的 404 頁（維持 404 狀態碼）
 * 2026-10-14 泰坦人。
 *
 * 背景：本專案 Pages Functions 完全不被編譯（repo 根與 dist/functions 兩處皆實證無效，
 * POST /api/contact 自 2026-10-08 起一直 404/0B）；production 缺頁回 0 bytes、無 content-type。
 * 對策：進 advanced mode 由本 worker 接管路由；env.ASSETS 原樣服務資產（_redirects 的 301 一併沿用）。
 *
 * ⚠️ 2026-10-14 踩雷：不能用 '/404.html' 取檔 —— production 對 /404.html 回 307（extensionless
 * redirect），舊版因此取不到而回退成空 404。改用 '/404'（實測 200），並保留 .html 備援。
 */
async function designed404(env, request) {
  for (const path of ['/404', '/404.html']) {
    try {
      const r = await env.ASSETS.fetch(
        new Request(new URL(path, request.url).toString(), { method: 'GET' })
      );
      if (r.status === 200) return r;
    } catch (e) {
      /* 取不到就換下一個候選 */
    }
  }
  return null;
}

export default {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    if (res.status !== 404) return res; // 正常頁、301/308、資產 → 原樣返回

    const nf = await designed404(env, request);
    if (!nf) return res; // 取不到 404 頁 → 維持原本行為（不會更糟）

    return new Response(await nf.text(), {
      status: 404,
      headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-cache' },
    });
  },
};
