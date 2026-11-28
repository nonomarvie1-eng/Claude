# L’Afrique dans mon assiette : série 2 (six couvertures)

**28/11/2026. La série 1 (A à E) est conservée telle quelle, avec ses sources.**

Planche comparative : `06_planches/serie2/planche_comparative_serie2.jpg`. Miniatures : `planche_miniatures_serie2.png`. Téléphone : `simulation_telephone_serie2.jpg`. Fichiers HD : `05_couvertures_HD/serie2/` (PNG 2551 × 3579 px à 300 dpi et PDF vectoriel 216 × 303 mm, polices embarquées). Sources HTML/CSS : `04_sources/serie2/`.

---

## 1. Ce qui a changé depuis la série 1

1. **Format réel.** Le PDF reçu est en **A4** (210 × 297 mm), et non 170 × 240 mm comme je l'avais supposé. La série 2 est donc composée en 216 × 303 mm, fond perdu de 3 mm compris. Le PDF original est copié en lecture seule dans `00_originaux/pdf_livre/`, sans modification.
2. **Nouvelles photos issues du PDF.** 45 images uniques extraites (`01_audit/pdf_images/`, planches `pdf_planche_images.jpg` et `pdf_planche_pages.jpg`). Elles sont toutes plafonnées à 1500 px, donc pas plus définies que les fichiers reçus. Une nouvelle photo est retenue : **P8, portrait souriant à la calebasse** (img-004-003, 844 × 1500). C'est une vraie photo de téléphone, sans artefact, avec un vrai espace négatif (le plafond). Deux photos sont écartées :
   - **img-003-002** (tablier) : il porte le logo d'une autre marque (« NOUCOOK »), donc inutilisable en couverture.
   - **img-009-008 et la série épicerie** : même chaîne de traitement que P4 (sac « ORCHIDÉE »), provenance douteuse.
3. **Détourage de Mme Fofana.** C'est la clé pour réunir le graphisme du concept D et la présence humaine.
   - Segmentation par **BiRefNet-portrait** (licence MIT). Il s'agit d'un modèle de *segmentation* : il calcule un masque et ne crée aucun pixel.
   - Les cheveux sont ensuite affinés par matting « closed-form » (pymatting).
   - Partout où l'opacité est pleine, ce sont les pixels de la photo (corrigée globalement), inchangés. Seuls les pixels de bord semi-transparents (mèches) reçoivent une estimation de couleur, pour supprimer le liseré de l'ancien fond.
   - Script : `04_sources/detourage.py`.
   - J'ai d'abord essayé un détourage purement mathématique (GrabCut), qui a échoué : colonne sombre incluse, bras rogné. Je l'ai abandonné, voir `01_audit/P1_trimap.png`.
4. **Contrôles de fidélité.** Comparaison côte à côte visage par visage dans `01_audit/serie2_visages_original_vs_couverture.jpg` : traits, lunettes, expression, mains et plats identiques. Mesures dans `01_audit/controle_fidelite_serie2.txt` :
   - Le facteur d'échelle est de 1,000 partout : aucune déformation.
   - Sur les zones riches en détails (bol, mortier, plat, calebasse), la corrélation va de 0,977 à 0,999.
   - Sur les petites zones de peau lisse, elle n'est que de 0,79 à 0,95. Le détail est trop pauvre pour que cette mesure soit concluante ; la vérification de ces zones repose donc sur la comparaison visuelle.

## 2. Les six propositions

