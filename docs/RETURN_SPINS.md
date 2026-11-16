# GOLDEN SERVE — RETURN SPINS (build de test RETURN-01)

Statut : **tranche verticale prototype**, sur la vraie grille 6×5. Les crédits sont fictifs. Les mathématiques sont expérimentales : le RTP est **mesuré par simulation**, il n'est pas calculé exactement et pas validé par un tiers. La refonte visuelle globale **n'est pas faite** (voir §7).

## 1. Audit

- **Sources réelles** :
  - mathématiques : Python, `math/rally_math` ;
  - moteur du jeu : port TypeScript, `game/src/engine` ;
  - rendu : PixiJS 8, `game/src/render/scene.ts` ;
  - interface : Svelte 5, `game/src/ui` ;
  - déploiement : `vite build` (fichier unique, `npm run build:single`).
- Le fichier HTML compilé n'est **jamais** modifié à la main : il est reconstruit à partir des sources.
- **Grille 6×5 / 15 625 façons** : l'évaluation des façons (`engine.evaluate_ways`, `engine.ts evaluateWays`) est inchangée. Les tests existants la vérifient : comptes par rouleau, Wild, minimum de 3 rouleaux, parité Python/TS.
- Le premier arrêt de chaque tour de base est exactement l'évaluation v6 de cette grille (test `test_first_stop_win_is_the_ordinary_slot_win`).
- **Réinitialisation** : `RallyScene.resetRound()` (début de chaque tour et de chaque rejeu) vide la zone frappée, la balle, les plaques, les surimpressions et les effets. Le test e2e le vérifie à chaque lancement : rien ne reste.
- **Archivage** : branche locale `archive/championship-duel-01`, plus les archives précédentes. Les anciens prototypes restent dans le code, inaccessibles dans ce build :

| Prototype archivé | Reconstruction |
|---|---|
| Championship Duel | `VITE_GAMEPLAY=duel` |
| Golden Serve A/B | `VITE_GAMEPLAY=goldenserve` |
| Rally Path | `VITE_GAMEPLAY=rallypath` |
| Final Set v6 | `VITE_GAMEPLAY=finalset` |

  Un test vérifie que 400 tours aléatoires ne contiennent aucun de leurs événements.

## 2. Règles

1. Les six rouleaux s'arrêtent : c'est l'**arrêt 1**. La grille complète est évaluée (15 625 façons) et payée.
2. **GOLDEN SERVE** : si la grille montre au moins une **Balle d'or**, celle du rouleau le plus à gauche (la plus haute) sert.
   - La Balle d'or n'est ni Wild ni Scatter. Elle ne paie rien et ne remplace aucun symbole : pour les façons, c'est une case vide.
   - Toutes les Balles d'or visibles à cet instant sont **utilisées**. Elles restent affichées en grisé et ne serviront plus.
3. Le moteur tire la **zone frappée** : GAUCHE (rouleaux 1-2), CENTRE (3-4) ou DROITE (5-6). Les zones sont équiprobables au service.
   - **GOLDEN SMASH** (probabilité par frappe : 1,5 % en jeu de base, 0 en Rally Challenge, 8 % en Championship Night) frappe une zone élargie : rouleaux 1-4 ou 3-6.
4. **Seuls les rouleaux frappés sont relancés.** Les autres ne bougent pas : le test vérifie leurs positions.
   - La grille complète est réévaluée et payée : **chaque arrêt est payé en entier, y compris les combinaisons déjà présentes**.
   - Gain du tour = somme des arrêts, plus le paiement des scatters de l'arrêt 1. Chaque arrêt est affiché à part (« ARRÊT n · +gain · TOTAL »).
5. **RETURN SPIN** : si la relance fait tomber une **nouvelle** Balle d'or sur les rouleaux frappés, et si la limite n'est pas atteinte, celle-ci renvoie la balle vers une zone **non frappée** au coup précédent.
   - Retours maximum par tour : 2 en jeu de base, 2 en Rally Challenge, 3 en Championship Night.
   - Il n'y a donc jamais de boucle : au plus 4 relances par tour.
