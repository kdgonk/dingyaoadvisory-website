/**
 * 404 fallback 修復 — Cloudflare Pages Middleware（2026-10-14，土星人指派）
 *
 * 問題：本專案的 CF Pages 內建「找不到 → 最近的 404.html」機制失效 ——
 *       任意不存在路徑一律 HTTP 404 且 body = 0 bytes（訪客看不到設計好的 404 頁）。
 *       已排除：_redirects 無 catch-all（93 條全是具體 301）、無 _worker.js / _routes.json /
 *       functions、dist/404.html 存在且完整（46KB）、_redirects 的 301 正常生效、
 *       /404.html 會被 307 正規化到 /404（200）。同帳號的 crestline 專案同一機制正常運作。
 *       官方文件：_redirects 不支援 404 狀態碼（Rewrites ❌），而 catch-all 會蓋掉所有
 *       靜態資源（"Redirects are always followed, regardless of whether or not an asset
 *       matches"）→ 因此兩條路都不能走，改用 middleware 補上 fallback。
 *
 * 安全設計（完全被動、不可能造成 500）：
 *   1. 先 context.next() 走正常流程；非 404 一律原樣返回 → 正常頁面/資源完全不受影響。
 *   2. 只有 404 時才去取 /404.html 內容回填，並維持 HTTP 404 狀態碼。
 *   3. 取不到 404.html、或任何例外 → 回原本的 404（不會製造新的錯誤頁）。
 *   4. /__middleware-check 為健康探針（確認 middleware 有被執行），no-store。
 */

export async function onRequest(context) {
  let res;
  try {
    res = await context.next();
  } catch (err) {
    return new Response('Not Found', {
      status: 404,
      headers: { 'content-type': 'text/plain; charset=utf-8' },
    });
  }

  try {
    const url = new URL(context.request.url);

    // 健康探針：證明 middleware 真的被 Pages 執行
    if (url.pathname === '/__middleware-check') {
      return new Response('middleware-ok', {
        status: 200,
        headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' },
      });
    }

    if (res.status !== 404) return res;

    // 取設計好的 404 頁（先試 404.html，失敗再試正規化後的 /404）
    let page = await context.env.ASSETS.fetch(new URL('/404.html', url.origin));
    if (!page.ok) page = await context.env.ASSETS.fetch(new URL('/404', url.origin));
    if (!page.ok) return res;

    const headers = new Headers(page.headers);
    headers.set('content-type', 'text/html; charset=utf-8');
    headers.set('cache-control', 'no-store');
    headers.delete('content-length');
    return new Response(page.body, { status: 404, statusText: 'Not Found', headers });
  } catch (err) {
    return res;
  }
}
