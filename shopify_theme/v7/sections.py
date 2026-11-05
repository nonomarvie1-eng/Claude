# Page d'accueil Gâté Pourri v7 : style moderne et lumineux.
# Chaque entrée = une section "custom-liquid" de Horizon.
CDN = "https://cdn.shopify.com/s/files/1/1109/7712/2629/files/"
IMG = {
 "toutou_m": CDN+"C01B7A47-649A-4D8E-838B-9C7018B9CF7E.png?v=1793887831",
 "avenue_m": CDN+"0525FFD2-E074-4DC9-BE5A-19AF0C0A5CB4.png?v=1793887831",
 "chateau_m": CDN+"57B2D92B-CCF0-4687-8D2D-098E5DD3AE5F.png?v=1793887831",
 "noel_m": CDN+"33728BC1-3584-475F-84E9-8292CD6C9261.png?v=1793887831",
 "toutou_d": CDN+"5CCB3C6A-5A54-4113-B002-CF632CF6835F.png?v=1793887870",
 "avenue_d": CDN+"04579DE4-C312-4C54-B263-4D118626FA17.png?v=1793887867",
 "chateau_d": CDN+"2AFE91A5-F75F-40DD-8BC7-58B1F4D69833.png?v=1793887868",
 "noel_d": CDN+"2610AB4E-777D-4710-BCA6-4A0B942D0DCB.png?v=1793887867",
}
H = {
 "toutou": "/products/plaque-le-petit-toutou-personnalisee-portrait-de-votre-chien",
 "avenue": "/products/plaque-de-rue-avenue-personnalisee-portrait-de-votre-chien",
 "chateau": "/products/plaque-chateau-personnalisee-etiquette-de-grand-cru-de-votre-chien",
 "noel": "/products/plaque-lettre-au-pere-noel-personnalisee-ecrite-par-votre-chien",
}
def img(key, w):
    return IMG[key] + f"&width={w}"

