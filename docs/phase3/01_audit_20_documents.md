# Phase 3 — Audit des 20 documents

Convention : **[DOC]** = écrit dans le document ; **[PROP]** = définition ou complément NEXUS ; **[TEST]** = ce que nous avons effectivement mesuré, avec le renvoi vers le résultat. Aucun exemple graphique n'est traité comme une preuve statistique : tous les exemples des documents sont choisis après coup, et plusieurs auteurs le reconnaissent (ORB, Ross Cameron).

Les 5 premiers documents ont été audités en phase 1 (`docs/phase1/01_audit_strategies.md`) ; ils sont résumés ici avec les résultats obtenus depuis. Les 15 nouveaux documents ont été lus intégralement (résumé français et transcription anglaise).

---

## A. Documents de la phase 1 (rappel)

| # | Document | Concepts | [TEST] et résultat |
|---|---|---|---|
| 1 | SBA — cassure du range asiatique | Range nocturne, cassure en clôture, stop EMA 50, TP en R, sortie horaire | REF-SBA-01 sur BTC M5 : incompatible (−0,15R net) |
| 2 | Day trading ICT (H4/M15/M5) | Swing 3 bougies, prise de liquidité H4, MSS, FVG, OB | Familles B (sweep + CHoCH) : rejetées sur BTC M5 ; EV-05, EV-08 (phase 3) |
| 3 | Day trading sans indicateur | Tendance H4, Fibonacci 0,705–1, OB, CHoCH M1 | Famille C (pullback) : rejetée |
| 4 | New York M1/M15 | CHoCH en clôture, FVG à 50 %, Fibonacci 50–61,8 %, 4R | Non testé (instrument non précisé ; coûts M1 prohibitifs sur BTC) |
| 5 | EMA 100 + Fibonacci | Biais EMA 100, OTE 0,618–0,786 | Règles absentes du document ; familles C et G (MA) testées |

---

## B. Les 15 nouveaux documents

### 6. Modèle Unicorn (breaker + FVG) — Nasdaq M1/M2

