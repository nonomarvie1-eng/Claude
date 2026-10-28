// Webhook Stripe : quand un paiement est réussi, (1) baisse le stock, (2) envoie un e-mail de commande à Mme Fofana.
// Variables Netlify nécessaires : STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET (whsec_...), RESEND_API_KEY, ORDER_EMAIL, et (facultatif) SENDCLOUD_PUBLIC_KEY, SENDCLOUD_SECRET_KEY.
// Étapes : (1) baisse le stock, (2) e-mail de commande, (3) crée le colis dans Sendcloud.
const crypto = require('crypto');
const { api } = require('./lib/stripe');

const ok = (b) => ({ statusCode: 200, body: b || 'ok' });

function verify(raw, header, secret) {
  if (!header || !secret) return false;
  const parts = Object.fromEntries(header.split(',').map((p) => p.split('=')));
  const t = parts.t;
  const sigs = header.split(',').filter((p) => p.startsWith('v1=')).map((p) => p.slice(3));
  if (!t || !sigs.length) return false;
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return false;
  const expected = crypto.createHmac('sha256', secret).update(t + '.' + raw).digest('hex');
  return sigs.some((s) => s.length === expected.length && crypto.timingSafeEqual(Buffer.from(s), Buffer.from(expected)));
}

const eur = (c) => (c / 100).toFixed(2).replace('.', ',') + ' €';
const esc = (x) => String(x == null ? '' : x).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

async function sendMail(session, items) {
  const key = process.env.RESEND_API_KEY, to = process.env.ORDER_EMAIL;
  if (!key || !to) { console.log('E-mail non envoyé : RESEND_API_KEY ou ORDER_EMAIL manquant'); return; }
  const cd = session.customer_details || {};
  const sd = session.shipping_details || (session.collected_information && session.collected_information.shipping_details) || {};
  const ad = sd.address || cd.address || {};
  const md = session.metadata || {};
  const relay = (session.custom_fields || []).find((f) => f.key === 'point_relais');
  const relayTxt = relay && relay.text && relay.text.value;
  const ship = session.shipping_cost ? session.shipping_cost.amount_total : 0;
  const lines = items.map((i) => `${i.quantity} × ${i.description} — ${eur(i.amount_total)}`);
  const addr = [sd.name || cd.name, ad.line1, ad.line2, [ad.postal_code, ad.city].filter(Boolean).join(' '), ad.country].filter(Boolean);
  const mode = md.livraison === 'domicile' ? 'À domicile' : 'Point Relais';
  const text = [
    `Nouvelle commande — ${eur(session.amount_total)}`, '',
    'Produits :', ...lines, '',
    `Livraison : ${mode} (${eur(ship)})`,
    relayTxt ? `Point Relais indiqué : ${relayTxt}` : '', '',
    'Client :', cd.name || '', cd.email || '', cd.phone || '', '',
    'Adresse :', ...addr, '',
    `Poids estimé du colis : ${md.poids_g || '?'} g`,
  ].filter((l) => l !== undefined).join('\n');
  const html = `<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222"><h2 style="margin:0 0 8px">Nouvelle commande — ${eur(session.amount_total)}</h2><p><b>Produits</b><br>${lines.map(esc).join('<br>')}</p><p><b>Livraison</b> : ${mode} (${eur(ship)})${relayTxt ? '<br><b>Point Relais indiqué</b> : ' + esc(relayTxt) : ''}</p><p><b>Client</b><br>${esc(cd.name)}<br>${esc(cd.email)}<br>${esc(cd.phone)}</p><p><b>Adresse</b><br>${addr.map(esc).join('<br>')}</p><p style="color:#777">Poids estimé du colis : ${esc(md.poids_g || '?')} g</p></div>`;
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: 'La Boutique de Mme Fofana <onboarding@resend.dev>', to: [to], subject: `Nouvelle commande — ${eur(session.amount_total)}`, text, html, reply_to: cd.email || undefined }),
  });
  if (!r.ok) console.log('Resend a refusé l\'e-mail :', r.status, await r.text());
}

