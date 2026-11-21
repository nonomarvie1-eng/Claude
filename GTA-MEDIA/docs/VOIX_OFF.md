# Voix off française : comparatif (usage commercial)

*Vérifié le 21/11/2026. Les prix et conditions changent : relisez toujours les conditions
officielles avant de monétiser. Aucun abonnement n'est souscrit par le pipeline.*

| Solution | Coût | Usage commercial | Qualité FR | Hors ligne | Intégré au pipeline |
|---|---|---|---|---|---|
| **Votre propre voix** (micro USB ~30–60 €) | gratuit | ✅ total | la plus authentique | ✅ | phase 2 (alignement Whisper) |
| **Piper** — voix `fr_FR-siwis-medium` | gratuit | ✅ CC BY 4.0 → **créditer** la base SIWIS | correcte, un peu robotique | ✅ | ✅ `tts.backend: piper` |
| **Kokoro-82M** — voix `ff_siwis` | gratuit | ✅ poids Apache-2.0 (données SIWIS CC BY 4.0) | bonne | ✅ | à ajouter si Piper ne suffit pas |
| **Azure AI Speech** (`fr-FR-HenriNeural`, `DeniseNeural`…) | 0,5 M caractères/mois gratuits (offre F0), puis paiement à l'usage | ✅ | très bonne, naturelle | ❌ | ✅ `tts.backend: azure` |
| **ElevenLabs** | gratuit = **non commercial** ; offre Starter ≈ 5–6 $/mois | ✅ uniquement avec un plan payant | excellente | ❌ | ✅ `tts.backend: elevenlabs` |
| Coqui XTTS v2 | gratuit | ❌ licence CPML non commerciale | — | — | exclu |
| edge-tts (voix lecture Edge) | gratuit | ❌ usage non autorisé du service | — | — | exclu |

## Repères de volume
Un Short de 45 s ≈ 600–700 caractères. Les 0,5 M caractères gratuits d'Azure couvrent donc
**environ 700 vidéos par mois**. Il faut un compte Azure (une carte bancaire est demandée à
l'inscription) : **je ne le crée pas sans votre accord**.

## Recommandation
1. **Démarrer avec Piper** : gratuit, local, sans compte. À créditer en description :
   « Voix de synthèse : Piper (voix fr_FR-siwis, base SIWIS, CC BY 4.0) ».
2. Si la voix paraît trop robotique : passer à **Azure F0** (gratuit dans la limite mensuelle),
   bien plus naturel.
3. ElevenLabs seulement si vous décidez de payer, car l'offre gratuite interdit la monétisation.

## Obligations plateformes
- YouTube et TikTok demandent d'étiqueter les contenus **réalistes** générés par IA. Une voix
  de synthèse qui commente du gameplay n'est généralement pas concernée, mais ne faites jamais
  imiter la voix d'une personne réelle.
- La politique de Rockstar/Take-Two autorise les vidéos de gameplay monétisées. Évitez d'utiliser
  la musique des radios du jeu (ce qui déclenche souvent un Content ID) : le pipeline baisse le son du jeu.

Sources : [piper-voices siwis](https://huggingface.co/rhasspy/piper-voices/tree/856d185c267ad13c45e707792c8c6fbf5fac01d9/fr/fr_FR/siwis/medium),
[re-host siwis (CC BY 4.0)](https://huggingface.co/Trelis/piper-fr-fr-siwis-medium),
[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M),
[Tarifs Azure Speech](https://azure.microsoft.com/pricing/details/cognitive-services/speech-services),
[Facturation ElevenLabs](https://elevenlabs.io/docs/overview/administration/billing),
[Tarifs ElevenLabs](https://www.elevenlabs.io/pricing).
