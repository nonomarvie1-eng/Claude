"""Contrôle qualité automatique d'une vidéo produite.

1. Format : 1080x1920, H.264 yuv420p, AAC 48 kHz, faststart.
2. Lisibilité : décodage complet sans erreur.
3. Synchro audio : corrélation croisée entre la voix off d'origine et l'audio
   final → décalage mesuré (doit être < 1 image).
4. Synchro sous-titres : chaque début de phrase sous-titrée doit coïncider
   avec un démarrage de parole détecté dans l'audio.
5. Planche contact : images extraites aux instants des sous-titres.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from .utils import PipelineError, ffprobe, log, parse_rate, read_wav, require_tool, run

SR = 16000


def decode_audio(path: Path) -> np.ndarray:
    res = subprocess.run([require_tool("ffmpeg"), "-v", "error", "-i", str(path), "-vn", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True)
    if res.returncode != 0:
        raise PipelineError(res.stderr.decode(errors="replace")[-500:])
    return np.frombuffer(res.stdout, dtype="<i2").astype(np.float32) / 32768.0


def resample(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    n = int(len(x) * sr_out / sr_in)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def xcorr_lag(ref: np.ndarray, sig: np.ndarray, max_lag_s: float = 0.5) -> tuple[float, float]:
    """Décalage (s) de sig par rapport à ref. Positif = sig en retard."""
    n = min(len(ref), len(sig))
    a, b = ref[:n] - ref[:n].mean(), sig[:n] - sig[:n].mean()
    size = 1 << (2 * n - 1).bit_length()
    c = np.fft.irfft(np.fft.rfft(b, size) * np.conj(np.fft.rfft(a, size)), size)
    m = int(max_lag_s * SR)
    lags = np.concatenate([np.arange(0, m + 1), np.arange(-m, 0)])
    vals = np.concatenate([c[:m + 1], c[-m:]])
    k = int(np.argmax(vals))
    score = float(vals[k] / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    return lags[k] / SR, score


def speech_onsets(x: np.ndarray, hop: float = 0.01, min_gap: float = 0.12) -> list[float]:
    """Instants où la parole démarre après un silence d'au moins min_gap."""
    h = int(SR * hop)
    frames = len(x) // h
    rms = np.sqrt(np.mean(x[:frames * h].reshape(frames, h) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    active = db > max(db.max() - 35, -50)
    onsets, silent_run = [], int(min_gap / hop)
    quiet = silent_run
    for i, on in enumerate(active):
        if on and quiet >= silent_run:
            onsets.append(i * hop)
        quiet = 0 if on else quiet + 1
    return onsets


def verify(video: Path, timeline_file: Path | None = None, sheet: bool = True) -> dict:
    video = video.resolve()
    checks, ok = [], True

    def check(name: str, passed: bool, detail: str):
        nonlocal ok
        ok &= passed
        checks.append({"test": name, "ok": bool(passed), "detail": detail})
        log(f"   {'✔' if passed else '✗'} {name} — {detail}")

    log(f"▶ Vérification : {video.name}")
    info = ffprobe(video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    aus = [s for s in info["streams"] if s["codec_type"] == "audio"]
    fps = parse_rate(vs["avg_frame_rate"])
    check("Résolution verticale", (vs["width"], vs["height"]) == (1080, 1920), f"{vs['width']}x{vs['height']}")
    check("Codec vidéo compatible", vs["codec_name"] == "h264" and vs["pix_fmt"] == "yuv420p",
          f"{vs['codec_name']} {vs.get('profile')} {vs['pix_fmt']} {fps:.2f} i/s")
    check("Piste audio", bool(aus) and aus[0]["codec_name"] == "aac" and aus[0]["sample_rate"] == "48000",
          f"{aus[0]['codec_name']} {aus[0]['sample_rate']} Hz {aus[0].get('channels')} canaux" if aus else "absente")
    vd, ad = float(vs.get("duration", 0)), float(aus[0].get("duration", 0)) if aus else 0
    check("Durées audio/vidéo identiques", abs(vd - ad) <= 1.5 / fps,
          f"vidéo {vd:.3f}s / audio {ad:.3f}s (écart {abs(vd-ad)*1000:.0f} ms)")
    with open(video, "rb") as f:
        head = f.read(64 * 1024)
    check("Lecture web rapide (moov en tête)", head.find(b"moov") != -1 and
          (head.find(b"mdat") == -1 or head.find(b"moov") < head.find(b"mdat")), "faststart")

    res = subprocess.run([require_tool("ffmpeg"), "-v", "error", "-i", str(video), "-f", "null", "-"],
                         capture_output=True, text=True)
    errs = res.stderr.strip()
    check("Décodage complet sans erreur", res.returncode == 0 and not errs,
          "OK" if not errs else errs.splitlines()[0][:120])

    report = {"video": str(video), "checks": checks}
    tl = json.loads(timeline_file.read_text(encoding="utf-8")) if timeline_file and timeline_file.exists() else None
    if tl and not tl["cues"]:
        log("   (pas de voix off : contrôles de synchronisation voix/sous-titres sans objet)")
    if tl and tl["cues"]:
        nar, sr = read_wav(Path(tl["narration_wav"]))
        nar = resample(nar, sr, SR)
        final = decode_audio(video)
        lag, score = xcorr_lag(nar, final)
        check("Synchro voix off ↔ audio final", abs(lag) * 1000 <= 1000 / fps,
              f"décalage mesuré {lag*1000:+.1f} ms (tolérance ±{1000/fps:.0f} ms, corrélation {score:.2f})")
        onsets = speech_onsets(nar)
        errors = []
        for c in tl["cues"]:
            near = min(onsets, key=lambda o: abs(o - c["start"])) if onsets else 99
            errors.append(abs(near - c["start"] - 0) * 1000)
        worst = max(errors) if errors else 999
        check("Synchro sous-titres ↔ début des phrases", worst <= 60,
              f"{len(errors)} phrases, écart moyen {np.mean(errors):.0f} ms, max {worst:.0f} ms (tolérance 60 ms)")
        last = max(c["end"] for c in tl["cues"])
        check("Sous-titres dans la durée de la vidéo", last <= vd, f"dernier sous-titre {last:.2f}s / {vd:.2f}s")
        report.update({"audio_lag_ms": round(lag * 1000, 2), "subtitle_max_error_ms": round(worst, 1)})

        if sheet:
            frames_dir = timeline_file.parent / "verify"
            frames_dir.mkdir(exist_ok=True)
            times = [0.6] + [round((w["start"] + w["end"]) / 2, 3) for w in tl["words"][::max(1, len(tl["words"]) // 5)]][:5]
            for i, t in enumerate(times):
                run([require_tool("ffmpeg"), "-y", "-v", "error", "-ss", str(t), "-i", str(video),
                     "-frames:v", "1", "-vf", "scale=360:640", str(frames_dir / f"f{i}.png")])
            sheet_png = video.with_name(video.stem + "_controle.png")
            run([require_tool("ffmpeg"), "-y", "-v", "error", "-i", str(frames_dir / "f%d.png"),
                 "-vf", f"tile={len(times)}x1:padding=8:color=white", "-frames:v", "1", str(sheet_png)])
            report["contact_sheet"] = str(sheet_png)
            log(f"   planche contact : {sheet_png}")

    report["ok"] = bool(ok)
    out = video.with_name(video.stem + "_verification.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"{'✔ VIDÉO VALIDÉE' if ok else '✗ PROBLÈMES DÉTECTÉS'} — rapport : {out}")
    return report
