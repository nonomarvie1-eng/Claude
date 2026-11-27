# Phase 5 — Données historiques d'indices : sources légales et gratuites

Date : 2026-11-27. **Aucun achat, aucune inscription.** Hôtes ajoutés à l'environnement réseau pour lire les conditions et, si elles le permettent, télécharger : `stooq.com`, `mba.tuck.dartmouth.edu`, `fred.stlouisfed.org`.

## 1. Sources examinées

| Source | Contenu | Conditions | Accès depuis la session | Décision |
|---|---|---|---|---|
| **Kenneth R. French Data Library** (Tuck, Dartmouth) | Rendements journaliers du **marché américain** (Mkt−RF + RF, CRSP, toutes les actions NYSE/AMEX/NASDAQ pondérées par la capitalisation, dividendes inclus) depuis le **1926-07-01** ; marchés **développés, Europe, Japon, Asie-Pacifique hors Japon, Amérique du Nord** depuis le **1990-07** (en USD) | Bibliothèque publique de recherche, téléchargement libre sans inscription, mention « Copyright Kenneth R. French ». **Aucune licence formelle publiée.** Usage retenu : recherche personnelle, citation de la source, **aucune redistribution** des données (non versionnées). Les données dérivent de CRSP | Page lue (HTTP 200) | **Retenue** |
| Stooq | OHLC journaliers de SPY, ^SPX, ^NDX | Licence « non commerciale » selon un tiers ; **page des conditions non lisible** (connexion refusée par le site, deux essais) | Refusé | **Non utilisée** tant que les conditions ne sont pas lues |
| FRED (Fed de Saint-Louis) | SP500 (10 ans, © S&P), NASDAQ100 (depuis 1986, clôtures, © Nasdaq) | Usage personnel autorisé ; l'API interdit le stockage et l'archivage (résumé tiers) | Connexion refusée par le site (deux essais) | **Non utilisée** |
| Yahoo Finance | OHLC SPY depuis 1993 | Conditions défavorables à la collecte automatisée ; bibliothèques non officielles | — | **Exclue** |
| Alpha Vantage, Tiingo, Nasdaq Data Link | OHLC journaliers d'ETF | Clé gratuite : **inscription par vous** ; conditions à lire | — | Option (votre décision) |
| Historique du compte démo d'un courtier MT5 | CFD US500 ou US100 : **l'instrument même** que l'agent Cubrik traderait | Conditions du courtier ; compte à ouvrir par vous | — | **Meilleure option pour la validation de l'instrument** |

**Correctif de lien** : FRED ne publie pas le S&P 500 au-delà de 10 ans ; une étude depuis 1993 n'y est pas possible.

## 2. Ce que permettent (et ne permettent pas) les données French

| Possible | Impossible |
|---|---|
| Stratégies fondées sur les **clôtures** : SMA, RSI, plus bas ou plus haut des clôtures | Plus haut et plus bas journaliers : IBS, « plus haut de la veille », ATR, trois jours bas |
| Exécution à la clôture du signal (Connors) ou à la clôture suivante (retard d'une séance) | Exécution à l'ouverture suivante (pas de prix d'ouverture) |
| Stop vérifié **à la clôture** | Stop intrajournalier (le risque de gap entre deux clôtures est inclus, pas le chemin intrajournalier) |
| Indice de rendement total reconstruit (dividendes réinvestis) | Prix d'un ETF ou d'un CFD réellement négociable |
| Réplication sur 4 régions hors des États-Unis | Indices nationaux précis (Nifty, DAX…) |

## 3. Ne pas confondre les instruments

| | Marché CRSP (French) | ETF SPY | Indice S&P 500 au comptant | Future ES/MES | CFD US500 |
|---|---|---|---|---|---|
| Composition | ≈ 3 500 à 4 000 actions US (corrélation quotidienne avec le S&P 500 ≈ 0,99 [H]) | 500 actions | 500 actions | 500 actions | 500 actions |
| Dividendes | Inclus (rendement total) | Versés trimestriellement | Exclus (indice de prix) | Dans le prix (base) | Ajustement de dividende sur la position |
| Horaires de la bougie journalière | Clôture NYSE 16:00 NY | Clôture NYSE | Clôture NYSE | ≈ 23 h/24, clôture de règlement 16:00 | Journée du courtier (souvent 23:00 CET) |
| Financement | — | Aucun | — | Dans la base | **Financement de nuit pour les positions acheteuses** (≈ taux de référence + 2 à 3 %/an) |
| Taille minimale vs 1 000 € | — | 1 action ≈ 600 $ (fractions selon le courtier ; ETF US souvent inaccessible en UE, faute de document PRIIPs) | Non négociable | MES : 5 $/point ; un stop de 3 % ≈ 900 $ → **incompatible** | 0,1 à 1 $/point selon le courtier : **compatible** |
| Coût par aller-retour | — | Spread ≈ 0,01 % + commission | — | Commission + tick | Spread ≈ 0,4 à 1 point (≈ 0,01 à 0,02 %) + financement |

**Conséquence** : un résultat obtenu sur le marché CRSP est une **preuve sur le phénomène** (retour à la moyenne de l'indice actions américain), **pas sur l'instrument**. Le passage au CFD exige une seconde validation sur l'historique du CFD lui-même (compte démo), avec son financement et sa bougie journalière.

## 4. Modèle de coûts pré-enregistré (CFD indice, journalier)

- Écart et glissement : **0,03 % par côté** (≈ 1,5 point sur un S&P 500 à 5 000).
- Financement : position acheteuse, **(RF + 2,5 %/an) / 360 par nuit calendaire** (RF = taux sans risque quotidien French). Le week-end compte 3 nuits.
- Stress : coûts × 2, puis **0,20 % par côté**. Ce dernier niveau est proche du seuil d'annulation de l'avantage indiqué par le document indien (0,18 %).

## 5. Ce qu'il faudrait pour aller plus loin

1. **Votre compte Cubrik Demo** : `list_instruments` pour confirmer US500 et US100, et l'heure de la bougie D1.
2. **L'historique journalier d'un CFD US500** depuis un compte démo MT5 (export manuel par vous), si les conditions du courtier l'autorisent. Il permettrait de valider sur l'instrument exact, après autorisation d'ouvrir les périodes correspondantes.
3. **Une clé gratuite** (Alpha Vantage ou Tiingo) si vous souhaitez l'OHLC de SPY pour les variantes qui exigent plus haut et plus bas : inscription par vous ; je lirai d'abord leurs conditions.

*Source : Kenneth R. French Data Library, https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html (données CRSP). Les données ne sont ni versionnées ni redistribuées.*