STYLE = """
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
<style>
.gp{--ink:#1d1a2f;--soft:#5b5870;--accent:#e5451f;--accent-d:#c9381a;--peach:#ffeee6;--sun:#ffd84d;--sky:#e8f1ff;--line:#ece7e2;
 font-family:'DM Sans',system-ui,sans-serif;color:var(--ink);font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.gp *{box-sizing:border-box}
.gp h1,.gp h2,.gp h3{font-family:'Poppins',sans-serif;color:var(--ink);margin:0;letter-spacing:-.02em}
.gp p{margin:0}
.gp a{color:inherit}
.gp-wrap{max-width:1160px;margin:0 auto;padding:0 20px}
.gp-sec{padding:56px 0}
.gp-kicker{display:inline-block;font-family:'Poppins',sans-serif;font-weight:700;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
.gp-h2{font-size:clamp(28px,5vw,42px);line-height:1.12;font-weight:800}
.gp-lead{color:var(--soft);font-size:17px;max-width:560px;margin-top:12px}
.gp-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--accent);color:#fff!important;text-decoration:none;font-family:'Poppins',sans-serif;font-weight:700;font-size:16px;padding:16px 28px;border-radius:999px;transition:transform .15s,background .15s;border:0}
.gp-btn:hover{background:var(--accent-d);transform:translateY(-1px)}
.gp-btn--ghost{background:transparent;color:var(--ink)!important;box-shadow:inset 0 0 0 2px var(--ink)}
.gp-btn--ghost:hover{background:var(--ink);color:#fff!important}
/* Hero */
.gp-hero{padding:28px 0 48px;background:linear-gradient(180deg,#fff 0%,var(--peach) 100%)}
.gp-hero__grid{display:grid;gap:28px;align-items:center}
.gp-hero h1{font-size:clamp(36px,8.5vw,64px);line-height:1.04;font-weight:800}
.gp-hero h1 em{font-style:normal;color:var(--accent)}
.gp-hero__txt p{font-size:18px;color:var(--soft);margin-top:16px;max-width:520px}
.gp-hero__cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
.gp-pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px;padding:0;list-style:none}
.gp-pills li{background:#fff;border:1px solid var(--line);border-radius:999px;padding:7px 14px;font-size:14px;font-weight:500}
.gp-hero__img{position:relative}
.gp-hero__img img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:28px;display:block;box-shadow:0 24px 60px -24px rgba(29,26,47,.35)}
.gp-sticker{position:absolute;left:-6px;bottom:18px;background:var(--sun);color:var(--ink);font-family:'Poppins',sans-serif;font-weight:800;font-size:15px;line-height:1.15;padding:14px 16px;border-radius:18px;transform:rotate(-4deg);box-shadow:0 10px 24px -10px rgba(0,0,0,.3)}
.gp-sticker small{display:block;font-weight:600;font-size:12px}
/* Produits */
.gp-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:28px}
.gp-card{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:22px;overflow:hidden;text-decoration:none;transition:transform .2s,box-shadow .2s}
.gp-card:hover{transform:translateY(-3px);box-shadow:0 18px 40px -22px rgba(29,26,47,.4)}
.gp-card__img{position:relative;aspect-ratio:1/1;background:var(--peach)}
.gp-card__img img{width:100%;height:100%;object-fit:cover;display:block}
.gp-tag{position:absolute;top:10px;left:10px;background:#fff;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:700}
.gp-tag--noel{background:#d92c2c;color:#fff}
.gp-card__body{padding:14px 14px 16px;display:flex;flex-direction:column;gap:4px;flex:1}
.gp-card__body h3{font-size:17px;font-weight:700}
.gp-card__body p{font-size:14px;color:var(--soft);flex:1}
.gp-card__foot{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.gp-price{font-family:'Poppins',sans-serif;font-weight:700;font-size:16px}
.gp-arrow{width:36px;height:36px;border-radius:50%;background:var(--ink);color:#fff;display:grid;place-items:center;font-size:18px}
/* Étapes */
.gp-steps{display:grid;gap:14px;margin-top:28px;counter-reset:s}
.gp-step{background:#fff;border-radius:22px;padding:22px;border:1px solid var(--line)}
.gp-step__n{width:44px;height:44px;border-radius:14px;background:var(--sun);display:grid;place-items:center;font-family:'Poppins',sans-serif;font-weight:800;font-size:20px;margin-bottom:14px}
.gp-step h3{font-size:19px;font-weight:700;margin-bottom:6px}
.gp-step p{color:var(--soft);font-size:15px}
/* Exemple */
.gp-ex{background:var(--ink);color:#fff;border-radius:32px;padding:32px 22px;display:grid;gap:28px;align-items:center}
.gp-ex h2{color:#fff}
.gp-ex .gp-lead{color:#c9c6d8}
.gp-ex__img{max-width:300px;margin:0 auto}
.gp-ex__img img{width:100%;height:auto;max-width:380px;display:block;margin:0 auto;border-radius:10px;box-shadow:0 30px 60px -20px rgba(0,0,0,.6);transform:rotate(-2deg)}
.gp-ex ul{list-style:none;padding:0;margin:20px 0 0;display:grid;gap:12px}
.gp-ex li{display:flex;gap:12px;align-items:flex-start;font-size:16px}
.gp-ex li b{color:var(--sun)}
.gp-dot{flex:none;width:26px;height:26px;border-radius:50%;background:var(--accent);display:grid;place-items:center;font-size:13px;font-weight:700;margin-top:1px}
/* Garanties */
.gp-trust{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:28px}
.gp-trust div{background:var(--sky);border-radius:20px;padding:18px}
.gp-trust .ic{font-size:26px;display:block;margin-bottom:8px}
.gp-trust b{display:block;font-family:'Poppins',sans-serif;font-size:15px;margin-bottom:4px}
.gp-trust span{font-size:14px;color:var(--soft)}
/* Noël */
.gp-xmas{background:#d92c2c;color:#fff;border-radius:28px;padding:28px 22px;display:grid;gap:18px;align-items:center}
.gp-xmas h2{color:#fff;font-size:clamp(24px,4.6vw,34px);font-weight:800;line-height:1.15}
.gp-xmas p{color:#ffe1e1;margin-top:8px}
.gp-xmas .gp-btn{background:#fff;color:#d92c2c!important}
/* FAQ */
.gp-faq{margin-top:24px;border-top:1px solid var(--line)}
.gp-faq details{border-bottom:1px solid var(--line)}
.gp-faq summary{list-style:none;cursor:pointer;padding:18px 40px 18px 0;font-family:'Poppins',sans-serif;font-weight:600;font-size:17px;position:relative}
.gp-faq summary::-webkit-details-marker{display:none}
.gp-faq summary::after{content:'+';position:absolute;right:4px;top:50%;transform:translateY(-50%);width:28px;height:28px;border-radius:50%;background:var(--peach);display:grid;place-items:center;font-size:18px;color:var(--accent)}
.gp-faq details[open] summary::after{content:'–'}
.gp-faq details p{padding:0 0 18px;color:var(--soft)}
/* Fin */
.gp-end{text-align:center;background:var(--peach);border-radius:32px;padding:44px 22px}
.gp-end .gp-lead{margin:12px auto 24px}
@media(min-width:750px){
 .gp-ex__img{max-width:380px}
 .gp-sec{padding:84px 0}
 .gp-hero{padding:56px 0 80px}
 .gp-hero__grid{grid-template-columns:1.05fr 1fr;gap:56px}
 .gp-sticker{left:-22px;bottom:30px;font-size:18px;padding:16px 20px}
 .gp-grid{grid-template-columns:repeat(4,1fr);gap:20px}
 .gp-steps{grid-template-columns:repeat(3,1fr);gap:20px}
 .gp-ex{grid-template-columns:1fr 1fr;padding:56px;gap:56px}
 .gp-trust{grid-template-columns:repeat(4,1fr);gap:16px}
 .gp-xmas{grid-template-columns:1fr auto;padding:36px 44px}
 .gp-faq{max-width:820px}
 .gp-end{padding:72px 40px}
}
</style>
"""

