# Phase 2D — Littérature et hypothèses structurelles (non lancées)

## 1. Ce que dit la littérature (résultats publiés, non reproduits par nous sauf mention)

| Thème | Référence (vérifiée par recherche le 2026-11-27) | Résultat publié | Ce que NOUS avons observé |
|---|---|---|---|
| Time-series momentum, multi-actifs | Moskowitz, Ooi & Pedersen (2012), *Journal of Financial Economics* — référence classique, non revérifiée en ligne dans cette session | Persistance des rendements sur 1 à 12 mois dans des dizaines de marchés à terme | — |
| Trend following, long terme | Hurst, Ooi & Pedersen (2017), « A Century of Evidence on Trend-Following Investing », *Journal of Portfolio Management* ([PDF](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)) | Rendements mensuels de 67 marchés dans 4 classes d'actifs, bruts et nets de coûts simulés | F et G sur BTC : positifs, mais non distinguables de l'exposition (F) ou prometteurs sans significativité (G) |
| Momentum crypto | Liu & Tsyvinski (2021), « Risks and Returns of Cryptocurrency », *Review of Financial Studies* 34(6) ([NBER w24877](https://nber.org/papers/w24877)) | Momentum de série temporelle significatif aux fréquences journalière et hebdomadaire (BTC, XRP, ETH) | NXF-01 L = 20 : E[R] +0,36 [+0,03 ; +0,81], mais alpha non significatif |
| Volatility targeting | Moreira & Muir (2017), « Volatility-Managed Portfolios », *Journal of Finance* 72(4) ([NBER w22208](https://www.nber.org/papers/w22208)). Résultats hors échantillon contestés dans des travaux ultérieurs | Mise à l'échelle par l'inverse de la variance passée : Sharpe amélioré sur plusieurs facteurs actions | NXG-03 sur BTC : **aucune contribution** (−0,6 %/an contre le passif à même exposition) |
| Périodicité intraday de la volatilité crypto | Hansen, Kim & Kim (2024), « Periodicity in Cryptocurrency Volatility and Liquidity », *Journal of Financial Econometrics* 22(1) ; Eross, McGroarty, Urquhart & Wolfe (2019), *Research in International Business and Finance* 49 ([lien](https://eprints.soton.ac.uk/429352/)) | Volatilité et volume périodiques (jour, semaine, heure), plus élevés aux ouvertures des grandes places boursières | — |
| Rendements par heure ou par jour (crypto) | Baur, Cahill, Godfrey & Liu (2019), *Finance Research Letters* 31 ([RePEc](https://econpapers.repec.org/RePEc:eee:finlet:v:31:y:2019:i:c:p:78-92)) | Anomalies ponctuelles, **non persistantes** dans le temps | Cohérent avec nos rejets intraday (A, B, M5) |
| Momentum intraday aux ouvertures | Gao, Han, Li & Zhou (2018), « Market Intraday Momentum », *JFE* — référence classique, non revérifiée en ligne dans cette session | La 1re demi-heure prédit la dernière sur le S&P 500 (ETF) | — |

Un article publié n'est pas une preuve d'exploitabilité avec 1 000 €, nos frais (0,2 % aller-retour sur BTC spot) et nos instruments.

## 2. Trois hypothèses prioritaires proposées (classement)

Notes de 1 (faible) à 3 (fort). Pour la taille d'échantillon et le risque de surajustement, 3 = favorable.

| Critère | **S1. Reproduction croisée de l'allocation de tendance** (règles NXG-01 et NXG-04 figées, sur ETH/USDT, et sur EUR/USD journalier BCE en achat/vente via CFD) | **S2. Momentum intraday autour de l'ouverture US** sur BTC (rendement de la 1re heure après 15:30 Paris → rendement jusqu'à 22:00 Paris) | **S3. Exécution au moment de liquidité maximale** (rééquilibrer G aux heures de plus forte liquidité pour réduire les coûts) |
|---|---|---|---|
| Justification économique | 3 (comportements de suivi de tendance, primes de risque ; littérature abondante) | 2 (Gao et al. 2018 sur les actions ; volatilité plus forte aux ouvertures : Eross 2019) | 2 (périodicité de la liquidité : Hansen et al. 2024) |
| Données disponibles | 3 (Binance Vision ; BCE) | 3 (Binance Vision) | 1 (pas de spreads historiques spot dans les archives klines) |
| Coûts d'exécution | 3 (turnover 1,4 à 4 par an) | 1 (0,2 % aller-retour pour des mouvements horaires d'environ 0,5 %) | 3 (vise justement les coûts) |
| Faisabilité technique | 3 (simulateur G réutilisé tel quel) | 3 (cadre A réutilisé) | 1 (mesure du spread impossible avec nos données) |
| Taille d'échantillon | 1 (journalier ; peu d'épisodes de tendance indépendants) | 3 (≈ 1 250 jours) | 2 |
| Risque de surajustement | 3 (aucun paramètre nouveau : règles figées) | 2 (1 à 2 paramètres fixés a priori) | 2 |
| **Total** | **16** | **14** | **11** |

**Recommandation** : S1 en priorité, avec au plus 4 essais : 2 règles × 2 marchés (ETH/USDT, EUR/USD BCE).

- Les essais sur EUR/USD BCE exigeraient une nouvelle hypothèse journalière. Ils ne remplacent pas le lot intraday 2B-01.
- S2 est envisageable avec au plus 2 essais.
- S3 est reportée faute de données de spread.

**Rien n'est pré-enregistré ni lancé sans votre accord.** Si vous l'acceptez, ces essais s'ajouteraient au budget global, environ 116 + 6 essais au maximum.