// Crée le colis dans Sendcloud (SANS étiquette : Mme Fofana vérifie, choisit Mondial Relay et génère l'étiquette dans Sendcloud).
// Variables Netlify : SENDCLOUD_PUBLIC_KEY, SENDCLOUD_SECRET_KEY. Si elles manquent, cette étape est simplement ignorée.
async function createSendcloudParcel(session) {
  const pub = process.env.SENDCLOUD_PUBLIC_KEY, sec = process.env.SENDCLOUD_SECRET_KEY;
  if (!pub || !sec) { console.log('Sendcloud : clés absentes, colis non créé'); return; }
  const cd = session.customer_details || {};
  const sd = session.shipping_details || (session.collected_information && session.collected_information.shipping_details) || {};
  const ad = sd.address || cd.address || {};
  const md = session.metadata || {};
  const relay = (session.custom_fields || []).find((f) => f.key === 'point_relais');
  const relayTxt = relay && relay.text && relay.text.value;
  // Sépare le numéro de la rue (ex. « 12 rue des Lilas » ou « Kerkstraat 12 »).
  let street = (ad.line1 || '').trim(), house = '';
  let m = street.match(/^(\d+\s?[A-Za-z]?)(?:\s*,)?\s+(.+)$/);
  if (m) { house = m[1].trim(); street = m[2].trim(); }
  else if ((m = street.match(/^(.+?)[\s,]+(\d+\s?[A-Za-z]?(?:[-/]\d+)?)$/))) { street = m[1].trim(); house = m[2].trim(); }
  const grams = parseInt(md.poids_g, 10);
  const parcel = {
    name: sd.name || cd.name || '',
    address: street || ad.line1 || '',
    ...(house ? { house_number: house } : {}),
    ...(ad.line2 ? { address_2: ad.line2 } : {}),
    city: ad.city || '',
    postal_code: ad.postal_code || '',
    country: ad.country || 'FR',
    telephone: cd.phone || '',
    email: cd.email || '',
    weight: (Number.isFinite(grams) && grams > 0 ? grams / 1000 : 1).toFixed(3),
    order_number: 'MF-' + String(session.id).slice(-8).toUpperCase(),
    external_order_id: session.id,
    total_order_value: (session.amount_total / 100).toFixed(2),
    total_order_value_currency: 'EUR',
    shipping_method_checkout_name: md.livraison === 'domicile' ? 'Mondial Relay – domicile' : 'Mondial Relay – Point Relais' + (relayTxt ? ' : ' + relayTxt : ''),
    request_label: false,
  };
  const r = await fetch('https://panel.sendcloud.sc/api/v2/parcels', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Basic ' + Buffer.from(pub + ':' + sec).toString('base64') },
    body: JSON.stringify({ parcel }),
  });
  if (!r.ok) console.log('Sendcloud a refusé le colis :', r.status, await r.text());
  else console.log('Sendcloud : colis créé pour', parcel.order_number);
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Méthode non autorisée' };
  const raw = event.isBase64Encoded ? Buffer.from(event.body || '', 'base64').toString('utf8') : (event.body || '');
  if (!verify(raw, event.headers['stripe-signature'], process.env.STRIPE_WEBHOOK_SECRET)) return { statusCode: 400, body: 'Signature invalide' };

  let ev;
  try { ev = JSON.parse(raw); } catch { return { statusCode: 400, body: 'JSON invalide' }; }
  if (ev.type !== 'checkout.session.completed') return ok('ignoré');
  const session = ev.data.object;
  if (session.payment_status && session.payment_status !== 'paid') return ok('non payé');

  try {
    // Évite de traiter deux fois la même commande (Stripe peut renvoyer un message).
    const pi = session.payment_intent;
    if (pi) {
      const p = await api('/payment_intents/' + pi);
      if (p.metadata && p.metadata.traite === '1') return ok('déjà traité');
    }
    // 1. Baisse du stock
    const items = ((session.metadata && session.metadata.items) || '').split(',').filter(Boolean);
    for (const entry of items) {
      const [id, qs] = entry.split(':');
      const q = parseInt(qs, 10);
      if (!id || !(q > 0)) continue;
      let prod;
      try { prod = await api('/products/' + encodeURIComponent(id)); } catch { continue; }
      const cur = parseInt(prod.metadata && prod.metadata.stock, 10);
      if (!Number.isFinite(cur)) continue; // produit sans limite de stock
      await api('/products/' + encodeURIComponent(id), { method: 'POST', form: new URLSearchParams({ 'metadata[stock]': String(Math.max(0, cur - q)) }) });
    }
    if (pi) await api('/payment_intents/' + pi, { method: 'POST', form: new URLSearchParams({ 'metadata[traite]': '1' }) });
    // 2. E-mail de commande (une erreur d'e-mail ne bloque pas le reste)
    try {
      const li = await api('/checkout/sessions/' + session.id + '/line_items?limit=50');
      await sendMail(session, li.data || []);
    } catch (e) { console.log('Erreur e-mail :', e.message); }
    // 3. Colis Sendcloud (une erreur ici ne bloque pas la commande)
    try { await createSendcloudParcel(session); } catch (e) { console.log('Erreur Sendcloud :', e.message); }
    return ok();
  } catch (e) {
    console.log('Erreur webhook :', e.message);
    return { statusCode: 500, body: 'Erreur' };
  }
};