HERO = f"""
<div class="gp"><section class="gp-hero"><div class="gp-wrap gp-hero__grid">
 <div class="gp-hero__txt">
  <span class="gp-kicker">Plaques personnalisées pour chiens</span>
  <h1>Son portrait.<br>Ses bêtises.<br><em>Sur une plaque.</em></h1>
  <p>Envoyez-nous une photo de votre chien. On crée une plaque vintage rien qu'à lui, à accrocher chez vous ou à offrir.</p>
  <div class="gp-hero__cta"><a class="gp-btn" href="#plaques">Choisir ma plaque</a><a class="gp-btn gp-btn--ghost" href="#comment">Comment ça marche</a></div>
  <ul class="gp-pills"><li>34,90 €</li><li>🚚 Livraison offerte</li><li>👀 Aperçu avant impression</li></ul>
 </div>
 <div class="gp-hero__img">
  <img src="{img('avenue_m',1100)}" alt="Plaque de rue Avenue personnalisée avec le portrait d'un chien, accrochée près d'une porte" width="1100" height="1100" fetchpriority="high">
  <div class="gp-sticker">Votre chien,<br>votre texte<small>fait à partir de votre photo</small></div>
 </div>
</div></section></div>
"""

def card(key, name, pitch, tag="", tagcls=""):
    t = f'<span class="gp-tag {tagcls}">{tag}</span>' if tag else ""
    return f"""<a class="gp-card" href="{H[key]}">
  <div class="gp-card__img"><img src="{img(key+'_m',700)}" alt="Plaque {name} personnalisée" loading="lazy" width="700" height="700">{t}</div>
  <div class="gp-card__body"><h3>{name}</h3><p>{pitch}</p>
  <div class="gp-card__foot"><span class="gp-price">34,90 €</span><span class="gp-arrow" aria-hidden="true">→</span></div></div></a>"""

PRODUITS = f"""
<div class="gp" id="plaques"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">La collection</span>
 <h2 class="gp-h2">Choisissez son style</h2>
 <p class="gp-lead">Quatre plaques, quatre façons de raconter votre chien. Toutes en aluminium, format 20 × 30 cm.</p>
 <div class="gp-grid">
  {card('toutou','Le Petit Toutou','Votre chien fait la une du journal.','Le plus drôle')}
  {card('avenue','Avenue','Sa propre plaque de rue, façon Paris.')}
  {card('chateau','Château','Son étiquette de grand cru.')}
  {card('noel','Lettre au Père Noël','Sa liste de cadeaux, signée de sa patte.','Noël','gp-tag--noel')}
 </div>
</div></section></div>
"""

ETAPES = """
<div class="gp" id="comment" style="background:#faf8f6"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">Simple comme un « assis »</span>
 <h2 class="gp-h2">Comment ça marche</h2>
 <div class="gp-steps">
  <div class="gp-step"><div class="gp-step__n">1</div><h3>Choisissez la plaque</h3><p>Journal, plaque de rue, grand cru ou lettre au Père Noël.</p></div>
  <div class="gp-step"><div class="gp-step__n">2</div><h3>Envoyez sa photo</h3><p>Après la commande, on vous écrit pour recevoir sa photo, son prénom et sa bêtise préférée.</p></div>
  <div class="gp-step"><div class="gp-step__n">3</div><h3>Validez l'aperçu</h3><p>Vous recevez le design sous 48 h. On imprime seulement quand vous dites OK.</p></div>
 </div>
</div></section></div>
"""

EXEMPLE = f"""
<div class="gp"><section class="gp-sec"><div class="gp-wrap"><div class="gp-ex">
 <div class="gp-ex__img"><img src="{img('toutou_d',800)}" alt="Exemple : plaque Le Petit Toutou avec Tokyo, un shiba, en une du journal" loading="lazy" width="800" height="1200"></div>
 <div>
  <span class="gp-kicker" style="color:var(--sun)">Exemple</span>
  <h2 class="gp-h2">Voici Tokyo.<br>Il a mangé la télécommande.</h2>
  <p class="gp-lead">Une photo et une phrase suffisent. Voilà ce que ça donne.</p>
  <ul>
   <li><span class="gp-dot">1</span><span><b>Son portrait</b> dessiné à partir de la photo</span></li>
   <li><span class="gp-dot">2</span><span><b>Son prénom</b> en gros titre</span></li>
   <li><span class="gp-dot">3</span><span><b>Sa bêtise</b> racontée comme un fait divers</span></li>
  </ul>
  <div style="margin-top:26px"><a class="gp-btn" href="{H['toutou']}">Faire la même pour mon chien</a></div>
 </div>
</div></div></section></div>
"""

