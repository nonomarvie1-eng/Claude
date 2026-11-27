# NEXUS QUANT — Rapport de phase 2 (2A infrastructure + 2B premières expériences)

Date : 2026-11-27. Tous les chiffres ci-dessous proviennent d'exécutions réelles, journalisées dans `results/registry.sqlite`. Les tableaux complets sont générés automatiquement : `reports/phase2_batch_2b_01_BTCUSDT.md` et `reports/phase2_batch_2b_02_diag_BTCUSDT.md`. **Seule la période de développement (2020-01 → 2023-06) a été utilisée.** La validation et le test final n'ont pas été ouverts : le registre compte 0 accès au test final.

## 1. Synthèse

1. **Infrastructure opérationnelle** : collecteurs, stockage Parquet, contrôle qualité, simulateur d'exécution conservateur, gestionnaire de risque indépendant, registre des hypothèses, lanceur d'expériences pré-enregistrées, 42 tests qui passent.
2. **Données** : BTC/USDT est complet et validé (Binance Data Vision, sommes de contrôle vérifiées). **EUR/USD est bloqué** : le serveur Dukascopy limite le débit au point de rendre le téléchargement depuis le cloud impraticable (plusieurs semaines). Un script Windows est prêt.
3. **Résultats BTC/USDT spot** (27 essais pré-enregistrés + 6 essais de diagnostic) : **aucune stratégie ne présente d'avantage**. Verdicts : « absence d'avantage démontré » pour NEXUS A et ses ablations ; « résultats incompatibles avec une exploitation rentable » pour la référence SBA et pour NEXUS B.
4. **Cause principale sur BTC** : les coûts au comptant (0,10 % par côté, plus spread et glissement) représentent ≈ 0,14–0,18R par trade avec des stops intraday M5. Les seuls résultats positifs de NEXUS A proviennent de la période haussière 2020-2021 et s'inversent en 2022. C'est une exposition à la tendance du marché, pas un avantage de timing.
5. **NEXUS B n'existe pas sur BTC, même avant commissions** : espérance négative de −0,12 à −0,42R avant commissions, spread et glissement inclus.

## 2. Fichiers créés ou modifiés

| Type | Fichiers |
|---|---|
| Moteur | `nexus/config.py`, `nexus/instruments.py`, `nexus/timeutils.py`, `nexus/engine/{execution,risk,backtest}.py` |
| Données | `nexus/data/{http,binance,dukascopy,store,quality}.py`, `scripts/download_data.py`, `scripts/build_bars.py`, `scripts/windows/telecharger_eurusd.ps1` |
| Caractéristiques | `nexus/features/core.py` |
| Stratégies | `nexus/strategies/{base,session,random_baseline}.py` |
| Statistiques | `nexus/stats/{metrics,inference}.py` |
| Recherche | `nexus/research/{registry,runner,report}.py`, `experiments/preregistration/batch_2b_01.toml`, `batch_2b_02_diag.toml` |
| Tests | `tests/test_execution.py`, `test_execution_equivalence.py`, `test_risk_backtest.py`, `test_features_causality.py`, `test_time_registry_stats.py`, `helpers.py` |
| Résultats | `results/registry.sqlite`, `results/batch_2b_01/summary_BTCUSDT.json`, `results/batch_2b_02_diag/summary_BTCUSDT.json`, `reports/data_quality/BTCUSDT.json`, `reports/phase2_*.md` |
| Documents | `docs/phase2/01_decisions_et_revisions.md`, `02_acces_donnees.md`, `03_architecture_moteur.md`, ce rapport ; révisions dans `docs/phase1/00, 03, 05, 06` |
| Projet | `pyproject.toml`, `.gitignore` (les données ne sont jamais versionnées) |

## 3. Fonctionnalités développées

Voir `03_architecture_moteur.md` pour la liste complète des garanties et des tests correspondants. Points principaux :

