# 04 — Sources de données historiques

Statut de vérification : les informations ci-dessous proviennent de ma connaissance des fournisseurs et **n'ont pas pu être vérifiées en ligne depuis cet environnement** (l'accès réseau de la session cloud est limité aux dépôts de paquets : `data.binance.vision`, `datafeed.dukascopy.com`, `histdata.com` et Yahoo renvoient 403 au proxy). Elles devront être revérifiées depuis votre PC avant tout téléchargement, ainsi que les **conditions d'utilisation** de chaque source.

## 1. Sources gratuites recommandées

| Source | Instruments couverts | Résolution | Profondeur | Bid/Ask | Fuseau | Remarques |
|---|---|---|---|---|---|---|
| **Dukascopy** (datafeed public) | EUR/USD, GBP/USD, USD/JPY, XAU/USD ; CFD indices USA100 (NASDAQ 100), DEU40 (DAX) ; quelques cryptos | Ticks et bougies M1 | FX ≈ 2003+, indices CFD ≈ 2012+ (à vérifier) | **Oui (bid et ask séparés)** | UTC | Meilleure source gratuite pour FX/or : permet de mesurer le spread réel minute par minute et de descendre au tick pour les cas ambigus. Format `.bi5` (LZMA), outils open source disponibles. Usage personnel : vérifier les CGU. Le volume est un volume de cotations, pas un volume d'échange. |
| **HistData.com** | EUR/USD, GBP/USD, USD/JPY, XAU/USD, + quelques indices (SPX, NSX, GRX ≈ DAX) | M1 et ticks | 2000+ pour FX | Bid seulement en M1 | **EST fixe sans DST (UTC−5)** | Bon contrôle croisé de Dukascopy. Le fuseau fixe impose une conversion explicite. |
| **Binance Data Vision** | BTC/USDT, ETH/USDT spot et perpétuels USDT-M, **historique de funding** | Bougies 1 s à 1 mois, trades agrégés | Spot 2017+, futures 2019+ | Non (trades/OHLCV) ; spread estimable via bookTicker récent | UTC | Fichiers mensuels ZIP + checksum, gratuits, publics. Source idéale pour la crypto. |
| **MetaTrader 5 (compte démo)** via le paquet Python `MetaTrader5` (Windows uniquement) | Les symboles du courtier (FX, or, CFD DAX/NASDAQ) | M1 et ticks | Variable selon courtier (souvent 1–10 ans en M1) | Spread par bougie | Heure serveur du courtier (souvent UTC+2/+3) | Avantage : **spécifications exactes** du courtier (taille de contrat, lot min, pas, swaps). **Risque : le paquet permet aussi d'envoyer des ordres** → module isolé, compte démo uniquement, fonction d'envoi d'ordres jamais importée (vérifié par test). |
| **OANDA v20 (compte de démonstration)** | FX, or, CFD indices | M1 (candles bid/ask/mid) | ≈ 2005+ | Oui | UTC | API gratuite avec compte practice ; même réserve que MT5 sur l'existence d'endpoints d'ordres. Disponibilité selon le pays à vérifier. |
| **Yahoo Finance** (`yfinance`) | ^NDX, ^GDAXI, futures | 1 min sur ~7–30 jours, 1 h sur ~2 ans | Insuffisant pour l'intraday | Non | Local | Utile uniquement pour du journalier (contrôle, régimes). |

## 2. Sources payantes (non utilisées sans votre accord)

| Source | Intérêt | Coût |
|---|---|---|
| Databento | Futures CME (NQ, MNQ) et Eurex (FDAX), qualité institutionnelle | Paiement à l'usage ; crédit d'essai offert à l'inscription (montant à vérifier) |
| FirstRate Data, Kibot, Portara | Historiques M1 de futures et indices, achat unique | Typiquement quelques dizaines à quelques centaines d'euros (à vérifier) |
| Tick Data LLC, TickStory (export Dukascopy facilité) | Qualité / confort | Variable |

Recommandation : **aucune dépense en phase 2**. Les sources gratuites couvrent les 8 instruments en qualité suffisante pour une première recherche. Un achat ne serait justifié que si une stratégie sur indices survit et qu'il faut la valider sur le vrai future.

