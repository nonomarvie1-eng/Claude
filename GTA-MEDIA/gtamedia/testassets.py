"""Génère des ressources de test 100 % libres de droits (créées par FFmpeg).

Elles imitent le format des captures Xbox Series X|S :
- 3 clips 1920x1080 60 i/s H.264 + AAC 48 kHz (comme une capture SDR),
- 1 clip 3840x2160 HEVC 10 bits marqué HDR10 (comme une capture 4K HDR),
- 1 boucle musicale synthétique.
Aucune image du jeu n'est utilisée : ce sont des mires animées.
"""
from __future__ import annotations

from .utils import ROOT, log, p, require_tool, run

FONT = "assets/fonts/InterDisplay-Bold.otf"


def _label(text: str) -> str:
    return (f"drawtext=fontfile={FONT}:text='{text}':fontsize=64:fontcolor=white:"
            f"box=1:boxcolor=black@0.55:boxborderw=18:x=60:y=60,"
            f"drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':fontsize=52:fontcolor=yellow:"
            f"box=1:boxcolor=black@0.55:boxborderw=14:x=60:y=h-130")


CLIPS = [
    ("Grand Theft Auto V-2026_11_20-21_14_33.mp4",
     "testsrc2=s=1920x1080:r=60", "CAPTURE TEST 1 - mire FFmpeg", 12),
    ("Grand Theft Auto V-2026_11_20-21_18_02.mp4",
     "life=s=480x270:r=60:mold=10:ratio=0.1:death_color=#202040:life_color=#00e070,"
     "scale=1920:1080:flags=neighbor", "CAPTURE TEST 2 - jeu de la vie", 12),
    ("Grand Theft Auto V-2026_11_20-21_25_47.mp4",
     "gradients=s=1920x1080:r=60:speed=0.03:c0=#ff3c00:c1=#2a0a5e:c2=#ffd400:n=3", "CAPTURE TEST 3 - degrade", 12),
]


def generate() -> None:
    ffmpeg = require_tool("ffmpeg")
    cfg_inbox = ROOT / "inbox"
    cfg_inbox.mkdir(exist_ok=True)
    log("▶ Génération des captures de test (format Xbox)")
    for i, (name, src, label, d) in enumerate(CLIPS):
        out = cfg_inbox / name
        if out.exists():
            log(f"   = existe : {name}")
            continue
        run([ffmpeg, "-y", "-v", "error",
             "-f", "lavfi", "-i", f"{src},{_label(label)}",
             "-f", "lavfi", "-i", f"anoisesrc=c=brown:a=0.25:seed={i+1},lowpass=f=500,"
                                 f"volume='0.6+0.4*sin(2*PI*0.3*t)':eval=frame",
             "-t", str(d), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", out], cwd=ROOT)
        log(f"   + inbox/{name}")

    hdr = cfg_inbox / "Grand Theft Auto V-2026_11_20-22_02_10 (HDR 4K).mp4"
    if not hdr.exists():
        run([ffmpeg, "-y", "-v", "error",
             "-f", "lavfi", "-i", f"mandelbrot=s=1280x720:r=30,scale=3840:2160,{_label('CAPTURE TEST 4 - 4K HDR')}",
             "-f", "lavfi", "-i", "sine=f=220:sample_rate=48000",
             "-t", "5", "-c:v", "libx265", "-preset", "ultrafast", "-pix_fmt", "yuv420p10le",
             "-x265-params", "log-level=error:hdr10=1:colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc",
             "-color_primaries", "bt2020", "-color_trc", "smpte2084", "-colorspace", "bt2020nc",
             "-tag:v", "hvc1", "-c:a", "aac", "-ac", "2", "-shortest", hdr], cwd=ROOT)
        log(f"   + inbox/{hdr.name}")

    music = ROOT / "assets" / "music" / "test_beat_libre.wav"
    music.parent.mkdir(parents=True, exist_ok=True)
    if not music.exists():
        root = "(110*eq(floor(mod(t,8)/2),0)+87.31*eq(floor(mod(t,8)/2),1)+130.81*eq(floor(mod(t,8)/2),2)+98*eq(floor(mod(t,8)/2),3))"
        kick = "0.9*sin(2*PI*55*mod(t,0.5))*exp(-14*mod(t,0.5))"
        bass = f"0.35*sin(2*PI*{root}*t)*(0.6+0.4*exp(-6*mod(t,0.25)))"
        hat = "0.12*(random(0)*2-1)*exp(-60*mod(t+0.25,0.5))"
        pad = f"0.10*sin(2*PI*{root}*2.997*t)+0.08*sin(2*PI*{root}*4.01*t)"
        expr = f"{kick}+{bass}+{hat}+{pad}"
        run([ffmpeg, "-y", "-v", "error", "-f", "lavfi",
             "-i", f"aevalsrc='{expr}|{expr}':s=48000:d=16",
             "-af", "alimiter=limit=0.8", music], cwd=ROOT)
        log("   + assets/music/test_beat_libre.wav")
    log("✔ Ressources de test prêtes (générées localement, aucun droit tiers).")
