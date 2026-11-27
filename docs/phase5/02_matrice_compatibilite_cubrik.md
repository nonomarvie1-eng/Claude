# Phase 5 — Matrice de compatibilité Cubrik

Source des capacités de Cubrik : `skills/cubrik-backtesting/references/rules.md` du dépôt officiel [`target1m/cubrik-mcp`](https://github.com/target1m/cubrik-mcp), commit `6582752` (voir `docs/phase4/01_audit_cubrik.md`).

Légende :

- **V** : capacité vérifiée dans ce texte ;
- **?** : non documentée, à vérifier dans le schéma JSON de `run_backtest`, accessible depuis votre compte ;
- **✗** : absente du format documenté.

## 1. Capacités utiles (rappel)

| Capacité | Statut |
|---|---|
| Opérandes `price`, `sma`, `ema`, `rsi`, `bollinger` (lignes), `stochastic`, `atr`, `highest`, `lowest`, `roc`, `adx`… | V |
| Période quelconque d'un opérande (RSI 2, RSI 5, SMA 200…) | ? Le schéma « décrit les périodes » sans les lister |
| `highest`/`lowest` : sur le plus haut et le plus bas, ou sur la clôture ? bougie courante incluse ? | ? |
| Comparer un indicateur à **sa propre valeur des jours précédents** (décalage) | ✗ (seule la séquence `within: n` existe) |
| Calculs entre opérandes (par exemple %B = (clôture − basse) / (haute − basse)) | ✗ |
| `maxBarsInTrade` (sortie temporelle) | V |
| `stopLossPct: null` (pas de stop) | V |
| Paliers `management` avec action `lock` (protection des gains) | V |
| Vente partielle | ✗ non documentée |
| Opérande horaire ou de session | ✗ |
| Instruments indices et CFD (US500, US100…) | ? `list_instruments` ; « forex, métaux et indices à partir de H1 » V |
| Bougie D1 d'un CFD d'indice | ? Le plus souvent la journée du courtier (≈ 23 h/24), **différente** de la séance au comptant de SPY [H] |
| Exécution de l'agent réel | Contrôle toutes les 30 à 60 minutes selon l'offre ; ordre passé par une IA qui suit l'instruction V |

## 2. Stratégies

| Stratégie | Règle d'origine | Fonction Cubrik | Compatibilité | Adaptation | Impact potentiel |
|---|---|---|---|---|---|
| RSI 2 (Connors) | Clôture > SMA 200 ; RSI(2) < 10 ; sortie clôture > SMA 5 ; pas de stop | `price > sma(200)` ET `rsi(2) < 10` ; sortie `price crossesAbove sma(5)` | **V**, si la période 2 est acceptée (?) | (a) Exécution après la clôture de la bougie D1 du CFD (≈ clôture) ; (b) **stop catastrophe** en % fixe : variante pré-enregistrée | Bougie CFD ≠ séance au comptant : signaux légèrement différents. Le stop coupe les rares pertes extrêmes, mais aussi certains rebonds |
| RSI 30/50 | Clôture > SMA 200 ; RSI(5) < 30 ; sortie RSI(5) croise au-dessus de 50 | `rsi(5) < 30` ET `price > sma(200)` ; sortie `rsi(5) crossesAbove 50` | **V** (forme la plus native) | Idem (a) et (b) | Idem |
| Double 5 | Clôture > SMA 200 ; clôture au plus bas des 5 jours ; sortie à la clôture au plus haut des 5 jours | `price <= lowest(5)` ; sortie `price >= highest(5)` | **?** Selon la définition de `lowest`/`highest` (plus bas ou clôture, bougie courante incluse ou non) | Si `lowest` porte sur les plus bas : « clôture ≤ plus bas des 5 bougies » est **plus strict** que « clôture la plus basse des 5 » | Moins de trades ; à mesurer si l'opérande est confirmé |
| R3 | RSI(2) en baisse 3 jours de suite et < 20 ; sortie RSI(2) > 70 | Nécessite RSI(t) < RSI(t−1) < RSI(t−2) | **✗** (aucun décalage) | Aucune sans hypothèse forte | **Exclue** |
| %B 3 jours | %B(5, 2) < 0,2 trois jours de suite | Nécessite un calcul et un décalage | **✗** | Approximation « clôture < bande basse » : c'est une autre stratégie | **Exclue** |
| Jours de baisse | Clôture < SMA 5, 4 baisses sur 5 jours | Comptage de jours | **✗** | — | **Exclue** |
| Trois jours bas | Plus haut et plus bas en baisse 3 jours de suite ; sortie non précisée | Décalage, sortie inconnue | **✗** | — | **Exclue** |
| Plus bas de 5 jours (SPY) | Achat sur plus bas de 5 jours ; sortie clôture > plus haut de la veille ou 5 jours | `price <= lowest(5)` ; sortie `price > highest(1)` (?) ; `maxBarsInTrade: 5` | ? | — | Non testée : le plus haut journalier est **absent de nos données** (document 03) |
| IBS | (C − L) / (H − L) | `stochastic` de période 1 ≈ IBS (?) | ? | — | Non testée (données) |
| Williams %R | — | Proche de `stochastic` | ? | — | Non testée |
| Gestion de l'exposition, tendance (essai autorisé) | P4-01 + protection progressive | Paliers `management` (`unit: price`, `lock`) | **V** | Paliers fixés a priori (protocole) | Moins de gains rendus ; gros gagnants peut-être écourtés |
| Kullamägi : vente d'1/3 à 1/2 après 3 à 5 jours, stop au point mort | Vente partielle + stop au point mort | Vente partielle ✗ ; stop au point mort ≈ `lock` à +0 % ? | Partielle | Seul le `lock` est testé | La vente partielle reste non testée |

## 3. Conséquences

1. **Trois stratégies de retour à la moyenne sont exprimables** dans le format documenté : RSI 2, RSI 30/50 et, sous réserve, Double 5. Toutes les autres Connors exigent des décalages ou des calculs absents.
2. **Avant tout agent**, il faudra vérifier dans votre compte (offre Demo) :
   - l'existence d'un CFD S&P 500 ou Nasdaq 100 dans `list_instruments` ;
   - les périodes acceptées pour `rsi` ;
   - la définition de `lowest`/`highest` ;
   - l'heure de clôture de la bougie D1 de ce CFD.
3. Un **backtest Cubrik** de ces stratégies couvrirait les 5 dernières années, donc nos périodes verrouillées : il n'est pas lancé sans votre autorisation.
