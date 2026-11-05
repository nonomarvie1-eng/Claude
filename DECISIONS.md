# DECISIONS

## D-001 — 2026-11-04 — Aucun produit validé
Décision : aucune opportunité ne passe le jalon 1 complet. Deux pistes sont gardées pour vérification, une en veille, sept rejetées.
Justification : les prix fournisseurs, volumes de recherche et prix Amazon.fr n'ont pas pu être vérifiés (accès bloqué). Sans eux, la marge et la demande restent des hypothèses.

## D-002 — 2026-11-04 — Seuil de prix minimum ~50 € pour un produit expédié de Chine
Justification : depuis le 1er juillet 2026, droit UE de 3 € par catégorie d'article + TVA import (non récupérable en franchise) + frais de traitement UE (montant inconnu, 0–2 €). Sur un produit à 30 €, cela pèse 13–20 % du prix. Le modèle (`tools/unit_economics.py`) montre une marge pessimiste proche de zéro pour les paniers ≤ 35 €.
Exception : panier relevé par des lots (ex. 2 kits = une seule catégorie tarifaire, un seul droit de 3 € — à confirmer).

## D-003 — 2026-11-04 — Rejets
Filtre de douche (promesse anticalcaire non tenue selon test indépendant), masque de sommeil 3D (guerre des prix), masque lesté (brevet), tabouret WC (encombrant, concurrent FR made in France), tapis d'acupression (allégations santé), mouth tape (risque santé et réglementaire), accessoires espresso (panier trop faible, compatibilité). Détail : `OPPORTUNITIES.csv`.

## D-004 — 2026-11-04 — Pas d'objectif Noël 2026
Échantillon + boutique + délais Chine → impossible de garantir des livraisons avant Noël sans précipiter les jalons 3 à 5.

## D-005 — 2026-11-04 — Le client ne paiera jamais de frais à la livraison
Toute offre devra être en DDP (droits et TVA réglés en amont). Un client qui reçoit une demande de paiement du transporteur = remboursement, mauvais avis et risque de litige.

## D-006 — 2026-11-04 (soir) — L'aiguiseur passe sous le seuil avec les prix réels
Données AliExpress relevées : un modèle de qualité correcte coûte 28–32 $ (prix public), les basiques 4–7 $. Avec ce coût, marge 18 % à 59,90 € et 28 % à 69,90 € (CPA max 10–20 €). Seuil fixé : 35 % et CPA max ≥ 20 €. → Piste maintenue **uniquement** si un devis fournisseur (CJ ou usine) donne ~15 € rendu pour une qualité vérifiée. Sinon, abandon.

## D-007 — 2026-11-04 (soir) — Pas de contournement des protections anti-robot
Amazon.fr bloque les requêtes automatisées : relevé à faire manuellement (10 min) plutôt que de contourner.

## D-008 — 2026-11-04 (nuit) — Les trois pistes restantes sont rejetées
Source : captures Google Shopping France fournies par le fondateur (relevé : `data/google_shopping_2026-11-04.csv`).
- **Aiguiseur** : au moins 4 boutiques françaises paient déjà des pubs sur le même produit générique (mêmes photos), et AliExpress s'affiche dans le même carrousel à 4,79–14,69 €.
- **Kit crochet** : Mypeluchic occupe exactement notre positionnement (5 annonces, 29,99–49,90 €). Nature & Découvertes vend aussi des kits débutant « avec vidéos ».
- **Pressuriseur padel** : premium (Bounce ~90–100 €) et entrée de gamme (~20 €, Decathlon, Amazon, AliExpress) déjà pris.

**Leçon :** un produit générique chinois vendu en France se retrouve à côté de sa propre version AliExpress sur Google Shopping. Avec le droit de 3 € et des délais de 6–14 jours, ce modèle n'offre pas de raison crédible de nous choisir.

**Nouveaux critères pour la prochaine recherche** (au moins un obligatoire) :
1. **Stock en Europe** (fournisseur UE qui accepte le dropshipping) : pas de droit de 3 €, livraison en 2–5 jours, un vrai avantage face à AliExpress.
2. **Personnalisation** (gravure, prénom, contenu sur mesure) : la comparaison de prix devient impossible.
3. **Produit absent d'AliExpress** sous la même forme (fabricant ou artisan européen).

