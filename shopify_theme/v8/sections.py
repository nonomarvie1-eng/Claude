# Gâté Pourri v8 : bleu nuit + crème, orange pour l'action, jaune en touche.
import re as _re
CDN = "https://cdn.shopify.com/s/files/1/1109/7712/2629/files/"
IMG = {
 "toutou_m": "C01B7A47-649A-4D8E-838B-9C7018B9CF7E.png?v=1793887831",
 "avenue_m": "0525FFD2-E074-4DC9-BE5A-19AF0C0A5CB4.png?v=1793887831",
 "chateau_m": "57B2D92B-CCF0-4687-8D2D-098E5DD3AE5F.png?v=1793887831",
 "noel_m": "33728BC1-3584-475F-84E9-8292CD6C9261.png?v=1793887831",
 "toutou_d": "5CCB3C6A-5A54-4113-B002-CF632CF6835F.png?v=1793887870",
 "avenue_d": "04579DE4-C312-4C54-B263-4D118626FA17.png?v=1793887867",
 "chateau_d": "2AFE91A5-F75F-40DD-8BC7-58B1F4D69833.png?v=1793887868",
 "noel_d": "2610AB4E-777D-4710-BCA6-4A0B942D0DCB.png?v=1793887867",
}
H = {
 "toutou": "/products/plaque-le-petit-toutou-personnalisee-portrait-de-votre-chien",
 "avenue": "/products/plaque-de-rue-avenue-personnalisee-portrait-de-votre-chien",
 "chateau": "/products/plaque-chateau-personnalisee-etiquette-de-grand-cru-de-votre-chien",
 "noel": "/products/plaque-lettre-au-pere-noel-personnalisee-ecrite-par-votre-chien",
}
def img(key, w): return CDN + IMG[key] + f"&width={w}"

FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">"""

BASE_CSS = """
.gp{--ink:#1b2a4a;--soft:#56607a;--accent:#e5451f;--accent-d:#c9381a;--cream:#f7f0e3;--cream-d:#efe4cf;--sun:#ffd84d;--line:#e7dfd0;
 font-family:'DM Sans',system-ui,sans-serif;color:var(--ink);font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased}
.gp *{box-sizing:border-box}
.gp h1,.gp h2,.gp h3{font-family:'Poppins',sans-serif;color:var(--ink);margin:0;letter-spacing:-.02em}
.gp p{margin:0}
.gp a{color:inherit}
.gp-wrap{max-width:1120px;margin:0 auto;padding:0 18px}
.gp-sec{padding:40px 0}
.gp-kicker{display:inline-block;font-family:'Poppins',sans-serif;font-weight:700;font-size:12px;letter-spacing:.07em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
.gp-h2{font-size:clamp(24px,4.4vw,36px);line-height:1.15;font-weight:800}
.gp-lead{color:var(--soft);font-size:16px;max-width:560px;margin-top:8px}
.gp-btn{display:inline-flex;align-items:center;justify-content:center;background:var(--accent);color:#fff!important;text-decoration:none;font-family:'Poppins',sans-serif;font-weight:700;font-size:16px;padding:15px 28px;border-radius:999px;transition:background .15s,transform .15s}
.gp-btn:hover{background:var(--accent-d);transform:translateY(-1px)}
.gp-link{font-weight:700;text-decoration:underline;text-underline-offset:3px}
@media(min-width:750px){.gp-sec{padding:64px 0}}
"""

