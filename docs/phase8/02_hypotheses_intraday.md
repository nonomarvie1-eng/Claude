# Phase 8 — Cinq hypothèses intrajournalières (PRÉSENTÉES, NON LANCÉES)

**Statut : en attente de votre autorisation.**

- Aucune règle n'est enregistrée au registre et aucun essai n'est lancé.
- Brouillon machine : `experiments/drafts/batch_8_01_intraday_DRAFT.toml`. Il sera commité comme pré-enregistrement définitif, inchangé ou corrigé selon vos remarques, **avant** toute exécution.

## Contraintes qui ont guidé le choix (audit `01`)

- **Unité H1** : la seule unité intrajournalière compatible avec Cubrik sous l'offre Demo ou Beginner (contrôle toutes les 60 min) et économiquement tenable avec 1 000 €. Le coût d'un aller-retour en perpétuel y vaut environ 0,15 R.
- **Crypto perpétuels**, achat **et** vente, sans levier (notionnel ≤ capital). Ce sont les seules données intrajournalières légales dont nous disposons, et le seul marché backtestable sous H1 dans Cubrik.
- **Opérandes Cubrik natifs uniquement** : aucune heure, aucune session, aucun calcul entre indicateurs.
- **Fréquence de 1 à 3 trades par jour atteinte par la diversification** : environ 0,1 à 0,3 trade par jour et par actif, sur 10 actifs, et non par le sur-trading d'un seul actif.
- **Aucune famille déjà rejetée n'est reprise à l'identique.**

## Les cinq hypothèses

| Clé | Stratégie (H1, perpétuels, achat et vente) | Justification économique et littérature | Règles Cubrik | Différence avec nos 194 essais |
|---|---|---|---|---|
| **H8-1 Cassure de volatilité sur 24 h** | Long si la clôture croise au-dessus du plus haut des 24 bougies précédentes ; short si elle croise sous le plus bas. Sortie sur le canal opposé de 12 bougies. Stop = 2 × ATR médian (mesuré avant la période), en % fixe | Momentum de série temporelle intrajournalier documenté sur Bitcoin (Shen, Urquhart & Wang, 2022, *Financial Review* ; Wen et al., 2022) : diffusion lente de l'information, flux des acteurs de tendance | `price crossesAbove highest(24)` / `crossesBelow lowest(24)` ; sortie `lowest(12)`/`highest(12)` ; `side: both` | P4-01 et P4-03 portaient sur du D1 et du ROC 90 jours ; A et B sur du M5 avec des sessions. **H1 avec vente à découvert : nouveau** |
| **H8-2 Tendance par rapport au VWAP** | Long quand la clôture croise au-dessus du VWAP de la journée ET EMA50 > EMA200 ; short dans le cas symétrique ; sortie au croisement inverse du VWAP | Le VWAP sert de référence d'exécution aux institutionnels. Zarattini & Aziz (2023, SSRN) décrivent un système de tendance intrajournalier fondé sur le VWAP (QQQ) | `vwap`, `ema` ; `crossesAbove` / `crossesBelow` | Jamais testé. **Ancrage du VWAP dans Cubrik à vérifier** (réinitialisation à 00:00 UTC ?) |
| **H8-3 Retour à la moyenne en marché sans tendance** | Long si la clôture < Bollinger basse (20, 2) ET ADX(14) < 20 ; short dans le cas symétrique ; sortie au retour à la moyenne (clôture croise la SMA 20) | En l'absence de tendance, les écarts de court terme reflètent un besoin de liquidité qui se résorbe (Nagel, 2012). Le filtre ADX vise les régimes de range | `bollinger`, `adx`, `sma` | La famille E (H1/H4, achat seulement, sans filtre de régime) a été rejetée. **Ici : filtre de régime + vente à découvert.** Risque de doublon partiel, signalé |
| **H8-4 Repli dans la tendance** | Long si EMA50 > EMA200 ET RSI(14) < 30 ; short si EMA50 < EMA200 ET RSI(14) > 70 ; sortie quand le RSI recroise 50 | Combinaison des deux effets documentés aux horizons courts sur crypto : momentum de tendance et retournement de court terme (Wen et al., 2022) | `ema`, `rsi` | P4-04 (RSI 2, D1, achat seulement) a été rejeté. **H1, deux sens, filtre de tendance : distinct**, mais de la même famille que H8-3. Les deux seront corrigés ensemble pour les tests multiples |
| **H8-5 Réplication multi-classes** | La meilleure des hypothèses H8-1 à H8-4, **figée**, sur XAU/USD, EUR/USD, GBP/USD, NAS100, US500 et JP225 en H1 | Un avantage réel doit survivre ailleurs que sur un seul marché (leçon des phases 3 et 5) | Identiques ; Cubrik backteste ces marchés à partir de H1 | **Exécutable seulement si vous fournissez** des exports MT5 démo H1 de ces instruments, jusqu'au 2023-06-30 |

