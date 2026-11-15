# Évaluation commerciale — Golden Rally

Légende : **[V]** vérifié (source officielle consultée) · **[S]** source secondaire, à confirmer · **[H]** hypothèse de travail · **[?]** inconnu.

> Aucune mise théorique ne garantit un revenu. Tous les montants ci-dessous sont des simulations de scénarios, pas des prévisions.

## 1. Plateformes de distribution envisageables

| Voie | Accès pour un studio débutant | Statut |
|---|---|---|
| **Stake Engine** (Stake.com, Stake.us) | Inscription directe, fichiers statiques, RGS fourni | Voie principale. Format compatible **[V]** ; conditions contractuelles **[?]** |
| Programmes « Powered By » de fournisseurs licenciés (agrégateurs ou studios qui distribuent des jeux tiers) | Sélectif : portfolio et sélection demandés | **[H]** possible dans un second temps |
| Vente ou licence de la propriété intellectuelle (maths, art, code) à un studio licencié | Négociation de gré à gré | **[H]** |
| Casino social / jeux sans argent réel | Moins de contraintes réglementaires, revenus publicitaires ou d'achats intégrés | **[H]** demande d'adapter le modèle économique |
| Vente directe à des opérateurs | Exige des licences B2B, une certification par laboratoire et un RGS agréé par marché | Hors de portée à court terme **[H]** |

## 2. Critères d'admission connus (Stake Engine)

- Fichiers mathématiques au format exigé, RTP de 96,0 à 96,7 % selon le SDK, mode de base à 1×, écart-type de base ≥ 0,6, contrôles de risque **[V]**. Golden Rally les passe tous (outil officiel, voir `MATH_REPORT.md`).
- Interface : RTP et gain maximal affichés pour chaque mode, langues et devises supportées, drapeaux de juridiction respectés **[S]**/**[V partiel]**.
- Revue humaine par Stake : un rapport automatique propre n'est pas une approbation **[S]**.

## 3. Rémunération documentée

- **10 % du GGR** (mises − gains) généré par le jeu, versé mensuellement **[S]** (blog Stake, easygo.io, presse spécialisée).
- Calcul exact du GGR, traitement des mois où le GGR est négatif, devises, fiscalité, seuil de paiement : **[?]**.

Avec le RTP exact de 96,4857 %, l'avantage maison vaut 3,514 % des mises. Sur la durée, la part du studio est donc d'environ **0,351 % des mises** (10 % × 3,514 %).

## 4. Coûts identifiés

| Poste | Montant | Statut |
|---|---|---|
| Production des visuels et sons | 0 € (procédural, réalisé) | **[V]** |
| Développement, maths, tests | 0 € de sous-traitance (réalisé ici) ; temps de maintenance du studio | **[V]** |
| Hébergement | 0 € si Stake héberge les fichiers statiques (CDN Stake documenté) | **[S]** |
| Frais d'inscription Stake Engine | Aucun frais trouvé dans les sources accessibles | **[?]** |
| Revue juridique du contrat | 1 500 – 4 000 € | **[H]** |
| Dépôt de marque EUIPO (1 classe) | ~850 € (+ recherche d'antériorité) | **[H]** (barème public courant, à vérifier) |
| Structure juridique et comptabilité | 500 – 2 000 €/an selon le pays | **[H]** |
| Certification par laboratoire (si exigée hors Stake) | 5 000 – 20 000 € par jeu et par marché | **[H]** |
| Licence B2B (vente directe aux opérateurs) | Dizaines de milliers d'euros par an et par juridiction | **[H]** |
| Maintenance (mises à jour, traductions, support) | ~150 €/mois de temps valorisé | **[H]** |

## 5. Scénarios (voie Stake Engine, montants mensuels, hypothèse 1 € ≈ 1 $)

| Scénario | Mises mensuelles **[H]** | GGR attendu | Part studio attendue (10 %) |
|---|---|---|---|
| Pessimiste | 20 000 $ | 703 $ | **70 $** |
| Central | 300 000 $ | 10 543 $ | **1 054 $** |
| Optimiste | 3 000 000 $ | 105 430 $ | **10 543 $** |

Les volumes sont des hypothèses. Stake annonce environ 3,3 milliards de dollars de mises par an sur l'ensemble des jeux Engine **[S]**, mais leur répartition entre des centaines de jeux n'est pas publiée **[?]**. La visibilité dans le lobby détermine l'essentiel du volume et n'est pas maîtrisée par le studio.

**Volatilité du revenu** : avec un écart-type de 6,5× la mise par tour, 300 000 $ de mises en tours de 1 $ donnent un GGR mensuel de 10 543 $ ± 3 574 $ (1 écart-type). En tours de 10 $, l'écart-type monte à ± 11 303 $ : un mois **négatif** est alors plausible. Ce qu'il advient d'un GGR négatif dans le contrat est **[?]**.

## 6. Seuil de rentabilité

Part du studio = 0,35143 % des mises.

| Charges à couvrir | Mises mensuelles nécessaires |
|---|---|
| 150 €/mois (maintenance seule) | **≈ 42 700 $/mois** |
| 150 €/mois + 3 500 € de frais initiaux amortis sur 12 mois | **≈ 125 700 $/mois** |
| 400 €/mois + 6 000 € amortis sur 12 mois (structure, juridique renforcé) | **≈ 256 100 $/mois** |

Lecture : avec le scénario central (300 000 $/mois), un unique jeu couvrirait des charges modestes. Avec le scénario pessimiste, il ne les couvrirait pas. Le levier principal est le **portefeuille** : plusieurs jeux réutilisant ce moteur, à faible coût marginal. Ce levier ne doit être actionné qu'une fois ce premier jeu validé.

## 7. Recommandations

1. Lire le contrat Stake Engine (propriété intellectuelle, exclusivité, GGR négatif, résiliation) **avant** toute soumission.
2. Lancer la recherche d'antériorité de la marque « Golden Rally ».
3. Viser une première soumission Stake Engine comme preuve de marché, avec un coût fixe minimal.
4. Mesurer les mises réelles pendant 3 mois avant d'investir dans d'autres jeux, une licence ou une certification.
