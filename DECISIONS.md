# DECISIONS

## D-001 — 2026-11-04 — Aucun produit validé
Décision : aucune opportunité ne passe le jalon 1 complet. Deux pistes sont gardées pour vérification, une en veille, sept rejetées.
Justification : les prix fournisseurs, volumes de recherche et prix Amazon.fr n'ont pas pu être vérifiés (accès bloqué). Sans eux, la marge et la demande restent des hypothèses.

## D-002 — 2026-11-04 — Seuil de prix minimum ~50 € pour un produit expédié de Chine
Justification : depuis le 1er juillet 2026, droit UE de 3 € par catégorie d'article + TVA import (non récupérable en franchise) + frais de traitement UE (montant inconnu, 0–2 €). Sur un produit à 30 €, cela pèse 13–20 % du prix. Le modèle (`tools/unit_economics.py`) montre une marge pessimiste proche de zéro pour les paniers ≤ 35 €.
Exception : panier relevé par des lots (ex. 2 kits = une seule catégorie tarifaire, un seul droit de 3 € — à confirmer).

## D-003 — 2026-11-04 — Rejets
Filtre de douche (promesse anticalcaire non tenue selon test indépendant), masque de sommeil 3D (guerre des prix), masque lesté (brevet), tabouret WC (encombrant, concurrent FR made in France), tapis d'acupression (allégations santé), mouth tape (risque santé et réglementaire), accessoires espresso (panier trop faible, compatibilité). Détail : `OPPORTUNITIES.csv`.

## D-004 — 2026-11-04 — Pas d'objectif Noël 2026
Échantillon + boutique + délais Chine → impossible de garantir des livraisons avant Noël sans précipiter les jalons 3 à 5.

## D-005 — 2026-11-04 — Le client ne paiera jamais de frais à la livraison
Toute offre devra être en DDP (droits et TVA réglés en amont). Un client qui reçoit une demande de paiement du transporteur = remboursement, mauvais avis et risque de litige.

## D-006 — 2026-11-04 (soir) — L'aiguiseur passe sous le seuil avec les prix réels
Données AliExpress relevées : un modèle de qualité correcte coûte 28–32 $ (prix public), les basiques 4–7 $. Avec ce coût, marge 18 % à 59,90 € et 28 % à 69,90 € (CPA max 10–20 €). Seuil fixé : 35 % et CPA max ≥ 20 €. → Piste maintenue **uniquement** si un devis fournisseur (CJ ou usine) donne ~15 € rendu pour une qualité vérifiée. Sinon, abandon.

## D-007 — 2026-11-04 (soir) — Pas de contournement des protections anti-robot
Amazon.fr bloque les requêtes automatisées : relevé à faire manuellement (10 min) plutôt que de contourner.

## D-008 — 2026-11-04 (nuit) — Les trois pistes restantes sont rejetées
Source : captures Google Shopping France fournies par le fondateur (relevé : `data/google_shopping_2026-11-04.csv`).
- **Aiguiseur** : au moins 4 boutiques françaises paient déjà des pubs sur le même produit générique (mêmes photos), et AliExpress s'affiche dans le même carrousel à 4,79–14,69 €.
- **Kit crochet** : Mypeluchic occupe exactement notre positionnement (5 annonces, 29,99–49,90 €). Nature & Découvertes vend aussi des kits débutant « avec vidéos ».
- **Pressuriseur padel** : premium (Bounce ~90–100 €) et entrée de gamme (~20 €, Decathlon, Amazon, AliExpress) déjà pris.

**Leçon :** un produit générique chinois vendu en France se retrouve à côté de sa propre version AliExpress sur Google Shopping. Avec le droit de 3 € et des délais de 6–14 jours, ce modèle n'offre pas de raison crédible de nous choisir.

**Nouveaux critères pour la prochaine recherche** (au moins un obligatoire) :
1. **Stock en Europe** (fournisseur UE qui accepte le dropshipping) : pas de droit de 3 €, livraison en 2–5 jours, un vrai avantage face à AliExpress.
2. **Personnalisation** (gravure, prénom, contenu sur mesure) : la comparaison de prix devient impossible.
3. **Produit absent d'AliExpress** sous la même forme (fabricant ou artisan européen).

