# GOLDEN RALLY — Golden Serve : audit, prototypes A/B, animation signature

Build de test : **GOLDEN-SERVE-02** (démo, crédits fictifs). Statut : **prototype**. Les mathématiques ne sont pas définitives et aucun achat n'est activé.

## Phase 1 — Stabilisation (audit)

### Sauvegarde
- Branche locale `backup/before-golden-serve` (commit `a95e322`, build RALLY-PATH-01). Branches antérieures : `backup/before-final-set`, `backup/before-championship-night`, `backup/before-v5-modes`.
- Aucun ancien gameplay n'est supprimé. Le build est choisi par `VITE_GAMEPLAY` :
  - `goldenserve` (défaut) → GOLDEN-SERVE-02 ;
  - `rallypath` → RALLY-PATH-01 ;
  - `finalset` → v6.
- Tests correspondants : `npm test`, `npm run test:rallypath`, `npm run test:finalset`.

### Chaîne réelle (point d'entrée → résultat → affichage)
`index.html` → `main.ts` → `App.svelte` → `Controller.spin()` → `DemoRgs.play()` → moteur (`goldenServe.ts`) → livre d'événements → `playBook()` (`player.ts`) → `RallyScene` (PixiJS).

Le moteur fixe tout le résultat avant l'animation : grille, coup, trajectoire, cases touchées, grille transformée et gains.

### Mécaniques présentes dans le code
| Mécanique | Fichiers | Statut |
|---|---|---|
| v6 THE FINAL SET (Hawk-Eye, Power Shots, marques, Championship Point v6) | `engine/bonus.ts`, `render/match.ts` | conservée, inaccessible dans ce build |
| Rally Path | `engine/rallyPath.ts`, `math/rally_math/rally_path.py` | conservée, inaccessible dans ce build |
| Golden Serve A / B | `engine/goldenServe.ts`, `math/rally_math/golden_serve.py` | **actif** |
| Achats, Bonus Chance | `ui/BuyBonus.svelte`, modes Stake | masqués et refusés côté serveur de démo (prix non vérifiés pour ce gameplay) |

### Bugs d'affichage corrigés
- **Éléments restant affichés après un tour** : `RallyScene.resetRound()` est appelé au début de chaque tour et de chaque rejeu. Il vide les surimpressions, les effets, les plaques, les trajectoires, l'état « événement », le tremblement du plateau et les compteurs d'accélération.
  - Le test e2e le vérifie à chaque lancement : `overlay 0, gsLayer 0, rpPlate false, fx 0`.
- **Grille incohérente après une animation interrompue** : à la fin de chaque coup, toutes les cases sont forcées sur la grille publiée par le moteur. Un test vérifie que la grille affichée est égale à la grille du moteur, y compris après accélération par toucher.
- **Double célébration** : Championship Point remplace le grand écran « méga gain » et n'apparaît qu'à partir de 50 fois la mise.
- **Stockage** : clés séparées par gameplay (`golden-rally-demo-gs02`, `golden-rally-history-gs02`). Une partie d'un autre gameplay ne peut plus être reprise.

## Phase 2 — Les deux prototypes

