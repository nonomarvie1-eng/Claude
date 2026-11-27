# NEXUS QUANT — Rapport de phase 5 : retour à la moyenne sur indices et gestion de l'exposition

Date : 2026-11-27. **Période de développement seulement** (rien après le 2023-06-30). Validation et test final verrouillés : 0 accès. Aucun compte Cubrik, aucun agent, aucun achat, aucun ordre.

Détails :

- `01_audit_7_documents.md` à `05_preregistration.md` ;
- résultats générés : `06_resultats_backtests.md`, `07_robustesse_monte_carlo.md`.

*Données : Kenneth R. French Data Library (dérivées de CRSP), usage de recherche, non redistribuées ; Binance Vision (CC BY-NC-SA 4.0) pour H5-EXP.*

## 1. Conclusion

1. **Une stratégie franchit tous les critères pré-enregistrés de la phase de recherche : RSI 2 de Connors avec stop catastrophe, sur le marché japonais.**
   - Rendement net moyen : +0,47 % par trade [IC95 +0,18 ; +0,73], sur 184 trades de 1991 à 2023 S1.
   - Elle bat les entrées aléatoires appariées : p corrigé 0,005.
   - Elle est positive sur les 3 sous-périodes, résiste aux coûts doublés et au retard d'une séance, et 94 % de sa grille de paramètres est positive.
   - Monte Carlo : le 5e percentile du bootstrap reste positif, et le résultat ne dépend ni du meilleur trade ni de la meilleure année.
   - **Mais** :
     - c'est **une seule réussite sur quatre marchés** pour la même règle : États-Unis non significatif, Europe nulle, Asie-Pacifique perdante ;
     - les données japonaises sont **en USD**, donc elles mêlent le Nikkei et le yen, alors qu'un CFD JP225 est en yens ;
     - au dimensionnement NEXUS (0,5 % de risque au stop), elle rapporte **+4 % en 32 ans**.
   - C'est une **candidate de recherche**, pas une stratégie exploitable en l'état.
2. **RSI 30/50 sur le marché américain** est le meilleur résultat américain, mais seulement **prometteur**.
   - Sur 2010-2023 S1 : +0,62 % par trade [IC95 +0,11 ; +1,05], p corrigé 0,005, 81 % de gagnants. La règle tient à 0,20 % de coût par côté et au retard d'une séance.
   - Elle **perdait de l'argent sur 1928-1992** (−0,38 % par trade) : critère C5 non rempli.
   - Le retour à la moyenne de l'indice américain est donc un **phénomène d'époque**, et non une loi permanente. Le document 1 le disait lui-même (« depuis 1985 »).
3. **Le RSI 2 d'origine ne bat pas le hasard sur l'indice américain après sa publication.**
   - Sur 2010-2023 : +0,24 % par trade, p = 0,12.
   - Les chiffres d'avant 2010 se reproduisent à peu près, mais l'avantage s'est affaibli après publication : c'est la leçon du document indien, retrouvée sur le marché d'origine.
4. **Un taux de réussite élevé ne prouve rien.** Des entrées **au hasard** avec la même règle de sortie gagnent 59 à 75 % des trades.
5. **La gestion de l'exposition (H5-EXP) réduit le risque, mais pas assez, et détruit l'alpha.**
   - Les paliers `lock` sur P4-01 font passer le drawdown de 45 % à 29 % et la part du meilleur trade de 79 % à 70 %.
   - L'alpha tombe de +13,5 à +1,8 %/an (p 0,41).
   - Verdict : **rejeté**. La concentration n'est pas un défaut de gestion : c'est la nature même de ces gains.

**Aucun agent Cubrik n'est préparé.** La consigne l'exige seulement après franchissement des critères **et** validation autorisée par vous.

## 2. Ce que disent les 7 documents (résumé de l'audit)

- **Connors (6 stratégies)** :
  - une seule famille d'achats de repli dans une tendance haussière ;
  - règles antérieures à 2010, d'où une période post-2010 hors échantillon ;
  - aucun stop, aucun coût, aucune période précisés.
