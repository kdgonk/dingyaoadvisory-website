/**
 * dy-funnel.js — 鼎曜四層漏斗 dataLayer 實作
 * ------------------------------------------------------------------
 * 目標：讓 GA4 (G-4H4T55YXB0) 能按 pillar 拉出 L1→L2→L3→L4 轉換率。
 *
 * 設計原則
 *  1. 零侵入：不覆寫任何既有函式；既有頁面不加此檔就不受影響。
 *  2. 單一真相：所有事件共用同一份 attribution（UTM / click id / LINE）。
 *  3. 前端只負責 push，GTM 負責送 GA4（容器目前 0 個 event tag）。
 *  4. Consent Mode v2 由頁面既有 gtag('consent') 控管，本檔不碰 consent。
 *
 * 掛法：<script src="/js/dy-funnel.js" defer></script>
 *       <body data-pillar="property">   ← 選用，預設由 pathname 推導
 */
(function () {
  'use strict';

  var VERSION = '1.0.0';
  var DL = (window.dataLayer = window.dataLayer || []);
  var ATTR_KEY = 'dy_attr_v1';
  var SESSION_KEY = 'dy_sess_v1';

  /* ================================================================
   * 0. 小工具
   * ============================================================== */
  function push(obj) {
    DL.push(obj);
  }

  function readStore(store, key) {
    try {
      var raw = store.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeStore(store, key, val) {
    try {
      store.setItem(key, JSON.stringify(val));
    } catch (e) {
      /* private mode / quota — 靜默失敗，事件仍會送出但無 attribution */
    }
  }

  function nowIso() {
    return new Date().toISOString();
  }

  /* ================================================================
   * 1. Attribution：UTM + click id + LINE 佔位（第一階段就存起來）
   * ================================================================
   * 為什麼要在第一秒存：
   *   LINE / WhatsApp 導流會把參數吃掉（in-app browser 轉址、LIFF 重導），
   *   等到 L3 表單送出時 URL 已經沒有 utm_*。先在落地頁抓下來存
   *   sessionStorage，後面 L1-L4 每一層都帶同一組值，歸因才不會斷。
   */
  var PARAM_MAP = {
    utm_source: 'utm_source',
    utm_medium: 'utm_medium',
    utm_campaign: 'utm_campaign',
    utm_content: 'utm_content',
    utm_term: 'utm_term',
    gclid: 'gclid',
    fbclid: 'fbclid',
    // ↓ LINE 專用：帳號上線後 OA 推廣連結會帶這兩個，先預留
    liff_id: 'liff_id',        // 例：1657xxxxxx-xxxxxxxx
    line_oa_id: 'line_oa_id',  // 例：@dingyao
    // ↓ 內部用：哪一個 pillar / 白皮書把人帶進來（火星人放連結時填）
    ref_pillar: 'ref_pillar',
    ref_asset: 'ref_asset'
  };

  function captureAttribution() {
    var qs;
    try {
      qs = new URLSearchParams(window.location.search);
    } catch (e) {
      qs = null;
    }
    if (!qs) return readStore(window.sessionStorage, ATTR_KEY) || {};

    var stored = readStore(window.sessionStorage, ATTR_KEY) || {};
    var incoming = {};
    var hasNew = false;

    for (var q in PARAM_MAP) {
      if (!Object.prototype.hasOwnProperty.call(PARAM_MAP, q)) continue;
      var v = qs.get(q);
      if (v) {
        incoming[PARAM_MAP[q]] = String(v).slice(0, 200);
        hasNew = true;
      }
    }

    // 首次帶參數進站 → 覆寫（last-touch 進站）；沒帶參數 → 沿用舊的
    var attr;
    if (hasNew) {
      attr = incoming;
      attr.landing_page = window.location.pathname;
      attr.captured_at = nowIso();
      writeStore(window.sessionStorage, ATTR_KEY, attr);
    } else {
      attr = stored;
    }
    return attr || {};
  }

  /* ================================================================
   * 2. Pillar 判定
   * ================================================================
   * 三個支柱的代碼是固定的，GA4 端靠這個值做維度切分：
   *   bank_account = 南非銀行開戶
   *   property     = 南非置產
   *   education    = 教育留學
   * 頁面可用 <body data-pillar="property"> 覆寫，否則由路徑推導。
   */
  var PILLAR_BY_PATH = {
    '/south-africa-bank-account': 'bank_account',
    '/south-africa-bank-account-en': 'bank_account',
    '/south-africa-property': 'property',
    '/south-africa-property-en': 'property',
    '/education': 'education',
    '/education-en': 'education',
    // 次要入口：漏斗中段頁，pillar 由 data-pillar 或 ref_pillar 決定
    '/consultation': 'multi',
    '/consultation-en': 'multi',
    '/assets': 'multi',
    '/assets-en': 'multi'
  };

  function resolvePillar() {
    var override = document.body && document.body.getAttribute('data-pillar');
    if (override) return override;

    var p = window.location.pathname.replace(/\/+$/, '') || '/';
    if (PILLAR_BY_PATH[p]) return PILLAR_BY_PATH[p];

    // 不在對照表 → 用進站時記錄的 ref_pillar，最後才 unknown
    var attr = readStore(window.sessionStorage, ATTR_KEY);
    if (attr && attr.ref_pillar) return attr.ref_pillar;
    return 'unknown';
  }

  /* ================================================================
   * 3. Session 標記：讓 GA4 能把同一次造訪的 L1-L4 串起來
   * ================================================================ */
  function sessionId() {
    var s = readStore(window.sessionStorage, SESSION_KEY);
    if (s && s.id) return s.id;
    var id = 's_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
    writeStore(window.sessionStorage, SESSION_KEY, { id: id, started_at: nowIso() });
    return id;
  }

  /* ================================================================
   * 4. 事件共通 payload
   * ================================================================
   * 每一層都帶同樣的 attribution + pillar，GA4 才能交叉分析
   * 「同一個 pillar 從 L1 到 L4 掉在哪一層」。
   */
  function baseParams(extra) {
    var attr = captureAttribution(); // 每次呼叫都重讀，容忍中途帶參數進來
    var out = {
      dy_funnel_version: VERSION,
      dy_session_id: sessionId(),
      pillar: resolvePillar(),
      page_path: window.location.pathname,
      page_lang: /\-en$/.test(window.location.pathname) ? 'en' : 'zh'
    };

    // attribution（有才帶，避免 GA4 出現空維度）
    var attrKeys = [
      'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
      'gclid', 'fbclid', 'liff_id', 'line_oa_id', 'ref_pillar', 'ref_asset',
      'landing_page'
    ];
    for (var i = 0; i < attrKeys.length; i++) {
      var k = attrKeys[i];
      if (attr[k]) out[k] = attr[k];
    }

    if (extra) {
      for (var e in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, e) && extra[e] !== undefined && extra[e] !== null) {
          out[e] = extra[e];
        }
      }
    }
    return out;
  }

  /* ================================================================
   * L1 — view_service_page
   * ================================================================
   * 觸發：服務頁載入完成（三個支柱頁 + 白皮書頁）
   * 去重：同一 session 同一 pillar 只送一次，避免 SPA 式返回重複計數
   */
  var L1_SENT_KEY = 'dy_l1_sent';
  var L1_PILLARS = { bank_account: 1, property: 1, education: 1 };

  function trackViewServicePage() {
    var pillar = resolvePillar();
    if (!L1_PILLARS[pillar]) return; // 只在三支柱頁送 L1

    var sent = readStore(window.sessionStorage, L1_SENT_KEY) || {};
    if (sent[pillar]) return; // 本 session 已送過
    sent[pillar] = 1;
    writeStore(window.sessionStorage, L1_SENT_KEY, sent);

    var payload = baseParams({ event_category: 'funnel_l1', service_pillar: pillar });
    payload.event = 'view_service_page';
    push(payload);
  }

  /* ================================================================
   * L2 — cta_click
   * ================================================================
   * 觸發：點擊帶 data-cta-id 的元素，或三個支柱頁上的主 CTA。
   * 參數：cta_id / cta_location / pillar / cta_text
   *
   * 標記方式（火星人寫頁面時照這個加）：
   *   <a href="/consultation" data-cta-id="hero_primary"
   *      data-cta-location="hero">預約免費評估</a>
   *
   * cta_location 建議值：hero / mid_section / bottom_cta / sticky_bar / nav / faq
   */
  var CTA_FALLBACK_SELECTOR = [
    'a[href^="/consultation"]',
    'a[href*="consultation"]',
    '.btn-primary',
    '.cta-button'
  ].join(',');

  function ctaInfo(el) {
    var node = el.closest('[data-cta-id]');
    if (node) {
      return {
        cta_id: node.getAttribute('data-cta-id') || 'unnamed',
        cta_location: node.getAttribute('data-cta-location') || 'unspecified',
        cta_text: (node.textContent || '').trim().slice(0, 60)
      };
    }
    node = el.closest(CTA_FALLBACK_SELECTOR);
    if (node) {
      return {
        // 沒標記 → 用 href 推導，保證不空
        cta_id: 'auto_' + (node.getAttribute('href') || 'unknown').replace(/[^a-z0-9]+/gi, '_'),
        cta_location: 'untagged',
        cta_text: (node.textContent || '').trim().slice(0, 60)
      };
    }
    return null;
  }

  function bindCtaClick() {
    document.addEventListener(
      'click',
      function (e) {
        var t = e.target;
        if (!t || !t.closest) return;
        var info = ctaInfo(t);
        if (!info) return;

        var payload = baseParams({
          event_category: 'funnel_l2',
          cta_id: info.cta_id,
          cta_location: info.cta_location,
          cta_text: info.cta_text
        });
        payload.event = 'cta_click';
        push(payload);
        // 不 preventDefault、不延遲導航 —— L2 絕不可影響使用者體驗
      },
      true
    );
  }

  /* ================================================================
   * L3 — lead_submit
   * ================================================================
   * 觸發（三種來源）：
   *   a) 白皮書表單送出成功 → dyFunnel.lead({asset_name:'whitepaper_xxx'})
   *   b) 試算器完成計算     → dyFunnel.lead({asset_name:'calculator_xxx', calc_done:1})
   *   c) 既有 lm-form 成功   → 本檔以 MutationObserver 偵測 #lmSuccess 顯示（零侵入備援）
   *
   * 參數：pillar / asset_name / lead_type / form_id
   */
  var L3_SENT_KEY = 'dy_l3_sent';

  function trackLead(opts) {
    opts = opts || {};
    var payload = baseParams({
      event_category: 'funnel_l3',
      lead_type: opts.lead_type || 'form',
      asset_name: opts.asset_name || 'none',
      form_id: opts.form_id || 'none',
      calculator_step: opts.calculator_step || undefined,
      // 表單可指定 pillar（例：白皮書頁面本身是 multi，但使用者選了 property）
      // baseParams 會跳過 undefined，所以沒指定時仍用頁面推導值
      pillar: opts.pillar || undefined
    });
    payload.event = 'lead_submit';

    // 同一 session 同一 asset 只算一次轉換（避免重送/重試造成重複計算）
    var key = payload.pillar + '|' + payload.asset_name;
    var sent = readStore(window.sessionStorage, L3_SENT_KEY) || {};
    if (!sent[key]) {
      sent[key] = 1;
      writeStore(window.sessionStorage, L3_SENT_KEY, sent);
    }
    payload.first_submit_in_session = !sent[key] ? 1 : 0;

    push(payload);

    // L3 成功通常代表「同一段對話」，順手標記，L4 才知道來源
    writeStore(window.sessionStorage, 'dy_l3_meta', {
      pillar: payload.pillar,
      asset_name: payload.asset_name,
      at: nowIso()
    });
  }

  // 既有 lm-form.js 零侵入備援：它成功時會把 #lmSuccess 設為 display:block
  function observeLegacyLeadForm() {
    var target = document.getElementById('lmSuccess');
    if (!target) return;
    if (typeof MutationObserver === 'undefined') return;

    var mo = new MutationObserver(function () {
      if (target.style.display === 'block') {
        var form = document.getElementById('lmForm') || document.querySelector('form');
        var source = 'legacy_lm_form';
        if (form && form.getAttribute('data-asset')) {
          source = form.getAttribute('data-asset');
        }
        trackLead({ lead_type: 'lead_magnet', asset_name: source, form_id: 'lmForm' });
        mo.disconnect();
      }
    });
    mo.observe(target, { attributes: true, attributeFilter: ['style'] });
  }

  /* ================================================================
   * L4 — booking_confirmed
   * ================================================================
   * 「30 分鐘顧問評估預約成立」這件事，前端只有在預約流程結束後才知道。
   * 三種落地方式，本檔支援前兩種，第三種需後端：
   *
   *   1) 預約完成頁（建議）：Calendly / Chatwoot / n8n 預約成功後導向
   *      /booking-confirmed?booking=1&slot=<時間>
   *      → 本檔偵測到即送 L4
   *
   *   2) 預約 widget 回呼：外部服務 JS 觸發 window.dyFunnel.booking({...})
   *
   *   3) webhook 後端送 Measurement Protocol（真正權威來源）
   *      → 需 GTM server-side container 或直接打 GA4 MP API，屬第二階段
   *
   * 注意：L4 是「營收級」事件，不可用前端猜測。若無明確確認訊號就不要送。
   */
  var L4_PATHS = ['/booking-confirmed', '/booking-confirmed-en', '/consultation-confirmed'];

  function trackBookingConfirmed(opts) {
    opts = opts || {};
    var l3 = readStore(window.sessionStorage, 'dy_l3_meta') || {};
    push({
      event: 'booking_confirmed',
      event_category: 'funnel_l4',
      pillar: opts.pillar || l3.pillar || resolvePillar(),
      booking_ref: opts.booking_ref || 'unknown',
      booking_source: opts.booking_source || 'confirmation_page',
      booking_slot: opts.booking_slot || undefined,
      origin_asset: l3.asset_name || 'none',
      dy_session_id: sessionId(),
      dy_funnel_version: VERSION
    });
  }

  function detectBookingPage() {
    var p = window.location.pathname.replace(/\/+$/, '');
    if (L4_PATHS.indexOf(p) === -1) return;

    var qs = new URLSearchParams(window.location.search);
    // 必須有明確確認參數，避免直接開頁面誤判成預約成立
    var confirmed = qs.get('booking') === '1' || qs.get('confirmed') === '1';
    if (!confirmed) return;

    trackBookingConfirmed({
      booking_ref: qs.get('ref') || 'unknown',
      booking_source: qs.get('src') || 'confirmation_page',
      booking_slot: qs.get('slot') || undefined
    });
  }

  /* ================================================================
   * 公開 API
   * ================================================================ */
  window.dyFunnel = {
    version: VERSION,
    lead: trackLead,
    booking: trackBookingConfirmed,
    view: trackViewServicePage,
    attr: captureAttribution,
    pillar: resolvePillar,
    // 手動補送（例如 SPA 換頁後）
    pageview: function (opts) {
      opts = opts || {};
      push(
        Object.assign(baseParams({ event_category: 'funnel_l1' }), {
          event: 'view_service_page',
          service_pillar: opts.pillar || resolvePillar()
        })
      );
    }
  };

  /* ================================================================
   * 初始化
   * ================================================================ */
  function init() {
    captureAttribution();
    trackViewServicePage();
    bindCtaClick();
    detectBookingPage();
    observeLegacyLeadForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
