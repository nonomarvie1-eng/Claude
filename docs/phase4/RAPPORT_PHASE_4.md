# NEXUS QUANT — Rapport de phase 4 : recherche de stratégies compatibles Cubrik

Date : 2026-11-27. **Période de développement uniquement** (2020-01 → 2023-06). Validation et test final verrouillés (0 accès). Aucun compte Cubrik, aucun abonnement, aucun ordre.

Détails générés automatiquement : `reports/phase4_cubrik_lot_4_01.md`. Audit de la plateforme : `01_audit_cubrik.md`. Protocole pré-enregistré : `02_hypotheses_protocole.md`.

*Résultats dérivés de données Binance Vision (CC BY-NC-SA 4.0).*

## 1. Conclusion

**Aucune stratégie n'est assez robuste pour être transformée en agent Cubrik.** Les 4 hypothèses pré-enregistrées sont **rejetées** selon les critères fixés à l'avance. Conformément à la consigne, je ne prépare donc **aucun prompt d'agent**.

Trois constats nuancent ce verdict :

1. **Le suivi de tendance contient de l'information de timing.**
   - Les entrées de Donchian, de la SMA100 et du momentum font mieux que des entrées aléatoires de même nombre, de même durée et de même sens : 96e à 98e centile.
   - Mais leur avantage sur un panier passif à exposition égale **n'est pas significatif** : p corrigé de 0,35 à 0,37.
2. **Les gains reposent sur très peu de trades.**
   - Un seul trade MATIC (+174R, de 0,025 à 1,10 $) fournit **984 des 1 240 € de gain** de P4-01.
   - Sans MATIC, P4-01 gagne 324 € et P4-03 perd 352 €.
   - Le R médian est négatif pour les trois règles de tendance.
3. **Le dimensionnement façon Cubrik ne limite pas le drawdown du portefeuille.**
   - La taille est fixée à l'entrée et n'est jamais réduite. Les positions gagnantes grossissent jusqu'à représenter 82 % du capital (mai 2021), puis rendent leurs gains.
   - Drawdowns de **45 à 58 %**, malgré 0,5 % de risque par trade.
   - Avec la règle d'arrêt à 10 %, toutes les stratégies de tendance sont arrêtées : P4-01 en août 2022, P4-02 en mai 2022, P4-03 en juillet 2020.

## 2. Audit Cubrik (résumé)

Source principale : le dépôt public officiel de son serveur MCP, qui contient le format exact des règles de backtest.

| Contrainte | Conséquence |
|---|---|
| Règles : jusqu'à 6 conditions ET, 4 sorties OU ; 26 opérandes (SMA, EMA, RSI, ATR, MACD, Bollinger, Keltner, ADX, ROC, Donchian via `highest`/`lowest`, Supertrend, FVG, order blocks…) | Indicateurs classiques et tendance : **compatibles** |
| **Aucun opérande d'heure ni de session** | ORB, Silver Bullet, killzones, sessions : **incompatibles** |
| **Aucun opérande inter-actifs** ; un calcul par symbole | Force relative, SMT, arbitrage, rotation : **incompatibles** |
| Stop et objectif en **% fixe** | Les stops en ATR deviennent un % figé par actif |
| Unités de temps 1m à 1D ; forex, métaux et indices **à partir de H1** ; 1m limité aux 90 derniers jours | H1/H4/D1 conseillés |
| Backtest : 12 mois (19 €/mois) ou 5 ans avec frais et glissement (59 €/mois, offre qui donne aussi le serveur MCP) ; **toujours jusqu'à aujourd'hui** | **Un backtest Cubrik d'une candidate ouvre de fait nos périodes verrouillées** |
| L'agent réel est une **IA** qui suit une instruction textuelle, contrôlée toutes les 30 à 60 minutes | Écart possible avec le backtest, à mesurer sur compte démo |
| Offre Demo gratuite : 125 crédits, 1 agent, compte démo du courtier | Suffit pour les vérifications du §6 de l'audit |

Non publiés (à vérifier depuis votre compte) : frais et glissement simulés, modèle d'exécution, liste des instruments, sens de `perTradePct`.

## 3. Hypothèses testées (une configuration chacune, paramètres fixés a priori)

Univers figé **avant** la période, selon le volume d'octobre à décembre 2019, pour éviter le biais de survie : BTC, ETH, BNB, XRP, EOS, BCH, LTC, TRX, LINK, MATIC. Stops : 3 × l'ATR médian du 2e semestre 2019, soit 16 à 25 %.

| Hypothèse | Trades | R moyen net [IC95] | Rendement | Max DD | Sharpe | PF | Δ vs référence %/an [IC95] | p BH | Hasard (centile) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| P4-01 Donchian 55/20 D1 | 103 | +2,55 [−0,10 ; +6,91] | +124 % | 45 % | 0,82 | 3,14 | +13,5 [−10,8 ; +43,8] | 0,35 | 97 | Rejeté |
| P4-02 SMA100 D1 | 349 | +0,90 [−0,01 ; +2,35] | +141 % | 52 % | 0,82 | 2,55 | +8,4 [−16,8 ; +39,8] | 0,37 | 96 | Rejeté |
| P4-03 Momentum 90 j achat et vente (perpétuels) | 628 | +0,36 [−0,16 ; +1,30] | +70 % | 58 % | 0,56 | 1,50 | +25,9 contre trésorerie [−12,2 ; +70,0] | 0,35 | 98 | Rejeté |
| P4-04 RSI2 dans la tendance | 253 | +0,00 [−0,11 ; +0,11] | +0,2 % | 7 % | 0,04 | 1,01 | −1,8 [−5,1 ; +1,1] | 0,86 | 25 | Rejeté |