HOME_CSS = """
/* Accueil */
.gp-hero{background:var(--cream);padding:16px 0 24px;overflow:hidden}
.gp-hero__grid{display:grid;gap:0}
.gp-hero h1{font-size:clamp(28px,7.6vw,58px);line-height:1.04;font-weight:800}
.gp-hero h1 em{font-style:normal;color:var(--accent)}
.gp-fan{position:relative;height:clamp(210px,62vw,470px);margin:2px auto 4px;width:100%;max-width:440px}
.gp-fan img{position:absolute;top:50%;left:50%;height:auto;border-radius:6px;box-shadow:0 18px 34px -16px rgba(27,42,74,.55)}
.gp-fan .c{width:44%;transform:translate(-50%,-50%);z-index:3}
.gp-fan .l{width:38%;transform:translate(-118%,-46%) rotate(-8deg);z-index:2}
.gp-fan .r{width:38%;transform:translate(18%,-46%) rotate(8deg);z-index:2}
.gp-hero__txt p{font-size:16px;color:var(--soft);max-width:480px}
.gp-buy{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;margin-top:12px}
.gp-buy__price{font-family:'Poppins',sans-serif;font-weight:700;font-size:17px}
.gp-buy__price small{display:block;font-family:'DM Sans',sans-serif;font-weight:500;font-size:13px;color:var(--soft)}
.gp-hero__more{margin-top:10px;font-size:13.5px}
.gp-hero__more a{color:var(--soft);font-weight:400;text-decoration:underline;text-underline-offset:2px}
/* Collection */
.gp-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:20px}
.gp-card{display:flex;flex-direction:column;text-decoration:none;border-radius:18px;overflow:hidden;background:#fff;border:1px solid var(--line);transition:transform .2s,box-shadow .2s}
.gp-card:hover{transform:translateY(-3px);box-shadow:0 16px 34px -20px rgba(27,42,74,.45)}
.gp-card__img{position:relative;aspect-ratio:4/5;background:var(--cream);display:flex;align-items:center;justify-content:center;padding:14px}
.gp-card__img img{height:100%;width:auto;max-width:100%;object-fit:contain;border-radius:4px;box-shadow:0 10px 20px -10px rgba(27,42,74,.5)}
.gp-tag{position:absolute;bottom:8px;right:8px;z-index:2;background:var(--sun);color:var(--ink);border-radius:999px;padding:3px 9px;font-size:11px;font-weight:700}
.gp-card__body{padding:12px 12px 14px;display:flex;flex-direction:column;gap:2px;flex:1}
.gp-card__body h3{font-size:16px;font-weight:700}
.gp-card__body p{font-size:13.5px;color:var(--soft);flex:1}
.gp-card__foot{display:flex;justify-content:space-between;align-items:center;margin-top:8px;font-family:'Poppins',sans-serif;font-weight:700}
.gp-card__foot span:last-child{color:var(--accent);font-size:14px}
.gp-note{margin-top:14px;font-size:14px;color:var(--soft)}
/* Étapes */
.gp-steps{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:10px}
.gp-steps li{display:flex;gap:12px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.gp-steps b{font-family:'Poppins',sans-serif}
.gp-steps span.n{flex:none;width:30px;height:30px;border-radius:50%;background:var(--ink);color:#fff;display:grid;place-items:center;font-family:'Poppins',sans-serif;font-weight:700;font-size:14px}
.gp-steps p{font-size:14.5px;color:var(--soft)}
/* Chez vous */
.gp-strip{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;margin:18px -18px 0;padding:0 18px 6px}
.gp-strip figure{margin:0;flex:0 0 72%;scroll-snap-align:start}
.gp-strip img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:14px;display:block}
.gp-strip figcaption{font-size:13px;color:var(--soft);margin-top:6px}
/* Le produit */
.gp-spec{display:grid;gap:0;margin-top:16px;border-top:1px solid var(--line)}
.gp-spec div{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:11px 0;border-bottom:1px solid var(--line);font-size:15px}
.gp-spec dt,.gp-spec b{font-weight:700}
.gp-spec span{color:var(--soft)}
/* FAQ */
.gp-faq{margin-top:14px;border-top:1px solid var(--line)}
.gp-faq details{border-bottom:1px solid var(--line)}
.gp-faq summary{list-style:none;cursor:pointer;padding:14px 36px 14px 0;font-family:'Poppins',sans-serif;font-weight:600;font-size:16px;position:relative}
.gp-faq summary::-webkit-details-marker{display:none}
.gp-faq summary::after{content:'+';position:absolute;right:2px;top:50%;transform:translateY(-50%);font-size:22px;color:var(--accent)}
.gp-faq details[open] summary::after{content:'–'}
.gp-faq details p{padding:0 0 14px;color:var(--soft);font-size:15px}
.gp-center{text-align:center;margin-top:26px}
@media(min-width:750px){
 .gp-hero{padding:40px 0 48px}
 .gp-hero__grid{grid-template-columns:1fr 1fr;align-items:center;gap:40px}
 .gp-hero__grid .gp-fan{grid-column:2;grid-row:1/span 2;height:470px;max-width:520px;margin:0}
 .gp-hero__txt{margin-top:18px}
 .gp-grid{grid-template-columns:repeat(4,1fr);gap:18px}
 .gp-steps{grid-template-columns:repeat(3,1fr)}
 .gp-strip{margin:18px 0 0;padding:0;overflow:visible}
 .gp-strip figure{flex:1 1 0;max-width:360px}
 .gp-two{display:grid;grid-template-columns:1fr 1fr;gap:56px}
}
"""

def nbsp(html):
    def fix(m):
        t = m.group(0)
        t = _re.sub(r' ([?!:;»€h])(?=[\s<.,)]|$)', r'&nbsp;\1', t)
        t = t.replace('« ', '«&nbsp;').replace(' × ', '&nbsp;×&nbsp;').replace(' cm', '&nbsp;cm').replace(' semaines', '&nbsp;semaines')
        return t
    return _re.sub(r'>[^<]+<', fix, html)

