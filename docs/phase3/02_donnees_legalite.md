# Phase 3 — Données, légalité et instruments

| Besoin des documents | Instrument visé | Source légale et gratuite disponible | Statut |
|---|---|---|---|
| ICT (Silver Bullet, NWOG, One Trade Setup, Mentorship, SMT, Unicorn) | Futures CME NQ/ES (et micros MNQ/MES) | Aucune identifiée. Fournisseurs payants (Databento, etc.) : non engagés sans votre accord | **Bloqué** (coût) |
| SMT ES/NQ | Deux indices synchronisés | Idem | **Bloqué** ; analogue testé : BTC/ETH (Binance Vision) |
| ORB (document testé sur le S&P 500) | Indice cash / ETF / future | Idem | Analogue testé : « opening range » 09:30 NY sur BTC |
| Forex (Market Maker Models, Silver Bullet) | EUR/USD, GBP/USD | Dukascopy : outils automatisés et bases de données interdits sans accord écrit (phase 2D). Taux BCE : journaliers seulement | **Bloqué** (juridique) |
| Order Flow Imbalance | BTC Binance (trades, L2) | Binance Vision : klines avec **volume acheteur taker réel**, trades agrégés. Pas de carnet L2 historique spot | Faisabilité testée à la minute |
| Arbitrage statistique | Paires d'actions | Analogue BTC/ETH | Diagnostic de cointégration effectué |

## Ne pas confondre les instruments

| | Future (NQ, MNQ) | CFD Nasdaq 100 | ETF (QQQ, ou équivalent UCITS) | Indice cash (NDX) |
|---|---|---|---|---|
| Négociable | Oui (CME) | Oui (courtier) | Oui (bourse) | **Non** (calcul seulement) |
| Horaires | ≈ 23 h/24, 5 j/7, avec une pause quotidienne | Selon le courtier (≈ 23 h/24) | Heures de bourse (RTH 9 h 30–16 h NY) | RTH |
| Gap du dimanche (NWOG) | Oui | Oui | Non (gap du lundi 9 h 30) | — |
| Taille minimale vs 1 000 € | MNQ ≈ 2 $/point : 3,7 à 7,4 % de risque par trade → **incompatible** | 0,1 $/point : compatible | Fractions d'actions selon le courtier ; les ETF domiciliés aux États-Unis ne sont généralement pas accessibles aux particuliers de l'UE (documents PRIIPs), les équivalents UCITS le sont | — |
| Vente à découvert | Oui | Oui | Limitée | — |
| Échéances | Roulement trimestriel (H, M, U, Z) à gérer | Ajustements du courtier | — | — |

## Calendriers

Pour les indices, il faudra gérer les jours fériés et les séances écourtées (par exemple le lendemain de Labor Day, cité par ICT), les roulements de contrats et la distinction RTH/ETH. Une bibliothèque open source de calendriers de marché pourra être ajoutée le jour où des données d'indices seront disponibles. BTC n'a ni jours fériés, ni RTH, ni gap de week-end : la NWOG et l'opening range gap y sont **inapplicables**.

## EUR/USD

Toujours bloqué. Les options restent celles de la phase 2D :

- accord écrit de Dukascopy ;
- lecture des conditions de HistData, avec votre autorisation pour l'hôte ;
- historique d'un compte de démonstration d'un courtier.