Références :

- panier équipondéré passif, investi à 100 % : **+894 %**, drawdown **81 %** ;
- à même exposition moyenne (13 à 21 %), les règles de tendance font mieux de +8 à +14 %/an, mais avec des intervalles de confiance très larges.

**Critères** :

- C1 (significativité), C2 (IC du R moyen strictement positif) et C5 (stabilité dans le temps) échouent pour toutes les hypothèses.
- C6 (drawdown < 10 %) échoue pour toutes les règles de tendance.
- Les règles de tendance résistent bien aux coûts doublés (C3) et à leurs voisins de paramètres (C4) : elles ne sont pas fragiles aux réglages, mais elles dépendent du régime de marché.

**Stabilité dans le temps** : tout l'avantage vient de **2021**, l'année du marché haussier des altcoins (+53 à +111 %/an contre la référence). En 2020, toutes sont en dessous de la référence. 2022 et le 1er semestre 2023 sont neutres.

**P4-03 (achat et vente)** :

- la jambe vendeuse perd (R −0,17 sur 312 trades), comme la littérature le laissait prévoir (Han, Kang & Ryu) ;
- le financement a coûté **297 USDT**, soit 30 % du capital initial.

**P4-04 (retour à la moyenne)** : aucun effet. Cela confirme le rejet de la famille E.

### En euros, sur 1 000 €

| Hypothèse | 0,5 %, sans arrêts | Avec règles (2 %/jour, arrêt à 10 %) | 0,25 % (prudent) |
|---|---|---|---|
| P4-01 | 2 285 € (DD 39 %) | 1 267 € (DD 13 %, arrêt le 19/08/2022) | 1 672 € (DD 28 %) |
| P4-02 | 2 454 € (DD 47 %) | 1 244 € (DD 19 %, arrêt le 11/05/2022) | 1 779 € (DD 34 %) |
| P4-03 | 1 734 € (DD 57 %) | 971 € (DD 22 %, arrêt le 06/07/2020) | 1 481 € (DD 44 %) |
| P4-04 | 1 023 € (DD 15 %) | 1 052 € (DD 14 %) | 1 022 € (DD 15 %) |

Le drawdown mesuré avec les règles dépasse 10 % : l'arrêt est évalué heure par heure, et un gap peut faire sortir au-delà du seuil.

Ces gains en euros **ne sont pas des preuves** : ils viennent d'une seule année et de quelques trades, sans significativité. Vos objectifs indicatifs (drawdown < 10 %, Sharpe > 1) ne sont atteints par aucune stratégie.

## 4. Discipline et traçabilité

1. Pré-enregistrement commité **avant** les données et l'exécution : commit `bd61aa8`.
2. Un seul correctif avant les résultats :
   - le ticker de BCH a changé en 2019 (BCHABCUSDT puis BCHUSDT), et le premier classement de l'univers ne lisait qu'un des deux pendant le mois de transition ;
   - après correction, BCH entre dans l'univers et VET en sort ;
   - le premier classement est conservé : `results/batch_4_01_cubrik/universe_v1_bug_alias_bch.json`.
3. Registre : **167 essais** (139 avant cette phase).
   - Phase 4 : 4 essais de sélection, 20 de sensibilité ou de stress de coûts, 4 diagnostics (dont un 2e classement de l'univers après le correctif).
   - Aucune réinitialisation. Budgets respectés : P4 4/4, P4-SENS 20/20, P4-DIAG 4/8.
4. **96 tests réussis** (87 + 9 nouveaux) pour le simulateur Cubrik : causalité, exécution à l'ouverture suivante, stops et gaps, financement, absence de vente à découvert au comptant, plafond de capital, règle des 2 %.
5. Aucun développement d'exécution, de courtier, de déploiement ni de surveillance.

## 5. Ce que je recommande

1. **Ne pas créer d'agent Cubrik maintenant.** Aucune stratégie ne remplit les critères ; un agent ne ferait qu'automatiser une exposition au marché des cryptos sans avantage démontré.
2. **Ne pas ouvrir la validation** : rien ne la justifie.
3. **Vérifier les instruments Cubrik (gratuit, offre Demo)**, comme décrit au §9 de l'audit. C'est la condition pour tester P4-05 : tendance diversifiée sur forex, or et indices. La littérature y est la plus solide (Hurst et al. 2017), et la diversification entre classes d'actifs est la seule réponse crédible au problème de concentration constaté ici. Aucune donnée ne sera achetée avant de savoir quels marchés Cubrik exploite réellement.
4. **Une piste sérieuse, si vous l'autorisez : la gestion de la taille dans le temps.** Les règles de tendance ont du timing, mais le dimensionnement fixé à l'entrée les rend inutilisables. Cubrik propose des paliers de gestion (`management`), dont le détail des actions possibles est à vérifier. Une hypothèse unique, pré-enregistrée, pourrait tester une prise de profit partielle ou un stop suiveur à palier sur P4-01. Ce serait un **nouvel essai**, décompté du budget. Je ne le lance pas sans votre accord, car il risque de ressembler à une recherche de variante après coup.

## 6. Décisions qui vous reviennent

1. **Récupérer depuis votre compte Cubrik Demo** les 6 informations du §9 de l'audit, sans connecter de courtier ni démarrer d'agent.
2. **Autoriser ou non** l'hypothèse « gestion de la taille » sur P4-01 (1 essai pré-enregistré).
3. Selon la liste des instruments : **autoriser la recherche d'une source de données forex et indices** pour P4-05. Les options sont chiffrées dans les phases précédentes ; aucun achat sans votre accord.
