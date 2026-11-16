# Release checklist — Golden Rally: The Final Set (v6)

Légende : ✅ fait et vérifié ici · 🟡 fait, validation supplémentaire nécessaire · ⛔ pas réalisable dans cet environnement / dépend d'un tiers.

## Mathématiques
- ✅ RTP de chaque mode (96,46–96,56 %) dans la fenêtre SDK 96,0–96,7 % ; jeu de base exact, bonus par simulation ciblée (erreur standard ≤ 0,03 point).
- ✅ Monte-Carlo : 20 M tours (Normal, Bonus Chance), 1,92 M tours par achat ; chaque intervalle de confiance contient la valeur exacte.
- ✅ Prix d'achat dérivés de l'espérance (48,8× / 106,8×) ; Bonus Chance 1,4×.
- ✅ Fichiers Stake 4 modes ; vérificateur officiel math-sdk : 0 problème, 6/6 risques.
- 🟡 Revue indépendante des maths par un tiers (recommandée avant production).
- ⛔ Certification laboratoire (si exigée par la voie de distribution).

## Conformité plateforme
- ✅ Résultats sans état, indépendants ; aucune probabilité liée au solde ou à l'historique.
- ✅ Le client n'invente aucun gain : il présente les books ; test e2e « connexions dessinées = book ».
- 🟡 Lecture des « approval guidelines » Stake Engine : site inaccessible ici. À confirmer : mode Bonus Chance, deux achats, prix décimaux 48,8× et 106,8×, bonus non « free spins », noms des drapeaux de juridiction (`disabledBuyBonus`, `disabledBonusChance`).
- 🟡 Champ du book dans la réponse RGS (`state` / `events`) et noms de modes à confirmer sur le bac à sable Stake.
- ⛔ Tests sur le RGS réel / bac à sable (compte et accord requis ; aucun identifiant utilisé).

## Jeu
- ✅ 11 symboles, connexions lisibles, THE FINAL SET (Court Control, Power Shots, marques, Grand Slam, Hawk-Eye, Championship Point), deux achats confirmés, Bonus Chance, page d'informations.
- 🟡 Cinématiques 3D réelles (joueur animé, Ace en squelette, Hawk-Eye 3D, plans vidéo) : pipeline décrit dans FINAL_SET_DESIGN §7, assets à produire.
- ✅ e2e 165/165 : iPhone SE, iPhone 13, iPhone 14 Pro Max (portrait), iPhone 13 et Pixel 7 (paysage, émulés), iPad, 1920×1080, 1366×768 ; aucun contrôle sur les rouleaux, pas de défilement, pas de texte tronqué.
- 🟡 Safari iOS / Firefox / vrais Android : seul Chromium est disponible ici.
- 🟡 Performances GPU réelles (rendu logiciel ici) et écoute du son.
- 🟡 Droits du pack de symboles (« illustrations IA, vérifier les droits avant distribution commerciale » selon le README du pack).
- 🟡 Recherche de marque « Golden Rally ».

## Prototype Rally Path (Championship Night)
- ✅ Règles formalisées, maths exactes et simulées, 17 tests Python, parité TS, labo jouable avec 8 scénarios, e2e 6 formats.
- 🟡 Choix de la règle Second Serve (91 % actuellement) et recalibrage du Grand Final (73,8× < ancien 97,8×).
- 🟡 Illustration finale de la Balle d'or (asset actuel temporaire).
- ⛔ Pas encore de modes Stake, d'achats, ni de vérificateur pour le prototype : à faire seulement après validation de la variante.

## Avant toute mise en production
- ⛔ Aucun paiement réel connecté ; la démo utilise des crédits fictifs.
- ⛔ Pas de soumission sans vérification indépendante des maths, des obligations légales et des conditions de la plateforme.
