"""Montage vertical 1080x1920 en une seule passe FFmpeg.

Vidéo : découpe des plans → recadrage 9:16 (crop centré ou fond flouté) →
zoom lent → étalonnage → fondus entre plans → flash d'intro → titre et
sous-titres (libass) → barre de progression.
Audio : voix off + musique en boucle + son du jeu, ducking (la musique baisse
quand la voix parle), normalisation -14 LUFS.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import yaml

from . import subtitles, tts
from .utils import ROOT, PipelineError, ffprobe, log, p, require_tool, run


def filter_script_args(ffmpeg: str, name: str) -> list[str]:
    """FFmpeg >= 7 lit une option depuis un fichier avec '-/option' ;
    les versions plus anciennes utilisent '-filter_complex_script'."""
    import re
    import subprocess
    ver = subprocess.run([ffmpeg, "-version"], capture_output=True, text=True).stdout
    m = re.search(r"ffmpeg version n?(\d+)\.", ver)
    major = int(m.group(1)) if m else 0
    return ["-/filter_complex", name] if major >= 7 else ["-filter_complex_script", name]


def load_project(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        proj = yaml.safe_load(f)
    for key in ("clips", "narration"):
        if not proj.get(key):
            raise PipelineError(f"{path} : section '{key}' vide")
    return proj


def resolve(path: str, base: Path) -> Path:
    cand = Path(path)
    if cand.is_absolute():
        return cand
    for root in (base, ROOT):
        if (root / cand).exists():
            return root / cand
    raise PipelineError(f"Fichier introuvable : {path}")


def plan_segments(clips: list[dict], target: float, xd: float) -> list[dict]:
    """Enchaîne les plans (en boucle si besoin) jusqu'à couvrir la durée voulue."""
    segs, covered, i = [], 0.0, 0
    while covered < target + 0.05:
        c = dict(clips[i % len(clips)])
        c["dur"] = float(c["end"]) - float(c["start"])
        if c["dur"] <= xd + 0.2:
            raise PipelineError(f"Plan trop court : {c}")
        segs.append(c)
        covered += c["dur"] - (xd if len(segs) > 1 else 0)
        i += 1
        if i > 200:
            raise PipelineError("Durée de plans insuffisante")
    return segs


def video_chain(idx: int, seg: dict, cfg: dict) -> str:
    v, fx = cfg["video"], cfg["effects"]
    W, H, fps = v["width"], v["height"], v["fps"]
    d = seg["dur"]
    layout = seg.get("layout", "crop")
    focus = float(seg.get("focus_x", 0.5))
    base = f"[{idx}:v]fps={fps},setpts=PTS-STARTPTS,setsar=1"
    if layout == "blur":
        fg_w = int(W * float(seg.get("fg_zoom", 1.35)))
        chain = (f"{base},split[a{idx}][b{idx}];"
                 f"[a{idx}]scale={W//4}:{H//4}:force_original_aspect_ratio=increase,crop={W//4}:{H//4},"
                 f"gblur=sigma=12,scale={W}:{H},eq=brightness=-0.12:saturation=1.1[bg{idx}];"
                 f"[b{idx}]scale={fg_w}:-2,crop='min(iw,{W})':ih:(iw-ow)*{focus}:0[fg{idx}];"
                 f"[bg{idx}][fg{idx}]overlay=(W-w)/2:(H-h)/2")
    else:  # crop plein écran
        chain = f"{base},scale=-2:{H}:flags=lanczos,crop={W}:{H}:(iw-ow)*{focus}:0"
    z = float(seg.get("zoom", fx["zoom"]))
    if z > 0:
        hw, hh = W // 2, H // 2
        chain += (f",scale=w='2*trunc({hw}*(1+{z}*t/{d:.3f}))':h='2*trunc({hh}*(1+{z}*t/{d:.3f}))'"
                  f":eval=frame:flags=bicubic,crop={W}:{H}")
    chain += f",eq=contrast={fx['contrast']}:saturation={fx['saturation']}:brightness={fx['brightness']}"
    if fx.get("sharpen"):
        chain += ",unsharp=5:5:0.5"
    if fx.get("vignette"):
        chain += ",vignette=angle=PI/5"
    chain += f",format=yuv420p,trim=0:{d:.3f},setpts=PTS-STARTPTS[v{idx}]"
    return chain


def audio_chain(idx: int, seg: dict, has_audio: bool) -> str:
    d = seg["dur"]
    if has_audio:
        return (f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
                f"asetpts=PTS-STARTPTS,atrim=0:{d:.3f},apad,atrim=0:{d:.3f}[ga{idx}]")
    return f"anullsrc=r=48000:cl=stereo,atrim=0:{d:.3f}[ga{idx}]"


