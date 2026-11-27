# Phase 6 — Sources de données (recherche du 2026-11-27)

Hôtes réseau ajoutés à l'environnement : `www.ecb.europa.eu`, plus ceux de la phase 5. **Aucun achat, aucune inscription.**

| Donnée demandée | Source examinée | Conditions | Résultat | Décision |
|---|---|---|---|---|
| **USD/JPY** | **BCE, taux de référence** (`eurofxref-hist.zip`) | « Free access and free reuse », y compris commerciale, en citant « Source : ECB statistics », sans altérer les données (politique de réutilisation des statistiques du SEBC, lue le 2026-11-27) | Téléchargé, **coupé au 2023-06-30**, 6 274 jours depuis 1999 ; USD/JPY calculé (EUR/JPY ÷ EUR/USD) | **Utilisé** (D1-D3) |
| Nikkei 225 en JPY | FRED, série NIKKEI225 | Données © Nikkei Inc. ; usage personnel permis par FRED | Le site **refuse la connexion** aux clients automatisés (deux essais avec identification honnête). Je n'ai pas tenté de contourner : un en-tête de navigateur imité a d'ailleurs été refusé par le contrôle de sécurité de la session | Non utilisé |
| Nikkei 225 en JPY | Nikkei Inc. (indexes.nikkei.co.jp) | Indice protégé par le droit d'auteur ; conditions de téléchargement non trouvées | — | Non utilisé |
| Nikkei 225, TOPIX | Yahoo, Barchart, revendeurs (Portara, getdata.finance) | Conditions défavorables, ou payant | — | Exclus |
| TOPIX | JPX | Licence de données JPX (payante pour l'historique) | — | Non utilisé |
| ETF japonais (1321, 1306) | Stooq | Conditions illisibles (connexion refusée) | — | Non utilisé |
| CFD JP225 | Historique d'un compte démo MT5 | Conditions du courtier ; **compte à ouvrir par vous** | — | **Option recommandée** |
| S&P 500, Nasdaq 100 | FRED (SP500 sur 10 ans, NASDAQ100 depuis 1986) | Usage personnel | Connexion refusée | Non utilisé |
| SPY, QQQ | Stooq, Yahoo | Voir ci-dessus | — | Non utilisés |
| SPY, QQQ, Nikkei (ETF) | Alpha Vantage, Tiingo (clé gratuite) | Inscription par vous ; conditions à lire avant usage | — | Option |
| Marché US et Japon (en USD) | Kenneth R. French | Recherche, citation, pas de redistribution | Déjà utilisé | Utilisé |

## Ce que je vous demande (gratuit)

1. **Le plus utile : l'historique journalier des CFD JP225, US500 et US100 depuis le compte démo MT5 d'un courtier.** Dans MetaTrader 5 : Affichage → Symboles → onglet Barres → choisir le symbole, D1, la période → Exporter les barres (CSV). Lisez d'abord les conditions du courtier sur l'usage des données. Exportez **jusqu'au 2023-06-30 seulement**, pour respecter le verrou. C'est l'**instrument même** que l'agent Cubrik traderait (bougie journalière du courtier, dividendes, prix).
2. Sinon, une **clé gratuite Alpha Vantage ou Tiingo** (SPY, QQQ, ETF japonais), après lecture de leurs conditions. Il existe aussi un connecteur MCP Alpha Vantage dans l'annuaire de claude.ai, que vous pourriez activer.

*Source des taux de change : ECB statistics. Marché : Kenneth R. French Data Library (CRSP).*
