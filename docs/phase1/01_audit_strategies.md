# 01 — Audit comparatif des cinq stratégies

Convention utilisée dans tout ce dossier :

- **[DOC]** = règle explicitement présente dans le document fourni.
- **[PROP]** = proposition NEXUS (absente du document, ajoutée pour rendre la règle calculable).
- **[MANQUE]** = paramètre absent ou contradictoire, non complété par supposition dans la version « référence ».

Aucune performance annoncée par les vidéastes n'est retenue comme preuve. Elles sont citées uniquement pour signaler des incohérences.

---

## 1. SBA — Cassure du range asiatique

| Élément | Contenu |
|---|---|
| Entrée | [DOC] Range asiatique = plus haut / plus bas de 00:00 à 09:00 (fuseau non précisé). Fenêtre d'entrée 09:00–13:00. Achat sur **clôture** de bougie au-dessus du plus haut, vente sur clôture sous le plus bas (une mèche ne suffit pas). Exécution au marché après la clôture. Sens autorisé par actif (ex. USD/JPY achat seul, EUR/CHF vente seule). |
| Sortie | [DOC] SL « sous l'EMA 50 » (achat) / au-dessus (vente). TP = multiple fixe du risque (2R, 4R, 6R selon l'actif). Clôture forcée à 20:00. Break-even sur certains actifs après un multiple de R confirmé en clôture (USD/JPY 3R ou 3,2R). |
| Indicateurs | EMA 50 sur l'unité de temps de trading. |
| Unités de temps | [DOC] M5 (USD/JPY), M10 (EUR/CHF), M15 (DAX) ; autres non précisées. |
| Marché recherché | Consolidation asiatique suivie d'une impulsion à l'ouverture européenne. |
| Risque | [DOC] Taille calculée depuis capital, risque et distance du stop. Le document lui-même montre que 27 pertes à 1 % ≈ −23,8 % (vérifié : 1 − 0,99²⁷ = 0,2377). |
| Subjectif | Peu : c'est la plus mécanique des cinq. Restent l'exclusion « news » (délai non défini) et la distance de sécurité derrière l'EMA. |
| Contradictions / manques | Fuseau horaire et DST non spécifiés ; exemple DAX conservé overnight alors que la sortie est à 20:00 ; BE USD/JPY 3R vs 3,2R ; résultat +2,75R vs +0,75R ; TP 6R dans le tableau vs « 2R ou 4R » dans le texte ; date DAX 1er avril vs 19 septembre ; tableau de paramètres original absent ; nombre d'entrées par jour non défini (une seule ? les deux sens ?). **Cas non traité : si l'EMA 50 est du mauvais côté du prix d'entrée** (ex. cassure haussière alors que l'EMA 50 est au-dessus), le stop est indéfini. Distance stop–EMA potentiellement minuscule (coûts énormes en R) ou énorme. |
| Automatisation | Facile, sous réserve de trancher le fuseau (hypothèse [PROP] : Europe/Paris, vidéo francophone) et le cas « EMA du mauvais côté » (skip le trade). |
| Surajustement | **Élevé** : filtres par jour de la semaine et par mois exclus, sens unique, TP et BE différents par actif = de nombreux degrés de liberté choisis sur 2002–2025. Un filtre « mois exclus » choisi a posteriori est un cas d'école de data snooping. La version de référence testera **avec et sans** ces filtres. |

## 2. Day trading ICT (H4 · M15 · M5)