- exécution au marché à l'ouverture de la minute suivant la disponibilité du signal ; achat au ask, vente au bid ;
- ordres limites remplis uniquement si le prix traverse le niveau d'au moins un tick ; ordres non exécutés journalisés ;
- stop et objectif dans la même minute : stop retenu (hypothèse conservatrice) ; gap à travers le stop exécuté à l'ouverture ;
- tailles calculées sur le capital courant, frais inclus dans le budget, arrondi au pas de l'instrument, refus sous le minimum ;
- refus si les coûts estimés dépassent 33 % du risque (règle de faisabilité, journalisée) ;
- limite de perte journalière de 2 %, arrêt définitif à 10 % de drawdown, une position à la fois ;
- spot : ni levier ni vente à découvert ; conversion des gains en EUR par EUR/USDT, au dernier taux connu ;
- pré-enregistrement obligatoire et immuable ; tous les essais sont comptés, y compris les essais de rodage ;
- test final verrouillé techniquement.

## 4. Tests exécutés

`python -m pytest` → **42 tests réussis**, en ≈ 3 s, dont :

- 15 scénarios d'exécution vérifiables à la main (entrée, spread, ambiguïté SL/TP, tick de traversée, gap, sortie horaire, trou de données, spot, anomalies, stress des coûts) ;
- 1 test d'équivalence entre le simulateur vectorisé et une implémentation naïve, sur 3 000 trades aléatoires, avec résultats identiques ;
- 1 contrôle global : sur une marche aléatoire, l'espérance mesurée correspond aux seuls coûts (−0,05R attendu) ;
- 11 tests du gestionnaire de risque et de la boucle de backtest (dont un P&L calculé à la main : +19,20 €) ;
- 6 tests de causalité (troncature) ;
- 9 tests de fuseaux, DST, verrou, registre et statistiques.

## 5. Résultats réellement obtenus — BTC/USDT spot, période de développement

### 5.1 Statistique de l'avantage (R nets, 0,5 % de risque, sans disjoncteur)

Extraits, session `utc` (les sessions `paris` et `london` donnent des résultats très proches, voir le rapport complet) :

| Hypothèse | Trades | E[R] net | IC95 (blocs hebdo) | E[R] avant commissions | E[R] coûts ×2 | E[R] aléatoire | Verdict |
|---|---|---|---|---|---|---|---|
| REF-SBA-01 (stop EMA50, TP 2R) | 197 | −0,146 | [−0,326 ; +0,043] | +0,023 | −0,353 | −0,196 | Incompatible |
| NXA-01 cassure, TP 2R | 268 | −0,082 | [−0,216 ; +0,057] | +0,063 | −0,246 | −0,165 | Absence d'avantage |
| NXA-01 cassure, sortie horaire seule | 268 | −0,069 | [−0,232 ; +0,101] | +0,076 | −0,227 | −0,132 | Absence d'avantage |
| NXA-02 + filtre EMA100 H1 | 163 | −0,058 | [−0,235 ; +0,128] | +0,088 | −0,226 | −0,161 | Absence d'avantage |
| NXA-03 + filtre compression | 121 | +0,024 | [−0,205 ; +0,264] | +0,189 | −0,057 | −0,188 | Absence d'avantage |
| NXA-04 entrée sur retest | 170 | −0,098 | [−0,279 ; +0,083] | +0,056 | −0,211 | −0,173 | Absence d'avantage |
| NXB-01 / NXB-02 | 13–16 | — | — | — | — | — | Données insuffisantes (> 90 % des signaux refusés : coûts > 33 % du risque) |

- Après correction de Benjamini–Hochberg sur l'ensemble du lot, aucune p-valeur n'est significative : p(E[R] > 0) ajusté ≈ 0,97 partout, p(stratégie > aléatoire) ajusté de 0,21 à 0,35.
- Le filtre de compression (NXA-03) est le seul à battre le hasard en p-valeur **brute** (0,025–0,035). Ce n'est plus significatif après correction, et son espérance nette reste ≈ 0.
- Les entrées aléatoires comparables perdent ≈ −0,13 à −0,20R : c'est l'ordre de grandeur des coûts. Les stratégies font un peu mieux que le hasard, mais ne couvrent pas leurs coûts.
- Toutes les ablations de NEXUS A (filtre directionnel, compression, retest) ont un IC95 de différence qui inclut 0 : **aucune contribution marginale démontrée**.

