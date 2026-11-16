# Rapport des tests exécutés

Date : 16 novembre 2026 (refonte premium v4) · environnement : conteneur Linux, Node 22.23, Python 3.13, Chromium (Playwright 1.63, rendu WebGL logiciel SwiftShader).

## Synthèse

| Suite | Commande | Résultat |
|---|---|---|
| Mathématiques (pytest) | `cd math && .venv/bin/python -m pytest -q` | **18 / 18 réussis** (maths inchangées par la refonte) |
| Typage Svelte/TypeScript | `cd game && npm run check` | **0 erreur, 0 avertissement** |
| Tests unitaires du jeu (vitest) | `cd game && npm test` | **20 / 20 réussis** |
| Build de production | `npm run build` | **réussi** |
| Tests navigateur bout en bout | `npm run e2e` | **149 / 149 vérifications réussies** (`game/e2e/report.json`) |
| Simulation Monte-Carlo | `python -m rally_math.simulate -n 200000000` | RTP 96,468 % ± 0,108 % (IC 95 %) contre 96,487 % exact, z = −0,36 : **cohérent** |
| Outil officiel engineio/math-sdk | `stake/tools/verify_with_official_sdk.py` | **format conforme, 0 problème de soumission, 6/6 contrôles de risque** |

## Détail par exigence

| Exigence | Tests |
|---|---|
| Calcul des gains | Cas de façons de gagner (multiplication par rouleau, Wild, Scatter exclu), en Python et en TypeScript ; chemin vectorisé = moteur de référence sur 3 000 grilles ; `win = basePay × façons × multiplicateur` |
| Probabilités et table des gains | Table de gains monotone et compatible avec le RGS (paliers de 0,1×) ; contraintes des bandes (au plus 1 Scatter par fenêtre de 5, pas de Wild sur le rouleau 1) ; loi jointe Wilds/Trophées exacte contre énumération |
| Exactitude du RTP | Méthode polynomiale exacte **comparée à une énumération exhaustive** de toutes les grilles (bandes réduites, à 10⁻¹⁰ près) ; Monte-Carlo de 4 millions de tours dans les tests (\|z\| < 4) et de 200 millions dans le rapport ; RTP dans les limites Stake |
| Indépendance des résultats | Rejeu déterministe à partir des positions d'arrêt ; ordre des tours sans effet ; aucune variable d'état entre deux tours |
| Événements de bonus | Multiplicateur Rally appliqué au tour même ; relances et plafond de 50 tours restants (scénario déterministe) ; plafond de gain ; bonus forcé en démo ; chaque book Stake reconstruit par le moteur de référence |
| Cohérence affichage et résultat | 400 tours : chaque grille affichée = grille du book, gain affiché = paiement ; dans le navigateur : gain et solde affichés = réponse du RGS, sur 5 formats d'écran et pendant le bonus |
| Parité des moteurs Python et TypeScript | 200 tours de référence (dont 100 bonus) reproduits **à l'identique** |
| Erreurs de données | Book vide, `finalWin` incohérent ou grille malformée : rejetés avant affichage ; stockage local corrompu : réinitialisation ; erreur serveur simulée : boîte de dialogue puis reprise |
| Interruption ou rechargement | Rechargement en plein tour : le tour est repris et réglé **une seule fois**, sans tour actif résiduel |
| Tailles d'écran | 1920×1080, 1366×768, iPhone SE, iPhone 13 et iPhone 14 Pro Max en portrait, iPhone 13 et Pixel 7 en paysage, iPad en portrait. Contrôles : pas de défilement horizontal ni vertical, rouleaux entièrement à l'écran, **aucun bouton (HUD, menu, achat) sur la zone des rouleaux** (rectangles mesurés), cibles tactiles ≥ 38 px, aucun texte du HUD tronqué, cellule ≥ 44 px par rouleau (mesuré : 50 px sur iPhone SE, 54,7 px sur iPhone 13 en paysage), badge démo visible, aucune erreur console |
| Réduction des animations | Présentation d'un tour en moins de 9 s (mesuré : 4,4 s) |
| Client RGS Stake | Points d'accès, `sessionID`, montants, correspondance des codes d'erreur, panne réseau (requêtes simulées, **sans identifiants réels**) |
| Génération des fichiers de production | Mini-export Stake valide (ids, poids > 0, paiements identiques entre books et table, RTP de la table = exact) ; export complet vérifié par l'outil officiel (gain max 5 000× présent) ; build Vite |
| Gains ≤ mise non célébrés | Paliers de gain : `ldw` pour un gain ≤ mise, sans célébration |

Captures d'écran : `game/e2e/screenshots/` (chargement, jeu, gains, bonus, table des gains, réglages, historique, rejeu, erreur).

## Tests non exécutables dans cet environnement

| Test | Raison | À faire |
|---|---|---|
| Safari iOS / WebKit, Firefox | Seul Chromium est installé | Tester sur de vrais appareils iOS et Android et sous Firefox |
| Performances GPU réelles | Rendu logiciel (SwiftShader) | Mesurer les images par seconde sur un téléphone d'entrée de gamme |
| Écoute du son | Pas d'écoute humaine possible | Recette sonore au casque et sur haut-parleur de téléphone |
| RGS Stake réel / bac à sable | stake-engine.com bloqué ici ; aucun compte ; pas d'identifiants (volontairement) | Tester sur le bac à sable après création du compte, avec accord |
| Certification laboratoire (générateur aléatoire, maths) | Prestation externe | Uniquement si exigée par la voie de distribution |
| Lecteur d'écran | Non automatisable de façon fiable ici | Test manuel VoiceOver / TalkBack |