GARANTIES = """
<div class="gp"><section class="gp-sec" style="padding-top:0"><div class="gp-wrap">
 <span class="gp-kicker">Sans mauvaise surprise</span>
 <h2 class="gp-h2">On s'occupe de tout</h2>
 <div class="gp-trust">
  <div><span class="ic">👀</span><b>Aperçu sous 48 h</b><span>Vous voyez la plaque avant qu'elle existe.</span></div>
  <div><span class="ic">✍️</span><b>Corrections offertes</b><span>Un détail à changer ? On le refait.</span></div>
  <div><span class="ic">🚚</span><b>Livraison offerte</b><span>En France métropolitaine, avec suivi.</span></div>
  <div><span class="ic">💬</span><b>Réponse sous 24 h</b><span>Une vraie personne vous répond.</span></div>
 </div>
</div></section></div>
"""

NOEL = f"""
<div class="gp"><section class="gp-sec" style="padding-top:0"><div class="gp-wrap"><div class="gp-xmas">
 <div><h2>🎄 Un cadeau pour Noël ?</h2><p>Commandez avant le 1er décembre pour la recevoir à temps.</p></div>
 <a class="gp-btn" href="{H['noel']}">Voir la Lettre au Père Noël</a>
</div></div></section></div>
"""

FAQ = """
<div class="gp" style="background:#faf8f6"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">Questions</span>
 <h2 class="gp-h2">Vous vous demandez sûrement…</h2>
 <div class="gp-faq">
  <details><summary>Ce sera vraiment mon chien ?</summary><p>Oui. Le portrait est fait à partir de votre photo. Vous voyez l'aperçu avant l'impression et vous pouvez demander une correction.</p></details>
  <details><summary>Quelle photo envoyer ?</summary><p>Une photo nette et bien éclairée, la tête bien visible, de face ou de trois-quarts. Si elle ne suffit pas, on vous en demande une autre.</p></details>
  <details><summary>En combien de temps je la reçois ?</summary><p>Environ 3 semaines après la validation de l'aperçu. Pour Noël, commandez avant le 1er décembre.</p></details>
  <details><summary>Elle est en quoi ?</summary><p>En aluminium imprimé, 20 × 30 cm. L'effet ancien (rivets, usure) est imprimé : la plaque est plate. Elle est faite pour l'intérieur.</p></details>
  <details><summary>Ça marche pour les chats ?</summary><p>Oui ! Dites-le nous simplement quand vous envoyez la photo.</p></details>
  <details><summary>Et si elle arrive abîmée ?</summary><p>On la refait ou on vous rembourse. Comme elle est fabriquée sur mesure, elle ne peut pas être retournée si elle correspond à l'aperçu validé.</p></details>
 </div>
</div></section></div>
"""

FIN = """
<div class="gp"><section class="gp-sec"><div class="gp-wrap"><div class="gp-end">
 <h2 class="gp-h2">Il le mérite bien, non ?</h2>
 <p class="gp-lead">Une plaque unique, avec sa tête et ses bêtises. À partir d'une simple photo.</p>
 <a class="gp-btn" href="#plaques">Créer sa plaque</a>
</div></div></section></div>
"""

SECTIONS = [("hero", STYLE+HERO), ("plaques", PRODUITS), ("etapes", ETAPES), ("exemple", EXEMPLE),
            ("garanties", GARANTIES), ("noel", NOEL), ("faq", FAQ), ("fin", FIN)]

import re as _re
def _nbsp(html):
    # espaces insécables français (hors CSS : on ne traite que le texte entre balises)
    def fix(m):
        t=m.group(0)
        t=_re.sub(r' ([?!:;»€h])(?=[\s<.,]|$)', r'&nbsp;\1', t)
        t=t.replace('« ','«&nbsp;').replace(' × ','&nbsp;×&nbsp;').replace('20&nbsp;×&nbsp;30 cm','20&nbsp;×&nbsp;30&nbsp;cm')
        return t
    return _re.sub(r'>[^<]+<', fix, html)
SECTIONS=[(k, v if k!='hero' else v) for k,v in SECTIONS]
SECTIONS=[(k, (v.split('</style>')[0]+'</style>'+_nbsp(v.split('</style>')[1])) if '</style>' in v else _nbsp(v)) for k,v in SECTIONS]