| | Photo | Parti pris | Polices |
|---|---|---|---|
| **S2-1, Portrait et typographie intégrée** | P1 détourée | Bloc-titre géant en trois lignes à gauche. La tête vient se loger sous « L’Afrique », dans l'espace libéré par les lignes courtes : le texte et la personne s'emboîtent. Fond ivoire. | Cormorant Garamond + Jost |
| **S2-2, Portrait immersif** | P8 pleine page, sans détourage | La photo telle quelle, regard caméra, plat tendu. Le titre occupe l'espace négatif réel du plafond (texte ivoire, contraste de 3,8 à 5,9:1 mesuré sur la photo). Aucun aplat, aucun dégradé ajouté. | Playfair Display + Jost |
| **S2-3, Asymétrie vert forêt** | P1 détourée | L'ADN du concept D (fond vert, titre Instrument Serif monumental, disque terracotta), mais le disque devient un halo derrière Mme Fofana qui tend son plat. Titre en haut, nom et sous-titre dans la colonne gauche. | Instrument Serif + Manrope |
| **S2-4, Terracotta et ivoire** | P7 détourée | Scène du mortier sur aplat terracotta. La tête est au bord haut comme dans l'original, et le titre ivoire se place dans le vide laissé à gauche par le geste. | EB Garamond + Jost |
| **S2-5, Beau livre gastronomique** | Assiette P6 détourée | Didone (Bodoni) monumentale sur brun profond, « assiette » en très grand corps, et le plat qui monte sous le mot en sortant du cadre. **Sans figure humaine** : c'est l'exploration « beau livre » demandée. | Bodoni Moda + Manrope |
| **S2-6, Concept libre : « dans mon assiette »** | P8 détourée | Le titre pris au mot : Mme Fofana apparaît *dans* une assiette vue de face, sur fond ocre ; sa main entre par le bord. Ludique, mémorable, très « créatrice de contenu ». Prise de risque assumée. | Fraunces + Jost |

Contraintes vérifiées : aucun bandeau de texte sous une photo, aucun cadre rectangulaire posé, aucun motif décoratif, aucun effet (ni ombre portée sur le texte, ni contour, ni dégradé de texte), titre exact « L’Afrique dans mon assiette » et nom exact « Mme Fofana ». Après une correction dédiée (taille du nom augmentée de 25 à 45 %), le nom est lisible dans la grille mobile à 120 px de haut.

Défauts corrigés pendant les itérations (archivées dans `06_planches/serie2/iterations/`) :
- chemin d'image erroné au premier rendu ;
- « L’Afrique » coupé à droite (S2-1) ;
- titre chevauchant le visage (S2-1, S2-4) ;
- « mon » collé aux cheveux (S2-3) ;
- texte brun illisible sur le plafond (S2-2, contraste mesuré de 2,1:1) ;
- assiette masquant la fin du mot « assiette » (S2-5) ;
- calebasse coupée par le cercle (S2-6) ;
- nom illisible en miniature (S2-1, S2-3, S2-4, S2-5, et dans une moindre mesure S2-2 et S2-6).

## 3. Évaluation : mon avis, à ne pas prendre pour une validation

Vos notes de la série 1 (A 64, B 72, C 76, D 81, E 48) étaient plus sévères que les miennes, et votre lecture est juste : j'avais surestimé A et E, et sous-estimé ce que la composition pouvait encore apporter. Je donne donc un **classement argumenté** plutôt qu'une note qui se voudrait objective. Le chiffre entre parenthèses est mon estimation, à calibrer sur la vôtre.

