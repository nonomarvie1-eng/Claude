# 07 — Risques et limites du projet

## 1. Avis préalable (a priori, avant tout test)

Mon estimation honnête : **la probabilité qu'une des cinq stratégies, telle que décrite, présente un avantage net robuste après coûts est faible.** Raisons :

- Ces méthodes sont publiques, très diffusées et reposent sur des niveaux que tout le monde voit ; si un avantage simple existait, il serait vraisemblablement arbitré.
- Les preuves fournies sont des exemples choisis a posteriori, sans journal audité ; plusieurs chiffres se contredisent (voir `01`).
- Les filtres par actif, jour et mois (SBA) et la combinatoire des confluences (ICT) sont typiques d'un ajustement sur l'historique.
- Les stratégies M1 affrontent des coûts de 0,1–0,4R par trade.

Si un avantage existe, il est plus plausible qu'il soit **petit** et lié à des phénomènes structurels (saisonnalité horaire de la volatilité, momentum intraday sur indices, fausses cassures de niveaux très visibles), et qu'il soit fragile aux coûts. Le protocole est conçu pour que la conclusion « aucun avantage démontré » soit un résultat acceptable et probable.

## 2. Risques méthodologiques

| Risque | Mesure de contrôle |
|---|---|
| Look-ahead (swings, multi-TF, Fibonacci) | Horodatage `t_avail`, test de troncature obligatoire |
| Data snooping / comparaisons multiples | Pré-enregistrement, comptage de tous les essais, DSR, PBO, SPA, BH |
| Contamination du test final | Verrouillage technique + journal d'accès ; une seule exécution |
| Biais de l'intrabar OHLC | Hypothèse SL-d'abord + résolution par ticks |
| Qualité des données gratuites (CFD ≠ marché réel, volumes de cotation) | Contrôle croisé de deux sources ; résultats indices à confirmer sur futures avant toute conclusion |
| Non-stationnarité (2020 Covid, 2022 inflation/hausse des taux) | Analyse par année et par régime ; exiger la robustesse inter-périodes |
| Corrélations entre actifs (EUR/USD–GBP/USD, BTC–ETH, NASDAQ–DAX) | Les pools multi-actifs ne sont pas des échantillons indépendants ; bootstrap par blocs de dates |
| Survivance du « meilleur » backtest | Classement sur borne basse d'IC, pas sur le maximum |
| Biais de confirmation (vouloir que ça marche) | Critères de rejet écrits maintenant ; benchmarks aléatoires |

## 3. Risques d'exécution (pour une éventuelle phase ultérieure)

- Écart backtest / réel : spreads élargis aux news et aux ouvertures, slippage sur stops, requotes, horaires serveur.
- Spécifications courtier variables (lot min, swaps, commissions) : le résultat dépend du courtier.
- Petit capital : quantification du risque, impossibilité de diversifier, coûts fixes proportionnellement lourds.
- Réglementation UE retail : leviers plafonnés ; la majorité des comptes CFD de particuliers sont perdants selon les avertissements réglementaires obligatoires des courtiers européens.

## 4. Risques logiciels et opérationnels

- Bugs silencieux de moteur → tests unitaires sur scénarios à résultat connu, contrôle « marche aléatoire ⇒ espérance ≈ −coûts ».
- Dérive de configuration → stratégies versionnées par hash, aucune modification automatique de paramètres en production.
- Mauvaise gestion du temps (DST) → stockage UTC, tests dédiés aux semaines de transition.

## 5. Limites de cette première phase

- Aucun test n'a été exécuté sur données réelles : **aucun résultat de performance n'est présenté**, volontairement.
- Les informations sur les fournisseurs de données n'ont pas pu être vérifiées en ligne depuis ce conteneur et doivent l'être depuis votre PC.
- Votre PC Windows n'a pas été inspecté ; les estimations de temps de calcul sont des ordres de grandeur.
- Les tableaux de paramètres originaux (SBA), les graphiques et les indicateurs propriétaires (NY) ne sont pas disponibles : les versions « référence » sont donc nos interprétations documentées, pas des copies exactes.
- Aucun conseil en investissement : il s'agit d'un projet de recherche en simulation.