6. **Bonus** : déclenché par les scatters de l'arrêt 1 d'un tour de base.
   - 3 scatters : **RALLY CHALLENGE**, 8 tours gratuits.
   - 4 scatters ou plus : **CHAMPIONSHIP NIGHT**, 12 tours gratuits avec Golden Smash.
   - Rouleaux de bonus : plus riches en Wilds et en symboles premium, 2 Balles d'or par rouleau, sans scatter.
   - Pas de redéclenchement, pas de multiplicateur, pas de minimum garanti.
7. Le gain d'un tour est plafonné à 5 000×.

**Tirages**, dans l'ordre et enregistrés pour un rejeu exact : 6 arrêts ; pour chaque frappe, `[zone /1000, smash /1000]` ; puis les arrêts des rouleaux frappés. La couche graphique ne décide de rien.

## 3. Résultats mathématiques

Simulation reproductible : 20 M tours et 400 000 bonus par niveau, graine 2027, `math/reports/return_spins_sim.json`. Les valeurs ci-dessous sont **mesurées**, avec leur intervalle de confiance.

| Indicateur | Valeur |
|---|---|
| **RTP du jeu** | **96,02 %** (IC 95 % : 95,61–96,43) |
| Écart-type par tour | 9,34× |
| Fréquence de gain | 30,0 % |
| Golden Serve en jeu de base | 1 tour sur 10,8 |
| Retours après un service (jeu de base) | 0 : 96,8 % ; 1 : 3,1 % ; 2 : 0,08 % |
| Golden Smash par frappe (jeu de base) | 1,6 % |
| Rally Challenge | 1 tour sur 186 |
| Championship Night | 1 tour sur 3 416 |

| Bonus | Rally Challenge (8 tours) | Championship Night (12 tours) |
|---|---|---|
| Moyenne [IC 95 %] | 37,98× [37,75 ; 38,21] | 57,39× [57,11 ; 57,67] |
| Médiane | 17,8× | 31,7× |
| P(< 10×) | 30,4 % | 11,3 % |
| P(≥ 100×) / P(≥ 1 000×) | 7,7 % / 0,08 % | 13,6 % / 0,11 % |
| Maximum observé | 3 794× | 4 355× |
| Services / retours / smashs par bonus | 3,26 / 0,60 / 0 | 4,89 / 1,00 / 0,47 |

**Méthode et contrôles** :
- Moteur par événements (Python) et simulateur vectorisé : ils suivent la même loi, avec un ordre de tirage différent en lot. Un test statistique le vérifie : moyennes égales à 4 écarts-types près.
- Port TypeScript avec parité exacte sur 163 tours de référence.
- Comptabilité testée sur 12 000 tours : somme des arrêts plus scatters égale le gain final, chaque arrêt égale l'évaluation de la grille publiée, et les rouleaux non frappés gardent leur arrêt.

**Reste à faire en mathématiques** :
- Calcul semi-exact des relances : un arrêt partiel ne dépend que des rouleaux relancés, donc c'est faisable.
- Distribution complète par paliers et plafond en bonus.
- Revue indépendante.
- Aucun achat de bonus n'est calculé ni affiché.

## 4. Animations (dans le jeu, PixiJS)

| Étape | Rendu |
|---|---|
| Golden Ball Reveal (0,4 s) | Courte rotation, halo champagne, la balle s'élève, le reste des rouleaux s'assombrit légèrement |
| Golden Serve | La raquette entre près de la balle, lancer, geste au-dessus de la tête, frappe sonore ; trajectoire en arc avec ombre et traînée vers le centre de la zone tirée |
| Impact | Anneau, les rouleaux frappés s'écrasent brièvement, contour champagne de la zone et étiquette « ZONE CENTRE » |
| Relance | Seuls les rouleaux frappés tournent (flou de mouvement, rebond à l'arrêt) |
| Return Spin | Coup différent du service : coup droit à plat venant du côté opposé, sans lancer, trajectoire plus tendue |
| Golden Smash | Raquette haute, court ralenti avec bruit de vent, balle rapide et plongeante, contour élargi sur 4 rouleaux, léger tremblement, réaction du public |
| Gains | Combinaisons soulignées comme d'habitude, puis plaque « ARRÊT n · +gain · TOTAL ». Grande célébration (tableau d'affichage) seulement à partir de 50× |

