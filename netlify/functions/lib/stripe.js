// Petites fonctions communes pour parler à Stripe (sans aucune dépendance).
const { CATALOG } = require('./data');

async function api(path, { method = 'GET', form } = {}) {
  const r = await fetch('https://api.stripe.com/v1' + path, {
    method,
    headers: {
      Authorization: 'Bearer ' + process.env.STRIPE_SECRET_KEY,
      ...(form ? { 'Content-Type': 'application/x-www-form-urlencoded' } : {}),
    },
    body: form ? form.toString() : undefined,
  });
  const j = await r.json();
  if (!r.ok) throw new Error((j.error && j.error.message) || 'Stripe ' + r.status);
  return j;
}

// Stock actuel de chaque produit. Il est conservé dans Stripe (Catalogue de produits > produit > métadonnée "stock").
// Mme Fofana peut donc le modifier elle-même dans Stripe. Les produits manquants sont créés automatiquement.
async function getStock() {
  const list = await api('/products?limit=100');
  const have = {};
  list.data.forEach((p) => { have[p.id] = p; });
  const out = {};
  for (const [id, p] of Object.entries(CATALOG)) {
    if (typeof p.stock !== 'number') continue; // pas de limite de stock
    let prod = have[id];
    if (!prod) {
      try {
        prod = await api('/products', {
          method: 'POST',
          form: new URLSearchParams({ id, name: p.name, 'metadata[stock]': String(p.stock) }),
        });
      } catch (e) { out[id] = p.stock; continue; }
    }
    const n = parseInt(prod.metadata && prod.metadata.stock, 10);
    out[id] = Number.isFinite(n) ? n : p.stock;
  }
  return out;
}

module.exports = { api, getStock };
