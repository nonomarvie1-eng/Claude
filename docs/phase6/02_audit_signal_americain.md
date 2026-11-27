# Phase 6 — Audit du signal américain (RSI 30/50 + stop, figé en phase 5)

Configuration figée, **non modifiée** :

- entrée : RSI(5) < 30 et clôture > SMA 200 ;
- sortie : RSI(5) croise au-dessus de 50 ;
- stop catastrophe de 6 %, vérifié à la clôture ;
- exécution à la clôture.

**Reproduction exacte (D0)** : 88 trades identiques à la phase 5, +0,616 % par trade sur 2010-01 → 2023-06.

## 1. Stabilité temporelle (D5)

| Période | Trades | Rendement net moyen | Gagnants | Entrées aléatoires : p |
|---|---|---|---|---|
| 1930-1939 | 53 | +0,30 % | 71,7 % | 0,33 |
| 1940-1949 | 65 | −0,31 % | 63,1 % | 0,98 |
| 1950-1959 | 60 | −0,26 % | 53,3 % | 0,99 |
| 1960-1969 | 50 | **−1,00 %** | 54,0 % | 1,00 |
| 1970-1979 | 46 | **−0,94 %** | 43,5 % | 1,00 |
| 1980-1989 | 64 | −0,15 % | 67,2 % | 0,85 |
| 1990-1999 | 72 | +0,42 % | 77,8 % | 0,08 |
| 2000-2009 | 48 | **+0,62 %** | 77,1 % | **0,013** |
| 2010-2019 | 66 | **+0,50 %** | — | **0,011** |
| 2020-2023 S1 | 22 | +0,96 % | — | 0,03 |
| **1928-1992** | 371 | **−0,38 %** | — | 1,00 |
| **1993-2009** | 102 | **+0,61 %** | — | **0,002** |
| **2010-2023 S1** | 88 | **+0,62 %** | — | **0,001** |

**Lecture** :

- Pendant **cinq décennies (1940-1989)**, acheter les replis de l'indice américain a été **perdant**. Les années 1960-70 étaient même un régime de **momentum** à court terme : les baisses se prolongeaient.
- L'avantage apparaît dans les années 1990 et reste stable et significatif depuis 2000.
- C'est un **changement de régime documenté** : l'autocorrélation journalière de l'indice, positive avant les années 1990, est devenue négative ensuite [H].
- Deux conséquences pour la décision :
  1. l'avantage peut **disparaître** comme il est apparu ;
  2. il n'existe que depuis environ 30 ans, ce qui reste une période longue.

## 2. Transfert vers SPY, S&P 500, Nasdaq 100, QQQ, US500

- **Aucune source légale et automatisable** n'a été trouvée pour ces séries (`03_sources_donnees.md`). Je n'ai donc **pas** pu vérifier le transfert.
- Le marché CRSP French (toutes les actions US) a une corrélation quotidienne d'environ 0,99 avec le S&P 500 [H] ; le transfert vers SPY est **plausible mais non démontré**.
- Le **Nasdaq 100** est plus volatil, plus concentré et plus tourné vers la technologie. C'est un **autre marché**, qu'il faudrait tester séparément.
- **CFD US500** :
  - sa bougie journalière clôture à l'heure du courtier, pas à 16:00 New York ;
  - le financement de nuit et l'ajustement de dividende s'ajoutent.
  - Ces différences touchent directement un signal sur 5 jours.

## 3. Le stop (D4)

| Stop | Trades | Sorties sur stop | Dépassement au-delà du stop | Pire clôture |
|---|---|---|---|---|
| 6 % | 88 | 5 | 0,06 à 2,2 point | −8,2 % |

Les 5 sorties sur stop se sont faites entre −6,1 % et −8,2 %. C'est le **risque de gap** d'un stop vérifié à la clôture : un stop réel se déclencherait plus tôt dans la séance, mais aussi plus souvent.

## 4. Verdict de l'audit

- Le signal est **réel et significatif sur 1993-2023**, mais **dépendant du régime de marché** : perdant sur 1940-1989.
- Le transfert vers un instrument négociable **n'est pas démontré**.
- La stratégie reste au stade **prometteur** ; elle ne devient pas candidate.
