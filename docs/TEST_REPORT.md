# Rapport des tests exécutés

Date : 15 novembre 2026 · environnement : conteneur Linux, Node 22.23, Python 3.13, Chromium (Playwright 1.63, rendu WebGL logiciel SwiftShader).

## Synthèse

| Suite | Commande | Résultat |
|---|---|---|
| Mathématiques (pytest) | `cd math && .venv/bin/python -m pytest -q` | **27 / 27 réussis** |
| Typage Svelte/TypeScript | `cd game && npm run check` | **0 erreur, 0 avertissement** |
| Tests unitaires du jeu (vitest) | `cd game && npm test` | **19 / 19 réussis** |
| Build de production | `npm run build` | **réussi** |
| Tests navigateur bout en bout | `npm run e2e` | **65 / 65 vérifications réussies** (`game/e2e/report.json`) |
| Simulation Monte-Carlo | `python -m rally_math.simulate -n 10000000` | RTP 96,203 % ± 0,40 % (IC 95 %) contre 96,486 % exact, z = −1,38 : **cohérent** |
| Outil officiel engineio/math-sdk | `stake/tools/verify_with_official_sdk.py` | **format conforme, 0 problème de soumission, 6/6 contrôles de risque** |

## Détail par exigence

| Exigence | Tests |
|---|---|
| Calcul des gains | 11 cas de lignes (Wild, Scatter qui coupe la ligne, choix du meilleur gain), en Python et en TypeScript ; cohérence `winInfo` = somme des gains, `win = basePay × multiplicateur` |
| Probabilités et table des gains | Table de gains monotone ; contraintes des bandes (au plus 1 Scatter par fenêtre, Wilds sur les rouleaux 2-4) ; test du χ² de la distribution des Scatters, exacte contre 200 000 tirages |
| Exactitude du RTP | RTP exact recalculé par une **méthode indépendante** (linéarité sur les lois marginales, à 10⁻⁹ près) ; Monte-Carlo de 400 000 tours dans les tests (\|z\| < 4) et de 10 millions dans le rapport ; RTP dans les limites Stake |
| Indépendance des résultats | Rejeu déterministe à partir des positions d'arrêt ; ordre des tours sans effet ; aucune variable d'état entre deux tours |
| Événements de bonus | Multiplicateur Rally appliqué au tour même ; relances et plafond de 50 tours restants (scénario exact de 62 tours) ; plafond de gain 5 000× ; bonus forcé en démo |
| Cohérence affichage et résultat | 400 tours : chaque grille affichée = grille du book, gain affiché = paiement ; dans le navigateur : gain et solde affichés = réponse du RGS, sur 5 formats d'écran et pendant le bonus |
| Parité des moteurs Python et TypeScript | 200 tours de référence (dont 100 bonus) reproduits **à l'identique** |
| Erreurs de données | Book vide, `finalWin` incohérent ou grille malformée : rejetés avant affichage ; stockage local corrompu : réinitialisation ; erreur serveur simulée : boîte de dialogue puis reprise |
| Interruption ou rechargement | Rechargement en plein tour : le tour est repris et réglé **une seule fois**, sans tour actif résiduel |
| Tailles d'écran | 1920×1080, 1366×768, iPhone 13 en portrait, Pixel 7 en paysage, iPad en portrait : pas de débordement horizontal, bouton de lancement entièrement visible, badge démo visible, aucune erreur console |
| Réduction des animations | Présentation d'un tour en moins de 9 s (mesuré : 4,4 s) |
| Client RGS Stake | Points d'accès, `sessionID`, montants, correspondance des codes d'erreur, panne réseau (requêtes simulées, **sans identifiants réels**) |
| Génération des fichiers de production | Mini-export Stake valide (ids, poids > 0, paiements identiques entre books et table, RTP de la table = exact) ; build Vite |
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
