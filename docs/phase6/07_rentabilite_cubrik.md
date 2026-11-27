# Phase 6 — Rentabilité économique de Cubrik pour 1 000 €

Tarifs : cubrik.ai/en/pricing (phase 4, novembre 2026). Les rendements des stratégies sont **déjà nets** des frais de trading, des spreads (0,03 % par côté) et du financement de nuit.

## 1. Coûts fixes rapportés au capital

| Offre | Prix | Coût annuel | En % de 1 000 € | Ce qu'elle apporte pour nous |
|---|---|---|---|---|
| **Demo** | 0 € | 0 € | **0 %** | 1 agent actif, 1 connexion de courtier, 125 crédits IA par mois ; backtest et serveur MCP : non ou à vérifier |
| Beginner | 19 €/mois | 228 € | **22,8 %/an** | 2 agents, contrôle horaire, backtest sur 12 mois |
| Intermediate | 59 €/mois | 708 € | **70,8 %/an** | 5 agents, contrôle toutes les 30 min, backtest sur 5 ans, serveur MCP |
| Pro | 199 €/mois | 2 388 € | 238,8 %/an | — |

Coûts de données : 0 € si l'historique vient d'un compte démo MT5.

## 2. Rendement nécessaire contre rendement disponible

| Stratégie et profil | Rendement net annuel (développement) | Couvre Demo ? | Couvre Beginner (22,8 %) ? | Capital minimum pour couvrir Beginner |
|---|---|---|---|---|
| US RSI 30/50, risque 0,5 % | 0,33 % (≈ 3 €/an) | Oui | Non | ≈ 69 000 € |
| US RSI 30/50, risque 2 % | 1,33 % (≈ 13 €/an) | Oui | Non | ≈ 17 000 € |
| US RSI 30/50, exposition 100 % | 3,92 % (≈ 39 €/an) | Oui | Non | ≈ 5 800 € |
| Japon RSI 2, exposition 100 % | 2,60 % (≈ 26 €/an) | Oui | Non | ≈ 8 800 € |
| Les deux, exposition 100 % chacune (≈ 18 % des jours investis) | ≈ 6 à 6,5 % (≈ 65 €/an), si aucun chevauchement | Oui | Non | ≈ 3 600 € |

**Conclusion économique** :

- **Toute offre payante rend ces stratégies perdantes avec 1 000 €.**
- Seule l'offre **Demo** (gratuite) est compatible. Elle est limitée à **un agent actif**, mais un agent peut recevoir une instruction portant sur plusieurs marchés (à vérifier).
- Sans le serveur MCP (offre Intermediate), je ne peux pas piloter Cubrik moi-même : les manipulations se font dans l'application, par vous.

## 3. Autres coûts à vérifier (courtier, non Cubrik)

- **Spread CFD** réel :
  - US500 : environ 0,4 à 1 point, soit environ 0,01 à 0,02 % ;
  - JP225 : environ 7 à 10 points, soit environ 0,02 à 0,03 % [H].
  - Notre hypothèse de 0,03 % par côté est prudente.
- **Financement de nuit** : environ (taux de référence + 2,5 %)/an sur les positions acheteuses. En JPY, le taux de référence est proche de 0 : le financement du JP225 serait **plus faible** que celui modélisé (RF américain).
- **Taille minimale** de position CFD : elle doit permettre 45 à 85 € de notionnel au profil 0,5 % ; sinon la taille correcte est zéro.
- **Conversion de devise** du P&L (USD ou JPY vers EUR) et éventuels frais d'inactivité.

**Recommandation** : aucun abonnement. Si un agent est un jour justifié, ce sera sur l'offre **Demo**, d'abord connectée à un **compte démo** de courtier.
