# Phase 8 — Compatibilité Cubrik des règles de portefeuille

Sources :

- format officiel des règles de backtest et guides d'agent du dépôt `target1m/cubrik-mcp` (lus en phase 4) ;
- tarifs et FAQ de cubrik.ai.

Statuts : **V** vérifié dans la documentation ; **✗** absent ; **?** à vérifier dans votre compte Demo.

**Distinction essentielle** :

- le **moteur de backtest** Cubrik est déterministe, mais calcule **un symbole à la fois** ;
- l'**agent** est une IA qui suit une instruction textuelle ; il peut recevoir des consignes de portefeuille, mais **rien ne garantit qu'il les applique exactement**, et elles ne sont pas backtestables.

| Question | Constat | Statut | Reproductibilité |
|---|---|---|---|
| Un agent peut-il surveiller 10 cryptomonnaies ? | Le guide de création d'agent demande « Markets — which instruments (BTC, EUR/USD, gold, **a list**) » : une liste est prévue | V (liste) ; nombre maximal ? | Consigne textuelle |
| Peut-il gérer plusieurs positions simultanées ? | Les limites d'un agent incluent `max_positions_per_instrument` : par instrument, donc plusieurs instruments possibles en même temps | V (par instrument) | Le backtest, lui, traite chaque symbole séparément |
| Peut-il plafonner le risque cumulé (1 %) et le nombre de positions (2) du portefeuille ? | Aucun paramètre de portefeuille documenté (seulement `max_daily_loss_pct` et `max_positions_per_instrument`) | ✗ en paramètre ; seulement par consigne | **Non reproductible** en backtest ; à mesurer en démo |
| Peut-il éviter des entrées simultanées sur des actifs corrélés ? | Aucun opérande inter-actifs | ✗ | Consigne textuelle uniquement |
| Peut-il suspendre les entrées après une perte journalière ? | `max_daily_loss_pct` par agent | V (paramètre d'agent) | Comportement exact (fermeture ou suspension ?) **?** |
| Fréquence réelle de contrôle en Demo | Non publiée (Beginner : 60 min) | ? | — |
| Sorties conditionnelles | `exit.signal` (jusqu'à 4 conditions, OU) dans le backtest | V | Oui en backtest ; exécution par l'IA en réel |
| Stop et vente à découvert | `stopLossPct`, `side: both`, perpétuels `XXX/USDT:USDT` | V | Oui |
| VWAP | Opérande `vwap` | V ; **ancrage (00:00 UTC ?) : ?** | À vérifier |
| ADX, Bollinger, RSI, EMA, `highest`/`lowest` | Opérandes listés | V | Oui (sous réserve de la définition de `highest`) |
| Nombre d'agents actifs | Demo : 1 ; Beginner : 2 ; Intermediate : 5 | V | — |

## Conséquences

1. **Résultats théoriques et reproductibles.** Nos simulations de portefeuille (2 positions maximum, 1 % de risque cumulé, blocage après −2 % dans la journée, priorité fixe entre actifs) sont **théoriques** : aucune de ces règles ne s'exprime dans le backtest Cubrik. Elles pourraient être confiées à l'agent par consigne, sans garantie.
2. **Ce qui est reproductible** : les règles **mono-actif** (entrée, sortie, stop) et `max_daily_loss_pct` par agent. Les résultats **mono-actif** (critère C6) sont donc les plus proches de ce que Cubrik peut réellement backtester.
3. **Alternative mono-actif** : un seul agent sur BTC/USDT:USDT, l'actif le plus liquide. Sa fréquence est mesurée dans les résultats : colonne « mono-actif ».
4. **Les limites de risque ne sont pas des garanties.** Un stop au marché peut être exécuté au-delà de son niveau (gap, glissement), et la perte journalière peut dépasser 2 % avant que la règle n'agisse, surtout avec un contrôle toutes les 60 minutes.

## À vérifier dans Cubrik Demo (en plus de `docs/phase6/08` §4)

1. Le nombre maximal d'instruments dans la liste d'un agent.
2. Le comportement de `max_daily_loss_pct` : suspension des entrées ou fermeture des positions ?
3. La fréquence de contrôle de l'offre Demo (affichée dans `get_account` ou dans l'écran de l'agent).
4. L'ancrage horaire du `vwap`.
5. La disponibilité des perpétuels (`BTC/USDT:USDT`…) selon le courtier démo connecté, et leurs frais.
