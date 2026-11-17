# ACE! — cinématique d'ouverture (build ACE-OPEN-01)

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

## 3. Storyboard définitif et répartition technique

| Scène | Contenu | Réalisation | État |
|---|---|---|---|
| S1 Logo | Stade officiel, logo ACE! net au premier plan, caméra fixe (fondu d'entrée de 0,35 s, puis 0,75 s de tenue) | HTML5 / PixiJS | **Fait** |
| S2a Détachement | La balle du « ! » sort de son alvéole (petite montée) ; le reste du logo s'efface discrètement en 0,52 s ; le « ! » reste sans point | HTML5 | **Fait** |
| S2b Chute et rebond | Chute libre en 0,64 s (y ∝ t²) vers le premier plan du court. La balle du logo devient la balle photographique **au même endroit, à la même taille, sans coupe**. Ombre de contact, écrasement à l'impact, son de rebond à chaque contact, rebond à 30 % de la hauteur (restitution d'environ 0,55) | HTML5 | **Fait** |
| S3 Joueur | Le joueur entre, ramasse **cette** balle et se replace derrière la ligne de fond | **Production externe** (tournage ou 3D riggée) | **Manquant**, point d'intégration prêt |
| S4 Service | Les 7 phases d'un service professionnel | Production externe | **Manquant** |
| S5 Balle vers la caméra | Impact sec, la balle file vers l'objectif, l'arrière-plan devient flou, la balle masque l'objectif | Production externe ; son d'impact joué par le jeu au temps `contactAt` | Point d'intégration prêt |
| S5 (version sans joueur) | Tant que la séquence du joueur manque, la caméra se rapproche de **la même balle** pendant que le stade devient flou, jusqu'à l'occultation. Aucun personnage de substitution | HTML5 | **Fait** |
| S6 Raccord | Quand la balle couvre tout le cadre, les **vrais rouleaux** du jeu sont activés dessous ; la balle grossit encore légèrement et disparaît ; l'interface apparaît ensuite. Pas de faux rouleaux, pas de rechargement | Moteur du jeu | **Fait** |

Durées actuelles :
- **version HTML5** : environ 4,9 s ;
- **avec la séquence du joueur** : environ 2,5 s de HTML5, plus la durée du clip jusqu'à `occludedAt`, soit les 9 à 11 s visés.

## 4. Point d'intégration de la séquence du joueur
Il suffit de déposer deux fichiers dans `game/src/assets/cinematic/` : `serve.mp4` (H.264) et `serve.json` (voir le README de ce dossier). Aucune modification de code n'est nécessaire.

- **`handoffAt`, `ball{x,y,d}`** : la balle HTML5 rejoint en 0,16 s la position et la taille de la balle du clip à cet instant, puis le clip prend le relais en fondu (même balle, même cadrage).
- **`contactAt`** : le jeu joue le son d'impact de la raquette.
- **`occludedAt`** : la balle du clip couvre tout le cadre. Le jeu la remplace par la même balle en plein cadre, active les vrais rouleaux dessous et fait disparaître la balle.
- Si le clip est absent, impossible à lire ou chargé en plus de 5 s, la version HTML5 est jouée (testé). L'écran n'est jamais noir.
- Le mécanisme a été testé avec une vidéo synthétique de contrôle, utilisée **uniquement dans le test** et jamais intégrée au jeu.

### Cahier des charges de production (à confier à un studio ou à un animateur 3D)
- **Format** : 1080×1920, 30 ou 60 i/s, plan portrait. Stade : **plaque du stade officiel** (même caméra que `loading_stadium` au début du clip), éclairage nocturne identique, revêtement bleu nuit, mêmes lignes et même filet.
- **Personnage** : **original**, sans ressemblance avec un joueur réel. Bandeau blanc, polo bleu marine à liseré ivoire, short blanc, bracelets blancs, chaussures blanches, raquette bleu marine et jaune, **aucun logo de marque**.
- **Image 0** (`handoffAt`) : la balle au sol, au premier plan, dans la position où le jeu la laisse après le premier rebond (environ 79 % de la largeur, 86 % de la hauteur, diamètre d'environ 9 % de la largeur), en train de remonter.
- **Action** : le joueur entre, ramasse la balle, revient derrière la ligne de fond, puis enchaîne les 7 phases du service :
  1. position et prise ;
  2. lancer de la main non dominante ;
  3. flexion ;
  4. rotation des épaules (position d'armé) ;
  5. extension et accélération ;
  6. contact (`contactAt`) ;
  7. accompagnement et réception équilibrée.
- **Fin du clip** : la balle part vers l'objectif, l'arrière-plan devient progressivement flou, puis la balle couvre 100 % du cadre (`occludedAt`). Pas de traînée lumineuse ni d'effet.
- **Vérifications avant livraison** : un seul joueur et une seule balle ; aucune main supplémentaire ; aucun changement de visage ou de tenue ; aucun logo.

### Sons manquants (les sons actuels sont de synthèse)
- rebond de balle sur surface dure (3 intensités) ;
- frappe de service sèche ;
- souffle de la balle vers l'objectif ;
- ambiance de stade discrète.

## 5. Intégration et comportements
- **Quand** : à la première visite, après JOUER (geste requis pour le son sur iOS et Android). « Passer l'introduction » et les visites suivantes vont directement à la grille.
- **Passer** : bouton PASSER en haut à droite. Un toucher n'importe où accélère ×8, même s'il arrive avant le début de la cinématique.
- **Réduction des mouvements** : pas de cinématique, fondu de 0,18 s.
- **Musique** : elle démarre après la cinématique ; seuls les bruitages l'accompagnent.
- **Interface** : masquée pendant toute la cinématique (vérifié image par image).
- **Nettoyage** : le canvas d'ouverture est détruit, il ne reste qu'un canvas.
- **Logique du jeu** : aucun effet sur les mathématiques, le RTP, les bonus ou la logique (seule la couche d'introduction change).

## 6. Tests
- **`e2e/cinematic-e2e.mjs` : 19/19**. Points vérifiés :
  - continuité de la balle : la balle qui tombe démarre à la position et à la taille exactes de la balle du logo ;
  - montée avant la chute ;
  - 2 rebonds ;
  - occultation, puis vrais rouleaux jouables et spin après la cinématique ;
  - interface masquée pendant la cinématique ;
  - un seul canvas restant ;
  - visite suivante sans cinématique ;
  - bouton Passer ;
  - réduction des mouvements ;
  - clip externe (vidéo de contrôle) joué entre le rebond et l'occultation ;
  - clip absent : repli sur la version HTML5 ;
  - formats 390×844, 1440×900, Pixel 7 en paysage et 320×568.
- **`e2e/intro-e2e.mjs` : 56/56**.

## 7. Limites
- **Pas de séquence de joueur réaliste** : elle ne peut pas être produite ici avec une qualité commerciale. Le point d'intégration et le cahier des charges sont prêts ; **aucun personnage n'est simulé**.
- **Nom du jeu** : le logo ACE! n'est utilisé que dans la cinématique. Le jeu affiche encore « Golden Rally » (en-tête, carte de fonctionnalité, mascotte). Le changement de nom est à décider.
- **Résolution 1080×1920** : atteinte par le stade (941×1672 natif, mis à l'échelle) et le logo. Pour une finition maximale, une version 1080×1920 du stade serait préférable.
- **Appareils** : vérifié dans Chromium émulé uniquement, pas sur un vrai iPhone ni un vrai Android.