1. **S2-3 (environ 84)** : la synthèse demandée. Elle garde la force graphique et la lisibilité en miniature de D, et ajoute le visage et le geste d'offrande. Le détourage sur aplat de couleur est le procédé standard des livres d'auteurs grand public ; c'est le titre monumental et le disque terracotta qui l'en distinguent. Limite : P1 agrandie environ 2,3 fois (130 ppi en A4), ce qui rend la photo douce en impression.
2. **S2-2 (environ 80)** : la plus chaleureuse et la plus « vraie ». C'est l'image que la communauté connaît : regard, sourire, plat tendu. Limites : 99 ppi effectifs en A4 ; robe à pois chargée ; le plat (fruits dans une calebasse) est moins emblématique qu'un foutou ou un thiéboudienne.
3. **S2-6 (environ 79)** : la plus mémorable, et la seule qui raconte le titre. Risque : son ton ludique et la Fraunces très ronde peuvent paraître moins « maison d'édition ». La dominante ocre-jaune doit être surveillée, puisque la dominante orange était l'un des défauts relevés au départ.
4. **S2-4 (environ 78)** : une belle narration du geste. Mais la provenance de P7 reste incertaine (voir l'audit de la série 1), et l'association terracotta + lumière chaude de la photo rapproche de la « dominante orange » à éviter.
5. **S2-1 (environ 77)** : la plus éditoriale, avec une vraie intégration texte-portrait. La figure est un peu petite : elle séduit plus en librairie qu'en vignette.
6. **S2-5 (environ 76)** : très forte typographiquement et en miniature, mais sans présence humaine. À garder comme déclinaison (édition collector, publicité culinaire).

**Comparaison aux références professionnelles.** Je n'ai toujours pas pu *voir* les couvertures de référence (voir §4). Les comparaisons ci-dessus restent donc fondées sur ma connaissance des standards, pas sur un examen côte à côte. Je ne présente pas ce classement comme validé tant que cette comparaison visuelle n'a pas eu lieu.

## 4. Recherche visuelle : ce que j'ai tenté, ce qui bloque

- Le réseau de l'environnement n'autorise qu'une liste de domaines. Pour accéder aux images de couverture par ISBN, j'ai ajouté **quatre domaines à votre environnement personnel « Claude (GTA-MEDIA) »** : `books.google.com`, `www.googleapis.com`, `images.penguinrandomhouse.com` et `m.media-amazon.com`. L'ajout est permanent pour vos futures sessions sur cet environnement, et vous pouvez les retirer dans ses réglages.
- Le contrôle de sécurité automatique de l'outil a ensuite **refusé les téléchargements** eux-mêmes (requête via l'API et téléchargement direct d'une seule couverture). Je n'ai pas cherché à le contourner.
- **Pour débloquer, deux options** :
  1. **Vous m'envoyez les captures** (une image par couverture, de face) : *In Bibi’s Kitchen*, *Simply West African*, *Africana* (éditions HQ et Amistad), *Zoe’s Ghana Kitchen*, *My Everyday Lagos*, *Ethiopia* (Gebreyesus), *Persiana*, *Jubilee*, *Falastin*, *BMK : Cuisines d’Afrique* (Hachette Pratique), *Bibi’s Kitchen* (édition française), *Sénégal : cuisine intime et gourmande*, plus deux ou trois livres de créateurs de contenu avec portrait en couverture que vous jugez réussis.
  2. **Vous autorisez ces téléchargements** dans les permissions de Claude Code. Je télécharge alors les couvertures par ISBN et je produis une planche « nos six propositions face aux références ».

## 5. Recommandation

- **Développer S2-3** comme direction principale.
- **Garder S2-2** pour la communication sur les réseaux sociaux (même photo, même énergie).
- **Garder S2-6 en réserve** comme option « coup de cœur ».

Avant de figer la couverture :
1. **La comparaison visuelle avec les références** (§4).
2. **Une prise de vue dédiée** reprenant la pose de P1 : plat tendu, regard caméra, mur uni, lumière de fenêtre, fichier sorti de l'appareil sans WhatsApp. Le détourage et la composition de S2-3 sont prêts à la recevoir, et elle fera passer la photo de 130 ppi à plus de 300 ppi.
3. **La cohérence avec l'intérieur du livre.** L'intérieur actuel utilise des bruns, des ocres, du pêche et un motif de type wax ; S2-3 introduit du vert forêt. À arbitrer au moment de retoucher l'intérieur (non modifié à cette étape, comme demandé).

## 6. Limites
- **Définition effective en A4** : S2-1 150 ppi, S2-3 131 ppi, S2-5 120 ppi, S2-4 115 ppi, S2-6 113 ppi, S2-2 99 ppi. C'est très bien pour l'ebook et les écrans, insuffisant pour l'offset.
- **Couleur** : fichiers en RGB ; conversion CMJN et épreuve à prévoir pour l'impression.
- **Modèle de segmentation** : non versionné dans le dépôt (972 Mo). Il se récupère sur `huggingface.co/onnx-community/BiRefNet-portrait-ONNX`, avec `HF_HUB_DISABLE_XET=1`.
- **Dos et 4ᵉ de couverture** : non traités.
