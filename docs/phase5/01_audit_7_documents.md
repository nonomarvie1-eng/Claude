# Phase 5 — Audit des 7 nouveaux documents

Date : 2026-11-27. Les 7 transcriptions ont été lues en entier : résumé français et transcription anglaise.

Notation utilisée dans ce document :

- **[A]** : affirmation de l'auteur ;
- **[R]** : résultat annoncé, non vérifié ;
- **[H]** : mon hypothèse ou mon interprétation ;
- **[N]** : nos résultats indépendants (registre NEXUS).

## 1. « 6 stratégies de Larry Connors, modifiées et backtestées »

| Élément | Contenu |
|---|---|
| Marché, unité | ETF SPY, journalier ; « depuis 1985 » pour la leçon générale [A] ; période exacte des backtests non précisée |
| Filtre commun | Clôture > SMA 200 |
| 1. Double 5 | Achat : clôture au plus bas des 5 derniers jours. Vente : clôture au plus haut des 5 derniers jours. Version d'origine sur 7 jours [A]. **[R]** 352 trades, +0,65 % par trade, drawdown maximal 14 % |
| 2. Jours de baisse | Achat : clôture < SMA 5 et au moins 4 baisses sur les 5 derniers jours. Vente : clôture > plus haut de la veille. **[R]** +0,55 % par trade, 4 %/an, investi 10 % du temps, drawdown maximal 13 % |
| 3. %B | Achat : %B (Bollinger 5 jours, 2 σ) < 0,2 pour le **3e jour consécutif**. Vente : clôture > plus haut de la veille. **[R]** 55 trades, ≈ +1 % par trade, 87 % de gagnants, investi 2,5 % du temps |
| 4. R3 | Achat : RSI(2) **en baisse 3 jours de suite** et < 20. Vente : RSI(2) > 70. **[R]** 94 trades, 88 % de gagnants, +1,16 % par trade, exposition 4,57 % |
| 5. RSI 30/50 | Achat : RSI(5) < 30. Vente : RSI(5) repasse au-dessus de 50. **[R]** 6,1 %/an, investi moins de 12 % du temps |
| 6. Trois jours bas | Achat : plus haut et plus bas en baisse pour le 3e jour consécutif. **Vente non précisée.** **[R]** 3,6 %/an, ≈ +0,8 % par trade, 79 % de gagnants, drawdown maximal 14 % |

**Points non précisés** :

- frais, glissement, prix d'exécution (clôture du signal ou ouverture suivante), période de test ;
- stop : aucun n'est mentionné ;
- dimensionnement : implicitement 100 % du capital [H] ;
- la règle de sortie de la stratégie 6.

**Limites et biais** :

- Les stratégies ont été **modifiées par les auteurs** (Double 7 devenu Double 5, « plus de trades ») et choisies après coup sur les données qu'ils présentent : biais de sélection.
- « Les six ensemble » donnent 6,3 %/an : l'auteur reconnaît qu'elles se ressemblent trop. Ce ne sont pas six preuves indépendantes, mais **une seule famille**.
- Un taux de réussite élevé est en partie mécanique, puisqu'on sort au premier rebond (voir document 2).
- Le drawdown maximal de 14 % est mesuré avec le filtre SMA 200 et sans stop. Il ne dit rien du pire trade possible.

**Atout** : les règles datent d'avant 2010 [A]. Les données de **2010 à 2023 sont donc hors échantillon** par rapport à leur conception. J'utilise ce découpage (§4 du protocole).

**Différences avec nos essais** :

- P4-04 (RSI 2 sur 10 cryptos) a été rejeté [N] : R moyen +0,004, 25e centile des entrées aléatoires.
- La famille E (retour à la moyenne en H1/H4 sur BTC) a été rejetée [N].
- **Aucun de nos 167 essais ne porte sur un indice actions.**

## 2. « La stratégie RSI 2 de Connors fonctionne-t-elle en Inde ? »

