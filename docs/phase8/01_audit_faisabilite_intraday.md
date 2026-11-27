# Phase 8 — Audit de faisabilité du day trading quantitatif

Date : 2026-11-27. **Aucun backtest de stratégie, aucun essai ajouté au registre** (194 essais conservés).

- Les mesures ci-dessous sont **descriptives** et portent sur la période de développement (2020-01 → 2023-06).
- La phase 7, lancée sur les stratégies journalières, est **suspendue** : code commité, aucune hypothèse exécutée.

## 1. L'objectif de 5 % par jour, en chiffres

| Hypothèse | Calcul | Conséquence |
|---|---|---|
| 5 % par jour, composé | 1,05²⁵⁰ ≈ **206 000** | 1 000 € deviendraient environ 206 millions d'euros en un an. Aucun fonds, aucun teneur de marché ne publie rien d'approchant. |
| 5 % par jour, 3 trades par jour, risque de 2 % par trade | 5 % / 3 ≈ 1,67 % par trade, soit **+0,83 R net par trade** en moyenne | Il faudrait, par exemple, 70 % de gagnants à +1,5 R et 30 % de perdants à −1 R, **après frais**, sur des centaines de trades. |
| Même objectif, risque de 0,5 % par trade | **+3,3 R net par trade** | Hors de portée de toute méthode documentée. |
| Ce que nous avons mesuré en intraday (phases 2 et 3, BTC M5) | Espérance brute de −0,1 à +0,1 R ; coûts d'environ 0,15 R par trade | Aucune espérance nette positive démontrée. |

**Conclusion arithmétique** : 5 % par jour **n'est pas un objectif de recherche réaliste**, quel que soit le profil de risque sans levier. Je ne le fixerai pas comme critère. Je rapporterai la part des journées à +5 % comme vous le demandez, sans la rechercher.

## 2. Les coûts face aux mouvements intrajournaliers (mesures descriptives, BTC et ETH, 2020-2023 S1)

Amplitude médiane d'une bougie (ATR14, en % du prix) et coût d'un aller-retour exprimé en ATR. Avec un stop à 1 ATR, ce coût équivaut directement à **une fraction du risque R**.

| Unité | ATR médian BTC | ATR médian ETH | Coût au comptant (0,10 % × 2 + glissement ≈ 0,30 %) | Coût en perpétuel (0,05 % × 2 + glissement ≈ 0,15 %) |
|---|---|---|---|---|
| M5 | 0,23 % | 0,30 % | **1,0 à 1,3 R** | 0,5 à 0,6 R |
| M15 | 0,43 % | 0,55 % | 0,55 à 0,70 R | 0,27 à 0,35 R |
| M30 | 0,62 % | 0,79 % | 0,38 à 0,48 R | 0,19 à 0,24 R |
| H1 | 0,90 % | 1,15 % | 0,26 à 0,33 R | **0,13 à 0,17 R** |

**Lecture** :

- **Le scalping en M5 au comptant est impossible** : le coût dépasse le risque d'un trade.
- En perpétuel, M15 coûte environ 0,3 R par trade. Il faudrait une espérance **brute** supérieure à 0,3 R : nous n'avons jamais mesuré plus de 0,1 R en intraday.
- **H1 en perpétuel** est l'unité la plus défendable : coût d'environ 0,15 R.
- Avec 1 à 3 trades par jour (250 à 750 trades par an), les frais coûtent environ 37 à 112 R par an. À 0,5 % de risque par trade, cela représente **environ 19 à 56 % du capital par an**, à couvrir par l'espérance brute avant tout gain.

## 3. Cubrik et le day trading (documentation vérifiée en phase 4)

