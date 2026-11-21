"""Import des captures Xbox : détection, normalisation, indexation.

Les captures Xbox Series X|S sont des MP4 en 1080p ou 4K à 30/60 i/s :
- H.264 en SDR,
- HEVC 10 bits en HDR10 (smpte2084) quand le HDR est actif.
Pour que le montage soit fiable, chaque capture est convertie une seule fois en
"mezzanine" : H.264 1080p SDR, cadence constante, audio AAC 48 kHz.
L'original n'est jamais modifié (copie par défaut).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path

from .utils import PipelineError, ffmpeg_has, ffprobe, log, p, parse_rate, require_tool, run

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v"}
HDR_TRANSFERS = {"smpte2084", "arib-std-b67"}
DATE_PATTERNS = [
    # 2026_11_20-21_14_33 / 2026-11-20 21-14-33 / 20261120_211433
    re.compile(r"(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})[-_ T.]+(\d{2})[-_.:]?(\d{2})[-_.:]?(\d{2})"),
    # 11_20_2026 21_14_33 (format US)
    re.compile(r"(\d{2})[-_.](\d{2})[-_.](20\d{2})[-_ T.]+(\d{2})[-_.:](\d{2})[-_.:](\d{2})"),
]


def fingerprint(path: Path) -> str:
    """Empreinte rapide : taille + premiers/derniers 4 Mo."""
    h = hashlib.sha1()
    size = path.stat().st_size
    h.update(str(size).encode())
    with open(path, "rb") as f:
        h.update(f.read(4 << 20))
        if size > 8 << 20:
            f.seek(-(4 << 20), 2)
            h.update(f.read())
    return h.hexdigest()[:16]


def capture_date(path: Path, info: dict) -> dt.datetime:
    name = path.stem
    m = DATE_PATTERNS[0].search(name)
    if m:
        y, mo, d, hh, mm, ss = map(int, m.groups())
        try:
            return dt.datetime(y, mo, d, hh, mm, ss)
        except ValueError:
            pass
    m = DATE_PATTERNS[1].search(name)
    if m:
        mo, d, y, hh, mm, ss = map(int, m.groups())
        try:
            return dt.datetime(y, mo, d, hh, mm, ss)
        except ValueError:
            pass
    tag = info.get("format", {}).get("tags", {}).get("creation_time")
    if tag:
        try:
            return dt.datetime.fromisoformat(tag.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            pass
    return dt.datetime.fromtimestamp(path.stat().st_mtime)


def slug(text: str) -> str:
    for pat in DATE_PATTERNS:
        text = pat.sub("", text)
    text = re.sub(r"(?i)grand[ _-]*theft[ _-]*auto[ _-]*v", "gtav", text)
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:40] or "capture"


def describe(info: dict) -> dict:
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        raise PipelineError("aucune piste vidéo")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    return {
        "codec": v.get("codec_name"),
        "width": int(v["width"]),
        "height": int(v["height"]),
        "fps": round(parse_rate(v.get("avg_frame_rate") or v.get("r_frame_rate", "0/1")), 3),
        "pix_fmt": v.get("pix_fmt"),
        "transfer": v.get("color_transfer", "unknown"),
        "hdr": v.get("color_transfer") in HDR_TRANSFERS,
        "duration": float(info["format"].get("duration", 0)),
        "has_audio": a is not None,
    }


def build_filters(meta: dict, cfg: dict, can_tonemap: bool) -> str:
    max_h = cfg["ingest"]["max_height"]
    vf = []
    if meta["hdr"]:
        if can_tonemap:
            vf.append("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
                      "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv")
        else:
            log("   ⚠ capture HDR mais FFmpeg sans 'zscale' : couleurs ternes possibles. "
                "Utilisez la build 'full' de gyan.dev.")
    if meta["height"] > max_h:
        vf.append(f"scale=-2:{max_h}:flags=lanczos")
    vf.append("format=yuv420p")
    return ",".join(vf)


def load_index(lib: Path) -> dict:
    idx = lib / "index.json"
    if idx.exists():
        return json.loads(idx.read_text(encoding="utf-8"))
    return {}


def save_index(lib: Path, index: dict) -> None:
    (lib / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def scan_sources(cfg: dict) -> list[Path]:
    dirs = [p(cfg, "inbox")] + [Path(d) for d in cfg["paths"].get("xbox_sources") or []]
    files = []
    for d in dirs:
        if not d.exists():
            log(f"   (dossier absent, ignoré : {d})")
            continue
        files += [f for f in sorted(d.rglob("*")) if f.suffix.lower() in VIDEO_EXT and f.is_file()]
    return files


def ingest(cfg: dict, move: bool = False, dry_run: bool = False) -> list[dict]:
    ffmpeg = require_tool("ffmpeg")
    lib = p(cfg, "library")
    lib.mkdir(parents=True, exist_ok=True)
    index = load_index(lib)
    known = {e["fingerprint"] for e in index.values()}
    can_tonemap = ffmpeg_has("filters", "zscale")
    max_fps = cfg["ingest"]["max_fps"]
    added = []

    files = scan_sources(cfg)
    log(f"▶ Import : {len(files)} fichier(s) vidéo trouvé(s)")
    for src in files:
        fp = fingerprint(src)
        if fp in known:
            log(f"   = déjà importé : {src.name}")
            continue
        try:
            info = ffprobe(src)
            meta = describe(info)
        except PipelineError as e:
            log(f"   ✗ illisible, ignoré : {src.name} ({e})")
            continue
        date = capture_date(src, info)
        name = f"{date:%Y%m%d_%H%M%S}_{slug(src.stem)}_{fp[:6]}.mp4"
        dst = lib / name
        fps = min(round(meta["fps"]) or 60, max_fps)
        log(f"   + {src.name}\n     {meta['width']}x{meta['height']} {meta['codec']} "
            f"{meta['fps']} i/s {'HDR' if meta['hdr'] else 'SDR'} {meta['duration']:.1f}s → {name}")
        if dry_run:
            continue
        cmd = [ffmpeg, "-y", "-v", "error", "-i", src,
               "-vf", build_filters(meta, cfg, can_tonemap),
               "-r", str(fps), "-fps_mode", "cfr",
               "-c:v", "libx264", "-preset", "fast", "-crf", str(cfg["ingest"]["crf"]),
               "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
        if meta["has_audio"]:
            cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
        cmd += ["-movflags", "+faststart", dst]
        tmp = dst.with_suffix(".part.mp4")
        cmd[-1] = tmp
        run(cmd)
        tmp.replace(dst)
        out_meta = describe(ffprobe(dst))
        entry = {
            "file": f"library/{name}",
            "source": str(src),
            "fingerprint": fp,
            "captured": date.isoformat(),
            "imported": dt.datetime.now().isoformat(timespec="seconds"),
            "original": meta,
            "duration": out_meta["duration"],
            "has_audio": out_meta["has_audio"],
        }
        index[name] = entry
        known.add(fp)
        added.append(entry)
        if move and src.parent == p(cfg, "inbox"):
            done = p(cfg, "inbox") / "_importes"
            done.mkdir(exist_ok=True)
            shutil.move(str(src), done / src.name)
    if not dry_run:
        save_index(lib, index)
    log(f"✔ Import terminé : {len(added)} nouvelle(s) capture(s), {len(index)} au total dans library/")
    return added
