# Écran de chargement — version 2 (build FIRST-SERVE-02), avec les trois assets fournis

## Assets fournis (aucun autre asset inventé)
| Fichier fourni | Fichier du jeu | Format | Fidélité |
|---|---|---|---|
| Stade de nuit (941×1672, PNG) | `loading_stadium.webp` (185 Ko) + PNG d'origine en secours | WebP q92 | écart moyen < 1,7/255 |
| Barre ivoire et champagne (2172×724, PNG transparent) | `loading_bar.webp` (47 Ko) + PNG | WebP q95, transparence exacte | écart moyen < 1,8/255 |
| Balle jaune transparente (1024×1024) | `loading_ball.webp` (251 Ko) + PNG | WebP q92, transparence exacte | écart moyen < 2,3/255 |

Proportions toujours conservées : aucun étirement.

**Mesures sur l'image de la barre** : canal ivoire de x = 7,73 % à 92,40 % de la largeur, et de y = 46,8 % à 55,8 % de la hauteur ; tube complet de y = 44,5 % à 58,7 %. La balle occupe 89 % de son image.

## Composition (portrait 9:16)
- **Stade** : il remplit l'écran (coupé sur les côtés si l'écran est plus étroit que le 9:16). Sur un écran plus large (paysage, ordinateur), la composition 9:16 est conservée en pleine hauteur, et les côtés sont complétés par le même stade flouté et assombri, sans recadrage ni déformation.
- **Zone logo réservée** : de 7,5 à 23,5 % de la hauteur, au centre, vide pour le futur logo (`IntroScene.logoArea()`).
- **Barre** : centrée à 29 % de la hauteur, largeur égale à 53 % de la largeur portrait (dans la fourchette demandée de 48 à 58 %).
- **Balle** : diamètre visible égal à 2,3 fois la hauteur du tube, au début de la piste.

## Animation
1. **Progression** :
   - Le canal ivoire se remplit d'or champagne (dégradé discret, à 88 % d'opacité) en suivant la progression **réelle** : images de l'intro 15 %, images du jeu 70 %, polices 5 %, scène 10 %.
   - L'interpolation est douce (exponentielle, environ 140 ms) et ne dépasse jamais la valeur réelle.
   - Le centre de la balle reste toujours entre les bornes de la piste (testé). Sa rotation correspond exactement à la distance parcourue, sans rotation ajoutée.
