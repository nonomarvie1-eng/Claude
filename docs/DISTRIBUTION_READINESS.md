# Dossier de préparation à la distribution (Stake Engine)

## Déjà prêt

| Élément | Emplacement | État |
|---|---|---|
| `index.json`, table de correspondance, books `.jsonl.zst` (mode `base`, coût 1×) | `stake/publish_files/` | ✅ Format validé par `engineio/math-sdk` (commit `141b4e8`) |
| RTP de la table : 96,4857 %, identique au modèle exact | `stake/publish_files/export_summary.json` | ✅ |
| Statistiques de l'outil officiel (risques 6/6, 0 problème de soumission) | `stake/official_sdk_verification.json` | ✅ |
| Fichiers frontend statiques, chemins relatifs (`base: './'`) | `game/dist/` après `npm run build` | ✅ |
| Client RGS conforme à la documentation (authenticate, balance, play, end-round, event, codes d'erreur, argent à 6 décimales, paramètres d'URL) | `game/src/rgs/stakeRgs.ts` | ✅ testé avec des réponses simulées, **non testé sur le vrai RGS** |
| Désactivation par défaut du client réel (variable de build `VITE_ENABLE_RGS=1` requise) | `game/src/rgs/index.ts` | ✅ |
| Reprise d'un tour actif renvoyé par `authenticate` | `controller.ts` | ✅ |
| Rejeu fidèle d'un tour à partir de son book | Historique → « Rejouer » | ✅ |
| Drapeaux de juridiction gérés : `socialCasino`, `disabledTurbo`, `disabledFullscreen`, `disabledSpacebar`, `displayRTP`, `minimumRoundDuration` | `Hud.svelte`, `controller.ts` | ✅ (noms à confirmer) |
| Événements de book documentés | ci-dessous | ✅ |

## Événements d'un book

Tous les montants sont en unités `payoutMultiplier` (multiple de la mise × 100).

| Type | Champs | Sens |
|---|---|---|
| `reveal` | `gameType`, `board[5][3]`, `stops[5]`, `paddingAbove`, `paddingBelow`, `anticipation[5]` | Grille affichée (jeu de base ou tour gratuit) et positions d'arrêt réelles |
| `winInfo` | `gameType`, `multiplier`, `totalWin`, `wins[]` (`kind`, `line`, `symbol`, `count`, `basePay`, `multiplier`, `win`, `positions`) | Détail des gains du tour |
| `setWin` | `amount`, `winLevel` | Gain du tour (présentation) |
| `freeSpinTrigger` | `totalFs`, `positions` | Déclenchement du bonus |
| `updateFreeSpin` | `amount`, `total` | Compteur de tours gratuits |
| `rallyUp` | `added`, `collected`, `multiplier`, `previousMultiplier`, `positions` | Les Raquettes d'Or font monter le multiplicateur Rally |
| `freeSpinRetrigger` | `totalFs`, `added`, `positions` | Tours supplémentaires |
| `setTotalWin` | `amount` | Total cumulé du tour |
| `wincap` | `amount` | Plafond atteint (fin anticipée du bonus) |
| `freeSpinEnd` | `amount`, `winLevel` | Fin du bonus |
| `finalWin` | `amount` | Gain final = `payoutMultiplier` |

## Restrictions par marché prévues

- Mode « casino social » (`socialCasino`) : vocabulaire « Jouer » au lieu de « Mise ». **À compléter** selon la terminologie Stake.us : éviter « bet », « gamble » et « cash ».
- Turbo, plein écran et barre d'espace désactivables ; durée minimale d'un tour configurable.
- Pas d'autoplay, pas d'achat de bonus, pas d'arrêt rapide.

## Éléments restant nécessaires avant commercialisation

### Bloquants

1. **Accès et lecture des documents officiels Stake Engine** : FAQ, distribution, critères d'approbation et contrat développeur. Ils n'étaient pas accessibles depuis cet environnement.
2. **Compte développeur Stake Engine** et tests sur leur bac à sable : forme exacte de `round`, drapeaux de juridiction, devises. Cette démarche relève d'une décision du studio et n'a pas été effectuée.
3. **Gain maximal** : ajouter aux books une strate de queue, échantillonnée par importance avec rapport de vraisemblance exact, pour que des gains proches de 5 000× existent réellement. Sinon, afficher le maximum réel de la table, aujourd'hui 1 137,1×.
4. **Revue juridique** du contrat et des marchés couverts ; recherche et dépôt de marque.
5. **Tests sur appareils réels** : iOS Safari, Android Chrome, Firefox et appareils d'entrée de gamme.

### Importants

6. Traductions des 16 langues Stake, avec relecture humaine des textes réglementaires.
7. Recette sonore à l'oreille, mixage et volume, sur casque et haut-parleur de téléphone.
8. Revue d'accessibilité : lecteur d'écran, contrastes.
9. Si une distribution hors Stake est envisagée : certification par laboratoire indépendant, avec rapport du générateur aléatoire côté RGS et vérification des mathématiques.
10. Gel de version : mathématiques versionnées (`MATH_VERSION`), empreintes SHA-256 des fichiers publiés et journal des modifications.