| Élément | Contenu |
|---|---|
| Entrée | [DOC] 1) En H4, prise de liquidité d'un Swing High (ou Low) puis rejet. 2) En M15/M5, Market Structure Shift (prise d'un plus bas récent). 3) Retour dans un FVG (SIBI en vente / BISI en achat), idéalement face à un Order Block, en zone Premium/OTE. Entrée « à l'entrée du SIBI » ou ordre limite sur l'OB. |
| Sortie | [DOC] SL derrière l'Order Block / « derrière toutes les mèches » avec marge. TP sur la liquidité opposée « évidente » (Sell Side Liquidity), clôture le jour même. RR cités 2,81 et 3. |
| Indicateurs | Aucun indicateur classique : swings fractals, FVG, OB, IFVG, Premium/Discount, OTE. |
| Unités de temps | H4 (contexte), M15 ou M5 (exécution). |
| Marché recherché | Retournement après chasse aux stops sur un extrême H4. |
| Risque | [MANQUE] Aucun % de risque, aucune limite journalière. |
| Subjectif | **Très élevé** : « liquidité importante », « Low Resistance Liquidity », trendlines, « dernier FVG en face d'un OB », « laisser respirer le stop », choix du TP « évident », choix M5 vs M15. |
| Contradictions / manques | [DOC] Swing = fractal 3 bougies (mèches) : c'est le seul concept précisément défini. Non définis : quel swing H4 (le plus récent ? un « grand niveau » ?), amplitude/temps de la prise de liquidité, MSS en clôture ou en mèche, fenêtre de temps entre prise H4 et MSS, choix du FVG, définition de l'OB, déplacement (« displacement »), règle de re-entrée (« enchaîner les ventes »). « Pas besoin de kill zones » contredit implicitement la contrainte intraday. |
| Automatisation | Moyenne à difficile : tout est formalisable mais **chaque concept introduit 1 à 3 paramètres libres**, ce qui gonfle l'espace de recherche. |
| Surajustement | Élevé, par la combinatoire des confluences. Les exemples sont choisis a posteriori (biais de sélection évident : deux exemples gagnants). |

## 3. Day trading sans indicateur

