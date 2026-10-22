function submitLmForm(e, source) {
  e.preventDefault();
  var form = e.target;
  var email = form.querySelector('#lmEmail').value.trim();
  var name = form.querySelector('#lmName').value.trim() || '未具名（Lead Magnet）';
  var interest = form.querySelector('#lmInterest').value;
  var consent = form.querySelector('#lmConsent');
  if (!email) { alert('請填寫 Email，我們才能把檔案寄給您。'); return false; }
  if (consent && !consent.checked) { alert('請先勾選同意條款，我們才能寄送給您。'); return false; }
  var btn = form.querySelector('button[type="submit"]');
  var label = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 送出中...';
  fetch('/api/lead', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      inbox_id: 2,
      name: name,
      email: email,
      custom_attributes: {
        source: source || 'lead_magnet',
        interest: interest || '',
        lm_consent: 'granted (checkbox checked at submit)'
      }
    })
  })
  .then(function(res){ return res.json(); })
  .then(function(data){
    if (data.ok || (data.payload && data.payload.contact)) {
      if (typeof gtag === 'function') {
        gtag('event', 'generate_lead', { event_category: 'lead_magnet', event_label: source });
      } else if (window.dataLayer) {
        window.dataLayer.push({ event: 'generate_lead', event_category: 'lead_magnet', event_label: source });
      }
      // 2026-10-22：GA4 在 analytics_storage=denied（訪客沒點 cookie 同意）時會丟掉
      // generate_lead，導致「表單明明送出成功、GA4 轉換卻是 0」。Plausible 是
      // cookieless，同一個轉換在 Plausible 一律記得到，兩邊對照就不會再誤判掉單。
      try {
        if (typeof window.plausible === 'function') {
          window.plausible('generate_lead', { props: { source: source || 'lead_magnet' } });
        }
      } catch (e) {}
      form.style.display = 'none';
      document.getElementById('lmSuccess').style.display = 'block';
    } else { throw new Error(data.error || '建立聯絡人失敗'); }
  })
  .catch(function(err){
    btn.disabled = false;
    btn.innerHTML = label;
    alert('送出失敗，請稍後再試或來信 info@dingyaoadvisory.tw');
  });
  return false;
}
