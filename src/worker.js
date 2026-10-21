/**
 * dingyao Worker — static assets + server-side Chatwoot proxy.
 *
 * 為什麼存在：2026-10-19 前 dist/js/lm-form.js 與 8 個頁面的行內 script
 * 直接以 `api_access_token: '...'` 呼叫 Chatwoot，等於把 administrator
 * 的 API token 公開在 HTML 原始碼（任何人可讀 15 筆聯絡人）。本 Worker
 * 讓瀏覽器只打自家同源端點 /api/lead，token 只存在於 Worker secret
 * （env.CHATWOOT_API_TOKEN），永不進前端、永不進 repo。
 */

const CHATWOOT_BASE = 'https://chat.dingyaoadvisory.tw/api/v1/accounts/2';
const CHATWOOT_CONTACTS = CHATWOOT_BASE + '/contacts';
const CHATWOOT_CONVERSATIONS = CHATWOOT_BASE + '/conversations';
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

/**
 * 在 Chatwoot 找既有聯絡人。
 *
 * 為什麼需要：Chatwoot 對 phone_number 有唯一性限制，重複 create 會回
 * 422 "Phone number has already been taken"。原版直接把 422 傳回前端，
 * 造成「同一支電話第二次諮詢必定失敗」——回訪客戶全掉單，而且
 * GA4 的 generate_lead 只在成功時觸發，所以從數據完全看不出來。
 *
 * 先用 email 搜（Chatwoot 的 search 是跨欄位模糊比對），
 * 沒中就再用電話搜；兩者都比對到完全相同才視為同一人。
 */
async function findContact(env, email, phone) {
  const headers = { 'api_access_token': env.CHATWOOT_API_TOKEN };
  const queries = [];
  if (email) queries.push(email);
  if (phone) queries.push(phone.replace(/^\+/, ''));

  for (const q of queries) {
    let res;
    try {
      res = await fetch(
        CHATWOOT_CONTACTS + '/search?q=' + encodeURIComponent(q),
        { headers }
      );
    } catch (err) {
      continue;  // 搜尋失敗不阻斷流程，往下走 create
    }
    if (!res.ok) continue;

    let data = {};
    try {
      data = await res.json();
    } catch (err) {
      continue;
    }

    const list = Array.isArray(data && data.payload) ? data.payload : [];
    for (const c of list) {
      const cEmail = str(c.email, 254).toLowerCase();
      const cPhone = str(c.phone_number, 40).replace(/^\+/, '');
      if ((email && cEmail && cEmail === email.toLowerCase()) ||
          (phone && cPhone && cPhone === phone.replace(/^\+/, ''))) {
        return c;
      }
    }
  }
  return null;
}

/**
 * 建一筆新 conversation。
 *
 * 原本只 create contact，Chatwoot 不會自動開對話，等於名單進來卻沒有
 * 任何一筆待處理的諮詢；upsert 之後每次送出都留一筆 conversation，
 * 業務端才看得到「這個人今天又問了一次」。
 */
async function createConversation(env, contactId, message) {
  const content = str(message, 1000) || '（官網表單送出，未填訊息）';
  let res;
  try {
    res = await fetch(CHATWOOT_CONVERSATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api_access_token': env.CHATWOOT_API_TOKEN
      },
      body: JSON.stringify({
        source_id: 'lead-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8),
        inbox_id: INBOX_ID,
        contact_id: contactId,
        status: 'open',
        message: { content }
      })
    });
  } catch (err) {
    return { ok: false, reason: 'unreachable' };
  }
  if (!res.ok) {
    return { ok: false, reason: 'status_' + res.status };
  }
  let data = {};
  try {
    data = await res.json();
  } catch (err) {
    data = {};
  }
  return { ok: true, id: (data && data.id) || null };
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

  // ── upsert：先找既有聯絡人，避免 422 "Phone number has already been taken" ──
  const existing = await findContact(env, email, payload.phone_number);

  let res;
  try {
    if (existing) {
      // 命中就更新。custom_attributes 用合併，不覆蓋掉前一次的 interest/budget，
      // 這樣業務端看得到完整的諮詢軌跡（這次問 education、上次問 bank）。
      const merged = Object.assign({}, existing.custom_attributes || {}, custom_attributes);
      res = await fetch(CHATWOOT_CONTACTS + '/' + existing.id, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'api_access_token': env.CHATWOOT_API_TOKEN
        },
        body: JSON.stringify({
          name: payload.name,
          email: payload.email,
          phone_number: payload.phone_number,
          custom_attributes: merged
        })
      });
    } else {
      res = await fetch(CHATWOOT_CONTACTS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api_access_token': env.CHATWOOT_API_TOKEN
        },
        body: JSON.stringify(payload)
      });
    }
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

  // PUT 回傳的是 contact 物件本身；POST 回傳的是 {payload:{contact}}。兩種都要吃。
  const contact = (data && data.payload && data.payload.contact)
    || (data && data.id ? data : null)
    || existing
    || null;
  const contactId = contact && contact.id ? contact.id : (existing && existing.id) || null;

  // 每次送出都開一筆新 conversation。contact 只是名單，conversation 才是
  // 業務端 inbox 裡看得到的「有人來問」。
  let conversation = null;
  if (contactId) {
    conversation = await createConversation(env, contactId, custom_attributes.message);
  }

  return json({
    ok: true,
    matched_existing: Boolean(existing),
    contact: contact || null,
    conversation
  });
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
