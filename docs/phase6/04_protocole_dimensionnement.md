# Phase 6 — Protocole de dimensionnement (pré-enregistré)

Fichier machine : `experiments/preregistration/batch_6_01_confirmation.toml`, commité avant l'exécution (`58b12eb`).

## Principes

- **Les règles d'entrée et de sortie ne changent pas.** Seule la fraction du capital engagée par trade varie.
- Le dimensionnement **ne change pas la qualité du signal** :
  - le rendement par trade, le taux de réussite et la p-valeur sont identiques pour tous les profils ;
  - sans levier, le Sharpe et le Calmar restent presque constants : rendement et drawdown sont multipliés par le même facteur.
- **Aucun profil n'est sélectionné par le rendement historique.** Le choix reste votre décision.

## Profils

| Type | Profils | Notionnel engagé |
|---|---|---|
| Risque initial au stop | 0,25 %, 0,5 %, 1 %, 2 % | risque / stop, plafonné à 100 % (sans levier). Japon (stop 11 %) : 2,3 à 18,2 % ; US (stop 6 %) : 4,2 à 33,3 % |
| Diagnostic : exposition fixe | 10 %, 25 %, 50 %, 100 % | Fraction fixe du capital courant à chaque trade |

## Mesures

- Rendement annualisé, drawdown maximal, Sharpe, Calmar.
- Exposition moyenne et maximale.
- **Risque de gap** : pire trade et pire journée, en % du capital.
- Frais, financement de nuit.
- **Monte Carlo** : bootstrap par blocs mensuels de trades, 10 000 tirages.
  - Rendement annualisé médian et 5e percentile.
  - 95e percentile du drawdown.
  - P(drawdown > 10, 15, 20, 25 %).
- **Frontière de Pareto** : on maximise le rendement annualisé médian simulé, on minimise le 95e percentile du drawdown.

## Fenêtres (développement seulement)

- Japon : 1991-07 → 2023-06.
- US : 2010-01 → 2023-06.

**Limites** :

- le stop est vérifié à la clôture (`01` et `02`, §stop) ;
- l'effet de change est ignoré pour les euros ;
- les coûts sont ceux de la phase 5 (0,03 % par côté, financement RF + 2,5 %).