### 5.2 Diagnostic NEXUS B sans filtre de coûts (lot 2B-02)

| Session | Objectif | Trades | E[R] avant commissions | E[R] net | IC95 net | Coût médian / risque |
|---|---|---|---|---|---|---|
| paris | milieu | 214 | −0,209 | −1,324 | [−1,64 ; −1,00] | 92 % |
| london | 2R | 234 | −0,124 | −1,295 | [−1,55 ; −1,05] | 100 % |
| utc | milieu | 239 | −0,416 | −1,594 | [−1,87 ; −1,33] | 111 % |

Les stops placés juste derrière la mèche balayée sont si serrés que les coûts égalent ou dépassent le risque. Et le mécanisme est négatif même avant commissions.

### 5.3 Stabilité temporelle — le résultat le plus instructif

E[R] net par semestre, NXA-01 sortie horaire, session utc : 2020-S1 +0,07 · 2020-S2 +0,14 · 2021-S1 +0,32 · 2021-S2 −0,10 · 2022-S1 −0,71 · 2022-S2 −0,48 · 2023-S1 −0,20.

Comme la vente à découvert est impossible en spot, NEXUS A n'achète que les cassures haussières. Il profite du marché haussier 2020-2021 et perd lourdement en 2022. Ce profil est celui d'une **exposition directionnelle**, pas d'un avantage. Pour comparaison, l'achat-conservation de BTC sur la même période transforme 1 000 € en ≈ 4 336 € après frais, avec un drawdown d'environ −77 %. Ce point de comparaison n'est pas comparable en risque.

### 5.4 Profils de risque (capital 1 000 €, limites actives) — à lire avec prudence

Session utc, NXA-01 sortie horaire :

| Profil | Trades | Rendement net | Max DD observé | Disjoncteur 10 % | Frais totaux | Sharpe | P(DD ≥ 10 %) MC | P(DD ≥ 20 %) MC |
|---|---|---|---|---|---|---|---|---|
| prudent 0,25 % | 262 | −4,1 % | 10,0 % | oui | 81 € | −0,46 | 0,31 | 0,00 |
| équilibré 0,5 % | 216 | +1,9 % | 10,1 % | oui | 137 € | 0,16 | 0,86 | 0,28 |
| dynamique 1 % | 195 | +14,1 % | 10,6 % | oui (2022) | 262 € | 0,56 | 1,00 | 0,84 |

(Monte-Carlo : 2 000 trajectoires par blocs hebdomadaires des R nets, sans arrondi de taille ni disjoncteur — borne indicative du risque de perte importante.)

Interprétation :

- Le profil dynamique paraît le meilleur **uniquement par effet de trajectoire** : il gagne en 2020-2021 (+67 €, +121 €), puis le disjoncteur l'arrête en 2022 après −47 €. Il fige ainsi ses gains par hasard. Les mêmes signaux ont une espérance négative. Ce résultat ne doit pas servir à choisir un profil.
- Le disjoncteur se déclenche dans presque tous les essais aux profils équilibré et dynamique ; au profil dynamique, la probabilité Monte-Carlo d'un drawdown ≥ 20 % est de 84 % (sans disjoncteur). Le drawdown observé dépasse le seuil (10,0–10,8 %), car la perte qui déclenche l'arrêt est subie en entier : un arrêt automatique ne garantit pas la perte maximale.
- Les **frais totaux (80 à 260 € sur 1 000 €)** dépassent tout gain potentiel. C'est la confirmation, en euros, du verdict en R.
- Les tailles minimales ne sont pas contraignantes sur BTC (minimum ≈ 5 USDT). C'est le rapport coûts/risque qui est rédhibitoire.

### 5.5 Conclusion scientifique pour BTC/USDT spot

**Aucune des stratégies testées ne présente d'avantage statistique**, et les mécanismes intraday M5 testés sont **incompatibles avec une exploitation rentable** aux frais spot standard. Je ne recommande pas de chercher davantage de filtres intraday sur BTC spot : ce serait du surajustement.