| Élément | Contenu |
|---|---|
| Règles | Clôture > SMA 200 et RSI(2) < 10 : achat **à la clôture**. Vente à la clôture du 1er jour où la clôture dépasse la SMA 5. **Pas de stop** |
| Coûts | 0,5 % par côté (futures Nifty), 0,4 % par côté (SPY, actions) [A]. Ces niveaux sont très élevés au regard d'un gain moyen de 0,63 % : l'hypothèse ou la transcription est peut-être erronée [H] |
| Résultats SPY depuis 1993 [R] | 76,6 % de gagnants, +0,63 % par trade après coûts, profit factor 2,98, investi 10,6 % du temps, 1 devient 4,14. Entrées aléatoires (5 000 séries, mêmes durées, jours au-dessus de la SMA 200) : +0,16 % avant coûts contre +0,67 % pour la stratégie ; **aucune série aléatoire ne fait aussi bien** |
| Inde [R] | Nifty : 63,6 % de gagnants, +0,26 % par trade, PF 1,29 ; 1 devient 1,46 contre 5,18 en conservant l'indice ; p ≈ 1/11. Sensex : p ≈ 1/5. Bank Nifty : pire que le hasard. Actions : plus aucun avantage une fois les trades groupés par jour |
| Leçons méthodologiques [A] | (1) Entrées aléatoires + même sortie : 59,7 % de gagnants contre 63,6 % ; **le taux de réussite vient de la sortie**. (2) Un trade sans stop a perdu 35,1 % (Bank Nifty, Covid). (3) Seules 7 variantes sur 15 battent le hasard. (4) Achat le lendemain matin : l'avantage disparaît dès environ 0,18 % de coût par côté. (5) Trades groupés par jour pour éviter la fausse indépendance |

**Biais signalés** :

- transcription erronée sur plusieurs nombres (« 266 000 trades », « 120 % ») ;
- l'auteur note que l'avantage était plus faible dans la seconde moitié des données.

**Ce que je reprends** :

- le test d'entrées aléatoires conditionnées (même régime au-dessus de la SMA 200, mêmes durées) ;
- le taux de réussite des entrées aléatoires avec la même sortie ;
- le stress du moment d'exécution ;
- le groupement par jour ;
- la réplication sur d'autres marchés.

## 3. « Turtle Trade Channels : backtest »

| Élément | Contenu |
|---|---|
| Règles d'origine [A] | Achat si le plus haut ≥ plus haut des 20 bougies précédentes ; vente à découvert si le plus bas ≤ plus bas des 20 précédentes ; sortie au plus bas (ou plus haut) des 10 précédentes ; stop initial à 2 × ATR |
| Variante testée par l'auteur | **Ni stop ni sortie** : mode toujours en position (« buy and sell »), chaque signal inverse retourne la position. Ordres fixes de 10 000 $, commission 0,06 % |
| Résultats [R] | 4 h, paire « F usdt » (illisible), sans levier : +331 %, 151 trades, 39 % de gagnants, PF 1,79, drawdown 19 %, **plus gros gain 50 % du capital initial**. 30 min, paire illisible, levier 2 : +975 %, 1 143 trades, PF 1,32, drawdown 28 %, plus grosse perte 50 % |
| Non précisé | **Période**, paires exactes, glissement ; la commission du 2e test est incohérente (0,6 ou 0,06 %) |

**Biais** :

- deux paires choisies sans justification ;
- aucune référence (achat-conservation) ;
- résultats exprimés sur le capital initial ;
- un seul trade représente 50 % du capital : concentration.

**Ces chiffres ne prouvent rien.** Les règles diffèrent de l'original, faute de stop en ATR.

**Lien avec nos essais [N]** : P4-01 (Donchian 55/20, achat seulement, D1, 10 cryptos) va dans le même sens :

- +124 %, mais un seul trade fournit 984 € des 1 240 € de gain ;
- drawdown de 45 % ;
- alpha non significatif.

Le document confirme qualitativement **la concentration des gains**, sans apporter de preuve.

## 4. « Tester la robustesse avec Monte Carlo »

