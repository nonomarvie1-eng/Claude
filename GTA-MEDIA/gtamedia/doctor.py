"""Diagnostic de l'environnement (Windows, macOS ou Linux)."""
from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
import sys

from .utils import ROOT, ffmpeg_has, p

REQUIRED_FILTERS = ["ass", "xfade", "loudnorm", "sidechaincompress", "gblur", "drawbox", "acrossfade"]
OPTIONAL_FILTERS = ["zscale", "tonemap"]


def _ver(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception as e:  # noqa: BLE001
        return f"erreur : {e}"


def doctor(cfg: dict) -> bool:
    ok = True

    def line(status: str, name: str, detail: str):
        print(f"  [{status}] {name:<22} {detail}")

    print("=== GTA-MEDIA : diagnostic ===")
    line("i", "Système", f"{platform.system()} {platform.release()} ({platform.version()}) {platform.machine()}")
    py_ok = sys.version_info >= (3, 10)
    ok &= py_ok
    line("OK" if py_ok else "!!", "Python", f"{sys.version.split()[0]} ({sys.executable})")

    for tool in ("ffmpeg", "ffprobe"):
        v = _ver([tool, "-version"])
        ok &= v is not None
        line("OK" if v else "!!", tool, v or "ABSENT — requis")
    if shutil.which("ffmpeg"):
        missing = [f for f in REQUIRED_FILTERS if not ffmpeg_has("filters", f)]
        ok &= not missing
        line("OK" if not missing else "!!", "Filtres FFmpeg", "tous présents" if not missing else f"manquants : {missing}")
        opt = [f for f in OPTIONAL_FILTERS if not ffmpeg_has("filters", f)]
        line("OK" if not opt else "--", "Tonemapping HDR", "zscale+tonemap OK" if not opt else "absent (captures HDR ternes)")
        x264 = ffmpeg_has("encoders", "libx264")
        ok &= x264
        line("OK" if x264 else "!!", "Encodeur libx264", "présent" if x264 else "ABSENT")
        nv = ffmpeg_has("encoders", "h264_nvenc")
        line("i", "Encodeur NVIDIA", "h264_nvenc compilé (utilisable si GPU NVIDIA)" if nv else "non disponible")

    node = _ver(["node", "--version"])
    line("OK" if node else "--", "Node.js (optionnel)", node or "absent (non requis pour ce pipeline)")
    git = _ver(["git", "--version"])
    line("OK" if git else "--", "Git (recommandé)", git or "absent")

    for mod, req in [("yaml", True), ("numpy", True), ("requests", True), ("piper", False)]:
        found = importlib.util.find_spec(mod) is not None
        if req:
            ok &= found
        line("OK" if found else ("!!" if req else "--"), f"module {mod}",
             "installé" if found else ("ABSENT — pip install -r requirements.txt" if req else "absent (voix Piper)"))

    voice = p(cfg, "voices") / f"{cfg['tts']['piper']['voice']}.onnx"
    line("OK" if voice.exists() else "--", "Voix Piper", str(voice.relative_to(ROOT)) if voice.exists()
         else f"absente — python gta.py voices --download {cfg['tts']['piper']['voice']}")
    fonts = list(p(cfg, "fonts").glob("*.otf")) + list(p(cfg, "fonts").glob("*.ttf"))
    line("OK" if fonts else "!!", "Polices", ", ".join(f.name for f in fonts) or "aucune")
    free = shutil.disk_usage(ROOT).free / 1e9
    line("OK" if free > 20 else "!!", "Espace disque", f"{free:.0f} Go libres (20 Go conseillés)")
    print("=== Résultat :", "PRÊT" if ok else "INCOMPLET (voir lignes !!)", "===")
    return ok