HERO = f"""
<div class="gp"><section class="gp-hero"><div class="gp-wrap gp-hero__grid">
 <div><span class="gp-kicker">Plaques personnalisées pour chiens</span>
  <h1>Son portrait.<br>Ses bêtises.<br><em>Sur une plaque.</em></h1></div>
 <div class="gp-fan" aria-hidden="true">
  <img class="l" src="{img('avenue_d',500)}" alt="" width="500" height="750">
  <img class="r" src="{img('chateau_d',500)}" alt="" width="500" height="750">
  <img class="c" src="{img('toutou_d',600)}" alt="Plaque Le Petit Toutou : un chien en une du journal" width="600" height="900" fetchpriority="high">
 </div>
 <div class="gp-hero__txt">
  <p>Une photo de votre chien suffit&nbsp;: on en fait une plaque vintage unique, avec son prénom et ses bêtises.</p>
  <div class="gp-buy"><span class="gp-buy__price">34,90 €<small>Livraison offerte en France</small></span>
   <a class="gp-btn" href="#plaques">Créer sa plaque</a></div>
  <p class="gp-hero__more"><a href="#comment">Comment ça marche&nbsp;?</a></p>
 </div>
</div></section></div>
"""

def card(key, name, pitch, tag=""):
    t = f'<span class="gp-tag">{tag}</span>' if tag else ""
    return f"""<a class="gp-card" href="{H[key]}"><div class="gp-card__img">{t}<img src="{img(key+'_d',500)}" alt="Plaque {name} personnalisée, vue de face" loading="lazy" width="500" height="750"></div>
 <div class="gp-card__body"><h3>{name}</h3><p>{pitch}</p><div class="gp-card__foot"><span>34,90 €</span><span>Créer →</span></div></div></a>"""

PLAQUES = f"""
<div class="gp" id="plaques"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">La collection</span>
 <h2 class="gp-h2">Choisissez son style</h2>
 <div class="gp-grid">
  {card('toutou','Le Petit Toutou','Sa bêtise en une du journal.','Le plus drôle')}
  {card('avenue','Avenue','Sa plaque de rue, façon Paris.')}
  {card('chateau','Château','Son étiquette de grand cru.')}
  {card('noel','Lettre au Père Noël','Ses 3 vœux, signés de sa patte.','Noël')}
 </div>
 <p class="gp-note">Sur chaque plaque : son portrait dessiné d'après votre photo, son prénom et votre texte.</p>
</div></section></div>
"""

ETAPES = """
<div class="gp" id="comment" style="background:var(--cream,#f7f0e3)"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">Comment ça marche</span>
 <h2 class="gp-h2">3 étapes, et c'est tout</h2>
 <ol class="gp-steps">
  <li><span class="n">1</span><div><b>Personnalisez</b><p>Prénom, texte et photo, directement sur la page de la plaque.</p></div></li>
  <li><span class="n">2</span><div><b>Validez l'aperçu</b><p>Par e-mail, sous 2 jours ouvrés après réception d'une photo exploitable. Rien n'est imprimé sans votre accord.</p></div></li>
  <li><span class="n">3</span><div><b>Recevez-la</b><p>Environ 3 semaines après votre validation. Livraison offerte, avec suivi.</p></div></li>
 </ol>
</div></section></div>
"""

CHEZVOUS = f"""
<div class="gp"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">Chez vous</span>
 <h2 class="gp-h2">Au salon, dans la cuisine, sur la cheminée</h2>
 <div class="gp-strip">
  <figure><img src="{img('toutou_m',700)}" alt="Plaque Le Petit Toutou accrochée dans un salon" loading="lazy" width="700" height="700"><figcaption>Le Petit Toutou, dans un salon</figcaption></figure>
  <figure><img src="{img('chateau_m',700)}" alt="Plaque Château dans une cuisine, avec ses dimensions 20 × 30 cm" loading="lazy" width="700" height="700"><figcaption>Château : format 20 × 30 cm</figcaption></figure>
  <figure><img src="{img('noel_m',700)}" alt="Plaque Lettre au Père Noël sur une cheminée" loading="lazy" width="700" height="700"><figcaption>Lettre au Père Noël, sur la cheminée</figcaption></figure>
 </div>
 <p class="gp-note">Images d'illustration. La plaque est plate : les rivets, l'usure et les reliefs sont imprimés.</p>
</div></section></div>
"""