| Point | Constat | Conséquence |
|---|---|---|
| Fréquence de contrôle de l'agent | Beginner : **60 min** ; Intermediate : 30 min ; Pro : 15 min ; Max : 5 min ; Demo : non publiée | Une stratégie M5 exige l'offre **Max** ; une stratégie M15 exige au minimum **Pro** |
| Coût de ces offres pour 1 000 € | Pro : 199 €/mois ≈ **19,9 % du capital par mois**. Max : 399 €/mois ≈ **39,9 % par mois** | **Rédhibitoire** : la stratégie devrait gagner environ 1 à 2 % par jour de bourse rien que pour payer la plateforme |
| Exécution | Le contrôle des conditions est du code, mais l'ordre est passé par une **IA** qui interprète l'instruction | Latence, risque d'interprétation ; **non mesurables sans compte démo** |
| Backtest Cubrik | Crypto : 1m (90 derniers jours), 5m, 15m, 1h, 4h, 1D. **Forex, or et indices : à partir de 1h seulement** | XAU/USD, EUR/USD, GBP/USD, NAS100, US500 et JP225 **ne peuvent pas être backtestés en M5, M15 ou M30 dans Cubrik** |
| Heure ou session | **Aucun opérande** | ORB, killzones, sessions, sortie en fin de journée : **impossibles** dans les règles |
| Limiter le nombre de trades par jour | Non documenté dans les règles ; seul `max_daily_loss_pct` existe par agent | Le plafond de 3 trades par jour serait une consigne textuelle à l'IA, non vérifiable en backtest |
| Stop et objectif | % fixe depuis l'entrée ; paliers `lock` | Pas de stop en ATR dynamique ; un stop en % convient à une unité et un actif donnés |
| Vente à découvert | `side: short` ou `both` | Seulement sur perpétuel ou CFD, avec levier possible chez le courtier |
| Taille minimale | Binance perpétuels : environ 5 USDT de notionnel minimum (100 USDT pour BTC) [à vérifier] | Compatible avec 1 000 € : 0,5 % de risque à 1 % de stop ≈ 500 € de notionnel |

**Verdict de compatibilité** :

- **M5 et M15 : incompatibles économiquement avec 1 000 €.** Il faudrait les offres Pro ou Max, qui coûtent 20 à 40 % du capital par mois ; l'offre Beginner contrôle toutes les heures, ce qui ne permet pas de suivre une bougie de 5 ou 15 minutes.
- **H1 : la seule unité intrajournalière compatible** avec Demo ou Beginner, et seulement sur **crypto** pour le backtest.
- **Le forex, l'or et les indices ne sont backtestables dans Cubrik qu'à partir de H1** ; de plus, nous n'avons **pas de données légales** pour eux.
- 1 à 3 trades par jour en H1 restent possibles en surveillant **plusieurs actifs** avec un ou deux agents.

## 4. Données disponibles

| Marché | Intraday disponible | Statut |
|---|---|---|
| BTC, ETH (Binance Vision) | M1 depuis 2020 (développement), donc M5, M15 et H1 reconstruits | **Disponible** |
| Autres cryptos liquides | H1 pour 10 actifs (phase 4) ; M1 téléchargeable gratuitement | Disponible ou téléchargeable |
| Perpétuels (financement) | Taux de financement 2020-2023 pour les 10 actifs | **Disponible** |
| XAU/USD, EUR/USD, GBP/USD | Aucune source légale (Dukascopy bloqué sans accord écrit) | **Indisponible** : export MT5 démo à faire par vous |
| NAS100, US500, JP225 | Aucune | **Indisponible** : idem |

## 5. Ce que nos recherches intrajournalières ont déjà montré (à ne pas répéter)

| Phase | Essais | Résultat |
|---|---|---|
| 2 (A, B, SBA) | Sessions et cassures de structure, BTC M5 | Rejetées : **coûts ≈ 0,15 R par trade**, espérance nette négative |
| 2C (C, E) | Structure et retour à la moyenne en H1/H4, BTC | Rejetées |
| 3 (NLI) | 14 études d'événements M5/H1 (FVG, swings, killzones, ORB, SMT) | 13 nulles ; ORB +5,7 points de probabilité, **sous le seuil de rentabilité** et non répliqué sur ETH |
| 3 (OFI) | Déséquilibre d'ordres à la minute | Prédictif à la seconde seulement, **non rentable après frais** |

**Erreurs à ne pas répéter** :

- choisir des niveaux et des sessions après coup ;
- ignorer les coûts en R ;
- prendre un taux de réussite pour un avantage ;
- tester sur un seul actif sans réplication.

## 6. Profils de risque (simulation seulement)

Profils prévus : 0,25 %, 0,5 %, 1 % et 2 % par trade. Ils ne changent **pas** la qualité du signal (phase 6) : ils multiplient rendement et drawdown ensemble.

**Exemple de ruine** : à 2 % par trade, avec 45 % de gagnants, la probabilité d'au moins une série de 10 pertes consécutives sur 750 trades (environ un an à 3 trades par jour) est d’environ **57 %** (simulation de 5 000 tirages). Une telle série coûte environ 18 % du capital.

**Le levier** sera analysé à part, comme un simple multiplicateur, et ne sera jamais recommandé.
