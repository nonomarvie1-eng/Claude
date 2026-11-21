# GTA-MEDIA : pipeline de montage automatique de Shorts GTA (FR)

Le pipeline prend des **captures Xbox** et produit un **MP4 vertical 1080 × 1920** prêt pour
TikTok et YouTube Shorts. Il ajoute une voix off française, des sous-titres mot à mot
synchronisés, de la musique avec ducking, des effets et un contrôle qualité automatique.

```
captures Xbox ─► ingest ─► library/ (1080p SDR CFR) ─┐
episode.yaml (plans + texte) ─► voix off phrase/phrase ┼─► rendu FFmpeg 1 passe ─► output/*.mp4
                                  └► sous-titres ASS ──┘                          └► vérification auto
```

## Arborescence
| Dossier | Rôle |
|---|---|
| `inbox/` | Déposez ici vos captures Xbox |
| `library/` | Captures normalisées + `index.json` (générées) |
| `projects/<nom>/episode.yaml` | Une vidéo = un fichier : titre, plans, narration |
| `output/` | MP4 final, `.srt`, planche de contrôle, rapport de vérification |
| `work/` | Fichiers intermédiaires (suppression possible à tout moment) |
| `assets/fonts` `music` `voices` `sfx` | Ressources (police Inter, licence OFL, fournie) |
| `config/settings.yaml` | Tous les réglages : style, effets, audio, voix |
| `gtamedia/` | Code du pipeline (Python + FFmpeg) |
| `scripts/windows/` | `audit.ps1` (lecture seule), `install.ps1` (guidé), `build.ps1` |
| `docs/VOIX_OFF.md` | Comparatif des voix off et de leurs licences |

## 1. Installation sous Windows (une seule fois)
Dans PowerShell, depuis le dossier `GTA-MEDIA` :
```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\audit.ps1     # diagnostic, ne modifie rien
powershell -ExecutionPolicy Bypass -File scripts\windows\install.ps1   # demande O/N avant chaque installation
.\.venv\Scripts\python.exe gta.py doctor                                # doit afficher "PRÊT"
```
Ce que `install.ps1` propose, tout en gratuit et via winget : Python 3.12, FFmpeg (build complète
gyan.dev), Git, Node.js (optionnel), les modules Python et la voix Piper `fr_FR-siwis-medium`.

> Dans la suite, `python` désigne `.\.venv\Scripts\python.exe`. Vous pouvez aussi activer
> l'environnement avec `.\.venv\Scripts\Activate.ps1`.

## 2. Récupérer les captures Xbox
- **Sur la console** : touche Xbox → Capture et partage → *Enregistrer ce qui s'est passé*.
  Dans les paramètres de capture, choisissez la résolution 1080p (4K possible, convertie ensuite).
- **Vers le PC**, au choix :
  - application **Xbox** pour PC (ou application mobile Xbox) → Captures → Télécharger ;
  - téléversement automatique **OneDrive** : ajoutez le dossier dans `paths.xbox_sources` ;
  - clé USB (Paramètres → Capture → emplacement), puis copie dans `inbox/`.
- Les captures en HDR (HEVC 10 bits) sont détectées et converties en SDR automatiquement.

## 3. Produire une vidéo
```powershell
python gta.py ingest                       # importe inbox/ (+ dossiers xbox_sources), ignore les doublons
python gta.py library                      # liste les captures disponibles
python gta.py new mon-episode              # crée projects/mon-episode/episode.yaml
# éditez episode.yaml : titre, plans (start/end en secondes), phrases de narration
python gta.py build projects/mon-episode/episode.yaml          # voix Piper (par défaut)
python gta.py build projects/mon-episode/episode.yaml --tts test   # sans voix réelle (test)
```
Raccourci Windows (import et montage) :
`powershell -ExecutionPolicy Bypass -File scripts\windows\build.ps1 projects\mon-episode\episode.yaml`

Résultats dans `output/` :
- `mon-episode.mp4` : la vidéo à publier ;
- `mon-episode.srt` : sous-titres séparés (facultatif sur YouTube) ;
- `mon-episode_controle.png` : 6 images pour vérifier le rendu en un coup d'œil ;
- `mon-episode_verification.json` : rapport du contrôle qualité.

### Format d'un projet (`episode.yaml`)
```yaml
title: "LE SECRET DU MONT CHILIAD"   # bandeau en haut pendant title_duration s
title_duration: 2.8
music: assets/music/ma_musique_libre.mp3
clips:
  - file: library/20261120_211433_gtav_a13421.mp4
    start: 12.5          # secondes dans la capture
    end: 18.0
    layout: crop         # crop = plein écran recadré ; blur = image entière + fond flouté
    focus_x: 0.5         # crop : 0 = gauche, 0.5 = centre, 1 = droite
    zoom: 0.08           # optionnel : intensité du zoom lent
narration:
  - "Une phrase = un bloc de sous-titres."
  - "Le montage s'adapte automatiquement à la durée de la voix."
```
Si les plans sont plus courts que la narration, ils sont réutilisés en boucle.

## 4. Contrôle qualité automatique
`build` lance la vérification à la fin. Vous pouvez la relancer à part : `python gta.py verify output/demo.mp4`.

| Test | Critère |
|---|---|
| Format | 1080 × 1920, H.264 High, yuv420p, AAC 48 kHz, `faststart` |
| Lisibilité | décodage intégral sans aucune erreur |
| Synchro audio | corrélation entre la voix d'origine et l'audio final : décalage < 1 image (33 ms) |
| Synchro sous-titres | début de chaque phrase sous-titrée = démarrage de la voix (± 60 ms) |
| Durées | piste audio = piste vidéo (± 1,5 image) |

## 5. Réglages utiles (`config/settings.yaml`)
- `video.encoder: h264_nvenc` : encodage 3 à 5 fois plus rapide avec une carte NVIDIA.
- `style.*` : police, taille, couleur du mot surligné, position (zone sûre TikTok).
- `effects.*` : zoom, contraste et saturation, vignette, transition (`fade`, `slideleft`…), flash, barre de progression.
- `audio.*` : volumes, ducking, cible -14 LUFS.
- `tts.backend` : `piper` (gratuit, local), `azure` (clé `AZURE_SPEECH_KEY`), `elevenlabs` (clé `ELEVENLABS_API_KEY`).

## 6. Reproduire le prototype de test
```powershell
python gta.py test-assets            # 4 fausses captures Xbox (mires FFmpeg, dont une 4K HDR) + une musique
python gta.py ingest
python gta.py build projects/demo/episode.yaml --tts test
```
Les noms des fichiers de la démo dépendent d'une empreinte du contenu. S'ils diffèrent chez
vous, recréez le projet avec `python gta.py new demo2`.

## Licences et droits
- Police Inter : SIL OFL 1.1 (`assets/fonts/LICENSE-Inter-OFL.txt`).
- Les ressources de test sont générées par FFmpeg et n'ont aucun ayant droit.
- Musique : utilisez uniquement des titres libres de droits ou sous licence (bibliothèque audio
  YouTube, bibliothèque commerciale TikTok). **N'utilisez pas les radios de GTA.**
- Voix off : voir `docs/VOIX_OFF.md` (crédit obligatoire pour Piper SIWIS, sous CC BY 4.0).
