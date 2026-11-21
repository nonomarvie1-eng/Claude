"""Sous-titres dynamiques style TikTok (fichier ASS rendu par libass).

- Le début et la fin de chaque phrase sont exacts (issus de la synthèse).
- À l'intérieur d'une phrase, le minutage des mots est réparti au prorata des
  syllabes (écart typique < 150 ms) ; le mot prononcé est surligné en jaune.
- Un fichier .srt est aussi produit (pour l'importer dans TikTok/YouTube si besoin).
"""
from __future__ import annotations

import re
from pathlib import Path

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


def word_timings(cue: dict) -> list[dict]:
    words = cue["text"].split()
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
Style: Title,{st['font']},{st['title_size']},{black},{black},{yellow},{shadow},-1,0,0,0,100,100,0,0,3,18,0,8,90,90,{int(H*st['title_y'])},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if title:
        lines.append(f"Dialogue: 1,{ass_time(0.05)},{ass_time(title_dur)},Title,,0,0,0,,"
                     f"{{\\fad(120,250)\\fscx85\\fscy85\\t(0,180,\\fscx100\\fscy100)}}{esc(up(title))}")
    x, y = W // 2, int(H * st["sub_y"])
    words_all = []
    for cue in cues:
        words = word_timings(cue)
        words_all += words
        for chunk in chunk_words(words, st["words_per_chunk"], st["max_chunk_chars"]):
            for i, w in enumerate(chunk):
                end = chunk[i + 1]["start"] if i + 1 < len(chunk) else chunk[-1]["end"]
                parts = []
                for j, ww in enumerate(chunk):
                    txt = esc(up(ww["word"]))
                    parts.append(f"{{\\c{yellow}}}{txt}{{\\c{white}}}" if j == i else txt)
                anim = "\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)" if i == 0 else ""
                lines.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Sub,,0,0,0,,"
                             f"{{\\pos({x},{y}){anim}}}" + " \\h".join(parts))
    out_ass.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")

    with open(out_srt, "w", encoding="utf-8") as f:
        for n, cue in enumerate(cues, 1):
            f.write(f"{n}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}\n\n")
    return words_all