- **RSI 2 en Inde** : la seule source méthodologiquement sérieuse. Elle compare aux entrées aléatoires appariées, montre que le taux de réussite vient de la sortie, examine le retard d'exécution et regroupe les trades. Nous avons reproduit ces contrôles.
- **Turtles** :
  - aucune période ni paire identifiable ;
  - variante sans stop ;
  - un trade valant 50 % du capital.
  - Ces chiffres n'apportent aucune preuve.
- **Monte Carlo** : méthodes reprises. Le « score de robustesse » commercial ne l'est pas, et le drawdown de 200 % n'existe qu'en P&L additif.
- **Gestion du risque** : distinction entre risque au stop, exposition et gap ; taille zéro si le minimum dépasse le budget.
- **Kullamägi et Breitstein** :
  - principe transposable : protection progressive des gains ;
  - non transposables : la vente partielle (non documentée dans Cubrik) et l'entrée au range d'ouverture (aucun opérande horaire).
- **3 stratégies de retour à la moyenne** : deux n'ont pas de règles publiées ; la stratégie SPY exige les plus hauts journaliers, absents des données.

## 3. Compatibilité Cubrik (résumé de la matrice)

**Exprimables dans le format documenté** :

- RSI 2 et RSI 30/50 (`rsi`, `sma`, sortie `crossesAbove`) ;
- `maxBarsInTrade` ;
- les paliers `lock`.

**Non exprimables** :

