# NEXUS QUANT — Rapport de phase 2D (diversification et nouvelles hypothèses)

Date : 2026-11-27. Tous les chiffres viennent d'exécutions réelles sur la **période de développement**, journalisées dans `results/registry.sqlite`. Rapports générés automatiquement :

- `reports/phase2d_G_allocation.md`
- `reports/phase2d_E_mean_reversion.md`
- `reports/phase2d_audit_technique.md`

Validation et test final : **verrouillés** (0 accès) ; la validation l'est désormais aussi techniquement.

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

## 1. Conclusions

1. **Aucun avantage statistique n'est démontré.** NEXUS E (retour à la moyenne) est rejeté. NEXUS G (allocation dynamique) donne les résultats les plus encourageants du projet, sans significativité après correction.
2. **NEXUS G** : la règle de moyenne mobile (NXG-01) et l'allocation progressive (NXG-04) battent le portefeuille passif à même exposition de **+2,7 à +3,0 %/an** (plafond 10 %) et **+6,7 à +7,8 %/an** (plafond 25 %).
   - p brut de 0,04 à 0,05 ; **p corrigé (BH) de 0,12** ; IC95 touchant ou incluant 0.
   - Leur rendement est **proche de celui d'un poids fixe égal au plafond** (+0,1 à +1,7 %/an, non significatif), avec un drawdown **nettement plus faible**. Par exemple, NXG-01 à 10 % : +23,3 %, drawdown 4,2 %, contre +21,2 % et drawdown 10,9 % pour le poids fixe 10 %.
   - Le timing **réduit surtout le risque**, en sortant pendant le marché baissier de 2022, plus qu'il n'ajoute du rendement. Le dimensionnement par la volatilité seul (NXG-03) n'apporte **rien**.
3. **Données EUR/USD : bloquées pour raison juridique.** Les conditions Dukascopy interdisent les outils automatisés et la constitution de bases de données sans accord écrit. Le téléchargeur est bloqué dans le code et les 16 fichiers déjà obtenus sont supprimés. Le lot EUR/USD pré-enregistré reste en attente, **sans substitution** par une source de qualité insuffisante.
4. **Audit technique** : 5 défauts trouvés et corrigés (§4). Leur effet sur les résultats antérieurs est faible et **ne change aucun verdict**.

## 2. Conditions d'utilisation (détail : `01_conditions_utilisation.md`)

| Source | Recherche historique personnelle | Stockage local / cloud | Trading réel | Redistribution / commercial |
|---|---|---|---|---|
| Binance Vision (v1.0 du 26/08/2026, PDF SHA-256 `0ec62cd2…`) | **Autorisé** (§4.1) | Local : permis ; cloud : non traité explicitement (données privées, non versionnées) | **Exclu** : §4.2 « live proprietary trading execution » | Exclu (§4.3, §4.4) |
| Dukascopy (TCU lues le 2026-11-27) | Usage personnel non commercial seulement | **Base de données interdite** | Non autorisé (non commercial) | Interdits |
| Dukascopy, outils automatisés | **Interdits sans accord écrit préalable** | — | — | — |

## 3. EUR/USD et sources alternatives

| Option | Statut |
|---|---|
| Accord écrit de Dukascopy | Seule voie vers des données bid/ask M1 de qualité. **Action de votre part** |
| HistData (manuel, bid seulement) | Conditions non lues (hôte non autorisé) |
| Historique d'un compte démo MT5 | Conditions du courtier à lire ; compte à ouvrir par vous |
| Taux de référence BCE (journaliers) | Réutilisation libre avec citation. **Insuffisant** pour le lot intraday pré-enregistré ; utilisable seulement pour une nouvelle hypothèse journalière |

Le script Windows est **bloqué**. Les instructions restent prêtes pour le cas où un accord écrit serait obtenu : renseigner la référence de l'accord dans `NEXUS_DUKASCOPY_WRITTEN_CONSENT`, puis lancer `telecharger_eurusd.ps1`.

## 4. Audit technique (détail : `03_audit_technique.md`)

| Défaut | Correction | Effet mesuré sur les résultats 2C |
|---|---|---|
| 1. Courbe de capital limitée à [1er signal, dernière sortie] | Période entière | Sharpe : −0,09 à +0,05 |
| 2. Buy & Hold démarrant à la clôture du 1er jour | Démarrage au prix d'ouverture | +331,8 % → +332,1 % |
| 3. Valorisation quotidienne au taux d'entrée | Taux du jour | Alpha : −0,4 à +0,07 %/an |
| 4. Validation protégée seulement par le protocole | Verrou technique et journal d'accès | — |
| 5. Statistiques qualité des données incluant la période de validation (phase 2) | Développement seulement ; couverture seule ailleurs | Aucun (contrôle de données) |

