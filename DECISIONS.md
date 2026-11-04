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
