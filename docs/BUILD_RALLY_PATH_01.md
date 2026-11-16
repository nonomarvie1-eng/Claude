# Build de test RALLY-PATH-01 — diagnostic et intégration

## Pourquoi l'ancien bonus restait visible
- Point d'entrée unique : `game/index.html` → `src/main.ts` → `App.svelte` → `Controller` (`src/game/controller.ts`) → `DemoRgs.play()` (`src/rgs/demoRgs.ts`).
- Jusqu'à cette version, `DemoRgs.play()` appelait toujours `playRound()` de `src/engine/engine.ts`, qui contient le bonus v6 THE FINAL SET (`bonus.ts` : Hawk-Eye, ACE/SMASH/AMORTIE, échanges et points). Les boutons d'achat (`BuyBonus.svelte`), Bonus Chance et « 3/4/5 × BONUS » passaient par le même chemin.
- Le Rally Path livré avant n'était raccordé qu'à un « labo » non crédité dans Réglages (`Controller.labRound`) : **implémenté mais pas branché sur le vrai jeu**.
- Le déploiement : une seule URL (artefact `S7QBvZjRnoUDJsfEnUNRqN`), fichier unique `npm run build:single`, pas de service worker. En revanche, `localStorage` conservait la partie en cours et l'historique : une partie v6 interrompue pouvait être reprise et rejouée au rechargement.

## Changements
- `src/engine/gameplay.ts` : `RALLY_PATH_BUILD` (par défaut) et `BUILD_ID = 'RALLY-PATH-01'`. `VITE_GAMEPLAY=finalset` reconstruit le v6 (`npm run build:finalset`, `npm run test:finalset`). Le code v6 n'est pas supprimé.
- `rally_path.play_game_round` (Python) / `playGameRound` (TS, parité testée) : tour réel complet. Jeu de base 6×5 avec Rally Path ; 3 scatters → Rally Challenge (8 tours) ; 4+ → The Grand Final (12 tours + Second Serve).
- `DemoRgs` : en build Rally Path, seul le mode `base` est accepté (achats et Bonus Chance refusés). Scénarios forcés `game_full6`, `game_rally`, `game_final`. Clés de stockage séparées (`golden-rally-demo-rp01`, `golden-rally-history-rp01`) : aucune ancienne partie ne peut être reprise.
- Interface : identifiant RALLY-PATH-01 sous le badge démo ; bouton **TEST 6 COUPS** à la place de « BONUS MODES » ; compteur de bonus « TOURS x / y » sans points ; page d'informations avec les règles Rally Path (règles Final Set, modes et RTP v6 masqués) ; tests de bonus dans Réglages.
- Pas de seconde célébration « méga gain » après un Championship Shot.

## Vérification
`node e2e/rally-build-e2e.mjs` (preview Vite) et `URL=… node e2e/rally-build-e2e.mjs` (fichier publié) : 44/44 chacun. Les points couverts : 390×844, identifiant visible, TEST 6 COUPS → chemin rouleaux 0→5 sur raquettes adjacentes, Championship Shot, aucun événement v6, comptabilité des crédits, Rally Challenge / Grand Final, page d'informations, 320×568, iPhone SE, 1440×900. Captures : `game/e2e/screenshots/rp01-*`.

Limites : Chromium émulé (pas Safari iOS réel). L'artefact claude.ai est privé et demande une connexion, donc la vérification en ligne s'est faite en relisant le fichier publié (identique au fichier testé), pas en ouvrant l'URL dans un navigateur connecté.
