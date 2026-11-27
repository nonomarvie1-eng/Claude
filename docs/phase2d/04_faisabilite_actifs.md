# Phase 2D — Étude de faisabilité des marchés supplémentaires

Aucune recherche n'a été lancée sur ces marchés. Les chiffres de frais, de spreads et de tailles sont des ordres de grandeur courants pour un compte de détail européen et **doivent être vérifiés** chez le fournisseur retenu. Objectif : **vérifier la reproductibilité** des mécanismes déjà définis, sans choisir les actifs sur leurs résultats.

| Marché | Données gratuites légalement utilisables | Conditions d'utilisation | Frais et spread réalistes | Taille min. et compatibilité 1 000 € | Horaires | Vente à découvert | Réglementation |
|---|---|---|---|---|---|---|---|
| **EUR/USD** | M1 bid/ask : Dukascopy **bloqué** (pas d'outil automatisé ni de base de données sans accord écrit). Journalier : **taux de référence BCE**, réutilisation gratuite avec citation de la source et données non modifiées (politique BCE, à confirmer dans le texte intégral) | Dukascopy : voir `01_conditions_utilisation.md` ; BCE : citation obligatoire | Spread ≈ 0,1–1 pip + commission ≈ 0,7 pip aller-retour (ECN) | 0,01 lot = 1 000 € de nominal ; risque minimal ≈ 0,1–0,2 % pour 10–20 pips : **compatible** | 24 h/24, 5 j/7 ; rollover vers 23 h Paris ; DST Europe/États-Unis | Oui (CFD/compte Forex) | ESMA : levier max 30:1 (majeures), protection contre le solde négatif |
| **GBP/USD** | Mêmes sources. Journalier BCE : croisé EUR/USD ÷ EUR/GBP (dérivé, à mentionner) | Idem | Spread un peu plus large qu'EUR/USD | Compatible | Idem | Oui | 30:1 |
| **USD/JPY** | Mêmes sources. Journalier BCE : croisé EUR/JPY ÷ EUR/USD | Idem | Proche d'EUR/USD | Compatible | Idem ; Tokyo sans DST | Oui | 30:1 |
| **XAU/USD** | Intraday : même blocage Dukascopy. Journalier : pas de source officielle gratuite identifiée (les prix de référence LBMA sont sous licence, à vérifier) | À identifier | Spread ≈ 0,2–0,5 $ | 0,01 lot = 1 oz ; stop de 10 $ ≈ 0,9 % du capital : **limité** au profil dynamique | ≈ 23 h/24, 5 j/7, pause quotidienne | Oui (CFD) | ESMA : 20:1 |
| **ETH/USDT** | **Binance Vision** (mêmes archives et mêmes conditions que BTC : §4.1 recherche personnelle autorisée, §4.2 trading réel exclu) | Lues (même document que BTC) | Taker 0,10 % + spread faible | Notionnel min ≈ 5 USDT : **compatible** | 24 h/24, 7 j/7 | **Non en spot** | Cadre MiCA (UE) pour les prestataires crypto |
| **NASDAQ 100** | Pas de source officielle gratuite d'intraday identifiée. Agrégateurs journaliers (Stooq, Yahoo) sans conditions de réutilisation claires | À clarifier | CFD : spread ≈ 1–2 points | CFD 0,1 $/pt : compatible ; future micro MNQ (2 $/pt) : **incompatible** (3,7–7,4 % de risque par trade) | Cash 15:30–22:00 Paris ; CFD quasi 23 h/24 | Oui (CFD) | ESMA : 20:1 (indices majeurs) |
| **DAX 40** | Même situation | À clarifier | CFD : spread ≈ 1–2 points | CFD 0,1 €/pt : compatible ; micro-future FDXS : marge vraisemblablement > capital | Xetra 09:00–17:30 Paris | Oui (CFD) | ESMA : 20:1 |

## Conclusions de faisabilité

1. **ETH/USDT** est le seul marché supplémentaire immédiatement exploitable avec des données de qualité et des conditions lues. C'est le candidat naturel pour vérifier la reproductibilité des mécanismes G et F. Limite : ETH est fortement corrélé à BTC, donc ce ne serait pas une diversification indépendante.
2. **EUR/USD intraday** reste bloqué. Le lot 2B-01 pré-enregistré, intraday M5, exige des données bid/ask M1 qu'aucune source conforme ne fournit pour l'instant.
3. **EUR/USD journalier (BCE)** permettrait de tester des mécanismes **journaliers** (momentum, allocation), mais **pas** le lot intraday pré-enregistré. Ce serait une nouvelle hypothèse à pré-enregistrer, pas une substitution.
4. **Indices et or** : sans source gratuite et conforme, ils ne sont pas faisables sans dépense. Aucune dépense n'est engagée.
