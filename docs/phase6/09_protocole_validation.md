# Phase 6 — Protocole de validation (préparé, NON exécuté)

**Statut : non exécuté. Il exige votre autorisation explicite, une fois toutes les conditions préalables remplies.**

## 1. Conditions préalables (toutes requises)

| # | Condition | État au 2026-11-27 |
|---|---|---|
| 1 | Instruments confirmés dans Cubrik (JP225, US500), RSI 2 et 5 acceptés, sens de `perTradePct` connu | **Non** (manipulations au §4 de `08`) |
| 2 | Données adaptées : historique D1 de l'**instrument négocié** (CFD du courtier) jusqu'au 2024-12-31 | **Non** (export MT5 démo à faire par vous) |
| 3 | Règles figées (ci-dessous) | **Oui** |
| 4 | Coûts réalistes : spread, swap et commission relevés chez le courtier | **Non** |
| 5 | Dimensionnement fixé (votre décision, `06`) | **Non** |
| 6 | Compatibilité Cubrik démontrée (agent créé **en pause**, `test_agent` en lecture seule) | **Non** |

## 2. Règles figées (aucune modification autorisée)

| | V-JP (RSI 2 Japon) | V-US (RSI 30/50 US) |
|---|---|---|
| Instrument | CFD JP225 du courtier choisi (en JPY) | CFD US500 du courtier choisi |
| Entrée (clôture D1 du courtier) | RSI(2) < 10 **et** clôture > SMA 200 | RSI(5) < 30 **et** clôture > SMA 200 |
| Sortie | Clôture > SMA 5 | RSI(5) croise au-dessus de 50 |
| Stop | 11 % sous le prix d'entrée | 6 % sous le prix d'entrée |
| Objectif | Aucun | Aucun |
| Sens et nombre de positions | Achat, une position | Achat, une position |
| RSI | Wilder | Wilder |

## 3. Données et simulation

- **Période** : 2023-07-01 → 2024-12-31, **une seule ouverture**, journalisée (`validation_access`). Le test final (2025-01 → 2026-06) reste verrouillé.
- Les indicateurs sont amorcés avec l'historique antérieur au 2023-07 ; aucun paramètre n'est réestimé.
- **Simulation sur OHLC du CFD** :
  - stop déclenché par le **plus bas** de la bougie, exécuté au stop ou à l'ouverture en cas de gap ;
  - entrées et sorties à la clôture de la bougie du courtier, plus 0,5 point de glissement ;
  - financement de nuit égal au swap réel ;
  - spread réel ;
  - conversion en EUR au taux BCE du jour.
- **Simulation en parallèle** : même calcul sur la série French de la phase 5 pour mesurer l'écart entre instruments. Cet écart est mesuré, jamais corrigé.

## 4. Critères de réussite (fixés maintenant)

Sur 18 mois, on attend environ 9 trades par stratégie. **Aucun test statistique n'aura de puissance** : la validation est un **contrôle de cohérence**, pas une preuve.

| # | Critère | Seuil |
|---|---|---|
| V1 | Rendement net moyen par trade | > 0 |
| V2 | Rendement moyen dans l'intervalle de prédiction de la phase 5 | Ne pas être sous le 5e percentile de la distribution bootstrap de moyennes sur 9 trades, tirées des trades de développement |
| V3 | Drawdown maximal au dimensionnement retenu | ≤ 95e percentile simulé en développement (`05`) |
| V4 | Écart entre instruments (CFD et série French) | Signaux identiques ≥ 50 % ; écart de rendement moyen expliqué par les coûts ou le décalage horaire |
| V5 | Agent Cubrik (`test_agent`, lecture seule) sur 5 dates de signal de la période | Décision identique à la règle dans 5 cas sur 5 |

**Issue** :

- **V1 à V5 satisfaits** : passage à un **compte démo** de courtier connecté à Cubrik Demo, pendant au moins 3 mois. Le test final reste verrouillé jusqu'à une décision séparée de votre part.
- **Un critère manque** : la stratégie est arrêtée, sans ajustement des paramètres.
