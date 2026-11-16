import json, copy
G="#1f3d2c"; R="#a3312f"; GOLD="#b8893a"; CREAM="#fbf8f3"
H="font-family:var(--font-heading--family);"
css = ("<style>"
".sl-wrap{max-width:1200px;margin:0 auto}"
".sl-h{"+H+"color:"+G+";font-size:clamp(28px,5vw,40px);line-height:1.1;margin:0 0 6px;text-align:center}"
".sl-sub{color:#6b6a64;text-align:center;margin:0 0 26px;font-size:15px}"
".sl-k{display:block;text-align:center;font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:"+GOLD+";margin-bottom:8px;font-weight:600}"
"</style>")
trust = css + ("<style>.sl-trust{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;max-width:1200px;margin:0 auto}"
".sl-trust div{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid #ece4d6;border-radius:14px;padding:14px 16px}"
".sl-trust svg{flex:none;width:30px;height:30px;color:"+R+"}.sl-trust b{display:block;color:"+G+";font-size:14px}.sl-trust span{color:#6b6a64;font-size:12.5px}"
"@media(max-width:800px){.sl-trust{grid-template-columns:1fr 1fr;gap:10px}.sl-trust div{padding:12px;flex-direction:column;text-align:center;gap:6px}}</style>"
"<div class='sl-trust'>"
"<div><svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.6' stroke-linecap='round'><path d='M4 20l4-1 11-11-3-3L5 16z'/><path d='M14 6l3 3'/></svg><p style='margin:0'><b>Personnalisation offerte</b><span>Le prénom de votre choix</span></p></div>"
"<div><svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.6' stroke-linecap='round'><path d='M3 7h11v9H3zM14 10h4l3 3v3h-7'/><circle cx='7' cy='18' r='1.6'/><circle cx='17' cy='18' r='1.6'/></svg><p style='margin:0'><b>Livré avant Noël</b><span>Commandez avant le 12/12</span></p></div>"
"<div><svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.6' stroke-linecap='round'><path d='M12 3l2.5 5 5.5.8-4 3.9.9 5.5L12 15.6 7.1 18.2 8 12.7 4 8.8 9.5 8z'/></svg><p style='margin:0'><b>Imprimé en Europe</b><span>Fabriqué à la commande</span></p></div>"
"<div><svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.6' stroke-linecap='round'><rect x='4' y='10' width='16' height='10' rx='2'/><path d='M8 10V7a4 4 0 0 1 8 0v3'/></svg><p style='margin:0'><b>Paiement sécurisé</b><span>Carte, Apple Pay, PayPal</span></p></div>"
"</div>")
cats = css + ("<style>.sl-cats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}"
".sl-cat{display:block;text-decoration:none;color:"+G+"}.sl-cat .im{aspect-ratio:4/5;border-radius:16px;overflow:hidden;background:#f1ece3}"
".sl-cat img{width:100%;height:100%;object-fit:cover;transition:transform .4s}.sl-cat:hover img{transform:scale(1.04)}"
".sl-cat b{display:block;"+H+"font-size:21px;margin-top:10px}.sl-cat span{font-size:13px;color:"+R+";font-weight:600}"
"@media(max-width:800px){.sl-cats{grid-template-columns:1fr 1fr;gap:12px}.sl-cat b{font-size:17px}}</style>"
"<div class='sl-wrap'><span class='sl-k'>Cadeaux de Noël personnalisés</span><h2 class='sl-h'>Trouvez le cadeau parfait</h2><p class='sl-sub'>Pour la famille, pour bébé, pour le sapin ou pour le chocolat chaud.</p>"
"<div class='sl-cats'>{% assign hs = 'decorations-de-sapin,premier-noel-de-bebe,mugs-de-noel,en-famille' | split: ',' %}{% for h in hs %}{% assign c = collections[h] %}"
"<a class='sl-cat' href='{{ c.url }}'><div class='im'>{% if c.image %}{{ c.image | image_url: width: 700 | image_tag: loading: 'lazy', alt: c.title }}{% endif %}</div><b>{{ c.title }}</b><span>Découvrir →</span></a>{% endfor %}</div></div>")
steps = css + ("<style>.sl-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}"
".sl-step{background:#fff;border-radius:16px;padding:22px;text-align:center;border:1px solid #ece4d6}"
".sl-step i{display:inline-grid;place-items:center;width:44px;height:44px;border-radius:50%;background:"+G+";color:#fff;font-style:normal;"+H+"font-size:20px;margin-bottom:10px}"
".sl-step b{display:block;color:"+G+";font-size:16px;margin-bottom:4px}.sl-step p{margin:0;color:#6b6a64;font-size:14px}"
"@media(max-width:800px){.sl-steps{grid-template-columns:1fr;gap:10px}}</style>"
"<div class='sl-wrap'><span class='sl-k'>Simple et rapide</span><h2 class='sl-h'>Comment ça marche ?</h2><p class='sl-sub'>Votre cadeau personnalisé en 3 étapes.</p><div class='sl-steps'>"
"<div class='sl-step'><i>1</i><b>Choisissez votre article</b><p>Médaillon, mug, body ou sweat de Noël.</p></div>"
"<div class='sl-step'><i>2</i><b>Ajoutez le prénom</b><p>Touchez « Personnaliser » et voyez l'aperçu en direct.</p></div>"
"<div class='sl-step'><i>3</i><b>On imprime et on livre</b><p>Fabriqué en Europe, livré chez vous en 5 à 10 jours.</p></div>"
"</div></div>")
faq = css + ("<style>.sl-faq{max-width:760px;margin:0 auto}.sl-faq details{border-bottom:1px solid #e6dfd3;padding:6px 0}"
".sl-faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:12px;padding:12px 0;font-weight:600;color:"+G+";font-size:16px}"
".sl-faq summary::-webkit-details-marker{display:none}.sl-faq summary::after{content:'+';color:"+R+";font-size:22px;line-height:1}"
".sl-faq details[open] summary::after{content:'−'}.sl-faq p{margin:0 0 14px;color:#5f5d57}</style>"
"<div class='sl-faq'><span class='sl-k'>Vos questions</span><h2 class='sl-h' style='margin-bottom:18px'>Questions fréquentes</h2>"
"<details><summary>Vais-je recevoir ma commande avant Noël ?</summary><p>Oui, pour toute commande passée avant le 12 décembre. Chaque article est fabriqué à la commande en Europe, puis livré en 5 à 10 jours ouvrés.</p></details>"
"<details><summary>Comment ajouter le prénom ?</summary><p>Sur la page du produit, touchez le bouton de personnalisation, écrivez le prénom et vérifiez l'aperçu avant d'ajouter au panier.</p></details>"
"<details><summary>Combien coûte la livraison ?</summary><p>4,90 € en France métropolitaine, et offerte dès 35 € d'achat.</p></details>"
"<details><summary>Que se passe-t-il si mon article est abîmé ?</summary><p>Écrivez-nous à sapinetlin.contact@gmail.com avec une photo dans les 14 jours : nous le remplaçons gratuitement.</p></details>"
"</div>")
def cl(html, bg, pt=36, pb=36, width="page-width"):
    return {"type":"custom-liquid","settings":{"custom_liquid":html,"background_color":bg,"section_width":width,"padding-block-start":pt,"padding-block-end":pb}}