- R3 et %B sur 3 jours (comparaison d'un indicateur à ses valeurs passées) ;
- les comptages de jours ;
- la vente partielle (non documentée).

**À vérifier dans votre compte** :

- les périodes acceptées pour le RSI ;
- la définition de `lowest`/`highest` ;
- la présence de CFD **JP225 / US500** ;
- l'heure de clôture de leur bougie journalière.

## 4. Résultats détaillés (fenêtre principale)

| Stratégie | Trades | Gagnants | Rend. moyen [IC95] | PF | p BH (hasard) | Coûts × 2 / t+1 | 1928-1992 | Verdict |
|---|---|---|---|---|---|---|---|---|
| RSI 2 sans stop (US) | 104 | 70 % | +0,24 % [−0,12 ; +0,54] | 1,49 | 0,21 | +0,14 / +0,30 | −0,34 % | Rejeté |
| RSI 2 + stop 6 % (US) | 104 | 70 % | +0,18 % [−0,20 ; +0,51] | 1,34 | 0,23 | +0,09 / +0,32 | −0,32 % | Rejeté |
| **RSI 30/50 + stop (US)** | 88 | 81 % | **+0,62 % [+0,11 ; +1,05]** | 2,19 | **0,005** | +0,51 / +0,91 | **−0,38 %** | **Prometteur** |
| Double 5 + stop (US) | 211 | 75 % | +0,26 % [−0,01 ; +0,51] | 1,47 | 0,20 | +0,15 / +0,16 | −0,27 % | Rejeté |
| RSI 2 + stop (Europe) | 223 | 66 % | +0,12 % [−0,09 ; +0,33] | 1,25 | 0,23 | +0,03 / +0,31 | — | Rejeté |
| **RSI 2 + stop (Japon)** | 184 | 72 % | **+0,47 % [+0,18 ; +0,73]** | 1,86 | **0,005** | +0,37 / +0,51 | — | **Candidate** |
| RSI 2 + stop (Asie-Pacifique) | 252 | 59 % | −0,20 % [−0,46 ; +0,04] | 0,73 | 0,99 | −0,30 / −0,05 | — | Rejeté |

**En euros (1 000 €, effet de change ignoré)**

| Stratégie | Règle NEXUS 0,5 % : final (DD) | Notionnel 100 %, hors règle : final (DD) | Achat-conservation de l'indice |
|---|---|---|---|
| RSI 30/50 (US, 2010-2023 S1) | 1 046 € (1,5 %) | 1 680 € (16,9 %) | +408 % (filtre SMA 200 seul, investi à 100 % : +95 %, DD 22,7 %) |
| RSI 2 (Japon, 1991-2023 S1) | 1 040 € (0,7 %) | 2 274 € (14,4 %) | +110 % en USD (filtre SMA 200 seul : −27,5 %, DD 65 %) |

Le chiffre exact de chaque ligne figure dans `06_resultats_backtests.md`, ainsi que les frais, le financement et le Sharpe.

## 5. Le vrai problème : avantage statistique contre rentabilité exploitable

- Avec la règle NEXUS (0,5 % de risque au stop, stop catastrophe de 6 à 11 %), la position n'engage que **5 à 8 % du capital**, quelques jours par an. Le rendement annuel est donc de l'ordre de **0,1 %**, même quand l'avantage est réel.
- Pour atteindre 2 à 4 %/an, il faut investir **100 % du capital** à chaque signal. Le risque réel par trade monte alors à 6 à 11 % du capital au stop, et le 95e percentile du drawdown simulé atteint **22 à 23 %**, bien au-delà de 10 %.
- **Aucune des stratégies étudiées n'atteint vos objectifs indicatifs** (10 à 20 %/an avec un drawdown inférieur à 10 %). Par construction, le retour à la moyenne est investi environ 10 % du temps ; il ne peut rapporter que quelques pour cent par an sans levier.

## 6. Discipline

- **Pré-enregistrement** (`3e0a221`) commité avant les données d'indices. La donnée est coupée au 2023-06-30 dès la lecture et le fichier brut n'est pas conservé.
- **Registre : 184 essais** (167 avant cette phase).
  - P5 : 8 essais sur 8.
  - P5-SENS : 6 sur 8.
  - P5-DIAG : 3 sur 8.
  - Aucune réinitialisation.
  - Validation : 0 accès. Test final : 0 accès.
- **Tests** : 103 réussis (96 + 7 nouveaux).
- **Corrections avant résultats** : aucune modification des hypothèses.
- **Corrections après résultats** :
  - l'étiquette du verdict de la candidate japonaise affichait encore « à confirmer » après Monte Carlo ; corrigée, sans changer aucun chiffre ;
  - une phrase du rapport généré sur la volatilité était trop générale ; corrigée.
- **Limites** :
  1. Indice CRSP et indices régionaux French : ni SPY ni CFD. Il manque les plus hauts et plus bas, donc pas de stop intrajournalier.
  2. Données régionales en USD : effet de change mêlé.
  3. Exécution à la clôture : une approximation de la bougie D1 d'un CFD.
  4. Financement CFD estimé (RF + 2,5 %).
  5. Les 7 tests utilisent les mêmes données de marché sur des périodes qui se recouvrent ; la correction BH suppose une dépendance modérée.

## 7. Recommandations et décisions qui vous reviennent

1. **Ne créer aucun agent maintenant.**
2. **Vérifier dans Cubrik Demo** (gratuit) :
   - CFD JP225 et US500 dans `list_instruments` ;
   - RSI de période 2 et 5 accepté ;
   - heure de la bougie D1.
3. **Si JP225 est disponible**, deux décisions vous reviennent :
   - (a) m'autoriser à rechercher des données journalières JP225 ou Nikkei **en yens** (source légale à trouver, sans achat sans votre accord), pour séparer l'effet de change ;
   - (b) autoriser **une seule ouverture** de la période de validation (2023-07 → 2024-12) pour RSI 2 Japon et RSI 30/50 US, figés tels quels. Un backtest Cubrik de ces stratégies **ouvrirait aussi** cette période, ainsi que le test final.
4. **Décision de dimensionnement** :
   - soit vous gardez 0,5 % de risque au stop, et ces stratégies ne rapporteront que des fractions de pour cent par an ;
   - soit vous acceptez un notionnel plus élevé, avec un drawdown attendu de 15 à 25 %. Cela modifierait la règle permanente de risque ; c'est votre décision, pas une conclusion de recherche.
5. **Suivi de tendance** : la gestion `lock` ne résout pas la concentration. Je recommande de **ne plus consacrer d'essais** aux variantes de gestion de P4-01, sauf diversification réelle vers d'autres classes d'actifs (forex, or, indices) selon les instruments Cubrik.
