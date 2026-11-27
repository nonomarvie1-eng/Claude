# Phase 7 — Audit des 8 documents

Les 8 PDF ont été lus intégralement : résumé français et transcription anglaise.

Notation : **[A]** affirmation de l'auteur, **[R]** résultat annoncé non vérifié, **[H]** mon interprétation, **[N]** résultat NEXUS indépendant.

## 0. Doublon Connors

`Larry_Connors_6_strategies(1).pdf` et le document de la phase 5 ont la **même empreinte SHA-256** (`e52aa4ff…`, 78 174 octets). C'est un **doublon exact**, déjà audité en phase 5 (`docs/phase5/01_audit_7_documents.md` §1). Aucune nouvelle analyse n'est nécessaire.

## 1. IBS — 3 stratégies (QQQ, XLP, SPY)

| Élément | Contenu |
|---|---|
| Formule | IBS = (C − L) / (H − L), journalier, entre 0 et 1 |
| A. QQQ, depuis 2000 | Achat **à la clôture** si IBS < 0,1 ; vente si IBS > 0,9. [R] 100 000 $ → ≈ 1,5 M$ en 2023 (> 12 %/an), investi 38 % du temps, +0,79 % par trade, 7 jours en moyenne, drawdown maximal 21 % (contre plus de 70 % en achat-conservation) |
| B. XLP, depuis 2000 | Moyenne de l'IBS sur 2 jours < 0,25 ; sortie si > 0,75. [R] 131 trades, 6,3 %/an, investi 33 % du temps |
| C. SPY, depuis 1993 | RSI(3) < 30 et IBS < 0,2 ; sortie si clôture > plus haut de la veille ou IBS > 0,9. [R] 9,6 %/an, investi 18 % du temps, drawdown maximal 23 %, +47 % en 2008, deux années perdantes (2001, 2018) |
| Logiciel | AmiBroker, journalier |
| Non précisé | Frais, glissement, filtre de tendance (aucun SMA 200), stop (aucun), dimensionnement (100 % implicite) |

**Biais et limites** :

- **L'exécution à la clôture est irréalisable telle quelle** : l'IBS n'est connu qu'après la clôture. Il faut acheter juste avant la clôture avec un IBS estimé, ou à l'ouverture suivante, ce qui change le résultat.
- Les 9 trades montrés en exemple sont choisis.
- Il n'y a ni stop ni coûts : un trade de 7 jours sans stop en 2008 ou 2020 peut perdre beaucoup.
- Résultats sur **ETF américains seulement**, à partir de 1993 ou 2000, publiés en 2023 : **pas de période hors échantillon** postérieure à la publication.

**Lien avec nos essais [N]** :

- même famille que H5 (repli acheté sur indice américain) ;
- le RSI 30/50 est significatif depuis 1993, mais perdant de 1940 à 1989 (phase 6).
- L'IBS est **un autre signal**, fondé sur le range intrajournalier. Il **n'a jamais été testé** chez nous, faute de plus haut et plus bas.

## 2. Williams %R — GBP/USD (Jared Goodwin)

| Élément | Contenu |
|---|---|
| Règles de base | %R(10) en M30 ; achat (ou couverture) si la clôture donne %R < −90 ; vente à découvert (ou sortie) si %R > −10 ; **entrée à l'ouverture de la bougie suivante** ; stop de 250 pips |
| Variantes | 1. Stop and reverse, toujours en position ; 2. Filtre horaire 17:00-minuit New York ; 3. Sortie en fin de séance (16:50-17:00 NY) ; 4. Filtre « veille forte pour acheter, veille faible pour vendre » ; 5. Filtre de la veille + sortie en fin de journée |
| [R] | 2008-2020. Trade moyen 25 $ (base) ; 29 $ (fin de journée) ; plus de 200 $ (filtre de la veille, plusieurs jours) ; 114 $ (filtre de la veille, journée) ; frais estimés de 20 à 30 $ ; toutes les années positives sauf 2016 |
| Non précisé | Taille de position derrière les montants en $ ; **définition de « veille forte ou faible »** ; maintien ou non du filtre horaire en versions 4 et 5 ; frais et spread réellement intégrés |

