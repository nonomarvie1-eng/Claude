## Études événementielles Liquidity Intelligence — lot 3-01 (période de développement)

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

Code `7bbe643` ; essais au registre après le lot BTC : 136.

Δ = métrique(niveaux réels) − métrique(contrôles) ; IC95 bootstrap par semaines ; p unilatéral ; BH sur les 14 tests BTC.

| Test | Métrique principale | n réel / contrôle | Réel | Contrôle | Δ [IC95] | p | p BH | Information | P(contact) réel | P(retournement) réel | Seuil de rentabilité | Exploitable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EV-01-PDHL | M_target | 2544 / 7632 | 0.445 | 0.467 | -0.023 [-0.037 ; -0.008] | 0.9976 | 0.9992 | non | 0.445 | 0.451 | 0.651 | — |
| EV-02-PWHL | M_target | 362 / 1086 | 0.285 | 0.260 | +0.025 [-0.021 ; +0.071] | 0.1416 | 0.6111 | non | 0.285 | 0.427 | 0.661 | — |
| EV-03-LONDON | M_reaction | 1851 / 3078 | 0.506 | 0.522 | -0.016 [-0.042 ; +0.009] | 0.8898 | 0.9992 | non | 0.730 | 0.506 | 0.659 | non |
| EV-04-PMRANGE | M_reaction | 567 / 1182 | 0.476 | 0.503 | -0.026 [-0.069 ; +0.015] | 0.8814 | 0.9992 | non | 0.345 | 0.476 | 0.648 | non |
| EV-05-SWING | M_reaction | 6941 / 17325 | 0.481 | 0.500 | -0.020 [-0.031 ; -0.008] | 0.9992 | 0.9992 | non | 0.791 | 0.481 | 0.654 | non |
| EV-06-EQHL | M_target | 469 / 1407 | 0.800 | 0.807 | -0.008 [-0.051 ; +0.035] | 0.6467 | 0.9992 | non | 0.800 | 0.448 | 0.661 | — |
| EV-07-LRL | M_target | 4689 / 14067 | 0.821 | 0.817 | +0.004 [-0.009 ; +0.017] | 0.3055 | 0.6111 | non | 0.821 | 0.484 | 0.657 | — |
| EV-08-FVG | M_reaction | 30982 / 9179 | 0.504 | 0.498 | +0.006 [-0.008 ; +0.020] | 0.2218 | 0.6111 | non | 0.934 | 0.504 | 0.659 | non |
| EV-09-IFVG | M_reaction | 30896 / 7370 | 0.506 | 0.500 | +0.007 [-0.010 ; +0.023] | 0.2118 | 0.6111 | non | 0.942 | 0.506 | 0.659 | non |
| EV-10-FPFVG | M_reaction | 1145 / 8456 | 0.513 | 0.524 | -0.012 [-0.040 ; +0.018] | 0.7774 | 0.9992 | non | 0.901 | 0.513 | 0.658 | non |
| EV-11-UNICORN | M_reaction | 5148 / 5011 | 0.496 | 0.480 | +0.017 [-0.003 ; +0.037] | 0.0646 | 0.4521 | non | 0.884 | 0.496 | 0.659 | non |
| EV-12-ORB | M_continuation | 1158 / 1185 | 0.529 | 0.473 | +0.057 [+0.018 ; +0.094] | 0.0014 | 0.0196 | oui | — | — | — | — |
| EV-13-SILVERBULLET | M_reaction | 3804 / 3682 | 0.498 | 0.492 | +0.006 [-0.017 ; +0.029] | 0.3051 | 0.6111 | non | 0.917 | 0.498 | 0.660 | non |
| EV-14-SMT | M_reaction | 1218 / 1820 | 0.489 | 0.504 | -0.015 [-0.053 ; +0.021] | 0.7880 | 0.9992 | non | — | — | — | — |

### Mesures complémentaires (niveaux réels)

