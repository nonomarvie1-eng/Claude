# Phase 5 — Pré-enregistrement (lot 5-01)

Fichier machine : `experiments/preregistration/batch_5_01_indices.toml`. Il a été commité **avant** le téléchargement des données d'indices et avant toute exécution.

## 1. Doublons audités

- Les 8 règles Connors et assimilées forment **une seule famille**. Seules 3 sont retenues (`01_audit_7_documents.md` §8).
- P4-04 (RSI 2 sur cryptos) est déjà rejeté : je ne le reteste pas. H5-01 porte sur un autre marché (indice actions), pour lequel les règles ont été conçues.
- H5-EXP réutilise P4-01 à l'identique (même moteur, mêmes stops, mêmes coûts). Seule la gestion `lock` change : **une seule règle modifiée à la fois**.

## 2. Données et périodes

**Données** : Kenneth R. French Data Library.

- Indice de rendement total reconstruit à partir des rendements journaliers du marché.
- États-Unis depuis 1926, quatre régions développées depuis 1990.
- **Aucune observation postérieure au 2023-06-30 n'est lue** : validation et test final restent verrouillés.

| Fenêtre | Dates | Rôle |
|---|---|---|
| US principale | 2010-01 → 2023-06 | **Décision.** Postérieure à la publication des règles (avant 2010) : hors échantillon pour leurs auteurs |
| US reproduction | 1993-02 → 2009-12 | Comparaison avec les chiffres annoncés (SPY depuis 1993) |
| US historique | 1928 → 1992 | Contrôle antérieur, lui aussi hors échantillon des auteurs |
| International | 1991-07 → 2023-06 | Réplication (Europe, Japon, Asie-Pacifique hors Japon) |

## 3. Exécution, coûts, stop, taille

- **Exécution** :
  - principale : à la **clôture du signal** (règle d'origine). C'est proche de ce que permettrait la bougie journalière d'un CFD, qui clôture environ une heure après la séance au comptant [H] ;
  - stress : exécution à la **clôture suivante**, une borne conservatrice du délai de 30 à 60 minutes de Cubrik.
- **Coûts** :
  - 0,03 % par côté ;
  - financement de nuit des positions acheteuses (RF + 2,5 %/an) ;
  - stress : × 2, puis 0,20 % par côté.
- **Stop catastrophe** : 3 × l'écart-type des rendements sur 5 séances mesuré **avant 2010**, borné à [5 %, 15 %]. Il est vérifié à la clôture, puisque les données n'ont ni plus haut ni plus bas.
- **Taille** :
  - **décision** : règle NEXUS, 0,5 % de risque au stop ;
  - information : 0,25 % de risque, et notionnel 100 % sans levier (comme dans les documents).

## 4. Tests

1. **Entrées aléatoires appariées** (méthode du document 2) :
   - même nombre de trades, mêmes durées de détention, jours tirés au hasard **parmi ceux où la clôture est au-dessus de la SMA 200** ;
   - 10 000 tirages ;
   - p = part des tirages au moins aussi bons que la stratégie.
2. **Entrées aléatoires avec la même règle de sortie** : taux de réussite et rendement moyen, pour isoler l'apport de la sortie.
3. **Rendement net moyen par trade** : IC95 par bootstrap de mois.
4. **Alpha** contre l'indice passif ramené à la même exposition moyenne (bootstrap par blocs de 20 jours).
5. Benjamini–Hochberg sur les 7 tests principaux (H5-01a, H5-01b, H5-02, H5-03, H5-04 sur 3 marchés).

**Références** :

- achat-conservation de l'indice ;
- indice passif à exposition égale ;
- filtre seul : investi quand la clôture > SMA 200 (Faber), pour mesurer ce que le repli ajoute au filtre.

## 5. Critères

| # | Critère |
|---|---|
| C1 | p corrigé du test des entrées aléatoires < 0,05 |
| C2 | Rendement net moyen par trade > 0, avec un IC95 strictement positif |
| C3 | Rendement net moyen > 0 avec coûts × 2 **et** avec exécution à t+1 |
| C4 | Au moins 70 % des configurations de la grille pré-déclarée ont un rendement net moyen > 0 |
| C5 | Positif sur 1928-1992 (US) **et** sur au moins 2 des 3 sous-périodes post-2010 |
| C6 | Drawdown maximal < 10 % au dimensionnement NEXUS |
| MC | 5e percentile du rendement total > 0 (bootstrap par blocs) ; médiane > 0 avec 20 % des trades supprimés ; rendement > 0 sans le meilleur trade et sans la meilleure année |

**Verdicts** :

- **candidate** : tous les critères ;
- **prometteur** : C2, C3 et p BH < 0,20 ;
- **rejeté** : tous les autres cas.

Vos objectifs indicatifs (profit factor > 1,5, Sharpe > 1, 10 à 20 %/an) sont **rapportés**, mais ne servent pas à sélectionner.

## 6. Procédure Monte Carlo (doc. 07)

Elle s'applique à toutes les hypothèses. Ce sont des rééchantillonnages, pas de nouveaux essais.

1. **Mélange de l'ordre des trades** (10 000) : pertinent ici, car la taille dépend du capital composé.
2. **Bootstrap par blocs mensuels** (10 000) : rendement médian, 5e percentile, 95e percentile du drawdown, proportion de simulations perdantes, probabilité que le drawdown dépasse 10 %.
3. **Suppression aléatoire** de 5, 10 et 20 % des trades (10 000 chacune). Elle simule aussi les signaux manqués.
4. **Coûts** × 2 et 0,20 % par côté.
5. **Retard d'exécution** : clôture suivante.
6. **Perturbation des paramètres** : grille pré-déclarée (1 essai P5-SENS par hypothèse).
7. **Bruit de ±0,1 % sur les clôtures** (200 tirages) : sensibilité aux croisements exacts.
8. Retrait du meilleur trade ; retrait de la meilleure année.
9. **Régimes** : tercile de volatilité réalisée sur 20 jours à l'entrée, et décennie.

**Conventions** :

- les drawdowns sont calculés sur un capital composé et solvable, donc toujours inférieurs ou égaux à 100 % ;
- un « drawdown de 200 % » comme dans le document 4 ne peut exister qu'en P&L additif, et ne sera pas utilisé ;
- **ces simulations ne donnent pas une probabilité de réussite future** : elles mesurent la fragilité du résultat historique.

## 7. Essai de gestion de l'exposition (H5-EXP, autorisé)

- **Stratégie de départ** : P4-01, reproduit par le même code.
- **Règle ajoutée** : paliers Cubrik `lock` en % du prix.
  - Dès que le plus haut atteint +50 %, +100 %, +200 %, … +3 200 %, le stop remonte à la moitié du gain du palier.
  - On ne rend donc jamais plus de la moitié du gain d'un palier atteint.
- **Comparaison** :
  - P4-01 d'origine ;
  - P4-01 avec la gestion `lock` ;
  - panier passif à exposition égale.
- **Analyses** : contribution du plus gros trade, de la meilleure année (2021) et des périodes de forte tendance.
- **Pas de vente partielle** : sa disponibilité dans Cubrik n'est pas documentée.
- **Sensibilité** : fraction conservée 1/3 et 2/3 (1 essai P5-SENS).
