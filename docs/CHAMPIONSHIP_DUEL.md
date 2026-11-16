# CHAMPIONSHIP DUEL — spécification, modèle mathématique, prototype (build DUEL-01)

Statut : **prototype**. Les crédits sont fictifs. Aucun achat n'est activé. Les mathématiques sont expérimentales : les valeurs ci-dessous sont **calculées exactement**, mais restent à valider par un tiers.

## 1. Audit et archivage

Le jeu passe par la chaîne suivante :
`index.html` → `main.ts` → `App.svelte` → `Controller` → `DemoRgs.play()` → moteur → livre d'événements → `playBook()` → `RallyScene` → `Court` (nouveau).

Les anciennes mécaniques sont **archivées sans suppression**. Branches locales :
- `archive/bonus-prototypes-gs02` (état exact avant Championship Duel, commit `6fcf8ff`) ;
- `backup/before-golden-serve` ;
- `backup/before-final-set`.

Chaque mécanique archivée reste reconstructible avec `VITE_GAMEPLAY` :

| Mécanique archivée | Code | Reconstruction |
|---|---|---|
| Golden Serve A Cross-Court / B Court Switch | `engine/goldenServe.ts`, `math/rally_math/golden_serve.py` | `VITE_GAMEPLAY=goldenserve` |
| Rally Path | `engine/rallyPath.ts`, `math/rally_math/rally_path.py` | `VITE_GAMEPLAY=rallypath` |
| THE FINAL SET v6 (Hawk-Eye, Power Shots…) | `engine/bonus.ts`, `render/match.ts` | `VITE_GAMEPLAY=finalset` |

Aucune de ces mécaniques n'est accessible dans le build DUEL-01 : un test vérifie l'absence de leurs événements dans 400 tours aléatoires. Le stockage du navigateur est séparé (`golden-rally-demo-duel01`), ce qui empêche toute reprise d'une partie d'un ancien gameplay.

Branche de travail : les commits sont poussés sur `claude/awesome-feynman-xrl3oz`, la seule branche distante autorisée dans cette session. L'archive est une branche **locale** dédiée.

## 2. Règles

**Jeu de base (inchangé, provisoire)**
- Grille 6×5, 15 625 façons, rouleaux et table de gains v6.
- Les scatters paient 2×, 5×, 20× et 100× pour 3, 4, 5 et 6.
- 3 scatters déclenchent **TIE-BREAK DUEL** (4 points) ; 4 scatters ou plus déclenchent **THE GRAND FINAL** (6 points).

**Le bonus quitte les rouleaux** et se joue sur un court nocturne. Le joueur n'agit pas : aucune adresse n'est suggérée.

**Un point** — le moteur fait toujours 6 tirages uniformes dans [0, 1000) : `[gmp, service1, service2, échange, gain, présentation]`.
1. *(Grand Final seulement)* **Golden Match Point** si `gmp < P_GMP`. Le point se joue normalement. S'il est gagné, son gain est tiré dans la table GMP ; s'il est perdu, il ne paie rien.
2. **Premier service** : ACE, FAUTE ou BON.
3. **Après une faute, second service** : ACE, DOUBLE FAUTE ou BON. Un ace en second service paie comme un ace. Une double faute fait perdre le point et ne paie rien.
4. **Service bon → échange** : perdu (0), gagné sur erreur adverse (petit gain), coup gagnant, ou événement doré rare (Golden Winner au Tie-Break, Golden Smash au Grand Final).
5. **Gain d'un point gagné** : tiré dans la table de son résultat.
6. Le tirage **présentation** choisit seulement la mise en scène : cible du service (T, extérieur, corps), nombre de frappes, direction du coup final. Il ne modifie jamais un gain, ce qui est vérifié par un test.

**Gain du bonus** = somme des points. Pas de multiplicateur, pas de report, pas de minimum garanti. Le gain d'un tour est plafonné à 5 000×.

## 3. Table des événements (probabilités exactes par point)

| Résultat | Tie-Break Duel | Grand Final | Gains possibles (Tie-Break / Grand Final) |
|---|---|---|---|
| Double faute | 7,00 % | 5,94 % | 0 |
| Ace (1ᵉʳ ou 2ᵉ service) | 10,05 % | 10,99 % | 15–100× / 15–80× |
| Échange perdu | 31,52 % | 29,07 % | 0 |
| Point gagné (erreur adverse) | 30,69 % | 29,91 % | 2–5× / 3–6× |
| Coup gagnant | 18,25 % | 20,77 % | 12–60× / 12–75× |
| Golden Winner / Golden Smash | 2,49 % | 3,32 % | 70–1 200× / 80–3 000× |
| Golden Match Point (par point) | — | 2,5 % | gagné : 50–5 000× ; perdu : 0 |

Les tables complètes de gains et de poids sont dans `config.CHAMPIONSHIP_DUEL`. Elles sont aussi affichées sur la page d'informations du jeu.

## 4. Modèle mathématique (exact)

- **Méthode** : les points d'un bonus sont indépendants et de même loi. La loi d'un bonus est donc la convolution de la loi d'un point, calculée exactement sur une grille de 0,5×. Le jeu de base est calculé exactement par polynômes générateurs (`exact.joint_stats`).
- **Contrôles** :
  - la loi d'un point est égale à l'énumération complète des tirages (test) ;
  - la moyenne exacte est égale à la simulation Monte-Carlo, graines 7 et 8 : Tie-Break 43,62× [43,37 ; 43,87] et Grand Final 109,78× [108,93 ; 110,64].

