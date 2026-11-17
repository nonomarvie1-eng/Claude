# Changelog

## FIRST-SERVE-02 — écran de chargement avec les assets fournis (2026-11-17)
- Stade de nuit, barre ivoire et champagne, balle de tennis fournis (WebP fidèles et PNG d'origine en secours), proportions conservées.
- Remplissage or champagne et balle qui suit la progression réelle ; à 100 % : rebond unique, son d'impact s'il est disponible, reflet sur la barre, fondu ; transition de 500 ms vers le jeu sur le même stade.
- Composition 9:16 conservée sur les écrans larges (stade flouté sur les côtés), zone logo réservée, pré-chargement HTML identique à la scène.
- Tests : intro 55/55 (54/54 sur le fichier publié), Return Spins 104/104.

## FIRST-SERVE-01 — chargement et entrée en jeu « The First Serve » (2026-11-16)
- Nouvelle scène de chargement PixiJS séparée (`render/intro.ts`) : stade nocturne réel, projecteurs qui s'allument avec la progression réelle, logo révélé sur un tableau d'affichage, barre de progression sur la ligne de fond avec la Balle d'or.
- Pré-chargement HTML avec le vrai fond de stade avant le script (aucun faux pourcentage) ; chargement en deux temps (orientation courante d'abord).
- Transition de 600 ms (rebond de la balle, tableau d'affichage → cadre des rouleaux, léger rapprochement de caméra), passable, fondu de 180 ms avec réduction des mouvements.
- Carte de fonctionnalité Golden Serve · Return Spins à la première visite (vrais symboles, texte exact, sans RTP ni gain maximal) ; accès direct ensuite ; disposition dédiée au téléphone en paysage.
- Son seulement après un geste ; connexion lente et erreur de chargement gérées.
- Script principal 965 → 617 Ko (fixtures de test retirées du jeu par un plugin Vite).
- `Loading.svelte` supprimé (remplacé par `Intro.svelte`). Mécaniques de bonus inchangées.
- Tests : e2e intro 50/50 (49/49 sur le fichier publié), Return Spins 104/104, vitest 39. Détails : docs/FIRST_SERVE_INTRO.md.

## Build de test RETURN-01 — GOLDEN SERVE : RETURN SPINS (2026-11-16, tranche verticale, crédits fictifs)
- Le bonus reste une slot : une Balle d'or frappe une zone (rouleaux 1-2, 3-4 ou 5-6) et seuls ces rouleaux sont relancés ; chaque arrêt est réévalué (15 625 façons) et payé, affiché séparément puis cumulé. Return Spins bornés (2 / 2 / 3), Golden Smash sur 4 rouleaux.
- Rally Challenge (8 tours) et Championship Night (12 tours) joués sur les rouleaux.
- Moteur Python + simulateur vectorisé + port TS (parité 163 tours) ; RTP mesuré 96,02 % [95,61 ; 96,43] (20 M tours).
- Animations dans la grille : révélation de la balle, service, retour (coup droit), smash, contour de zone, relance partielle, plaque par arrêt.
- Balle d'or refaite sans médaillon (asset temporaire). Outils de test réservés au développement (`VITE_DEV_TOOLS`), aucun résultat forcé en jeu normal.
- Championship Duel et prototypes précédents archivés (`VITE_GAMEPLAY`).
- Tests : pytest (dont 7 Return Spins), vitest 39 (+ gameplays archivés), e2e 104/104. Détails : docs/RETURN_SPINS.md.

## Build de test DUEL-01 — CHAMPIONSHIP DUEL (2026-11-16, prototype, crédits fictifs)
- Nouvelle direction : le bonus quitte les rouleaux pour une suite de points de tennis. 3 scatters → TIE-BREAK DUEL (4 points), 4+ → THE GRAND FINAL (6 points, Golden Smash, Golden Match Point).
- Modèle exact (convolution) : RTP 96,25 % ; Tie-Break 43,60×, Grand Final 110,14× ; contrôlé par Monte-Carlo et par énumération complète des tirages d'un point.
- Moteur Python + port TS (parité sur 368 fixtures) ; vue court 2,5D (PixiJS) : service, faute, double faute, ace, échange, coup gagnant, Golden Smash, Golden Match Point ; tableau d'affichage.
- Démo reproductible « double faute · ace · coup gagnant » (bouton TEST POINT, non crédité) et 7 scénarios d'un point, 2 tours complets forcés.
- Archivage : Rally Path, Cross-Court, Court Switch et Final Set conservés derrière `VITE_GAMEPLAY`, inaccessibles dans ce build ; branche locale `archive/bonus-prototypes-gs02`.
- Tweener : report du temps excédentaire entre interpolations enchaînées (pas de perte d'une image par étape).
- Tests : pytest 74/74, vitest 36 (+36/36/38 gameplays archivés), e2e 35/35 (preview et fichier publié). Détails : docs/CHAMPIONSHIP_DUEL.md.

## Build de test GOLDEN-SERVE-02 (2026-11-16, prototypes, crédits fictifs)
- Deux prototypes de bonus jouables dans le vrai jeu : **A Cross-Court** (la balle transforme les cases touchées en un symbole cible) et **B Court Switch** (les cases touchées s'échangent de part et d'autre du filet), choix dans les Réglages ; Golden Smash (bande de 2 rangées) et Double Serve.
- Moteur Python de référence + simulateur vectorisé (égalité testée tirage par tirage) + port TS (parité exacte). A : RTP 96,75 % [96,40 ; 97,11] sur 20 M tours ; B : 64,4 % aux mêmes réglages → **A recommandé**.
- Animation signature dans PixiJS : révélation de la Balle d'or, raquette, lancer, frappe, rebonds sur les cases calculées, transformation/échange, Smash avec tremblement contrôlé, Championship Point (≥ 50×) en tableau d'affichage.
- Stabilisation : `resetRound()` central (plus aucun bandeau, plaque, trajectoire ou effet d'un tour précédent), grille finale forcée sur celle du moteur, stockage séparé par gameplay, libellés du panneau de bonus.
- Anciens gameplays conservés : `VITE_GAMEPLAY=rallypath` / `finalset`.
- Tests : pytest 64/64, vitest 33 (+ 33 Rally Path, 35 Final Set), e2e 68/68 (preview et fichier publié). Détails : docs/GOLDEN_SERVE_PROTOTYPES.md.

## Prototype RALLY PATH — Championship Night (2026-11-16, expérimental, non publié dans les modes Stake)
- Nouvelle mécanique **Rally Path** : la Balle d'or (rouleau 1, ni Wild ni Scatter) sert, les raquettes renvoient (même rangée ou ±1), 1 seul chemin par tour, le plus long, départage déterministe ; récompenses 2/8/30/100× ; 6 coups = **Championship Shot** (table documentée 150–4 000×, moyenne 455,5×).
- Bonus prototypes : Rally Challenge 8 tours, The Grand Final 12 tours + Second Serve (une fois).
- Maths exactes (propagation des rangées atteignables) + simulation 10 M tours / 400 k bonus (graine 2026) : RTP prototype 96,18 % exact, 96,09 % simulé [95,16 ; 97,02].
- Constat : Second Serve déclenché dans 91,2 % des Grand Final → variante « dernière balle » (18,3 %) proposée, non appliquée.
- Port TS en parité exacte ; **Labo Rally Path** dans la démo (Réglages) avec 8 scénarios reproductibles, sans débit ni crédit.
- Animations courtes : révélation 0,3 s, trajet ≤ 1,1 s, Championship Shot ≈ 2,5 s, Second Serve 1,1 s, accélérables sans changer le résultat.
- Asset temporaire `sym_G` (Balle d'or recolorée) — à remplacer.
- Tests : pytest 51/51 (dont 17 Rally Path), vitest 29/29, svelte-check 0 erreur, e2e labo 98/98. Détails : docs/RALLY_PATH_PROTOTYPE.md.

## v6 — THE FINAL SET — game 3.0.0 / math 4.0.0 (2026-11-16)

### Mathématiques
- Bonus entièrement remplacés : plus de tours gratuits ni de multiplicateur. **Court Control** (6 zones), **Power Shots** (Rally, ACE, Smash, Passing Shot, Amortie, Golden Rally), marques de terrain avec durée, **Grand Slam**, **Hawk-Eye** IN/OUT et **Championship Point** (Grand Final).
- 3 scatters → RALLY CHALLENGE (8 échanges) ; 4+ → THE GRAND FINAL (12/14/16 échanges).
- Moteur scalaire (événements) + vectorisé (simulation) consommant les mêmes tirages ; parité testée ; port TypeScript identique.
- Modes : `buy_rally` 48,8×, `buy_final` 106,8× (renommés), Bonus Chance 1,4× ; RTP 96,46–96,56 %.
- Méthode : jeu de base exact, bonus mesurés par simulation ciblée (8 M / 6 M / 2 M), erreur standard publiée. Un premier échantillon de 2 M avait donné une valeur basse : détecté en recoupant avec les simulations complètes (écart d'environ 3 σ) ; précision augmentée et prix corrigé de 48,7× à 48,8×.
- Correction d'un bug du simulateur (variable écrasée) qui faussait le RTP affiché par la simulation (pas les fichiers Stake).
- Export Stake 4 modes ; vérificateur officiel : 0 problème.

### Jeu
- Directeur de match (`render/match.ts`) : court et zones sur la grille, valeur de chaque zone, marques avec compteur, balle avec hauteur, ombre et traînée, trajectoire propre à chaque coup, caméra (zoom, suivi, tremblement), sous-titres de retransmission.
- Hawk-Eye : son coupé, image désaturée, reconstruction au ras du sol, ralenti, verdict du moteur ; Championship Point ; Grand Slam.
- Intros : Rally Challenge (bleu électrique) et Grand Final (vue aérienne, projecteurs, public, tableau). Récapitulatif, et cérémonies uniquement au-dessus des seuils publiés (75× / 200×).
- Tap = avance rapide (le résultat ne change pas) ; mouvements réduits sans caméra.
- Page d'informations : table des coups avec probabilités, valeurs « court », règles des marques, Hawk-Eye, Championship Point, cérémonies.

### Tests
- pytest 34/34, vitest 25/25, svelte-check 0 erreur, e2e 165/165.

## v5 — game 2.0.0 / math 3.0.0 (2026-11-16)

### Mathématiques (refonte complète, recalculée)
- 11 symboles (W, S, H1–H4, L1–L5) : suppression de l'ancien H5 ; nouvelle table de gains et nouvelle composition des rouleaux.
- Symboles empilés (blocs de 1 à 3) : fréquence de gain 67 % → 27,9 %.
- Deux niveaux de bonus : TIE-BREAK (3 scatters, 9 tours, ×1) et SUPER TIE-BREAK (4/5/6 scatters, 12/15/20 tours, ×2).
- Quatre modes Stake : `base` 1×, `bonus_chance` 1,4×, `buy_tiebreak` 49,4×, `buy_super` 105× ; RTP 96,41–96,52 % après plafond.
- Le calcul exact intègre désormais l'effet du plafond 5 000× (mesuré par simulation ciblée, erreur standard publiée). Sans cette correction, l'achat Super aurait été annoncé à 97,4 % au lieu de 96,4 %.
- Correction : probabilité « atteindre ×20 » (le dernier tour n'était pas compté).
- Export Stake généralisé aux 4 modes ; vérificateur officiel : 0 problème.
- Ancien achat unique 100× (tirage 3/4 scatters) supprimé.

### Jeu
- Nouveau pack de 11 symboles colorés (originaux conservés), taille uniforme, sans cadre commun.
- Connexions gagnantes lisibles : cadres colorés, tracé du rouleau 1 au dernier rouleau, comptes par rouleau, étiquette détaillée, présentation successive puis globale, bouton « Revoir les gains ».
- Fenêtre « Modes de jeu et achats » : 4 cartes (Normal, Bonus Chance, Achat Tie-Break, Achat Super Tie-Break), confirmation avec le montant exact ; prix du prochain tour affiché dans le HUD.
- Super Tie-Break : introduction dédiée, ambiance bleu électrique / or blanc, cadre lumineux bleu, panneau dédié, entrée spécifique d'Ace, récapitulatif.
- Ace : le symbole H1 du pack sert aussi de mascotte animée.
- Page d'informations refaite : 11 symboles, connexions, bonus, achats, Bonus Chance, RTP par mode.

### Tests
- pytest 29/29, vitest 24/24, svelte-check 0 erreur, e2e 161/161 (9 formats d'écran).

## v4 — refonte premium (2026-11-16)
Pack de 15 symboles, palette nuit, HUD sans chevauchement, écran d'accueil, Ace, Tie-Break distinct. Voir l'historique Git.
