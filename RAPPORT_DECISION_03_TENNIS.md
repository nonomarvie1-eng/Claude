# Rapport n°3 — Niche tennis — 2026-11-04

## Pourquoi le tennis
Le fondateur joue au tennis et le regarde : c'est la seule niche où notre contenu peut être crédible sans montrer de visage (mains, raquette, court, matériel).
Marché : **1 228 679 licenciés** au 31/08/2025 et **~7 000 clubs** (FFT, via [Sportbusiness.club](https://www.sportbusiness.club/?p=181251) et l'[étude FFT-CDES](https://cdes.fr/wp-content/uploads/2025/11/Synthese-FFT-Vfinale-corrections-avec-nouveau-schema.pdf)).

## Pistes examinées

| Piste | Constat | Verdict |
|---|---|---|
| Surgrips / antivibrateurs | AliExpress : lots de 15–60 surgrips de 3 à 34 $ (plusieurs à 2 000–4 000 ventes) ; grandes marques partout (Wilson, Head, Tourna) ; panier de 1 à 10 € (source sur l'antivibrateur : [Alibaba Reads](https://reads.alibaba.com/?p=125551)) | **Rejeté** : panier trop faible, produit comparé sur le prix |
| Appareil de rebond (« tennis trainer ») | 7 à 50 € en France ([Kaufland](https://www.kaufland.fr/product/512160343/), [TW Europe](https://www.tenniswarehouse-europe.com/Entraineur_de_Tennis_Tretorn/descpageWESTGUT-TTTRAIN-FR.html)), 6–8 $ sur AliExpress | **Rejeté** : générique |
| Pressuriseur de balles | Déjà analysé (Bounce 90–100 €, génériques 20 €) | **Rejeté** (D-008) |
| Vêtements « tennis club » (impression à la demande) | Tendance réelle ([SI](https://www.si.com/onsi/serve/style/how-wilson-dominated-tennis-fashion-in-2025) : Wilson ; Lacoste « tenniscore »), mais grandes marques présentes ; une marque DTC vendue sur Flippa : ~58 k$ de CA avec 80 000 abonnés ([Flippa](https://flippa.com/11928649-profitable-dtc-tennis-fashion-brand-with-44-margins-58k-revenue-2-4m-monthly-reach-and-80k-followers-ready-to-scale-with-paid-ads-and-new-lines)) | **En veille** : faible marge par article, long à construire |
| Cadeaux tennis personnalisés | Affiches avec score/prénoms existantes (FFLOSE), balles personnalisées (Etsy, Zazzle) ([FFLOSE](https://fflose.com/idees-cadeau-tennis)) | **En veille** |
| **Kit de cordage à domicile** (machine + outils + bobine + formation vidéo en français) | Voir ci-dessous | **À VÉRIFIER — piste n°1** |

## Piste n°1 — Kit de cordage à domicile

**Hypothèse :** Nous pourrions vendre un kit « cordez vous-même » (machine à poids tombant + outils + bobine + formation vidéo en français filmée aux mains) aux joueurs de compétition et aux parents de jeunes joueurs, qui paient un cordage à chaque casse. Le kit se positionnerait entre les machines de marque (Gamma Momentum 2 à 419 €) et les machines chinoises sans accompagnement. Sous réserve de vérifier : prix usine, poids et port, qualité, taille réelle de la demande.

**Pourquoi c'est intéressant**
- Problème réel et coûteux : un joueur régulier paie la pose à chaque cordage. Wilson indique 10 à 75 € pour un jeu de cordage seul ([Wilson](https://www.wilson.com/fr-fr/blog/tennis/how-tos/how-choose-tennis-string)) ; la pose en magasin (~20–30 €) **n'est pas vérifiée**.
- Bobine de 200 m = ~18 cordages : Babolat RPM Blast à 118,99 € chez Decathlon Pro ([Decathlon Pro](https://www.decathlonpro.fr/cordage-de-tennis-monofilament-rpm-blast-1-25mm-noir-200m-id-8340557.html)), bobines génériques à 20–45 $ sur AliExpress. → **Achat répété naturel** (bobines, pinces, alênes).
- **Peu saturé sur AliExpress** : machines à poids tombant à 180–260 $, mais seulement 1 à 3 ventes par annonce (relevé du 2026-11-04). Le client ne voit pas une version à 5 € à côté de la nôtre.
- Contenu sans visage idéal : tutoriels de cordage filmés aux mains, comparatifs de cordages, tension et sensations.
- Panier élevé (~349 €) → CPA max confortable si le coût d'achat est bon.

**Économie unitaire** (`tools/unit_economics.py`)
| Scénario | Prix | Marge avant pub | CPA max |
|---|---|---|---|
| Machine achetée au prix AliExpress (223 $) | 349 € | **−41 €** | non viable |
| Prix usine ~100 € (non vérifié) | 349 € | 98 € (28 %) | 98 € |
| Optimiste | 349 € | 142 € (41 %) | 142 € |
Au-dessus de 150 €, il n'y a plus de droit forfaitaire de 3 € mais des droits normaux, la TVA à l'import (non récupérable en franchise) et des frais de dédouanement. **Viable uniquement avec un prix usine ~100 €**, à obtenir par devis.

**Pourquoi ça pourrait échouer**
- Marché de niche : combien de joueurs français veulent corder eux-mêmes ? **Inconnu** (aucun volume de recherche disponible).
- Lourd (10–15 kg estimés) : port cher, un retour coûte 30–80 €.
- La précision de la tension est essentielle : une machine imprécise = mauvais avis immédiats chez des joueurs exigeants.
- Concurrence spécialisée : Tennis Warehouse Europe, Tennispro (machines CB10/CB14), Babolat, Tecnifibre.
- Les usines vendent rarement à l'unité en dropshipping pour un produit lourd : il faudra peut-être un agent ou un petit stock.
- Le fondateur doit savoir corder (ou apprendre) pour produire les tutoriels.

**Confiance : faible à moyenne.** C'est la première piste où notre avantage (expertise + contenu) est crédible **et** où AliExpress ne nous concurrence pas directement.

## Étapes de vérification (gratuites d'abord)
1. Le fondateur : sait-il corder ? À quelle fréquence fait-il corder ses raquettes, et à quel prix dans son club ?
2. Mesurer la demande : volume de recherche « machine à corder », « corder sa raquette » ; groupes et forums de tennis.
3. Devis Alibaba (avec accord) : prix usine, poids, port DDP France, dropshipping unitaire possible ou non.
4. Si les étapes 1–3 sont positives : tester une machine (servira aussi au fondateur et aux tutoriels).
