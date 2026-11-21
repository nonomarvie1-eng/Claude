"""Synthèse vocale française, phrase par phrase.

Chaque phrase est synthétisée séparément : on connaît donc sa durée exacte, ce
qui donne des sous-titres calés à l'échantillon près sur la voix.

Moteurs :
  piper       local, gratuit, hors ligne (voix sous licence ouverte, voir docs/VOIX_OFF.md)
  azure       Microsoft Azure Speech (offre gratuite F0 mensuelle, clé requise)
  elevenlabs  ElevenLabs (usage commercial seulement avec un plan payant)
  test        signal "parole synthétique" sans voix réelle, pour tester le pipeline
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import wave
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

from .utils import PipelineError, log, p, read_wav, to_wav48, write_wav

PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


@dataclass
class Segment:
    text: str
    wav: Path
    duration: float


# ----------------------------------------------------------------- backends
def _piper(text: str, out: Path, cfg: dict) -> None:
    try:
        from piper import PiperVoice  # type: ignore
    except ImportError as e:
        raise PipelineError("Piper n'est pas installé (pip install piper-tts). "
                            "Ou utilisez --tts test pour un essai sans voix.") from e
    pc = cfg["tts"]["piper"]
    model = p(cfg, "voices") / f"{pc['voice']}.onnx"
    if not model.exists():
        raise PipelineError(f"Voix absente : {model}\n"
                            f"Téléchargez-la : python gta.py voices --download {pc['voice']}")
    voice = _piper.cache.get(str(model)) or PiperVoice.load(str(model))
    _piper.cache[str(model)] = voice
    ls = float(pc.get("length_scale", 1.0))
    with wave.open(str(out), "wb") as wf:
        if hasattr(voice, "synthesize_wav"):          # piper-tts >= 1.3
            from piper import SynthesisConfig  # type: ignore
            voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=ls))
        else:                                          # piper-tts 1.2
            voice.synthesize(text, wf, length_scale=ls)


_piper.cache = {}


def _azure(text: str, out: Path, cfg: dict) -> None:
    import requests
    key = os.environ.get("AZURE_SPEECH_KEY")
    if not key:
        raise PipelineError("Variable d'environnement AZURE_SPEECH_KEY absente.")
    ac = cfg["tts"]["azure"]
    ssml = (f"<speak version='1.0' xml:lang='fr-FR'><voice name='{ac['voice']}'>"
            f"<prosody rate='{ac.get('rate', '0%')}'>{escape(text)}</prosody></voice></speak>")
    r = requests.post(
        f"https://{ac['region']}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={"Ocp-Apim-Subscription-Key": key,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "riff-48khz-16bit-mono-pcm",
                 "User-Agent": "gta-media-pipeline"},
        data=ssml.encode("utf-8"), timeout=60)
    if r.status_code != 200:
        raise PipelineError(f"Azure TTS : HTTP {r.status_code} {r.text[:200]}")
    out.write_bytes(r.content)


def _elevenlabs(text: str, out: Path, cfg: dict) -> None:
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise PipelineError("Variable d'environnement ELEVENLABS_API_KEY absente.")
    ec = cfg["tts"]["elevenlabs"]
    if not ec.get("voice_id"):
        raise PipelineError("tts.elevenlabs.voice_id est vide dans settings.yaml")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ec['voice_id']}?output_format=pcm_44100",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        json={"text": text, "model_id": ec["model"], "language_code": "fr"}, timeout=120)
    if r.status_code != 200:
        raise PipelineError(f"ElevenLabs : HTTP {r.status_code} {r.text[:200]}")
    pcm = np.frombuffer(r.content, dtype="<i2").astype(np.float32) / 32768.0
    write_wav(out, pcm, 44100)


def _test(text: str, out: Path, cfg: dict) -> None:
    """Signal à l'enveloppe de parole (syllabes ~5/s), durée réaliste. PAS une voix."""
    sr = 48000
    words = text.split()
    syll = sum(max(1, sum(c in "aeiouyéèêàùâîôûAEIOUY" for c in w)) for w in words)
    dur = max(0.6, syll / 5.2)
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    t = np.arange(int(sr * dur)) / sr
    f0 = 125 + 25 * np.sin(2 * np.pi * 0.7 * t)                       # intonation
    phase = 2 * np.pi * np.cumsum(f0) / sr
    voiced = sum(np.sin(k * phase) / k for k in range(1, 12))          # timbre "voix"
    env = np.zeros_like(t)
    pos = 0.0
    for w in words:                                                     # mots + micro-pauses
        n = max(1, sum(c in "aeiouyéèêàùâîôû" for c in w.lower()))
        wl = dur * n / syll * 0.86
        for k in range(n):
            a, b = pos + k * wl / n, pos + (k + 1) * wl / n
            m = (t >= a) & (t < b)
            env[m] = np.sin(np.pi * (t[m] - a) / (b - a)) ** 0.6
        pos += dur * n / syll
    noise = rng.standard_normal(len(t)) * 0.08
    sig = (voiced * 0.35 + noise) * env
    write_wav(out, sig / (np.abs(sig).max() + 1e-9) * 0.7, sr)