| Test | Niveaux | Déjà franchis à la disponibilité | Délai médian de contact (h) | P(clôture M5 au-delà) | P(réintégration \| franchissement) | MFE médiane (ATR) | MAE médiane (ATR) | Distance médiane (ATR) | Coût moyen (ATR) |
|---|---|---|---|---|---|---|---|---|---|
| EV-01-PDHL | 2544 | 0 | 8.0 | 0.748 | 0.491 | 2.14 | 2.42 | 2.16 | 0.303 |
| EV-02-PWHL | 362 | 0 | 12.9 | 0.680 | 0.343 | 3.56 | 4.32 | 6.82 | 0.322 |
| EV-03-LONDON | 2544 | 2 | 1.9 | 0.723 | 0.623 | 2.11 | 2.04 | 0.67 | 0.318 |
| EV-04-PMRANGE | 2552 | 896 | 1.0 | 0.732 | 0.581 | 1.73 | 1.96 | 1.67 | 0.295 |
| EV-05-SWING | 8778 | 1 | 4.8 | 0.754 | 0.550 | 3.05 | 2.94 | 1.01 | 0.309 |
| EV-06-EQHL | 469 | 0 | 4.4 | 0.821 | 0.468 | 3.22 | 3.03 | 0.97 | 0.323 |
| EV-07-LRL | 4690 | 1 | 4.3 | 0.740 | 0.570 | 3.08 | 2.96 | 0.90 | 0.314 |
| EV-08-FVG | 33301 | 0 | 0.3 | 0.773 | 0.656 | 2.02 | 2.01 | 0.21 | 0.319 |
| EV-09-IFVG | 32897 | 1 | 0.1 | 0.789 | 0.645 | 2.03 | 2.03 | 0.17 | 0.319 |
| EV-10-FPFVG | 1277 | 0 | 0.3 | 0.752 | 0.675 | 2.00 | 2.01 | 0.29 | 0.316 |
| EV-11-UNICORN | 5840 | 0 | 0.8 | 0.739 | 0.651 | 2.03 | 2.08 | 0.41 | 0.317 |
| EV-13-SILVERBULLET | 4164 | 0 | 0.3 | 0.772 | 0.659 | 2.00 | 2.03 | 0.23 | 0.320 |

**ORB (EV-12)** : continuation 0.529 contre 0.473 pour le range de contrôle. Avec retest dans les 6 bougies : 0.472 (n = 933) ; sans retest : 0.769 (n = 225). Ce conditionnement utilise l'information des 30 minutes suivantes : il est **descriptif** (confirme le biais de sélection décrit par le document ORB), pas un signal. Grande cassure : 0.516 ; petite : 0.542.

**LRL vs HRL (EV-07, comparaison brute)** : P(contact) 0.821 contre 0.757, Δ = +0.064 [+0.047 ; +0.082]. Contre des contrôles à même distance normalisée, l'effet disparaît : l'écart brut s'explique par la distance.

**Silver Bullet (EV-13), P(retournement) par heure de formation du FVG (NY)** : 3 h : 0.492 (n = 1470) ; 10 h : 0.522 (n = 1238) ; 14 h : 0.481 (n = 1096) ; 5 h : 0.499 (n = 1309) ; 12 h : 0.490 (n = 1023) ; 16 h : 0.488 (n = 1350)

**SMT BTC/ETH (EV-14)** : P(retournement) avec SMT 0.487 (n = 1223) ; sans SMT 0.501 (n = 1833).

**Réplication ETH (EV-12-ORB)** : Δ = +0.004 [-0.038 ; +0.045], p = 0.431 → **non répliqué**.

**Diagnostic cointégration BTC/ETH** : fenêtres cointégrées à 5 % : 5.6 % ; β roulant de 0.03 à 1.23 ; corrélation des rendements quotidiens 0.84 ; CUSUM p = 1.3e-114.

**Diagnostic OFI (minute)** : Spearman h = 1 min : -0.010 ; h = 5 min : -0.021 ; écart entre déciles extrêmes +0.06 pb (1 min), -0.27 pb (5 min), contre 24.0 pb de coût aller-retour.