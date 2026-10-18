/**
 * dingyao Worker — static assets + server-side Chatwoot proxy.
 *
 * 為什麼存在：2026-10-19 前 dist/js/lm-form.js 與 8 個頁面的行內 script
 * 直接以 `api_access_token: '...'` 呼叫 Chatwoot，等於把 administrator
 * 的 API token 公開在 HTML 原始碼（任何人可讀 15 筆聯絡人）。本 Worker
 * 讓瀏覽器只打自家同源端點 /api/lead，token 只存在於 Worker secret
 * （env.CHATWOOT_API_TOKEN），永不進前端、永不進 repo。
 */

const CHATWOOT_CONTACTS = 'https://chat.dingyaoadvisory.tw/api/v1/accounts/2/contacts';
const INBOX_ID = 2;
const MAX_BODY_BYTES = 8192;

// 只允許官網實際會送出的來源值，其他一律降級為 website，
// 避免 proxy 被當成任意寫入 Chatwoot 的跳板。
const ALLOWED_SOURCES = new Set([
  'home_page',
  'contact_page',
  'contact_page_en',
  'consultation_page',
  'lead_magnet',
  'tour_page',
  'website'
]);

const JSON_HEADERS = { 'Content-Type': 'application/json; charset=utf-8' };

function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
}

function str(value, max = 500) {
  if (value === undefined || value === null) return '';
  return String(value).trim().slice(0, max);
}

function normalizeSource(source) {
  const s = str(source, 40).toLowerCase();
  if (!s) return 'website';
  if (ALLOWED_SOURCES.has(s)) return s;
  // Lead magnet 有多個檔案（lm_allocation_guide / lm_passport_checklist ...）
  if (/^lm_[a-z0-9_]{1,37}$/.test(s)) return s;
  return 'website';
}

async function handleLead(request, env) {
  if (!env.CHATWOOT_API_TOKEN) {
    return json({ ok: false, error: 'Server misconfigured: missing CHATWOOT_API_TOKEN' }, 500);
  }

  const declared = Number(request.headers.get('content-length') || 0);
  if (declared > MAX_BODY_BYTES) {
    return json({ ok: false, error: 'Payload too large' }, 413);
  }

  let body;
  try {
    body = await request.json();
  } catch (err) {
    return json({ ok: false, error: 'Invalid JSON' }, 400);
  }
  if (!body || typeof body !== 'object') {
    return json({ ok: false, error: 'Invalid JSON' }, 400);
  }

  const email = str(body.email, 254);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return json({ ok: false, error: 'Valid email required' }, 400);
  }

  const incoming = (body.custom_attributes && typeof body.custom_attributes === 'object')
    ? body.custom_attributes
    : {};

  const custom_attributes = { source: normalizeSource(incoming.source) };
  for (const key of ['budget', 'interest', 'message', 'plan', 'note', 'lm_consent']) {
    const value = str(incoming[key], 1000);
    if (value) custom_attributes[key] = value;
  }

  const payload = {
    inbox_id: INBOX_ID,
    name: str(body.name, 120) || '未具名（官網表單）',
    email,
    phone_number: str(body.phone_number, 40),
    custom_attributes
  };

  let res;
  try {
    res = await fetch(CHATWOOT_CONTACTS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api_access_token': env.CHATWOOT_API_TOKEN
      },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    return json({ ok: false, error: 'Upstream unreachable' }, 502);
  }

  let data = {};
  try {
    data = await res.json();
  } catch (err) {
    data = {};
  }

  if (!res.ok) {
    // 不把上游原始錯誤訊息整包外洩，只回狀態碼與短訊息
    const detail = str((data && (data.message || data.error)) || '', 200);
    return json({ ok: false, error: detail || 'Chatwoot rejected the request', upstream_status: res.status }, res.status === 401 ? 502 : res.status);
  }

  const contact = data && data.payload ? data.payload.contact : null;
  return json({ ok: true, contact: contact || null });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '') || '/';

    if (path === '/api/lead') {
      if (request.method === 'OPTIONS') {
        return new Response(null, {
          status: 204,
          headers: {
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
          }
        });
      }
      if (request.method !== 'POST') {
        return json({ ok: false, error: 'Method not allowed' }, 405);
      }
      return handleLead(request, env);
    }

    if (path === '/api/health') {
      return json({ ok: true, chatwoot_token_configured: Boolean(env.CHATWOOT_API_TOKEN) });
    }

    return env.ASSETS.fetch(request);
  }
};