- Toucher l'écran accélère sans changer le résultat (testé). Le mode rapide et la réduction des mouvements sont pris en compte.
- Panneau des bonus : TOURS, ÉVÉNEMENT (« RETOUR n/m » seulement pendant un événement, sinon « — ») et GAIN TOTAL.

## 5. Démonstration (développement uniquement)

Réglages → « Développement — scénarios forcés ». Le bloc n'existe que si `DEV_TOOLS` est actif : une version joueur se construit avec `VITE_DEV_TOOLS=0`. Le bouton Lancer n'est **jamais** forcé (testé).

1. Spin ordinaire sans Golden Serve.
2. Golden Serve → rouleaux 3-4.
3. Golden Serve + 2 Return Spins (centre → gauche → centre).
4. Événement sans gain.
5. Gain sur deux arrêts, correctement cumulé (+1,2× puis +2,2×, total 3,4×).
6. Golden Smash sur quatre rouleaux.

S'y ajoutent deux bonus forcés : Rally Challenge et Championship Night.

## 6. Perspective B2B (inchangée)

- Moteur de résultats séparé du rendu.
- Livres d'événements rejouables à partir des tirages.
- Historique, reprise des tours interrompus, client RGS séparé.

Il n'existe aucun connecteur Shuffle ou Celsius, aucune mise réelle et aucune certification.

## 7. Bible d'assets (à produire, non réalisé dans cette tranche)

La Balle d'or a été refaite en balle de feutre doré, sans médaillon, avec une lumière champagne. Elle reste un **asset temporaire**, dérivé recoloré de la balle du pack. Elle se distingue moins bien qu'il ne faudrait du symbole « balle jaune » L1 : la production finale devra trancher, par exemple en changeant de symbole bas.

| Élément | Spécification de production |
|---|---|
| Famille de symboles | Rendu 2,5D peint, vue de 3/4 haute, lumière de nuit en haut à gauche, contour champagne fin, même échelle (85 % de la case), pas de néon |
| Golden Ball | Feutre doré (micro-fibres visibles), coutures ivoire en relief, reflet champagne ; 8 images de rotation ; version « utilisée » désaturée |
| Raquette d'animation | Cadre nuit et or champagne, cordage ivoire ; 4 poses (prête, armée, impact, accompagnement), flou de mouvement ; versions coup droit et smash |
| Wild / Scatter | Silhouettes uniques (pas des balles) : Wild = trophée-couronne champagne ; Scatter = billet ou insigne « Championship Night » bleu nuit et or |
| Cadre des rouleaux | Métal champagne brossé, profil fin (moins de 3 % de la largeur), coins biseautés, séparateurs de zones discrets (gauche, centre, droite) |
| Interface | Logo réduit pendant le jeu ; boutons circulaires nuit et or ; typographie titre Cinzel, texte Inter ; contraste AA sur iPhone |
| Sons | Révélation de la balle, frappe de service, retour, smash (vent puis impact), rebond de zone, relance, foule à 3 intensités |

## 8. Limites (honnêtes)

- **Refonte visuelle globale non faite** : le logo, le cadre, les boutons et les symboles sont inchangés, sauf la Balle d'or.
- **Vérification** : Chromium émulé uniquement, pas de vrai iPhone.
- **Mathématiques** : RTP mesuré par simulation, avec intervalle de confiance de ±0,41 point.
- **Lisibilité** : la règle « chaque arrêt est payé en entier » répond à votre demande. Elle fait cependant repayer les combinaisons qui ne bougent pas. Une variante qui ne paierait que les combinaisons nouvelles ou modifiées est possible ; elle changerait le modèle et devrait être recalibrée.