| Élément | Contenu |
|---|---|
| Méthodes [A] | Mélange de l'ordre des trades ; rééchantillonnage avec remise ; suppression de 5 à 20 % des trades ; bruit sur les prix OHLC (±0,1 à 0,5 %) ; perturbation des paramètres (RSI de 12 à 16, EMA de 45 à 55) ; de 1 000 à 10 000 simulations ; regarder la queue de distribution |
| Résultats [R] | Stratégie à +1 700 % : drawdown d'origine 19 %, mais **médiane 61 %**, moyenne 80 % et « jusqu'à 200 % » après mélange ; 62,5 % de probabilité de dépasser 50 %. En supprimant 5 à 20 % des trades : rendement moyen −6,95 %, 5e percentile −18 % |
| Biais et limites | **Outil commercial** (CoinQuant, lien de parrainage). « Score de robustesse » propriétaire non défini (55 %, 22 %) : **je ne le reprends pas**. Un drawdown de 200 % n'a de sens que sur une courbe en **P&L additif** (montant fixe par trade, capital rechargé) : un portefeuille solvable sans levier ne perd jamais plus de 100 % |

**Ce que je reprends**, sous réserve de pertinence (§7 du protocole) :

- mélange de l'ordre des trades, **seulement si le dimensionnement dépend du capital** : avec une taille fixe, l'ordre ne change que le drawdown ;
- bootstrap **par blocs**, pour préserver les dépendances ;
- suppression aléatoire de trades ;
- coûts accrus ;
- retard d'exécution ;
- perturbation des paramètres ;
- retrait du meilleur trade et de la meilleure année ;
- analyse par régime.

**Convention** : nos drawdowns sont calculés sur une courbe de capital **composée** et solvable, donc bornés à 100 %.

## 5. « La gestion du risque en trading »

Documentaire pédagogique, **exemples fictifs** [A]. Pas de stratégie testable.

**Règles retenues** (cohérentes avec notre cadre) :

- taille = (budget − frais fixes) / distance au stop, arrondie vers le bas ; **si la plus petite taille dépasse le budget, la taille est zéro** ;
- distinguer le risque au stop de l'exposition notionnelle ;
- un stop n'est pas un prix garanti (gap : 61,50 $ perdus au lieu de 50 $) ;
- carte des expositions corrélées et limite globale ;
- un seuil de drawdown est un point d'arrêt et de réexamen, pas une garantie ;
- l'espérance (taux de réussite × gain moyen − taux de pertes × perte moyenne − coûts) prime sur le taux de réussite ;
- ne changer qu'une règle à la fois ; conserver toutes les versions.

**Usage** : ces règles fondent la distinction, dans nos résultats, entre le risque initial au stop, l'exposition, le risque de gap et les gains latents (§9 de la demande). Le document confirme aussi l'**incompatibilité des micro-futures** avec 1 000 € (taille minimale > budget), conclusion déjà notée en phase 3 [N].

## 6. « Les moyennes mobiles selon Kullamägi et Breitstein »

| Élément | Contenu |
|---|---|
| Unité | Journalier (Kullamägi) ; journalier et intraday (Breitstein) |
| Moyennes | Kullamägi : SMA 10, 20, 50 (EMA 10/20 pour les jambes courtes) ; Breitstein : SMA 20 et SMA 200 |
| Filtre de marché | SMA 10 > SMA 20 et les deux montantes : bon marché ; les deux en baisse et 10 < 20 : ne pas acheter de cassures |
| Entrée | Cassure de chaque « marche » d'un escalier de consolidation, au plus haut du **range d'ouverture** du jour de cassure ; valeurs « en jeu » (fort volume, tendance) |
| Gestion | Stop sous le plus bas du jour de cassure. **Après 3 à 5 jours, vendre 1/3 à 1/2 et remonter le stop au point mort.** Puis sortie à la 1re **clôture** sous la SMA 10 (valeurs rapides) ou SMA 20 (valeurs lentes) |
| Croisements 50/200 | Aucun des deux ne les utilise |

**Biais** :