- Les résultats enregistrés n'ont pas été modifiés ; les recalculs sont publiés à part.
- Nouveau test de cohérence : une stratégie investie à 100 % reproduit le Buy & Hold à la friction près. C'est la preuve qu'aucun avantage ne provient d'une différence de traitement des frais.
- **Concentration des profits** : celle des candidats de tendance 2C se situe dans la distribution attendue sous le hasard. L'alerte « 5 trades » n'était donc pas discriminante, et je la nuance.

## 5. NEXUS G — résultats sur 1 000 € (fenêtre 2020-05-01 → 2023-07-01)

| Stratégie (plafond) | Final € | Rendement | Max DD | Sharpe | Expo. moy. | Δ vs passif même expo. %/an [IC95] | p BH | Verdict |
|---|---|---|---|---|---|---|---|---|
| NXG-01 MA100 (10 %) | 1 233 | +23,3 % | 4,2 % | 1,38 | 6,0 % | +2,97 [−0,39 ; +6,42] | 0,12 | Prometteur (insuffisant) |
| NXG-04 progressive (10 %) | 1 219 | +21,9 % | 5,5 % | 1,42 | 5,8 % | +2,71 [−0,01 ; +5,72] | 0,12 | Prometteur (insuffisant) |
| NXG-02 momentum 90 j (10 %) | 1 182 | +18,2 % | 7,4 % | 1,13 | 6,0 % | +1,68 [−1,40 ; +5,36] | 0,34 | Absence |
| NXG-03 volatilité (10 %) | 1 183 | +18,3 % | 11,0 % | 0,90 | 9,8 % | −0,63 [−1,88 ; +0,22] | 0,88 | Absence |
| NXG-05 momentum × volatilité (10 %) | 1 162 | +16,2 % | 7,4 % | 1,04 | 5,9 % | +1,20 [−1,89 ; +4,80] | 0,37 | Absence |
| NXG-01 MA100 (25 %) | 1 689 | +68,9 % | 11,0 % | 1,39 | 15,1 % | +7,77 [−0,86 ; +16,47] | 0,12 | Prometteur (insuffisant) |
| NXG-04 progressive (25 %) | 1 625 | +62,5 % | 13,3 % | 1,42 | 14,8 % | +6,65 [−0,30 ; +14,44] | 0,12 | Prometteur (insuffisant) |
| NXG-02 / 03 / 05 (25 %) | 1 468–1 518 | +46,8 à +51,8 % | 17,6–25,5 % | 0,94–1,12 | 15–24 % | −0,91 à +4,18 | ≥ 0,25 | Absence |

**Références sur la même fenêtre** (mêmes coûts) :

- Buy & Hold BTC : 3 510 € (+251 %), drawdown 73,6 %, Sharpe 0,93.
- Liquidités : 1 000 €.
- Poids fixe 10 % : +21,2 %, drawdown 10,9 %.
- Poids fixe 25 % : +57,6 %, drawdown 25,4 %.

**Décomposition**, NXG-01 à 10 % :

- exposition à BTC (passif à 6 %) : +12,3 points ;
- timing : +11,0 points ;
- frais : −1,2 point ;
- alpha de régression : +3,4 %/an, IC95 [−0,3 ; +7,0] ;
- NXG-04 : alpha IC95 [+0,1 ; +6,5], non corrigé pour les comparaisons multiples.

**Épisodes**, NXG-01 à 10 % comparé au passif de même exposition :

- marché baissier novembre 2021 → novembre 2022 : −4,0 % contre −6,4 % ;
- mai–juin 2022 (Terra-Luna, Celsius) : 0,0 % contre −3,3 %.

**Arrêt global à 10 %** (diagnostic seulement) :

- jamais déclenché pour NXG-01, 02, 04 et 05 au plafond de 10 % ;
- déclenché pour NXG-03 à 10 % (9 novembre 2022) et pour toutes les variantes à 25 % (mai 2021 à septembre 2022) ;
- drawdown observé de 10,2 à 12,3 % malgré le seuil : l'arrêt ne garantit pas la perte maximale.

**Limites propres à G** :

- un seul grand marché baissier dans la fenêtre ;
- le krach de mars 2020 tombe pendant la période d'amorçage et n'est pas mesuré ;
- les gains par rapport au passif dépendent principalement de 2022.

## 6. NEXUS E — retour à la moyenne (8 essais)

**Rejeté.**

- Cinq essais sont « incompatibles » (IC95 entièrement négatif) : z-score H1 et H4, écart ATR H1, z-score avec filtre de consolidation H1 et H4.
- Trois sont en « absence d'avantage démontré », dont le choc de rendement H4 : +0,20R, IC95 [−0,11 ; +0,50], 44 trades.
- Le filtre de consolidation n'apporte rien.
- La concentration des profits est inférieure à celle du hasard ; le problème n'est pas la concentration, mais l'espérance négative.