PRODUIT = """
<div class="gp" style="background:var(--cream,#f7f0e3)"><section class="gp-sec"><div class="gp-wrap gp-two">
 <div><span class="gp-kicker">Ce que vous recevez</span>
 <h2 class="gp-h2">La plaque, en détail</h2>
 <dl class="gp-spec">
  <div><dt>Matière</dt><span>Aluminium imprimé</span></div>
  <div><dt>Format</dt><span>20 × 30 cm, vertical</span></div>
  <div><dt>Rendu</dt><span>Plaque plate : l'effet ancien est imprimé</span></div>
  <div><dt>Usage</dt><span>Pour l'intérieur</span></div>
 </dl></div>
 <div><span class="gp-kicker">Nos engagements</span>
 <h2 class="gp-h2">Avant, pendant, après</h2>
 <dl class="gp-spec">
  <div><dt>Aperçu</dt><span>Par e-mail, sous 2 jours ouvrés après réception d'une photo exploitable</span></div>
  <div><dt>Retouches</dt><span>Jusqu'à 2 séries de corrections sur l'aperçu, incluses</span></div>
  <div><dt>Délai</dt><span>Environ 3 semaines entre votre validation et la livraison</span></div>
  <div><dt>Livraison</dt><span>Offerte en France métropolitaine, avec suivi</span></div>
  <div><dt>Problème</dt><span>Plaque abîmée ou différente de l'aperçu validé : on la refait ou on vous rembourse</span></div>
 </dl></div>
</div></section></div>
"""

FAQ = """
<div class="gp"><section class="gp-sec"><div class="gp-wrap" style="max-width:820px">
 <span class="gp-kicker">Questions</span>
 <h2 class="gp-h2">Vous vous demandez sûrement…</h2>
 <div class="gp-faq">
  <details><summary>Ce sera vraiment mon chien ?</summary><p>Oui. Le portrait est dessiné d'après votre photo. Vous voyez l'aperçu avant l'impression et vous pouvez demander des corrections.</p></details>
  <details><summary>Quelle photo choisir ?</summary><p>Nette, bien éclairée, sans filtre, la tête bien visible, de face ou de trois-quarts. Si elle ne suffit pas, on vous en demande une autre avant de commencer.</p></details>
  <details><summary>Et pour Noël ?</summary><p>Comptez environ 3 semaines après la validation de l'aperçu. Pour un cadeau, commandez le plus tôt possible.</p></details>
  <details><summary>Ça marche pour les chats ?</summary><p>Oui. Précisez-le simplement dans le champ « Une précision ? » de la fiche produit.</p></details>
  <details><summary>Puis-je la retourner ?</summary><p>Comme elle est fabriquée sur mesure, elle ne peut pas être retournée si elle correspond à l'aperçu validé. Si elle arrive abîmée ou différente, on la refait ou on vous rembourse.</p></details>
 </div>
 <div class="gp-center"><a class="gp-btn" href="#plaques">Créer sa plaque</a></div>
</div></section></div>
"""

def home_sections():
    css = FONTS + "<style>" + BASE_CSS + HOME_CSS + "</style>"
    secs = [("hero", HERO), ("plaques", PLAQUES), ("etapes", ETAPES), ("chez_vous", CHEZVOUS), ("produit", PRODUIT), ("faq", FAQ)]
    out = [(k, nbsp(v)) for k, v in secs]
    out[0] = (out[0][0], css + out[0][1])
    return out

# --- Preuve de ressemblance (à activer quand les vraies photos sont dans Shopify > Fichiers) ---
PREUVE_CSS = """
.gp-proof{display:grid;gap:14px;margin-top:18px}
.gp-pair{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:12px}
.gp-pair figure{margin:0}
.gp-pair img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;border-radius:10px;display:block}
.gp-pair figcaption{font-size:12.5px;color:var(--soft);margin-top:5px;text-align:center}
.gp-pair .arr{font-size:22px;color:var(--accent);font-weight:700}
.gp-pair p{grid-column:1/-1;font-size:13.5px;color:var(--soft)}
@media(min-width:750px){.gp-proof{grid-template-columns:1fr 1fr;gap:20px}}
"""
def preuve(exemples):
    """exemples = [(url_photo, url_plaque, 'Tokyo, shiba', 'Publié avec l'accord de sa famille.'), ...]"""
    pairs = "".join(f"""<div class="gp-pair"><figure><img src="{a}" alt="Photo d'origine de {n}" loading="lazy"><figcaption>La photo reçue</figcaption></figure>
 <span class="arr" aria-hidden="true">→</span>
 <figure><img src="{b}" alt="Plaque créée pour {n}" loading="lazy"><figcaption>Sa plaque</figcaption></figure><p><b>{n}.</b> {note}</p></div>""" for a, b, n, note in exemples)
    return nbsp(f"""<div class="gp"><section class="gp-sec"><div class="gp-wrap">
 <span class="gp-kicker">Est-ce que ce sera vraiment lui ?</span>
 <h2 class="gp-h2">De la photo à la plaque</h2>
 <div class="gp-proof">{pairs}</div>
</div></section></div>""")
