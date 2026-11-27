# Phase 2D — Budget global et protocole (rédigé avant exécution)

## 1. Comptabilité des essais

Le compteur n'est jamais réinitialisé ; le registre conserve tous les essais.

| Catégorie | Avant 2D | Prévu en 2D | Rôle dans la correction statistique |
|---|---|---|---|
| Hypothèses de sélection (A, B, REF, C, F, REG, D) | 80 (dont 18 de rodage en phase 2) | — | Comptées |
| Audits diagnostiques (AUDIT) | 12 | — | Hors sélection, publiés |
| Répétitions techniques (TECH) | 0 | 6 (recalcul après correction de défauts) | Hors sélection (même hypothèse, même signal) |
| G — allocation dynamique | — | **10** | Comptées |
| E — retour à la moyenne | — | **8** | Comptées |
| Hypothèses structurelles (≤ 3) | — | **0** cette phase : pré-enregistrées seulement si vous les validez | Comptées si lancées |
| EUR/USD (lot 2B-01 pré-enregistré, 27 essais) | — | 0 tant que les données sont bloquées | Comptées si lancées |

**Budget global de sélection en 2D : 18 essais.** Après la phase, le total sera d'environ 98 essais de sélection.

Justification statistique : le seuil unilatéral de Bonferroni passe de z = 3,23 (m = 80) à z = 3,29 (m = 98). Le coût marginal en puissance des 18 essais est donc faible, à condition qu'ils testent des mécanismes **différents** de ceux déjà rejetés, et non de nouvelles variantes. Les familles G et E répondent à ce critère : allocation continue, et retour à la moyenne, jamais testé jusqu'ici. Correction principale : BH au sein de chaque famille ; BH global sur tous les essais de sélection publié à titre de contrôle.

Justification informatique : environ 1 à 10 s par essai pour E (cadre déjà mesuré) ; moins de 5 s pour G (simulation journalière).

## 2. Exposition de NEXUS G : justification des niveaux

Sur la période de développement, la volatilité annualisée de BTC est d'environ 60 à 80 % et son drawdown maximal de −77 %. Pour un portefeuille BTC/liquidités à poids constant w, on a approximativement : volatilité ≈ w × σ_BTC et drawdown ≈ w × 77 %.

| Plafond w | Volatilité attendue | Drawdown passif attendu | Statut |
|---|---|---|---|
| 0 % | 0 | 0 | Référence « liquidités » |
| 10 % | ≈ 6–8 % | ≈ −8 % | **Testé** : compatible avec la cible de drawdown de 10 % même en passif |
| 25 % | ≈ 15–20 % | ≈ −19 % | **Testé** : le timing devrait réduire ce drawdown sous 10 % pour être utile |
| 50 % | ≈ 30–40 % | ≈ −38 % | **Écarté** : incompatible avec la cible de drawdown de 10 % du projet, sauf timing parfait |

## 3. Risque de NEXUS G

- **Pas de risque par position**, puisqu'il n'y a pas de stop individuel. Le risque est **global** : la perte maximale sur une journée vaut environ w × (baisse journalière de BTC). Exemple : −40 % de BTC sur une journée correspond à −4 % à 10 % d'exposition et −10 % à 25 %.
- Mesures publiées :
  - pire jour et pire semaine ;
  - valeur la plus basse en séance (sur le plus bas journalier) ;
  - CVaR 5 % quotidienne ;
  - drawdown maximal et durée sous l'eau ;
  - comportement pendant les épisodes de mars 2020, mai 2021, mai et juin 2022 (Terra-Luna, Celsius) et novembre 2022 (FTX).
- **Seuil d'arrêt global de 10 %** (passage définitif en liquidités) : simulé **avec et sans**, à titre de diagnostic uniquement. La règle de production reste inchangée.

## 4. Critères G (fixés avant les résultats)

- **Critère principal** : différence de rendement quotidien moyen entre la stratégie et le **portefeuille passif à la même exposition moyenne** (poids constant, rééquilibrage mensuel, mêmes coûts).
  - Test unilatéral : bootstrap par blocs de 20 jours.
  - Correction : BH sur les 10 essais G.
- « Prometteur » si cette différence est positive, avec p (BH) < 0,25, et le reste avec coûts × 2.
  - Doivent s'y ajouter un drawdown au plus égal à celui du passif de même exposition, et un Sharpe supérieur ou égal.
- « Incompatible » si la borne haute de l'IC95 de la différence est négative. Sinon : « absence d'avantage démontré ».
- Une réduction du drawdown n'est **pas** considérée comme une preuve d'alpha. Les composantes sont publiées séparément :
  - rendement dû à l'exposition à BTC ;
  - réduction mécanique du risque par les liquidités ;
  - timing ;
  - dimensionnement dynamique ;
  - frais ;
  - alpha de régression.

## 5. Références G

Toutes sur la même fenêtre (2020-05-01 → 2023-07-01), avec le même modèle de coûts :

- 100 % liquidités ;
- Buy & Hold BTC ;
- poids fixes 10 % et 25 % rééquilibrés mensuellement ;
- passif à même exposition moyenne ;
- passif à même volatilité ;
- moyenne mobile simple (NXG-01) ;
- momentum simple (NXG-02).

## 6. Critères E

verdict_v2 (phase 2C), avec les entrées aléatoires à exposition comparable et le passif à la même exposition comme références. Pas d'accumulation : une position à la fois, réinitialisation du signal exigée avant une nouvelle entrée.

## 7. Concentration des profits

Pour les stratégies de tendance, une forte concentration est attendue. La part des 5 meilleurs trades est donc comparée à celle des **entrées aléatoires à exposition comparable**, sur la même distribution de durées. Elle n'est plus jugée dans l'absolu (ajout du lot 2D).
