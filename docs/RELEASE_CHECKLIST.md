# Release checklist — Golden Rally: Match Point (v5)

Légende : ✅ fait et vérifié ici · 🟡 fait, validation supplémentaire nécessaire · ⛔ pas réalisable dans cet environnement / dépend d'un tiers.

## Mathématiques
- ✅ RTP exact de chaque mode, après plafond (96,41–96,52 %), dans la fenêtre SDK 96,0–96,7 %.
- ✅ Monte-Carlo : 20 M tours (Normal, Bonus Chance), 1,92 M tours par achat ; chaque intervalle de confiance contient la valeur exacte.
- ✅ Prix d'achat dérivés de l'espérance exacte (49,4× / 105×) ; Bonus Chance 1,4× dérivé avec la probabilité.
- ✅ Fichiers Stake 4 modes ; vérificateur officiel math-sdk : 0 problème, 6/6 risques.
- 🟡 Revue indépendante des maths par un tiers (recommandée avant production).
- ⛔ Certification laboratoire (si exigée par la voie de distribution).

## Conformité plateforme
- ✅ Résultats sans état, indépendants ; aucune probabilité liée au solde ou à l'historique.
- ✅ Le client n'invente aucun gain : il présente les books ; test e2e « connexions dessinées = book ».
- 🟡 Lecture des « approval guidelines » Stake Engine : site inaccessible ici. À confirmer : mode Bonus Chance, deux achats, prix décimal 49,4×, noms des drapeaux de juridiction (`disabledBuyBonus`, `disabledBonusChance`).
- 🟡 Champ du book dans la réponse RGS (`state` / `events`) et noms de modes à confirmer sur le bac à sable Stake.
- ⛔ Tests sur le RGS réel / bac à sable (compte et accord requis ; aucun identifiant utilisé).

## Jeu
- ✅ 11 symboles, connexions lisibles sans animation, deux bonus, deux achats confirmés, Bonus Chance, page d'informations.
- ✅ e2e 161/161 : iPhone SE, iPhone 13, iPhone 14 Pro Max (portrait), iPhone 13 et Pixel 7 (paysage, émulés), iPad, 1920×1080, 1366×768 ; aucun contrôle sur les rouleaux, pas de défilement, pas de texte tronqué.
- 🟡 Safari iOS / Firefox / vrais Android : seul Chromium est disponible ici.
- 🟡 Performances GPU réelles (rendu logiciel ici) et écoute du son.
- 🟡 Droits du pack de symboles (« illustrations IA, vérifier les droits avant distribution commerciale » selon le README du pack).
- 🟡 Recherche de marque « Golden Rally ».

## Avant toute mise en production
- ⛔ Aucun paiement réel connecté ; la démo utilise des crédits fictifs.
- ⛔ Pas de soumission sans vérification indépendante des maths, des obligations légales et des conditions de la plateforme.
