"""Sous-titres dynamiques style TikTok (fichier ASS rendu par libass).

- Le début et la fin de chaque phrase sont exacts (issus de la synthèse).
- À l'intérieur d'une phrase, le minutage des mots est réparti au prorata des
  syllabes (écart typique < 150 ms) ; le mot prononcé est surligné en jaune.
- Un fichier .srt est aussi produit (pour l'importer dans TikTok/YouTube si besoin).
"""
from __future__ import annotations

import random
import re
import zlib
from pathlib import Path

DEFAULT_KEYWORDS = {
    "gta", "argent", "million", "millions", "milliard", "dollars", "police", "flics", "secret", "secrets",
    "caché", "cachée", "glitch", "bug", "rare", "gratuit", "gratuite", "illégal", "braquage", "jamais",
    "personne", "incroyable", "fou", "énorme", "mort", "explosion", "attention", "interdit", "record",
}
VOWELS = "aeiouyàâäéèêëîïôöùûüœæ"


def ass_color(hex_rgb: str, alpha: int = 0) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ass_time(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def esc(text: str) -> str:
    return text.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", " ")


def syllables(word: str) -> int:
    w = word.lower()
    groups = re.findall(f"[{VOWELS}]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("ée", "ie")):
        n -= 1                                   # e muet final
    return max(1, n)


def split_words(text: str) -> list[str]:
    """Découpe en mots en rattachant la ponctuation isolée (« suite ! ») au mot précédent."""
    out = []
    for tok in text.split():
        if out and re.fullmatch(r"[!?:;…»\"]+", tok):
            out[-1] += tok
        else:
            out.append(tok)
    return out


def word_timings(cue: dict) -> list[dict]:
    words = split_words(cue["text"])
    weights = []
    for w in words:
        wt = syllables(w) + 0.35
        if w[-1] in ",;:":
            wt += 0.9                            # petite pause après virgule
        weights.append(wt)
    total = sum(weights)
    span = cue["end"] - cue["start"]
    out, t = [], cue["start"]
    for w, wt in zip(words, weights):
        d = span * wt / total
        out.append({"word": w, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


def chunk_words(words: list[dict], max_words: int, max_chars: int) -> list[list[dict]]:
    chunks, cur = [], []
    for w in words:
        length = sum(len(x["word"]) + 1 for x in cur) + len(w["word"])
        if cur and (len(cur) >= max_words or length > max_chars):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if w["word"][-1] in ".,;:!?…":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(cues: list[dict], cfg: dict, title: str, title_dur: float, total: float,
              out_ass: Path, out_srt: Path) -> list[dict]:
    st, v = cfg["style"], cfg["video"]
    W, H = v["width"], v["height"]
    up = (lambda s: s.upper()) if st.get("uppercase") else (lambda s: s)
    white = ass_color(st["sub_color"])
    yellow = ass_color(st["highlight_color"])
    black = ass_color("000000")
    shadow = ass_color("000000", 0x60)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{st['font']},{st['sub_size']},{white},{yellow},{black},{shadow},-1,0,0,0,100,100,0,0,1,{st['outline']},4,5,60,60,0,1
Style: Emph,{st['font']},{st['sub_size']},{black},{black},{yellow},{shadow},-1,0,0,0,100,100,0,0,3,16,0,5,60,60,0,1
Style: Title,{st['font']},{st['title_size']},{black},{black},{yellow},{shadow},-1,0,0,0,100,100,0,0,3,18,0,8,90,90,{int(H*st['title_y'])},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if title:
        lines.append(f"Dialogue: 1,{ass_time(0.05)},{ass_time(title_dur)},Title,,0,0,0,,"
                     f"{{\\fad(120,250)\\fscx85\\fscy85\\t(0,180,\\fscx100\\fscy100)}}{esc(up(title))}")
    words_all = []
    for si, cue in enumerate(cues):
        words = word_timings(cue)
        words_all += [{**w, "word": clean(w["word"])} for w in words]
        if st.get("dynamic", True):
            lines += dynamic_events(words, si, cue["text"], cfg)
        else:
            x, y = W // 2, int(H * st["sub_y"])
            for chunk in chunk_words(words, st["words_per_chunk"], st["max_chunk_chars"]):
                for i, w in enumerate(chunk):
                    end = chunk[i + 1]["start"] if i + 1 < len(chunk) else chunk[-1]["end"]
                    parts = [f"{{\\c{yellow}}}{esc(up(clean(ww['word'])))}{{\\c{white}}}" if j == i
                             else esc(up(clean(ww["word"]))) for j, ww in enumerate(chunk)]
                    anim = "\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)" if i == 0 else ""
                    lines.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Sub,,0,0,0,,"
                                 f"{{\\pos({x},{y}){anim}}}" + " \\h".join(parts))
    out_ass.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    with open(out_srt, "w", encoding="utf-8") as f:
        for n, cue in enumerate(cues, 1):
            f.write(f"{n}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{clean(cue['text'])}\n\n")
    return words_all


# ------------------------------------------------------------ style dynamique
def clean(word: str) -> str:
    """Retire le balisage *mot* (emphase manuelle)."""
    return word.replace("*", "")


def mark_emphasis(words: list[dict], keywords: set[str]) -> None:
    """Marque les mots à mettre en valeur :
    - balisage manuel *mot* ou *plusieurs mots* dans episode.yaml,
    - nombres (« 3 millions », « 2013 »),
    - mots-clés (config style.keywords),
    - mot qui termine une exclamation."""
    inside = False
    for w in words:
        raw = w["word"]
        starts, ends = raw.startswith("*"), raw.rstrip(".,;:!?…»\"'").endswith("*")
        manual = inside or starts
        if starts and not ends:
            inside = True
        elif ends:
            inside = False
        core = clean(raw).lower().strip(".,;:!?…«»\"'")
        w["manual"] = manual or ("*" in raw)
        w["emph"] = w["manual"] or bool(re.search(r"\d", core)) or core in keywords or raw.endswith("!")
        w["shout"] = raw.endswith("!")


def chunk_dynamic(words: list[dict], max_words: int, max_chars: int) -> list[list[dict]]:
    """Comme chunk_words, mais un groupe de mots mis en valeur forme son propre bloc."""
    chunks, cur = [], []
    for w in words:
        if cur and w["emph"] != cur[-1]["emph"]:
            chunks.append(cur)
            cur = []
        length = sum(len(clean(x["word"])) + 1 for x in cur) + len(clean(w["word"]))
        limit = 2 if w["emph"] else max_words
        if cur and (len(cur) >= limit or length > max_chars):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if w["word"][-1] in ".,;:!?…":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def dynamic_events(words: list[dict], si: int, text: str, cfg: dict) -> list[str]:
    st, v = cfg["style"], cfg["video"]
    W, H = v["width"], v["height"]
    up = (lambda s: s.upper()) if st.get("uppercase") else (lambda s: s)
    palette = [ass_color(c) for c in st.get("palette", ["FFD400", "3CFF6B", "FF4D4D", "4DD2FF"])]
    white = ass_color(st["sub_color"])
    black = ass_color("000000")
    keywords = DEFAULT_KEYWORDS | {k.lower() for k in st.get("keywords", [])}
    positions = st.get("positions", [0.62, 0.54, 0.68])
    base = st["sub_size"]
    rng = random.Random(zlib.crc32(text.encode()))

    # couleur de la phrase : question = bleu, exclamation = rouge, sinon rotation
    if text.rstrip().endswith("?"):
        color = palette[3 % len(palette)]
    elif text.rstrip().endswith("!"):
        color = palette[2 % len(palette)]
    else:
        color = palette[si % len(palette)]
    y_base = positions[si % len(positions)]

    mark_emphasis(words, keywords)
    out = []
    for ci, chunk in enumerate(chunk_dynamic(words, st["words_per_chunk"], st["max_chunk_chars"])):
        chars = sum(len(clean(w["word"])) for w in chunk)
        x = W // 2 + rng.randint(-25, 25)
        if chunk[0]["emph"]:
            # Mot fort : gros, texte noir sur pavé de couleur, incliné, effet "pop"
            box = palette[(si + ci) % len(palette)] if not chunk[0]["shout"] else palette[2 % len(palette)]
            size = int(base * (1.55 if chars <= 7 else 1.3 if chars <= 12 else 1.1))
            rot = rng.choice([-5, -4, -3, 3, 4, 5])
            y = int(H * (y_base - 0.035))
            txt = " ".join(esc(up(clean(w["word"]))) for w in chunk).rstrip(".,;:…")
            anim = f"\\fscx160\\fscy160\\t(0,140,\\fscx100\\fscy100)"
            if chunk[0]["shout"]:
                anim += f"\\t(140,200,\\frz{rot + 6})\\t(200,260,\\frz{rot - 6})\\t(260,320,\\frz{rot})"
            out.append(f"Dialogue: 2,{ass_time(chunk[0]['start'])},{ass_time(chunk[-1]['end'])},Emph,,0,0,0,,"
                       f"{{\\pos({x},{y})\\fs{size}\\frz{rot}\\3c{box}\\1c{black}{anim}}}{txt}")
            continue
        # Bloc normal : taille selon la longueur, mot prononcé coloré et grossi
        size = int(base * (1.22 if chars <= 8 else 1.0 if chars <= 15 else 0.86))
        rot = rng.choice([-2, -1, 0, 0, 1, 2])
        y = int(H * y_base)
        for i, w in enumerate(chunk):
            end = chunk[i + 1]["start"] if i + 1 < len(chunk) else chunk[-1]["end"]
            parts = []
            for j, ww in enumerate(chunk):
                t = esc(up(clean(ww["word"])))
                parts.append(f"{{\\c{color}\\fscx112\\fscy112}}{t}{{\\c{white}\\fscx100\\fscy100}}" if j == i else t)
            anim = "\\fscx70\\fscy70\\t(0,110,\\fscx104\\fscy104)\\t(110,170,\\fscx100\\fscy100)" if i == 0 else ""
            out.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Sub,,0,0,0,,"
                       f"{{\\pos({x},{y})\\fs{size}\\frz{rot}{anim}}}" + " \\h".join(parts))
    return out