## 7. Hypothèses structurelles (détail : `05_hypotheses_structurelles.md`)

La littérature vérifiée inclut Liu & Tsyvinski (RFS 2021), Moreira & Muir (JF 2017), Hurst, Ooi & Pedersen (JPM 2017), Hansen, Kim & Kim (JFEc 2024), Eross et al. (2019) et Baur et al. (2019). Les résultats publiés y sont distingués des nôtres.

Classement proposé, **aucune hypothèse lancée** :

1. **S1** : reproduction croisée de l'allocation de tendance, avec des règles figées, sur ETH/USDT et EUR/USD journalier (BCE).
2. **S2** : momentum intraday autour de l'ouverture des actions américaines (BTC).
3. **S3** : exécution aux heures de liquidité maximale (reportée, faute de données de spread).

## 8. Validation BTC (proposition non lancée, détail : `06_proposition_validation_btc.md`)

- **Hypothèse unique** : VAL-TREND-01, avec trois variantes figées au plafond de 10 % : NXG-01, NXG-04, et NXG-02 comme contrôle.
- **Critère principal** : différence avec le passif à même exposition, α = 0,05/3.
- **Puissance faible** : la période de validation est majoritairement haussière.

## 9. Fichiers créés et modifiés (phase 2D)

| Catégorie | Fichiers |
|---|---|
| Nouveaux modules | `nexus/portfolio/allocation.py`, `nexus/research/g_runner.py`, `report_2d.py`, `tech_audit_2d.py`, `concentration_2d.py` |
| Modules modifiés | `nexus/engine/backtest.py` (période, MTM), `nexus/stats/metrics.py` (B&H), `nexus/data/store.py` (verrou de validation), `nexus/data/dukascopy.py` (blocage), `nexus/research/registry.py` (journal de validation), `lab_runner.py` (E, période, concentration), `nexus/strategies/trend.py` (E), `random_baseline.py` (concentration), `scripts/build_bars.py`, `scripts/windows/telecharger_eurusd.ps1` |
| Tests | `tests/test_audit_2d.py`, `tests/test_allocation.py`, tests E (causalité), test de blocage Dukascopy |
| Pré-enregistrement | `experiments/preregistration/batch_2d_01.toml` ; brouillon `experiments/drafts/validation_btc_trend_01.toml` |
| Documents | `docs/phase2d/01` à `06`, ce rapport |
| Résultats | `results/batch_2d_01/`, `results/tech_audit_2d/`, `reports/phase2d_*.md` |

## 10. Tests et expériences

- **77 tests réussis** (60 à la fin de 2C, + 17).
- **122 essais au registre** :
  - 98 de sélection (51 en phase 2, 29 en 2C, 18 en 2D) ;
  - 12 audits diagnostiques ;
  - 12 répétitions techniques.
- Budget 2D respecté : G 10/10, E 8/8.

## 11. Erreurs rencontrées

- Téléchargement automatique Dukascopy effectué en phase 2 avant la lecture des conditions (16 fichiers) : supprimés, et la source est bloquée.
- Cinq défauts du moteur et des références (§4).
- Le wiki Dukascopy redirige vers un hôte non autorisé et n'a pas été lu.

## 12. Limites statistiques

- Environ 98 essais de sélection : le seuil de Bonferroni est d'environ z = 3,3, et aucun résultat n'en approche.
- G et F reposent sur un seul cycle haussier, un baissier et une reprise.
- Aucune significativité après correction, même pour les meilleurs G.
- La validation est majoritairement haussière, donc peu puissante pour tester une protection en marché baissier.

## 13. Problèmes juridiques et techniques ouverts

1. Binance Vision §4.2 : un trading réel fondé sur ces données est exclu, sauf licence. **C'est un obstacle à l'objectif final d'un bot en argent réel.**
2. Dukascopy : accord écrit indispensable pour toute utilisation automatisée ou en base de données.
3. Les hôtes Dukascopy restent autorisés dans le réseau de l'environnement, sans être utilisés ; vous pouvez les retirer.

## 14. Prochaines décisions nécessaires

1. **EUR/USD** : demander un accord écrit à Dukascopy, ou m'autoriser à lire les conditions de HistData (`www.histdata.com`), ou abandonner l'intraday Forex.
2. **Validation BTC** : ouvrir VAL-TREND-01 maintenant, malgré la faible puissance, ou d'abord la reproduction S1.
3. **Hypothèses S1/S2** : autoriser leur pré-enregistrement, avec au plus 6 essais supplémentaires.
4. **Objectif final** : faire examiner juridiquement l'usage de données pour un trading réel (Binance §4.2) avant tout investissement de développement du bot en conditions réelles.
