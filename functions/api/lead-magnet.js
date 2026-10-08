export async function onRequestPost(context) {
  const { request, env } = context;
  const body = await request.json();
  const { email, name, interest, source } = body;

  if (!email) {
    return new Response(JSON.stringify({ error: 'Email required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }

  const token = env.CHATWOOT_API_TOKEN;
  if (!token) {
    return new Response(JSON.stringify({ error: 'Server misconfigured: missing CHATWOOT_API_TOKEN' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }

  const payload = {
    inbox_id: 2,
    name: name || '未具名（Lead Magnet）',
    email: email,
    custom_attributes: {
      source: source || 'lead_magnet',
      interest: interest || '',
      lm_consent: 'granted (checkbox checked at submit)'
    }
  };

  try {
    const chatwootRes = await fetch('https://chat.dingyaoadvisory.tw/api/v1/accounts/2/contacts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api_access_token': token
      },
      body: JSON.stringify(payload)
    });

    const chatwootData = await chatwootRes.json();

    if (!chatwootRes.ok) {
      return new Response(JSON.stringify(chatwootData), {
        status: chatwootRes.status,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }

    return new Response(JSON.stringify({
      ok: true,
      contact: chatwootData.payload ? chatwootData.payload.contact : chatwootData
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