## D-009 — 2026-11-04 — Recherche n°2 : modèles d'approvisionnement
- AliExpress avec stock UE : utile pour la logistique seulement. Le client voit la même annonce AliExpress, elle aussi livrée vite.
- BigBuy / grossistes UE : rejetés (abonnement 69–120 €/mois + ~90 € d'inscription, produits vendus partout).
- Impression à la demande UE (Gelato/Printful) : seule voie qui rend la comparaison de prix impossible, mais niches génériques saturées (ex. affiches de course : The Post Trace à 18 €).
- La niche doit partir d'une expertise ou d'une passion du fondateur. Question posée au fondateur. Détail : `RAPPORT_DECISION_02.md`.

## D-009 — 2026-11-04 — Recherche n°2 : modèles d'approvisionnement
- AliExpress avec stock UE : utile pour la logistique seulement. Le client voit la même annonce AliExpress, elle aussi livrée vite.
- BigBuy / grossistes UE : rejetés (abonnement 69–120 €/mois + ~90 € d'inscription, produits vendus partout).
- Impression à la demande UE (Gelato/Printful) : seule voie qui rend la comparaison de prix impossible, mais niches génériques saturées (ex. affiches de course : The Post Trace à 18 €).
- La niche doit partir d'une expertise ou d'une passion du fondateur. Question posée au fondateur. Détail : `RAPPORT_DECISION_02.md`.

## D-010 — 2026-11-04 — Niche tennis retenue comme terrain de recherche
Raison : le fondateur joue au tennis et le regarde → contenu crédible sans visage. Piste n°1 à vérifier : **kit de cordage à domicile** (`RAPPORT_DECISION_03_TENNIS.md`). Viable seulement avec un prix usine ~100 € pour la machine. Surgrips, appareil de rebond et pressuriseur rejetés ; vêtements et cadeaux personnalisés en veille.

## D-011 — 2026-11-04 — Kit de cordage abandonné
Le fondateur ne sait pas corder, ne souhaite pas apprendre et joue occasionnellement, pour le plaisir. Or l'avantage de cette piste reposait sur une expertise crédible (tutoriels, conseils) face à des clients exigeants. Sans elle, il ne reste qu'un produit lourd, cher, à risque de retours, vendu face à des spécialistes (Tennispro, Tennis Warehouse). → **Rejeté.**
Constat honnête : après 3 recherches (14 pistes produits, 4 modèles d'approvisionnement), aucune piste ne combine demande prouvée + différenciation + économie unitaire compatible avec le profil (débutant, sans visage, sans expertise métier, 500–1 000 €). Le choix de la suite revient au fondateur (options dans NEXT_ACTIONS.md).

## D-012 — 2026-11-04 — Recherche hors tennis : une piste à tester
Marque de designs dédiée à une race de chien, imprimée à la demande en Europe (`RAPPORT_DECISION_04_AUTRES_UNIVERS.md`). C'est le risque en capital le plus faible trouvé, mais avec une marge faible (CPA max 8–18 €) : la croissance devra venir du contenu et de la communauté, pas de la pub. Moto, auto, bricolage, fitness et tapis gaming rejetés.

## D-013 — 2026-11-04 — Race choisie et designs par IA
- Le fondateur n'a pas de chien et ne paiera pas d'illustrateur. Designs générés par IA puis **retravaillés** : une image IA brute est probablement non protégée en France, donc copiable par un concurrent.
- Race choisie sur données : **berger australien** (~14 600 naissances LOF en 2025, 4 robes distinctes → personnalisation). Plan B : golden retriever.
- Étape suivante à coût nul : compte Instagram/TikTok pendant 30 jours (`PLAN_TEST_30J.md`), décision selon les demandes d'achat spontanées.
- Risque signalé : sans chien ni lien personnel avec la race, le ton doit rester juste. S'appuyer sur la communauté (avec autorisations) plutôt que de feindre une expérience de propriétaire.

## D-014 — 2026-11-04 — Leçon de l'exemple « Lanoxie » (déboucheur en poudre)
Exemple montré par le fondateur (vidéo TikTok d'un coach) : produit banal de résolution de problème, consommable, marque propre, prix Alibaba 0,62–0,84 € l'unité dès 50 pièces, ~40 pubs Meta actives (FR, BE, CA), ~15 000 visites/mois (estimation Trendtrack, non vérifiée).
**Ce qu'on retient (le fondateur a raison) :** un produit « ennuyeux » peut fonctionner s'il règle un problème, se rachète, porte une vraie marque et que la vente est bien faite. Notre filtre ne doit pas exiger un produit révolutionnaire.
**Ce qu'on ne copie pas :**
- Produit chimique : déboucheurs généralement classés dangereux (pictogramme corrosif, « Danger »), étiquetage CLP en français, code UFI et déclaration aux centres antipoison obligatoires. L'allégation « désinfecte » relève a priori du règlement biocides : vérification séparée nécessaire. Transport aérien de matières dangereuses restreint. Coût et risque juridique trop élevés pour nous.
- Avis Trustpilot partagés (« toujours bouché », accusation de faux avis) : la pub ne prouve ni la satisfaction ni la rentabilité.
- Les chiffres viennent d'une vidéo de coach qui vend une formation : biais du survivant.
**Changement de modèle à envisager :** prix de gros très bas (50 pièces < 50 €) → un **micro-stock en marque propre** (étiquette FR, stock en France) devient abordable pour des consommables bon marché. C'est ce qui distingue ces marques d'AliExpress : marque, livraison rapide depuis la France, service. Décision du fondateur attendue (accepter 100–200 € de stock ?).
Sources : [Trustpilot Lanoxie](https://uk.trustpilot.com/review/lanoxie.com), [Your Europe — CLP](https://europa.eu/youreurope/business/product-requirements/chemicals/classification-labelling-packaging/index_fr.htm), [EcoMundo — PCN/UFI](https://ecomundo.eu/blog/declaration-pcn-melanges-dangereux-ufi), [INRS](https://www.inrs.fr/risques/classification-etiquetage-produits-chimiques/ce-qu-il-faut-retenir.html).
