# NEXT ACTIONS

Classées par impact sur la décision. ⛔ = nécessite votre accord ou votre action.

## ⚠️ 2026-11-04 (nuit) — 3 pistes rejetées (D-008), recherche n°2 faite (D-009). EN ATTENTE : centres d'intérêt et compétences du fondateur pour choisir la niche.
Prochaine action : recherche n°2 avec les nouveaux critères (stock UE, personnalisation, produit absent d'AliExpress). Aucun compte CJ ni Amazon nécessaire.

## 0. (caduc) Mise à jour 2026-11-04 (soir) — ce qui reste après ouverture du réseau
1. ⛔ **Devis CJ (votre compte gratuit, aucun paiement)** : aiguiseur « 4 angles, disques 360/600 + céramique, support magnétique » et kit crochet amigurumi. Il me faut : prix unitaire, port France DDP, délai, poids. **C'est le test décisif pour l'aiguiseur** : il faut ~15 € rendu pour une qualité correcte.
2. **Relevé Amazon.fr manuel (10 min)** : pour « aiguiseur à rouleau » et « kit crochet débutant », noter les 5 premiers résultats non sponsorisés : prix, note, nombre d'avis, mention « X achetés le mois dernier ». Une capture d'écran suffit.
3. Optionnel : ajouter `*.service-public.gouv.fr` aux domaines autorisés (vérification officielle des seuils TVA).
4. Expert-comptable : poser la question du régime « dropshipping avec minoration de la base à l'importation » (cité par la douane).

## 1. Débloquer les données (fait le 2026-11-04 — voir PROJECT.md pour ce qui reste bloqué)
- ⛔ **Autoriser des domaines réseau** dans les réglages de l'environnement cloud (voir PROJECT.md) : amazon.fr, aliexpress, cjdropshipping.com, trends.google.com, facebook.com (Ad Library), douane.gouv.fr, service-public.fr. Coût : 0 €. Effet : je pourrai relever prix, avis, publicités actives et textes officiels moi-même.
- À défaut, **10 minutes de votre côté** : créer un compte gratuit CJdropshipping (aucun paiement) et me copier pour « rolling knife sharpener » et « beginner crochet kit » : prix produit, prix de livraison France (option DDP), délai. Je n'ai pas le droit de créer ce compte à votre place.

## 2. Vérifier la demande française (gratuit)
- Google Trends FR 5 ans : « aiguiseur couteau », « aiguiseur à rouleau », « HORL », « kit crochet », « crochet débutant », « amigurumi ».
- Amazon.fr : top 10 aiguiseurs à rouleau et kits crochet débutant (prix, nombre d'avis, avis 1-2 étoiles = objections).
- Meta Ad Library (pays : France) : annonceurs actifs sur « aiguiseur rouleau » et « kit crochet », ancienneté des pubs.

## 3. Questions à faire valider par un professionnel (avant toute vente)
- Expert-comptable : traitement TVA à l'import en dropshipping pour une micro-entreprise en franchise (IOSS accessible ou non ? qui est l'importateur ?).
- REP : filières concernées (emballages ; ASL pour un produit sport) et obligations pour un petit volume.

## 4. Brouillon de demande de devis (NE PAS ENVOYER sans votre accord)
> Subject: Quotation request — rolling knife sharpener, dropshipping to France (DDP)
>
> Hello,
> We are a new French brand preparing a test launch in France. We are interested in your rolling knife sharpener with magnetic angle holder (diamond + ceramic discs).
> Could you please send:
> 1. Unit price for dropshipping (1 unit per order) and for 50 / 200 units.
> 2. Shipping cost and transit time to France, DDP (all EU duties and VAT paid, no fee for the customer at delivery), and the tracking method.
> 3. Grit of each disc, materials, magnet strength, product weight with packaging.
> 4. The name and address of the EU responsible economic operator (GPSR), product safety documentation, and the HS code you declare.
> 5. Defective item policy and return handling.
> 6. Sample price and lead time, and whether a custom insert card can be added.
> Thank you,
> [Nom], [Marque provisoire]

## 5. Après réception des données
- Mettre à jour `UNIT_ECONOMICS.csv` avec les vrais prix → relancer `python3 tools/unit_economics.py`.
- Si marge centrale ≥ 35 % et CPA max ≥ 20 € → proposer l'achat de 2 échantillons concurrents (~60 € au total) avec un protocole de test écrit à l'avance. ⛔
