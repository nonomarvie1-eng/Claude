# Phase 6 — Résultats de développement : dimensionnement

Source : `results/batch_6_01_confirmation/sizing.json`. Capital : 1 000 €, effet de change ignoré.

## Japon — RSI 2 + stop 11 % (1991-07 → 2023-06, 184 trades, environ 5,8 par an)

| Profil | Notionnel | Final | CAGR | Max DD | Sharpe | Calmar | Expo. moy. / max | Pire trade (% capital) | Pire jour | Frais € | Financement € | MC : CAGR médian (5e pct) | MC : DD 95e pct | P(DD > 10/15/20/25 %) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Risque 0,25 % | 2,3 % | 1 020 € | +0,06 % | 0,3 % | 0,42 | 0,18 | 0,2 / 2,3 % | −0,15 % | −0,20 % | 2,5 | 2,7 | +0,06 (+0,03) | 0,5 % | 0 / 0 / 0 / 0 |
| Risque 0,5 % | 4,5 % | 1 040 € | +0,12 % | 0,7 % | 0,42 | 0,18 | 0,4 / 4,7 % | −0,31 % | −0,39 % | 5,1 | 5,5 | +0,12 (+0,06) | 1,1 % | 0 / 0 / 0 / 0 |
| Risque 1 % | 9,1 % | 1 081 € | +0,24 % | 1,4 % | 0,42 | 0,18 | 0,7 / 9,3 % | −0,61 % | −0,78 % | 10,4 | 11,2 | +0,24 (+0,12) | 2,1 % | 0 / 0 / 0 / 0 |
| Risque 2 % | 18,2 % | 1 167 € | +0,48 % | 2,7 % | 0,42 | 0,18 | 1,4 / 18,6 % | −1,22 % | −1,56 % | 21,4 | 22,9 | +0,49 (+0,24) | 4,2 % | 0 / 0 / 0 / 0 |
| Expo. 10 % | 10 % | 1 089 € | +0,27 % | 1,5 % | 0,42 | 0,18 | 0,8 / 10,2 % | −0,67 % | −0,86 % | 11,5 | 12,3 | +0,27 (+0,13) | 2,3 % | 0 / 0 / 0 / 0 |
| Expo. 25 % | 25 % | 1 236 € | +0,67 % | 3,7 % | 0,42 | 0,18 | 2,0 / 25,5 % | −1,68 % | −2,15 % | 30,1 | 32,0 | +0,67 (+0,32) | 5,8 % | 0,06 % / 0 / 0 / 0 |
| Expo. 50 % | 50 % | 1 522 € | +1,32 % | 7,3 % | 0,42 | 0,18 | 3,9 / 50,7 % | −3,36 % | −4,30 % | 65,7 | 68,5 | +1,33 (+0,63) | 11,4 % | 10,2 % / 0,8 % / 0,04 % / 0 |
| Expo. 100 % | 100 % | 2 274 € | +2,60 % | 14,4 % | 0,42 | 0,18 | 7,9 / 100,4 % | −6,73 % | −8,60 % | 157,0 | 157,7 | +2,62 (+1,20) | 21,9 % | 79,2 % / 30,9 % / 8,7 % / 2,0 % |

## US — RSI 30/50 + stop 6 % (2010-01 → 2023-06, 88 trades, environ 6,5 par an)

| Profil | Notionnel | Final | CAGR | Max DD | Sharpe | Calmar | Expo. moy. / max | Pire trade (% capital) | Pire jour | Frais € | Financement € | MC : CAGR médian (5e pct) | MC : DD 95e pct | P(DD > 10/15/20/25 %) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Risque 0,25 % | 4,2 % | 1 023 € | +0,17 % | 0,7 % | 0,60 | 0,23 | 0,5 / 4,3 % | −0,35 % | −0,20 % | 2,2 | 2,2 | +0,17 (+0,06) | 1,0 % | 0 / 0 / 0 / 0 |
| Risque 0,5 % | 8,3 % | 1 046 € | +0,33 % | 1,5 % | 0,60 | 0,23 | 1,0 / 8,5 % | −0,69 % | −0,41 % | 4,5 | 4,4 | +0,34 (+0,12) | 2,1 % | 0 / 0 / 0 / 0 |
| Risque 1 % | 16,7 % | 1 094 € | +0,67 % | 2,9 % | 0,60 | 0,23 | 2,0 / 17,0 % | −1,39 % | −0,82 % | 9,3 | 9,0 | +0,68 (+0,24) | 4,1 % | 0 / 0 / 0 / 0 |
| Risque 2 % | 33,3 % | 1 195 € | +1,33 % | 5,8 % | 0,60 | 0,23 | 4,0 / 33,9 % | −2,78 % | −1,65 % | 19,4 | 18,9 | +1,35 (+0,47) | 8,1 % | 1,4 % / 0,05 % / 0 / 0 |
| Expo. 10 % | 10 % | 1 055 € | +0,40 % | 1,8 % | 0,60 | 0,23 | 1,2 / 10,2 % | −0,83 % | −0,49 % | 5,5 | 5,3 | +0,41 (+0,15) | 2,5 % | 0 / 0 / 0 / 0 |
| Expo. 25 % | 25 % | 1 143 € | +1,00 % | 4,4 % | 0,60 | 0,23 | 3,0 / 25,5 % | −2,08 % | −1,23 % | 14,2 | 13,8 | +1,01 (+0,35) | 6,1 % | 0,2 % / 0 / 0 / 0 |
| Expo. 50 % | 50 % | 1 304 € | +1,99 % | 8,7 % | 0,60 | 0,23 | 5,9 / 50,7 % | −4,16 % | −2,49 % | 30,6 | 29,8 | +2,02 (+0,68) | 12,0 % | 12,3 % / 1,3 % / 0,1 % / 0 |
| Expo. 100 % | 100 % | 1 680 € | +3,92 % | 16,9 % | 0,61 | 0,23 | 11,9 / 100,3 % | −8,33 % | −5,07 % | 70,6 | 69,5 | +3,99 (+1,26) | 23,1 % | 66,7 % / 31,5 % / 11,0 % / 3,1 % |

## Lecture

1. **Le Sharpe (0,42 au Japon, 0,60 aux US) et le Calmar (0,18 et 0,23) ne dépendent pas du dimensionnement.** Le dimensionnement n'améliore pas la stratégie : il choisit un point sur une même droite rendement-risque.
2. **Le risque de gap est réel** :
   - pire trade : −6,7 % (Japon) et −8,3 % (US) du notionnel ;
   - à 100 % d'exposition, un seul trade coûte 6,7 à 8,3 % du capital, et la pire journée −8,6 %.
   - Le stop catastrophe ne protège pas d'un gap d'ouverture.
3. **Le plafond économique est bas.** Même investies à 100 % à chaque signal, sans levier, ces stratégies rapportent **2,6 %/an** (Japon) et **3,9 %/an** (US), avec 67 à 79 % de probabilité simulée de dépasser 10 % de drawdown.
4. **Utilisation du capital** :
   - Japon investi **7,9 %** des jours, US **12,6 %** (`08_compatibilite_strategies.md` §3) ;
   - c'est la cause du faible rendement : environ 6 trades de 4 à 6 jours par an et par stratégie.
