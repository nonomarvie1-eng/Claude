# 🎄 L'Atelier du Père Noël — boutique de Noël

Site vitrine + panier pour vendre des cadeaux de Noël. HTML/CSS/JS pur, aucun serveur nécessaire.

## Fonctionnalités
- Compte à rebours jusqu'à Noël + rappel de la date limite de livraison (urgence = ventes)
- Catalogue filtrable (personnalisés, déco, gourmand, moins de 20 €)
- Personnalisation (prénom à graver) directement sur la fiche produit
- Panier sauvegardé, code promo (`NOEL10`), livraison offerte dès 49 € avec message « plus que X € »
- Commande envoyée par email (récapitulatif pré-rempli)
- Newsletter, avis, FAQ, responsive mobile

## Personnaliser
- **Produits, prix, codes promo, email de commande** : `products.js`
- **Couleurs** : variables en haut de `style.css`
- **Textes** : `index.html` (remplacez les avis d'exemple par de vrais avis)

## Mettre en ligne gratuitement
GitHub Pages : Settings → Pages → Branch → `/ (root)`. Ou glissez le dossier sur netlify.com/drop.

## Pour encaisser des paiements par carte
La commande part actuellement par email. Pour du paiement en ligne : liens Stripe Payment Links / PayPal sur chaque produit, ou migrer le catalogue vers Shopify.
