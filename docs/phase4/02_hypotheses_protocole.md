# Phase 4 — Réexamen, hypothèses et protocole (pré-enregistré)

Rédigé et commité **avant** le téléchargement des nouvelles données et toute exécution. Fichier machine : `experiments/preregistration/batch_4_01_cubrik.toml`.

## 1. Réexamen des recherches précédentes selon les contraintes Cubrik

| Famille | Verdict antérieur | Exprimable dans Cubrik ? | Décision phase 4 |
|---|---|---|---|
| A, B, SBA (sessions intraday M5) | Rejetées (frais ≈ 0,15R par trade) | **Non** : aucun opérande horaire | Abandon |
| NLI (niveaux ICT, Silver Bullet, SMT, killzones) | 13/14 nuls | Partiellement (`fvg`, `orderBlock`, `swingHigh`) mais sans heure ni SMT | Abandon : aucun signal sur BTC |
| ORB 09:30 NY | Information réelle, non exploitable, non répliquée | **Non** (heure) | Abandon |
| C (structure) | Rejetée | Partiellement | Abandon |
| E (retour à la moyenne H1/H4) | Rejetée | Oui | Pas de nouveau test. Variante D1 + filtre de tendance distincte : P4-04, faible priorité |
| D (compression) | La compression n'apporte rien | Oui | Abandon |
| **F, REF-SMA, NXD-02 (tendance H4/D1 BTC)** | **Prometteurs, preuves insuffisantes** ; expliqués par l'exposition au marché | **Oui** | **Généralisation multi-actifs : P4-01, P4-02** |
| **G (allocation)** | **Prometteur** (alpha +3 %/an, p BH 0,12), effet surtout sur le risque | Oui, sous forme de règle d'entrée et de sortie à taille fixe | Intégré à P4-02 |
| Cointégration, OFI | Nuls ou infaisables | Non (inter-actifs, tick) | Abandon |

**Leçon principale** : avec un risque de 0,5 % par trade et un stop de tendance large (10 à 20 %), une position n'engage que 3 à 5 % du capital. Sur un seul actif, le rendement est donc forcément faible : +7 à +32 % sur 3,5 ans en phase 2C. Seule la **diversification sur plusieurs actifs peu corrélés** peut augmenter le nombre de positions simultanées à risque constant. C'est l'axe de cette phase.

## 2. Marchés : classement selon les contraintes

| Marché | Données légales disponibles | Frais | Liquidité | Faisable avec 1 000 € | Cubrik | Rang |
|---|---|---|---|---|---|---|
| Cryptos majeures au comptant (top 10) | **Oui**, gratuites (Binance Vision, recherche personnelle) | 0,10 %/côté | Élevée | Oui (montants minimaux ≈ 5–10 USDT) | Oui | **1** |
| Perpétuels crypto USDT-M | **Oui** (prix et financement Binance Vision) | 0,05 %/côté + financement | Élevée | Oui, levier 1 | Oui (`XXX/USDT:USDT`) | **2** |
| Forex majeurs, or | **Non** (Dukascopy bloqué) | Spread de 0,1 à 1 pip | Très élevée | Oui en CFD | Oui, à partir de H1 [à confirmer] | 3, en attente |
| Indices (NAS100, US500) | **Non** | Spread du CFD | Très élevée | Oui en CFD | Oui, à partir de H1 [à confirmer] | 4, en attente |
| Futures CME (NQ, ES) | Payantes | — | — | **Non** (MNQ : 3,7 à 7,4 % de risque par trade) | Via IB seulement | Exclu |

## 3. Hypothèses (4 exécutées + 1 en attente)

Classement fixé **avant** les résultats.

