// Renvoie le stock actuel au site (pour griser les produits épuisés).
const { getStock } = require('./lib/stripe');

exports.handler = async () => {
  try {
    const stock = await getStock();
    return { statusCode: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, body: JSON.stringify({ stock }) };
  } catch (e) {
    return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ stock: {} }) };
  }
};
