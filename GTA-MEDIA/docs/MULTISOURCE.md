# Montage multisource : méthode, droits et commandes

## Principe
Une vidéo = un **script en « beats »** : chaque phrase de narration porte l'extrait qui
l'illustre. Le pipeline :
1. génère la voix phrase par phrase ;
2. cale chaque extrait **exactement sur sa phrase** : le plan commence 0,12 s avant la voix ;
3. ajoute les sous-titres dynamiques, les annotations (cercle, bulle), les crédits et la marque ;
4. **refuse de monter** si un extrait n'a pas un statut de droits autorisé, et écrit
   `A_FILMER.md` avec le plan Xbox de remplacement.

## Quelles sources sont réellement utilisables ?
| Source | Statut dans le registre | Utilisable | Conditions |
|---|---|---|---|
| Vos captures Xbox (`ingest`) | `capture_perso` | ✅ | Politique vidéo Rockstar : pas de spoiler ni de cinématique isolée |
| Vidéo YouTube sous licence **Creative Commons BY** | `cc_by` | ✅ | Crédit obligatoire (fait automatiquement). Voir l'avertissement sur le téléchargement ci-dessous |
| Créateur qui a donné son **accord écrit** | `autorisation_ecrite` + `proof` | ✅ | Garder la capture d'écran de l'accord dans `sources/autorisations/` |
| Bande-annonce ou image officielle Rockstar | `officiel_rockstar` | ⛔ par défaut | À débloquer (`rights.allow_official: true`) seulement après lecture de la politique Rockstar |
| Vidéo TikTok ou YouTube classique, sans accord | `non_autorise` | ⛔ | Demander l'accord (`python gta.py permission ID`) ou filmer le remplacement |
| Statut non vérifié | `inconnu` | ⛔ | — |

**Ce qui ne rend PAS un extrait utilisable** : sa brièveté, un recadrage, un filtre, une voix
off par-dessus, ou le fait de citer l'auteur sans son accord.

**Droit de citation (France, art. L122-5 du Code de la propriété intellectuelle)** : il couvre
de « courtes citations justifiées par le caractère critique, polémique, pédagogique,
scientifique ou d'information » de l'œuvre qui les accueille. Son application aux extraits
vidéo est étroite et incertaine. De plus, les plateformes appliquent leurs propres systèmes
de détection (comme Content ID), quelle que soit l'exception invoquée. **Le pipeline ne
s'appuie donc pas dessus.**

**Téléchargement depuis YouTube** : la licence CC BY autorise la réutilisation de l'œuvre,
mais les conditions d'utilisation de YouTube encadrent le téléchargement en dehors des
fonctions qu'il prévoit. La voie la plus propre est de **demander le fichier à l'auteur**
(message généré par `permission`). Le pipeline ne télécharge rien automatiquement.

**TikTok** n'a pas de licence libre : tout extrait TikTok demande l'accord du créateur.

## Commandes
```powershell
python gta.py research "gta 6 physique eau"        # vidéos YouTube CC BY (clé YOUTUBE_API_KEY gratuite)
python gta.py research "gta 6 physique eau" --all-licenses   # tout, pour repérer qui contacter
python gta.py sources                               # registre et statuts
python gta.py source-add yt_XXXX --status autorisation_ecrite --proof sources/autorisations/XXXX.png --file library/XXXX.mp4
python gta.py permission yt_XXXX --from 0:12 --to 0:18   # message de demande à envoyer
python gta.py rights projects\NOM\episode.yaml      # contrôle des droits sans monter
python gta.py build projects\NOM\episode.yaml       # contrôle des droits, puis montage, puis vérification
```

## Clé YouTube Data API (gratuite)
1. console.cloud.google.com : créez un projet, puis « API et services » → activez **YouTube Data API v3**.
2. « Identifiants » → **Créer une clé API**. Restreignez-la à YouTube Data API v3.
3. Dans PowerShell : `setx YOUTUBE_API_KEY "votre_clé"`, puis rouvrez PowerShell.
Le quota gratuit est de 10 000 unités par jour. Une recherche en coûte environ 100, soit environ
une centaine de recherches par jour.

## Routine quotidienne (« Prépare la vidéo GTA du jour »)
| Étape | Qui | Durée |
|---|---|---|
| Sujet, vérification des faits, script en beats, choix des extraits | Claude | — |
| Recherche de sources libres (CC BY) et demandes d'autorisation | Claude (+ vous pour envoyer les messages) | 2 min |
| Plans manquants → liste `A_FILMER.md` | Claude | — |
| Capture des plans manquants sur Xbox | **Vous** | 10 à 20 min |
| `ingest` puis `build` : droits, voix, montage, vérification | PC | quelques minutes |
| Texte, hashtags, couverture, crédits | Claude + fichier `_credits.txt` | — |
| Validation et publication | **Vous** | 2 min |

Les crédits de chaque vidéo sont écrits dans `output/NOM_credits.txt`. Copiez-les en
description quand une source CC BY ou autorisée est utilisée.