| Champ | Contenu |
|---|---|
| Concepts | FVG 3 bougies ; breaker (structure bas-haut-plus bas balayant-plus haut avec déplacement) ; Unicorn = FVG chevauchant le breaker ; draw on liquidity ; mean threshold |
| Règles exactes [DOC] | Breaker haussier : plus bas, plus haut, plus bas plus bas (prise des stops), plus haut plus haut avec déplacement ; bougie breaker = dernière bougie haussière avant le mouvement qui a fait le plus bas plus bas. Unicorn = FVG créé par le déplacement à travers le breaker, chevauchant ce breaker |
| Entrée | Retour du prix dans le FVG / breaker, en direction d'une liquidité repérée à l'avance (smooth highs, equal highs) |
| Sortie | Cible = liquidité visée ; option : projection de la jambe de manipulation (−2 à −2,5 écarts-types) |
| Invalidation | Clôture d'un corps au-delà du mean threshold des bougies du breaker ; pas de trade si la cible est atteinte avant le retour dans la zone [DOC, exemple 2] |
| Stop | Sous le plus bas du swing (≈ 2,3R dans l'exemple) ou juste sous le breaker et le FVG (≈ 5R) |
| UT / instruments / horaires | M1, M2 ; Nasdaq ; ouverture de New York (exemple 2) |
| Ambiguïtés | Choix de la liquidité visée ; « displacement » non quantifié ; choix entre les deux stops ; « smooth highs » |
| Affirmations non vérifiées | Résultats 2,3R et 2,14R : 2 exemples gagnants ; le PDF de 40 pages des auteurs cités n'est pas fourni |
| Données | Futures NQ M1 : non disponibles gratuitement et légalement (§ données) |
| Automatisation | Moyenne : structure codable avec des pivots confirmés [PROP] |
| Nouveauté vs NEXUS | Breaker et Unicorn sont nouveaux comme zones. Le reste (FVG, sweep) est déjà dans A, B et D |
| [TEST] | EV-11-UNICORN (BTC M5, transposition [PROP]) |

### 7. ICT Market Maker Models (MMSM / MMBM) — GBP/USD

| Champ | Contenu |
|---|---|
| Concepts | Consolidation originale, buy/sell side of the curve, first stage accumulation, second stage reaccumulation, distribution, redistribution, smart money reversal, balanced price range, rejection block, mitigation block, IFVG, kill zones, London close |
| Règles [DOC] | Délimiter la consolidation originale (niveau revenant sans cesse, bords lisses des corps) ; montée vers les relative equal highs jusqu'à une inefficience proche (FVG 60 min) ; corps dans le FVG, mèches au-delà ; puis short au CE du FVG 60 min, breaker baissier (1re distribution), OB baissier (2e redistribution = « unicorn ») ; objectif : bas de la consolidation originale (80 % de la position), puis relative equal lows |
| Horaires [DOC] | Retour dans la consolidation à l'ouverture de Londres ; montée jusqu'à 7 h NY ; kill zone 7 h–9 h NY ; cible atteinte au London close 10 h–12 h NY |
| Ambiguïtés | Très élevées : délimitation de la consolidation « un savoir-faire » [DOC] ; classification des étapes dépendante de l'expérience ; l'auteur dit lui-même que le modèle suppose « tous les PD arrays » et que les élèves le verront souvent après coup |
| Affirmations non vérifiées | « Les marchés ne montent que pour prendre des buy stops ou combler une inefficience » ; « algorithmes qui contrôlent le prix » ; aucune statistique |
| Automatisation | **Faible** : modèle composite et discrétionnaire, qui n'est pas réductible sans dizaines de paramètres |
| Nouveauté | Aucune règle testable nouvelle hors breaker, OB, FVG et kill zones (déjà couverts) |
| [TEST] | Non testé comme modèle (budget, surajustement) ; ses briques sont testées (EV-08, EV-11) |

### 8. SMT Divergence (ES / NQ)

| Champ | Contenu |
|---|---|
| Règles [DOC] | SMT baissière : un indice fait plus haut puis plus haut plus bas, l'autre plus haut plus haut ; signal baissier pour les deux. Haussière : inverse. **Valeur seulement au balayage d'un draw on liquidity de l'UT supérieure** ; ailleurs, « elles divergent tout le temps » [DOC]. Trader l'indice leader |
| UT | H4 pour le biais, M5 pour l'exécution |
| Ambiguïtés | Tolérance temporelle « au même moment » non définie ; quel swing comparer ; « draw on liquidity important » |
| Affirmations non vérifiées | « Peut dire le futur » ; aucune statistique |
| Données | ES/NQ non disponibles ; analogue BTC/ETH disponible (corrélation forte, mais autre marché [PROP]) |
| [TEST] | EV-14-SMT (BTC/ETH H1 ; tolérance ±2 h [PROP]) |

### 9. Draw on liquidity — PDH / PDL (Nasdaq)

| Champ | Contenu |
|---|---|
| Règles [DOC] | Sauf consolidation, le prix va chercher le PDH, le PDL ou les deux ; tendance haussière = PDH pris jour après jour ; absence de déplacement au-delà du PDH = biais baissier vers le PDL ; regarder 3 jours en arrière ; entrée sur une petite UT (FVG, box setup) |
| Invalidation | Pas de trade si la cible est déjà atteinte (jours 2 et 4 : PDH pris en Asie) [DOC] |
| Horaires | Schéma AMD : Asie/Londres consolidation, manipulation avant NY, distribution ; news 8 h 30 NY |
| Ambiguïtés | « Consolidation » non définie ; « déplacement » non quantifié |
| [TEST] | EV-01-PDHL (contact du PDH/PDL vs contrôles) ; vérification que la cible n'est pas déjà atteinte (niveau exclu s'il est déjà franchi) |

### 10. Arbitrage statistique — spread Apple / Microsoft

| Champ | Contenu |
|---|---|
| Règles [DOC] | Spread ajusté = A − (α + β·B) par régression linéaire ; opportunité quand le spread s'éloigne de sa moyenne ; mise en garde : stationnarité à tester (ADF) |
| Défauts [PROP] | Le code de la vidéo estime α et β **sur tout l'échantillon** (look-ahead) ; régression en niveaux de prix (régression fallacieuse si non cointégrés) ; aucun coût ni règle de sortie |
| Données | Actions : non disponibles ici ; analogue BTC/ETH |
| Contraintes | Spot : **vente à découvert impossible** → un spread neutre n'est pas exécutable sans dérivés ou emprunt |
| [TEST] | Diagnostic de cointégration roulante BTC/ETH (fenêtres passées uniquement) |

### 11. ICT Silver Bullet

| Champ | Contenu |
|---|---|
| Règles [DOC] | Fenêtres NY 03–04, 10–11, 14–15 ; FVG formé **dans** la fenêtre, entrée dans la fenêtre, trade conservable après ; direction du prochain draw on liquidity (PDH/PDL, extrêmes de session, PWH/PWL, NWOG, OTE, inefficience) ; cadre minimal 10 points (indices) / 15 pips (FX) ; corps qui respectent le FVG |
| Affirmations non vérifiées | « Se forme chaque jour », « extrêmement haute probabilité » : aucun chiffre ; l'auteur demande de backtester |
| [TEST] | EV-13 (FVG des fenêtres vs fenêtres de contrôle 05–06, 12–13, 16–17 NY), transposé sur BTC [PROP] |

