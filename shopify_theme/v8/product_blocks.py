# Blocs de la fiche produit : formulaire de personnalisation + « ce que vous recevez ».
from sections import FONTS, BASE_CSS, nbsp

PERSO_CSS = """
.gp-perso{background:#f7f0e3;border-radius:18px;padding:16px;display:grid;gap:14px}
.gp-perso h3{font-size:18px;font-weight:700}
.gp-perso__sub{font-size:14px;color:#56607a;margin-top:2px}
.gp-f label{display:block;font-weight:700;font-size:14.5px;margin-bottom:5px}
.gp-f label i{font-style:normal;font-weight:500;color:#56607a}
.gp-f input[type=text],.gp-f textarea{width:100%;font:inherit;font-size:16px;color:#1b2a4a;background:#fff;border:1.5px solid #ddd2bf;border-radius:12px;padding:11px 13px;outline:none}
.gp-f input[type=text]:focus,.gp-f textarea:focus{border-color:#1b2a4a}
.gp-f textarea{min-height:92px;resize:vertical}
.gp-f small{display:block;font-size:12.5px;color:#56607a;margin-top:4px}
.gp-photo{border:1.5px dashed #c9b998;background:#fff;border-radius:14px;padding:14px;text-align:center}
.gp-photo input[type=file]{width:100%;font:inherit;font-size:14px}
.gp-photo ul{list-style:none;padding:0;margin:10px 0 0;text-align:left;font-size:13px;color:#56607a;display:grid;gap:3px}
.gp-perso__foot{font-size:13px;color:#56607a}
.accelerated-checkout-block{display:none!important}
"""

PERSO = """
{%- liquid
  assign gp_handle = product.handle
  assign fid = 'BuyButtons-ProductForm-' | append: section.id
-%}
<div class="gp"><div class="gp-perso" id="gp-perso" data-form="{{ fid }}">
 <div><h3>Personnalisez sa plaque</h3><p class="gp-perso__sub">Tout se remplit ici, avant le paiement. Vous recevrez l'aperçu par e-mail.</p></div>
 <div class="gp-f"><label for="gp-prenom">Son prénom</label>
  <input type="text" id="gp-prenom" name="properties[Prénom]" form="{{ fid }}" maxlength="12" required placeholder="Tokyo"><small>12 caractères maximum.</small></div>
{%- if gp_handle contains 'petit-toutou' -%}
 <div class="gp-f"><label for="gp-betise">Sa plus grosse bêtise</label>
  <input type="text" id="gp-betise" name="properties[Bêtise]" form="{{ fid }}" maxlength="40" required placeholder="a mangé la télécommande"><small>Elle deviendra le sous-titre du journal. 40 caractères maximum.</small></div>
 <div class="gp-f"><label for="gp-date">Date du journal <i>(facultatif)</i></label>
  <input type="text" id="gp-date" name="properties[Date du journal]" form="{{ fid }}" maxlength="20" placeholder="14 avril 2021"><small>Son adoption, son anniversaire… Sinon, on choisit pour vous.</small></div>
{%- elsif gp_handle contains 'avenue' -%}
 <div class="gp-f"><label for="gp-titre">Son titre officiel</label>
  <input type="text" id="gp-titre" name="properties[Titre]" form="{{ fid }}" maxlength="25" required placeholder="Chef du canapé"><small>25 caractères maximum.</small></div>
 <div class="gp-f"><label for="gp-annee">Année de son arrivée</label>
  <input type="text" id="gp-annee" name="properties[Année d'arrivée]" form="{{ fid }}" maxlength="4" inputmode="numeric" pattern="[0-9]{4}" required placeholder="2021"></div>
{%- elsif gp_handle contains 'chateau' -%}
 <div class="gp-f"><label for="gp-mill">Millésime</label>
  <input type="text" id="gp-mill" name="properties[Millésime]" form="{{ fid }}" maxlength="4" inputmode="numeric" pattern="[0-9]{4}" required placeholder="2021"><small>Son année de naissance ou d'adoption.</small></div>
{%- elsif gp_handle contains 'pere-noel' -%}
 <div class="gp-f"><label for="gp-voeux">Ses 3 vœux</label>
  <textarea id="gp-voeux" name="properties[Vœux]" form="{{ fid }}" maxlength="120" required placeholder="un canapé rien qu'à moi&#10;des chaussettes à voler&#10;une montagne de madeleines"></textarea><small>Un vœu par ligne, 120 caractères au total.</small></div>
{%- endif -%}
 <div class="gp-f gp-photo"><label for="gp-photo">Sa photo</label>
  <input type="file" id="gp-photo" name="properties[Photo]" form="{{ fid }}" accept="image/jpeg,image/png,image/heic,image/webp" required>
  <ul><li>✓ Nette et bien éclairée, sans filtre</li><li>✓ La tête bien visible, de face ou de trois-quarts</li><li>✓ Une photo récente, prise au téléphone, suffit</li></ul></div>
 <div class="gp-f"><label for="gp-note">Une précision ? <i>(facultatif)</i></label>
  <input type="text" id="gp-note" name="properties[Précision]" form="{{ fid }}" maxlength="80" placeholder="c'est un chat, collier rouge…"></div>
 <p class="gp-perso__foot">Si la photo ne permet pas un bon portrait, on vous en demande une autre avant de commencer.</p>
</div></div>
<script>
(function(){var w=document.getElementById('gp-perso');if(!w)return;var id=w.dataset.form;
 if(!document.getElementById(id)){var f=document.querySelector('form[id^="BuyButtons-ProductForm-"]');if(f){id=f.id;}}
 w.querySelectorAll('input,textarea').forEach(function(el){el.setAttribute('form',id);});})();
</script>
"""

RECU = """
<div class="gp"><dl class="gp-spec2">
 <div><dt>La plaque</dt><dd>Aluminium imprimé, 20 × 30 cm. Plaque plate : rivets et usure sont imprimés. Pour l'intérieur.</dd></div>
 <div><dt>L'aperçu</dt><dd>Par e-mail sous 48 h ouvrées après la commande. Jusqu'à 2 séries de corrections incluses. Rien n'est imprimé sans votre accord.</dd></div>
 <div><dt>Le délai</dt><dd>Environ 3 semaines entre votre validation et la livraison. Livraison offerte en France métropolitaine, avec suivi.</dd></div>
 <div><dt>Un souci ?</dt><dd>Plaque abîmée ou différente de l'aperçu validé : on la refait ou on vous rembourse.</dd></div>
</dl></div>
"""
RECU_CSS = """
.gp-spec2{margin:0;border-top:1px solid #e7dfd0}
.gp-spec2 div{padding:11px 0;border-bottom:1px solid #e7dfd0}
.gp-spec2 dt{font-family:'Poppins',sans-serif;font-weight:700;font-size:14.5px}
.gp-spec2 dd{margin:2px 0 0;font-size:14.5px;color:#56607a}
"""

def perso_block():
    return FONTS + "<style>" + BASE_CSS + PERSO_CSS + RECU_CSS + "</style>" + nbsp(PERSO)
def recu_block():
    return nbsp(RECU)
