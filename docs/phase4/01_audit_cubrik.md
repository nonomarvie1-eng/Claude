# Phase 4 — Audit de la plateforme Cubrik

Date : 2026-11-27. **Aucun compte créé ni connecté, aucun abonnement, aucun backtest lancé sur Cubrik.**

Sources, par ordre de fiabilité :

1. **Dépôt public officiel du serveur MCP** de Cubrik, [`target1m/cubrik-mcp`](https://github.com/target1m/cubrik-mcp) (commit `6582752`, 21/11/2026), lu intégralement. Il contient le README et les guides des outils, dont le **format exact des règles de backtest** (`skills/cubrik-backtesting/references/rules.md`). L'éditeur l'a écrit pour décrire ce que ses outils acceptent ; c'est la source la plus précise disponible.
2. **Pages de cubrik.ai** (tarifs, FAQ, conditions, à propos), lues à travers les extraits de recherche web : le site ne répond pas à l'outil de lecture de cette session.
3. **Sources tierces** (MoonX, annuaires MCP), signalées comme telles.

Légende : **[V]** vérifié dans une source officielle ; **[?]** non documenté publiquement, à vérifier avec votre compte (liste en §9).

## 1. Nature de la plateforme

- Cubrik exécute des **« agents » : une instruction en langage naturel suivie par une IA**, sur un calendrier, sur les comptes de courtier ou d'exchange que vous connectez. Cubrik ne détient pas les fonds et n'est pas un courtier [V].
- **Le contrôle des conditions est du code, l'IA n'intervient que lorsqu'une condition se déclenche** (FAQ) [V]. L'ordre est donc passé par une IA qui interprète l'instruction : c'est une source de divergence avec le backtest, qui, lui, est déterministe (§6).
- Éditeur : Next Step L.L.C-FZ (Dubaï). Société américaine : Cubrik Inc. (Delaware, lancement commercial au 3e trimestre 2026). La plateforme est **jeune**.
- Il n'existe **pas de mode simulation interne** : la FAQ recommande de connecter le **compte démo de votre courtier** [V]. Un essai à blanc existe aussi : `test_agent` lit le marché et dit ce que l'agent aurait fait, sans rien placer (20 par jour, gratuit) [V].

## 2. Marchés et instruments

| Élément | Constat |
|---|---|
| Plateformes connectables [V] | OKX, Bybit, Coinbase, Kraken, Bitget, Binance, Hyperliquid, MetaTrader 4/5, Interactive Brokers, Robinhood, eToro, TradingView, Polymarket, MoonX (les listes de la FAQ et de la page d'accueil diffèrent légèrement) |
| Classes d'actifs [V] | Crypto au comptant et perpétuels (notation `BTC/USDT` et `BTC/USDT:USDT`), forex, indices, matières premières (FAQ) |
| Liste exacte des symboles [?] | Outil `list_instruments`, accessible seulement depuis un compte |
| Vente à découvert [V] | `side: "short"` ou `"both"` dans les règles ; en pratique, sur perpétuels ou CFD. Au comptant sans marge, le short n'est pas possible chez le courtier |
| Levier [V] | `risk.leverage` ; `marginMode` isolé ou croisé, à votre choix |

## 3. Création d'agents et règles de stratégie

Format des règles de backtest [V, `rules.md`] :

| Élément | Possibilités |
|---|---|
| Unités de temps | `1m`, `5m`, `15m`, `1h`, `4h`, `1D` |
| Symboles | jusqu'à **8 par backtest**, mais **un calcul indépendant par symbole** : pas de portefeuille, pas de condition inter-actifs |
| Sens | `long`, `short`, `both` ; **une seule position à la fois** |
| Entrée | jusqu'à **6 conditions, toutes requises (ET)** ; `within: n` pour une séquence (condition vraie dans les n dernières bougies) |
| Opérateurs | comparaisons et croisements (`crossesAbove`, `crossesBelow`…) |
| Opérandes | `price`, `const`, `sma`, `ema`, `rsi`, `atr`, `macd`, `bollinger`, `keltner`, `stochastic`, `adx` (+DI/−DI), `cci`, `mfi`, `roc`, `vwap`, `ichimoku`, `psar`, `supertrend`, `highest`, `lowest`, `volume`, `volumeAvg`, `obv`, ainsi que `swingHigh`, `swingLow`, `orderBlock`, `fvg`, `structure` |
| Stop | `stopLossPct` : **pourcentage fixe depuis l'entrée** (pas de stop en ATR) |
| Objectif | `takeProfitPct` : pourcentage fixe, ou `null` |
| Sortie temporelle | `maxBarsInTrade` |
| Sortie sur signal | jusqu'à 4 conditions, **une seule suffit (OU)** |
| Gestion de position | paliers `management` (`at` → `action`, par exemple déplacer le stop au seuil de rentabilité), en % du prix ou du ROI sur marge |
| Taille | `risk.perTradePct` ; un montant fixe est aussi possible |
| Achats réguliers | `accumulate` (DCA) |
| Historique | `months` de 1 à 60, **toujours jusqu'à aujourd'hui** : aucun paramètre de date de début ou de fin n'est documenté |

**Limites qui comptent pour notre recherche :**

- **Aucun opérande d'heure, de jour ou de session.** Les stratégies de session (ORB, Silver Bullet, killzones, ouverture de New York) ne sont pas exprimables dans le backtest ; un agent pourrait seulement recevoir la consigne en texte, sans test possible.
- **Aucun opérande inter-actifs** : force relative, SMT, spread ou rotation entre actifs sont impossibles.
- **Stop en % fixe** : un stop en ATR doit être converti en un % figé par actif.
- **Historique** : la minute est limitée aux 90 derniers jours ; **forex, métaux et indices commencent à l'unité H1** [V].
- **Données de backtest** : « historical market data », source non nommée [?]. La notation `BTC/USDT:USDT` suggère des bougies d'exchange crypto.

## 4. Moteur de backtest

| Élément | Constat |
|---|---|
| Coût | Un backtest ne consomme **aucun crédit** [V] |
| Profondeur | **12 mois** (Beginner) ; **5 ans, « fees and slippage included »** (Intermediate et plus) [V] ; Demo [?] |
| Résultats [V] | Rendement, drawdown maximal, taux de réussite, nombre de trades, profit factor, détail mensuel comparé au marché (`pricePct`), courbe de capital ; un champ `methodology` liste les hypothèses (frais, exécutions, ce qui n'est pas simulé) |
| Valeurs des frais et du glissement | **[?]**, non publiées |
| Modèle d'exécution | **[?]** : ouverture de la bougie suivante, clôture, ordre stop/objectif dans une même bougie |
| Capital par défaut | 10 000 ; `starting_balance` est réglable [V] |
| Échecs possibles [V] | `timeframe_unavailable`, `no_candles`, `not_enough_history`, `too_many_backtests` |
| Bibliothèque [V] | Agents prêts à l'emploi, backtestés sur 12 mois et retestés chaque semaine ; un « Jev score » résume ces backtests (descriptif) |

**Conséquence critique pour le protocole** : un backtest Cubrik couvre toujours les *n* derniers mois jusqu'à aujourd'hui. Il recouvre donc nos périodes verrouillées : la **validation** (2023-07 → 2024-12) et le **test final** (2025-01 → 2026-06).

- **Tout backtest Cubrik d'une stratégie candidate revient à ouvrir ces périodes.** Il ne doit être lancé qu'avec votre autorisation, au moment prévu pour la validation.
- Seule exception sans risque : les mois **postérieurs au 2026-07-01**, qui n'appartiennent à aucune période réservée. Un backtest de 1 à 4 mois s'y limite et peut servir à comparer les moteurs, de préférence sur une règle de référence qui n'est pas candidate (§8).

## 5. Abonnements (cubrik.ai/en/pricing, novembre 2026)

| Offre | Prix mensuel | Crédits IA par mois | Agents actifs | Fréquence de contrôle | Backtest | Serveur MCP |
|---|---|---|---|---|---|---|
| Demo | gratuit, sans carte ni limite de durée | 125 (modèles DeepSeek) | 1 | [?] | [?] | Non |
| Beginner | 19 € | 4 000 | 2 | 1 h | 12 mois | Non |
| **Intermediate** | **59 €** | [?] | 5 | 30 min | **5 ans, frais et glissement inclus** | **Oui** |
| Pro | 199 € | [?] | 15 | 15 min | 5 ans | Oui |
| Max | 399 € | 80 000 | 50 | 5 min | 5 ans | Oui |

- Crédits supplémentaires : 1 000 pour 5 €, sans expiration.
- Pas de commission sur les trades.
- Résiliation en fin de période payée, sans remboursement au prorata.

## 6. Écarts attendus entre le moteur NEXUS et Cubrik

1. **Données** : nous utilisons Binance Vision au comptant ; Cubrik utilise des bougies d'exchange de source non précisée. Écart faible en crypto (même exchange possible), inconnu ailleurs.
2. **Exécution du backtest** : hypothèses inconnues (§4). Notre simulateur suppose une entrée à l'ouverture de la bougie suivante, le **stop avant l'objectif** dans une même bougie, et le prix du gap.
3. **Frais et glissement** : inconnus chez Cubrik. Nous utilisons 0,10 % de frais et 0,05 % de glissement par côté au comptant, et nous testons le double.
4. **Live et backtest chez Cubrik** : l'agent en réel est une IA qui suit une instruction textuelle, avec contrôle toutes les 30 à 60 minutes. Des erreurs d'interprétation, de taille ou de délai sont possibles, et seule une phase sur compte démo les mesurera.
5. **Portefeuille** : Cubrik calcule chaque symbole séparément, alors que nos résultats agrègent plusieurs agents sur un capital commun. La somme des backtests Cubrik par symbole ne reproduit pas exactement le partage du capital.
6. **Arrêts globaux** (2 % par jour, 10 % de drawdown) : Cubrik propose `max_daily_loss_pct` **par agent** [V], pas de limite globale de drawdown documentée [?]. `pause_all_agents` existe, mais c'est une action manuelle.

## 7. Conditions d'utilisation et sécurité

- Cubrik ne donne pas de conseil en investissement. Les performances passées, backtests compris, ne préjugent pas de l'avenir [V].
- Clés d'API **sans droit de retrait** ; MetaTrader par identifiants chiffrés [V].
- Les droits du serveur MCP se choisissent à la connexion : lecture, gestion des agents, trading [V].
- `start_agent` et `run_agent_now` passent de **vrais ordres**. **Je ne les appellerai jamais** ; si le connecteur est installé un jour, seule la portée `cubrik.read` (et au besoin `cubrik.agents` pour créer des agents en pause) devrait être accordée, sans `cubrik.trade`.
- Rappel : les données Binance Vision restent réservées à la recherche personnelle (§4.2 de leurs conditions : trading réel exclu). Cubrik, lui, utilise ses propres données.

## 8. Ce que Cubrik change pour NEXUS

| Avant | Maintenant |
|---|---|
| Bot autonome à construire | **Supprimé** : pas d'exécution, de courtier, de déploiement ni de surveillance (consigne respectée : aucun de ces éléments n'est développé) |
| Toute stratégie testable en Python | Seules les stratégies **exprimables avec les opérandes Cubrik** (§3) sont retenues |
| Sessions intraday, ICT temporel, SMT, arbitrage de paires | **Incompatibles** (aucun opérande horaire ni inter-actifs) |
| Allocation dynamique G (poids continu) | Compatible **seulement sous forme de règle d'entrée et de sortie** (par exemple prix au-dessus de la SMA 100 en D1), avec une taille fixe par trade |
| Données NQ/ES/FX à acheter | **Inutile pour l'instant** : forex, indices et métaux ne sont disponibles chez Cubrik qu'à partir de H1, et leur source et leur profondeur sont inconnues. **Aucun achat avant d'avoir vérifié `list_instruments`** (consigne : ne pas dépenser pour un marché inexploitable) |

## 9. À récupérer depuis votre compte (gratuit, offre Demo)

Sans rien connecter à un courtier et sans démarrer d'agent :

1. **La liste des instruments** : l'application, ou le texte de l'outil `list_instruments`. Je cherche notamment s'il y a des perpétuels crypto, EUR/USD, GBP/USD, l'or, NAS100 et US500, et quelle profondeur pour chacun.
2. **Le backtest est-il possible en Demo, et sur combien de mois ?**
3. **Le texte « methodology » d'un backtest neutre**, pour éviter d'ouvrir une période réservée sur une stratégie candidate : par exemple un achat régulier (DCA) hebdomadaire de BTC/USDT sur **1 mois**. Je cherche les frais, le glissement, le prix d'exécution, l'ordre stop/objectif et le fuseau des bougies D1.
4. **La signification de `perTradePct`** : % du capital risqué jusqu'au stop, ou % du capital engagé ?
5. **L'opérande `highest(N)` inclut-il la bougie courante ?** Sinon, « prix croise au-dessus de `highest(50)` » est impossible. Le schéma JSON de `run_backtest` le précise.
6. **Les fréquences de contrôle possibles en Demo**, et si un agent D1 agit juste après la clôture de la bougie (00:00 UTC ?).

## Sources

[Dépôt cubrik-mcp](https://github.com/target1m/cubrik-mcp) · [cubrik.ai](https://cubrik.ai/en) · [Tarifs](https://cubrik.ai/en/pricing) · [FAQ](https://cubrik.ai/fr/faq) · [Conditions](https://cubrik.ai/en/legal/terms) · [À propos](https://cubrik.ai/en/about) · [Remboursements](https://cubrik.ai/en/legal/refunds) · [Confidentialité](https://cubrik.ai/fr/legal/privacy) · [Google Play](https://play.google.com/store/apps/details?id=ai.cubrik.app) · [App Store](https://apps.apple.com/us/app/cubrik-ai-crypto-agent/id6811330637) · [Communiqué Cubrik Inc.](https://www.streetinsider.com/Press+Releases/Cubrik+Inc.+Incorporates+in+Delaware+as+Demand+for+Agentic+Trading+Software+Accelerates/27231899.html) · [MoonX : qu'est-ce que Cubrik](https://moon-x.io/fr/blog/quest-ce-que-cubrik) · [Annuaire mcpservers.org](https://mcpservers.org/servers/cubrik-ai-en-mcp) · [Glama](https://glama.ai/mcp/servers/target1m/cubrik-mcp)
