#!/usr/bin/env python3
"""GTA-MEDIA — commande unique du pipeline.

  python gta.py doctor                         diagnostic de l'environnement
  python gta.py test-assets                    génère des captures de test libres
  python gta.py ingest [--move] [--dry-run]    importe les captures Xbox
  python gta.py library                        liste les captures importées
  python gta.py new NOM                        crée un projet à partir des captures
  python gta.py voices --download VOIX         télécharge une voix Piper
  python gta.py voices --elevenlabs            liste vos voix ElevenLabs (voice_id)
  python gta.py say "phrase" [--tts …]         écoute une phrase → output/voix_test.wav
  python gta.py build projects/NOM/episode.yaml [--tts test|piper|azure|elevenlabs]
  python gta.py verify output/NOM.mp4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # accents sous Windows

from gtamedia import compose, doctor, ingest, testassets, tts, verify  # noqa: E402
from gtamedia.utils import ROOT, PipelineError, load_config, p  # noqa: E402

TEMPLATE = """# Projet GTA-MEDIA : {name}
name: {name}
title: "TITRE ACCROCHEUR ICI"      # affiché en haut pendant title_duration secondes
title_duration: 2.8
# tts: piper                       # pour forcer un moteur sur ce projet
music: assets/music/test_beat_libre.wav   # remplacez par une musique libre de droits

clips:                             # plans dans l'ordre ; start/end en secondes
{clips}
narration:                         # une ligne = une phrase = un bloc de sous-titres
  - "Première phrase d'accroche, courte et percutante."
  - "Deuxième phrase qui développe l'idée."
  - "Abonne-toi pour la suite !"
"""


def cmd_new(cfg: dict, name: str) -> None:
    index = ingest.load_index(p(cfg, "library"))
    if not index:
        raise PipelineError("Bibliothèque vide : lancez d'abord 'python gta.py ingest'.")
    lines = []
    for e in sorted(index.values(), key=lambda e: e["captured"])[-4:]:
        end = min(6.0, round(e["duration"] - 0.2, 2))
        lines.append(f"  - file: {e['file']}\n    start: 0\n    end: {end}\n    layout: crop   # crop | blur\n    focus_x: 0.5")
    d = ROOT / "projects" / name
    d.mkdir(parents=True, exist_ok=True)
    f = d / "episode.yaml"
    if f.exists():
        raise PipelineError(f"{f} existe déjà")
    f.write_text(TEMPLATE.format(name=name, clips="\n".join(lines)), encoding="utf-8")
    print(f"✔ Projet créé : {f}\n  Éditez-le, puis : python gta.py build {f.relative_to(ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Pipeline de montage vertical GTA-MEDIA")
    ap.add_argument("--config", type=Path, default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("test-assets")
    s = sub.add_parser("ingest")
    s.add_argument("--move", action="store_true", help="déplace les originaux de inbox/ vers inbox/_importes")
    s.add_argument("--dry-run", action="store_true")
    sub.add_parser("library")
    s = sub.add_parser("new")
    s.add_argument("name")
    s = sub.add_parser("voices")
    s.add_argument("--download", help="télécharge une voix Piper")
    s.add_argument("--elevenlabs", action="store_true", help="liste les voix de votre compte ElevenLabs")
    s = sub.add_parser("say")
    s.add_argument("text")
    s.add_argument("--tts", default=None)
    s = sub.add_parser("build")
    s.add_argument("project", type=Path)
    s.add_argument("--tts", default=None)
    s.add_argument("--out", type=Path, default=None)
    s.add_argument("--no-verify", action="store_true")
    s = sub.add_parser("verify")
    s.add_argument("video", type=Path)
    s.add_argument("--timeline", type=Path, default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)

    try:
        if args.cmd == "doctor":
            return 0 if doctor.doctor(cfg) else 1
        if args.cmd == "test-assets":
            testassets.generate()
        elif args.cmd == "ingest":
            ingest.ingest(cfg, move=args.move, dry_run=args.dry_run)
        elif args.cmd == "library":
            for name, e in sorted(ingest.load_index(p(cfg, "library")).items()):
                o = e["original"]
                print(f"{e['file']:<70} {e['duration']:6.1f}s  orig {o['width']}x{o['height']} "
                      f"{o['codec']} {'HDR' if o['hdr'] else 'SDR'}")
        elif args.cmd == "new":
            cmd_new(cfg, args.name)
        elif args.cmd == "voices":
            if args.elevenlabs:
                tts.eleven_list_voices()
            elif args.download:
                tts.download_voice(cfg, args.download)
            else:
                print("Précisez --download VOIX ou --elevenlabs")
        elif args.cmd == "say":
            out = p(cfg, "output") / "voix_test.wav"
            out.parent.mkdir(parents=True, exist_ok=True)
            tts.preview(args.text, cfg, args.tts, out)
        elif args.cmd == "build":
            tl = compose.build(args.project, cfg, backend=args.tts, out=args.out)
            if not args.no_verify:
                rep = verify.verify(Path(tl["output"]), Path(tl["timeline"]))
                return 0 if rep["ok"] else 2
        elif args.cmd == "verify":
            tl = args.timeline or p(cfg, "work") / args.video.stem / "timeline.json"
            rep = verify.verify(args.video, tl)
            return 0 if rep["ok"] else 2
    except PipelineError as e:
        print(f"\n✗ ERREUR : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