| Clé | Stratégie | Justification économique | Faisabilité | Coût d'exécution | Rang |
|---|---|---|---|---|---|
| P4-01-DONCH | Cassure de Donchian 55/20, D1, 10 cryptos, achat | Forte : suivi de tendance documenté sur un siècle (Hurst et al. 2017) et sur les cryptos (Liu & Tsyvinski 2021 ; Zarattini et al. 2025) ; sous-réaction et attention des investisseurs | Totale (règles Cubrik natives) | Faible : peu de trades, D1 | **1** |
| P4-02-SMA | Croisement de la SMA100, D1, 10 cryptos, achat | Forte (Faber 2007) ; prolonge G et REF-SMA | Totale | Faible à moyen : faux signaux autour de la moyenne | **2** |
| P4-03-TSMOM-LS | ROC 90 j, achat et vente sur perpétuels | Moyenne : momentum documenté, mais sa jambe vendeuse est faible en crypto (Han, Kang & Ryu) | Totale (perpétuels) | Moyen : financement | **3** |
| P4-04-RSI2 | RSI(2) < 10 au-dessus de la SMA200, D1, achat | Faible en crypto (documenté sur les actions) | Totale | Moyen : plus de trades | **4** |
| P4-05 | Règles P4-01/P4-02 sur forex, or et indices | Forte (diversification entre classes d'actifs) | **Données absentes** | — | En attente |

Points fixés pour toutes les hypothèses :

- aucun paramètre n'est optimisé : valeurs fixées a priori, chacune testée **une seule fois** ;
- voisins de sensibilité pré-déclarés, jamais utilisés pour choisir.

## 4. Univers et stops (règles figées avant les données)

- **Univers** : les 10 paires USDT au comptant ayant le plus fort volume en USDT d'octobre à décembre 2019, parmi 38 candidates listées dans le TOML. Le classement est donc établi avant la période de développement, ce qui évite de retenir après coup les gagnants d'aujourd'hui (biais de survie).
- **Stops** : Cubrik n'accepte qu'un % fixe. Le stop de chaque actif vaut 3 × la médiane de (ATR14 / prix) en D1 du 2019-07-01 au 2019-12-31, arrondi au % entier et borné à [5 %, 25 %].

## 5. Simulation et métriques

- **Moteur** : `nexus/phase4/sim.py`, conçu pour reproduire la sémantique des règles Cubrik.
  - Signaux sur bougies D1 UTC à la clôture ; exécution au marché à l'ouverture du jour suivant.
  - Stops vérifiés heure par heure sur bougies H1 : exécution au prix du stop, ou à l'ouverture si le prix a ouvert au-delà du stop (gap).
  - Une position par actif ; taille = 0,5 % du capital courant / stop % ; somme des positions ≤ capital.
- **Coûts** :
  - comptant : 0,10 % de frais et 0,05 % de glissement par côté ;
  - perpétuels : 0,05 % + 0,05 % par côté, plus le financement réel ;
  - conversion EUR/USDT : 0,10 % par côté ;
  - stress : frais et glissement × 2.
- **Capital** : 1 000 €, converti en USDT au départ ; capital en EUR au taux du jour.
- **Métriques** :
  - rendement total et annualisé ;
  - drawdown maximal ;
  - Sharpe quotidien avec IC95 par blocs ;
  - profit factor ;
  - R moyen net par trade, avec IC95 par bootstrap de semaines ;
  - taux de réussite ;
  - exposition moyenne ;
  - **alpha contre un panier équipondéré passif ramené à la même exposition moyenne** (bootstrap par blocs de 20 jours, p unilatéral) ;
  - résultats par année, par actif, longs et shorts séparés ;
  - comparaison à des **entrées aléatoires** de même nombre et de même durée, par actif (200 tirages).
- **Statistiques de jugement** : sans les arrêts globaux. Les résultats en euros sont présentés **avec** les règles de risque (perte maximale de 2 % par jour, arrêt à 10 % de drawdown) et sans elles. La phase 2C a montré que l'arrêt fausse le jugement d'un signal.

## 6. Critères (une stratégie n'est « candidate Cubrik » que si TOUS sont remplis)

| # | Critère |
|---|---|
| C1 | Alpha > 0 avec p corrigé (Benjamini–Hochberg sur les 4 tests principaux) < 0,05. Pour P4-03, rendement > 0 contre la trésorerie |
| C2 | R moyen net par trade > 0, avec une borne basse de l'IC95 > 0 |
| C3 | R moyen encore > 0 avec des coûts × 2 |
| C4 | Au moins 3 des 4 voisins de sensibilité ont un alpha positif |
| C5 | Alpha (estimation ponctuelle) positif sur au moins 3 des 4 sous-périodes (2020, 2021, 2022, 2023 S1). C'est la stabilité temporelle qui tient lieu de walk-forward, puisqu'aucun paramètre n'est réestimé |
| C6 | Drawdown maximal < 10 % au risque de 0,5 % par trade |

- **« Prometteur, preuves insuffisantes »** : C2 et C3 sont remplis, avec un p corrigé < 0,20.
- **« Rejeté »** : tous les autres cas.
- Vos objectifs indicatifs (Sharpe > 1, profit factor > 1,5, 10 à 20 % par an) sont **rapportés**, mais ne servent pas à sélectionner.

## 7. Après ce lot

- **Aucune stratégie candidate** : rapport des résultats réels. Aucune variante supplémentaire n'est testée pour « trouver » un résultat.
- **Une stratégie candidate** :
  1. fiche de stratégie et prompt d'agent Cubrik ;
  2. **demande d'autorisation** pour ouvrir la validation (2023-07 → 2024-12), une seule fois et en Python ;
  3. comparaison avec Cubrik plus tard, puisque tout backtest Cubrik de la candidate recouvre les périodes verrouillées.
