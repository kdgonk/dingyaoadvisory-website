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
  fetch('https://chat.dingyaoadvisory.tw/api/v1/accounts/2/contacts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'api_access_token': '3GcboBf6MgYfn54yiGJDJscb'
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
    if (data.payload && data.payload.contact) {
      if (typeof gtag === 'function') {
        gtag('event', 'generate_lead', { event_category: 'lead_magnet', event_label: source });
      } else if (window.dataLayer) {
        window.dataLayer.push({ event: 'generate_lead', event_category: 'lead_magnet', event_label: source });
      }
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
