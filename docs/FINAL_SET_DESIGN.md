# GOLDEN RALLY — THE FINAL SET · Document technique des bonus (maths 4.0.0)

Chiffres validés : `math/reports/exact.json` (jeu de base exact, bonus mesurés par simulation ciblée avec erreur standard) et `math/reports/montecarlo.json` (20 M tours en Normal et en Bonus Chance, 1,9 M par achat). Rapport complet : [MATH_REPORT.md](MATH_REPORT.md).

## 1. Audit (avant refonte)

| Élément | Constat | Décision |
|---|---|---|
| Moteur | Python de référence (`math/rally_math`) + port TypeScript (démo) + fichiers Stake (livres, tables de poids) | conservé, le bonus est réécrit |
| Grille | 6 × 5, 15 625 façons (5⁶), 11 symboles, rouleaux empilés | conservée |
| Gains de base | ways, Wild absent du rouleau 1, Scatter payant partout | conservés (RTP du jeu de base inchangé : 69,4 %) |
| Ancien bonus | tours gratuits + multiplicateur ×1→×20 piloté par les Wilds | **supprimé** : c'est exactement la mécanique « répétitive » à remplacer |
| Rendu | PixiJS 8 (WebGL 2D), Svelte 5 pour l'interface | conservé ; pas de Three.js (voir §7) |
| Limites | pas de moteur 3D, pas de personnages animés, pas d'acteurs ni de vidéo | cinématiques en 2,5D (profondeur, caméra, ralentis), pipeline 3D décrit au §7 |

Séparation stricte : `bonus.py` / `bonus.ts` calculent tout ; `render/match.ts` ne fait que lire les événements du livre.

## 2. COURT CONTROL

Pendant un bonus, la grille devient le demi-court adverse, vu du serveur :

```
 rouleaux 1-2   3-4    5-6
┌──────┬──────┬──────┐  rangées 1-3 : FOND (6 cases par zone)
│  DL  │  DC  │  DR  │
├──────┼──────┼──────┤  rangées 4-5 : COURT (4 cases par zone)
│  SL  │  SC  │  SR  │
└══════╧══════╧══════┘  filet
```

Un **échange** se déroule ainsi :
1. Les rouleaux du bonus tournent : le plateau est tiré par le moteur.
2. Le moteur tire un **coup** dans la table du bonus.
3. Il en déduit les **zones touchées**, la règle propre au coup, Hawk-Eye et les marques.
4. Chaque zone touchée rapporte la **valeur « court »** de ses symboles :

| Symbole | Wild | Ace | Trophée | Sac | Raquette | Balle | Chaussure | Casquette | Gourde | Poignet | Scatter |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Valeur (× mise) | 10 | 0,5 | 0,4 | 0,3 | 0,3 | 0,2 | 0,1 | 0,1 | 0,1 | 0,1 | 0 |

Chaque Scatter d'une zone touchée ajoute **+1 échange** (+2 pour une amortie). Le nombre d'échanges restants est plafonné à 30.

**Marques de terrain.** Elles ont toujours une conséquence réelle :
- une zone marquée qui est touchée de nouveau rapporte **6×** la mise, puis la marque est consommée ;
- une marque non touchée expire après sa durée, compteur visible sur le court ;
- **GRAND SLAM** : si les 6 zones sont marquées en même temps, l'échange rapporte **150×** la mise et toutes les marques sont effacées. C'est la grande récompense du contrôle du court.

## 3. POWER SHOTS (règles distinctes, pas des multiplicateurs)

| Coup | Zones touchées (tirées par le moteur) | Règle propre | Rally Challenge | Grand Final | Championship Point |
|---|---|---|---|---|---|
| RALLY | 1 zone parmi 6 | — | 47 % | 34 % | 0 % |
| ACE | 1 zone de fond | prime 3× + marque 3 échanges | 15 % | 16 % | 30 % |
| SMASH | la zone + ses voisines (3 ou 4 zones) | impact multiple | 12 % | 16 % | 25 % |
| PASSING SHOT | diagonale de 3 zones (4 trajectoires possibles) | traversée du court | 12 % | 16 % | 25 % |
| AMORTIE | 1 zone courte | Scatters ×2 en échanges + marque 2 échanges | 8 % | 10 % | 12 % |
| GOLDEN RALLY | 4 à 8 frappes, chacune sur 1 zone parmi 6 | chaque zone touchée est marquée 2 échanges | 6 % | 8 % | 8 % |

Fréquences mesurées (identiques aux tables, à l'erreur d'échantillonnage près ; un test le vérifie) : Grand Slam dans **4,9 %** des Rally Challenges et **12,6 %** des Grand Finals (4 scatters). Marques posées par bonus : 4,1 (RC) / 8,7 (GF). Marques retouchées : 1,7 / 4,0. Marques expirées : 1,3 / 2,5.

## 4. RALLY CHALLENGE (3 scatters)

- 8 échanges, table « Rally Challenge », sans Hawk-Eye ni Championship Point.
- Ambiance bleu électrique : générique « RALLY CHALLENGE » en 5 s (passable), caméras rapides, bandeau à chaque coup.
- Gain moyen du bonus **44,79× ± 0,01** (écart-type 40,5×, max observé 690×). En moyenne 8,8 échanges joués (prolongations par les Scatters).