def build(project_file: Path, cfg: dict, backend: str | None = None, out: Path | None = None) -> dict:
    ffmpeg = require_tool("ffmpeg")
    project_file = project_file.resolve()
    proj = load_project(project_file)
    name = proj.get("name") or project_file.parent.name
    work = p(cfg, "work") / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    out = out or p(cfg, "output") / f"{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1) Voix off
    segs = tts.synthesize(proj["narration"], cfg, backend or proj.get("tts"))
    narration_wav = work / "narration.wav"
    cues = tts.build_narration(segs, cfg, narration_wav)
    total = round(cues[-1]["end"] + float(cfg["audio"]["tail"]), 3)
    log(f"   durée finale : {total:.2f}s")

    # 2) Sous-titres
    ass, srt = work / "subs.ass", out.with_suffix(".srt")
    words = subtitles.build_ass(cues, cfg, proj.get("title", ""), float(proj.get("title_duration", 2.8)),
                                total, ass, srt)

    # 3) Plan de montage
    fx = cfg["effects"]
    xd = float(fx["transition_duration"])
    segments = plan_segments(proj["clips"], total, xd)
    inputs, filters = [], []
    for i, s in enumerate(segments):
        src = resolve(s["file"], project_file.parent)
        s["path"] = src
        s["has_audio"] = any(st["codec_type"] == "audio" for st in ffprobe(src)["streams"])
        inputs += ["-ss", f"{float(s['start']):.3f}", "-t", f"{s['dur'] + 0.1:.3f}", "-i", src]
        filters.append(video_chain(i, s, cfg))
        filters.append(audio_chain(i, s, s["has_audio"]))
    n = len(segments)
    nar_idx, mus_idx = n, None
    inputs += ["-i", narration_wav]
    music = proj.get("music")
    if music:
        mus_idx = n + 1
        inputs += ["-stream_loop", "-1", "-i", resolve(music, project_file.parent)]

    # Enchaînement vidéo (xfade) et audio (acrossfade)
    vlast, alast, offset = "[v0]", "[ga0]", segments[0]["dur"]
    for i in range(1, n):
        offset -= xd
        filters.append(f"{vlast}[v{i}]xfade=transition={fx['transition']}:duration={xd}:offset={offset:.3f}[x{i}]")
        filters.append(f"{alast}[ga{i}]acrossfade=d={xd}:c1=tri:c2=tri[xa{i}]")
        vlast, alast = f"[x{i}]", f"[xa{i}]"
        offset += segments[i]["dur"]

    W, H = cfg["video"]["width"], cfg["video"]["height"]
    post = f"{vlast}trim=0:{total},setpts=PTS-STARTPTS"
    if fx.get("flash_intro"):
        post += ",fade=t=in:st=0:d=0.35:color=white"
    rel_fonts = os.path.relpath(p(cfg, "fonts"), work).replace("\\", "/")
    post += f",ass=subs.ass:fontsdir='{rel_fonts}'"
    if fx.get("progress_bar"):
        # Barre de progression : une bande de couleur qui glisse depuis la gauche.
        # (overlay avec x dépendant du temps : compatible FFmpeg 4 à 9, contrairement
        #  à drawbox dont la largeur 0 au départ est refusée par FFmpeg >= 7)
        fps = cfg["video"]["fps"]
        filters.append(post + "[pre]")
        filters.append(f"color=c=0x{cfg['style']['highlight_color']}:s={W}x12:r={fps}:d={total}[bar]")
        post = f"[pre][bar]overlay=x='-w+w*t/{total}':y=H-12:eval=frame:shortest=1"
    post += ",fade=t=out:st={:.3f}:d=0.4,format=yuv420p[vout]".format(total - 0.4)
    filters.append(post)

    a = cfg["audio"]
    filters.append(f"[{nar_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[nar][sc]")
    filters.append(f"{alast}atrim=0:{total},volume={a['game_volume']}[game]")
    if mus_idx is not None:
        filters.append(f"[{mus_idx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},"
                       f"volume={a['music_volume']},afade=t=out:st={total - 1.2:.3f}:d=1.2[mus]")
        filters.append("[game][mus]amix=inputs=2:normalize=0:duration=first[bed]")
    else:
        filters.append("[game]anull[bed]")
    if a.get("ducking"):
        filters.append("[bed][sc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350:makeup=1[duck]")
    else:
        filters.append("[sc]anullsink;[bed]anull[duck]")
    filters.append(f"[duck][nar]amix=inputs=2:normalize=0:duration=longest,"
                   f"loudnorm=I={a['loudness']}:TP=-1.5:LRA=11,aresample=48000,"
                   f"apad,atrim=0:{total}[aout]")

    graph = work / "filtergraph.txt"
    graph.write_text(";\n".join(filters), encoding="utf-8")
    v = cfg["video"]
    enc = ["-c:v", v["encoder"]]
    if v["encoder"] == "libx264":
        enc += ["-preset", v["preset"], "-crf", str(v["crf"]), "-profile:v", "high", "-level", "4.2"]
    else:  # NVENC
        enc += ["-preset", "p6", "-rc", "vbr", "-cq", "19", "-b:v", "0", "-profile:v", "high"]
    cmd = [ffmpeg, "-y", "-v", "error", "-stats", *inputs,
           *filter_script_args(ffmpeg, graph.name),
           "-map", "[vout]", "-map", "[aout]", *enc,
           "-r", str(v["fps"]), "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-b:a", v["audio_bitrate"], "-ar", "48000",
           "-t", f"{total}", "-movflags", "+faststart", str(out.resolve())]
    (work / "ffmpeg_command.txt").write_text(" ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd),
                                             encoding="utf-8")
    log(f"▶ Rendu FFmpeg : {n} plan(s), {W}x{H} @ {v['fps']} i/s → {out}")
    run(cmd, cwd=work)

    timeline = {"timeline": str(work / "timeline.json"), "project": str(project_file), "output": str(out), "duration": total,
                "narration_wav": str(narration_wav), "subtitles_ass": str(ass), "srt": str(srt),
                "cues": cues, "words": words,
                "segments": [{k: (str(v) if isinstance(v, Path) else v) for k, v in s.items()} for s in segments]}
    (work / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"✔ Vidéo produite : {out}")
    return timeline
