# Passage sur Shopify – La Boutique de Mme Fofana

Tout ce qu'il faut pour créer la boutique Shopify à partir du site actuel (`index.html`).
Boutique : **mmefofana.myshopify.com** (La boutique de Mme Fofana, EUR, forfait Basic).

## État dans Shopify (29 octobre 2026)

Fait automatiquement avec le connecteur Shopify :

- [x] Métadonnée produit `custom.caracteristiques` (texte multiligne, lisible par la boutique)
- [x] 7 produits créés avec photos (19), poids, stock, caractéristiques ; 5 en ligne, 2 grands mortiers en brouillon ; tous visibles sur la Boutique en ligne
- [x] Collections automatiques Cuisine (5 produits) et Service de table (2), publiées
- [x] Livraison France : 14 tarifs Mondial Relay (Point Relais et Domicile par tranche de poids). Les anciens tarifs Shopify (Standard 7,99 €, gratuit dès 65 €, Express) et les zones International et UE ont été supprimés
- [x] Remise automatique « Livraison offerte dès 110 € » (France)
- [x] Pages Mentions légales, CGV, Livraison et retours, Politique de confidentialité, À propos (modèle `a-propos`)
- [x] Menu principal : Accueil, Boutique, À propos, Contact (Linktree)
- [x] Thème « Mme Fofana » importé, **non publié**

Reste à faire à la main dans l'admin Shopify :

