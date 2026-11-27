# Phase 7 — Compatibilité Cubrik

Source : format des règles de `run_backtest`, dépôt officiel `target1m/cubrik-mcp` (commit `6582752`), lu en phase 4. **Le moteur de backtest n'est pas l'agent IA** : l'agent peut lire une consigne textuelle quelconque (par exemple « le lundi »), mais **seules les règles du backtest sont vérifiables et reproductibles**. Je ne classe compatible que ce que le backtest exprime.

Statuts : **V** vérifié dans la documentation ; **✗** absent du format documenté ; **?** non documenté.

## 1. Capacités vérifiées pour cette phase

| Capacité | Statut |
|---|---|
| Unités de temps `1m 5m 15m 1h 4h 1D` ; forex, métaux et indices à partir de `1h` | V |
| `bollinger` (lignes haute, basse, médiane), `rsi`, `adx` (+DI, −DI), `atr`, `stochastic`, `highest`, `lowest` | V |
| **Williams %R** | **✗ : absent de la liste des opérandes** |
| **IBS** | **✗ : aucun opérande**, aucun calcul entre opérandes |
| `stochastic` de période 1 **sans lissage** (= 100 × IBS) | ? (période et lissage du %K non documentés) |
| Plusieurs unités de temps dans une même règle (RSI H4 avec un signal H1) | **✗** : une seule `timeframe` par backtest |
| Stop en ATR (dynamique) | **✗** : `stopLossPct` fixe seulement |
| Stop suiveur | Partiel : paliers `management` → `lock` (V), pas de suiveur continu |
| Sortie sur condition d'indicateur (OU) | V (≤ 4 conditions) |
| Jour de la semaine ou heure | **✗** |
| Plus haut de la veille (`highest(1)`) | ? (bougie courante incluse ou non) |
| Moyenne d'un indicateur sur 2 jours | **✗** |
| Taille : `risk.perTradePct` | V (sens exact : ?) |
| Fréquence de contrôle de l'agent | V : 60 min (Demo ou Beginner) |

## 2. Classement des stratégies

| Stratégie | Classe | Raison | Adaptation possible | Impact |
|---|---|---|---|---|
| **IBS QQQ** (IBS < 0,1 ; > 0,9) | **D** | IBS absent ; équivalent `stochastic(1)` **non vérifié** (lissage par défaut ?) ; instrument NAS100 à confirmer | `stochastic(1) < 10` pour entrer, `stochastic(1) > 90` pour sortir, si le %K de période 1 est accepté **sans lissage** | Identique mathématiquement, à données OHLC égales. Sur un CFD, la bougie journalière n'est pas la séance de QQQ : IBS différent |
| **RSI 3 + IBS SPY** | **D** | Idem, plus la sortie « clôture > plus haut de la veille » (`highest(1)` ?) | `rsi(3) < 30` ET `stochastic(1) < 20` ; sortie `stochastic(1) > 90` OU `price > highest(1)` | Idem |
| IBS XLP (moyenne sur 2 jours) | **C** | Moyenne d'un indicateur non exprimable ; XLP non négociable en CFD courant [H] | Aucune sans changer la règle | — |
| Williams %R GBP/USD M30 | **C** | M30 interdit pour le forex ; filtre horaire et sortie en fin de séance impossibles ; filtre de la veille non défini | Version H1 : nouvelle hypothèse, pas une reproduction | Inconnu ; aucune donnée forex disponible |
| Freqtrade crypto (BB H1 + RSI H4 + ADX H1/H4) | **B** | Plusieurs unités de temps et stop ATR impossibles | Tout en **H4** (une seule unité) ; stop en % fixe par actif = 4,5 × ATR médian mesuré avant la période (méthode de la phase 4) | Signal moins réactif, stop fixe au lieu d'adaptatif : **nouvelle hypothèse** |
| Taille par ATR | **B** | Taille dynamique non documentée ; `perTradePct` seulement | Possible côté agent IA (consigne textuelle), **non vérifiable** en backtest | — |
| Turnaround Tuesday | **C** | Jour de la semaine | — | Exclu |
| Lundi Nikkei | **C** | Jour et heure ; de plus, ce n'est pas une stratégie | — | Exclu |
| Or Fibonacci (cassure de la veille) | **C** | Ordres stop en attente sur le plus haut et le plus bas de la veille, stop et objectif en % du **range de la veille** (non fixe), heure d'annulation | — | Exclu (et non prioritaire) |

## 3. Ce qu'il faut vérifier dans Cubrik Demo (en plus de la phase 6, `docs/phase6/08` §4)

1. Le module de règles propose-t-il **Williams %R** ? Avec quelles périodes ?
2. **Stochastique** :
   - période du %K = 1 acceptée ?
   - lissage (« slowing ») réglable à 1 ?
   - texte d'aide : quel calcul exact ?
3. Opérande « plus haut de la veille » : `highest(1)` inclut-il la bougie courante ?
4. Instrument **NAS100** (US Tech 100) et son heure de clôture journalière.
5. Stop exprimable en **ATR**, ou seulement en % ?

Ne lancez aucun backtest de ces règles : il couvrirait nos périodes verrouillées.