### Règles communes
- **Balle d'or (G)** : uniquement sur le rouleau 1. Ni Wild ni Scatter : elle ne paie rien et ne remplace aucun symbole. Si plusieurs apparaissent, la plus haute sert.
- Chaque tour tire, après ses 6 arrêts, un vecteur de service : `[rangée d'arrivée /5, cible /1000, coup spécial /1000, rangée 2 /5]`. Ce tirage a lieu même sans Balle d'or, ce qui permet un rejeu exact et la parité Python/TS.
- **Trajectoire** : ligne droite de (rouleau 1, rangée r0) à (rouleau 6, rangée d'arrivée). Sur le rouleau i, la rangée est `floor(r0 + (rt − r0)·i/5 + 0,5)`. Le résultat est une case par rouleau, sans saut de plus d'une rangée.
- **Golden Smash** : la trajectoire touche une bande de 2 rangées. Fréquence : 0,5 % des services en jeu de base, 4 % en Rally Challenge, 10 % en Grand Final.
- **Double Serve** : un second service part du même serveur vers une autre rangée. Fréquence : 6 % en Rally Challenge, 15 % en Grand Final.
- Les Wilds et Scatters touchés ne changent pas. Les gains en façons sont calculés sur la grille **après** le coup. Le plafond est de 5 000×.
- **Bonus** :
  - 3 scatters → Rally Challenge, 8 tours ;
  - 4 scatters ou plus → The Grand Final, 12 tours, cibles plus prestigieuses, Smash et Double Serve plus fréquents ;
  - pas de redéclenchement, pas de gain minimum.

### A — CROSS-COURT (transformation)
Les cases touchées et la Balle d'or deviennent le symbole cible tiré par le moteur. Tables de cibles par phase : voir `config.GOLDEN_SERVE_PROTO["TARGET_W"]`.

### B — COURT SWITCH (échange)
Les cases touchées s'échangent de part et d'autre du filet : rouleau 2 ↔ 5 et rouleau 3 ↔ 6, pour chaque trajectoire. La case de la Balle d'or prend le symbole renvoyé par le rouleau 4. Aucun symbole n'est créé.

### Mesures (simulation reproductible, `math/reports/golden_serve_sim.json`)
Paramètres identiques pour A et B : mêmes rouleaux, même fréquence de Balle d'or, mêmes tirages. A et B ne diffèrent que par la règle appliquée.

| | A Cross-Court | B Court Switch |
|---|---|---|
| Tours simulés (graine) | 20 M (2026) | 10 M (2027) |
| RTP | **96,75 %** [96,40 ; 97,11] | 64,43 % [64,16 ; 64,70] |
| Écart-type par tour | 8,06× | 4,41× |
| Fréquence de gain | 28,9 % | 25,9 % |
| Balle d'or en jeu de base | 1 tour sur 20,2 | 1 tour sur 20,1 |
| Valeur d'un tour avec / sans balle | 4,19× / 0,55× | 1,07× / 0,55× |
| Rally Challenge : moyenne [IC 95 %] | 30,2× [30,0 ; 30,4] | 7,7× |
| Rally Challenge : médiane / P(< 10×) / P(≥ 100×) | 13,8× / 38,9 % / 5,4 % | 3,4× / 81,4 % / 0,5 % |
| Grand Final : moyenne [IC 95 %] | 92,3× [91,8 ; 92,7] | 11,6× |
| Grand Final : médiane / P(≥ 100×) / P(≥ 1 000×) | 43,9× / 25,8 % / 0,4 % | 5,9× / 0,9 % / 0 % |
| Gain maximal observé | 5 000× (plafond) | 2 888× |

Tests : `math/tests/test_golden_serve.py` (11 tests).
- Règles de trajectoire et tables.
- A : seules les cases touchées sont transformées.
- B : les rouleaux 2 à 6 conservent exactement leurs symboles.
- Moteur scalaire égal au moteur vectorisé, tirage par tirage.
- Gains égaux à l'évaluation de la grille publiée.
- Comptabilité exacte et rejeu exact.
- Niveau de bonus selon le nombre de scatters.
- Jeu normal non modifié.

## Phase 3 — Animation signature (dans le jeu)

Tout est implémenté dans `render/scene.ts`, section GOLDEN SERVE (PixiJS : interpolations et courbes, sans vidéo). Durées mesurées en mode normal, hors présentation des gains.

| Étape | Rendu | Durée |
|---|---|---|
| A. Révélation | Rotation courte, halo doré, la balle s'élève de 12 px, les autres cases sont assombries à 55 %, son dédié | 0,4 s |
| B. Préparation | La raquette (même famille graphique que le symbole raquette) entre près du serveur | 0,22 s |
| B. Lancer | La balle monte au niveau du cordage, la raquette arme son geste | 0,24 s |
| B. Frappe | Rotation accélérée de la raquette, son net, anneau d'impact | 0,11 s |
| B. Trajectoire | Rebonds en arc avec ombre portée et traînée dorée ; anneau et son à chaque case touchée | 0,135 s par case |
| B. Transformation (A) | Retournement de la case vers le symbole cible au moment de l'impact | — |
| B. Échange (B) | Les deux symboles se croisent en arc au-dessus du filet | 0,42 s |
| C. Golden Smash | Raquette haute, court arrêt avant la frappe (son de vent), balle rapide sur deux rangées en même temps, tremblement contrôlé du plateau, la mascotte dit « SMASH ! » | — |
| Double Serve | Second geste de raquette plus court, seconde trajectoire | — |
| E. Championship Point | Seulement à partir de 50× : tableau d'affichage nuit et or, compteur, réaction du public ; léger zoom au-dessus de 200× ; sans pluie d'étoiles | 1,9 à 3,5 s |

Au total, un service de base sans gain dure environ 1,5 à 2 s, un smash environ 2 à 2,5 s.

Comportements transverses :
- **Mode rapide** : tout est accéléré ×1,8. **Toucher l'écran** accélère ×5 sans changer le résultat.
- **Réduction des mouvements** : pas de rotation, d'arc, de tremblement ni de zoom ; durées courtes.
- **Hawk-Eye (D)** : **non retenu**. Dans ce gameplay, aucun verdict IN/OUT n'aurait de conséquence réglementaire, et le cahier des charges interdit de le garder comme décor.

### Critères d'acceptation (e2e `game/e2e/golden-serve-e2e.mjs`, 390×844)
Voir `game/e2e/golden-serve-report.json` :
1. La Balle d'or déclenche le coup.
2. Un geste de raquette est joué.
3. La balle rebondit sur chaque case calculée.
4. La grille affichée est égale à la grille du moteur.
5. Chaque transformation est animée.
6. Les gains sont calculés sur la grille transformée et le montant affiché égale le paiement.
7. L'animation se termine proprement.
8. Le tour suivant démarre normalement.
9. Les écrans 320×568, iPhone SE, 390×844 et 1440×900 sont vérifiés en Chromium émulé.
10. Rien ne reste affiché au tour suivant.

## Phase 4 — Choix de la mécanique (recommandation)

**Retenir A — Cross-Court.**

| Critère | A Cross-Court | B Court Switch |
|---|---|---|
| Simplicité | Une règle : « la balle transforme ce qu'elle touche » | Paires d'échange à suivre des yeux |
| Effet réel sur le jeu | +3,6× par service en moyenne : les combinaisons apparaissent visiblement | +0,5× : souvent aucun gain créé (0× sur le scénario de service) |
| Mathématiques | Calibrable autour de 96 % avec une volatilité forte | Aux mêmes réglages, RTP 64 %. Il faudrait multiplier les services, ce qui banalise l'événement |
| Animation | La trajectoire laisse une ligne lisible de symboles identiques | Mouvement spectaculaire, mais résultat peu lisible |

B pourrait devenir un événement secondaire, mais il n'est pas recommandé : cela ajouterait une mécanique de plus, ce que le cahier des charges veut éviter.

Pour la version stable, il faudrait retirer Rally Path, Final Set et B. Ce n'est **pas encore fait** et attend votre validation.

## Phase 5 — Mathématiques (état)
- RTP de A : 96,75 % par simulation. Il faut le ramener à environ 96,0–96,5 % (léger ajustement des cibles de base), puis faire une **mesure de précision supérieure**. Une méthode semi-exacte par énumération des trajectoires est possible, puisque les cibles et les rangées sont des tirages indépendants.
- Achats de bonus : non calculés, non affichés.
- Il reste à faire : plafonds en bonus, distribution des gains par paliers, revue indépendante.

## Phase 6 — Bible de production (inventaire, pas de nouveaux assets médiocres)
Les assets actuels sont **temporaires** pour : la Balle d'or (balle recolorée dans un médaillon), la raquette d'animation (art du symbole H4 réutilisé), l'anneau d'impact et la traînée (vectoriels).

| Ressource à produire | Spécification |
|---|---|
| Balle d'or (symbole + version animée) | Feutre doré, coutures ivoire, médaillon nuit et or champagne ; 512 px ; 8 images de rotation ; version lumineuse pour la révélation |
| Raquette de frappe | Cadre bleu nuit et or, cordage ivoire ; 3 poses (prête, armée, finale) + flou de mouvement ; vue de 3/4 |
| Trace de balle | Ruban doré dégradé (texture 256×32) + particule de feutre (4 variantes) |
| Impact | Onde ivoire + marque au sol « craie » (spritesheet de 6 images) |
| Wild, Scatter, trophées, accessoires | Une même famille : rendu peint 3/4, éclairage de nuit venant du haut à gauche, contour or champagne de 2 % ; pas de néon rose |
| Cadres et interfaces de bonus | Rally Challenge : bleu électrique sobre ; Grand Final : bleu nuit + or ; un seul compteur « TOURS » |
| Championship Point | Tableau d'affichage (9-slice), chiffres ivoire, projecteurs (calque additif), son de foule en 3 intensités |
| Mascotte | Golden retriever officiel, visière ivoire, bandana marine ; 3 courtes animations (regarder la balle, réaction au smash, célébration) |
| Sons | Balle d'or (révélation), service, frappe sèche, rebond ×3, smash (vent + frappe), transformation, foule légère / forte |

## Phase 7 — Architecture B2B (préparation, pas d'intégration fictive)
Déjà en place :
- moteur séparé de l'interface ;
- résultats en livres d'événements sans état ;
- client RGS séparé (`rgs/`) avec un adaptateur Stake documenté ;
- reprise des tours interrompus ;
- historique et rejeu ;
- tests automatisés (Python, TS, e2e).

À faire :
- adaptateur pour un agrégateur réel, sur la base de sa documentation ;
- journal des transactions côté serveur ;
- dossier mathématique pour un laboratoire ;
- certification.

**Aucune intégration à Shuffle, Celsius ou un autre opérateur n'existe ni n'est simulée.** Le jeu n'est ni certifié ni accepté par un casino.
