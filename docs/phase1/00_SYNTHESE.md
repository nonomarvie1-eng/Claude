# NEXUS QUANT — Phase 1 : synthèse des conclusions

> Révisions apportées en phase 2 : voir [`docs/phase2/01_decisions_et_revisions.md`](../phase2/01_decisions_et_revisions.md) (capital 1 000 €, hypothèses de session multiples, justification corrigée des tailles d'échantillon, quatre catégories de verdict).

Date : 2026-11-27. Aucun développement du bot n'a été engagé. **Aucun résultat de performance n'est présenté : aucun test n'a encore été exécuté sur données réelles.**

## Ce qui a été fait

1. Lecture intégrale des cinq documents → audit détaillé : `01_audit_strategies.md`.
2. Inspection de l'environnement : la session tourne dans un **conteneur Linux cloud**, pas sur votre PC Windows. Votre machine n'a pas pu être inspectée → script `scripts/check_env.py` fourni (lecture seule).
3. Définitions algorithmiques causales des 15 concepts demandés : `02_formalisation.md`.
4. Spécification de 5 références, 2 hybrides, 5 hypothèses alternatives, 5 benchmarks et du plan d'ablation : `03_strategies_candidates.md`.
5. Sources de données, fuseaux, DST, volumes : `04_donnees.md`.
6. Protocole expérimental et modèle d'exécution : `05_protocole_backtest.md`.
7. Ressources, coûts, temps de calcul : `06_ressources_couts.md`.
8. Risques et limites : `07_risques_limites.md`.
9. Architecture et plan de développement : `08_plan_developpement.md`.

## Conclusions principales

1. **Une seule stratégie est quasi mécanique : SBA.** NY M1/M15 et « sans indicateur » le deviennent après quelques choix documentés. ICT est majoritairement discrétionnaire. EMA 100 + Fibonacci ne contient pas de règles de trading complètes (le document le dit lui-même).
2. **Les cinq méthodes se ramènent à quatre primitives** : points pivots, cassure, échec de cassure, retracement, plus un contexte horaire et un filtre de tendance. La recherche portera sur ces primitives, avec ablations, plutôt que sur l'empilement de concepts.
3. **Les documents contiennent des contradictions** (SBA : sortie 20 h vs position conservée overnight, BE 3R vs 3,2R, résultat +2,75R vs +0,75R, fuseau absent, stop indéfini quand l'EMA est du mauvais côté ; NY : instrument non précisé, erreur arithmétique). Les filtres jour/mois de SBA ont une forte probabilité d'être du surajustement.
4. **La taille d'échantillon est le premier verrou statistique** : détecter +0,1R/trade avec un RR de 4 demande ≈ 1 500 trades (≈ 3 600 en tenant compte des comparaisons multiples). Les setups rares (ICT, H4) ne seront probablement pas validables actif par actif.
5. **Les coûts sont le premier verrou économique** : sur M1, ≈ 0,1–0,4R par trade.
6. **Le capital (500 € en phase 1, 1 000 € depuis la phase 2) impose des CFD/spot** (les micro-futures représentent 3,7–7,4 % de risque par trade à 1 000 €) et quantifie le risque ; XAU/USD sera souvent impossible à dimensionner au profil prudent.
7. **Données : coût 0 €.** Dukascopy (FX, or, CFD NASDAQ/DAX, bid/ask M1 et ticks), HistData (contrôle croisé), Binance Data Vision (crypto + funding), MT5 démo (spécifications courtier). ≈ 250–400 Mo de Parquet pour 8 actifs × 6 ans ; 8 Go de RAM suffisent en traitant un actif à la fois.
8. **Avis a priori** : la probabilité qu'une des stratégies, telle que décrite, survive au protocole est **faible**. Un éventuel avantage sera vraisemblablement petit et structurel (volatilité de session, momentum intraday, fausses cassures). La conclusion « aucun avantage démontré » est un résultat prévu et acceptable.

## Décisions attendues de votre part avant la phase 2

Voir `08_plan_developpement.md §3` : validation du découpage temporel et des critères d'acceptation, fuseau du range asiatique, sortie de `check_env.py`, lieu d'exécution (PC ou cloud avec accès réseau aux hôtes de données), ordre de priorité des actifs.
