# Phase 6 — Audit du signal japonais (RSI 2 + stop, figé en phase 5)

Configuration figée, **non modifiée** :

- entrée : RSI(2) < 10 et clôture > SMA 200 ;
- sortie : clôture > SMA 5 ;
- stop catastrophe de 11 %, vérifié à la clôture ;
- exécution à la clôture ;
- coûts : 0,03 % par côté, plus le financement de nuit.

Résultats : `results/batch_6_01_confirmation/diagnostics.json`. Pré-enregistrement : `experiments/preregistration/batch_6_01_confirmation.toml` (commit `58b12eb`, avant les données BCE).

## 1. Reproduction exacte (D0)

Le code figé de la phase 5 donne **exactement les mêmes 184 trades** : rendement net moyen de +0,466 % par trade, sur 1991-07 → 2023-06.

## 2. D'où vient l'avantage : marché, change ou portefeuille ? (D1, D2, D3)

Les données French Japon sont en **USD**. Le rendement d'un trade en USD vaut (1 + rendement local) × (1 + variation du yen) − 1. J'ai décomposé chaque trade depuis 1999 avec les taux de référence BCE (USD/JPY = EUR/JPY ÷ EUR/USD).

| Composante (151 trades, 1999-2023 S1) | Moyenne par trade | IC95 (bootstrap par mois) |
|---|---|---|
| Rendement brut en USD | +0,67 % | [+0,37 ; +0,96] |
| **Composante change (yen contre USD)** | **−0,34 %** | [−0,49 ; −0,17] |
| **Composante marché local (JPY)** | **+1,02 %** | [+0,68 ; +1,34] |
| Rendement net en USD | +0,55 % | [+0,25 ; +0,85] |

**Lecture** :

- l'avantage vient **du marché japonais en monnaie locale** ;
- le change **réduit** le résultat : le yen tend à baisser pendant les rebonds des actions japonaises, une relation connue entre le Nikkei et le yen [H] ;
- **le change n'explique donc pas l'avantage : il le masque en partie.**

**Contrôles** :

| Test | Trades | Rendement net moyen [IC95] | Gagnants | Entrées aléatoires appariées (10 000) : moyenne, p |
|---|---|---|---|---|
| Règle figée sur l'**indice reconstruit en JPY** (1999-11 → 2023-06) | 137 | **+0,55 % [+0,18 ; +0,88]** | 73,7 % | −0,01 %, **p = 0,0003** |
| Même fenêtre, indice French en USD | 141 | +0,50 % [+0,17 ; +0,80] | 73,8 % | −0,05 %, p = 0,0003 |
| Règle figée sur le **yen seul** (JPY/USD) | 129 | +0,07 % [−0,13 ; +0,27] | 62,0 % | non significatif |

- Les signaux en JPY et en USD ne coïncident que pour **55 entrées** sur environ 140. Ils sont sensibles au change et au décalage horaire, mais **les deux versions sont significatives**.
- Le change seul ne produit aucun avantage.

**Limites** :

1. Les taux BCE sont fixés à 14:15 CET, la clôture de Tokyo tombe vers 07:00 CET, et l'heure de conversion utilisée par French est inconnue. L'indice reconstruit contient donc du **bruit de change**.
2. **Portefeuille French** : il s'agit de toutes les actions japonaises pondérées par la capitalisation, proche du **TOPIX** et non du **Nikkei 225**, qui est pondéré par les prix et plus concentré (Fast Retailing, Tokyo Electron…).
   - La question « portefeuille French contre Nikkei 225 » **reste ouverte**.
   - Aucune source légale et automatisable du Nikkei 225 ou du TOPIX en JPY n'a été trouvée (`03_sources_donnees.md`).

## 3. Le stop simulé à la clôture (D4)

| | Stop | Trades | Sorties sur stop | Trades dont la pire clôture est passée sous la moitié du stop | Pire clôture pendant un trade |
|---|---|---|---|---|---|
| Japon | 11 % | 184 | **0** | 8 | **−10,5 %** |

**Ce que cela veut dire** :

- Le stop de la phase 5 est une **sortie à la clôture** quand la clôture franchit le niveau. **Ce n'est pas un vrai stop** intrajournalier :
  - un ordre stop réel peut être déclenché par le **plus bas de la séance**, même si la clôture remonte ensuite. Il sortirait alors plus souvent, et parfois à tort ;
  - à l'inverse, un gap d'ouverture fait sortir au-delà du stop.
- Au Japon, une clôture est descendue à −10,5 % alors que le stop est à 11 %. Un stop intrajournalier a donc **très probablement** été touché au moins une fois sans que notre simulation le compte.
- **Effet probable** :
  - quelques sorties supplémentaires à −11 %, sur des trades qui ont ensuite récupéré en clôture ;
  - donc un rendement moyen **légèrement inférieur** à celui mesuré.
  - L'ordre de grandeur est d'au plus quelques trades sur 184 [H]. Sa mesure exacte exige les plus bas journaliers.
- **Cubrik** vérifie les conditions toutes les 30 à 60 minutes. Son stop est un ordre placé chez le courtier : il sera touché en intrajournalier. **La simulation à la clôture est optimiste sur ce point.**

## 4. Verdict de l'audit

| Question | Réponse |
|---|---|
| L'avantage vient-il du change ? | **Non.** Le change le réduit (−0,34 % par trade) |
| Vient-il du marché japonais ? | **Oui, en monnaie locale** : +1,0 % par trade (brut), et il est significatif sur l'indice reconstruit en JPY |
| Vient-il de la composition French ? | **Inconnu.** Il faut le Nikkei 225 ou le TOPIX en JPY |
| Le stop est-il réaliste ? | **Non** : sortie à la clôture. Effet probablement faible, à mesurer avec des données OHLC |
| Le signal est-il transférable au CFD JP225 ? | **Pas démontré** : le JP225 est un indice pondéré par les prix, sa bougie journalière est celle du courtier, et il faut tenir compte du financement en JPY et du spread |