## 3. Correspondance instrument → source

| Instrument | Source principale | Contrôle croisé | Point de vigilance |
|---|---|---|---|
| EUR/USD, GBP/USD, USD/JPY | Dukascopy M1 bid+ask | HistData M1 | Spread élargi autour de 23:00 Paris (rollover) |
| XAU/USD | Dukascopy M1 bid+ask | HistData | Spread variable, gaps d'ouverture du dimanche, pause quotidienne |
| BTC/USDT, ETH/USDT | Binance spot M1 + perp M1 + funding | — | 24/7 ; le spot ne permet pas la vente à découvert → la vente se modélise sur le perpétuel avec funding |
| NASDAQ 100 | Dukascopy CFD USA100 M1 | MT5 démo | CFD ≠ indice cash ≠ future NQ ; dividendes/ajustements ; horaires CFD quasi 23 h/24 |
| DAX 40 | Dukascopy CFD DEU40 M1 | MT5 démo | Indice cash Xetra 09:00–17:30 Paris ; le « range asiatique » sur le DAX n'existe que sur CFD/future (marché peu liquide la nuit) |

## 4. Horaires, fuseaux et changements d'heure

- Stockage **systématiquement en UTC**, conversion à la volée via `zoneinfo` pour chaque session.
- Europe/Paris : DST de fin mars à fin octobre. America/New_York : DST de mi-mars à début novembre. **Deux à trois semaines par an** où l'écart Paris–New York est de 5 h au lieu de 6 h : l'ouverture US de 09:30 NY tombe à 14:30 Paris (normal 15:30). Toute stratégie codée en heure fixe d'un seul fuseau se décale pendant ces semaines.
- Asia/Tokyo n'a pas de DST : le range « asiatique » en heure de Paris ne correspond donc pas aux mêmes heures de Tokyo selon la saison. D'où les variantes de fuseau prévues dans S1.
- HistData : EST fixe (UTC−5) toute l'année. MT5 : heure serveur du courtier (à mesurer, pas à supposer).
- Jours fériés, clôtures anticipées (Noël, Thanksgiving), sessions réduites : détectés par couverture de données, pas par calendrier codé à la main.

## 5. Contrôles qualité prévus à l'ingestion

1. Monotonie et unicité des horodatages ; trous > N minutes hors week-end listés.
2. `L ≤ min(O, C) ≤ max(O, C) ≤ H` ; ask ≥ bid.
3. Détection de pics aberrants (rendement M1 > 10 × ATR) → signalés, pas supprimés silencieusement.
4. Comparaison Dukascopy vs HistData sur les clôtures M1 (écart médian, quantile 99 %).
5. Rapport de couverture par jour/session stocké avec chaque jeu de données (hash SHA-256 du fichier).

## 6. Volume et stockage estimés (avant téléchargement)

Bougies M1, 6 ans (2020-01 → 2025-12), bid+ask :

| Ensemble | Lignes | Taille brute float32 | Parquet compressé (estimation) |
|---|---|---|---|
| 1 paire FX (≈ 372 000 min/an) | ≈ 2,2 M | ≈ 80 Mo | ≈ 25–40 Mo |
| 1 crypto 24/7 (525 600 min/an) | ≈ 3,2 M | ≈ 110 Mo | ≈ 40–60 Mo |
| **8 instruments** | ≈ 19 M | ≈ 700 Mo | **≈ 250–400 Mo** |

Ticks : plusieurs centaines de Mo à quelques Go par paire et par an. **Non téléchargés en masse** : uniquement à la demande, pour les bougies où SL et TP sont touchés simultanément (typiquement < 5 % des trades).

Mémoire : un actif M1 sur 6 ans tient en ≈ 100–200 Mo dans pandas ; on traite un actif à la fois → compatible avec 8 Go de RAM.

Temps de téléchargement : Dukascopy sert un fichier M1 par jour et par côté (bid/ask) : ≈ 6 × 260 × 2 ≈ 3 100 requêtes par instrument. À un rythme courtois (1–2 requêtes/s), ≈ 30–60 min par instrument, 4–6 h pour l'ensemble, reprise possible après interruption.
