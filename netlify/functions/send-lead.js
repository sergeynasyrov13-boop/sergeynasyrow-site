// Server-side proxy for the contact form.
//
// Data flow (for 152-ФЗ data localization compliance):
//   1. Primary record: written to Yandex Object Storage (RF-based) FIRST.
//   2. Secondary notification: forwarded to Telegram for convenience.
// Both destinations get their credentials from Netlify environment
// variables — nothing is ever hardcoded in this file.

const crypto = require('crypto');

const YC_REGION = 'ru-central1';
const YC_SERVICE = 's3';
const YC_HOST = 'storage.yandexcloud.net';

function hmac(key, msg) {
  return crypto.createHmac('sha256', key).update(msg, 'utf8').digest();
}

function signingKey(secretAccessKey, dateStamp) {
  const kDate = hmac('AWS4' + secretAccessKey, dateStamp);
  const kRegion = hmac(kDate, YC_REGION);
  const kService = hmac(kRegion, YC_SERVICE);
  return hmac(kService, 'aws4_request');
}

// Minimal hand-rolled AWS SigV4 PUT, no SDK dependency.
// Yandex Object Storage is S3-compatible and accepts this signing scheme.
async function putToYandexStorage({ accessKeyId, secretAccessKey, bucket, key, body }) {
  const amzDate = new Date().toISOString().replace(/[:-]|\.\d{3}/g, '');
  const dateStamp = amzDate.slice(0, 8);
  const payloadHash = crypto.createHash('sha256').update(body).digest('hex');
  const host = `${bucket}.${YC_HOST}`;

  const canonicalHeaders = `host:${host}\nx-amz-content-sha256:${payloadHash}\nx-amz-date:${amzDate}\n`;
  const signedHeaders = 'host;x-amz-content-sha256;x-amz-date';
  const canonicalRequest = ['PUT', `/${key}`, '', canonicalHeaders, signedHeaders, payloadHash].join('\n');

  const credentialScope = `${dateStamp}/${YC_REGION}/${YC_SERVICE}/aws4_request`;
  const stringToSign = [
    'AWS4-HMAC-SHA256',
    amzDate,
    credentialScope,
    crypto.createHash('sha256').update(canonicalRequest).digest('hex'),
  ].join('\n');

  const signature = crypto.createHmac('sha256', signingKey(secretAccessKey, dateStamp)).update(stringToSign, 'utf8').digest('hex');
  const authorization = `AWS4-HMAC-SHA256 Credential=${accessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;

  return fetch(`https://${host}/${key}`, {
    method: 'PUT',
    headers: {
      Host: host,
      'x-amz-date': amzDate,
      'x-amz-content-sha256': payloadHash,
      Authorization: authorization,
      'Content-Type': 'application/json',
    },
    body,
  });
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const ycKeyId = process.env.YC_ACCESS_KEY_ID;
  const ycSecret = process.env.YC_SECRET_ACCESS_KEY;
  const ycBucket = process.env.YC_BUCKET;
  const tgToken = process.env.TELEGRAM_BOT_TOKEN;
  const tgChatId = process.env.TELEGRAM_CHAT_ID;

  if (!ycKeyId || !ycSecret || !ycBucket || !tgToken || !tgChatId) {
    return { statusCode: 500, body: 'Server is not configured' };
  }

  let payload;
  try {
    payload = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, body: 'Invalid JSON' };
  }

  const clean = (v) => String(v ?? '—').slice(0, 500).trim() || '—';
  const name = clean(payload.name);
  const task = clean(payload.task);
  const contact = clean(payload.contact);
  const submittedAt = new Date().toISOString();

  // 1. Primary record — RF-based storage, written first.
  const objectKey = `leads/${submittedAt.replace(/[:.]/g, '-')}-${crypto.randomUUID()}.json`;
  try {
    const putRes = await putToYandexStorage({
      accessKeyId: ycKeyId,
      secretAccessKey: ycSecret,
      bucket: ycBucket,
      key: objectKey,
      body: JSON.stringify({ name, task, contact, submittedAt }),
    });
    if (!putRes.ok) {
      return { statusCode: 502, body: 'Storage write failed' };
    }
  } catch {
    return { statusCode: 502, body: 'Failed to reach storage' };
  }

  // 2. Secondary notification — Telegram, best-effort.
  const escapeHtml = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const text = `📩 <b>Новая заявка с сайта</b>\n\n👤 <b>Имя:</b> ${escapeHtml(name)}\n📋 <b>Задача:</b> ${escapeHtml(task)}\n📞 <b>Контакт:</b> ${escapeHtml(contact)}`;
  try {
    await fetch(`https://api.telegram.org/bot${tgToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: tgChatId, text, parse_mode: 'HTML' }),
    });
  } catch {
    // Lead is already safely recorded in RF storage — a failed Telegram
    // ping is not worth failing the whole request over.
  }

  return { statusCode: 200, body: 'OK' };
};