### 12. ORB — breakout / pullback / continuation (S&P 500, 5 ans)

| Champ | Contenu |
|---|---|
| Règles [DOC] | Range = bougie 15 min de 9 h 30 NY ; cassure en clôture, entrée à l'ouverture suivante, stop de l'autre côté, 1,5R ; filtres : pas d'entrée après 12 h, range ni trop petit ni trop grand vs ATR. Variantes : pullback avec cassure ≥ 1 ATR puis reprise, ordre stop sur le haut du range, entrée au milieu |
| Résultats [DOC] | **Aucune variante pullback rentable** sur 5 ans ; 130 trades ; l'entrée au milieu est la pire ; les meilleures cassures ne reviennent pas → le retest sélectionne les cassures faibles |
| Intérêt | Document honnête : backtest, erreurs corrigées, exemples choisis après coup reconnus. Ses résultats restent non vérifiés (code non fourni) |
| [TEST] | EV-12-ORB (continuation après cassure du range 09:30–10:00 NY vs range de contrôle ; avec ou sans retest ; grande ou petite cassure) ; rappel : NXA-04 (retest) sans apport sur BTC M5 en phase 2 |

### 13. Order Flow Imbalance (BTC Binance)

| Champ | Contenu |
|---|---|
| Règles [DOC] | OFI normalisé sur N barres de volume = Σ(achat taker − vente taker)/Σ(volumes) ; barres de 1 BTC ≈ 6 s ; IC de Pearson 0,0597 et de Spearman 0,0778, t = 6,4 sur 2 jours ; backtest sans frais +6 174 pb ; avec frais taker 0,05 % ≈ −3 000 pb |
| Conclusion [DOC] | Prédictif mais **non rentable après frais** pour un particulier ; utile pour l'exécution (TWAP) |
| Données | Binance Vision fournit le volume acheteur taker par minute (klines) et les trades agrégés : volumes **réels** d'agresseurs. Le carnet L2 historique spot n'est pas fourni |
| [TEST] | Faisabilité uniquement (pas de stratégie à haute fréquence) : IC du déséquilibre taker par minute sur BTC dev |

### 14. ICT 2022 Mentorship — épisode 1

| Champ | Contenu |
|---|---|
| Règles [DOC] | Biais hebdo → liquidité daily (swings) → chasse aux stops 1 h / 15 min (relative equal highs) → cassure de structure 1–3 min → vente dans le FVG → cible : le plus proche sous le 50 % du range (« low-hanging fruit ») ; fenêtre 8 h 30–11 h NY |
| Ambiguïtés | Biais hebdo discrétionnaire (saisonnalité, Fed, « ton du marché ») ; un seul exemple, rétrospectif |
| Affirmations non vérifiées | « Un ATM qui se répète chaque semaine », « algorithme qui contrôle chaque tick » |
| Nouveauté | Séquence identique à NEXUS B + 50 % du range (premium/discount) |
| [TEST] | Briques : EV-05 (balayage de swing), EV-06 (equal highs), EV-08 (FVG) |

### 15. First Presented / Reflection FVG

| Champ | Contenu |
|---|---|
| Règles [DOC] | First presented FVG = premier FVG après 9 h 30 NY ; with displacement = premier FVG faisant partie d'un mouvement qui prend un plus haut ou un plus bas (prioritaire) ; reflection = premier FVG de sens opposé au first presented ; plus fort s'il se forme pendant une « macro » (ex. 10 h 01) |
| Contexte | Lendemain de jour férié : taille réduite (6 → 1 contrat) ; sortie au CE d'un « suspension block » 7 h–9 h |
| Ambiguïtés | Nombre de bougies pour « prendre un plus haut » ; « macro » ; seuil du CE à respecter |
| [TEST] | EV-10-FPFVG (with displacement [PROP : dépasse les extrêmes des 12 bougies précédentes] vs autres FVG du jour). Reflection FVG : non testé séparément (budget) |

### 16. ICT New Week Opening Gap (NWOG)

| Champ | Contenu |
|---|---|
| Règles [DOC] | NWOG = clôture du vendredi 16 h 59 NY → ouverture du dimanche 18 h NY ; variante RTH : clôture du vendredi → ouverture du lundi 9 h 30 ; CE = 50 % ; garder 4 à 5 NWOG ; le prix y revient (support/résistance) ; rester près de la NWOG = semaine de range |
| Données | **Inapplicable à BTC spot** : marché continu, sans fermeture de week-end, donc sans gap. Applicable aux futures et au Forex (non disponibles) |
| [TEST] | Aucun (non transposable) |

### 17. ICT One Trade Setup for Life

