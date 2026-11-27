# 06 — Ressources, coûts et temps de calcul

## 1. Environnement inspecté

**Important : je n'ai pas pu inspecter votre PC Windows.** Cette session s'exécute dans un conteneur Linux cloud (aucun ordinateur personnel n'est relié à la session). Ce que j'ai mesuré ici :

| Élément | Conteneur cloud (session actuelle) | Votre PC (déclaré) |
|---|---|---|
| OS | Linux x86_64 | Windows |
| CPU | 4 vCPU | à mesurer |
| RAM | 15 Go | ≈ 8 Go |
| GPU | aucun | aucun dédié |
| Disque libre | ≈ 61 Go | à mesurer |
| Python | 3.13, numpy 2.5, pandas 3.0 | à mesurer |
| Réseau | Dépôts de paquets uniquement ; sources de données bloquées (403) | Libre |

Pour mesurer votre PC : exécuter `python scripts/check_env.py` (fourni dans ce dépôt, lecture seule, aucune installation, aucun accès réseau) et me transmettre la sortie.

Pile logicielle proposée (toute open source, gratuite, compatible Windows sans compilateur) : Python 3.12, `numpy`, `pandas`, `pyarrow` (Parquet), `numba` (accélération des boucles de simulation sur CPU), `scipy`, `statsmodels`, `duckdb` (requêtes sur Parquet sans tout charger en RAM), `matplotlib`/`plotly`, `streamlit` (tableau de bord local), `pytest`, `pydantic` (validation des configs), `sqlite3` (bibliothèque standard). Pas de framework de backtest tiers comme moteur principal : aucun ne gère nativement la résolution intrabar conservatrice, bid/ask, lots minimaux et funding comme requis ; ils pourront servir de contrôle croisé.

## 2. Contrainte du capital (révisée en phase 2 : 1 000 €)

> Révision phase 2 : le capital simulé de référence est désormais **1 000 €** (décision validée). Les pourcentages ci-dessous ont été recalculés ; la version 500 € est conservée dans l'historique git.

Risque minimal imposé par le **lot minimal** (spécifications CFD courantes, à vérifier chez un courtier) :

| Instrument (lot min) | Stop typique M5–M15 | Risque au lot min | % de 1 000 € |
|---|---|---|---|
| EUR/USD (0,01 lot) | 10–20 pips | 0,93–1,85 € | 0,09–0,19 % |
| USD/JPY (0,01 lot) | 10–20 pips | 0,62–1,23 € | 0,06–0,12 % |
| XAU/USD (0,01 lot = 1 oz) | 5–10 $ | 4,63–9,26 € | 0,46–0,93 % |
| NASDAQ 100 CFD (0,1 $/pt) | 20–40 pts | 1,85–3,70 € | 0,19–0,37 % |
| DAX CFD (0,1 €/pt) | 20–40 pts | 2,00–4,00 € | 0,20–0,40 % |
| Micro future MNQ (2 $/pt) | 20–40 pts | 37–74 € | **3,7–7,4 %** → exclu |
| Crypto spot (min. ≈ 5 USDT notionnel) | — | quasi continu | OK |

Conséquences :

- Profil prudent (0,25 % = 2,50 €) : sur XAU/USD, la plupart des stops dépassent le budget au lot minimal → trades refusés. Sur EUR/USD, un stop > ≈ 27 pips est refusé.
- Le dimensionnement reste quantifié (pas de 0,01 lot) : le risque réel est arrondi vers le bas et le moteur simule exactement cet arrondi.
- Les futures restent incompatibles avec ce capital ; seuls les CFD et le spot sont réalistes.
- Aucune estimation de revenu n'est présentée avant d'avoir des résultats empiriques suffisants (décision phase 2).

## 3. Coûts d'exécution exprimés en R (point critique)

`coût_R = (spread + commission aller-retour + slippage) / distance du stop`

Exemple EUR/USD avec un coût total d'≈ 1 pip (spread brut ECN + commission + slippage — ordre de grandeur, à calibrer) :

| Distance de stop | Coût en R par trade | Effet sur un RR 4 (point mort 20 %) |
|---|---|---|
| 5 pips (M1, S4) | **0,20R** | Point mort relevé à ≈ 24 % |
| 10 pips | 0,10R | ≈ 22 % |
| 20 pips (S1 typique) | 0,05R | ≈ 21 % |
| 60 pips (H4, S3) | 0,017R | ≈ 20,3 % |

Les stratégies M1 doivent donc produire un avantage brut **plusieurs fois supérieur** à celui d'une stratégie H4 pour le même résultat net.

## 4. Coût financier

| Poste | Coût |
|---|---|
| Données (Dukascopy, HistData, Binance, MT5 démo) | 0 € |
| Logiciels | 0 € |
| Calcul | 0 € (PC local) |
| Option données futures (Databento, FirstRate…) | Non engagé ; uniquement sur votre accord, et seulement si nécessaire |

## 5. Stockage

≈ 250–400 Mo de Parquet M1 pour les 8 instruments sur 6 ans ; ≈ 1 Go avec les fichiers bruts ; + quelques Go optionnels de ticks ciblés. Résultats et journal SQLite : < 1 Go. **Total prévu : 2–5 Go.**

## 6. Temps de calcul (estimations, à mesurer sur votre PC)

| Tâche | Estimation |
|---|---|
| Features causales (swings, FVG, EMA, ATR) pour 1 actif M1 × 6 ans | 10–60 s (numpy/numba) |
| 1 backtest événementiel 1 actif × 6 ans, numba | ≈ 0,1–1 s ; en Python pur 10–60 s |
| Grille complète : 7 stratégies × ~50 configs × 8 actifs × 6 plis WF | ≈ 17 000 backtests → **≈ 0,5–5 h** sur 4 cœurs avec numba |
| Monte-Carlo 10 000 tirages sur listes de trades | secondes à minutes |
| Entrées aléatoires appariées (1 000 × stratégie × actif) | ≈ 1–3 h au total |

8 Go de RAM suffisent si l'on traite **un actif à la fois** et en `float32`, avec 2–3 processus parallèles maximum.

## 7. Temps humain

Voir `08_plan_developpement.md` : ≈ 6 à 10 semaines de développement et de recherche à rythme régulier avant une conclusion sur l'existence d'un avantage, puis ≥ 3 mois de paper trading.
