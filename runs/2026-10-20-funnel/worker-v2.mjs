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

/** Whitepaper lead 只收這幾個 pillar，其餘一律 multi，避免自由字串污染報表 */
const WHITEPAPER_PILLARS = new Set(['bank_account', 'property', 'education', 'multi']);

/**
 * 白皮書實體位置。刻意不寫進 HTML / 前端 JS：
 * 只有通過 /api/whitepaper 驗證的請求才會拿到 download_url，
 * 避免「看原始碼就看到 PDF 連結、直接抓檔跳過表單」。
 *
 * 檔名含 8 位隨機後綴 → 無法靠猜測掃描（R2 無目錄列表權限對外）。
 * 換檔時只改這張表 + 重新上傳 R2，不用動頁面。
 */
const WHITEPAPER_ASSETS = {
  whitepaper_bank_account_2026: 'whitepapers/wp-bank-account-2026-7f3c9a21.pdf',
  whitepaper_property_2026: 'whitepapers/wp-property-2026-b84e1d06.pdf',
  whitepaper_education_2026: 'whitepapers/wp-education-2026-2c95af73.pdf',
  whitepaper_tax_residency_2026: 'whitepapers/wp-tax-residency-2026-e61d40b8.pdf'
};
const ASSET_BASE = 'https://assets.dingyaoadvisory.tw/';

/**
 * WhatsApp / 手機正規化：只留數字與開頭 +。
 * 台灣 +886912345678、南非 +27821234567、本地 0912345678 都接受。
 */
function normalizePhone(raw) {
  const s = String(raw || '').replace(/[^\d+]/g, '');
  if (s.startsWith('+')) return '+' + s.slice(1).replace(/\+/g, '');
  return s.replace(/\+/g, '');
}

function isValidPhone(digits) {
  const bare = digits.replace(/^\+/, '');
  return /^\d{8,15}$/.test(bare);
}

/**
 * 白皮書 / 名單磁鐵專用端點（3 欄表單：稱呼、WhatsApp/手機、想了解哪一塊）。
 *
 * 為什麼不共用 /api/lead：
 *   1. /api/lead 對既有 8 個頁面是 mandatory email；白皮書表單依老闆定案只有 3 欄，沒有 email。
 *   2. 改 /api/lead 的 email 驗證會動到既有頁面的既有行為（任務明文禁止）。
 *   3. 獨立端點可套用不同的速率/欄位規則，互不影響。
 *
 * 沒有 email 時如何進 Chatwoot：
 *   用 `wa+<phone>@lead.dingyaoadvisory.tw` 當識別值。這是 RFC 保留的假域名，
 *   永遠不會誤發信，但能讓同一支手機在 Chatwoot 裡是同一筆聯絡人（可去重）。
 *   若使用者之後補填 email，Chatwoot 端以 email 為主要識別再合併。
 */
async function handleWhitepaper(request, env) {
  if (!env.CHATWOOT_API_TOKEN) {
    return json({ ok: false, error: 'Server misconfigured: missing CHATWOOT_API_TOKEN' }, 500);
  }

  const declared = Number(request.headers.get('content-length') || 0);
  if (declared > MAX_BODY_BYTES) {
    return json({ ok: false, error: 'Payload too large' }, 413);
  }

  // 雙重檢查：request 可能沒帶 content-length（chunked / 中間層改寫），
  // 所以實際讀到的長度也要再擋一次。
  let raw;
  try {
    raw = await request.text();
  } catch (err) {
    return json({ ok: false, error: 'Unreadable body' }, 400);
  }
  if (raw.length > MAX_BODY_BYTES) {
    return json({ ok: false, error: 'Payload too large' }, 413);
  }

  let body;
  try {
    body = JSON.parse(raw);
  } catch (err) {
    return json({ ok: false, error: 'Invalid JSON' }, 400);
  }
  if (!body || typeof body !== 'object') {
    return json({ ok: false, error: 'Invalid JSON' }, 400);
  }

  const name = str(body.name, 120);
  if (!name) {
    return json({ ok: false, error: 'Name required' }, 400);
  }

  const phone = normalizePhone(body.phone);
  if (!isValidPhone(phone)) {
    return json({ ok: false, error: 'Valid phone required' }, 400);
  }

  const rawPillar = str(body.pillar, 40).toLowerCase();
  const pillar = WHITEPAPER_PILLARS.has(rawPillar) ? rawPillar : 'multi';
  const assetName = str(body.asset_name, 120) || 'whitepaper_unspecified';

  // email 選填：有就用真的，沒有就用 WhatsApp 合成識別
  const emailInput = str(body.email, 254);
  const email = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(emailInput)
    ? emailInput
    : `wa${phone}@lead.dingyaoadvisory.tw`;

  const utm = body.utm && typeof body.utm === 'object' ? body.utm : {};
  const custom_attributes = {
    source: 'whitepaper_download',
    pillar,
    asset_name: assetName,
    lead_channel: 'whitepaper_form'
  };

  // UTM 只收白名單鍵，且截斷長度，避免被塞長字串
  for (const k of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'liff_id', 'line_oa_id', 'ref_pillar', 'ref_asset']) {
    const v = str(utm[k], 200);
    if (v) custom_attributes[k] = v;
  }
  if (utm.landing_page) custom_attributes.landing_page = str(utm.landing_page, 300);

  const payload = {
    inbox_id: INBOX_ID,
    name,
    email,
    phone_number: phone,
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
    const detail = str((data && (data.message || data.error)) || '', 200);
    return json({ ok: false, error: detail || 'Chatwoot rejected the request', upstream_status: res.status }, res.status === 401 ? 502 : res.status);
  }

  const contact = data && data.payload ? data.payload.contact : null;
  // download_url 只在驗證通過後才組出來，前端原始碼裡看不到 PDF 路徑
  const downloadUrl = WHITEPAPER_ASSETS[assetName]
    ? ASSET_BASE + WHITEPAPER_ASSETS[assetName]
    : null;
  return json({ ok: true, contact: contact || null, pillar, asset_name: assetName, download_url: downloadUrl });
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

    if (path === '/api/whitepaper') {
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
      return handleWhitepaper(request, env);
    }

    if (path === '/api/health') {
      return json({ ok: true, chatwoot_token_configured: Boolean(env.CHATWOOT_API_TOKEN) });
    }

    return env.ASSETS.fetch(request);
  }
};
