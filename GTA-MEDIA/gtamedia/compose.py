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
from .utils import ROOT, PipelineError, deep_merge, ffprobe, log, p, require_tool, run


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


def _fit(src: str, out: str, w: int, h: int, focus: float, fps: int) -> str:
    """Remplit exactement w x h (recadrage centré réglable)."""
    return (f"{src}fps={fps},setpts=PTS-STARTPTS,setsar=1,"
            f"scale='if(gt(iw/ih,{w}/{h}),-2,{w})':'if(gt(iw/ih,{w}/{h}),{h},-2)':flags=lanczos,"
            f"crop={w}:{h}:(iw-ow)*{focus}:(ih-oh)/2{out}")


def video_chain(label: int, ins: list[int], seg: dict, cfg: dict) -> str:
    v, fx = cfg["video"], cfg["effects"]
    W, H, fps = v["width"], v["height"], v["fps"]
    d = seg["dur"]
    layout = seg.get("layout", "crop")
    focus = float(seg.get("focus_x", 0.5))
    idx = ins[0]
    base = f"[{idx}:v]fps={fps},setpts=PTS-STARTPTS,setsar=1"
    z = float(seg.get("zoom", fx["zoom"]))
    if layout == "compare":
        # Écran partagé : plan du haut / plan du bas, séparés par un trait noir
        half = H // 2
        ft, fb = float(seg["top"].get("focus_x", 0.5)), float(seg["bottom"].get("focus_x", 0.5))
        chain = (_fit(f"[{ins[0]}:v]", f"[ct{label}]", W, half, ft, fps) + ";" +
                 _fit(f"[{ins[1]}:v]", f"[cb{label}]", W, half, fb, fps) + ";" +
                 f"[ct{label}][cb{label}]vstack=inputs=2,"
                 f"drawbox=x=0:y={half - 5}:w={W}:h=10:color=black:t=fill")
        z = 0.0
    elif layout == "blur":
        fg_w = int(W * float(seg.get("fg_zoom", 1.35)))
        chain = (f"{base},split[a{label}][b{label}];"
                 f"[a{label}]scale={W//4}:{H//4}:force_original_aspect_ratio=increase,crop={W//4}:{H//4},"
                 f"gblur=sigma=12,scale={W}:{H},eq=brightness=-0.12:saturation=1.1[bg{label}];"
                 f"[b{label}]scale={fg_w}:-2,crop='min(iw,{W})':ih:(iw-ow)*{focus}:0[fg{label}];"
                 f"[bg{label}][fg{label}]overlay=(W-w)/2:(H-h)/2")
    else:  # crop plein écran
        chain = f"{base},scale=-2:{H}:flags=lanczos,crop={W}:{H}:(iw-ow)*{focus}:0"
    if z > 0:
        hw, hh = W // 2, H // 2
        chain += (f",scale=w='2*trunc({hw}*(1+{z}*t/{d:.3f}))':h='2*trunc({hh}*(1+{z}*t/{d:.3f}))'"
                  f":eval=frame:flags=bicubic,crop={W}:{H}")
    chain += f",eq=contrast={fx['contrast']}:saturation={fx['saturation']}:brightness={fx['brightness']}"
    if fx.get("sharpen"):
        chain += ",unsharp=5:5:0.5"
    if fx.get("vignette") and layout != "compare":
        chain += ",vignette=angle=PI/5"
    chain += f",format=yuv420p,trim=0:{d:.3f},setpts=PTS-STARTPTS[v{label}]"
    return chain


def audio_chain(label: int, ins: list[int], seg: dict) -> str:
    d = seg["dur"]
    fmt = f"aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,atrim=0:{d:.3f},apad,atrim=0:{d:.3f}"
    srcs = [i for i, has in zip(ins, seg["has_audio"]) if has]
    if not srcs:
        return f"anullsrc=r=48000:cl=stereo,atrim=0:{d:.3f}[ga{label}]"
    if len(srcs) == 1:
        return f"[{srcs[0]}:a]{fmt}[ga{label}]"
    parts = ";".join(f"[{i}:a]{fmt}[gs{label}_{k}]" for k, i in enumerate(srcs))
    mix = "".join(f"[gs{label}_{k}]" for k in range(len(srcs)))
    return f"{parts};{mix}amix=inputs={len(srcs)}:normalize=0,volume=0.8[ga{label}]"


def _sources(seg: dict) -> list[dict]:
    """Liste des sources vidéo d'un plan (1, ou 2 en mode compare)."""
    if seg.get("layout") == "compare":
        top, bot = dict(seg["top"]), dict(seg["bottom"])
        for x in (top, bot):
            x.setdefault("start", seg.get("start", 0))
        return [top, bot]
    return [seg]