## 5. THE GRAND FINAL (4 scatters ou plus)

- **Échanges** : 12 (4 scatters), 14 (5) ou 16 (6). Table plus riche en coups spéciaux.
- **Phase 1, entrée dans le stade** : vue aérienne (dézoom du stade), allumage des projecteurs en trois temps, la foule, la caméra qui descend, puis le tableau « GOLDEN RALLY · THE GRAND FINAL ». Environ 7 s, passable.
- **Phase 2, le match** : Court Control et Power Shots. La progression est un compteur explicite de points gagnants, pas un faux score de tennis (les règles d'égalité/avantage ne s'appliqueraient pas à un compte d'échanges).
- **Phase 3, HAWK-EYE** :
  - Un coup à une seule zone (rally, ACE, amortie) tombe sur la ligne dans 15 % des cas ; c'est mesuré : 1,2 challenge par Grand Final.
  - Le verdict est tiré avant l'animation : **IN dans 60 %**. La zone compte, prime 8× et marque de 3 échanges.
  - **OUT** : rien n'est encaissé et le point est rejoué (+1 échange).
  - Cinématique : son du stade coupé, image désaturée (« figée »), reconstruction au ras du sol, balle au ralenti, trace d'impact, verdict.
- **Phase 4, CHAMPIONSHIP POINT** : l'échange qui commence avec un seul échange restant utilise la table « Championship Point » (coups spéciaux uniquement). La mise en scène suit : silence, poussée de caméra, bandeau. Si un échange supplémentaire est gagné, le match continue (1,15 balle de match par Grand Final en moyenne).
- **Phase 5, CÉRÉMONIE** : seuils publiés.
  - Trophée à partir de 75× gagnés dans le bonus : 43,7 % des Grand Finals, 5,8 % des Rally Challenges.
  - « Champion » à partir de 200× : 11,4 % / 2,4 %.
  - En dessous : un simple récapitulatif. Aucune cérémonie grandiose sur un faible gain.
- Gain moyen **97,78× ± 0,03** avec 4 scatters (écart-type 63,6×, max observé 852×).
- Avec 5 et 6 scatters (même bonus, plus d'échanges) : 114,5× et 131,2×.
- Plus favorable que le Rally Challenge, **sans montant garanti**.

## 6. Architecture « moteur → résultat → événement → cinématique → gain »

Chaque échange consomme exactement deux tirages : les 6 arrêts de rouleaux, puis un vecteur AUX de taille fixe (type de coup, zones, nombre de frappes, ligne, verdict).
- La version scalaire (événements, livres) et la version vectorisée (simulations) consomment les mêmes nombres. Un test les compare sur 1 200 manches rejouées.
- Le port TypeScript rejoue les manches de référence à l'identique (test de parité).
- Une manche se rejoue exactement à partir de ses tirages enregistrés (test).

Événements du livre :

| Événement | Contenu |
|---|---|
| `bonusStart` | type de bonus, nombre d'échanges |
| `exchangeStart` | n°, total, balle de match, marques |
| `reveal` | plateau, valeurs et Scatters des 6 zones |
| `hawkEye` | zone, verdict, prime, point rejoué |
| `shot` | coup, trajectoire, zones touchées (cases, valeur, prime de marque, échanges gagnés), prime, gain, marques posées, Grand Slam |
| `grandSlam`, `markExpire`, `extraExchange` | événements du court |
| `exchangeEnd` | gain, points, total, état des marques |
| `bonusEnd` | total, échanges, points, niveau de cérémonie |

`render/match.ts` lit ces événements : la balle vole vers les zones de `shot.path`, les cases encadrées sont `hits[].cells` et les montants affichés sont `hits[].value` et `markPrize`. Le verdict Hawk-Eye vient de `hawkEye.call`. Passer une séquence (tap) ne fait qu'accélérer les animations : le livre est déjà fixé. Un test vérifie que le total affiché est égal à la somme des coups.

## 7. Cinématiques : ce qui est réalisé, ce qui manque

**Réalisé (PixiJS, 2,5D)** :
- zooms et suivis de caméra, tremblement au smash ;
- trajectoires avec hauteur, ombre au sol, traînées et ondes d'impact ;
- ralenti, image figée et désaturée pour Hawk-Eye, plan en perspective de la reconstruction ;
- allumage des projecteurs et vue aérienne du stade, public qui réagit, confettis, trophée.

Mode rapide, mouvements réduits (pas de caméra ni de tremblement, durées divisées par deux) et passage au tap.

**Non réalisable ici sans ressources supplémentaires** (pipeline proposé) :
- joueur ou joueuse animé(e) qui sert ou smashe : modélisation et rig 3D (Blender) + animations (capture de mouvement), puis rendu en spritesheets ou glTF via Three.js / pixi-3d ;
- Ace animé en squelette (Spine ou DragonBones) à partir de calques séparés de l'illustration ;
- vraie reconstruction Hawk-Eye 3D : scène Three.js du court avec une trajectoire balistique calculée à partir du verdict ;
- plans de foule et de stade filmés ou rendus : séquences vidéo WebM courtes, déclenchées par événement.

Aucun de ces éléments n'est simulé par un placeholder présenté comme final. La version livrée est jouable et entièrement liée aux événements.
