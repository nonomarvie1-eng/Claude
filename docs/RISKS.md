# Risques juridiques et techniques

Échelle : impact / probabilité (Faible, Moyen, Élevé).

## Juridiques et réglementaires

| Risque | Impact | Prob. | Mesure |
|---|---|---|---|
| Exploiter le jeu en argent réel sans licence dans une juridiction qui l'exige | Élevé | Moyen | Démo seulement. La distribution passe par un opérateur licencié (Stake). Avis juridique par marché obligatoire avant toute autre voie. |
| France : les machines à sous en ligne en argent réel sont interdites (ANJ) | Élevé | — | Ne pas cibler de joueurs français en argent réel. Une démo gratuite, sans gain convertible, reste d'un autre ordre (vérifier les règles de publicité). |
| Contrat Stake Engine défavorable (cession de propriété intellectuelle, exclusivité, GGR négatif à la charge du studio) | Élevé | [?] | Revue juridique avant signature. |
| Contrefaçon de marque (nom, symboles) | Moyen | Faible-Moyen | Recherche d'antériorité, ressources 100 % originales, aucune référence à un tournoi, un joueur ou une marque réels. |
| Thème tennis assimilé à un tournoi existant (« passing off ») ou personnage ressemblant à une vraie personne | Moyen | Faible | Personnages génériques inventés, aucun nom, lieu ou trophée réel ; revue avant diffusion. |
| Ressemblance avec le style d'un concurrent | Moyen | Faible | Inspiration de principes uniquement, dessins entièrement originaux. |
| Publicité de jeux d'argent auprès de mineurs ou des publics protégés | Élevé | Faible | Aucune communication publique sans cadre légal ; style non enfantin. |
| Exigences spécifiques des marchés : durée minimale d'un tour, interdiction de l'arrêt rapide, de l'autoplay ou de la célébration des pertes déguisées en gains (exemple : RTS 14 de l'UKGC) | Moyen | Moyen | Déjà en place : pas d'autoplay, pas d'arrêt manuel, pas de célébration des gains ≤ mise, `minimumRoundDuration` respecté, turbo désactivable par drapeau. |
| Protection des données (RGPD) | Moyen | Faible | La démo ne collecte rien : seul le stockage local du navigateur est utilisé, sans cookie ni traceur. |

## Techniques

| Risque | Impact | Prob. | Mesure |
|---|---|---|---|
| Probabilités des tranches de gros gains estimées par simulation, pas par calcul exact (le RTP global reste exact) | Faible | — | Méthode et effectifs documentés dans `MATH_REPORT.md` ; augmenter le pilote si demandé. |
| Fréquence de gain élevée (65 %), mais beaucoup de gains inférieurs à la mise | Moyen (perception joueur, règles sur les pertes déguisées en gains) | Certain | Aucune célébration des gains ≤ mise (déjà en place) ; fréquence affichée honnêtement dans les règles. |
| Champ du « book » dans la réponse `/wallet/play` (`state` ou `events`) non confirmé | Moyen | Moyen | Le client accepte les deux ; à valider sur le bac à sable Stake. |
| Format exact des drapeaux de juridiction non documenté au complet | Faible | Moyen | Drapeaux inconnus ignorés sans erreur ; à valider sur le bac à sable. |
| Performances sur appareils d'entrée de gamme (WebGL, flou de mouvement) | Moyen | Moyen | Mode « réduire les animations » ; à tester sur de vrais appareils. |
| Safari iOS et Firefox non testés (seul Chromium est disponible ici) | Moyen | Moyen | Campagne de tests sur appareils réels avant soumission. |
| Écart entre le moteur de démo (TypeScript) et le moteur de référence (Python) | Élevé | Faible | Test de parité sur 200 tours de référence (identiques à l'octet près), plus validation de chaque book avant affichage. |
| Erreur de calcul RTP | Élevé | Faible | Méthode exacte validée par énumération exhaustive, simulation de 200 millions de tours, vérification par l'outil officiel du SDK. |
| Perte de session ou rechargement en cours de tour | Moyen | Moyen | Reprise automatique du tour actif, réglé une seule fois (test navigateur). |
| Achat de bonus (75× la mise par tour) et autoplay : interdits ou restreints sur certains marchés ; risque de jeu excessif | Élevé | Moyen | Désactivables par drapeau de juridiction ; confirmation explicite avec prix et RTP ; limite de perte obligatoire et arrêt facile pour l'autoplay ; pas de célébration d'un bonus acheté qui rapporte moins que son prix. Revue juridique par marché obligatoire. |

## Ce qui n'est **pas** garanti

- Aucune approbation Stake Engine, aucune certification de laboratoire et aucune conformité juridique ne sont simulées ni revendiquées.
- Les revenus ne sont pas garantis (`BUSINESS.md`).