## 6. Erreurs rencontrées (et corrections)

| Erreur | Cause | Correction |
|---|---|---|
| Sources bloquées (403) | Liste d'hôtes de l'environnement | Ajout de 2 hôtes officiels, approuvé par vous |
| Dukascopy : 429 et coupures | Limitation de débit du serveur | Rythme ralenti puis arrêt ; script Windows |
| Diagnostic par variation du User-Agent refusé | Contrôle de sécurité (assimilable à un contournement) | Abandonné ; identifiant unique et honnête |
| Modèle aléatoire biaisé (1re version) | Tirage limité aux jours tradés, donc conditionné sur l'issue de la journée | Tirage sur tous les jours éligibles ; détecté lors du rodage, avant le lot officiel |
| Comparaison d'horodatages avec et sans fuseau, unités pandas 3 | pandas 3 n'impose plus les nanosecondes | Conversion explicite en entiers (ns) |
| Taux EUR/USDT absent du 1er au 3 janvier 2020 | Début de cotation de la paire | Signal refusé et journalisé (« taux de change indisponible ») |
| 3 tests du risque en échec au premier passage | Erreurs dans mes scénarios (stops de 100 pips au-delà du budget) | Scénarios corrigés, le moteur avait raison |
| Essais du lot 2B-01 marqués `+dirty` | Code non commité au moment de l'exécution | Code figé dans le commit `018f564` ; lots futurs sur code commité |

Les essais de rodage (18) sont conservés dans le registre et comptés : 51 essais au total à ce jour.

## 7. Limites restantes

- EUR/USD non testé (données manquantes) : les conclusions ne valent que pour BTC/USDT spot.
- Coûts BTC : tarif standard Binance de 0,10 % par côté, sans remise. Un compte à frais réduits changerait les chiffres nets, pas les espérances brutes.
- Les spécifications de lots et de commissions d'EUR/USD sont des hypothèses (marquées `ASSUMPTION` dans `instruments.py`).
- Le capital n'est réévalué qu'aux clôtures de trades, sans valorisation intrajournalière des positions ouvertes. C'est sans effet ici : toutes les positions sont fermées dans la journée.
- Le walk-forward se réduit pour l'instant à une analyse par semestre : les modèles minimaux n'ont pas de paramètre optimisé. Le walk-forward avec sélection de paramètres viendra avec les familles paramétrées.
- Le Deflated Sharpe et l'analyse par régime sont implémentés ou prévus, mais pas encore inclus dans le rapport automatique.
- Les conditions d'utilisation de Dukascopy et de Binance n'ont pas pu être lues depuis cet environnement.

## 8. Prochaines actions

**Nécessitent votre action ou votre décision :**

1. **Action sur votre PC** : exécuter `scripts/windows/telecharger_eurusd.ps1` (instructions dans `02_acces_donnees.md §3`) et me transmettre `nexus_eurusd_bars.zip`. L'archive contient aussi la sortie de `check_env.py` (confirmation de votre configuration).
2. **Conditions d'utilisation** : vérifier celles de Dukascopy (page du wiki indiquée par le serveur) et de Binance Data Vision.
3. **Choix scientifique pour BTC** (je recommande l'option a) :
   - a. abandonner l'intraday M5 sur BTC spot et tester BTC uniquement avec des familles à horizon plus long (C Trend Pullback H4, F Momentum journalier), où les coûts pèsent beaucoup moins par rapport au risque ;
   - b. poursuivre l'intraday BTC en supposant un niveau de frais réduit (hypothèse de compte à justifier) ;
   - c. retirer BTC de la recherche intraday et se concentrer sur EUR/USD.

**Autonomes, dès que les données EUR/USD seront disponibles :**

4. Exécuter le lot 2B-01 pré-enregistré sur EUR/USD (même code, déjà prêt).
5. Ajouter Deflated Sharpe, analyse par régime de volatilité et par jour de semaine (en diagnostic) au rapport automatique.
6. Préparer le pré-enregistrement de la famille suivante (C ou F selon votre choix), avec son modèle minimal et ses ablations.