| Champ | Contenu |
|---|---|
| Règles [DOC] | Fenêtres NY : range PM de la veille 13 h 30–16 h (RTH), raid de Londres 2 h–5 h (ETH), opening range gap (clôture RTH → ouverture 9 h 30), lunch 12 h–13 h 30, session AM 9 h 30–12 h, macro 13 h 30 ; ordre de lecture PM → London → opening range 9 h 30–10 h → déplacement de 10 h → lunch → PM ; jours de discours de la Fed : attendre l'après-midi ; low-hanging fruit, partiels sur la liquidité ; comparer des marchés corrélés (Dow/NQ/ES, EUR/USD/GBP/USD/DXY) |
| Affirmations non vérifiées | « L'IA contrôle le prix », « le prix ne monte que pour deux raisons », gain de 9 362 $ sur un exemple |
| Données | Opening range gap : inapplicable à BTC (pas de séance RTH) |
| [TEST] | EV-03-LONDON, EV-04-PMRANGE (transposition BTC [PROP]) ; EV-12 (opening range) |

### 18. Ross Cameron (Warrior Trading) — analyse critique

| Champ | Contenu |
|---|---|
| Concepts | Momentum small caps, scanners (float < 100 M, volume relatif, catalyseur) ; règles de give-back (≈ 30 % du gain maximal) ; limite de perte journalière ; spirale après pertes (80 % de chances de doubler la perte au-delà du max) ; effet « chat room » |
| Règles testables | Aucune stratégie programmable fournie ; marché (micro caps US) hors de notre périmètre |
| Apport | **Gestion du risque** : limite journalière codée en dur (déjà en place), interdiction de « se refaire » (déjà en place : anti-martingale) ; un avantage réel peut ne pas être reproductible (effet d'audience) |
| [TEST] | Aucun ; confirme les règles déjà codées |

### 19. ICT Power of Three (AMD)

| Champ | Contenu |
|---|---|
| Règles [DOC] | Accumulation (range, souvent l'Asie) → manipulation (fausse cassure, souvent Londres, avec retour agressif dans le range) → distribution (souvent NY) ; OLHC / OHLC journalier ; entrée sur inversion FVG ou « box setup » ; cibles = projection de la manipulation à −2/−2,5 et −4/−4,5 écarts-types |
| Ambiguïtés | « Agressif » non quantifié ; consolidation repérée à partir de la manipulation (raisonnement rétrospectif admis par l'auteur) |
| Nouveauté | Doublon de NEXUS A/B (range asiatique et fausse cassure) déjà rejetés sur BTC M5 ; nouveau : IFVG comme entrée |
| [TEST] | EV-09-IFVG ; EV-03-LONDON |

### 20. Low / High Resistance Liquidity

| Champ | Contenu |
|---|---|
| Règles [DOC] | Failure swing = plus haut suivi d'un plus haut plus bas sans balayage → **LRL** (cible facile) ; balayage préalable → **HRL** (place du stop) ; viser la LRL, stop derrière la HRL ; biais daily : HRL sur les plus bas et failure swings sur les plus hauts → biais acheteur ; PDL balayé = HRL |
| Ambiguïtés | UT des swings ; « plus facilement » non quantifié |
| [TEST] | EV-07-LRL (contact des failure swings vs contrôles ; LRL vs HRL) |

---

## C. Doublons et chevauchements

| Concept | Documents | Familles NEXUS déjà testées |
|---|---|---|
| Fausse cassure / sweep / Judas swing | 2, 9, 14, 17, 19 | B (rejetée, BTC M5) |
| Cassure de range de session / opening range | 1, 12, 17, 19 | A (rejetée), REF-SBA (incompatible) |
| FVG / IFVG / OB / breaker | 2, 3, 4, 6, 7, 11, 14, 15, 19 | B-02 (CHoCH), D (FVG implicite) |
| Draw on liquidity (PDH/PDL, PWH/PWL, equal highs) | 6, 9, 11, 14, 17, 20 | — (nouveau en tant que test d'aimant) |
| Fenêtres horaires NY | 4, 11, 14, 15, 17 | A (sessions) |
| Biais hebdomadaire / daily | 9, 14, 17, 20 | G (filtre de tendance) |
| Corrélation entre marchés (SMT, triades) | 8, 17, 20 | — (nouveau) |
| Retour à la moyenne d'un spread | 10 | E (retour à la moyenne, rejeté) |
| Microstructure / coûts | 13 | Constat identique : les coûts dominent |
| Gestion du risque comportementale | 18 | Règles déjà codées |

Hypothèses **réellement nouvelles** retenues pour les études événementielles : aimant des niveaux (PDH/PDL, PWH/PWL, equal highs, LRL), réaction aux zones (FVG, IFVG, FPFVG, Unicorn), raids de sessions NY (Londres, range PM), fenêtres Silver Bullet, opening range NY et biais de sélection du retest, SMT BTC/ETH.