- [ ] Boutique en ligne › Thèmes : prévisualiser « Mme Fofana » puis **Publier** (le connecteur ne peut pas publier un thème)
- [ ] Réglages › Politiques : coller les textes de `pages/` (le connecteur n'a pas le droit de modifier les politiques)
- [ ] Réglages › Taxes : vérifier que la TVA n'est pas facturée (franchise en base)
- [ ] Installer l'application Sendcloud ou Mondial Relay pour le choix du Point Relais au paiement
- [ ] Mettre le vrai poids de la grande taille Côte d'Ivoire (0 g actuellement)

## Deuxième thème : « Mme Fofana – Horizon » (essai, non retenu : on garde « Mme Fofana »)

Copie du thème officiel Shopify **Horizon 4.3.0**, habillée aux couleurs de la boutique. Non publié : le thème « Mme Fofana » reste le choix par défaut.

- Seuls quelques fichiers diffèrent d'Horizon : `theme-horizon/config/settings_data.json` et les fichiers générés par `theme-horizon/build.py` (accueil, fiche produit, page À propos, en-tête, pied de page).
- Logo et favicon : `theme-horizon/images/` (envoyés dans Contenu › Fichiers).
- Accueil : grande photo, bandeau défilant, « Les Trésors de Chez Nous » en carrousel, « Par univers » (Cuisine / Service de table), À propos, 4 engagements, newsletter.
- Fiche produit : galerie avec vignettes et zoom, stock restant, réassurance livraison, onglets Caractéristiques (métadonnée), Livraison, Retours, Pièce artisanale, barre d'achat fixe.
- Tout est modifiable dans l'éditeur de thème Shopify (glisser-déposer des sections et blocs).
- Aperçu : Boutique en ligne › Thèmes › « Mme Fofana – Horizon » › Aperçu.

## Contenu

| Dossier / fichier | Rôle |
|---|---|
| `catalogue/products.json` | Les 7 produits Shopify (5 en ligne, 2 en brouillon), générés depuis `index.html` |
| `catalogue/products.csv` | Le même catalogue au format d'import Shopify (Produits › Importer) |
| `catalogue/generer-catalogue.js` | Régénère les deux fichiers ci-dessus si le site change |
| `images/` | Les 19 photos produits extraites de `index.html` |
| `livraison.json` | Tarifs Mondial Relay France (Point Relais et domicile) |
| `pages/` | Mentions légales, CGV, livraison et retours, confidentialité (HTML prêt à coller) |
| `theme/` | Le thème Shopify qui reprend le design du site |
| `mme-fofana-theme.zip` | Le thème zippé, à importer dans Boutique en ligne › Thèmes |

## Produits

| Produit | Statut | Variantes | Prix | Poids | Stock |
|---|---|---|---|---|---|
| Plateau – Forme Afrique | En ligne | 1 compartiment / 2 compartiments | 32,90 € | 470 g | 3 / 1 |
| Plateau – Forme Côte d'Ivoire | En ligne | Moyenne / Grande | 29,90 € | 430 g / **0 g** | 2 / **0** |
| Talier en aluminium avec pilon | En ligne | – | 24,90 € | 940 g | 5 |
| Mortier artisanal en bois avec pilon | En ligne | – | 34,90 € | 1 200 g | 6 |
| Mortier traditionnel sculpté avec pilon | En ligne | – | 44,90 € | 2 600 g | 5 |
| Grand mortier traditionnel – Côte d'Ivoire | Brouillon | – | 54,90 € | 5 000 g | 2 |
| Imposant mortier traditionnel – Bois massif | Brouillon | – | 64,90 € | 10 000 g | 1 |

- Sur le site, les deux plateaux existaient chacun en deux fiches reliées. Sur Shopify, chaque plateau devient un seul produit avec deux variantes.
- La grande taille Côte d'Ivoire est en rupture (stock 0, vente en rupture refusée).
- Les caractéristiques vont dans la métadonnée produit `custom.caracteristiques` (texte multiligne, une ligne par caractéristique, « Libellé : valeur »). Le thème les affiche dans « Caractéristiques ».
- Le type de produit (`Cuisine` ou `Service de table`) sert de catégorie.

## Collections

Deux collections automatiques :
- **Cuisine** : type de produit égal à `Cuisine`
- **Service de table** : type de produit égal à `Service de table`

## Livraison (France)

Tarifs Sendcloud TTC arrondis aux 5 centimes. Shopify calcule sur le poids des produits seuls, donc chaque tranche est décalée des 300 g d'emballage (colis ≤ 0,5 kg = produits ≤ 0,2 kg, etc.).

| Poids du colis (emballage compris) | Produits seuls | Point Relais | Domicile |
|---|---|---|---|
| ≤ 0,5 kg | ≤ 0,2 kg | 4,15 € | 7,50 € |
| ≤ 1 kg | ≤ 0,7 kg | 4,55 € | 9,50 € |
| ≤ 2 kg | ≤ 1,7 kg | 6,35 € | 11,00 € |
| ≤ 3 kg | ≤ 2,7 kg | 6,75 € | 16,35 € |
| ≤ 5 kg | ≤ 4,7 kg | 13,40 € | 16,35 € |
| ≤ 10 kg | ≤ 9,7 kg | 13,40 € | 25,00 € |
| ≤ 15 kg | ≤ 14,7 kg | 21,00 € | 31,50 € |

Au-delà de 14,7 kg de produits, aucun tarif ne s'affiche (comme sur le site : devis à la demande).

## Thème

Thème Online Store 2.0 (sections JSON), en français, contrôlé avec l'outil officiel `theme-check` (aucune erreur).

- Accueil : grande photo, banderole défilante, bande de confiance, « Des objets, des histoires, des savoir-faire ». L'histoire de Mme Fofana est seulement sur la page À propos (menu).
- Slogan du logo : « Traditions, créations & art de vivre ».
- Boutique : recherche, catégories, filtres Shopify (disponibilité, prix), tri, pagination.
- Fiche produit : galerie avec flèches et vignettes, boutons de variante (rupture barrée), quantité limitée au stock, alerte « me prévenir » (formulaire de contact), caractéristiques, barre d'achat fixe sur mobile, « Tu aimeras aussi ».
- Panier en tiroir avec jauge « livraison offerte », page panier, pages légales, 404, recherche.
- Couleurs, textes, photos, liens des réseaux et seuil de livraison offerte modifiables dans l'éditeur de thème.

Pour la page À propos : créer une page « À propos » (adresse `a-propos`) et lui donner le modèle `a-propos`.

## Étapes dans Shopify

1. Vérifier la boutique connectée (nom, domaine) : ce doit être celle de Mme Fofana, **pas « Sapin & Lin »**.
2. Réglages : devise EUR, langue française, taxes désactivées (franchise en base de TVA).
3. Créer la définition de métadonnée produit `custom.caracteristiques` (texte multiligne).
4. Créer les 7 produits de `catalogue/products.json`, avec photos, poids, stock ; les deux grands mortiers en brouillon.
5. Créer les collections Cuisine et Service de table.
6. Créer la zone France et les deux tarifs de `livraison.json` ; la remise « livraison offerte dès 110 € » si elle est confirmée.
7. Créer les 4 pages depuis `pages/` (adresses : `mentions-legales`, `conditions-generales-de-vente`, `livraison-et-retours`, `politique-de-confidentialite`) et recopier les textes dans Réglages › Politiques.
8. Importer `mme-fofana-theme.zip`, créer la page À propos, vérifier puis publier.

## Points à décider ou compléter

- **Poids de la grande assiette Côte d'Ivoire** : 0 g sur le site. Sans poids réel, le calcul de livraison sera faux le jour où elle revient en stock.
- **Livraison offerte dès 110 €** : présente sur le site et dans la page Livraison, mais absente de la demande. Elle est prévue sous forme de remise automatique, à confirmer.
- **Autres pays** : le site livrait aussi Belgique, Luxembourg, Pays-Bas, Espagne, Portugal, Italie et Pologne. Seule la France est prévue ici, et la page Livraison a été ajustée en conséquence.
- **Choix du Point Relais au paiement** : Shopify ne propose pas de sélecteur de point relais par défaut. Il faut l'application Sendcloud (déjà utilisée pour les étiquettes) ou l'application Mondial Relay.
- **Mentions légales** : l'adresse de l'éditrice (domiciliation) et le médiateur de la consommation sont obligatoires et manquent déjà sur le site.
- **Pages légales adaptées** : l'hébergeur devient Shopify, le paiement passe par Shopify (plus Stripe), les prestataires et les cookies (Shopify dépose des cookies techniques, et de mesure seulement avec accord via son bandeau) sont mis à jour.