| | Tie-Break Duel | The Grand Final |
|---|---|---|
| Points | 4 | 6 |
| Moyenne d'un point | 10,90× (écart-type 34,9×) | 18,36× (écart-type 81,6×) |
| **Moyenne du bonus** | **43,60×** | **110,14×** |
| Écart-type du bonus | 69,9× | 199,4× |
| P(0) / P(< 10×) | 2,2 % / 19,6 % | 0,18 % / 2,7 % |
| Médiane | 27× | 62× |
| P(≥ 100×) / P(≥ 1 000×) | 8,7 % / 0,1 % | 30,1 % / 0,8 % |
| Quantile 99,9 % | 1 200× | 3 022× |
| Au moins un événement doré | 9,6 % | 18,4 % |
| Au moins un Golden Match Point | — | 14,1 % |
| Maximum théorique | 4 800× | 5 000× (plafond ; 30 000× sans plafond) |

**RTP du jeu (exact)** : 96,25 %, réparti ainsi :

| Composante | Part du RTP |
|---|---|
| Façons du jeu de base | 68,13 % |
| Scatters | 1,24 % |
| Tie-Break Duel | P = 0,5415 % × 43,60× = 23,61 % |
| Grand Final | P = 0,0297 % × 110,14× = 3,27 % |

L'effet supplémentaire du gain du tour déclencheur sur le plafond est inférieur à 10⁻⁶ de RTP.

**Double comptabilisation** : le livre ne contient que des gains disjoints (façons, scatters, points). Un test vérifie sur 20 000 tours que leur somme, plafonnée, est égale au gain final.

**Reproductibilité** : chaque tour est rejouable exactement depuis ses tirages enregistrés. La parité Python/TS est testée sur 368 fixtures. Les scénarios de démonstration sont des tirages enregistrés.

## 5. Animations (court 2,5D, PixiJS, `render/court.ts`)

**Rendu**
- Court aux dimensions ITF en perspective, filet avec bande et poteaux, public et projecteurs.
- Balle en 3D (x, y, hauteur) avec ombre portée, rebonds marqués au sol, trace du coup en cours.
- Raquettes qui frappent au point d'impact, ombre au sol de chaque joueur.
- Tableau d'affichage en haut, annonce du résultat au centre.
- Tout est déterministe, sans `Math.random`.

**Durées mesurées dans le jeu** (horloge d'animation, test e2e à 390×844, rendu logiciel à environ 20 images/s) :

| Événement | Action | Puis annonce du résultat | Cible du cahier des charges |
|---|---|---|---|
| Double faute (deux services manqués) | 1,47 s | 0,77 s | < 1,5 s |
| Ace (service puissant, rebond dans le carré, balle hors d'atteinte) | 0,93 s | 1,0 s | 0,8–1,2 s |
| Échange + coup gagnant (2–3 frappes) | 1,88 s | 1,0 s | 1–2 s |
| Golden Smash (lob, smash au-dessus de la tête, flash des projecteurs, tremblement contrôlé) | ≈ 2,1 s | 1,2 s | 1,5–2,5 s |
| Golden Match Point (annonce, lumières, point, révélation) | ≈ 2,5–3 s | — | 2–3 s |

- **Accélération** : toucher l'écran accélère ×5 sans changer le résultat (testé). Le mode rapide accélère ×1,8. La réduction des mouvements supprime le tremblement et les flashs.
- Le tweener reporte maintenant le temps excédentaire d'une interpolation sur la suivante. Les enchaînements ne perdent plus une image par étape sur les appareils lents.

## 6. Prototype jouable et démonstration

- **Bouton TEST POINT** (à la place de « BONUS MODES »), réservé au développement : joue la démonstration reproductible **double faute → ace → coup gagnant**. Rien n'est débité ni crédité ; un bandeau l'indique.
- **Réglages → Championship Duel — tests** :
  - 7 scénarios d'un point : double faute, ace, coup gagnant, échange perdu, faute puis ace, Golden Smash, Golden Match Point ;
  - point aléatoire Tie-Break ou Grand Final ;
  - deux tours complets forcés (3 et 4 scatters), crédités en crédits fictifs.
- Le bouton **Lancer** joue le vrai jeu : jeu de base, puis Championship Duel quand les scatters le déclenchent.

## 7. Limites connues (honnêtes)

- **Pas de personnages** : les joueurs sont représentés par leur raquette et leur ombre. Aucun asset de joueur fictif n'existe ; un mannequin approximatif aurait été pire.
- **Assets temporaires** : la raquette reprend l'art du symbole H4, la balle est vectorielle, la Balle d'or du jeu de base reste celle des prototypes.
- **Sons** : ce sont les sons de synthèse existants (service, frappe, rebond, foule visuelle). Il n'y a pas de sons de production.
- **Tests** : uniquement Chromium émulé. Le test sur un vrai iPhone reste à faire.
- **Mathématiques** : les gains et probabilités sont expérimentaux, non validés par un tiers. Il n'y a ni achats, ni prix de bonus, ni certification. Aucune intégration Shuffle ou Celsius n'existe.
