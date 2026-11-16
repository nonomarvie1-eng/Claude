# Golden Rally — Match Point · Conception du jeu (v4)

## Refonte premium v4 (pack de symboles client)

**Règles mathématiques inchangées** : RTP 96,487 % (base) et 96,457 % (achat ×100), paytable, rouleaux, IDs de symboles, Tie-Break et achat strictement identiques (vérifiés par `pytest` et `vitest`). Seuls les visuels, l'interface, l'audio et les libellés ont changé.

- **Palette** : bleu nuit `#081B23`, vert émeraude `#093A31`, or chaud `#D5A64B` (réservé aux points forts), crème `#F2E5C3`, jaune balle `#D4E948` (scatter, multiplicateur, Tie-Break). Typographies Cinzel (titres, montants) et Inter (interface).
- **Symboles** (pack fourni, mappé sans toucher aux IDs) : W = Balle couronnée (wild), S = Le Central (scatter), H1 Champion, H2 Championne, H3 Arbitre, H4 Trophée de la victoire, H5 Ace, L1 Avantage (AD), L2 40, L3 30, L4 15, L5 LOVE (remplace « 0 » à l'affichage seulement). `golden_ball` sert aux transitions, `tiebreak_bonus` à l'annonce du bonus et à l'écran d'achat ; `champion_racket` est gardé en réserve.
- **Écran principal** : grille 6×5 centrée entre la barre du haut et le HUD (dimensions mesurées en direct, aucun bouton sur les rouleaux), cadre or fin, séparateurs discrets, plaque de gain sous la grille (elle ne cache aucun symbole). HUD : crédits, mise et gain, puis achat bonus, −, lancer, +, auto. Plus aucun halo permanent.
- **Écran d'accueil** : le vrai stade de nuit (projecteurs, tribunes floutées, court en perspective), logo Cinzel, balle d'or qui traverse le logo une fois, Ace qui passe la tête, bouton COMMENCER, bandeau crédits fictifs. Les animations sont coupées en mouvement réduit.
- **Ace, mascotte** : il n'est pas affiché en permanence. Il apparaît au lancement (« Bienvenue au Night Cup ! »), apporte la balle d'or à l'entrée du Tie-Break, réagit aux gros gains (« Quel point ! ») et à la fin du bonus. Il se place à côté des rouleaux, ou dans le bandeau du logo sur téléphone, jamais sur un symbole. Il intervient toujours après que le résultat est connu et n'annonce jamais de gain.
- **Tie-Break** : ambiance distincte (stade bleuté, projecteurs renforcés, liseré lumineux autour du cadre) et panneau « GOLDEN RALLY · TIE-BREAK » qui affiche TOUR x / y, MULTIPLICATEUR ×m et GAIN TOTAL. Ces valeurs viennent des événements du livre (`updateFreeSpin`, `rallyUp`, `setTotalWin`). Le panneau occupe une colonne latérale en paysage et un bandeau en portrait. Les symboles non gagnants restent visibles (atténués). Un récapitulatif final indique les tours joués, le multiplicateur final et le gain total.
- **« MATCH POINT ! »** s'affiche dans le bandeau du logo, plus sur les rouleaux.
- **Audio** (synthétisé, original) : service, rebond, contact raquette, ambiance de stade discrète, jingle de transition Tie-Break, apparition d'Ace. Tout est coupable et ne démarre qu'après le geste « COMMENCER ».

## Historique : ## Direction artistique v3 « Match Point » (fun premium)

**Concept** : le **Golden Rally Club** organise sa **Night Cup**, un tournoi fictif joué la nuit sous les projecteurs. C'est notre univers maison : notre club, notre trophée, nos personnages et notre mascotte.

- **Palette** : vert court profond, or brillant, jaune balle, blanc cassé, touches d'orange.
- **Matière** : dégradés métalliques, biseaux, reflets, lueurs colorées et ombres portées. Les contours restent fins et encrés, le style fun mais travaillé.
- **Décor vivant** : ciel étoilé, tours de projecteurs dont les faisceaux respirent, tribunes avec **flashs d'appareils photo** (plus nombreux quand le public s'enflamme), panneau LED « GOLDEN RALLY CLUB · NIGHT CUP », court vert éclairé.
- **Logo iconique** : « GOLDEN » en or poli, « RALLY » en jaune balle, petite coupe au-dessus, balle d'or avec traînée de feu, ruban **MATCH POINT**.
- **Mascotte signature : ACE**, le bulldog du club (bandeau jaune balle, médaille d'or « ACE »).
- **Symboles désirables** :
  - **Wild** : la Balle d'Or en feu.
  - **Scatter** : la **Coupe Golden Rally**, trophée fictif entouré de lauriers.
  - **Personnages en médaillons dorés**, chacun avec sa gemme : le Champion (arrogant, bandeau or), la Championne (star, créoles dorées), l'Arbitre (« OUT ! »), le Président (monocle) et ACE.
  - **Symboles faibles** : **jetons de tournoi** hexagonaux façon joyaux (0 améthyste et bronze, 15 ambre et argent, 30 saphir et argent, 40 émeraude et or, AD rubis et or), avec un chiffre lumineux.
- **Moments forts** :
  - **« MATCH POINT ! »** quand 2 Coupes sont tombées et que les derniers rouleaux peuvent encore déclencher le bonus : bannière pulsante, roulement de tambour, rumeur du public. Le résultat est déjà fixé ; on ne fait que mettre en scène sa révélation.
  - Annonces des gros gains : **ACE !** (≥ 10×), **SMASH !** (≥ 50×), **JEU, SET ET MATCH !** (≥ 200×).
  - Annonce **« RALLY ×N ! »** à chaque hausse du multiplicateur, avec le public qui saute.
- **Interface** : verre sombre et liserés dorés. Le **bouton de lancement est une balle d'or** avec un halo pulsant, l'**achat de bonus une médaille dorée**, et le gain s'affiche en or plus grand que le reste.



## Identité

- **Nom de travail** : Golden Rally. Une recherche de marque est à faire avant toute diffusion publique.
- **Style : cartoon à gros traits.** Contours d'encre épais, aplats de couleur avec ombrage cel, ombres décalées façon BD, trames de points. Typographies Luckiest Guy et Lilita One.
- **Univers** : le club de tennis du quartier, un jour de tournoi interne. Fanions, tribune pleine, court en terre battue, et le **vieux tableau de score en bois du club** qui sert de grille de jeu.
- **Ton** : humour et caractère. Chaque symbole fort est un personnage avec une attitude.
- **Inspiration, pas de copie** : on reprend des jeux du marché les principes qui créent la personnalité (personnages, style assumé, grille intégrée au décor, palette signature). Aucun dessin, nom ou mécanique propriétaire n'est repris. Aucun personnage ne représente une personne réelle, un tournoi ou une marque.

## Personnages et symboles

| Code | Symbole | Rôle | Gain par façon 3/4/5/6 (× mise) |
|---|---|---|---|
| W | **Smash** : raquette qui frappe la balle | Wild (rouleaux 2 à 6) | — |
| S | **Trophée** | Scatter, déclenche le Tie-Break | 2 / 5 / 20 / 100 (total, n'importe où) |
| H1 | **Le Président** : moustache, monocle, nœud papillon, air satisfait | Haut | 0,5 / 1 / 2 / 5 |
| H2 | **La Championne** : bandeau, regard déterminé, raquette sur l'épaule | Haut | 0,4 / 0,8 / 1,5 / 3 |
| H3 | **L'Arbitre** : lunettes, crie « OUT ! » | Haut | 0,3 / 0,5 / 1,2 / 2,5 |
| H4 | **Le Ramasseur** : casquette à l'envers, taches de rousseur, dent manquante | Haut | 0,2 / 0,4 / 1 / 2 |
| H5 | **Le Bulldog du club** : bandeau éponge, balle dans la gueule | Haut | 0,2 / 0,3 / 0,8 / 1,5 |
| L1–L5 | **Plaques de score** AD, 40, 30, 15, 0 accrochées au tableau | Bas | 0,1 → 0,7 |

Les symboles bas reprennent toute la progression du score au tennis (0, 15, 30, 40, AD). C'est notre clin d'œil, à la place des cartes A, K, Q, J habituelles.

## Gameplay

- **Grille 6 × 5, 15 625 façons de gagner** : un symbole paie s'il est présent, ou remplacé par un Smash, sur des rouleaux adjacents à partir de la gauche, sur 3 à 6 rouleaux. Le gain vaut la valeur par façon multipliée par le nombre de façons.
- **Tie-Break (tours gratuits)** : 3, 4, 5 ou 6 Trophées donnent 9, 12, 15 ou 20 tours.
- **Mécanique signature « Rally »** : pendant le Tie-Break, chaque Smash qui tombe *relance l'échange*. Le multiplicateur de tous les gains en façons monte, avant le calcul du tour : ×1 → ×2 → ×3 → ×4 → ×5 → ×6 → ×8 → ×10 → ×12 → ×15 → ×20. Il ne redescend jamais pendant le bonus et s'affiche sur le cadran RALLY.
- Relance du bonus : 3 Trophées ou plus ajoutent 5 tours, avec au plus 50 tours restants.
- **Achat du Tie-Break** (badge « ACHAT BONUS ») : **100× la mise** pour lancer directement le bonus. Le tour acheté affiche 4 Trophées (12 tours gratuits) avec une probabilité de 13/16, sinon 3 Trophées (9 tours), puis le Tie-Break suit les règles normales. Le RTP exact de ce mode est de 96,457 %. Une confirmation affiche le prix et le RTP. Le badge peut être désactivé par juridiction.
- **Tours automatiques** : 10, 25, 50 ou 100 tours. La **limite de perte est obligatoire**. Arrêts optionnels sur un gros gain unitaire et au déclenchement du bonus (activé par défaut). Le bouton Stop arrête la série après le tour en cours, et la barre d'espace arrête aussi. Désactivable par juridiction.
- Gain maximal : 5 000× la mise. Ce gain est **réellement présent** dans les fichiers Stake.
- RTP : **96,487 %** (calcul exact). Volatilité élevée : écart-type de 7,8× la mise. Bonus en moyenne une fois tous les 174 tours.

## Direction visuelle v2.2 : « cartoon premium », fini l'effet carré

- **Personnages dans des médaillons ronds** à liseré doré, avec un halo coloré. La tête dépasse du cercle et chaque fond a son propre motif.
- **Symboles faibles en grands chiffres 3D** (0, 15, 30, 40, AD) : relief encré, dégradé brillant, halo de couleur. Plus aucune plaque carrée.
- **Grille sans cases** : colonnes arrondies sur un terrain vert profond éclairé par le haut.
- **Cadre de court** : bande blanche de ligne de court, bordure en filet, balles de tennis aux quatre coins. Le logo est posé à cheval sur le haut du cadre.
- **Gains entourés d'anneaux lumineux** (plus de carrés), barre de commandes aux coins supérieurs arrondis.

## Finitions visuelles (v2.1)

- Les personnages **débordent de leur carte** (la tête dépasse le cadre). Ils ont une deuxième couche d'ombre, un liseré de lumière et un motif de fond propre à chacun : losanges VIP pour le Président, lignes de court pour la Championne, damier de tableau pour l'Arbitre, filet pour le Ramasseur, empreintes de pattes pour le Bulldog.
- Les plaques de score sont agrandies et remplissent mieux la case sur mobile.
- Le **décor est animé** : la tribune ondule doucement et **saute de joie** sur les gros gains et au Tie-Break, et les fanions oscillent. Les rouleaux s'écrasent légèrement à l'atterrissage et les symboles gagnants se dandinent.

## Présentation (le résultat est toujours fixé avant l'animation)

- Les rouleaux défilent sur leurs vraies bandes et s'arrêtent sur les positions tirées par le serveur.
- Les gains sont mis en valeur symbole par symbole (cadres jaunes, nombre de façons, montant). Les gains inférieurs ou égaux à la mise ne sont pas célébrés.
- Tie-Break : écran « TIE-BREAK ! ». À chaque Smash, la balle vole vers le cadran RALLY et l'aiguille avance, puis vient l'écran récapitulatif.
- Gros gains (≥ 10× la mise **débitée**, soit 10 × 100 × la mise pour un bonus acheté) : célébration avec pluie de balles et tribune en délire, qu'un toucher écourte sans changer le montant.

## Production 100 % par code

- `game/art/build-art.mjs` dessine tout en SVG (personnages, décor, tableau, logo, cadran), puis `game/art/rasterize.mjs` les rend en PNG avec Chromium.
- `game/audio/synth.py` synthétise tous les sons (balles, rebonds, swoosh, carillons, applaudissements) et les musiques en boucle.
- **Limite assumée** : un style graphique fort et des personnages cartoon sont produits ici à un niveau professionnel. Des illustrations *peintes* ou très détaillées, comme celles de certains jeux concurrents, demanderaient un illustrateur ou un outil d'IA d'image (voir `ASSETS_AND_LICENSES.md`).

## Accessibilité et confort

- Mode « réduire les animations », qui suit aussi le réglage système.
- Mode rapide, désactivable par juridiction.
- Volumes séparés (général, musique, effets) ; son coupé quand l'onglet est masqué.
- Navigation au clavier ; la barre d'espace lance un tour.
- Langues : français et anglais.
