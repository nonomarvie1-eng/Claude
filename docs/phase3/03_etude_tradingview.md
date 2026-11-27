# Étude de faisabilité : connecter TradingView à Claude Code (avant la phase 4)

Date : 2026-11-27. Étude documentaire uniquement : **aucun abonnement souscrit, aucun compte connecté, aucune donnée TradingView téléchargée, aucun ordre.**

Méthode : recherche web sur les pages officielles de TradingView (documentation MCP, conditions d'utilisation, blog, centre d'aide) et sur des sources tierces signalées comme telles. L'hôte `www.tradingview.com` a été ajouté à l'environnement réseau pour lire les pages complètes, mais l'outil de lecture n'a toujours pas pu le joindre. Les citations ci-dessous viennent donc des **extraits des pages officielles renvoyés par la recherche**. Les points marqués **[à vérifier]** devront être confirmés sur la page en direct avant toute décision payante.

## 1. Conclusion

**TradingView ne résout pas notre problème de données de façon conforme.**

Ses conditions interdisent explicitement d'utiliser le serveur MCP officiel, ou tout autre moyen automatisé, pour collecter ou stocker des données de marché afin de constituer un jeu de données. Or c'est exactement ce dont notre moteur Python a besoin : des barres M1 stockées localement, rejouables et verrouillées par période.

TradingView peut au mieux servir de **backtesteur indépendant de contrôle**, via son serveur MCP officiel et la fonction `run_pine_backtest`, pour des stratégies déjà gelées. Cet usage a quatre limites :

- il coûte au minimum l'offre Premium pour le Deep Backtesting, soit environ 60 à 70 $ par mois ;
- les études événementielles avec contrôles et bootstrap, qui sont au cœur de notre protocole, n'y sont pas reproductibles ;
- le moteur d'exécution diffère du nôtre (section 6) ;
- les périodes verrouillées ne peuvent y être protégées que par une procédure, pas techniquement.

**Recommandation** : résoudre le problème de données par une source sous licence qui autorise le stockage local pour la recherche personnelle. La piste la moins chère identifiée est **Databento** :

- 125 $ de crédits offerts à l'inscription ;
- les données CME Globex couvrent **NQ, ES, et les futures de change 6E (EUR/USD) et 6B (GBP/USD)** ;
- conditions de licence et coût exact à vérifier avant tout engagement, votre autorisation étant requise.

TradingView reste une option facultative de contre-vérification.

## 2. Connecteurs MCP disponibles

| Connecteur | Nature | Fonctionnement | Conformité | Verdict |
|---|---|---|---|---|
| **Serveur MCP officiel TradingView** (`https://mcp.tradingview.com/mcp`) | Officiel, bêta publique, offres payantes (Essential ou plus), essais exclus | HTTP + OAuth 2.1 avec le compte TradingView ; outils dont `get_ohlcv` et les outils Pine (`run_pine_backtest`…) | Conforme **dans le cadre de la section 27** (usage personnel, réponse à une question précise, pas de constitution de base de données) | **Seule option acceptable** |
| tradesdontlie/tradingview-mcp, wezzcoetzee/tradingview-mcp | Communautaires | Pilotent TradingView Desktop via le Chrome DevTools Protocol (port de débogage 9222) | Automatisation de l'interface : contraire à « all our features are for manual use only » ; risque de bannissement du compte | **Rejeté** |
| ranjan98/tradingview-mcp, atilaahmettaner/tradingview-mcp | Communautaires | Points d'accès non documentés (screener, OHLCV, backtests) | Collecte automatisée hors canal officiel | **Rejeté** |
| daviddme/tradingview-indicator-search-mcp-server | Communautaire | Recherche de scripts publics et récupération du code Pine open source | Le code reste soumis à la licence de chaque auteur ; aucune donnée de marché | Inutile pour notre problème |
| pineforge-backtest-mcp | Tiers, hors ligne | Transpile Pine v6 en C++ et backteste localement sur des données Binance | N'utilise pas les données TradingView | Hors sujet : nous avons déjà notre moteur |

### Ce que disent les textes officiels sur le serveur MCP

- **Documentation MCP, outil `get_ohlcv`** :
  - au plus 5 000 barres par appel, 300 par défaut ;
  - l'historique intraday (1 min à 4 h) est « peu profond », et la documentation recommande le 1D ou le 1W pour les longues périodes ;
  - la profondeur et le délai suivent l'abonnement et les abonnements bourse de l'utilisateur.