- deux traders **sélectionnés pour leur réussite** (biais du survivant) ;
- exemples choisis a posteriori (NVDA, PLUG, PLTR, SMCI) ;
- aucune statistique ;
- « ça marche depuis 100 ans » n'est pas démontré.

**Non quantifiable sans hypothèses supplémentaires** :

- « valeurs en jeu » ;
- « escalier » ;
- range d'ouverture du jour de cassure, qui suppose une heure : **incompatible avec Cubrik**, qui n'a pas d'opérande horaire ;
- choix entre SMA 10 et SMA 20 selon la vitesse de la valeur, qui est discrétionnaire.

**Ce qui est transposable** : le principe de **protection progressive des gains** (stop remonté au point mort, puis sortie sur une moyenne).

**Compatibilité Cubrik** :

- **Vérifié** dans le format des règles (`rules.md` du dépôt officiel) : la gestion `management` par paliers (`at` → `action`), avec l'action **`lock`** (« un lock doit garder moins que le gain qui le déclenche ») ; ainsi que la sortie sur signal « clôture croise sous la SMA N ».
- **Non documenté** : la **vente partielle**. Je ne la suppose pas.

## 7. « 3 stratégies de retour à la moyenne sur ETF »

| Élément | Contenu |
|---|---|
| 1. XLP achat | « Les règles exactes sont affichées à l'écran, pas dites » [A] : **règles inconnues**, non testables. [R] 457 trades, +0,38 % par trade, 6,7 %/an contre 6,8 % en achat-conservation, investi 28 % du temps |
| 2. FXI vente à découvert | Indicateur IBS ; règles **non dites**. [R] « Bat largement l'achat-conservation » sur 15 ans ; ne marchait pas avant 2008 (instabilité reconnue) |
| 3. SPY plus bas de 5 jours | Achat à la clôture sur un plus bas de 5 jours (le texte ne précise pas : plus bas des **clôtures** ou des **plus bas** [H]). Vente quand la clôture dépasse le **plus haut de la veille**, ou après 5 jours de bourse. [R] Depuis 1993 : 8,8 %/an contre 9,5 % en achat-conservation, investi 19 % du temps |
| Affirmations générales [A] | Retour à la moyenne meilleur sur actions que sur les autres classes d'actifs ; journalier meilleur ; meilleur en marché baissier ; achat meilleur que vente ; meilleurs indicateurs : IBS, RSI, Williams %R |

**Limites** :

- le « rendement ajusté au risque » (rendement / temps investi) n'est **pas** une mesure de risque : il suppose qu'on peut placer le capital ailleurs sans risque le reste du temps ;
- le code est réservé aux membres payants.

**Remarque** : la stratégie 3 n'a **pas de filtre SMA 200** ; elle est distincte de Double 5.

## 8. Doublons et sélection

| Famille | Membres | Décision |
|---|---|---|
| Achat de repli dans une tendance haussière (Connors) | RSI 2, R3, RSI 30/50, %B, Double 5, jours de baisse, trois jours bas, plus bas de 5 jours (SPY) | **Une seule famille**, fortement corrélée (aveu de l'auteur). J'en retiens 3, distinctes par la construction du signal et compatibles avec des données de clôture : **RSI 2** (référence documentée), **RSI 30/50** (la plus native dans Cubrik) et **Double 5** (extrêmes de prix plutôt qu'oscillateur). Exclues : R3 et %B (comparaison d'un indicateur à ses valeurs passées, non vérifiée dans Cubrik) ; jours de baisse (comptage de jours) ; trois jours bas et plus bas de 5 jours (plus haut et plus bas journaliers indisponibles dans nos données, §3 du document 03) |
| Réplication hors marché | RSI 2 sur l'Europe, le Japon et l'Asie-Pacifique | Retenue : leçon du document indien |
| Suivi de tendance et gestion | Turtles, Kullamägi, P4-01 | **L'essai unique autorisé** : protection progressive des gains sur P4-01 |
| Méthodologie | Monte Carlo, gestion du risque | Intégrées au protocole, pas d'essai |