BACKENDS = {"piper": _piper, "azure": _azure, "elevenlabs": _elevenlabs, "test": _test}


def _cache_key(text: str, cfg: dict, backend: str) -> str:
    settings = json.dumps(cfg["tts"].get(backend, {}), sort_keys=True)
    return hashlib.sha1(f"{backend}|{settings}|{text}".encode()).hexdigest()[:20]


def synthesize(sentences: list[str], cfg: dict, backend: str | None = None) -> list[Segment]:
    backend = backend or cfg["tts"]["backend"]
    if backend not in BACKENDS:
        raise PipelineError(f"Moteur TTS inconnu : {backend} ({', '.join(BACKENDS)})")
    cache = p(cfg, "work") / "tts_cache"
    cache.mkdir(parents=True, exist_ok=True)
    segs = []
    log(f"▶ Narration ({backend}) : {len(sentences)} phrase(s)")
    for i, text in enumerate(sentences, 1):
        key = _cache_key(text, cfg, backend)
        final = cache / f"{key}.wav"
        if not final.exists():
            raw = cache / f"{key}.raw.wav"
            BACKENDS[backend](text, raw, cfg)
            to_wav48(raw, final, trim_silence=True)
            raw.unlink(missing_ok=True)
        data, sr = read_wav(final)
        segs.append(Segment(text, final, len(data) / sr))
        log(f"   {i:02d}. {len(data)/sr:5.2f}s  {text}")
    return segs


def build_narration(segs: list[Segment], cfg: dict, out: Path) -> list[dict]:
    """Place les phrases sur la timeline à l'échantillon près. Renvoie les repères."""
    a = cfg["audio"]
    sr = 48000
    cues, t = [], float(a["lead_in"])
    for s in segs:
        cues.append({"text": s.text, "start": round(t, 4), "end": round(t + s.duration, 4)})
        t += s.duration + float(a["sentence_gap"])
    total = cues[-1]["end"] + float(a["tail"])
    track = np.zeros(int(round(total * sr)) + 1, dtype=np.float32)
    for s, c in zip(segs, cues):
        data, _ = read_wav(s.wav)
        i0 = int(round(c["start"] * sr))
        track[i0:i0 + len(data)] += data
    write_wav(out, track, sr)
    return cues


def download_voice(cfg: dict, voice: str) -> None:
    """Télécharge une voix Piper (modèle .onnx + config + fiche de licence)."""
    import requests
    parts = voice.split("-")                       # fr_FR-siwis-medium
    if len(parts) != 3:
        raise PipelineError("Nom attendu : langue_PAYS-nom-qualité, ex fr_FR-siwis-medium")
    lang, name, quality = parts
    base = f"{PIPER_BASE}/{lang.split('_')[0]}/{lang}/{name}/{quality}"
    dst = p(cfg, "voices")
    dst.mkdir(parents=True, exist_ok=True)
    for fname, remote in [(f"{voice}.onnx.json", f"{voice}.onnx.json"),
                          (f"{voice}.MODEL_CARD.txt", "MODEL_CARD"),
                          (f"{voice}.onnx", f"{voice}.onnx")]:
        url = f"{base}/{remote}"
        log(f"   ↓ {url}")
        try:
            r = requests.get(url, timeout=300)
        except requests.RequestException as e:
            raise PipelineError(f"Connexion impossible pour {url}\n"
                                f"Vérifiez Internet / pare-feu / proxy. Détail : {str(e)[:300]}") from e
        if r.status_code != 200:
            raise PipelineError(f"Téléchargement impossible ({r.status_code}) : {url}")
        (dst / fname).write_bytes(r.content)
    card = (dst / f"{voice}.MODEL_CARD.txt").read_text(encoding="utf-8", errors="replace")
    log("✔ Voix installée. Fiche de licence (à lire avant usage commercial) :\n" + card)
