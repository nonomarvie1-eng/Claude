# Golden Rally — machine à sous de démonstration (tennis, style cartoon)

Jeu original **6 × 5, 15 625 façons de gagner**, personnages cartoon (le Président, la Championne, l'Arbitre, le Ramasseur, le Bulldog), Wild **Smash**, Scatter **Trophée**, bonus **Tie-Break** avec multiplicateur persistant **Rally** (×1 → ×20). RTP théorique **96,487 %** calculé exactement, vérifié par 200 millions de tours simulés ; gain maximal 5 000×.

> **Démonstration uniquement.** Les crédits sont fictifs, sans valeur monétaire, ni retirables, ni convertibles. Aucune connexion à un opérateur, aucun paiement, aucune transaction n'est activé. La commercialisation reste subordonnée à une validation technique, juridique et contractuelle (voir `docs/`).

## Contenu du dépôt

| Dossier | Rôle |
|---|---|
| `math/` | Moteur mathématique Python : règles (`rally_math/config.py`), bandes de rouleaux (`reels/`), calcul exact, Monte-Carlo, export Stake Engine, rapport, tests |
| `shared/` | `game-config.json` (règles exportées pour le jeu) et `parity-fixtures.json` (tours de référence Python/TypeScript) |
| `game/` | Jeu TypeScript + Svelte 5 + PixiJS 8 (Vite) : moteur de démo, client RGS, rendu, interface, tests unitaires et navigateur |
| `game/art/` | Générateur des visuels (SVG procédural → PNG via Chromium) |
| `game/audio/` | Synthèse procédurale de tous les sons et musiques (Python/numpy) |
| `stake/publish_files/` | Fichiers mathématiques au format Stake Engine (`index.json`, table CSV, books `.jsonl.zst`) |
| `stake/tools/` | Vérification des fichiers avec l'outil officiel `engineio/math-sdk` |
| `docs/` | Rapports : faisabilité, conception, maths, tests, distribution, business, risques, licences |

## Prérequis

- Node.js ≥ 20 (testé avec 22.23), npm
- Python ≥ 3.11 (testé avec 3.13) et `uv` ou `pip`
- ffmpeg (uniquement pour régénérer l'audio)
- Chromium/Playwright (uniquement pour régénérer les visuels et pour les tests navigateur)

## Lancer la démo

```bash
cd game
npm install
npm run dev          # http://localhost:5173  (développement)
# ou version de production :
npm run build && npm run preview   # http://localhost:4173
```

Ouvrir l'URL, toucher « Toucher pour commencer », puis lancer avec le bouton central ou la barre d'espace.
Le menu **Réglages** permet de **tester le bonus** (résultat forcé, signalé comme tel, démo uniquement) et de recharger les crédits fictifs.

Version « fichier unique » (tout intégré dans un seul `index.html`, pratique pour partager la démo) :

```bash
cd game && npm run build:single   # -> game/dist-single/index.html
```

## Chaîne de production automatisée

```bash
# 1. Mathématiques
cd math
uv venv .venv && uv pip install --python .venv/bin/python numpy zstandard matplotlib scipy pytest
.venv/bin/python -m rally_math.reels          # bandes de rouleaux (déterministes)
.venv/bin/python -m rally_math.exact          # RTP exact -> reports/exact.json
.venv/bin/python -m rally_math.simulate -n 200000000  # Monte-Carlo (~1 min) -> reports/montecarlo.json
.venv/bin/python -m rally_math.export_stake   # fichiers Stake -> ../stake/publish_files
.venv/bin/python -m rally_math.export_config  # règles + fixtures -> ../shared
.venv/bin/python -m rally_math.report         # ../docs/MATH_REPORT.md
.venv/bin/python -m pytest -q                 # tests mathématiques

# 2. Vérification avec l'outil officiel (non inclus dans ce dépôt)
git clone --depth 1 https://github.com/engineio/math-sdk.git /tmp/math-sdk
math/.venv/bin/python stake/tools/verify_with_official_sdk.py /tmp/math-sdk stake/publish_files

# 3. Visuels et sons
cd game
npm run assets       # SVG -> PNG (src/assets/img)
npm run audio        # synthèse -> src/assets/audio

# 4. Tests du jeu
npm run check        # typage Svelte/TS
npm test             # tests unitaires (parité moteur, RGS, cohérence affichage)
npm run build && npm run e2e   # tests navigateur (5 formats d'écran) -> e2e/report.json + e2e/screenshots
```

## Principes non négociables appliqués

- Le résultat est déterminé **avant** toute animation, par le serveur de jeu (en démo : le simulateur local, qui utilise les mêmes règles). Le navigateur ne fait qu'afficher le « book » reçu.
- Aucun résultat ne dépend du solde, de l'historique ou du comportement du joueur.
- Pas d'animation trompeuse : les rouleaux défilent sur leurs vraies bandes et s'arrêtent sur la position tirée ; pas d'arrêt manuel influençant le résultat ; les gains inférieurs ou égaux à la mise ne sont pas célébrés.
- Pas de fausses statistiques, pas de messages incitatifs, pas d'autoplay.

## Documents

- `docs/FEASIBILITY.md` — étude de la distribution (Phase 1) et obstacles
- `docs/GAME_DESIGN.md` — conception, direction artistique, mécanique
- `docs/MATH_REPORT.md` — rapport mathématique (généré)
- `docs/TEST_REPORT.md` — tests exécutés et non exécutables
- `docs/DISTRIBUTION_READINESS.md` — dossier de préparation Stake Engine + éléments restant avant commercialisation
- `docs/BUSINESS.md` — évaluation commerciale
- `docs/RISKS.md` — risques juridiques et techniques
- `docs/ASSETS_AND_LICENSES.md` — origine et droits de chaque ressource