| Élément | Contenu |
|---|---|
| Entrée | [DOC] Tendance H4 par structure (HH/HL + dernier BOS). Fibonacci du dernier swing low ayant créé le dernier HH. Zone d'entrée 0,705–1 (OTE 0,618–0,786, préférence pour la partie profonde). Zone institutionnelle par ordre de préférence : OB, BPR, Breaker, FVG. Entrée limite à 50 % de l'OB ou au début de l'OB. Option : confirmation CHoCH en M1 puis OB M1. Variante momentum : M30 → M15 → M5, sweep d'Equal Lows, BOS, retracement. |
| Sortie | [DOC] SL sous le niveau 1 (swing low d'origine) ; invalidation si le niveau 1 casse. TP au niveau 0 (dernier sommet). Gestion : BE à 1R ou 1,5R, ou 50 % partiel puis le reste au BOS. |
| Indicateurs | Fibonacci, structure, OB/BPR/Breaker/FVG. |
| Unités de temps | H4 (biais + zone), M1–M15 (timing), fallback H3/H2/H1/M45/M30. |
| Marché recherché | Retracement profond dans une tendance établie. |
| Risque | [DOC] RR minimum 2. [DOC] Pas de trading 30 min avant et après NFP, CPI, décisions de taux — **seule règle news chiffrée des cinq documents**. |
| Subjectif | Élevé : identification de l'OB, choix de la timeframe de repli, trendlines, Equal Highs. |
| Contradictions / manques | Présentée comme du day trading mais SL/TP H4 impliquent des durées de plusieurs jours ; aucune durée maximale. Les RR annoncés (15, 19, 22, 67) sont mécaniquement dus à des entrées très profondes : ils ne disent rien de la probabilité de déclenchement ni de réussite. La liste de timeframes de repli est une source majeure de comparaisons multiples cachées. BPR et Breaker non définis. |
| Automatisation | Moyenne : la version « H4 Fibonacci + entrée limite 0,705/0,786 + SL niveau 1 + TP niveau 0 » est entièrement définissable. |
| Surajustement | Moyen si on fige une seule timeframe et un seul niveau d'entrée ; élevé sinon. |

## 4. New York M1/M15

| Élément | Contenu |
|---|---|
| Entrée | [DOC] Après 09:30 America/New_York. Tendance M1 (HH/HL, LH/LL). CHoCH confirmé en **clôture**. FVG dans le nouveau sens (définition 3 bougies explicite et correcte). Fibonacci sur l'impulsion du CHoCH, confluence FVG ∩ zone 50–61,8 %. Entrée limite au milieu (50 %) du FVG. Confluence optionnelle : FVG M15 des 1–2 derniers jours (POI), « Liquidity Inflection Level » retesté. |
| Sortie | [DOC] SL au-delà de la bougie ayant formé le FVG ou d'un niveau structurel. TP initial 4R minimum. BE après clôture au-delà du sommet/creux de référence. Prises partielles non détaillées. |
| Indicateurs | Indicateur « IT Foundation » (sessions) et indicateur propriétaire non fournis ; le modèle public n'en dépend pas selon l'auteur. |
| Unités de temps | M1 exécution, M15 contexte. |
| Marché recherché | Premier retracement d'une nouvelle tendance intraday à l'ouverture US. |
| Risque | [DOC] Risque fixe par trade (2 000 $ / 150 $ dans les exemples). |
| Subjectif | Moyen : « dernier Higher Low pertinent », « niveau structurel pertinent ». |
| Contradictions / manques | **Instrument non précisé.** Fin de fenêtre de trading non précisée. Erreur arithmétique documentée (2 × −1R + 8R à 150 $ = 900 $, pas 600 $). Un win rate de 42 % à ≥ 4R impliquerait une espérance ≈ +1,1R/trade : niveau extraordinaire, incompatible avec un marché liquide sur la durée sans preuve auditée. |
| Automatisation | Bonne pour le cœur (CHoCH clôture + FVG + Fib + limite 50 %). |
| Surajustement | Moyen. **Risque principal : les coûts.** Sur M1, les stops sont de l'ordre de quelques pips/points ; spread + commission + slippage peuvent représenter 0,1 à 0,4R par trade (voir `06_ressources_couts.md`). |

## 5. EMA 100 + Fibonacci (Casper, pédagogique)

| Élément | Contenu |
|---|---|
| Entrée | [DOC] Biais acheteur si prix > EMA 100, vendeur sinon. Fibonacci du dernier creux au sommet (tendance haussière). Zone OTE 0,618–0,786. [MANQUE] Aucune règle d'entrée précise. |
| Sortie | [MANQUE] Le document indique lui-même qu'aucune règle systématique de SL/TP n'est fournie. |
| Indicateurs | EMA 100, Fibonacci. |
| Unités de temps | [MANQUE] Non précisées (exemples sur XAU/USD ; préférence scalping M1/M5). |
| Risque | [DOC] Notions de RR et de seuil de rentabilité 1/(1+RR) — **correct**, et utile : c'est le point mort de toute stratégie à RR fixe. |
| Subjectif | Total pour l'exécution. |
| Automatisation | Uniquement via des règles [PROP] (voir `03_strategies_candidates.md`, S5). |
| Surajustement | Faible en soi, mais la stratégie n'existe pas encore : toute règle ajoutée est la nôtre. Le document recommande d'ailleurs un test hors-échantillon : c'est la bonne démarche. |

---

## 6. Synthèse comparative

| Critère | SBA | ICT | Sans indicateur | NY M1/M15 | EMA100+Fib |
|---|---|---|---|---|---|
| Règles mécaniques présentes | ●●●●○ | ●●○○○ | ●●●○○ | ●●●○○ | ●○○○○ |
| Paramètres manquants | Fuseau, stop EMA | Presque tous | OB, durée | Instrument, fenêtre | Entrée/SL/TP |
| Degrés de liberté (risque snooping) | Élevé (filtres jour/mois) | Très élevé | Élevé (timeframes) | Moyen | Faible / indéfini |
| Sensibilité aux coûts | Moyenne (stop EMA variable) | Moyenne (M5) | Faible (H4) | **Très forte (M1)** | Dépend de l'UT |
| Nombre de trades attendu | ~1/jour/actif max | Rare | Rare (H4) | Plusieurs/jour | Variable |
| Testable en référence | Oui | Partiellement | Oui (version figée) | Oui | Non sans [PROP] |

### Mécanismes communs réellement extractibles

Une fois le vocabulaire retiré, les cinq méthodes reposent sur **quatre primitives** seulement :

1. **Points pivots** (swing high/low) et l'état de structure qu'ils définissent.
2. **Cassure d'un niveau** (range, swing) : en clôture ou en mèche.
3. **Échec de cassure** (sweep / fausse cassure) : franchissement puis réintégration.
4. **Retracement** vers une zone (Fibonacci, FVG, OB, EMA, niveau cassé = retest).

Plus deux couches de contexte : **la session/l'heure** (Asie, Londres, New York) et **un filtre directionnel** (EMA, structure HTF).

C'est sur ces primitives que portera la recherche : elles sont peu nombreuses, définissables sans ambiguïté et permettent des tests d'ablation propres.

### Observation statistique préalable importante

Avec un SL et un TP fixes en multiples de R, une entrée **aléatoire** sur une marche aléatoire touche le TP avec une probabilité ≈ 1/(1+RR) : espérance brute ≈ 0, **nette négative** du fait des coûts. Un win rate de 46 % (SBA AUD/JPY) ou 42 % (NY) n'a donc de sens qu'en le comparant à 1/(1+RR) pour le RR effectivement utilisé, **après coûts**. Chaque stratégie sera comparée à un modèle d'entrées aléatoires appariées (même heure, même SL/TP).
