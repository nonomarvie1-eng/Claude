# ACE! — cinématique d'ouverture (build ACE-OPEN-02)


## 0. Correction ACE-OPEN-02 : classement A / B / C

**A — ce qui fonctionnait et a été conservé :**
- stade de nuit, logo ACE! avec la balle du « ! » ;
- chargement réel (barre + balle), pré-chargement HTML ;
- vraie interface de la slot, bouton PASSER ;
- moteur, mises, bonus et rouleaux : **aucune modification**.

**B — corrigé dans ce build :**

| Problème constaté (enregistrement d'écran) | Correction |
|---|---|
| La carte de fonctionnalité apparaissait **avant** la cinématique | Nouvel ordre : chargement → JOUER (le geste qui autorise le son sur iOS) → logo → détachement → chute et rebonds → [joueur] → balle vers la caméra → **vrais rouleaux** → carte de fonctionnalité **par-dessus les rouleaux**, 0,7 s après, première visite seulement. Aucun retour au chargement, aucun écran noir |
| La caméra restait fixe pendant la chute | La caméra suit la balle : léger rapprochement et bascule vers le court (×1,12 autour du bas de la composition) pendant la chute et le premier rebond ; le logo, déjà en fondu, sort par le haut avec le stade. Les lettres ne bougent pas pendant le détachement |
| Deux rebonds puis zoom immédiat | Rebonds décroissants physiques (restitution ≈ 0,55 : 30 %, 9 %, 2,5 % de la hauteur), un son par contact (volume décroissant), petite roulade, puis **la balle s'immobilise à un point de relais fixe** : 60 % de la largeur, 84 % de la hauteur, diamètre 11,5 % de la largeur du cadre 9:16. C'est la première image du futur clip du joueur |
| Le relais vers le clip faisait glisser la balle vers la balle du clip | La balle **se pose directement** à la position de la balle du clip (lue dans `serve.json`), puis fondu de 0,12 s entre deux images identiques |
| Fin du clip uniquement par la balle du clip | Deux modes : `occludedAt` (la balle du clip remplit le cadre) ou **`exit`** (à l'instant `exit.at`, l'image se fige, la balle HTML5 recouvre exactement la balle frappée et file vers l'objectif avec flou, puis les vrais rouleaux) |
| Clip chargé seulement après JOUER (jusqu'à 5 s d'attente) | Clip **préchargé pendant l'écran de chargement** ; abandon automatique en cas d'échec, de délai (8 s) ou de blocage de lecture (2,5 s sans progression) |
| Sons du clip | Repères sonores sur l'horloge de la vidéo (`cues` : rebonds de la balle par le joueur…) + impact de raquette à `contactAt`. Vidéo muette (autoplay iOS autorisé : `muted` + `playsinline`) |
| Nom visible « GOLDEN RALLY » | Logo d'en-tête du jeu → ACE! ; carte de fonctionnalité → ACE! ; panneau du bonus « ACE! » ; « ACE! · NIGHT FINAL » ; bandeau publicitaire du court « ACE! · CHAMPIONSHIP NIGHT » (régénéré depuis `art/build-art.mjs`) ; mascotte « Bienvenue sur ACE! » ; titre de la page « ACE! » |

Non modifiés volontairement : identifiants internes, clés de sauvegarde des préférences et de l'historique, noms Golden Serve / Return Spins / Rally Challenge / Championship Night, textes des prototypes archivés (inaccessibles dans ce build). Seul le drapeau de présentation « introduction déjà vue » a une nouvelle clé (`ace-opening-seen-v2-rs01`), pour que la nouvelle ouverture soit montrée une fois de plus ; il ne contient aucune donnée de jeu.

**C — ressources externes manquantes** : voir §4 (séquence du joueur, sons). Rien n'a été simulé à leur place.

## 1. Audit des ressources

| Ressource | Constat | Usage |
|---|---|---|
| Stade officiel (941×1672) | Identique, octet pour octet, à `loading_stadium` déjà dans le jeu | Fond de la cinématique : c'est le même stade que l'écran de chargement, d'où une continuité totale |
| Logo ACE! (1774×887, PNG transparent) | La balle du « ! » occupe un cercle de centre (1495 ; 609,5) et de rayon 96,5 px, logé dans une alvéole bleu marine à filet doré | Découpé en deux calques **sans rien redessiner** : `ace_logo_ball` (la balle du logo, cercle découpé avec bord adouci) et `ace_logo_noball` (le logo avec son alvéole vide, comblée du bleu marine du logo) |
| Balle photographique (1024×1024) | Déjà dans le jeu (`loading_ball`) | La balle tombée prend progressivement cet aspect |
| Références du joueur (images 1 à 3) | Images fixes générées. Logos de marque visibles (bandeau, chaussures). Gestuelle à valider (le cahier des charges le signale) | **Non utilisées dans le jeu** : références de direction pour la production externe |
| Balle vers la caméra (image 4) | Image fixe de référence | Référence de cadrage pour la fin de la séquence du joueur |
| Rebond (image 5) | Image fixe d'un autre stade | Référence de lumière et d'ombre uniquement |
| Vidéo de référence | 576×1024, 24 i/s, 8,04 s, son AAC | Mise en scène uniquement (voir §2) |

## 2. Analyse de la vidéo de référence (24 images extraites, une tous les tiers de seconde)

Déroulé observé :
1. 0–1 s : balle au premier plan qui rebondit, joueur flou au fond.
2. 1–3 s : le joueur fait rebondir la balle, puis se met en position.
3. 3–4,5 s : lancer et armé du service (contre-plongée, projecteurs).
4. 4,5–5,5 s : plan de la balle qui traverse le filet vers la caméra.
5. 5,5–6 s : la balle occulte l'objectif.
6. 6–8 s : des **rouleaux inventés** (5 rouleaux, symboles qui ne sont pas les nôtres).

Défauts confirmés :
- **Stade** : c'est une salle couverte (gradins plongés dans le noir, rampes de plafond), pas notre stade nocturne.
- **Résolution** : 576×1024.
- **Raccords** : la balle change d'échelle et de place entre le plan 4 et le plan 5.
- **Joueur** : le logo d'une marque tierce est visible, et sa silhouette évoque un champion réel. C'est un **risque de droit à l'image** : la séquence finale doit utiliser un personnage original, sans ressemblance avec une personne réelle.
- **Rouleaux** : inventés.

**Conclusion** : la vidéo n'est utilisable dans le jeu sous aucune forme. Elle sert seulement de référence de rythme.

## 3. Storyboard et répartition technique

| Scène | Contenu | Réalisation | État |
|---|---|---|---|
| 0 Chargement | Stade, barre et balle de chargement, progression réelle ; à 100 % : bouton JOUER (première visite) | HTML5 | **Fait** |
| S1 Logo | Logo ACE! net, caméra fixe (0,35 s d'entrée, 0,75 s de tenue) | HTML5 | **Fait** |
| S2a Détachement | La balle du « ! » sort de son alvéole ; les lettres restent immobiles et s'effacent en 0,52 s | HTML5 | **Fait** |
| S2b Chute | Chute libre 0,64 s (y ∝ t²), la caméra suit (×1,12) ; la balle du logo devient la balle photographique au même endroit, à la même taille | HTML5 | **Fait** |
| S2c Rebonds et repos | 3 rebonds décroissants + contact final (4 sons), roulade de 0,3 s, arrêt au point de relais (60 % / 84 %, Ø 11,5 %) | HTML5 | **Fait** |
| S3 Joueur | Le joueur entre, ramasse **cette** balle, se place derrière la ligne de fond | Production externe | **Manquant** — intégration prête |
| S4 Service | Les phases techniques du service (voir §4) | Production externe | **Manquant** |
| S5 Balle vers la caméra | Avec clip : mode `exit` (balle HTML5 sur image figée) ou `occludedAt`. Sans clip : rapprochement de caméra sur la même balle au repos, stade flouté | HTML5 + clip | **Fait** (sans clip) / prêt (avec clip) |
| S6 Raccord | Balle plein cadre → vrais rouleaux activés dessous → la balle s'efface → interface | Moteur du jeu | **Fait** |
| 7 Explications | Carte « Golden Serve · Return Spins » par-dessus les vrais rouleaux (première visite), bouton JOUER | DOM (Svelte) | **Fait** |

Durée de la version HTML5 : environ 5,8 s sur un appareil fluide (logo 1,1 s ; détachement 0,24 s ; chute et rebonds ≈ 2,3 s ; repos 0,22 s ; rapprochement 0,7 s ; dégagement 0,26 s).

## 4. Ressources manquantes (catégorie C) et point d'intégration

Déposer dans `game/src/assets/cinematic/` ; **aucune modification de code** n'est nécessaire.

| Fichier | Format | Rôle |
|---|---|---|
| `serve.mp4` | H.264 (High, yuv420p), **1080×1920**, 30 ou 60 i/s, sans piste audio, ≤ 6 Mo, `faststart` | Séquence du joueur S3–S5 |
| `serve.json` | Manifeste (interface `ServeClip`, `game/src/render/aceCinematic.ts`) | Synchronisation |
| `docs/ace_handoff/handoff_frame.png` (**fourni**) | 1080×1920 | Image exacte où la balle HTML5 s'immobilise : **la première image du clip doit lui être identique** |
| `docs/ace_handoff/handoff_plate.png` (**fourni**) | 1080×1920 | Même cadrage sans la balle (plaque pour la composition ou la génération image→vidéo) |
| Sons (WAV 48 kHz ou OGG) | voir ci-dessous | Remplacent les sons de synthèse |

Ces deux images sont régénérées par `node game/tools/export-handoff.mjs` (après `npm run build`) si le cadrage change.

**Manifeste attendu** (valeurs par défaut du point de relais) :

```json
{ "src": "serve.mp4", "width": 1080, "height": 1920,
  "handoffAt": 0.0, "ball": { "x": 0.60, "y": 0.84, "d": 0.115 },
  "cues": [ { "t": 2.10, "sound": "bounce", "volume": 0.5 }, { "t": 2.55, "sound": "bounce", "volume": 0.5 } ],
  "contactAt": 5.20,
  "exit": { "at": 5.30, "x": 0.52, "y": 0.42, "d": 0.06, "ms": 320 },
  "occludedAt": 5.60 }
```

- `ball` : centre (fractions de largeur et de hauteur) et diamètre (fraction de la largeur) de la balle à l'image `handoffAt`. Le jeu pose la balle exactement là ; si le clip est livré avec une autre position, il suffit de corriger ces valeurs.
- `exit` (recommandé) : image où la balle vient d'être frappée, avec sa position et son diamètre. Le clip peut s'arrêter juste après ; le jeu fige cette image et fait partir la balle vers l'objectif.
- `occludedAt` : utilisé seulement sans `exit` ; le clip doit alors montrer lui-même la balle couvrant 100 % du cadre.

### Cahier des charges de la séquence du joueur
- **Durée** : 5 à 7 s jusqu'au contact. **Image 0** = `handoff_frame.png` à l'identique (même plaque, même balle au repos, même ombre). Pas de coupe.
- **Caméra** : libre après l'image 0, en un seul mouvement continu. Comme la balle repose côté caméra, la caméra peut accompagner le joueur et tourner autour de lui pour qu'il serve **vers l'objectif**.
- **Personnage** : **original**, sans ressemblance avec un joueur réel ; tenue et raquette des références fournies (bandeau blanc, polo bleu marine à liseré ivoire, short blanc, raquette bleu marine et jaune), **aucun logo de marque**.
- **Action** :
  1. le joueur entre dans le champ, ramasse la balle (raquette ou main) et la fait éventuellement rebondir (`cues`) ;
  2. il se place derrière la ligne de fond ;
  3. service techniquement correct :
     1. placement des pieds ;
     2. lancer de balle de la main non dominante, bras tendu ;
     3. flexion des genoux ;
     4. rotation des épaules (position d'armé, raquette dans le dos) ;
     5. montée de la raquette et extension du bras ;
     6. contact au point le plus haut (`contactAt`) ;
     7. accompagnement et réception équilibrée.
- **Fin** : la balle part vers l'objectif (`exit`). Ni traînée lumineuse, ni texte, ni faux rouleaux, ni interface.
- **Contrôles avant livraison** :
  - un seul joueur et une seule balle à chaque image ;
  - aucune main ou raquette en double ;
  - visage et tenue constants ;
  - aucun logo.
- **Production** : tournage sur fond vert composité sur la plaque, ou 3D riggée et capture de mouvement. Un générateur image→vidéo peut partir de `handoff_frame.png`, mais le résultat doit passer les contrôles ci-dessus.

### Sons manquants (les sons actuels sont de synthèse)
- rebond sur surface dure, 3 intensités, < 0,4 s ;
- frappe de service sèche, < 0,5 s ;
- souffle de la balle vers l'objectif, environ 0,4 s ;
- ambiance de stade de nuit en boucle (30 s et plus).

## 5. Comportements
- **Première visite** : JOUER sur l'écran de chargement, puis l'ouverture, les rouleaux et la carte des fonctionnalités. « Passer l'introduction » va directement aux rouleaux, la carte s'affiche ensuite.
- **Visites suivantes** : directement à la grille, sans écran intermédiaire.
- **Passer** : bouton PASSER. Un toucher accélère ×8, même avant le début de l'ouverture.
- **Réduction des mouvements** : pas d'ouverture, fondu court.
- **Son** : il démarre au geste JOUER. Les rebonds et la frappe sont synchronisés ; la musique commence après l'ouverture.
- **Interface** : masquée pendant toute l'ouverture. La carte bloque la grille jusqu'à JOUER (pas de lancement accidentel).
- **Échecs** :
  - clip absent, illisible, trop lent ou bloqué : version HTML5 ;
  - image de chargement en erreur : message et bouton Réessayer.
- **Logique du jeu** : aucune modification des mises, bonus, rouleaux, RTP ou RNG.

## 6. Tests (ACE-OPEN-02)
- **`e2e/cinematic-e2e.mjs` : 24/24**. Points vérifiés :
  - même balle (position et taille) ;
  - 4 contacts ;
  - repos exact au point de relais, après le suivi de caméra ;
  - occultation puis vrais rouleaux ;
  - interface masquée, un seul canvas ;
  - passer, réduction des mouvements ;
  - clip de contrôle : relais exact sur la balle du clip, repères sonores, modes `occludedAt` et `exit` ;
  - clip absent : repli ;
  - 4 formats d'écran.
- **`e2e/intro-e2e.mjs` : 64/64**. Points vérifiés :
  - ordre des écrans : JOUER sans carte avant l'ouverture, carte après les rouleaux, grille inaccessible sous la carte ;
  - logo ACE! dans l'en-tête ;
  - titre de la page ;
  - visites suivantes ;
  - formats d'écran, erreurs.
- **Return Spins** : 104/104.

## 7. Limites
- **Pas de séquence de joueur** : elle ne peut pas être produite ici avec une qualité commerciale. **Aucun personnage n'est simulé**. Sans clip, la balle au repos est suivie d'un rapprochement de caméra, pas d'un service.
- **Mode `exit`** : testé avec une vidéo synthétique uniquement. Le réglage fin des valeurs (`exit.x/y/d`) se fera sur le vrai clip.
- **Résolution du stade** : 941×1672 en natif, mis à l'échelle à 1080×1920. Une version native 1080×1920 serait préférable.
- **Appareils** : vérifié dans Chromium émulé uniquement, pas sur un vrai iPhone.
