/**
 * Pages「Advanced Mode」_worker.js — 讓缺頁回設計好的 404 頁（維持 404 狀態碼）
 * 2026-10-14 泰坦人。用途：本專案 Pages Functions 完全不被編譯（已實證），
 * 且 production 缺頁回 0 bytes；改由 advanced-mode worker 接管路由。
 * 被動式：非 404 一律原樣返回（含 _redirects 的 301／200，由 env.ASSETS 套用）。
 */
export default {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    if (res.status !== 404) return res;
    // 缺頁 → 取設計好的 404.html，維持 404 狀態碼
    const url = new URL('/404.html', request.url);
    const nf = await env.ASSETS.fetch(new Request(url.toString(), { method: 'GET' }));
    if (nf.status !== 200) return res;
    return new Response(await nf.text(), {
      status: 404,
      headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-cache' },
    });
  },
};