- **Documentation MCP, usage des données** : ne pas utiliser le serveur pour « collect, scrape or store data for a database, dataset or data feed », et ne récupérer que ce qui est nécessaire pour répondre à la question posée.
- **Conditions d'utilisation, section 27 (fonctions d'IA, MCP)** :
  - interdit de redistribuer les données obtenues par MCP ;
  - interdit de les mettre en cache ou de les stocker systématiquement pour constituer un jeu de données ;
  - interdit d'en récupérer plus que nécessaire ;
  - seule exception : laisser un client d'IA que l'on utilise personnellement traiter les données pour répondre à ses propres demandes, avec un affichage lisible par un humain.
- **Blog TradingView** : usage personnel uniquement. Pas de partage, de revente ni de téléchargement en masse, pas d'entraînement de modèles, **pas de connexion à du trading automatisé ou à des robots**.
- **Conditions d'utilisation, section 3** : données de marché sous licence d'affichage uniquement (« display-only »).
- **Centre d'aide (bannissement pour activité suspecte)** : sont interdits « any automated data collection methods, including … scripts, APIs, screen scraping, data mining, robots ».
- **Fournisseurs de données** : leurs propres droits s'appliquent en plus (CME, ICE, FactSet…).

**Conséquence** : constituer notre historique M1 EUR/USD, GBP/USD, NQ et ES à partir de TradingView, par MCP, export CSV automatisé ou pont vers l'application de bureau, serait **non conforme**. Un export CSV manuel de graphique (offres Plus et supérieures [à vérifier]) reste soumis à la licence d'affichage uniquement. Je ne le recommande pas pour alimenter une base de recherche.

## 3. Limites par abonnement

Prix mensuels publiés en novembre 2026 (sources tierces concordantes) ; l'équivalent mensuel en paiement annuel est entre parenthèses.

