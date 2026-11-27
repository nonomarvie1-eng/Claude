# NEXUS QUANT — Rapport de phase 3 : Liquidity Intelligence

Date : 2026-11-27. **Période de développement uniquement.** Validation et test final verrouillés techniquement (0 accès). Résultats détaillés générés automatiquement : `reports/phase3_liquidity_events.md`.

*Résultats dérivés de données Binance Vision (CC BY-NC-SA 4.0).*

## 1. Conclusion

**Aucun niveau de liquidité ICT ne contient d'information exploitable sur BTC/USDT.**

- Sur 14 tests pré-enregistrés, 13 sont non significatifs. Les probabilités de retournement aux niveaux (FVG, IFVG, FPFVG, Unicorn, swings, raids de Londres et du range PM) valent 0,48 à 0,51, comme pour des niveaux quelconques, et le seuil de rentabilité est d'environ 0,65.
- Le seul effet détecté, la continuation après cassure du range d'ouverture NY (+5,7 points, p corrigé = 0,020), est **sous le seuil de rentabilité** (52,9 % contre 65,6 %) et **ne se réplique pas sur ETH** (+0,4 point, p = 0,43).
- Conformément au protocole, **aucun backtest de stratégie n'a été lancé**, et aucun modèle probabiliste n'est justifié.

Limite majeure : les documents visent surtout NQ/ES et le Forex, qui ne sont pas disponibles. Ces résultats valent pour BTC (transposition [PROP]) et ne réfutent pas les concepts sur leurs marchés d'origine.

## 2. Synthèse des 20 documents

Fiches complètes, matrice des concepts et doublons : `01_audit_20_documents.md`.

- Ce sont **15 vidéos de vulgarisation et 5 transcriptions de stratégies**. Une seule est un backtest systématique (ORB, conclusions négatives) et une seule une étude quantitative (OFI : prédictif, mais non rentable après frais).
- **Aucun document ICT ne fournit de statistique.** Tous les exemples sont choisis après coup. Les affirmations centrales (« algorithme qui contrôle chaque tick », « le prix ne monte que pour deux raisons », « se forme chaque jour ») ne sont pas vérifiables telles quelles.
- **Règles objectivement programmables** : FVG 3 bougies, swings fractals, PDH/PDL/PWH/PWL, extrêmes de sessions horaires NY, relative equal highs/lows, failure swings, IFVG, FPFVG avec déplacement (seuil [PROP]), breaker et Unicorn (structure [PROP]), opening range, fenêtres Silver Bullet.
- **Non programmables sans arbitraire fort** : Market Maker Models (consolidation originale « au savoir-faire »), biais hebdomadaire, « displacement » et « agressif » non quantifiés.
- **Inapplicables à BTC** : NWOG et opening range gap (pas de fermeture de marché). Ross Cameron : pas de stratégie testable, mais des confirmations utiles pour la gestion du risque.

## 3. Méthode

