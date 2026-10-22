/**
 * /api/whitepaper 與既有 /api/lead 的單元測試（mock Chatwoot，不寫入真實 CRM）
 * 執行：node test-worker.mjs
 */
import worker from './worker-v2.mjs';

const results = [];
function check(name, cond, detail = '') {
  results.push([name, !!cond]);
  console.log((cond ? 'PASS  ' : 'FAIL  ') + name + (detail ? '  :: ' + detail : ''));
}

// ---- mock Chatwoot ----
let captured = null;
let mockStatus = 200;
let mockBody = { payload: { contact: { id: 9911, name: 'mock' } } };

globalThis.fetch = async (url, init) => {
  captured = { url: String(url), headers: init.headers, body: JSON.parse(init.body) };
  return {
    ok: mockStatus >= 200 && mockStatus < 300,
    status: mockStatus,
    json: async () => mockBody
  };
};

const env = { CHATWOOT_API_TOKEN: 'fake-token-for-test', ASSETS: { fetch: async () => new Response('ASSET', { status: 200 }) } };

function req(path, body, method = 'POST', raw = null) {
  return new Request('https://dy.test' + path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: method === 'GET' ? undefined : raw !== null ? raw : JSON.stringify(body)
  });
}

async function call(reqObj) {
  const res = await worker.fetch(reqObj, env);
  let json = null;
  try { json = await res.json(); } catch (e) {}
  return { status: res.status, json };
}

// ============ /api/whitepaper ============
console.log('\n--- /api/whitepaper ---');

captured = null;
let r = await call(req('/api/whitepaper', {
  name: '陳小姐', phone: '+886 912-345-678', pillar: 'property',
  asset_name: 'whitepaper_property_2026',
  utm: { utm_source: 'line', utm_campaign: '2026q4', liff_id: '1657-abc' }
}));
check('3 欄表單（無 email）可成功送出', r.status === 200 && r.json.ok === true, `status=${r.status} ${JSON.stringify(r.json).slice(0,80)}`);
check('無 email 時合成 WhatsApp 識別', captured && captured.body.email === 'wa+886912345678@lead.dingyaoadvisory.tw', captured && captured.body.email);
check('phone 正規化（去空白與連字號）', captured && captured.body.phone_number === '+886912345678', captured && captured.body.phone_number);
check('pillar 進 custom_attributes', captured && captured.body.custom_attributes.pillar === 'property', captured && captured.body.custom_attributes.pillar);
check('asset_name 進 custom_attributes', captured && captured.body.custom_attributes.asset_name === 'whitepaper_property_2026');
check('source 固定 whitepaper_download', captured && captured.body.custom_attributes.source === 'whitepaper_download');
check('UTM 有帶入', captured && captured.body.custom_attributes.utm_source === 'line');
check('LIFF 佔位有帶入', captured && captured.body.custom_attributes.liff_id === '1657-abc');
check('token 只走 server 端 header', captured && captured.headers.api_access_token === 'fake-token-for-test');

// 有 email 時用真的
captured = null;
r = await call(req('/api/whitepaper', { name: 'A', phone: '+27821234567', email: 'real@example.com', pillar: 'bank_account' }));
check('有 email 時保留真實 email', captured && captured.body.email === 'real@example.com', captured && captured.body.email);

// 驗證失敗
r = await call(req('/api/whitepaper', { name: 'A', phone: '123', pillar: 'property' }));
check('電話太短 → 400', r.status === 400, JSON.stringify(r.json));

r = await call(req('/api/whitepaper', { name: '', phone: '+886912345678' }));
check('缺稱呼 → 400', r.status === 400, JSON.stringify(r.json));

r = await call(req('/api/whitepaper', { name: 'A' }));
check('缺電話 → 400', r.status === 400, JSON.stringify(r.json));

captured = null;
r = await call(req('/api/whitepaper', { name: 'A', phone: '+886912345678', pillar: '<script>alert(1)</script>' }));
check('非法 pillar 降級 multi（防空字串污染）', r.status === 200 && captured.body.custom_attributes.pillar === 'multi', captured && captured.body.custom_attributes.pillar);

captured = null;
r = await call(req('/api/whitepaper', { name: 'A', phone: '+886912345678', utm: { evil_key: 'x', utm_source: 'fb' } }));
check('UTM 白名單（未知鍵不寫入）', captured && captured.body.custom_attributes.evil_key === undefined, JSON.stringify(captured && captured.body.custom_attributes));

r = await call(req('/api/whitepaper', null, 'POST', 'not-json{'));
check('非法 JSON → 400', r.status === 400);

r = await call(req('/api/whitepaper', null, 'GET'));
check('GET → 405', r.status === 405);

r = await call(req('/api/whitepaper', { name: 'A', phone: '+886912345678', note: 'x'.repeat(9000) }));
check('超量 payload → 413', r.status === 413, `status=${r.status}`);

mockStatus = 401;
mockBody = { error: 'Unauthorized' };
r = await call(req('/api/whitepaper', { name: 'A', phone: '+886912345678' }));
check('Chatwoot 401 → 502（不洩漏上游原文）', r.status === 502, JSON.stringify(r.json));
mockStatus = 200;
mockBody = { payload: { contact: { id: 1 } } };

// ============ 回歸：既有 /api/lead 行為不能被改壞 ============
console.log('\n--- /api/lead 回歸 ---');
r = await call(req('/api/lead', { name: 'x', custom_attributes: { source: 'lead_magnet' } }));
check('既有 /api/lead 無 email 仍回 400（行為未變）', r.status === 400 && r.json.error === 'Valid email required', JSON.stringify(r.json));

captured = null;
r = await call(req('/api/lead', { name: 'x', email: 'ok@example.com', custom_attributes: { source: 'evil_inject' } }));
check('既有 /api/lead source 降級仍生效', r.status === 200 && captured.body.custom_attributes.source === 'website', captured && captured.body.custom_attributes.source);

r = await call(req('/api/health', null, 'GET'));
check('/api/health 仍正常', r.status === 200 && r.json.chatwoot_token_configured === true);

// ============ download_url 只在驗證後回傳 ============
console.log('\n--- download_url 防護 ---');
captured = null;
r = await call(req('/api/whitepaper', { name: 'B', phone: '+886911111111', asset_name: 'whitepaper_property_2026' }));
check('驗證通過才給 download_url', r.status === 200 && typeof r.json.download_url === 'string' && r.json.download_url.endsWith('.pdf'), r.json.download_url);
check('download_url 指向 assets 網域', r.json.download_url && r.json.download_url.startsWith('https://assets.dingyaoadvisory.tw/whitepapers/'), r.json.download_url);
r = await call(req('/api/whitepaper', { name: 'B', phone: '+886911111111', asset_name: 'no_such_asset' }));
check('未知 asset 不給 download_url（回 null）', r.status === 200 && r.json.download_url === null, r.json.download_url);

const total = results.length;
const passed = results.filter(([, ok]) => ok).length;
console.log(`\n===== ${passed}/${total} passed =====`);
process.exit(passed === total ? 0 : 1);
