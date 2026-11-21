"""Fonctions communes : configuration, appels FFmpeg/FFprobe, fichiers WAV."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent


class PipelineError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(msg, flush=True)


def deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Path | None = None) -> dict:
    path = path or ROOT / "config" / "settings.yaml"
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def p(cfg: dict, key: str) -> Path:
    """Chemin absolu d'une entrée de cfg['paths']."""
    path = Path(cfg["paths"][key])
    return path if path.is_absolute() else ROOT / path


def require_tool(name: str) -> str:
    exe = shutil.which(name)
    if not exe:
        raise PipelineError(
            f"'{name}' est introuvable dans le PATH. Lancez scripts/windows/install.ps1 "
            f"ou installez-le (voir README)."
        )
    return exe


def run(cmd: list[str], cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess:
    res = subprocess.run(
        [str(c) for c in cmd],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        tail = "\n".join(res.stderr.strip().splitlines()[-25:])
        raise PipelineError(f"Échec de la commande :\n{' '.join(map(str, cmd))[:600]}\n---\n{tail}")
    return res


def ffprobe(path: Path) -> dict:
    res = run([require_tool("ffprobe"), "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", str(path)])
    return json.loads(res.stdout)


def ffmpeg_has(kind: str, name: str) -> bool:
    """kind = 'filters' ou 'encoders'."""
    res = subprocess.run([require_tool("ffmpeg"), "-hide_banner", f"-{kind}"],
                         capture_output=True, text=True)
    return any(line.split()[1:2] == [name] for line in res.stdout.splitlines() if line.strip())


def parse_rate(rate: str) -> float:
    if "/" in rate:
        a, b = rate.split("/")
        return float(a) / float(b) if float(b) else 0.0
    return float(rate)


# ---------------------------------------------------------------- audio WAV
def read_wav(path: Path) -> tuple[np.ndarray, int]:
    """Lit un WAV PCM 16 bits -> (float32 mono, samplerate)."""
    with wave.open(str(path), "rb") as w:
        sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
        raw = w.readframes(n)
    if sw != 2:
        raise PipelineError(f"{path} : seul le PCM 16 bits est géré")
    data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    return data, sr


def write_wav(path: Path, data: np.ndarray, sr: int) -> None:
    pcm = np.clip(data, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def to_wav48(src: Path, dst: Path, trim_silence: bool = True) -> None:
    """Convertit en WAV mono 48 kHz, en retirant les silences de début/fin."""
    af = "aresample=48000"
    if trim_silence:
        trim = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02"
        af = f"{trim},areverse,{trim},areverse,aresample=48000"
    run([require_tool("ffmpeg"), "-y", "-v", "error", "-i", str(src), "-ac", "1",
         "-af", af, "-c:a", "pcm_s16le", str(dst)])


def python_exe() -> str:
    return sys.executable
