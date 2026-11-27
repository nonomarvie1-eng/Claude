# Phase 6 — Frontière rendement-risque

Axes :

- rendement annualisé **médian** simulé (bootstrap par blocs mensuels, 10 000 tirages) ;
- **95e percentile** du drawdown simulé.

Les 8 profils de chaque stratégie sont tous **sur la frontière de Pareto**. Sans levier, rendement et drawdown augmentent ensemble et proportionnellement : aucun profil n'en domine un autre.

```
CAGR médian simulé (%/an)
 4.0 |                                                   ● US 100 %
 3.5 |
 3.0 |
 2.5 |                                              ○ JP 100 %
 2.0 |                          ● US 50 %
 1.5 |                    ● US 2 %      ○ JP 50 %
 1.0 |            ●US 25 %
 0.5 |     ○JP 2 %  ○JP 25 %
 0.0 |●○○●●○○●
     +----+----+----+----+----+----+----+----+----+----+---- DD 95e percentile (%)
     0    2    4    6    8   10   12   14   16   18   20   22   24
```

| Zone | Profils | CAGR médian | DD 95e pct | P(DD > 10 %) |
|---|---|---|---|---|
| Règle actuelle (≤ 0,5 % de risque) | JP 0,25 à 0,5 %, US 0,25 à 0,5 % | 0,06 à 0,34 % | 0,5 à 2,1 % | 0 % |
| Intermédiaire | JP 2 %, US 1 à 2 %, expositions de 10 à 25 % | 0,3 à 1,4 % | 2 à 8 % | 0 à 1,4 % |
| Au-delà de votre seuil de 10 % | Expositions de 50 à 100 % | 1,3 à 4,0 % | 11 à 23 % | 10 à 79 % |

**Pente de la frontière** : environ 0,12 point de rendement annuel par point de drawdown pour le Japon, et 0,17 pour les US. Ce rapport est très faible.

- Un dimensionnement compatible avec votre seuil (DD 95e percentile < 10 %) plafonne vers **1 à 1,4 %/an**.
- Votre objectif de 10 à 20 %/an est **hors de portée** de ces signaux, à n'importe quel dimensionnement sans levier.
- Avec levier, le rendement et le drawdown seraient multipliés ensemble ; le levier est exclu par vos règles.