## D-009 — 2026-11-04 — Recherche n°2 : modèles d'approvisionnement
- AliExpress avec stock UE : utile pour la logistique seulement. Le client voit la même annonce AliExpress, elle aussi livrée vite.
- BigBuy / grossistes UE : rejetés (abonnement 69–120 €/mois + ~90 € d'inscription, produits vendus partout).
- Impression à la demande UE (Gelato/Printful) : seule voie qui rend la comparaison de prix impossible, mais niches génériques saturées (ex. affiches de course : The Post Trace à 18 €).
- La niche doit partir d'une expertise ou d'une passion du fondateur. Question posée au fondateur. Détail : `RAPPORT_DECISION_02.md`.

## D-009 — 2026-11-04 — Recherche n°2 : modèles d'approvisionnement
- AliExpress avec stock UE : utile pour la logistique seulement. Le client voit la même annonce AliExpress, elle aussi livrée vite.
- BigBuy / grossistes UE : rejetés (abonnement 69–120 €/mois + ~90 € d'inscription, produits vendus partout).
- Impression à la demande UE (Gelato/Printful) : seule voie qui rend la comparaison de prix impossible, mais niches génériques saturées (ex. affiches de course : The Post Trace à 18 €).
- La niche doit partir d'une expertise ou d'une passion du fondateur. Question posée au fondateur. Détail : `RAPPORT_DECISION_02.md`.

## D-010 — 2026-11-04 — Niche tennis retenue comme terrain de recherche
Raison : le fondateur joue au tennis et le regarde → contenu crédible sans visage. Piste n°1 à vérifier : **kit de cordage à domicile** (`RAPPORT_DECISION_03_TENNIS.md`). Viable seulement avec un prix usine ~100 € pour la machine. Surgrips, appareil de rebond et pressuriseur rejetés ; vêtements et cadeaux personnalisés en veille.

## D-011 — 2026-11-04 — Kit de cordage abandonné
Le fondateur ne sait pas corder, ne souhaite pas apprendre et joue occasionnellement, pour le plaisir. Or l'avantage de cette piste reposait sur une expertise crédible (tutoriels, conseils) face à des clients exigeants. Sans elle, il ne reste qu'un produit lourd, cher, à risque de retours, vendu face à des spécialistes (Tennispro, Tennis Warehouse). → **Rejeté.**
Constat honnête : après 3 recherches (14 pistes produits, 4 modèles d'approvisionnement), aucune piste ne combine demande prouvée + différenciation + économie unitaire compatible avec le profil (débutant, sans visage, sans expertise métier, 500–1 000 €). Le choix de la suite revient au fondateur (options dans NEXT_ACTIONS.md).

## D-012 — 2026-11-04 — Recherche hors tennis : une piste à tester
Marque de designs dédiée à une race de chien, imprimée à la demande en Europe (`RAPPORT_DECISION_04_AUTRES_UNIVERS.md`). C'est le risque en capital le plus faible trouvé, mais avec une marge faible (CPA max 8–18 €) : la croissance devra venir du contenu et de la communauté, pas de la pub. Moto, auto, bricolage, fitness et tapis gaming rejetés.

## D-013 — 2026-11-04 — Race choisie et designs par IA
- Le fondateur n'a pas de chien et ne paiera pas d'illustrateur. Designs générés par IA puis **retravaillés** : une image IA brute est probablement non protégée en France, donc copiable par un concurrent.
- Race choisie sur données : **berger australien** (~14 600 naissances LOF en 2025, 4 robes distinctes → personnalisation). Plan B : golden retriever.
- Étape suivante à coût nul : compte Instagram/TikTok pendant 30 jours (`PLAN_TEST_30J.md`), décision selon les demandes d'achat spontanées.
- Risque signalé : sans chien ni lien personnel avec la race, le ton doit rester juste. S'appuyer sur la communauté (avec autorisations) plutôt que de feindre une expérience de propriétaire.

## D-014 — 2026-11-04 — Leçon de l'exemple « Lanoxie » (déboucheur en poudre)
Exemple montré par le fondateur (vidéo TikTok d'un coach) : produit banal de résolution de problème, consommable, marque propre, prix Alibaba 0,62–0,84 € l'unité dès 50 pièces, ~40 pubs Meta actives (FR, BE, CA), ~15 000 visites/mois (estimation Trendtrack, non vérifiée).
**Ce qu'on retient (le fondateur a raison) :** un produit « ennuyeux » peut fonctionner s'il règle un problème, se rachète, porte une vraie marque et que la vente est bien faite. Notre filtre ne doit pas exiger un produit révolutionnaire.
**Ce qu'on ne copie pas :**
- Produit chimique : déboucheurs généralement classés dangereux (pictogramme corrosif, « Danger »), étiquetage CLP en français, code UFI et déclaration aux centres antipoison obligatoires. L'allégation « désinfecte » relève a priori du règlement biocides : vérification séparée nécessaire. Transport aérien de matières dangereuses restreint. Coût et risque juridique trop élevés pour nous.
- Avis Trustpilot partagés (« toujours bouché », accusation de faux avis) : la pub ne prouve ni la satisfaction ni la rentabilité.
- Les chiffres viennent d'une vidéo de coach qui vend une formation : biais du survivant.
**Changement de modèle à envisager :** prix de gros très bas (50 pièces < 50 €) → un **micro-stock en marque propre** (étiquette FR, stock en France) devient abordable pour des consommables bon marché. C'est ce qui distingue ces marques d'AliExpress : marque, livraison rapide depuis la France, service. Décision du fondateur attendue (accepter 100–200 € de stock ?).
Sources : [Trustpilot Lanoxie](https://uk.trustpilot.com/review/lanoxie.com), [Your Europe — CLP](https://europa.eu/youreurope/business/product-requirements/chemicals/classification-labelling-packaging/index_fr.htm), [EcoMundo — PCN/UFI](https://ecomundo.eu/blog/declaration-pcn-melanges-dangereux-ufi), [INRS](https://www.inrs.fr/risques/classification-etiquetage-produits-chimiques/ce-qu-il-faut-retenir.html).

## D-015 — 2026-11-05 — Modèle « dropshipping avec stock privé » adopté comme piste principale
Le fondateur refuse de gérer les envois mais accepte un stock si l'idée est solide. Modèle : lot à notre marque → entrepôt CJ en UE → CJ expédie. Évite le droit de 3 € par catégorie et par colis, et livre plus vite qu'AliExpress. Candidat n°1 : kit anti-bouchon sans chimie (marge estimée 43–46 %). Candidat n°2 : surgrips à notre marque. Détail : `RAPPORT_DECISION_05_CONSOMMABLES.md`. Le test berger australien reste possible en parallèle (0 €).

## D-016 — 2026-11-05 — Lecture de la Meta Ad Library : vendre la solution d'urgence, pas la prévention
Constats (`data/meta_ad_library_2026-11-05.md`) :
- La demande payante existe sur le **débouchage** (Lanoxie : plusieurs créations actives ; Carrefour/Canard).
- La **prévention non chimique** est presque vide (« attrape cheveux » : 0 pub ; 1 seul vendeur de filtre d'évier). Cela peut être une opportunité, ou le signe que les gens n'achètent pas avant d'avoir le problème.
- Lanoxie monte son panier avec des lots (« 3 achetés + 2 gratuits »).
**Décision :** repositionner le kit sur l'**urgence**. Produit vedette = la tige débouche-canalisation (mécanique, sans chimie) : « Débouchez votre douche en 30 secondes, sans produit corrosif ». Les autocollants et le filtre deviennent la suite logique (« pour que ça ne revienne pas ») et les recharges. Offres en lots pour monter le panier.
**Limite honnête à afficher :** une tige mécanique retire les bouchons de cheveux proches de la bonde (douche, lavabo). Elle ne règle pas un bouchon profond ou de graisse en cuisine. Ne pas promettre plus.

## D-017 — 2026-11-05 — Contre-expertise d'une autre IA : adoptée en grande partie
**Erreurs corrigées dans nos calculs :**
- **Cotisations micro-entrepreneur oubliées** (~12,3 % du chiffre d'affaires en achat-revente, + 0,1 % formation, hors ACRE ; taux 2026 à confirmer). Ajoutées au modèle. Nouvelles marges avant pub : kit 24,90 € → **7,59 €** (30 %), double kit 34,90 € → **11,60 €** (33 %). Aiguiseur, surgrips et mugs baissent aussi.
- **Réachat surestimé** : les autocollants peuvent durer longtemps et le filtre silicone fait doublon. → Rentabilité calculée **sans réachat**.
- **TVA d'un stock en Allemagne ou en Pologne** : un stock détenu dans un autre pays de l'UE peut créer des obligations de TVA dans ce pays. La franchise française ne couvre pas automatiquement ce montage. → **Privilégier un stock en France** (logisticien français), ou faire valider le montage CJ par le service des impôts des entreprises (SIE) ou un comptable avant tout achat.
- Douane : le droit de 3 € vise tous les envois hors UE (pas seulement la Chine), par catégorie tarifaire. Un kit vendu comme assortiment n'a pas forcément 3 catégories. Frais de traitement de 2 € par catégorie annoncés à partir du 01/11/2026 (selon l'autre IA, citant la douane ; à vérifier).
**Points adoptés :** pas de stock personnalisé maintenant ; échantillons et essais réels avant toute promesse ; message prudent (« Retirez les cheveux accessibles près de la bonde, sans déboucheur corrosif ») au lieu de « 30 secondes » ; réserve de trésorerie de 150–250 € ; responsabilité de fabricant au sens du GPSR si vente sous notre marque.
**Conséquence :** avec 7,59 € de marge par kit, la publicité payante est quasi impossible à rentabiliser. Le projet n'est viable que si (a) le contenu organique génère les ventes, ou (b) le prix ou l'offre montent sans perdre l'acheteur. À tester avant d'engager du stock.

## D-018 — 2026-11-05 — Le kit anti-bouchon devient une référence, pas un choix ; nouveau filtre pour la recherche n°6
Le fondateur veut chercher mieux avant de choisir. D'accord : le kit sert de **référence** (les devis CJ, gratuits, restent utiles pour comparer).
**Leçon tirée de Lanoxie et de nos calculs :** ce qui fait vivre ces marques n'est pas l'originalité, c'est l'**écart entre le prix de vente et le coût** (poudre ~0,80 € vendue en lots à ~30–40 €). Notre kit est trop faible sur ce point (24,90 € pour ~10 € de coût rendu, livraison comprise).
**Filtre recherche n°6 (tous obligatoires) :**
1. Coût produit livré ≤ ~20 % du prix de vente (multiplicateur ≥ 5).
2. Panier ≥ 35 € (produit seul ou lot logique).
3. Léger (< 300–400 g) pour limiter le port.
4. Ni chimie, ni électricité/batterie, ni allégation santé, ni tailles.
5. Problème concret, démontrable en vidéo filmée aux mains.
6. Annonceurs actifs en France (preuve de demande), sans saturation.
7. Marge après cotisations ≥ 15 € par commande.
Répartition : je cherche et chiffre les candidats ; le fondateur vérifie la Meta Ad Library et Google Shopping sur les 3–5 meilleurs (captures).

## D-019 — 2026-11-05 — Recherche n°6 : un seul candidat passe le filtre
Collier gravé portrait/prénom d'animal en dropshipping (sans stock) : marge estimée 18,81 € après cotisations (pessimiste 7,21 €). Kit anti-poils, râteau et serviettes auto rejetés (marges de 6 à 11 €). Enseignement : il faut des produits très légers, personnalisés ou à forte valeur perçue, vendus ≥ 40–45 €. Détail : `RAPPORT_DECISION_06.md`.

## D-020 — 2026-11-05 — Catégorie retenue : le cadeau personnalisé
Preuve par la Meta Ad Library (4 séries de captures) : hors santé/beauté, les pubs qui durent le plus (14 mois à 3,5 ans) vendent toutes des cadeaux personnalisés. Avantages pour nous : pas de comparaison de prix, pas de stock (fabrication à la commande), règles simples, contenu facile sans visage, l'IA aide à créer les visuels. Trois candidats finalistes : pendentif gravé, plaque métal humoristique avec avatar, portrait/aquarelle d'animal à partir d'une photo. Choix final à faire avec le fondateur.

## D-021 — 2026-11-05 — Pendentif prénom générique abandonné ; règle « passion + personnalisation »
Le bijou prénom gravé est occupé par de grosses plateformes (Callie, Candychristy, My Little Necklace). Règle retenue : un objet personnalisé **ciblé sur une passion ou un public précis**, comme la plaque « accro aux plantes » (17 mois de pub), l'étui à médiators gravé ou les boules de pétanque gravées. Fin de la chasse : il faut maintenant choisir la niche.

## D-022 — 2026-11-05 — Produit choisi (par délégation du fondateur) : plaque personnalisée chien/chat
Le fondateur me confie le choix. Décision : plaque alu personnalisée (race, robe, prénom, phrase drôle), positionnée cadeau/déco. Prix : 39,90 € (1) / 54,90 € (2). Marge estimée ~14 € / ~20 €. Test pendant la période de Noël si les échantillons sont bons. Plan : `PLAN_LANCEMENT.md`. Prochaine dépense (échantillons ~15 €) soumise à l'accord du fondateur.

## D-023 — 2026-11-05 — Design retenu : style ChatGPT, reproduit dans notre outil (v3)
Le design proposé par ChatGPT est jugé meilleur que nos v1/v2 (médaillon du prénom sur le poitrail, bandeau ATTENTION en arc, ruban bas). Mais l'image ChatGPT fait 1024×1536 px (~130 dpi à 20×30 cm) et devrait être regénérée à chaque commande, avec un risque de fautes. → Style reproduit dans `tools/make_plaque_v3.py` à 300 dpi, avec prénom, phrase et titre modifiables en quelques secondes. Fichier échantillon : `designs/plaque_v3_max.png`.

## D-024 — 2026-11-05 — Design final : ChatGPT v2 (jardin, plaque vintage patinée)
Rendu jugé nettement plus désirable que nos versions faites en code. Fichier d'impression : `designs/plaque_finale_max_impression.png` (agrandi de 1024×1536 à 2362×3543, netteté vérifiée sur un zoom du visage). Pour la vente : obtenir une version au cartouche vide afin d'écrire le prénom proprement, et vérifier sur l'échantillon que l'effet « rouille » imprimé ne passe pas pour un défaut.

## D-025 — 2026-11-05 — Chaîne de fabrication validée
Modèle ChatGPT au cartouche vide + `tools/ecrire_prenom.py` (police Lobster, encre bleu-vert, texture conservée) → fichier d'impression 20×30 cm à 300 dpi en quelques secondes, prénoms longs gérés (testé avec « Marguerite »). Visuel de pub : `designs/pub_golden_v2.jpg`. Pour tenir la promesse « l'apparence peut être modifiée », il faut d'autres races : créer un modèle vide par race avec le même prompt ChatGPT.

## D-026 — 2026-11-05 — Gamme de lancement : 5 races
Modèles au cartouche vide dans `designs/modeles/` : golden retriever, berger australien bleu merle, bouledogue français fauve, staffie bringé, labrador noir (races parmi les plus nombreuses en France). Même cadre et même cartouche pour toutes → `tools/ecrire_prenom.py` fonctionne sans réglage. Visuel de pub multi-races : `designs/pub_races_v1.jpg`.

## D-027 — 2026-11-05 — Noms de marque présélectionnés
Recherche web : aucun homonyme trouvé pour « Gâté Pourri », « Rouille & Moustache », « La Patte Rétro » (proches sans conflit direct : série jeunesse « Chien Pourri », chaussures « M. Moustache », animalerie « Patte Blanche »). Recommandation : **Gâté Pourri** (prolonge le slogan « Un chien gâté vit ici », humour affectueux). Plan B : Rouille & Moustache (s'étend aux chats). Vérifications restant au fondateur (accès bloqué ici) : base des marques INPI (data.inpi.fr, classes 6, 20 et 21) et disponibilité du domaine. Dépôt INPI (~190 € pour une classe) reporté après les premières ventes.

## D-028 — 2026-11-05 — Vérification INPI de « Gâté Pourri »
Résultats (captures du fondateur, data.inpi.fr) : marque « POURRI GÂTÉ » n° 4841225, enregistrée le 07/02/2022, classe 25 (vêtements) uniquement ; marque « POURRI GATE » n° 3382246 (classes 18, 25, 28) **expirée** ; société « POURRIS GATES » (commerce d'habillement, 2020).
Analyse : en droit des marques, la protection est limitée aux produits désignés (principe de spécialité). Nos plaques relèvent des classes 6/20 → a priori pas de conflit. Risque si l'on vend un jour des **vêtements** sous ce nom (classe 25 = conflit direct).
Décision : **Gâté Pourri retenu** pour les plaques, avec la règle : jamais de textile sous ce nom. Avant tout dépôt de marque (après les premières ventes), faire valider par un conseil en propriété industrielle.

## D-029 — 2026-11-05 — Domaine gatepourri.fr disponible
IONOS : gatepourri.fr disponible, 6 € TTC la 1re année (prix barré 11 € HT, renouvellement à vérifier). Ne pas prendre le « pack multi-extensions » (prix barré 167 €/an au renouvellement). Achat seul du .fr possible maintenant pour sécuriser le nom (dépense de 6 € soumise à l'accord du fondateur) ; désactiver le renouvellement automatique tant que le projet n'est pas validé.

## D-030 — 2026-11-05 — Rendu de la phrase validé par le fondateur
`tools/generer_plaque.py` : phrase en Abril Fatface, posée lettre par lettre sur l'arc mesuré de la banderole (flèche 100 px), lettres inclinées selon la courbe, espaces conservés, hauteur de lettre fixe. Prénom en Lobster dans le cartouche. Réglage figé pour tous les modèles à deux zones vides (`designs/modeles2/`). Phrases ≤ ~22 caractères recommandées.

## D-031 — 2026-11-06 — Contre-expertise n°2 (ChatGPT) sur Gâté Pourri : adoptée
**Corrections adoptées :**
1. **Règle d'arrêt publicitaire** : « moins de 3 ventes après 150 € » était une erreur (3 ventes = 50 € par vente, très déficitaire). Nouvelle règle : coût par vente cible ≤ 9 € (1 plaque) / ≤ 15 € (duo), en gardant ~5 € par commande. Après 150 € : si le coût par vente dépasse 20 €, on coupe ; entre la cible et 20 €, on change la vidéo ou l'offre avant de remettre de l'argent. Seuils provisoires jusqu'au devis.
2. **Duo** : 54,90 € = -31 % pour ~6 € de marge en plus. Tester 59,90 € et 64,90 € après devis. Duo = une seule adresse de livraison.
3. **Descriptions honnêtes** : « illustration de la race et de la couleur choisies + prénom », pas « portrait de votre animal ». « Plaque en aluminium imprimée, style vintage, effet patiné », pas « émaillée ». Pas d'usage extérieur promis avant d'avoir des éléments sur la tenue aux UV et à la pluie.
4. **Devis à demander** : 1 plaque livrée en France, puis 2 plaques dans le même colis, poste par poste. Demander aussi un devis à un imprimeur européen en direct.
5. **Échantillons** : 1 modèle clair (golden) + 1 sombre (labrador noir), 1 prénom court + 1 long avec accent. Vérifier : netteté, accents, couleurs, patine, matériau réel (alu ou acier), rigidité, emballage, délai réel.
6. **Fiabilité de la personnalisation** : registre des commandes (n°, modèle, phrase, prénom, fichier, suivi) + limite de caractères + aperçu avant validation. Conditions écrites de réimpression du vendeur.
7. **Marque** : la seule différence de classes ne suffit pas à écarter un risque de confusion. Avant d'investir dans le nom (au-delà du domaine à 6 €) : lire les libellés exacts des marques proches, et idéalement un avis d'un conseil en propriété industrielle.
8. **TVA à l'import** : faire confirmer le montage par le service des impôts des entreprises (SIE).
9. **Budget** : réserve ≥ 200 € ; dépenses initiales limitées aux échantillons, une boutique simple et le premier test.
**Nuance** : l'ancienneté d'une pub reste un indice, pas une preuve de rentabilité (déjà noté en D-016/D-020).

## D-032 — 2026-11-06 — Réponses des vendeurs, plan d'échantillons
- hohappyme Official Store : maquette conforme (sans marges blanches), recommande la livraison « AliExpress Standard » payante, délai annoncé **5 à 25 jours** vers la France. Prix 20×30, matériau et réimpression : non précisés.
- FORJN-DECOR Store : « je peux imprimer vos images directement », renvoie vers une annonce à 8,39 €.
- Plan : 1 échantillon chez chacun (A golden « Max » chez hohappyme ; B labrador noir « Héloïse » chez FORJN), fichiers générés par notre outil pour tester le rendu réel du texte. Plafond : ~10 € livrée par plaque.
- Conséquence du délai 5–25 j : promesse « livré pour Noël » impossible à tenir de façon fiable cette année → vendre pour Noël avec une **date limite prudente** ou un message « carte cadeau / plaque après les fêtes » ; décision après réception des échantillons.

## D-033 — 2026-11-06 — Prix réel fournisseur : la marge s'améliore
Panier AliExpress hohappyme : 4,69 € (promo 11.11) + Standard 2,32 € = **7,01 €** (variante « 20×30 cm vertical, infos personnalisées »). Avec droit 3 € + traitement 2 € + TVA import supposés : marge avant pub **≈ 18 €** à 39,90 € (≈ 17 € hors promo), **≈ 28 €** pour un duo à 59,90 €. Coût de pub max par vente à l'équilibre : ~17–18 € (1 plaque), ~28 € (duo). À confirmer : montant des frais d'importation affiché au paiement.

## D-034 — 2026-11-06 — Concurrent direct identifié : evridwearcustom.fr vend déjà des plaques chiens/chats à 24,99 €
Relevé du fondateur : 305 produits, best-seller « Attention zone patrouillée par » (chiens et chats personnalisés, plusieurs animaux par plaque) à **24,99 €** (prix barré 42,99 €), 32 avis ; « accro aux plantes » 37 avis ; « Cette propriété est protégée par » (berger australien) 24,99 €. Style cartoon 3D, plusieurs animaux possibles.
Conséquences :
- Notre 39,90 € est trop cher face au même concept à 24,99 €.
- Marges à notre coût réel : 24,99 € → 6 € (pub quasi impossible) ; 29,90 € → 10 € ; 34,90 € → 14 € ; duo 44,90 € → 16 €.
- **Décision provisoire : prix 29,90 € livraison offerte**, duo 44,90 €. On se distingue par le style (illustration réaliste, plaque vintage patinée), pas par le prix.
- À ajouter si possible : **plusieurs animaux sur une plaque** (leur argument fort).
- Ne pas copier leurs prix barrés : en France, une réduction annoncée doit se référer au prix le plus bas pratiqué dans les 30 jours précédents (art. L112-1-1 C. conso, directive Omnibus) ; un faux prix barré est une pratique trompeuse.
- Réalité à assumer : un acteur installé (305 produits, avis) occupe déjà le créneau. Notre test dira si notre style suffit à vendre à 29,90 €.

## D-035 — 2026-11-06 — Coût réel livré confirmé : 13,00 € TTC par plaque
Écran de paiement AliExpress : 4,69 € + livraison 2,32 € + frais d'import estimés 5,99 € (droits + traitement + TVA, payés à la commande, rien à la livraison) = **13,00 €**. Marge avant pub ≈ 11 € à 29,90 €, ≈ 15 € à 34,90 €. Échantillon A commandé.

## D-036 — 2026-11-06 — Virage : plaques humoristiques à concept (le texte est la vedette)
Le fondateur rejette le style « Attention chien » même premium. Nouveaux concepts validés en principe (`designs/concepts_humour_v1.png`) : **Avis de recherche**, **Affiche de film**, **Accréditation officielle**, **Bienvenue chez…**. Choix recommandé : Avis de recherche en produit vedette (le plus drôle et le plus partageable), Accréditation en n°2 (champs personnalisables). Problème restant : rendu « trop IA » (lisse, brillant, uniforme). Piste : style d'affiche imprimée à l'ancienne (palette limitée, grain, trame, touches de pinceau) plutôt que photoréalisme ; la crédibilité « réelle » viendra des photos du vrai produit.

## D-037 — 2026-11-06 — Sélection des 5 plaques de lancement (sur 10 concepts)
Retenues : **Recherché**, **Max contre l'Aspirateur** (boxe), **Règlement de la maison**, **Accréditation officielle**, **Certificat du meilleur chien du monde**. En réserve : Affiche de film, Météo, Bienvenue. Écartées : Bistrot, Horaires.
À corriger : les 6 nouvelles sont générées en format étroit (~1:2,6) au lieu de 2:3 → à refaire une par une en 2:3. Prévoir des textes au féminin (« gentille fille », « Directrice »). Pour la personnalisation, faire laisser vides les zones contenant le prénom.
