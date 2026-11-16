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
