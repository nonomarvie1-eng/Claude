# Sapin & Lin — résumé pour reprendre le projet

> À coller au début d'une nouvelle discussion avec Claude. Le dépôt GitHub contient tout le travail sur la branche `claude/boutique-noel`.

## La boutique
- **Nom** : Sapin & Lin — cadeaux de Noël personnalisés au prénom.
- **Shopify** : sapin-et-lin.myshopify.com (plan Basic, EUR, France). Connecteur Shopify branché dans Claude.
- **Fournisseur** : Printify (impression à la demande, **imprimeurs en Europe uniquement**).
- **Propriétaire** : Marvie Noël, 1104 boulevard des Belles Portes, 14200 Hérouville-Saint-Clair. E-mail boutique : sapinetlin.contact@gmail.com. SIRET en cours.
- **Paiement** : Shopify Payments actif (versements sur Revolut).
- **Livraison** : 4,90 € (5 à 10 jours ouvrés), offerte dès 35 €. Commander avant le 12/12 pour Noël.
- **Réduction automatique** : -15 % dès 2 articles (jusqu'au 31/12).
- **Médiateur** : CM2C (adhésion en cours ; texte à mettre dans les CGV, adresse 49 rue de Ponthieu 75008 Paris à confirmer avec leur e-mail).
- **TikTok** : @sapinetlin (créé, bio et lien à finaliser).

## Les 12 produits en ligne
| Produit | Prix |
|---|---|
| Médaillon « Joyeux Noël », « Mon premier Noël », « Notre premier Noël », « La famille », « Mon chien » | 12,90 € |
| Mug « Guirlande », « Nuit dorée », « Pull de Noël » | 14,90 € |
| Body « Mon premier Noël », « Le petit renne » | 27,90 € |
| Sweat « Pull de Noël » | 36,90 € |
| Affiche « Certificat du Père Noël » (20 × 28 cm) | 12,90 € |

Plaid « La famille » : retiré (brouillon), trop cher (55 €).
Catégories : Décorations de sapin · Premier Noël de bébé · Mugs de Noël · En famille · Toutes nos idées cadeaux (ordre manuel).

## Règles importantes
- **Chaque republication depuis Printify remet le prix, les options en anglais et supprime mes photos.** Après toute republication, demander à Claude de corriger (prix, options en français, photos, metafield `printify_custom.is_personalizable = true`, **et remettre le produit dans le « Profil général » de livraison** : 4,90 €, offerte dès 35 €, France uniquement).
- **Thème** : Claude ne peut pas modifier le thème publié. Il travaille sur une copie, la personne la publie (Boutique en ligne → Thèmes → Publier).
  - En ligne : « Sapin & Lin – v4 ». Prête à publier : **« Sapin & Lin – v5 »** (bandeau « -15 % dès 2 articles · Livraison offerte dès 35 € », plus de date limite du 12/12 sur le site ; 3ᵉ photo des mugs supprimée).
- Le bouton Printify « Personnaliser » : la fenêtre Printify reste en anglais (non modifiable). L'alerte « app block missing » de Printify est à ignorer (« Publish anyway »).
- **Style des photos** : la personne n'aime pas les images qui font « IA ». Elle aime les photos studio 3D des médaillons (fond gris clair #ecebe8) et ses propres images de mise en scène générées.
- Couleurs : vert sapin #1f3d2c, rouge #a3312f, doré #b8893a / #c9a24e, crème #fbf6ec. Polices : Pinyon Script (prénoms), Cinzel (titres), Caveat (textes manuscrits des vidéos).
- Parler simplement, en français, réponses courtes (elle lit sur téléphone).

## Fait récemment
- Logo + favicon, page d'accueil refaite, menus (haut + bas de page avec CGV, livraison, etc.).
- 3 vidéos TikTok : `designs/tiktok/medaillons-tiktok.mp4`, `designs/tiktok/pub/sapin-et-lin-pub-hd.mp4` (médaillons, 30 s), `designs/tiktok/mugs/sapin-et-lin-mugs.mp4` (mugs, 28 s).
- **Nouveaux designs de mugs** (rouge pull de Noël, vert sapin avec médaillon, crème guirlande) : `designs/mugs-v2/` — **à importer dans Printify** à la place des 3 mugs actuels, puis prévenir Claude.

## Point du 28/10 (avant ouverture)
- Livraison corrigée : tous les produits sont dans le Profil général, France seulement, 4,90 € ou offerte dès 35 € (avant : tarifs Printify de 5,69 à 7,79 €, jamais offerts).
- Médaillons fabriqués par Harrier, probablement au Royaume-Uni (délai annoncé par Printify : 13 à 35 jours ouvrés vers la France). À vérifier dans Printify.
- CGV : médiateur encore « à compléter ».

## À faire (dans l'ordre)
1. Publier la **v4** du thème.
2. Importer les **3 nouveaux mugs** dans Printify (fichiers `designs/mugs-v2/*-sans-prenom.png`), puis Claude corrige prix/options/photos.
3. Bandeau d'annonce : fait dans la v5.
4. **Commande test** (payer, vérifier le prénom dans Printify → Orders, annuler et rembourser).
5. Ajouter le **médiateur CM2C** dans les CGV.
6. Acheter **sapinetlin.fr** sur IONOS (6 € TTC la 1ʳᵉ année, sans options) puis le relier à Shopify (Claude guide).
7. **Ouvrir la boutique** (Préférences → retirer le mot de passe).
8. TikTok : bio, lien, publier les vidéos (18 h-21 h, un jour d'écart).

## Idées en attente
Nouveaux modèles possibles (choisis sur une planche d'idées) : médaillon « Renne enchanté », mug « Esprit de Noël » (renne doré sur vert), mug « Bonhomme de neige », body « Pain d'épices », body « Renne craquant ».
Pas disponibles en Europe sur Printify : chaussette/botte de Noël, bavoir, bandana chien, vraie boule ronde.