**Biais et limites** :

- Les filtres sont ajoutés **après avoir vu** les résultats : 5 versions successives, toutes sur la même période. Ce sont des **essais multiples non corrigés**.
- La règle décisive (filtre de la veille) n'est **pas définie**.
- Les montants en dollars n'ont pas de dénominateur.
- L'auteur dit lui-même : « ne pas appliquer ces réglages à d'autres marchés ou unités de temps ».

## 3. Retour à la moyenne crypto — Freqtrade (NEAR)

| Élément | Contenu |
|---|---|
| Indicateurs | Bollinger (SMA 20, ±2 σ) en H1 ; RSI en **H4** comme filtre de tendance ; ADX en H1 et H4 |
| Achat | RSI H4 > 55 **et** ADX H1 > 20 **et** ADX H4 > 25 **et** clôture H1 < bande basse ; entrée à la bougie suivante |
| Vente à découvert | RSI H4 < 45, mêmes conditions d'ADX, clôture > bande haute |
| Stop | Achat : « juste sous le plus bas de la bougie signal », puis « clôture de la bougie signal − 4,5 × ATR ». **Ambiguïté** : la transcription mentionne les deux. Vente : plus haut de la bougie signal + 4,5 × ATR |
| Sortie | Achat : clôture > bande haute ; vente : clôture < bande basse |
| Optimisation | hyperopt sur la période et l'écart-type des Bollinger, le seuil du RSI H4, les deux seuils d'ADX et le multiplicateur d'ATR. **Valeurs optimisées non publiées** (réservées aux soutiens payants) |
| [R] | NEAR perpétuel, 1 an, H1 : +179 % (marché −66 %), drawdown maximal 19,32 % |

**Biais** :

- Le +179 % inclut les **8 mois d'optimisation**. Seuls 4 mois sont hors échantillon, et leur résultat n'est pas isolé.
- Une seule paire, choisie par l'auteur.
- Paramètres finaux inconnus : la stratégie n'est **pas reproductible exactement**.
- Le marché à −66 % favorise une stratégie qui peut vendre à découvert.
- Pas de période ni de frais précisés.

## 4. Dimensionnement par la volatilité (ATR) — Trading 212

| Élément | Contenu |
|---|---|
| Méthode | ATR sur 21 jours (≈ 1 mois), en journalier ; taille = montant cible de variation quotidienne ÷ (ATR × valeur du point) |
| Exemple | Pétrole 100 barils × 1,71 $ = 171 $/jour ; or 171 / 10,31 ≈ 17 onces ; EUR/USD 171 / 0,00668 ≈ 25 600 |
| [A] | « Ce n'est pas une limite de perte : pour plafonner les pertes, il faut des stops » |

**Limites** :

- c'est une égalisation de la **variation moyenne**, pas du risque extrême ;
- l'ATR passé n'est pas l'ATR futur ;
- la conversion de devise est nécessaire hors USD ;
- le contenu est pédagogique, sans backtest.

**Étudié en `04_dimensionnement_ATR.md`.**

## 5. Nikkei 225 — biais du lundi (« Mr. Breakouts »)

| Élément | Contenu |
|---|---|
| Marché | Future Nikkei 225 en USD (CME), graphique 60 min, données jusqu'à **fin septembre 2025** |
| Observation | La séance principale (9:00-15:00 heure de Chicago) montre une dérive haussière ; **le lundi** est « très haussier depuis 5-6 ans », avec une courbe propre sur les 3 dernières années ; le mardi baisse sur 3 ans ; les autres jours sont irréguliers |
| [A] | « Argent presque gratuit » ; il faut un point d'entrée et des filtres (méthode payante) |
| Nature | **Un biais observé, pas une stratégie** : aucune règle d'entrée, de stop ni de coûts, aucun test statistique |