2. **Fin du chargement** (environ 1 s) :
   - la balle atteint le bout de la piste ;
   - elle fait un seul petit rebond (montée qui ralentit, descente qui accélère, léger écrasement à l'atterrissage) ;
   - le son d'impact est joué seulement si l'audio a déjà été débloqué par un geste ; sinon il est silencieux, ce qui est le cas normal à la première ouverture ;
   - un reflet sobre traverse la barre remplie ;
   - la barre et la balle disparaissent en fondu.
3. **Transition** (500 ms) :
   - le stade reste à l'écran et se rapproche très légèrement ;
   - le jeu apparaît en fondu par-dessus ;
   - l'interface se révèle ensuite.

   À la première visite, la carte de fonctionnalité s'affiche d'abord, sur le stade assombri.
4. **Réduction des mouvements** : ni roulement, ni rebond, ni reflet ; fondu de 0,2 s.
5. **Nettoyage** : boucle du ticker retirée, `ResizeObserver` déconnecté, application PixiJS détruite. Le test vérifie qu'il ne reste qu'un canvas.

## Pré-chargement HTML
- Même composition que la scène (stade, barre, balle au départ), aux mêmes coordonnées : la reprise par PixiJS ne fait aucun saut.
- Aucun pourcentage n'est affiché, seulement un léger éclat de la balle.
- Dans le fichier unique publié, le stade est intégré une seule fois : le décor flouté en recopie la source.

## Tests
`e2e/intro-e2e.mjs` : **55/55** sur le site de test, **54/54** sur le fichier publié (le test d'erreur réseau ne s'applique qu'au site de test). Sont vérifiés :
- l'affichage du stade avant le script ;
- la progression réelle et monotone ;
- la balle en bout de piste, jamais hors piste ;
- le rebond et le reflet ;
- l'interface masquée pendant toute la transition (relevé image par image) ;
- la durée de la transition : 567 ms d'animation ;
- le nettoyage des boucles ;
- la visite suivante ;
- l'absence de son avant un geste ;
- la réduction des mouvements ;
- l'accélération par toucher ;
- l'erreur de chargement ;
- les formats 390×844, Pixel 7 en paysage, 1440×900 et 320×568.

Pas de régression : Return Spins 104/104, vitest 39/39. Aucune logique de jeu n'a été modifiée.

---

# GOLDEN RALLY — THE FIRST SERVE (chargement et entrée en jeu)

Build : **FIRST-SERVE-01**, sur la base de RETURN-01. Les mécaniques de bonus ne changent pas.

## 1. Audit de l'écran précédent
- **Technique** : couche HTML/CSS (`ui/Loading.svelte`) avec un dégradé radial générique, le logo, l'ancienne balle `ui_golden_ball`, une barre de 4 px et la mascotte en image fixe. Le bouton « COMMENCER » était obligatoire à chaque visite.
- **Progression** : réelle (images décodées), mais la phase « scène » passait directement de 90 à 100 %, et les polices n'étaient pas comptées.
- **Affichage** : le stade (canvas PixiJS) n'apparaissait qu'une fois tout chargé. Avant le script, la page restait vide.
- **Poids** : le script principal faisait 965 Ko, dont environ 700 Ko de données de test (fixtures de parité) embarquées sans utilité en jeu.

## 2. Ce qui a été fait

### Scènes séparées
| Couche | Fichier | Rôle |
|---|---|---|
| Pré-chargement | `index.html` (`#preboot`) | Le vrai fond du stade nocturne et le logo, affichés dès les premiers octets. Aucun pourcentage : la progression réelle commence avec le script. |
| Chargement et entrée | `render/intro.ts` (`IntroScene`), dans son propre canvas PixiJS | Scène détruite après l'entrée en jeu (mémoire GPU libérée). |
| Couche accessible | `ui/Intro.svelte` | Barre de progression ARIA, connexion lente, erreur, boutons. |
| Jeu | `render/scene.ts` | Inchangé, sauf le paramètre de fondu de `setIntro`. |

### Chargement réel, en deux temps
1. Les images du stade de l'orientation courante : ciel, court, public, logo, halo, Balle d'or.
2. Les autres images du jeu, sans décoder deux fois les précédentes.

Répartition de la progression :

| Étape | Part |
|---|---|
| Images de l'intro | 15 % |
| Images du jeu | 70 % |
| Polices | 5 % |
| Scène et session | 10 % |

La valeur affichée suit la valeur réelle et ne la dépasse jamais (testé). Le calque `flags` (888 Ko) n'est plus dans le premier lot.

### Mise en scène pendant le chargement
- **Projecteurs** : les quatre rampes s'allument une à une à 12, 35, 60 et 85 %, avec un court scintillement, et le stade s'éclaircit progressivement.
- **Tableau d'affichage** : navy et champagne, rangées de lampes ; le logo s'y révèle de gauche à droite au rythme du chargement, puis « THE FIRST SERVE » apparaît.
- **Barre de progression** : c'est la ligne de fond du court ; la Balle d'or officielle roule en tête.

### Accès sans délai artificiel
Dès que tout est prêt :
- **Première visite** : la carte de fonctionnalité s'affiche, avec JOUER et « Passer l'introduction ».
- **Visites suivantes** : entrée automatique et immédiate.

### Transition (600 ms, une seule interpolation)
1. La Balle d'or rebondit vers le centre du court.
2. Le tableau d'affichage se transforme en cadre des rouleaux, exactement à la position réelle de la grille, avec un léger rapprochement de caméra.
3. Les rouleaux apparaissent, puis l'interface se révèle.

Toucher l'écran accélère la transition. Avec la réduction des mouvements, ce n'est qu'un fondu de 180 ms.

### Carte de fonctionnalité (première visite)
- Elle contient le logo officiel, « GOLDEN SERVE · RETURN SPINS » et une illustration faite avec les vrais symboles du jeu : grille 6×3, Balle d'or au rouleau 1, trajectoire, zone CENTRE encadrée, flèches de relance.
- Le texte, exact, reprend les règles RETURN-01.
- **Aucun RTP, volatilité, fréquence ni gain maximal** n'y figure.
- Sur un téléphone en paysage, la carte occupe la gauche et les boutons la droite.

### Son
Aucun son avant un vrai geste :
- **Première visite** : JOUER débloque l'audio.
- **Visites suivantes** : le premier toucher ou la première touche du clavier le débloque.

Le test vérifie qu'aucun `AudioContext` n'est créé avant.

### Robustesse
- **Connexion lente** : au-delà de 7 s, le message « Connexion lente : le chargement continue » s'affiche.
- **Échec de chargement** : un message clair et un bouton Réessayer apparaissent, sans entrer dans le jeu.
- **Reprise de session** : la partie interrompue est reprise par `ctrl.boot()` après la transition (mécanisme existant).
- **Intégration casino** : pas de barre de navigation ni de portefeuille simulés ; zones sûres iOS respectées.

### Poids
Les fixtures de test sont retirées du jeu par un plugin Vite (`stripTestFixtures`) et conservées pour vitest. Le script passe de 965 Ko à **617 Ko** (203 Ko compressé).

## 3. Assets
**Utilisés (assets réels du projet)** :
- `bg_portrait.jpg` / `bg_landscape.jpg` : ciel de nuit avec rampes de projecteurs ;
- `fore_*` : court et bandeau ;
- `crowd_*` : public ;
- `flags_*` : drapeaux, arrivent avec les images du jeu ;
- `logo.webp`, `glow.webp` ;
- `sym_G.webp` : Balle d'or, temporaire ;
- les symboles du jeu, pour l'illustration de la carte.

**Manquants, à produire pour une version finale** :

| Asset | Usage |
|---|---|
| Balle d'or finale | Feutre doré, coutures ivoire en relief, 8 images de rotation, version lumineuse |
| Tableau d'affichage peint | Métal champagne, cadran à LED, 9-slice pour se transformer en cadre des rouleaux |
| Projecteurs | Cônes et halos en calques dédiés (actuellement : halo générique et polygones additifs) |
| Ligne de fond « craie » | Avec texture de lumière pour la progression |
| Version nuit éclairée du court | Pour un fondu jour/nuit plus riche |
| Son d'ambiance d'entrée | Rumeur du stade, déclic des projecteurs, rebond de balle |
| Illustration de la fonctionnalité | Version peinte (actuellement : composition de symboles réels) |

## 4. Tests
`node e2e/intro-e2e.mjs` : **50/50** sur le site de test et sur le fichier publié (sauf l'erreur de chargement simulée, impossible avec un fichier unique). Sont couverts :
- iPhone 390×844 en connexion ralentie, Pixel 7 en paysage, 1440×900, 320×568 ;
- l'affichage du pré-chargement ;
- la progression réelle, monotone, qui se termine à 100 ;
- les 4 rampes de projecteurs ;
- la suppression du pré-chargement ;
- l'absence de son avant un geste ;
- la carte en première visite, et le fait qu'elle ne recouvre jamais les boutons ;
- le bouton à l'écran et d'au moins 44 px ;
- l'interface masquée pendant la transition ;
- la durée d'animation de la transition entre 0,5 et 0,8 s (667 ms mesurées) ;
- le son lancé par JOUER ;
- le spin après l'entrée ;
- la visite suivante directement sur la grille, sans son avant un geste ;
- le lien « Passer » ;
- la réduction des mouvements (fondu de 183 ms) ;
- l'accélération par toucher ;
- l'erreur de chargement avec Réessayer ;
- l'absence de débordement et d'erreur console.

Pas de régression : vitest 39/39, test Return Spins 104/104.

## 5. Limites
- **Vrai iPhone** : non testé, seulement Chromium émulé. Avec ce rendu logiciel (environ 12 i/s), la transition dure environ 0,9 s en temps réel ; sur un appareil fluide, elle dure 0,6 à 0,67 s.
- **Fichier unique publié** : les images y sont intégrées au HTML. La première phase du chargement correspond donc au téléchargement de ce fichier (environ 10 Mo), que le navigateur ne peut pas mesurer depuis le script. En hébergement normal (fichiers séparés, `npm run build`), la progression couvre chaque image.
- **Scène d'introduction** : elle utilise un second contexte WebGL, détruit après l'entrée.
- **Mascotte** : son message de bienvenue en jeu est inchangé.
- **Logo du jeu** : sa réduction pendant la partie relève de la refonte d'interface, non incluse ici.
