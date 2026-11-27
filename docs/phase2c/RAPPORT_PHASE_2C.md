# NEXUS QUANT — Rapport de phase 2C (recherche quantitative avancée, BTC/USDT)

Date : 2026-11-27. Tous les chiffres proviennent d'exécutions réelles sur la **période de développement** (2020-01 → 2023-06) et sont journalisés dans `results/registry.sqlite`. Les tableaux détaillés sont générés automatiquement :

- `reports/phase2c_audit_2b_01.md`
- `reports/phase2c_batch_2c_01.md`
- `reports/phase2c_batch_2c_02.md`

Validation et test final : **non ouverts** (0 accès enregistré).

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

## 1. Conclusion générale

**Aucun avantage statistique n'est démontré.** Aucun ne pouvait d'ailleurs l'être sans validation.

Les seuls résultats positifs (familles F, D-contrôle, et C en H4 avec sorties longues) relèvent tous du même mécanisme : **être acheteur de BTC pendant ses phases de tendance haussière**. Pour aucune variante, la performance n'est distinguable de l'exposition au marché (alpha quotidien dont l'IC95 inclut 0). Ces stratégies ne font pas mieux que la simple moyenne mobile de référence. Leurs profits sont concentrés sur quelques trades : 2021 pour F, le premier semestre 2023 pour C et D. Les filtres ajoutés (structure, confirmation, stop structurel, volatilité, régime, compression) n'apportent **aucune contribution démontrée**.

Six variantes obtiennent, selon la règle pré-enregistrée, le statut « **prometteur mais preuves insuffisantes** ». Je ne recommande d'en geler aucune telle quelle pour la validation (voir §8).

## 2. Conditions d'utilisation des données

- **Binance Vision Dataset Terms**, version 1.0 du 26/08/2026, lues intégralement (empreinte SHA-256 archivée). Le §4.1 autorise le « backtesting historique algorithmique pour une recherche purement personnelle, hors production ». C'est l'usage actuel ; les expériences BTC ont donc été lancées dans ce cadre.
- **Point bloquant pour l'objectif à long terme** : le §4.2 interdit l'usage des Datasets pour du « live proprietary trading execution ». Un passage en argent réel devra être examiné juridiquement.
- Le stockage dans le cloud n'est pas traité explicitement. Les données restent dans un conteneur privé et ne sont jamais versionnées.
- **Dukascopy : vérification en attente**, pages officielles inaccessibles depuis cet environnement. Liens et grille d'usage : `docs/phase2c/02_conditions_utilisation.md`.

## 3. Audit des résultats de la phase 2 (NEXUS A, SBA)

Reproductibilité : les 12 configurations ré-exécutées redonnent exactement les espérances enregistrées (ex. −0,0723 → −0,0723).

| Configuration (session utc) | E[R] sans frottement [IC95] | E[R] avant commissions [IC95] | E[R] net [IC95] | Coût moyen | Aléatoire, exposition comparable |
|---|---|---|---|---|---|
| SBA (TP 2R) | +0,020 [−0,116 ; +0,154] | +0,023 [−0,158 ; +0,213] | −0,146 [−0,33 ; +0,04] | 0,17R | −0,200 |
| NXA-01 TP 2R | +0,042 [−0,081 ; +0,170] | +0,063 [−0,072 ; +0,204] | −0,082 | 0,15R | −0,158 |
| NXA-01 sortie horaire | +0,106 [−0,062 ; +0,277] | +0,076 [−0,088 ; +0,246] | −0,069 | 0,15R | −0,158 |
| NXA-03 compression | +0,090 [−0,108 ; +0,286] | +0,189 [−0,038 ; +0,427] | +0,024 | 0,17R | −0,186 |

- **Espérance brute** : positive, mais tous les IC95 incluent 0, dans les trois sessions. Ce n'est pas une preuve.
- **Part de la hausse de BTC** : faible à cet horizon intraday, car la dérive sur environ 6 h ne représente qu'environ 0,03 %. Les entrées aléatoires à exposition comparable perdent environ −0,22 % par trade, c'est-à-dire essentiellement les coûts. La détention de BTC dans la même fenêtre horaire, tous les jours, perd −0,15 % par trade. Les stratégies gagnent entre +0,02 % et +0,29 % par trade : leur sélection des jours de cassure fait mieux que le hasard **avant coûts**, sans couvrir ces coûts. p(stratégie > aléatoire) brut : 0,08 à 0,13 pour NXA-01, 0,02 à 0,04 pour NXA-03, non significatif après correction.
- **Alpha quotidien** : −3 à −4 %/an pour NXA-01 et SBA (IC95 incluant 0 ou négatif) ; ≈ 0 pour NXA-03.
- **Par année** : positif en 2020-2021, fortement négatif en 2022 (−0,37 à −0,70R). Par régime : seul le régime haussier est ≈ 0 à +0,14R ; le régime baissier va de −0,26 à −0,44R.
- **Sensibilité aux coûts** : le point mort se situe vers 0,5 à 0,75 × les coûts réels. Avec la remise BNB (sensibilité seulement), l'espérance reste négative.
- **Biais de l'arrêt à 10 %** : aux profils équilibré et dynamique, l'arrêt se déclenche entre décembre 2021 et juin 2022. Les résultats « positifs » du profil dynamique (+3,6 % à +14,1 %) viennent du fait que l'arrêt a figé les gains de 2020-2021. **Sans arrêt**, les mêmes signaux donnent −15 % à −24 %, avec un drawdown de 28 à 38 %. Le biais joue aussi en sens inverse : NXC-06 H4 au profil dynamique est arrêté dès septembre 2020 (−6 %), alors que sans arrêt il finirait à +52 %. L'arrêt est une règle de sécurité ; il ne doit jamais servir à juger un signal.
- **NEXUS B, conclusion nuancée** : les configurations testées (fausse cassure du range nocturne en M5, stop au-delà de la mèche, objectif milieu du range ou 2R, avec ou sans CHoCH, trois hypothèses de session, achat seulement) sont rejetées sur BTC spot. Cela ne permet pas de conclure que le mécanisme général de prise de liquidité n'existe pas sur BTC : d'autres niveaux, unités de temps, stops ou la vente à découvert n'ont pas été testés.

## 4. Moteur : extensions et vérifications pour H1, H4 et D1

- Stop suiveur en cliquet ; valorisation quotidienne des positions sur plusieurs jours ; mesures d'exposition (temps sur le marché, exposition moyenne, turnover, durées) ; date d'arrêt.
- Régimes causals (le régime du jour D n'est utilisable qu'à partir de D+1) ; entrées aléatoires à exposition comparable ; alpha et bêta quotidiens et Sharpe avec IC par blocs de 20 jours ; références passives.
- Laboratoire : budgets d'expériences appliqués techniquement, statut archivé de chaque variante, empreinte des données, graine aléatoire, walk-forward du processus de sélection, alertes de surajustement, reprise d'un lot interrompu sans double comptage.
- Tests : **60 tests réussis**, contre 42 auparavant. Les 18 nouveaux couvrent le stop suiveur, la valorisation quotidienne, la causalité des régimes, l'indépendance au futur des 6 stratégies, les budgets, le walk-forward et l'intégrité des transferts.

## 5. Expériences

| | Nombre |
|---|---|
| Essais antérieurs (phases 2A/2B) | 51 |
| Audit (diagnostic, sans sélection) | 12 |
| C | 12 / budget 12 |
| F | 10 / budget 12 |
| REF (moyenne mobile) | 1 nouveau (famille : 6 / budget 7) |
| REG | 2 / budget 4 |
| D | 4 / budget 8 |
| **Total au registre** | **92** |

Hypothèses testées : NXC-01 à 06 (H1, H4), NXF-01 à 05, REF-SMA-01, REG-01, NXD-01 et 02. Pré-enregistrement : `experiments/preregistration/batch_2c_01.toml` et `batch_2c_02.toml`.

## 6. Résultats bruts et nets — principaux

| Hypothèse | Trades | E[R] sans frottement | E[R] net [IC95] | Coûts ×2 | Aléatoire, expo. comparable | Alpha %/an [IC95] | Part des 5 meilleurs trades | Verdict |
|---|---|---|---|---|---|---|---|---|
| NXC-01 H1 (minimal) | 301 | +0,018 | −0,135 [−0,25 ; −0,00] | −0,27 | −0,106 | — | — | Incompatible |
| NXC-01 H4 (minimal) | 74 | +0,090 | +0,019 [−0,20 ; +0,28] | −0,07 | +0,011 | — | — | Absence |
| NXC-06 H4 (sortie sur invalidation) | 74 | +0,820 | +0,736 [−0,16 ; +1,97] | +0,33 | +0,100 | +4,1 [−3,8 ; +11,1] | 77 % | Absence |
| NXF-01 D1 L = 20 | 51 | +0,380 | +0,363 [+0,03 ; +0,81] | +0,35 | +0,128 | +1,5 [−0,7 ; +3,4] | 74 % | Prometteur (insuffisant) |
| NXF-02 H4 N = 120 | 20 | +3,475 | +3,352 [+0,31 ; +6,57] | +1,41 | +0,339 | +5,9 [−2,4 ; +14,4] | 97 % | Prometteur (insuffisant) |
| REF-SMA-01 D1 (référence) | 24 | +2,046 | +2,023 [−0,16 ; +6,28] | +2,00 | +0,444 | +4,1 [−0,1 ; +8,8] | 97 % | Prometteur (insuffisant) |
| NXD-01 H4 (compression) | 78 | +0,579 | +0,481 [−0,11 ; +1,24] | −0,05 | +0,022 | +3,3 [−2,0 ; +9,0] | 63 % | Absence |
| NXD-02 H4 (contrôle sans compression) | 137 | +0,500 | +0,418 [+0,03 ; +0,89] | +0,10 | +0,006 | +4,5 [−1,5 ; +10,0] | 44 % | Prometteur (insuffisant) |

Références sur la même période :

- **Buy & Hold BTC** : +332 % (CAGR 52 %), drawdown maximal 74 %, Sharpe quotidien 0,95.
- **Liquidités** : 0 %.
- Les stratégies F, D et REF ont un Sharpe quotidien d'environ 1,0 à 1,3, mais leurs IC95 incluent la valeur du Buy & Hold.

Avec 1 000 € et un risque de 0,5 % par trade, la taille dictée par le stop (3 ATR en D1, soit environ 12 %) limite l'exposition moyenne à **1,4 à 5 % du capital**. Les gains en euros sont donc faibles : environ +7 % à +32 % sur 3,5 ans au profil équilibré. Ils sont **bien inférieurs au Buy & Hold**, avec des drawdowns de 2 à 7 %. À **exposition égale**, ces règles font mieux que la détention passive : par exemple, REF-SMA équilibré donne +23,7 % avec un drawdown de 4,8 %, contre +6,7 % avec un drawdown de 11,5 % pour la détention passive à 2 % d'exposition. Mais l'alpha qui mesure précisément cet écart n'est pas significatif. La réduction du risque est **suggérée, non démontrée**.

## 7. Stratégies rejetées et statut

- **Rejetées** (incompatibles ou absence d'avantage démontré) : NXC-01 à 06 en H1 et H4, REG-01, NXD-01 (la compression n'apporte rien : Δ = +0,06R, IC95 [−0,27 ; +0,47] en H4), NXD-02 H1, ainsi que toutes les configurations intraday A et B de la phase 2.
- **Données insuffisantes** (moins de 20 trades) : NXF-02 D1 (N = 20 et 55), NXF-03 L = 60, NXF-04, NXF-05.
- **« Prometteurs mais preuves insuffisantes »** (statut `candidate` au registre, aucune sélection) : NXF-01 (L = 20, L = 60), NXF-02 H4, NXF-03 L = 20, REF-SMA-01, NXD-02 H4.

## 8. Limites statistiques

1. **Peu d'épisodes indépendants** : la période de développement contient environ un cycle haussier, un baissier et une reprise. Les stratégies de tendance D1 et H4 ont 15 à 140 trades, mais leurs résultats reposent sur quelques tendances.
2. **Comparaisons multiples** : 29 essais de sélection dans cette phase (41 avec l'audit) et 92 au total. Les p-valeurs BH les plus favorables (≈ 0,15 à 0,20) restent loin de 0,05.
3. **Concentration** : les profits dépendent de 5 trades dans la plupart des cas « prometteurs ».
4. **Exposition** : aucune variante n'a d'alpha significatif. Les verdicts « prometteurs » respectent la règle pré-enregistrée mais **ne doivent pas être lus comme un avantage propre**.
5. **Walk-forward de la sélection** :
   - C : −0,08R sur 258 trades hors échantillon ;
   - F : +0,09R sur 40 trades, sans significativité ;
   - un processus de choix automatique au sein de C aurait perdu.
6. **Spot achat seulement** : en marché baissier, les stratégies restent souvent en liquidités. C'est voulu, mais cela limite les opportunités et le nombre de trades.

## 9. Erreurs rencontrées

| Erreur | Correction |
|---|---|
| Famille « REF » réutilisée : le budget de 2 incluait les essais REF-SBA antérieurs, et le garde-fou a bloqué le lot | Budget absolu corrigé et journalisé. J'avais d'abord écrit 15 essais antérieurs au lieu de 5 ; c'est corrigé (7 = 5 + 2), avec les 4 entrées conservées dans `budget_changes` |
| Le lanceur réimposait le budget du fichier TOML à chaque démarrage | Le fichier ne crée désormais un budget que s'il n'existe pas |
| Résumés perdus lors de l'interruption | Recalcul déterministe sous le même identifiant et la même graine, sans nouvel essai ; résultats identiques au premier passage |
| Comparaison d'horodatages avec et sans fuseau dans le walk-forward | Normalisation en UTC |
| Test de valorisation quotidienne mal paramétré (lot minimal EUR/USD) | Spécification de test adaptée |
| Décompte de F annoncé à 11 essais au lieu de 10 | Corrigé dans le protocole |

## 10. EUR/USD

Les hypothèses Forex pré-enregistrées (lot 2B-01) sont **inchangées**. Outils ajoutés :

- `scripts/transfer.py verify` : contrôle de chaque fichier téléchargé (décodage, taille, cohérence) ; avec `--repair`, les fichiers corrompus sont supprimés pour être retéléchargés.
- `scripts/transfer.py pack` : archive limitée aux Parquet, au rapport qualité, à `check_env` et à un manifeste SHA-256.
- `scripts/transfer.py import` : refuse tout fichier inattendu, tout chemin hors du projet et toute empreinte invalide.

Le script Windows enchaîne téléchargement avec reprise, vérification, réparation, construction et archive. Il rappelle de lire d'abord les conditions Dukascopy.

## 11. Prochaines décisions nécessaires

1. **Conditions Dukascopy** : les lire vous-même avant de lancer le script Windows, ou m'autoriser à demander l'ajout de `www.dukascopy.com` au réseau de l'environnement pour que je les lise.
2. **Trading réel et §4.2 Binance** : à garder en tête dès maintenant pour l'objectif à long terme. Un examen juridique sera nécessaire avant toute phase en argent réel.
3. **Choix scientifique pour la validation (BTC)**. Je recommande l'option a :
   - a. **ne rien ouvrir pour l'instant**. Seul mécanisme récurrent : la tendance haussière de BTC. Si vous voulez le tester, pré-enregistrer **une seule** hypothèse de famille, « exposition de tendance, achat seulement », avec 2 ou 3 variantes gelées (par exemple REF-SMA-01, NXF-02 H4, NXD-02 H4), et un critère de validation unique : alpha positif contre Buy & Hold à exposition égale, et drawdown inférieur. La validation (2023-07 → 2024-12) serait alors ouverte une seule fois ;
   - b. abandonner BTC et attendre EUR/USD ;
   - c. explorer d'autres familles (E, mean reversion) sur BTC avec un nouveau budget, ce qui ajoute des comparaisons.
4. **Taille d'exposition** : avec un stop obligatoire et 0,25 à 1 % de risque par trade, les stratégies de tendance D1 n'exposent que quelques pourcents du capital. Si l'objectif est un suivi de tendance « en liquidités ou investi », la règle de risque par trade et celle d'exposition maximale devront être discutées. Ce n'est pas une décision technique.