| Offre | Prix mensuel $ (annuel) | Barres historiques par graphique | Deep Backtesting | Bar Magnifier | Appels MCP par jour inclus (depuis le 17/11/2026) | Replay 1 min |
|---|---|---|---|---|---|---|
| Basic (gratuit) | 0 | ≈ 5 000 [à vérifier] | Non | Non | **MCP indisponible** | — |
| Essential | 14,95 (12,95) | 10 000 | Non | Non | 10 | 6 mois |
| Plus | 34,95 (29,95) | 10 000 | Non | Non | 20 | 1 an |
| Premium | 69,95 (59,95) | 20 000 | **Oui** (jusqu'à 2 M de barres et 1 M de trades) | **Oui** | 50 | [à vérifier] |
| Ultimate | 239,95 (199,95) | 40 000 | Oui | Oui | 500 | [à vérifier] |

- **Abonnement IA** (AI Copilot et MCP) : porte la limite à 500 appels par jour et 50 par minute sur toute offre payante. Il ne débloque pas le Deep Backtesting, qui dépend de l'offre de base.
- **Chaque appel MCP compte** : une validation de script, une exécution ou un backtest valent chacun un appel.
- **Données CME** :
  - gratuites avec 10 minutes de retard. Ce retard est sans effet sur l'historique, mais la profondeur intraday disponible n'est pas documentée [à vérifier] ;
  - le temps réel est une option payante d'environ 7 à 10 $ par mois en non-professionnel, inutile pour du backtest.
- **Deep Backtesting** :
  - les résultats n'apparaissent que dans le rapport de stratégie, pas sur le graphique ;
  - en mode Deep, le détail de **tous** les trades est conservé ; en mode standard, seulement les 9 000 derniers ;
  - export de la liste des trades en CSV et du rapport en XLSX : offres requises [à vérifier].

**Offre minimale utile** : Premium, soit environ 60 $ par mois en annuel ou 70 $ en mensuel. Sans Deep Backtesting, 10 000 à 20 000 barres ne couvrent pas la période de développement 2020-01 → 2023-07 :

- en H1, il faut environ 21 000 barres FX ;
- en M5, environ 250 000 ;
- en M1, environ 1,3 million.

## 4. Historique EUR/USD, GBP/USD, NQ et ES depuis 2020

| Instrument | Sur TradingView | Profondeur M1 depuis 2020 | Remarque |
|---|---|---|---|
| EUR/USD, GBP/USD | Flux OANDA, FXCM, FX_IDC… gratuits | **Non documentée** ; la documentation MCP qualifie l'intraday de « peu profond » | Prix généralement *bid* ou moyens selon le flux : pas d'*ask*, donc spread à modéliser |
| NQ, ES (CME) | Continus `NQ1!` et `ES1!`, retard de 10 min gratuit | Non documentée [à vérifier] | Contrats continus : règle de roulement imposée par TradingView |

Même avec Premium et le Deep Backtesting, aucune source ne garantit des barres **M1** depuis 2020 pour ces symboles. La limite de 2 millions de barres est un plafond, pas une garantie de profondeur. Le seul moyen de vérifier serait de tester un compte Premium, ce qui n'est pas fait.

## 5. Conversion de nos stratégies en Pine Script v6

| Famille | Convertible ? | Commentaire |
|---|---|---|
| A, B, SBA (sessions intraday) | Oui | Fenêtres horaires avec `time(timeframe.period, "0930-1000", "America/New_York")` ; DST géré |
| C, F (TSMOM, Donchian), REF-SMA, D, E | Oui | Indicateurs standards ; swings confirmés à décaler de R barres pour rester causal |
| G (allocation multi-actifs) | **Non, en pratique** | `request.security` lit d'autres symboles, mais le simulateur Pine gère **un seul instrument par stratégie** : pas de portefeuille |
| NLI (études événementielles, contrôles décalés dans le temps, bootstrap par semaines, correction BH) | **Non** | Pas de tirage de contrôles appariés, de bootstrap ni de correction multiple dans un rapport de stratégie |
| Bases aléatoires appariées | Partiellement | Le générateur pseudo-aléatoire Pine existe, mais il faut une exécution par graine, et chaque exécution coûte un appel MCP |

Les règles de risque se traduisent directement :

- `strategy(..., initial_capital=1000, currency=currency.EUR, pyramiding=0)` ;
- `strategy.risk.max_intraday_loss(2, strategy.percent_of_equity)` ;
- `strategy.risk.max_drawdown(10, strategy.percent_of_equity)` ;
- stop obligatoire via `strategy.exit(stop=…)` ;
- taille calculée à la main pour un risque de 0,25, 0,5 ou 1 % ;
- frais par `commission_type=strategy.commission.percent` et `slippage` (en ticks).

## 6. Écarts d'exécution entre TradingView et NEXUS

| Aspect | NEXUS (Python) | TradingView (émulateur de courtier) |
|---|---|---|
| Données | M1 *bid/ask* séparés, en EUR via EUR/USDT H1 | Une seule série OHLC, généralement *bid* ou dernier prix ; pas de spread natif |
| Ordre au marché | Ouverture de la minute suivante | Ouverture de la barre suivante par défaut ; `process_orders_on_close=true` exécute à la clôture |
| Chemin intrabarre | Minute par minute ; si stop et objectif tombent dans la même minute, **stop d'abord** (conservateur) | Chemin supposé : ouverture → extrême le plus proche → autre extrême → clôture. Le Bar Magnifier (Premium) utilise un intervalle inférieur. Ce n'est pas « stop d'abord » |
| Ordre limite | Exécuté seulement si le prix dépasse la limite d'au moins un tick | Exécuté au simple contact par défaut ; l'option de vérification du prix des ordres limites (en ticks) doit être réglée pour s'en rapprocher |
| Gaps | Exécution au prix du gap | Ordres à prix déclenchés au prix d'ouverture du gap |
| Frais | 0,1 % Binance, spread et commission FX modélisés | Commission (%, par contrat ou par ordre) et glissement fixe en ticks |
| Valorisation | Au prix du marché, au taux du jour | Conversion de devise de TradingView, au taux de la veille [à vérifier] |
| Périodes | Verrou **technique** (`LockedPeriodError`, accès journalisés) | Aucun verrou : le graphique charge tout l'historique ; seul un filtre de dates dans le script protège |

Une même stratégie donnera des résultats différents entre les deux moteurs. Pour comparer, il faudrait d'abord calibrer les deux sur le même actif, par exemple BTC/USDT Binance, disponible des deux côtés, et documenter l'écart.

## 7. Préserver le protocole et les périodes verrouillées

Si TradingView est utilisé, voici les règles à appliquer :

1. **Pré-enregistrement inchangé** : TOML commité avant toute exécution. Le fichier Pine est versionné dans `pine/` et son SHA-256 est inscrit au registre.
2. **Filtre de dates codé en dur** dans le script : `inDev = time >= timestamp("UTC", 2020, 1, 1) and time < timestamp("UTC", 2023, 7, 1)`. Aucune entrée hors de cette fenêtre ; un filtre `date_from` est aussi passé à `run_pine_backtest`. Toute modification du filtre est une **ouverture de période** et exige votre autorisation, comme aujourd'hui.
3. **Pas de visualisation libre** de la période de validation sur le graphique pendant la recherche. Cette discipline ne peut pas être vérifiée techniquement : c'est la faiblesse majeure par rapport à notre verrou.
4. **Journalisation** de chaque exécution comme essai du registre, avec `purpose="cross-check"` s'il s'agit d'une contre-vérification d'une stratégie gelée, ou comme essai de sélection décompté du budget de la famille s'il s'agit d'une nouvelle variante. Les compteurs ne sont jamais réinitialisés.
5. **Conservation** : uniquement les métriques agrégées de nos propres stratégies (nombre de trades, espérance, profit factor, drawdown), le code Pine et son empreinte. **Ni barres ni liste de trades avec prix**, pour rester dans la section 27. Cette lecture prudente devrait être confirmée par TradingView si l'usage devenait régulier.
6. **Aucune alerte, aucun webhook, aucun courtier connecté** au compte TradingView.

## 8. Architecture recommandée

```
                ┌─────────────────────────────────────────────┐
                │ NEXUS (Python) — moteur de référence        │
                │ données locales sous licence → store.py     │
                │ verrous techniques, registre, budgets       │
                └───────────────┬─────────────────────────────┘
   données sous licence         │                 contre-vérification facultative
   ┌────────────────────────────┴──┐            ┌──────────────────────────────────┐
   │ Binance Vision (BTC, ETH)     │            │ TradingView MCP officiel         │
   │ Databento GLBX.MDP3 M1 :      │            │ run_pine_backtest, Premium,      │
   │  NQ, ES, 6E, 6B 2020→2026     │            │ stratégies gelées, métriques     │
   │  (125 $ de crédits ; licence  │            │ agrégées seulement, journalisées │
   │   à vérifier ; votre accord)  │            │ (votre accord, ≈ 60–70 $/mois)   │
   │ EUR/USD spot : accord écrit   │            └──────────────────────────────────┘
   │  Dukascopy (gratuit) en option│
   └───────────────────────────────┘
```

Pourquoi Databento plutôt que TradingView pour les données :

- c'est un fournisseur dont le métier est de vendre des données brutes, téléchargeables et stockables localement pour la recherche [licence à lire] ;
- les crédits offerts devraient couvrir des barres M1 sur 2020-2026 pour quatre contrats, le schéma OHLCV étant de loin le moins cher [coût exact à confirmer avec leur estimateur avant tout téléchargement] ;
- 6E et 6B sont des **futures** de change : sessions CME, base par rapport au spot, roulements trimestriels. C'est un bon substitut pour la recherche, mais pas un équivalent exact d'un CFD EUR/USD ; il faut le documenter comme transposition ;
- l'inscription exige une carte bancaire, même si rien n'est facturé tant que les crédits ne sont pas dépassés. Un plafond mensuel de dépense peut être fixé à 0 $.

## 9. Étapes de connexion du MCP officiel (si vous l'autorisez)

À faire **sur votre ordinateur**, dans Claude Code. L'authentification OAuth passe par votre navigateur.

1. **Décision d'abonnement**, par vous : Premium pour le Deep Backtesting. Essential (10 appels par jour, sans Deep Backtesting) ne suffit pas pour la période de développement.
2. Dans un terminal : `claude mcp add --transport http mcp-tradingview https://mcp.tradingview.com/mcp`
3. Dans Claude Code : `/mcp`, choisir `mcp-tradingview`, puis s'authentifier avec le compte TradingView dans le navigateur.
4. Demander la liste des outils, puis **n'autoriser que** les outils de lecture et les outils Pine de validation et de backtest. Refuser tout outil d'alerte, de liste de suivi modifiable ou de courtier s'il en apparaît, avec une règle `deny` dans `.claude/settings.json`.
5. Premier essai technique : la stratégie de référence REF-SMA sur `BINANCE:BTCUSDT` H4 en période de développement, comparée à notre moteur pour mesurer l'écart d'exécution. Un seul appel ; résultat journalisé en `technical`.
6. Depuis cette session cloud, il faudrait en plus autoriser l'hôte `mcp.tradingview.com`. Je ne l'ai pas demandé.

## 10. Décisions qui vous reviennent

1. **Données NQ, ES, 6E et 6B** : m'autoriser à lire la licence et l'estimateur de coût de Databento (hôte `databento.com`), sans inscription ni carte. Je vous rapporterai le coût exact et les conditions avant tout engagement.
2. **TradingView** : ne rien souscrire maintenant (ma recommandation), ou bien Premium pour la contre-vérification seulement.
3. **EUR/USD spot** : demande d'accord écrit à Dukascopy (gratuit, rédigée par moi, envoyée par vous), en complément ou à la place de 6E.

## Sources

- [TradingView MCP Server — documentation](https://www.tradingview.com/mcp/docs)
- [TradingView — Terms of Service and Company Policy](https://www.tradingview.com/policies/)
- [TradingView Blog — MCP public beta](https://www.tradingview.com/blog/en/tradingview-mcp-server-public-beta-60864/)
- [TradingView Blog — MCP Pine Script et limites quotidiennes](https://www.tradingview.com/blog/en/tradingview-mcp-pine-script-and-daily-limits-62532/)
- [TradingView News — MCP en bêta publique (Crypto Briefing)](https://www.tradingview.com/news/cryptobriefing:c81f3a880094b:0-tradingview-enables-ai-agent-connectivity-via-mcp-server-in-public-beta/)
- [TradingView News — Finance Magnates](https://www.tradingview.com/news/financemagnates:e657df0ab094b:0-tradingview-adds-mcp-as-retail-brokers-adopt-ai-trading-tools/)
- [Why is my account banned due to suspicious activity?](https://www.tradingview.com/support/solutions/43000674726-why-is-my-account-banned-due-to-suspicious-activity/)
- [How Deep Backtesting works](https://www.tradingview.com/support/solutions/43000666265-how-deep-backtesting-works/)
- [Why are the results of Deep Backtesting not shown on the chart?](https://www.tradingview.com/support/solutions/43000670566-why-are-the-results-of-deep-backtesting-not-shown-on-the-chart/)
- [How to export strategy data](https://www.tradingview.com/support/solutions/43000613680-how-to-export-strategy-data/)
- [How to export chart data](https://www.tradingview.com/support/solutions/43000537255-how-to-export-chart-data/)
- [How much data is available for Bar Replay?](https://www.tradingview.com/support/solutions/43000692816-how-much-data-is-available-for-bar-replay/)
- [Pine Script — Strategies](https://www.tradingview.com/pine-script-docs/concepts/strategies/)
- [Strategy properties](https://www.tradingview.com/support/solutions/43000628599-strategy-properties)
- [Bar magnifier](https://www.tradingview.com/blog/en/accurate-backtesting-with-bar-magnifier-31746)
- [CME Group — TradingView](https://www.cmegroup.com/solutions/market-tech-and-data-services/technology-vendor-services/tradingview.html)
- [QuantVPS — TradingView pricing 2026](https://www.quantvps.com/blog/tradingview-pricing) (tiers)
- [GitHub — tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp), [wezzcoetzee/tradingview-mcp](https://github.com/wezzcoetzee/tradingview-mcp), [ranjan98/tradingview-mcp](https://github.com/ranjan98/tradingview-mcp), [atilaahmettaner/tradingview-mcp](https://github.com/atilaahmettaner/tradingview-mcp), [daviddme/tradingview-indicator-search-mcp-server](https://github.com/daviddme/tradingview-indicator-search-mcp-server), [pineforge-backtest-mcp](https://github.com/pineforge-4pass/pineforge-backtest-mcp)
- [Databento — usage-based pricing and data credits](https://databento.com/docs/knowledge-base/new-users/usage-based-pricing-and-data-credits), [Databento — futures](https://databento.com/futures)
