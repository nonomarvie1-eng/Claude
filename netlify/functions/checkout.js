// Crée la page de paiement Stripe. Prix, poids, stock et livraison sont recalculés ICI (jamais pris du navigateur).
// Clé Stripe : variable d'environnement STRIPE_SECRET_KEY (à définir dans Netlify, jamais dans le site).
const { CATALOG, SHIP } = require('./lib/data');
const { api, getStock } = require('./lib/stripe');

const json = (code, body) => ({ statusCode: code, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

exports.handler = async (event) => {
  // Diagnostic : ouvrir /.netlify/functions/checkout dans le navigateur. N'affiche jamais la clé.
  if (event.httpMethod === 'GET') {
    const k = process.env.STRIPE_SECRET_KEY || '';
    let stripe = 'non testé';
    if (k) { try { await api('/balance'); stripe = 'connexion OK'; } catch (e) { stripe = 'ERREUR : ' + e.message; } }
    return json(200, { fonction: 'en ligne', cle_stripe: k ? (k.startsWith('sk_live_') ? 'live (réel)' : k.startsWith('sk_test_') ? 'test' : 'format inattendu') : 'ABSENTE', stripe, url_site: process.env.URL || '(non définie)' });
  }
  if (event.httpMethod !== 'POST') return json(405, { error: 'Méthode non autorisée' });
  if (!process.env.STRIPE_SECRET_KEY) return json(500, { error: 'Paiement non configuré' });

  let data;
  try { data = JSON.parse(event.body || '{}'); } catch { return json(400, { error: 'Requête invalide' }); }

  const country = String(data.country || 'FR');
  if (!SHIP.c.some((c) => c[0] === country)) return json(400, { error: 'Pays non livré' });
  const mode = data.ship === 'home' ? 'home' : 'relay';
  if (!Array.isArray(data.items) || !data.items.length) return json(400, { error: 'Panier vide' });

  let stock = {};
  try { stock = await getStock(); } catch (e) { /* on retombe sur le stock du catalogue */ }

  let weight = SHIP.pack;
  const lines = [];
  for (const it of data.items) {
    const p = CATALOG[it.id];
    const q = Math.floor(Number(it.q));
    if (!p || p.soon || !(q >= 1)) return json(400, { error: 'Produit indisponible' });
    const st = it.id in stock ? stock[it.id] : p.stock;
    if (st === 0) return json(400, { error: 'Produit indisponible' });
    if (typeof st === 'number' && q > st) return json(400, { error: 'Stock insuffisant' });
    if (q > 50) return json(400, { error: 'Quantité trop élevée' });
    weight += p.w * q;
    lines.push({ id: it.id, name: p.name, cents: p.cents, q });
  }

  const table = SHIP[SHIP.map[country] || country] || [];
  const rate = table.find((r) => weight <= r[0]);
  if (!rate) return json(400, { error: 'Commande trop lourde : contactez-nous pour un devis' });
  let shipEuros = mode === 'home' ? rate[2] : rate[1];
  if (shipEuros != null && lines.reduce((t, l) => t + l.cents * l.q, 0) >= SHIP.free) shipEuros = 0; // livraison offerte dès 110 €
  if (shipEuros == null) return json(400, { error: 'Livraison à domicile indisponible pour ce pays' });

  const origin = process.env.URL || event.headers.origin || '';
  const f = new URLSearchParams();
  f.set('mode', 'payment');
  f.set('locale', 'fr');
  f.set('success_url', origin + '/#/merci');
  f.set('cancel_url', origin + '/#/boutique');
  f.set('phone_number_collection[enabled]', 'true');
  f.set('shipping_address_collection[allowed_countries][0]', country);
  f.set('metadata[livraison]', mode === 'home' ? 'domicile' : 'point_relais');
  f.set('metadata[pays]', country);
  f.set('metadata[poids_g]', String(weight));
  f.set('metadata[items]', lines.map((l) => l.id + ':' + l.q).join(','));
  lines.forEach((l, i) => {
    f.set(`line_items[${i}][quantity]`, String(l.q));
    f.set(`line_items[${i}][price_data][currency]`, 'eur');
    f.set(`line_items[${i}][price_data][unit_amount]`, String(l.cents));
    f.set(`line_items[${i}][price_data][product_data][name]`, l.name);
  });
  f.set('shipping_options[0][shipping_rate_data][type]', 'fixed_amount');
  f.set('shipping_options[0][shipping_rate_data][display_name]',
    (shipEuros === 0 ? 'Livraison offerte' : (mode === 'home' ? 'Livraison à domicile (Mondial Relay)' : 'Livraison en Point Relais (Mondial Relay)')));
  f.set('shipping_options[0][shipping_rate_data][fixed_amount][amount]', String(Math.round(shipEuros * 100)));
  f.set('shipping_options[0][shipping_rate_data][fixed_amount][currency]', 'eur');
  if (mode === 'relay') {
    f.set('custom_fields[0][key]', 'point_relais');
    f.set('custom_fields[0][label][type]', 'custom');
    f.set('custom_fields[0][label][custom]', 'Votre Point Relais (nom et ville)');
    f.set('custom_fields[0][type]', 'text');
  }

  try {
    const s = await api('/checkout/sessions', { method: 'POST', form: f });
    if (!s.url) return json(502, { error: 'Erreur Stripe' });
    return json(200, { url: s.url });
  } catch (e) {
    return json(502, { error: e.message || 'Erreur Stripe' });
  }
};