**Biais** :

- choix a posteriori du jour, de l'heure et de la période (3 ans « propres ») ;
- vidéo sponsorisée (Breakout OS) ;
- « argent gratuit » n'est pas un résultat.

**Contamination de nos périodes réservées** :

- les observations couvrent environ **2019-2025** ;
- cela inclut toute notre **validation (2023-07 → 2024-12)** et notre **test final jusqu'à 2025-09**.
- **Si une hypothèse « lundi Nikkei » était un jour testée, ces périodes ne seraient plus indépendantes pour elle** : l'hypothèse a été formée en regardant ces données.
- Je le consigne comme **contamination indirecte**.

## 6. Turnaround Tuesday (Quantified Strategies)

| Élément | Contenu |
|---|---|
| Règles | Achat le **lundi à la clôture** si la clôture < celle du vendredi ; sortie quand la clôture > plus haut de la veille, ou après 5 jours au plus |
| [R] | SPY depuis 1993 : 10,6 %/an contre 9,8 % en achat-conservation ; drawdown maximal 24 % (bref, sinon < 10 %) ; investi 24 % du temps ; rendement moyen du lundi au mardi ≈ 0,24 % quand le lundi est baissier (« 24 % » dans la transcription) |
| Limites | Exécution à la clôture du lundi ; pas de frais précisés ; version « améliorée » réservée aux abonnés ; effet calendaire connu depuis les années 1980 (effet lundi, French 1980), donc publié et potentiellement arbitré |

## 7. Or — « une bougie + Fibonacci »

| Élément | Contenu |
|---|---|
| Règles | Ordres stop à l'achat sur le plus haut et à la vente sur le plus bas **de la veille** ; stop à 10 % du range de la veille à l'intérieur du range ; objectif à 25 % du range au-delà (2,5 pour 1) ; un ordre déclenché annule l'autre ; annulation des deux à une heure limite (non précisée) |
| [R] | Or, 2020 → 2025, ticks réels, 1 % de risque : **profit factor 1,11, drawdown maximal 51,71 %**, gagnants 28 % (vente) et 35 % (achat). Mauvaise jusqu'à mi-2023 ; bonne ensuite |
| Optimisation | **243 combinaisons** (stop et objectif de 0,1 à 0,5, sens), sur **les mêmes données** ; retenues : 0,1/0,3 (drawdown ≈ 29 %) et 0,15/0,3 (courbe « préférée ») ; USD/JPY ré-optimisé à part |
| Biais | Sur-ajustement manifeste (243 combinaisons, choix visuel) ; tout le profit vient du régime haussier de l'or depuis 2023 ; le drawdown de 51,7 % au réglage d'origine est incompatible avec notre seuil de 10 % |

**Décision** : documentée seulement, non testée (consigne).

## 8. Synthèse des doublons avec nos 194 essais

| Document | Proche de | Nouveau ? |
|---|---|---|
| IBS | H5 (achat de repli sur indice US) | **Oui** : signal intrajournalier jamais testé (données manquantes) |
| Williams %R GBP/USD | Famille E (retour à la moyenne H1 et H4 sur BTC, rejetée) | Marché nouveau (forex), mais données et compatibilité bloquantes |
| Freqtrade (crypto) | E, P4-04 (RSI 2 cryptos, rejeté) | **Construction différente** : Bollinger + filtre de tendance RSI et ADX, plusieurs unités de temps. Partiellement nouveau |
| ATR | Phase 6 (dimensionnement) | Méthode de dimensionnement nouvelle |
| Lundi Nikkei, Turnaround Tuesday | — | Effets calendaires : **incompatibles avec Cubrik** |
| Or Fibonacci | Cassures (A, B, ORB) | Non prioritaire |