**Exclues, avec la raison** :

- M5 et M15 : coût de 0,3 à 1,3 R par trade, et contrôle Cubrik trop lent hors des offres Pro et Max (20 à 40 % du capital par mois) ;
- ORB, Silver Bullet, sessions, Turnaround Tuesday, lundi Nikkei, sortie en fin de journée : pas d'opérande horaire ;
- « Beat the Market » (Zarattini, Aziz & Barbon, 2024 : momentum intrajournalier sur SPY avec bornes de bruit), la littérature la plus solide en day trading sur indice : elle exige l'heure **et** des données SPY en minute. Elle est **incompatible avec Cubrik** et sans données ;
- Williams %R sur GBP/USD M30 : M30 interdit pour le forex dans Cubrik, filtre de la veille non défini, pas de données. Sa version oscillateur en H1 est couverte par H8-4.

## Données nécessaires

- **H8-1 à H8-4** :
  - M1 Binance de BTC et ETH déjà disponible ;
  - téléchargement gratuit, sur Binance Vision, du H1 perpétuel et du financement des 8 autres actifs de l'univers de la phase 4 (déjà en H1 au comptant), **jusqu'au 2023-06-30 seulement**.
- **H8-5** : vos exports MT5 démo.

## Protocole proposé (à valider)

- **Univers** : BTC, ETH (décision) + les 8 autres cryptos de l'univers de la phase 4 (réplication). Univers figé, sans biais de survie.
- **Période** : 2020-01 → 2023-06, découpée en 2020-2021 (marché haussier) et 2022-2023 S1 (marché baissier).
- **Exécution** :
  - à l'ouverture de la bougie H1 suivante ;
  - **stress** : une bougie de retard supplémentaire, pour simuler le contrôle Cubrik toutes les 60 minutes ;
  - stop vérifié sur les bougies M1 (BTC, ETH) ou H1 (les autres), stop d'abord.
- **Coûts** :
  - taker perpétuel 0,05 % par côté, glissement de 0,05 %, financement réel ;
  - stress : coûts × 2.
- **Taille** :
  - **0,5 % de risque** pour la décision ;
  - 0,25 %, 1 % et 2 % rapportés en information ;
  - le levier est analysé à part (multiplicateur), jamais recommandé.
- **Mesures demandées** :
  - rendement journalier moyen et médian, hebdomadaire, mensuel ;
  - trades par jour ;
  - % de journées gagnantes, à +5 % et perdantes ;
  - espérance nette par trade, profit factor, Sharpe ;
  - drawdown maximal, pire journée, pire semaine, plus longue série de pertes ;
  - risque de ruine (scénarios : −20 %, −50 % du capital) ;
  - frais, financement, capital final.
- **Statistiques** :
  - R moyen net avec IC95 (bootstrap par semaines) ;
  - entrées aléatoires appariées (même nombre, mêmes durées, mêmes sens) ;
  - p corrigé (Holm, 4 tests) ;
  - **Sharpe déflaté** avec le nombre total d'essais du registre (198 et plus) ;
  - sous-périodes ;
  - Monte Carlo (10 000 tirages) seulement si C1 à C3 sont satisfaits.
- **Critères de candidature** :
  - R net > 0 avec IC95 > 0 ;
  - p corrigé < 0,05 ;
  - Sharpe déflaté > 0,95 ;
  - positif dans les deux sous-périodes et sur au moins 6 des 8 actifs de réplication ;
  - toujours positif avec coûts × 2 et avec une bougie de retard.
- **Budget proposé** :
  - 4 essais de sélection (H8-1 à H8-4, une configuration chacune) ;
  - 16 essais de sensibilité (4 voisins pré-déclarés par hypothèse) ;
  - 4 diagnostics ;
  - H8-5 : 1 essai par instrument fourni, plafonné à 6.

## Ce qu'il est honnête d'attendre

- Nos phases 2 et 3 n'ont trouvé **aucune espérance nette positive** en intraday sur BTC.
- Le meilleur signal intrajournalier mesuré (ORB) apportait environ +0,1 R brut, contre 0,15 R de coûts en H1.
- **La probabilité a priori qu'une des quatre hypothèses survive est faible.**
- Même dans le cas favorable d'un avantage de +0,1 à +0,2 R net par trade, à 0,5 % de risque et 2 trades par jour, le rendement serait d'environ **0,1 à 0,2 % par jour** en moyenne, très loin de 5 %, avec des journées perdantes fréquentes.
