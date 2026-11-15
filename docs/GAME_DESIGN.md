# Golden Rally — Conception du jeu

## Identité

- **Nom de travail** : Golden Rally (recherche de marque à faire avant diffusion publique).
- **Univers** : un club de tennis privé, haut de gamme, au crépuscule. Gazon fauché en bandes, terre battue ocre, ivoire, laiton et or. Typographies Cinzel, Marcellus et Poiret One.
- **Ton** : élégant, calme, prestigieux. Pas de mascotte, pas d'élément enfantin.
- **Contraintes juridiques respectées** : aucun joueur réel, aucun tournoi, trophée ou court identifiable, aucune marque d'équipementier, aucun logo de fédération. Le trophée et la chaise d'arbitre sont des dessins génériques originaux.

## Symboles

| Code | Symbole | Rôle | Paiement 3/4/5 (× mise totale) |
|---|---|---|---|
| W | Raquette d'Or | Wild (rouleaux 2-4), remplace tout sauf le Trophée | 2 / 10 / 50 |
| S | Trophée | Scatter, paie partout, déclenche le bonus | 2 / 10 / 50 |
| H1 | Balle d'Or (couronne de laurier) | Haut | 2 / 10 / 50 |
| H2 | Chaise d'arbitre | Haut | 1,5 / 6 / 25 |
| H3 | Tube de balles « CLUB » | Haut | 1,2 / 4 / 15 |
| H4 | Casquette du club | Haut | 1 / 3 / 10 |
| L1 | Médaillon « AD » (avantage) | Bas | 0,5 / 1,5 / 5 |
| L2 | Médaillon « 40 » | Bas | 0,4 / 1,2 / 4 |
| L3 | Médaillon « 30 » | Bas | 0,3 / 1 / 3 |
| L4 | Médaillon « 15 » | Bas | 0,2 / 0,8 / 2,2 |

Les symboles bas utilisent le comptage des points au tennis (15, 30, 40, AD). C'est un clin d'œil thématique qui remplace les habituelles valeurs de cartes.

## Mécanique distinctive : « Rally »

- 3, 4 ou 5 Trophées → 10, 12 ou 15 tours gratuits, plus le gain Scatter (2×, 10× ou 50×).
- Pendant le bonus, chaque Raquette d'Or qui tombe **prolonge l'échange** : le compteur de Wilds collectés augmente. L'augmentation a lieu *avant* le calcul des gains du tour.
- Multiplicateur des gains de ligne : ×1 → ×2 → ×3 → ×4 → ×5 → ×6 → ×8 → ×10. Il est conservé jusqu'à la fin du bonus et matérialisé par un cadran « RALLY ».
- 3 Trophées ou plus pendant le bonus : +5 tours, avec au plus 50 tours restants.
- Gain maximal par tour : 5 000× la mise.

Pourquoi cette mécanique :
- elle est **élégante** : une seule idée, lisible dès le premier bonus ;
- elle crée une **tension honnête**, puisque le multiplicateur est visible et ne redescend jamais pendant le bonus ;
- elle est **exactement calculable** (chaîne de Markov finie), donc vérifiable par un laboratoire.

## Déroulé d'un tour (tout est déjà déterminé avant l'animation)

1. La mise est débitée et le serveur renvoie le « book » complet du tour, bonus compris.
2. Les rouleaux défilent **sur leurs vraies bandes** et s'arrêtent sur les positions du book.
3. Les gains sont présentés : lignes tracées et symboles mis en valeur. Les gains ≤ mise ont un retour sonore discret, sans célébration.
4. Bonus : écran d'introduction, puis chaque tour gratuit. Les Wilds envoient une énergie vers le cadran, le multiplicateur monte, puis vient le récapitulatif.
5. Les gros gains (≥ 10× la mise) déclenchent une célébration qu'on peut écourter d'un toucher ; seul l'affichage est accéléré, le montant reste le même.

## Accessibilité et confort

- Mode « réduire les animations » : il suit aussi le réglage système `prefers-reduced-motion`.
- Mode rapide, désactivable par juridiction.
- Volumes séparés : général, musique et effets.
- Coupure automatique du son quand l'onglet est masqué.
- Interface en HTML, avec libellés ARIA et navigation au clavier ; la barre d'espace lance le tour.
- Langues : français et anglais. Les autres langues Stake retombent sur l'anglais en attendant une traduction.

## Production des ressources (100 % pilotée par code)

- **Visuels** : `game/art/build-art.mjs` dessine chaque symbole, le décor, le cadre, le logo et le cadran en SVG par programme (géométrie, dégradés métalliques, ombres). `rasterize.mjs` les rend en PNG haute définition avec Chromium.
- **Sons** : `game/audio/synth.py` synthétise tout : coups de balle, rebonds, swoosh de raquette, carillons, applaudissements et deux musiques en boucle parfaite.
- **Pourquoi pas d'IA générative externe** : aucun connecteur d'image ou d'audio n'est disponible dans cet environnement. Les conditions commerciales des services de génération varient et la protégeabilité de leurs sorties est incertaine. La génération procédurale donne au studio **la pleine propriété** des ressources, une reproductibilité totale et un coût nul. Si un rendu encore plus illustratif est souhaité plus tard, voir `ASSETS_AND_LICENSES.md`, section « Évolutions possibles ».
