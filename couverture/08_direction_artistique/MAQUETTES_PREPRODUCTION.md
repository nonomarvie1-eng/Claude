# Maquettes de préproduction A1, A2, B1

*Ces maquettes ne sont pas destinées à la commercialisation. Elles servent à valider la composition, la typographie, la palette et le cadrage avant la séance photo définitive. L'intérieur du livre n'a pas été modifié.*

## Fichiers
- **Côte à côte** : `06_planches/maquettes/planche_maquettes_cote_a_cote.jpg`
- **Test des 3 familles** : `06_planches/maquettes/planche_typographies_3x3.jpg` et `typo_miniatures.png`
- **Page de vente mobile** : `06_planches/maquettes/simulation_boutique_mobile.png`. On y voit une grille de résultats « cuisine africaine » mêlant nos maquettes aux vraies couvertures, et une fiche produit.
- **HD** : `05_couvertures_HD/maquettes/{A1,A2,B1}_{bodoni,playfair,cormorant}.png` (A4 + fond perdu, 300 dpi)
- **Sources modifiables** : `04_sources/maquettes/`
  - le titre s'ajuste automatiquement à une largeur cible en millimètres, d'où une comparaison équitable entre polices ;
  - rendu : `node 04_sources/render_maquettes.js`.
- **Photos provisoires** : `04_sources/maquettes_prep.py` et `03_photos_retouchees/maquettes/`
- **Guide photo smartphone** : `09_guide_photo/Guide_photo_smartphone.pdf`

## Photos provisoires : ce qui est réel, ce qui est simulé

| Maquette | Photo | Opérations | Fidélité (sur les originaux) |
|---|---|---|---|
| **A1** | P1 : cuisine, regard caméra, foutou + sauce | Correction globale. **Zone simulée** : environ 25 mm de plafond ajoutés au-dessus de la tête, en miroir flou du plafond réel, pour représenter l'espace que la vraie photo devra avoir. | Visage + bol : NCC 0,997, facteur 1,000 |
| **A2** | P2 : grand plateau tenu au premier plan, regard caméra | Correction globale et recadrage uniquement. La tenue cible (vert forêt ou indigo) **n'existe pas** dans les photos disponibles. | Visage + plateau : NCC 0,989, facteur 1,000 |
| **B1** | P6 entière, **sans détourage**, sur son vrai set en vannerie | Correction globale. **Brûlage local** du set hors de l'assiette (assiette protégée par masque). **Zones simulées** : prolongement en haut et bande sombre à gauche. | Plat : NCC 0,964, facteur 1,000 (l'écart vient du brûlage du décor visible dans la zone mesurée) |

Pour B1, j'ai cherché une vraie photographie de surface sombre sous licence CC0 pour servir de fond provisoire. La seule candidate adaptée (« Wood051 », ambientCG) s'est révélée être une texture **procédurale**, donc générée : je l'ai écartée.

## Typographie : verdict

| Famille | Points forts | Limites | Lisibilité à 90 px |
|---|---|---|---|
| **Playfair Display** (700 / italique 500) | La plus chaleureuse et la plus « généreuse ». Contrastes francs, italique très expressive. | Très répandue (risque d'aspect générique), d'où l'importance de soigner la composition et la couleur. | **La meilleure** |
| **Bodoni Moda** (500 / italique) | La plus « beau livre », dans la continuité de S2-5. | Déliés très fins qui disparaissent en petit ; trou après l'apostrophe, à corriger manuellement (réglé dans les maquettes). | Correcte |
| **Cormorant Garamond** (600 / italique) | Élégante, littéraire. | Trop fine pour une vignette ; manque de présence en vente en ligne. | Faible |

**Recommandation : Playfair Display** comme famille de marque (titre + nom), avec Jost en petites capitales.
- Bodoni Moda reste l'option d'une **édition prestige** reliée.
- Si vous voulez une typographie plus distinctive, une police sous licence payante de même esprit (serif chaleureuse à fort contraste) pourrait être étudiée. Licence « publication » à budgéter.

## Lecture critique des trois maquettes
- **A1** : la plus proche de votre stratégie. Dans la grille de résultats, elle tient la comparaison avec *Zoe’s Ghana Kitchen* et *Simply West African* : visage reconnaissable, plat identifiable, titre lisible. Ce que la vraie photo doit corriger :
  - l'espace au-dessus de la tête (simulé ici) ;
  - les LED et bougies qui rendent l'image orange ;
  - le haut à cœurs ;
  - la définition (900 px via WhatsApp).
- **A2** : la composition centrée et le nom posé sur le mur sombre fonctionnent. Mais le titre brun sur le plafond gris de P2 **manque de contraste en vignette**, et le décor (cartons, radiateur) est encombré. Cette maquette prouve surtout qu'A2 exige **un mur clair et uni** et une tenue de couleur. C'est la plus dépendante de la future séance.
- **B1** : la plus forte en vignette. La hiérarchie de S2-5 fonctionne aussi sur une vraie photo sans détourage, et le set en vannerie assombri donne une texture authentique et sans cliché. Ce que la vraie photo doit apporter : un plat **commun** et généreux plutôt qu'une portion individuelle, une surface sombre réelle, et éventuellement une main.

## Prochaine étape proposée
1. Votre choix de police : je recommande Playfair Display.
2. La séance photo à domicile, selon le guide (4 pages).
3. À réception des originaux : intégration dans les gabarits existants. Les fichiers HTML sont prêts : il suffit de remplacer l'image provisoire et d'ajuster le cadrage.
