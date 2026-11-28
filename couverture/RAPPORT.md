# L’Afrique dans mon assiette : direction artistique de la couverture

**Rapport de mission, première série de cinq concepts (28/11/2026)**

---

## 0. À lire en premier : trois constats qui conditionnent tout le reste

1. **Le PDF du livre n'a pas été transmis.** Seules 7 images ont été reçues. Le format a donc été fixé par hypothèse à **170 × 240 mm** (format courant des livres de cuisine en France), plus 3 mm de fond perdu, soit **176 × 246 mm**. Toute la mise en page est paramétrée en millimètres (`04_sources/concepts/base.css` et `render.js`) : on pourra l'adapter au format réel dès réception du PDF. Le PDF original n'a pas été touché.
2. **Toutes les photos sont en basse définition** (de 900 × 1600 à 1145 × 1374 px, trois d'entre elles recompressées par WhatsApp). Imprimées sur la couverture, elles donnent **130 à 190 ppi effectifs**, alors que l'impression offset demande 300 ppi. C'est la limite principale du projet.
3. **Au moins une photo a été générée ou régénérée par IA (P4)**, et la provenance de trois autres (P3, P5, P6) est **incertaine**. P7 présente aussi des indices suspects. Voir l'audit ci-dessous. **Avant toute impression, il faut obtenir les fichiers originaux sortis de l'appareil photo (HEIC/JPEG avec EXIF).**

---

## 1. Audit des photographies

Fichiers copiés en lecture seule dans `00_originaux/` (empreintes SHA-256 dans `SHA256SUMS.txt`). Zooms de contrôle : `01_audit/zoom_controle_1.jpg`, `zoom_controle_2.jpg`, `grilles_reperage.jpg`.

| # | Contenu | Fichier, dimensions | Netteté (variance du laplacien) | Provenance | Potentiel éditorial |
|---|---|---|---|---|---|
| **P1** | Mme Fofana tend un bol de foutou et sa sauce, cuisine en lumière chaude | JPEG 900×1600, 72 dpi, en-tête IPTC typique de WhatsApp, sans EXIF d'appareil | 128 (douce) | **Probablement authentique** : flou d'arrière-plan cohérent avec un mode portrait de smartphone, pas d'artefact. Recompression WhatsApp. | **Fort** : regard caméra, geste d'offrande, plat lisible. Seul vrai portrait « autrice + plat ». Défauts : dominante orange, cadrage 9:16 serré (le titre ne peut aller qu'en bas). |
| **P2** | Riz et sauce feuille sur plateau, intérieur | JPEG 900×1600, WhatsApp | 329 | **Authentique** : décor domestique non mis en scène (cartons, radiateur, sacs). | **Faible pour une couverture** : arrière-plan encombré, lumière mélangée, plat tenu de biais. Utilisable en page intérieure ou sur les réseaux sociaux. |
| **P3** | Portrait en pied, pagne madras, jardin tropical | PNG 1086×1448, sans métadonnées | 249 | **Incertaine** : mêmes dimensions non standard que P4 (image IA avérée), même chaîne de traitement. Traits du visage légèrement différents de P1, P2 et P7. | Pas de nourriture. Envisageable en 4ᵉ de couverture ou en page « autrice », **après vérification**. |
| **P4** | En épicerie, calebasse remplie de produits | PNG 1086×1448 | 491 | **Générée ou régénérée par IA, ÉCARTÉE.** Preuve : le texte du sac de riz est incohérent (« JASMINE RICE**E** », « **BASTRA** SUPER QUALITY », logo « Orchid » illisible), signature classique de la génération d'image. Visage lissé, dents uniformes. | Inutilisable : elle reproduit exactement le problème signalé (« visage artificiellement modifié »). |
| **P5** | Six gâteaux vapeur sur un plateau tressé | PNG 1086×1448 | 464 | **Incertaine** (même chaîne de traitement que P4). Rien d'anormal visible. | Moyen : peu contrasté, faible appétence pour une couverture. Bon pour l'intérieur. |
| **P6** | Poulet grillé, oignons façon yassa, couscous de mil (thiéré), alloco, piment, vue de dessus sur un set tressé | PNG 1086×1448 | 724 (la plus nette) | **Incertaine** : même chaîne que P4. Rendu très lisse, oignons « vitreux » et accentuation très régulière, compatibles avec un passage dans un outil d'« amélioration » par IA. Aucune incohérence anatomique ou textuelle. | **Le meilleur visuel culinaire** : composition circulaire, contrastes, set tressé authentique (bien plus juste qu'un motif « africain » générique). |
| **P7** | Mme Fofana pile le foutou au mortier, assise au sol sur un pagne | JPEG 1145×1374, WhatsApp, recadré | 563 | **Incertaine, à vérifier en priorité** : petites taches brunes irrégulières sur les cœurs du débardeur (artefact fréquent de régénération), peau très lissée, foutou en anneau parfait. Même tenue que P1 : séance probablement réelle, mais l'image a pu être retouchée par IA. | **Le plus fort potentiel narratif** (gestes, transmission, objet patrimonial). Le haut du crâne est coupé dans l'original. |

**Exposition** : aucun écrêtage significatif (moins de 0,5 % de pixels saturés). **Dominante chaude** sur toutes les photos (moyenne R > G > B nettement), ce qui explique l'impression « trop orange » des essais précédents.

### Retouches appliquées (script `04_sources/retouche.py`, journal `03_photos_retouchees/journal_retouche.json`)

Uniquement des opérations globales, identiques sur toute l'image :
- **Balance des blancs partielle** (22 à 30 % de neutralisation « gray world », en lumière linéaire) : la dominante orange baisse, la chaleur d'ambiance reste.
- Exposition +0 à +3 %, contraste +3 à +4 %, saturation −8 à −10 %.
- **Agrandissement Lanczos** (interpolation mathématique, **pas de super-résolution IA**), puis accentuation douce (rayon 1,4 px, 35 %).
- Détourage de l'assiette P6 pour le concept D : **ellipse ajustée automatiquement sur le bord blanc de l'assiette**, avec 3 px de marge et un bord adouci de 1,5 px. Aucun pixel d'aliment n'est touché ; seul un canal de transparence est ajouté.
- Aucune retouche locale, aucun remplissage génératif, aucune modification du visage, des mains ou des plats. Avant/après : `01_audit/avant_apres_retouche.jpg`.

**Contrôle de fidélité** (`01_audit/controle_fidelite.txt`) : chaque zone photo des couvertures finales a été réduite à l'échelle source puis recalée sur l'**original**. Corrélation de 0,987 à 0,999, facteur d'échelle de 1,000 dans les cinq cas : aucune déformation. Les écarts résiduels proviennent uniquement de la correction colorimétrique et du rééchantillonnage.

---

## 2. Synthèse de la recherche éditoriale

**Transparence sur la méthode.** Les pages éditeurs et libraires ci-dessous ont été consultées dans cette session. En revanche, le réseau de l'environnement de travail **bloque le téléchargement des images de couverture** (Amazon, Google Books, Penguin Random House, Open Library, Waterstones…). L'analyse visuelle repose donc sur ma connaissance préalable de ces couvertures, et non sur un examen fait ici. Je préfère le dire plutôt que de prétendre avoir « étudié 20 couvertures ». Pour la prochaine itération, je recommande d'en photographier ou capturer 10 à 15 en librairie : je pourrai alors les analyser image par image.

### Références documentées (liens consultés)
| Ouvrage | Éditeur | Lien consulté |
|---|---|---|
| *In Bibi’s Kitchen*, Hawa Hassan | Ten Speed Press, 2020 ; VF *Bibi’s Kitchen*, Hachette Pratique, 2022 | https://www.penguin.com.au/books/in-bibis-kitchen-9781984856739 · https://www.mollat.com/livres/2660373/hawa-hassan-bibi-s-kitchen-la-cuisine-des-grands-meres-africaines · https://www.manypixels.co/blog/print-design/cookbook-covers-2020 |
| *Simply West African*, Pierre Thiam | Clarkson Potter, 2023 | https://www.penguin.com.au/books/simply-west-african-9780593578025 · https://www.barnesandnoble.com/w/simply-west-african-pierre-thiam/1143797443 |
| *Africana*, Lerato Umah-Shaylor | HQ / Amistad, 2022-2023 | https://aalbc.com/books/9780063277496 · https://www.thebookseller.com/rights/hq-lands-cookbook-celebrating-modern-african-cookery-umah-shaylor-1282070 |
| *Zoe’s Ghana Kitchen*, Zoe Adjonyoh | Mitchell Beazley (Hachette) | https://www.hachette.co.nz/zoe-adjonyoh/zoes-ghana-kitchen · https://www.businesslive.co.za/bd/life/books/2017-04-28-book-review-from-ghana-to-the-globe-with-love/ |
| *The Ghana Cookbook*, F. Osseo-Asare et B. Baeta | Hippocrene, 2015 | https://hippocrenebooks.com/store/p66/The_Ghana_Cookbook.html |
| *Persiana*, Sabrina Ghayour | Mitchell Beazley (Hachette) | https://www.hachette.co.uk/titles/sabrina-ghayour/persiana/9781845339104 |
| *Ethiopia*, Yohanis Gebreyesus | Kyle Books (Hachette) / Interlink | https://hachette.co.uk/titles/yohanis-gebreyesus/ethiopia/9780857834669 |
| *My Everyday Lagos*, Yewande Komolafe | Ten Speed Press, 2023 | https://www.penguin.com.au/books/my-everyday-lagos-9781984858948 · https://www.culturedmag.com/article/2023/12/05/yewande-komolafe-lagos-cookbook |
| *The Contemporary African Kitchen*, A. Smalls et N. Oduro | Hachette | https://www.hachette.co.nz/alexander-smalls-nina-oduro/the-contemporary-african-kitchen-home-cooking-recipes-from-the-leading-chefs-of-africa |
| *BMK : Cuisines d’Afrique de Paris à Bamako* | Hachette Pratique, 2026 | https://www.mollat.com/livres/3406420/abdoulaye-djikine-bmk-cuisines-d-afrique-de-paris-a-bamako |
| *La cuisine du Sénégal*, Coumba Diop | Hachette Pratique, 2010 | https://www.afrik.com/la-cuisine-senegalaise-racontee-par-coumba-diop |
| *Sénégal : cuisine intime et gourmande*, Y. N’Dour et I. Rozenbaum | La Martinière, 2014 | https://www.mollat.com/livres/1584964/youssou-n-dour-senegal-cuisine-intime-et-gourmande |
| *Goûts d’Afrique*, collectif | Mango, 2019 | https://www.e.leclerc/fp/gouts-d-afrique-recettes-et-rencontres-cartonne-9782317022159 |
| *Grain d’Afrique*, Aïssatou Mbaye | Beau livre | https://actualitte.com/livres/880155/extraits/grain-d-afrique-aissatou-mbaye-9791032312186 |
| *Cuisines d’Afrique vegan*, Marie Kacouchia | — | https://www.mollat.com/livres/2560556/marie-kacouchia-cuisines-d-afrique-vegan |
| Article : la stratégie de couverture des livres de cuisine | — | https://www.yahoo.com/lifestyle/cover-story-why-rarely-see-224157031.html · https://food52.com/blog/13085-food52-s-two-new-cookbooks-the-covers-we-rejected-along-the-way |

Références complémentaires issues de ma connaissance préalable, **sans lien consulté dans cette session** : *Jubilee* (T. Tipton-Martin), *Falastin* (Sami Tamimi), *Ottolenghi Simple*, *Salt Fat Acid Heat*, *Mexico: The Cookbook* et *Lebanon* (Phaidon), *Zaitoun*, ainsi que les collections « Les recettes culte » et « Fait maison » chez Marabout. Je n'ai trouvé **aucun livre de cuisine africaine chez Marabout** (recherche sans résultat).

### Ce que les couvertures de référence ont en commun
- **Hiérarchie** : le titre occupe 25 à 40 % de la largeur utile, en une ou deux lignes. Le nom de l'auteur est secondaire en taille mais **toujours lisible en miniature** lorsque l'auteur est une marque (Ghayour, Ottolenghi, Thiam).
- **Une seule image forte**, rarement plus. Pour un auteur connu du public (créateur de contenu), le **visage en couverture** se vend mieux. Pour un livre « de référence », c'est le **plat iconique**.
- **Espaces négatifs** : aplat uni ou fond photo calme. Pas de bandeau promotionnel sur les livres d'éditeurs haut de gamme (ou alors sur un sticker amovible).
- **Identité culturelle** : les meilleurs titres africains récents (*In Bibi’s Kitchen*, *Simply West African*, *My Everyday Lagos*) évitent le motif wax en fond plein et passent par **la couleur, les objets réels (vaisselle, textile, vannerie) et la typographie**. Le motif décoratif « africain » générique est précisément ce qui rend une couverture amateur.
- **Typographie** : serif à contraste (Garamond, Didone, serif « soft ») associée à une linéale discrète en capitales espacées, sur deux familles au maximum.
- **Prix perçu** : il monte avec la retenue (moins d'éléments, plus de marge) et baisse avec le nombre d'effets (ombres portées sur le texte, contours, dégradés, bandeaux).

---

## 3. Les cinq concepts

Fichiers HD (PNG 2079 × 2906 px à 300 dpi et PDF vectoriel avec polices embarquées) dans `05_couvertures_HD/`. Planche comparative : `06_planches/planche_comparative.jpg`. Miniatures : `06_planches/planche_miniatures.png`. Simulation sur téléphone : `06_planches/simulation_telephone.jpg`. Trois itérations de correction sont archivées dans `06_planches/iterations/`.

| | Image | Composition | Intention |
|---|---|---|---|
| **A, Portrait d'autrice** | P1 en pleine page | Photo sur environ 82 % de la hauteur, bandeau ivoire en bas séparé par un filet terracotta ; titre à gauche, « Mme Fofana » à droite, lignes de base alignées | La personne que la communauté connaît, qui « tend le plat » au lecteur |
| **B, Transmission** | P7 intacte, en fond perdu à droite et en bas | Bandeau vert forêt au-dessus et marge verte à gauche : l'image est posée comme une planche ; le regard va du titre aux mains, puis au mortier | Le geste, le savoir-faire, la filiation |
| **C, Gastronomie** | P6 avec son set tressé | En-tête typographique ivoire (environ 32 %), photo carrée en dessous ; nom en haut à droite | L'envie : « je veux cuisiner ça » |
| **D, Afrique contemporaine** | Assiette P6 détourée | Aplat vert forêt, titre très grand en Instrument Serif, assiette sortant du cadre à droite, disque terracotta décalé comme un soleil ou un plat de terre | Graphique, affirmé, lisible à 60 px |
| **E, Édition de prestige** | Détail de P1 : les mains qui tendent le plat | Toile indigo, double filet ocre, composition centrée classique, encart photo encadré | Beau livre, cadeau, édition reliée (dorure ocre possible) |

---

## 4. Évaluation (sur 100) : notation volontairement sévère

| Critère (barème) | A | B | C | D | E |
|---|---|---|---|---|---|
| Authenticité photographique (20) | 16 | 11 | 12 | 12 | 16 |
| Composition (15) | 11 | 13 | 12 | 12 | 11 |
| Typographie (15) | 12 | 13 | 12 | 13 | 12 |
| Attractivité commerciale (15) | 12 | 12 | 13 | 12 | 8 |
| Identité visuelle (10) | 6 | 8 | 7 | 9 | 7 |
| Mise en valeur de Mme Fofana ou de sa cuisine (10) | 9 | 10 | 8 | 7 | 6 |
| Lisibilité en miniature (5) | 4 | 3 | 4 | 5 | 3 |
| Qualité technique (5) | 2 | 3 | 3 | 3 | 4 |
| Intemporalité (5) | 3 | 4 | 4 | 3 | 5 |
| **Total** | **75** | **77** | **75** | **76** | **72** |

**Justifications**
- **A (75)** : la plus « honnête » photographiquement et la plus efficace pour la communauté (le visage fait vendre auprès de ses abonnés). Mais c'est la photo la moins définie, étirée ×2,31 (130 ppi), avec un léger flou visible à 100 %. La structure photo + bandeau est éprouvée mais peu distinctive. Identité africaine faible : elle repose sur le plat et le pagne, presque masqué.
- **B (77)** : le meilleur concept éditorial. Il raconte quelque chose : geste, objet patrimonial, regard vers le plat. Le vert et l'ivoire donnent la retenue d'un livre d'éditeur. **Pénalisé par l'authenticité incertaine de P7.** Si l'original confirme l'absence de retouche IA, la note monte à environ 83. Titre un peu petit en miniature.
- **C (75)** : grand classique de librairie, très appétissant. Le set tressé apporte une identité juste et non clichée. Moins de personnalité que A ou B ; provenance de P6 à confirmer.
- **D (76)** : la plus forte en miniature et la plus « maison d'édition contemporaine ». Le détourage est géométrique et propre, mais une assiette détourée perd l'ancrage de son décor : c'est le parti pris le plus « graphique » et le moins « famille ». Provenance de P6 à confirmer.
- **E (72)** : la plus intemporelle et la plus haut de gamme en grand format, mais faible en vente en ligne (encart trop petit en miniature). À réserver à une édition reliée ou collector.

**Comparaison avec les références** : aucun concept n'atteint le niveau de *In Bibi’s Kitchen* ou de *Simply West African* (environ 90 et plus selon ce barème). L'écart **ne vient pas de la mise en page** : trois itérations ont corrigé collisions, alignements et recadrages, et une quatrième n'apporterait presque rien. **Il vient de la matière photographique** : définition insuffisante, lumière d'intérieur mélangée, provenance incertaine. Les couvertures des éditeurs de référence reposent sur des prises de vue réalisées *pour* la couverture, avec de l'espace prévu pour le titre.

---

## 5. Recommandation finale

1. **Direction recommandée : B (Transmission)**, à condition de récupérer l'original de P7 et de vérifier qu'il n'a pas été régénéré. C'est le concept qui différencie le livre (patrimoine, gestes) tout en mettant Mme Fofana au centre, et qui tient la comparaison avec les références sur le plan de la retenue.
2. **Solution de repli immédiate : A**, si P7 ne peut pas être authentifiée. P1 est la photo la plus sûre.
3. **Déclinaison** : D comme visuel publicitaire et vignette de boutique en ligne (excellente lisibilité), E pour une future édition reliée.
4. **Pour une version imprimable de niveau éditeur : refaire la photo de couverture** en reprenant exactement la mise en scène de B (ou de A). C'est l'investissement qui fera passer la couverture d'environ 77 à plus de 88.

### Cahier des charges de la séance photo de couverture
- **Appareil** : hybride ou reflex d'au moins 24 Mpx, en RAW. À défaut, iPhone 14 Pro ou plus récent en ProRAW 48 Mpx, **envoyé en fichier** (AirDrop, WeTransfer, câble) et **jamais via WhatsApp ou Instagram**.
- **Lumière** : une seule source, fenêtre latérale ou grande boîte à lumière à 45°, réflecteur blanc côté ombre. **Éteindre les LED chaudes et les bougies**, qui causent la dominante orange.
- **Cadrage** : vertical 4:5, **avec 30 à 35 % d'espace libre au-dessus de la tête** (mur ou fond uni et calme) pour poser le titre, et la tête entière dans le cadre.
- **Plans à réaliser** : (1) B, assise au mortier avec le pilon, de trois quarts face, regard alternativement vers le mortier et vers l'objectif ; (2) A, plat tendu vers l'objectif, à hauteur de poitrine ; (3) plat seul vu de dessus (thiéré-yassa ou foutou-sauce) sur le set tressé, avec 10 cm de marge tout autour ; (4) détail des mains (pilon, puis plat tendu).
- **Fond** : mur uni (ivoire, ocre ou vert sauge) ou textile uni. Le pagne se porte, il ne sert pas de fond.
- **Livraison** : fichiers RAW et JPEG pleine taille, sans filtre ni application d'« amélioration ».

---

## 6. Limites techniques et photographiques rencontrées
- **PDF absent** : format supposé (170 × 240 mm). Le **dos et la 4ᵉ de couverture** ne sont pas traités, car l'épaisseur du dos dépend du nombre de pages et du papier.
- **Définition** : 130 ppi (A), 182 ppi (B), 157 ppi (C et D), 166 ppi (E) en sortie. C'est acceptable pour l'ebook et le web, **insuffisant pour l'offset** (douceur visible à la loupe ; à la distance de lecture, A et C passent de justesse).
- **Couleur** : fichiers en RGB (sRGB). La conversion CMJN (profil FOGRA39 ou PSO Coated v3 selon l'imprimeur) et une épreuve contractuelle restent à faire. Le vert forêt et l'indigo bougeront légèrement.
- **Recherche** : couvertures de référence non visibles dans l'environnement (téléchargement d'images bloqué) ; voir §2.
- **Aucun outil génératif** n'a été utilisé pour les images. Le détourage par IA (rembg et similaires) a été volontairement exclu au profit d'un détourage géométrique.
- Un dossier `couverture/fonts/` contient des fichiers de police fragmentés issus d'un premier téléchargement inutilisable. L'environnement m'a empêché de le supprimer ; il est exclu du dépôt git et **peut être supprimé manuellement**.

---

## 7. Organisation des fichiers
```
couverture/
├── RAPPORT.md                  ← ce document
├── 00_originaux/               photos reçues, en lecture seule + SHA256SUMS.txt
├── 01_audit/                   zooms de contrôle, grilles, avant/après, contrôle de fidélité
├── 02_recherche/               (références : voir §2)
├── 03_photos_retouchees/       retouches + agrandissements + assiette détourée + journal JSON
├── 04_sources/                 FICHIERS SOURCES MODIFIABLES
│   ├── concepts/               A…E en HTML/CSS (texte réel, cotes en mm) + base.css
│   ├── polices/                polices OFL (TTF) + CSS
│   ├── retouche.py             pipeline photo reproductible
│   ├── render.js               rendu PNG 300 dpi + PDF (node render.js [A B …] [--guides])
│   └── planches.py             planches comparative, miniatures, téléphone
├── 05_couvertures_HD/          A…E en .png (2079×2906, 300 dpi) et .pdf (176×246 mm)
├── 06_planches/                comparative, miniatures, simulation téléphone, iterations/
└── 07_charte/                  palette.png + charte_typo_couleurs.md
```
**Modifier une couverture** : éditer le fichier HTML (textes, tailles en mm, couleurs), puis lancer `node 04_sources/render.js B`. Pour afficher les repères de coupe et de marge : `node 04_sources/render.js B --guides`.
