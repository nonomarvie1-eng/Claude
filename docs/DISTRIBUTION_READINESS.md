# Dossier de préparation à la distribution (Stake Engine)

## Déjà prêt

| Élément | Emplacement | État |
|---|---|---|
| `index.json`, tables de correspondance et books `.jsonl.zst` pour **2 modes** : `base` (coût 1×) et `bonus` (achat du Tie-Break, coût 100×) | `stake/publish_files/` | ✅ Format validé par `engineio/math-sdk` (commit `141b4e8`), 0 problème de soumission, contrôles de risque réussis sur les 2 modes |
| RTP de la table : 96,4871 %, identique au modèle exact ; gain maximal 5 000× présent dans la table | `stake/publish_files/export_summary.json` | ✅ |
| Statistiques de l'outil officiel (risques 6/6, 0 problème de soumission) | `stake/official_sdk_verification.json` | ✅ |
| Fichiers frontend statiques, chemins relatifs (`base: './'`) | `game/dist/` après `npm run build` | ✅ |
| Client RGS conforme à la documentation (authenticate, balance, play, end-round, event, codes d'erreur, argent à 6 décimales, paramètres d'URL) | `game/src/rgs/stakeRgs.ts` | ✅ testé avec des réponses simulées, **non testé sur le vrai RGS** |
| Désactivation par défaut du client réel (variable de build `VITE_ENABLE_RGS=1` requise) | `game/src/rgs/index.ts` | ✅ |
| Reprise d'un tour actif renvoyé par `authenticate` | `controller.ts` | ✅ |
| Rejeu fidèle d'un tour à partir de son book | Historique → « Rejouer » | ✅ |
| Drapeaux de juridiction gérés : `socialCasino`, `disabledTurbo`, `disabledFullscreen`, `disabledSpacebar`, `displayRTP`, `minimumRoundDuration`, `disabledAutoplay`, `disabledBuyBonus` | `Hud.svelte`, `controller.ts` | ✅ (noms à confirmer, surtout les deux derniers, qui sont des hypothèses) |
| Achat du bonus via `/wallet/play` avec `mode: "BONUS"` et montant = mise de base (débit = mise × coût du mode, selon la doc RGS) | `controller.ts`, `stakeRgs.ts` | ✅ en démo ; nom exact du mode à aligner sur `index.json` (`bonus`) lors des tests du bac à sable |
| Événements de book documentés | ci-dessous | ✅ |

## Événements d'un book

Tous les montants sont en unités `payoutMultiplier` (multiple de la mise × 100).

| Type | Champs | Sens |
|---|---|---|
| `reveal` | `gameType`, `board[6][5]`, `stops[6]`, `paddingAbove`, `paddingBelow`, `anticipation[6]` | Grille affichée (jeu de base ou tour gratuit) et positions d'arrêt réelles |
| `winInfo` | `gameType`, `multiplier`, `totalWin`, `wins[]` (`kind` = ways/scatter, `symbol`, `count` = rouleaux, `ways`, `basePay` par façon, `multiplier`, `win`, `positions`) | Détail des gains du tour |
| `setWin` | `amount`, `winLevel` | Gain du tour (présentation) |
| `freeSpinTrigger` | `totalFs`, `positions` | Déclenchement du bonus |
| `updateFreeSpin` | `amount`, `total` | Compteur de tours gratuits |
| `rallyUp` | `added`, `collected`, `multiplier`, `previousMultiplier`, `positions` | Les Smash font monter le multiplicateur Rally |
| `freeSpinRetrigger` | `totalFs`, `added`, `positions` | Tours supplémentaires |
| `setTotalWin` | `amount` | Total cumulé du tour |
| `wincap` | `amount` | Plafond atteint (fin anticipée du bonus) |
| `freeSpinEnd` | `amount`, `winLevel` | Fin du bonus |
| `finalWin` | `amount` | Gain final = `payoutMultiplier` |

## Restrictions par marché prévues

- Mode « casino social » (`socialCasino`) : vocabulaire « Jouer » au lieu de « Mise ». **À compléter** selon la terminologie Stake.us : éviter « bet », « gamble » et « cash ».
- Turbo, plein écran et barre d'espace désactivables ; durée minimale d'un tour configurable.
- L'autoplay (avec limite de perte obligatoire) et l'achat de bonus existent, et chacun **doit pouvoir être coupé par marché**. Plusieurs régulateurs les interdisent ou les restreignent ; le Royaume-Uni interdit par exemple l'autoplay. Pas d'arrêt rapide.

## Éléments restant nécessaires avant commercialisation

### Bloquants

1. **Accès et lecture des documents officiels Stake Engine** : FAQ, distribution, critères d'approbation et contrat développeur. Ils n'étaient pas accessibles depuis cet environnement.
2. **Compte développeur Stake Engine** et tests sur leur bac à sable : forme exacte de `round`, drapeaux de juridiction, devises. Cette démarche relève d'une décision du studio et n'a pas été effectuée.
3. **Gain maximal** : ✅ résolu en v2. Des tranches de gros gains sont échantillonnées, donc la table contient des tours jusqu'à 5 000×. Les probabilités de ces tranches sont estimées par un pilote Monte-Carlo de 3 millions de bonus par strate. Le laboratoire ou Stake devra accepter cette méthode documentée.
4. **Revue juridique** du contrat et des marchés couverts ; recherche et dépôt de marque.
5. **Tests sur appareils réels** : iOS Safari, Android Chrome, Firefox et appareils d'entrée de gamme.

### Importants

6. Traductions des 16 langues Stake, avec relecture humaine des textes réglementaires.
7. Recette sonore à l'oreille, mixage et volume, sur casque et haut-parleur de téléphone.
8. Revue d'accessibilité : lecteur d'écran, contrastes.
9. Si une distribution hors Stake est envisagée : certification par laboratoire indépendant, avec rapport du générateur aléatoire côté RGS et vérification des mathématiques.
10. Gel de version : mathématiques versionnées (`MATH_VERSION`), empreintes SHA-256 des fichiers publiés et journal des modifications.