src = json.loads(open('index-src.json').read())
hero = src["sections"]["hero_jVaWmY"]
hero["settings"]["section_height"] = "auto" if False else hero["settings"]["section_height"]
pl = src["sections"]["product_list_fa6P9H"]
def plist(coll, title, n, bg):
    p = copy.deepcopy(pl)
    p["settings"]["collection"] = coll; p["settings"]["max_products"] = n; p["settings"]["background_color"] = bg
    p["settings"]["padding-block-start"] = 40; p["settings"]["padding-block-end"] = 40
    hb = p["blocks"]["static-header"]["blocks"]
    hb["product_list_text_YFtzcL"]["settings"]["text"] = f"<p>{title}</p>"
    hb["product_list_text_YFtzcL"]["settings"]["type_preset"] = "h3"
    hb["product_list_button_MWeP9V"]["settings"]["label"] = "Tout voir"
    return p
out = {"sections":{
  "hero_jVaWmY": hero,
  "trust": cl(trust, CREAM, 22, 22),
  "cats": cl(cats, "#ffffff", 48, 40),
  "medaillons": plist("decorations-de-sapin", "Nos médaillons de Noël", 4, CREAM),
  "steps": cl(steps, "#f4efe6", 48, 48),
  "tout": plist("all", "Toutes nos idées cadeaux", 12, "#ffffff"),
  "faq": cl(faq, CREAM, 48, 56)},
  "order":["hero_jVaWmY","trust","cats","medaillons","steps","tout","faq"]}
open('index.json','w').write(json.dumps(out, ensure_ascii=False, indent=2))
print(len(json.dumps(out)))