- Pré-enregistrement commité **avant** le code et les résultats : `experiments/preregistration/batch_3_01_events.toml`, commit `1d6b25d`.
- **Amendement 3-01a**, commité avant toute donnée réelle (`7bbe643`). La calibration sur une marche aléatoire synthétique a révélé un biais : des contrôles de distance faussent la probabilité de contact de +1,4 à +10 points sous l'hypothèse nulle. La métrique de contact utilise désormais des contrôles décalés dans le temps, à même distance normalisée par l'ATR et à même heure NY ; le biais disparaît. Un test automatisé vérifie cette absence de biais.
- **Métriques** :
  - contact du niveau (effet d'aimant) ;
  - course de barrières à ±1 ATR H1 : retournement ou franchissement, une minute ambiguë étant comptée comme franchissement ;
  - franchissement et réintégration en clôture M5 ;
  - délai de contact, MFE et MAE.
- **Inférence** : bootstrap par blocs de semaines et correction de Benjamini–Hochberg sur 14 tests.

## 4. Résultats des études événementielles (BTC/USDT, 2020-01 → 2023-06)

| Test | n | Réel | Contrôle | Δ [IC95] | p BH | Lecture |
|---|---|---|---|---|---|---|
| PDH/PDL (aimant) | 2 544 | 44,5 % touchés | 46,7 % | −2,3 [−3,7 ; −0,8] | 1,00 | **Moins** touchés que des niveaux témoins : contraire au document |
| PWH/PWL (aimant) | 362 | 28,5 % | 26,0 % | +2,5 [−2,1 ; +7,1] | 0,61 | Non significatif |
| Raid de Londres 02–05 NY | 1 851 | 50,6 % de retournements | 52,2 % | −1,6 | 1,00 | Aucun effet « Judas swing » |
| Range PM de la veille | 567 | 47,6 % | 50,3 % | −2,6 | 1,00 | Aucun effet |
| Swings H1 | 6 941 | 48,1 % | 50,0 % | −2,0 [−3,1 ; −0,8] | 1,00 | Légèrement moins de retournements |
| Relative equal highs/lows | 469 | 80,0 % touchés | 80,7 % | −0,8 | 1,00 | Pas d'aimant particulier |
| Failure swings (LRL) | 4 689 | 82,1 % | 81,7 % | +0,4 | 0,61 | L'écart brut LRL/HRL (82 % contre 76 %) **s'explique par la distance** |
| FVG M5 (CE) | 30 982 | 50,4 % | 49,8 % | +0,6 | 0,61 | Aucun |
| FVG inversé | 30 896 | 50,6 % | 50,0 % | +0,7 | 0,61 | Aucun |
| First Presented FVG avec déplacement | 1 145 | 51,3 % | 52,4 % (autres FVG du jour) | −1,2 | 1,00 | Aucun |
| Unicorn | 5 148 | 49,6 % | 48,0 % | +1,7 [−0,3 ; +3,7] | 0,45 | Non significatif |
| **Opening range 09:30–10:00 NY** | 1 158 | **52,9 % de continuation** | 47,3 % (range 03:30) | **+5,7 [+1,8 ; +9,4]** | **0,020** | Information réelle, mais seuil de 65,6 % non atteint ; non répliqué sur ETH |
| Fenêtres Silver Bullet | 3 804 | 49,8 % | 49,2 % (fenêtres témoins) | +0,6 | 0,61 | Aucun effet horaire |
| SMT BTC/ETH | 1 218 | 48,9 % | 50,4 % (balayages sans SMT) | −1,5 | 1,00 | La SMT n'améliore pas le simple balayage |

**ORB, comme le document le décrivait** :

- les cassures sans retest continuent à 76,9 %, celles avec retest à 47,2 %. Ce conditionnement utilise les 30 minutes suivantes : c'est un constat descriptif du biais de sélection, pas un signal ;
- la taille de la cassure ne change rien (51,6 % contre 54,2 %) ;
- l'effet est stable par année (52 à 54 %).

## 5. Diagnostics

- **Cointégration BTC/ETH** :
  - corrélation des rendements de 0,84, mais seulement **5,6 % des fenêtres** de 180 jours passés sont cointégrées, soit le taux de faux positifs attendu ;
  - β roulant de 0,03 à 1,23, et rupture structurelle massive (CUSUM).
  - Corrélation n'est pas cointégration. Un arbitrage de spread est en outre infaisable en spot sans vente à découvert.
- **OFI** : à la minute, aucun pouvoir prédictif (Spearman de −0,01 à −0,02 ; écart entre déciles de 0,06 point de base contre 24 de coûts). Cela concorde avec le document : l'information vit à l'échelle de quelques secondes, et une telle stratégie est hors de portée d'un particulier après frais. Seul usage envisageable : améliorer l'exécution d'ordres d'une stratégie lente, ce qui suppose des données tick à collecter en temps réel.

## 6. Étape 7 : faut-il des backtests ?

**Non.** Le protocole exigeait les critères d'information et d'exploitabilité à la fois, et aucun test ne les satisfait. Le budget de backtests NLI-BT (6 essais) reste intact. Aucun modèle logistique n'est entraîné : aucun signal crédible et exploitable n'existe à modéliser, et transformer des confluences en probabilité serait précisément l'erreur que vous avez demandé d'éviter.

## 7. Fichiers créés ou modifiés

| Catégorie | Fichiers |
|---|---|
| Détecteurs et événements | `nexus/liquidity/levels.py`, `nexus/liquidity/events.py` |
| Recherche | `nexus/research/nli_runner.py`, `nli_diag.py`, `report_3.py` |
| Tests | `tests/test_liquidity.py` (10 tests, dont la calibration sous l'hypothèse nulle) |
| Pré-enregistrement | `experiments/preregistration/batch_3_01_events.toml` (avec l'amendement 3-01a) |
| Documents | `docs/phase3/01_audit_20_documents.md`, `02_donnees_legalite.md`, ce rapport |
| Résultats | `results/batch_3_01_events/`, `reports/phase3_liquidity_events.md`, `reports/data_quality/ETHUSDT.json` |
| Données | ETH/USDT M1 2020-01 → 2026-06 (Binance Vision, sommes de contrôle vérifiées, non versionnées) |
| Correctif | `scripts/build_bars.py` : toute paire USDT est traitée comme Binance |

## 8. Tests et expériences

- **87 tests réussis**, dont 10 nouveaux.
- **139 essais au registre** :
  - 113 de sélection, dont 15 cette phase (14 BTC et 1 réplication ETH) ;
  - 14 diagnostics, dont 2 cette phase ;
  - 12 répétitions techniques.

## 9. Résultats en euros

Aucun backtest n'étant justifié, il n'y a **aucun résultat en euros** dans cette phase. Les résultats en euros des familles antérieures restent ceux des phases 2C et 2D.

## 10. Limites

1. **Transposition** : NQ/ES et Forex indisponibles ; BTC est un marché 24 h/24, sans séance d'ouverture « officielle ».
2. **Définitions [PROP]** : seuils de déplacement, tolérance des equal highs, structure du breaker, tolérance SMT de ±2 h. D'autres choix raisonnables existent, mais les essayer tous serait du surajustement.
3. **Barrières à ±1 ATR H1 seulement** : d'autres géométries (objectif lointain, stop serré) n'ont pas été mesurées.
4. **ETH** est fortement corrélé à BTC ; ce n'est pas une réplication indépendante au sens fort.

## 11. Décisions nécessaires

1. **Données d'indices** : acheter un historique de futures NQ/ES (coût à chiffrer, autorisation requise) pour tester les concepts ICT sur leur marché d'origine, ou y renoncer.
2. **EUR/USD** : voir la phase 2D (accord Dukascopy, HistData ou compte démo).
3. **Orientation** : les études sur BTC ne montrent d'information exploitable ni dans les niveaux ICT, ni dans les familles A à F. Seul l'axe allocation de tendance (NEXUS G) garde un statut « prometteur, preuves insuffisantes ». Je recommande de concentrer la suite sur sa validation (proposition VAL-TREND-01, en attente de votre décision) plutôt que sur de nouvelles variantes intraday.