def _seg_duration(seg: dict) -> float:
    if "dur" in seg:
        return float(seg["dur"])
    return float(seg["end"]) - float(seg["start"])


def make_overlays(segments: list[dict], xd: float, total: float, proj: dict, cfg: dict) -> list[dict]:
    """Étiquettes à l'écran : comparaison, pastille de fiabilité, filigrane de marque."""
    ov, t = [], 0.0
    for i, s in enumerate(segments):
        start = t
        end = t + s["dur"]
        if s.get("layout") == "compare":
            a0, a1 = start + (0.15 if i else 0.0), end - xd
            if s["top"].get("label"):
                ov.append({"kind": "label_top", "text": s["top"]["label"], "start": a0, "end": a1})
            if s["bottom"].get("label"):
                ov.append({"kind": "label_bottom", "text": s["bottom"]["label"], "start": a0, "end": a1})
            if s.get("caption"):
                ov.append({"kind": "center", "text": s["caption"], "start": a0, "end": a1})
        t = end - xd
    badge = proj.get("badge")
    if badge:
        ov.append({"kind": "badge", "text": badge, "start": 0.0, "end": total})
    handle = (cfg.get("brand") or {}).get("handle")
    if handle:
        ov.append({"kind": "brand", "text": handle, "start": 0.0, "end": total,
                   "compare": any(s.get("layout") == "compare" for s in segments)})
    return ov


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

    cfg = deep_merge(cfg, proj.get("config") or {})          # réglages propres au projet
    fx = cfg["effects"]
    xd = float(fx["transition_duration"])

    # Durée pilotée par les plans (comparaisons) ou par la voix (par défaut)
    clips_total = None
    if proj.get("length") == "clips":
        durs = [_seg_duration(c) for c in proj["clips"]]
        clips_total = round(sum(durs) - xd * (len(durs) - 1), 3)

    # 1) Voix off
    items = proj.get("narration") or []
    texts = [it if isinstance(it, str) else it["text"] for it in items]
    ats = []
    for it in items:
        at = None if isinstance(it, str) else it.get("at")
        if at is not None and float(at) < 0 and clips_total:
            at = clips_total + float(at)                          # "at: -3" = 3 s avant la fin
        ats.append(at)
    narration_wav = work / "narration.wav"
    if texts:
        segs = tts.synthesize(texts, cfg, backend or proj.get("tts"))
        cues = tts.build_narration(segs, cfg, narration_wav, ats)
        voice_end = cues[-1]["end"] + float(cfg["audio"]["tail"])
    else:
        cues, voice_end = [], 0.0
    total = round(max(clips_total or 0.0, voice_end), 3)
    if not texts:
        tts.write_silence(narration_wav, total)
    log(f"   durée finale : {total:.2f}s")

    # 2) Plan de montage
    segments = plan_segments(proj["clips"], total, xd) if clips_total is None else \
        [dict(c, dur=_seg_duration(c)) for c in proj["clips"]]
    if clips_total is not None and total > clips_total:
        segments[-1]["dur"] = round(segments[-1]["dur"] + total - clips_total, 3)   # la voix déborde : on prolonge le dernier plan

    # 3) Sous-titres et habillage
    ass, srt = work / "subs.ass", out.with_suffix(".srt")
    overlays = make_overlays(segments, xd, total, proj, cfg)
    words = subtitles.build_ass(cues, cfg, proj.get("title", ""), float(proj.get("title_duration", 2.8)),
                                total, ass, srt, overlays)

    inputs, filters, nin = [], [], 0
    for i, s in enumerate(segments):
        ins, has = [], []
        for src_def in _sources(s):
            src = resolve(src_def["file"], project_file.parent)
            src_def["path"] = str(src)
            has.append(any(st["codec_type"] == "audio" for st in ffprobe(src)["streams"]))
            inputs += ["-ss", f"{float(src_def.get('start', 0)):.3f}", "-t", f"{s['dur'] + 0.1:.3f}", "-i", src]
            ins.append(nin)
            nin += 1
        if s.get("layout") == "compare":
            pick = {"top": [0], "bottom": [1], "both": [0, 1]}[s.get("audio_from", "bottom")]
            a_ins, a_has = [ins[k] for k in pick], [has[k] for k in pick]
        else:
            a_ins, a_has = ins, has
        s["has_audio"] = a_has
        filters.append(video_chain(i, ins, s, cfg))
        filters.append(audio_chain(i, a_ins, s))
    n = len(segments)
    nar_idx, mus_idx = nin, None
    inputs += ["-i", narration_wav]
    music = proj.get("music")
    if music:
        mus_idx = nin + 1
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
        filters.append("[sc]anullsink")
        filters.append("[bed]anull[duck]")
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
