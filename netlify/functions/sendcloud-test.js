// Vérifie que les clés Sendcloud sont bien enregistrées dans Netlify et acceptées par Sendcloud.
// Ouvre simplement : https://mmefofana.fr/.netlify/functions/sendcloud-test
// Ne crée aucun colis et n'affiche jamais les clés.
exports.handler = async () => {
  const pub = process.env.SENDCLOUD_PUBLIC_KEY, sec = process.env.SENDCLOUD_SECRET_KEY;
  const out = {
    fonction: 'en ligne',
    cle_publique: pub ? 'présente' : 'ABSENTE (variable SENDCLOUD_PUBLIC_KEY)',
    cle_confidentielle: sec ? 'présente' : 'ABSENTE (variable SENDCLOUD_SECRET_KEY)',
  };
  if (pub && sec) {
    try {
      const r = await fetch('https://panel.sendcloud.sc/api/v2/user', {
        headers: { Authorization: 'Basic ' + Buffer.from(pub + ':' + sec).toString('base64') },
      });
      out.sendcloud = r.ok ? 'connexion OK' : r.status === 401 ? 'clés refusées (401) : vérifie qu\'elles sont bien copiées en entier' : 'réponse inattendue (' + r.status + ')';
    } catch (e) { out.sendcloud = 'impossible de joindre Sendcloud : ' + e.message; }
  }
  return { statusCode: 200, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }, body: JSON.stringify(out) };
};
