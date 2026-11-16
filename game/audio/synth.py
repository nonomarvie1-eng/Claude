"""GOLDEN RALLY — procedural sound design (tennis club).

Every sound of the game is synthesised from scratch here with numpy
(additive/FM synthesis, filtered noise, a small Schroeder reverb).  No sample
library, no third-party recording, no AI audio service: the studio owns 100%
of the output.

Run:  ../math/.venv/bin/python audio/synth.py
Output: public/assets/audio/*.mp3 (one-shots) and *.wav (seamless loops)
"""

from __future__ import annotations

import os
import sys
import subprocess
import wave

import numpy as np
from scipy.signal import lfilter

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "src", "assets", "audio")
rng = np.random.default_rng(1915)


def t_axis(d: float) -> np.ndarray:
    return np.arange(int(d * SR)) / SR


def env_exp(d: float, tau: float, attack: float = 0.003) -> np.ndarray:
    t = t_axis(d)
    e = np.exp(-t / tau)
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def note(n: str) -> float:
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
             "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    p, o = n[:-1], int(n[-1])
    midi = 12 * (o + 1) + names[p]
    return 440.0 * 2 ** ((midi - 69) / 12)


def bell(f: float, d: float = 2.5, bright: float = 1.0) -> np.ndarray:
    t = t_axis(d)
    partials = [(1.0, 1.0, 1.0), (2.0, 0.6, 0.7), (2.76, 0.45 * bright, 0.45), (5.4, 0.25 * bright, 0.25),
                (8.93, 0.12 * bright, 0.15), (0.5, 0.25, 1.4)]
    s = np.zeros_like(t)
    for ratio, amp, dec in partials:
        s += amp * np.sin(2 * np.pi * f * ratio * t + rng.random() * 6) * np.exp(-t / (d * 0.35 * dec))
    s *= np.minimum(1, t / 0.002)
    return s / 2.2


def musicbox(f: float, d: float = 1.6) -> np.ndarray:
    t = t_axis(d)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.55)
         + 0.35 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.18)
         + 0.15 * np.sin(2 * np.pi * f * 5.98 * t) * np.exp(-t / 0.07))
    s *= np.minimum(1, t / 0.001)
    return s * 0.6


def noise(d: float) -> np.ndarray:
    return rng.standard_normal(int(d * SR))


def bandpass(x: np.ndarray, f: float, q: float = 5.0) -> np.ndarray:
    w0 = 2 * np.pi * f / SR
    alpha = np.sin(w0) / (2 * q)
    b = [alpha, 0, -alpha]
    a = [1 + alpha, -2 * np.cos(w0), 1 - alpha]
    return lfilter(b, a, x)


def lowpass(x: np.ndarray, f: float) -> np.ndarray:
    k = np.exp(-2 * np.pi * f / SR)
    return lfilter([1 - k], [1, -k], x)


def highpass(x: np.ndarray, f: float) -> np.ndarray:
    return x - lowpass(x, f)


def click(f: float = 3200, d: float = 0.05, amp: float = 1.0) -> np.ndarray:
    n = noise(d) * env_exp(d, 0.006, 0.0005)
    ping = np.sin(2 * np.pi * f * t_axis(d)) * env_exp(d, 0.012, 0.0005)
    return amp * (0.6 * bandpass(n, f, 3) + 0.4 * ping)


def thunk(d: float = 0.35) -> np.ndarray:
    t = t_axis(d)
    f = 110 * np.exp(-t / 0.05) + 55
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env_exp(d, 0.09, 0.001)
    return 0.8 * body + 0.35 * click(1800, d, 1.0) + 0.2 * click(4200, d, 0.8)


def _comb(x: np.ndarray, d: int, g: float) -> np.ndarray:
    """y[n] = x[n] + g*y[n-d], processed in blocks of d samples (fast)."""
    y = x.copy()
    for i in range(d, len(y), d):
        j = min(i + d, len(y))
        y[i:j] += g * y[i - d:j - d]
    return y


def _allpass(x: np.ndarray, d: int, g: float) -> np.ndarray:
    """y[n] = -g*x[n] + x[n-d] + g*y[n-d]."""
    y = -g * x
    y[d:] += x[:-d]
    for i in range(d, len(y), d):
        j = min(i + d, len(y))
        y[i:j] += g * y[i - d:j - d]
    return y


def reverb(x: np.ndarray, mix: float = 0.25, size: float = 1.0) -> np.ndarray:
    combs = [1557, 1617, 1491, 1422, 1277, 1356]
    n = len(x) + int(SR * 2.5 * size)
    xp = np.concatenate([x, np.zeros(n - len(x))])
    src = lowpass(xp, 6000)
    out = np.zeros(n)
    for c in combs:
        out += _comb(src, int(c * size * 1.6), 0.84) / len(combs)
    for ap in (225, 556, 441):
        out = _allpass(out, ap, 0.5)
    return (1 - mix) * xp + mix * out * 0.35


def place(buf: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = max(0, int(at * SR))
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += gain * sig[: j - i]


def norm(x: np.ndarray, peak: float = 0.89) -> np.ndarray:
    m = np.abs(x).max() or 1
    return x * (peak / m)


def fade(x: np.ndarray, fin: float = 0.002, fout: float = 0.03) -> np.ndarray:
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def write_wav(path: str, x: np.ndarray) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def export(name: str, x: np.ndarray, loop: bool = False) -> None:
    os.makedirs(OUT, exist_ok=True)
    if loop:
        # loops stay WAV (22.05 kHz) so they loop sample-accurately in every browser
        y = x[::2]
        pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
        with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR // 2)
            w.writeframes(pcm.tobytes())
        return
    tmp = os.path.join(OUT, name + ".tmp.wav")
    write_wav(tmp, x)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "112k", os.path.join(OUT, name + ".mp3")], check=True)
    os.remove(tmp)


def pock(f0: float = 900.0, d: float = 0.18, amp: float = 1.0) -> np.ndarray:
    """Tennis ball on strings: short hollow tone with a fast pitch drop + felt noise."""
    t = t_axis(d)
    f = f0 * (1 + 0.6 * np.exp(-t / 0.004))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) * np.exp(-t / 0.028) + 0.4 * np.sin(2.7 * ph) * np.exp(-t / 0.012)
    felt = bandpass(noise(d), 2400, 1.2) * np.exp(-t / 0.006)
    return amp * (0.8 * tone + 0.5 * felt) * np.minimum(1, t / 0.0005)


def bounce(d: float = 0.16, amp: float = 1.0) -> np.ndarray:
    """Ball bouncing on the court: lower, duller pock."""
    t = t_axis(d)
    body = np.sin(2 * np.pi * 180 * t * (1 + 0.5 * np.exp(-t / 0.01))) * np.exp(-t / 0.03)
    return amp * (0.7 * body + 0.3 * lowpass(noise(d), 1500) * np.exp(-t / 0.01))


def swoosh(d: float = 0.35, amp: float = 1.0) -> np.ndarray:
    t = t_axis(d)
    n = noise(d)
    fc = 600 + 3000 * np.sin(np.pi * t / d) ** 2
    out = np.zeros_like(n)
    blk = 512
    for i in range(0, len(n), blk):
        out[i:i + blk] = bandpass(n[max(0, i - 2048):i + blk], float(fc[i]), 1.5)[-len(n[i:i + blk]):]
    return amp * out * np.sin(np.pi * t / d) ** 2


def applause(d: float = 3.0, density: float = 220.0, amp: float = 1.0) -> np.ndarray:
    """Polite club applause: many short band-limited claps with a swell envelope."""
    buf = np.zeros(int(d * SR))
    n = int(density * d)
    times = np.sort(rng.random(n)) * (d - 0.05)
    for tt in times:
        c = bandpass(noise(0.03), 1200 + rng.random() * 1800, 1.4) * env_exp(0.03, 0.006, 0.0005)
        place(buf, c, tt, 0.3 + 0.7 * rng.random())
    t = t_axis(d)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / (d * 0.55))
    return amp * buf * env


# ------------------------------------------------------------------ one-shots

def sfx_button() -> np.ndarray:
    return norm(fade(pock(1400, 0.08, 1.0)), 0.55)

def sfx_reel_stop() -> np.ndarray:
    return norm(fade(reverb(bounce(0.25) + 0.25 * pock(700, 0.25), 0.12, 0.5)[: int(0.6 * SR)]), 0.8)

def sfx_spin_start() -> np.ndarray:
    d = 0.8
    buf = np.zeros(int(d * SR))
    place(buf, swoosh(0.28), 0.0, 0.5)
    place(buf, pock(950, 0.2), 0.22)
    return norm(fade(reverb(buf, 0.2, 0.6)[: int(1.1 * SR)]), 0.7)

def sfx_spin_loop() -> np.ndarray:
    """1.0 s seamless loop: a soft baseline rally (two players, alternating pocks)."""
    d = 1.0
    buf = np.zeros(int(d * SR))
    place(buf, pock(880, 0.15, 0.7), 0.0)
    place(buf, bounce(0.12, 0.35), 0.24)
    place(buf, pock(760, 0.15, 0.6), 0.5)
    place(buf, bounce(0.12, 0.35), 0.74)
    buf += 0.03 * bandpass(noise(d), 500, 0.7)
    return norm(buf, 0.42)

def sfx_scatter_land(step: int = 0) -> np.ndarray:
    base = [note("D5"), note("F5"), note("A5")][step]
    s = bell(base, 2.5)
    place(s, bell(base * 2, 1.5, 0.6), 0, 0.5)
    return norm(fade(reverb(s, 0.35)[: int(3 * SR)], 0.002, 0.3), 0.75)


def sfx_wild_land() -> np.ndarray:
    d = 1.4
    buf = np.zeros(int(d * SR))
    for i, n in enumerate(["A5", "E6", "A6"]):
        place(buf, musicbox(note(n), 1.2), i * 0.06, 0.8)
    place(buf, click(5000, 0.05), 0)
    return norm(fade(reverb(buf, 0.3)[: int(2 * SR)], 0.002, 0.3), 0.7)


def sfx_win(level: int) -> np.ndarray:
    """level 0 small .. 3 big: chime arpeggios in D major (+ applause for big wins)."""
    scales = [["D5", "F#5", "A5"], ["D5", "F#5", "A5", "D6"], ["A4", "D5", "F#5", "A5", "D6", "F#6"],
              ["D4", "A4", "D5", "F#5", "A5", "D6", "F#6", "A6", "D7"]]
    notes = scales[level]
    step = [0.09, 0.08, 0.075, 0.07][level]
    d = len(notes) * step + (3.5 if level >= 2 else 2.5)
    buf = np.zeros(int(d * SR))
    for i, n in enumerate(notes):
        place(buf, bell(note(n), 2.2, 0.8), i * step, 0.7)
        place(buf, musicbox(note(n) * 2, 1.0), i * step + 0.01, 0.25)
    if level >= 2:
        place(buf, applause(3.0 if level == 3 else 2.2, 260 if level == 3 else 180), 0.15, 0.55 if level == 3 else 0.4)
    return norm(fade(reverb(buf, 0.3)[: int((d + 0.5) * SR)], 0.002, 0.5), 0.8)

def sfx_line_tick() -> np.ndarray:
    return norm(fade(reverb(pock(1100, 0.4, 0.8) + 0.3 * musicbox(note("A6"), 0.4), 0.2)[: int(0.6 * SR)]), 0.45)

def sfx_bonus_trigger() -> np.ndarray:
    d = 4.5
    buf = np.zeros(int(d * SR))
    seq = ["D4", "A4", "D5", "E5", "F#5", "A5", "D6", "E6", "F#6", "A6"]
    for i, n in enumerate(seq):
        place(buf, musicbox(note(n), 1.4), i * 0.08, 0.9)
    for n in ["D3", "A3", "D4", "F#4"]:
        place(buf, bell(note(n), 3.5, 0.5), 0.85, 0.5)
    place(buf, applause(3.6, 300), 0.6, 0.6)
    return norm(fade(reverb(buf, 0.35, 1.1)[: int(5.2 * SR)], 0.002, 0.8), 0.85)

def sfx_wind() -> np.ndarray:
    """Rally up: racket swoosh, crisp volley, bright chime."""
    d = 1.3
    buf = np.zeros(int(d * SR))
    place(buf, swoosh(0.3), 0.0, 0.7)
    place(buf, pock(1050, 0.2, 1.0), 0.24)
    place(buf, bell(note("A6"), 1.0, 1.2), 0.3, 0.5)
    return norm(fade(reverb(buf, 0.25)[: int(1.8 * SR)], 0.002, 0.3), 0.75)

def sfx_mult_up() -> np.ndarray:
    d = 1.6
    buf = np.zeros(int(d * SR))
    for i, n in enumerate(["D6", "A6", "D7"]):
        place(buf, bell(note(n), 1.4, 1.2), i * 0.05, 0.6)
    return norm(fade(reverb(buf, 0.35)[: int(2.2 * SR)], 0.002, 0.4), 0.7)


def sfx_count_tick() -> np.ndarray:
    return norm(fade(pock(1600, 0.05, 1.0)), 0.3)

def sfx_bonus_end() -> np.ndarray:
    d = 4.0
    buf = np.zeros(int(d * SR))
    for i, n in enumerate(["A5", "F#5", "D5", "A4", "D5"]):
        place(buf, bell(note(n), 2.5, 0.7), i * 0.22, 0.7)
    place(buf, applause(3.4, 240), 0.3, 0.5)
    return norm(fade(reverb(buf, 0.35, 1.1)[: int(4.8 * SR)], 0.002, 0.8), 0.8)

def sfx_match_point() -> np.ndarray:
    """Match point tension: rising drum roll + crowd 'ooh' swell + bell sting."""
    d = 2.6
    buf = np.zeros(int(d * SR))
    t = 0.0
    gap = 0.11
    while t < 1.9:
        place(buf, bounce(0.12, 0.5 + 0.5 * t / 1.9), t)
        t += gap
        gap = max(gap * 0.93, 0.035)
    tt = t_axis(d)
    ooh = sum(np.sin(2 * np.pi * f0 * tt + rng.random() * 6) for f0 in (196, 247, 294, 330))
    ooh = lowpass(ooh + 0.4 * bandpass(noise(d), 600, 0.8), 1200) * np.minimum(1, tt / 1.6) * np.minimum(1, (d - tt) / 0.5)
    buf += 0.12 * ooh
    place(buf, bell(note("A5"), 1.2, 1.0), 1.95, 0.5)
    return norm(fade(reverb(buf, 0.3)[: int(3.2 * SR)], 0.002, 0.4), 0.8)


def sfx_serve() -> np.ndarray:
    """Serve: ball toss, racket swoosh, firm string contact."""
    d = 0.9
    buf = np.zeros(int(d * SR))
    place(buf, bounce(0.1, 0.25), 0.0)
    place(buf, swoosh(0.26, 0.8), 0.12)
    place(buf, pock(820, 0.22, 1.0), 0.34)
    place(buf, highpass(pock(1900, 0.06, 0.5), 1200), 0.34)
    return norm(fade(reverb(buf, 0.18, 0.7)[: int(1.2 * SR)]), 0.75)

def sfx_bounce() -> np.ndarray:
    return norm(fade(reverb(bounce(0.2), 0.12, 0.5)[: int(0.5 * SR)]), 0.6)

def sfx_racket() -> np.ndarray:
    """Racket contact: hollow pock with a short string 'ping'."""
    d = 0.5
    t = t_axis(d)
    ping = np.sin(2 * np.pi * 2350 * t) * np.exp(-t / 0.05) * 0.25
    buf = np.zeros(int(d * SR))
    place(buf, pock(980, 0.2, 1.0), 0.0)
    buf += ping
    return norm(fade(reverb(buf, 0.15, 0.5)[: int(0.7 * SR)]), 0.6)

def sfx_pop() -> np.ndarray:
    """Ace appears: two quick playful bounces and a soft rising chirp."""
    d = 0.6
    buf = np.zeros(int(d * SR))
    place(buf, bounce(0.12, 0.6), 0.0)
    place(buf, bounce(0.12, 0.45), 0.13)
    t = t_axis(0.18)
    chirp = np.sin(2 * np.pi * np.cumsum(700 + 900 * t / 0.18) / SR) * np.sin(np.pi * t / 0.18) * 0.35
    place(buf, chirp, 0.24)
    return norm(fade(reverb(buf, 0.15, 0.5)[: int(0.8 * SR)]), 0.5)

def sfx_tiebreak() -> np.ndarray:
    """Transition into the Tie-Break: deep hit, crowd hush, rising bells."""
    d = 2.8
    buf = np.zeros(int(d * SR))
    place(buf, thunk(0.6), 0.0, 1.0)
    for i, n in enumerate(["D4", "F#4", "A4", "D5", "F#5", "A5"]):
        place(buf, bell(note(n), 1.6, 0.8), 0.25 + i * 0.12, 0.5)
    place(buf, applause(2.0, 160), 0.5, 0.35)
    return norm(fade(reverb(buf, 0.35, 1.1)[: int(3.4 * SR)], 0.002, 0.6), 0.8)

def amb_stadium() -> np.ndarray:
    """6 s seamless night-stadium bed: distant crowd murmur + rare far-off pocks."""
    d = 6.0
    tt = t_axis(d)
    murmur = lowpass(bandpass(noise(d), 500, 0.6), 900)
    murmur *= 0.7 + 0.3 * np.sin(2 * np.pi * tt / d) ** 2
    buf = 0.5 * murmur
    for at in (1.1, 1.62, 3.9, 4.45):
        place(buf, pock(880, 0.12, 0.12), at)
    n = int(0.25 * SR)  # crossfade the ends so the loop is seamless
    head = buf[:n].copy()
    buf[-n:] = buf[-n:] * np.linspace(1, 0, n) + head * np.linspace(0, 1, n)
    return norm(buf[: len(buf) - n], 0.35)


def saw(f: float, d: float) -> np.ndarray:
    t = t_axis(d)
    ph = (f * t) % 1.0
    return 2 * ph - 1


def pad_chord(freqs: list[float], d: float) -> np.ndarray:
    s = np.zeros(int(d * SR))
    for f in freqs:
        for det in (-0.12, 0.0, 0.13):
            s += saw(f * 2 ** (det / 12), d)
    s = lowpass(lowpass(s, 900), 1400)
    t = t_axis(d)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.2)
    return s * env / (len(freqs) * 3)


def compose(bpm: float, chords: list[list[str]], arps: list[list[str]], bright: float, name: str) -> np.ndarray:
    beat = 60 / bpm
    bar = 4 * beat
    total = bar * len(chords)
    L = int(total * SR)
    tail = int(3 * SR)
    buf = np.zeros(L + tail)
    for i, ch in enumerate(chords):
        start = i * bar
        pad = pad_chord([note(n) for n in ch], bar + 1.4)
        place(buf, pad, start - 0.4 if i else 0, 0.55)
        # bass
        bass_f = note(ch[0]) / 2
        tb = t_axis(bar)
        bass = np.sin(2 * np.pi * bass_f * tb) * np.exp(-tb / 1.6) * np.minimum(1, tb / 0.02)
        place(buf, bass, start, 0.45)
        # music box arpeggio (8th notes)
        arp = arps[i]
        for k in range(8):
            n = arp[k % len(arp)]
            vel = 0.55 if k % 2 == 0 else 0.38
            place(buf, musicbox(note(n), 1.3), start + k * beat / 2 + rng.normal(0, 0.004), vel * bright)
        # soft rally pulse: ball pock on 1 & 3, brushed shaker on off-beats
        for k in range(4):
            if k % 2 == 0:
                place(buf, pock(820 if k == 0 else 760, 0.12, 0.18), start + k * beat)
            place(buf, highpass(noise(0.06), 5000) * env_exp(0.06, 0.02, 0.005), start + k * beat + beat / 2, 0.05)
    wet = reverb(buf, 0.32, 1.2)
    out = wet[:L].copy()
    out[: len(wet) - L] += wet[L:]  # wrap the tail onto the start: seamless loop
    return norm(out, 0.7)


def music_base() -> np.ndarray:
    # D major, relaxed "garden party" feel
    chords = [["D3", "A3", "C#4", "F#4"], ["B2", "F#3", "A3", "D4"], ["G2", "D3", "F#3", "B3"], ["A2", "E3", "G3", "C#4"],
              ["D3", "A3", "C#4", "F#4"], ["B2", "F#3", "A3", "D4"], ["E3", "B3", "D4", "G4"], ["A2", "E3", "G3", "C#4"]]
    arps = [["F#5", "A5", "D6", "A5", "C#6", "A5"], ["D5", "F#5", "B5", "F#5"], ["G5", "B5", "D6", "B5", "F#5", "D5"], ["E5", "A5", "C#6", "G5"],
            ["A5", "D6", "F#6", "E6", "D6", "A5"], ["B5", "F#5", "D6", "F#5"], ["G5", "B5", "E6", "D6", "B5", "G5"], ["E5", "C#5", "A4", "E5"]]
    return compose(84, chords, arps, 1.0, "base")


def music_free() -> np.ndarray:
    chords = [["F3", "C4", "E4", "A4"], ["G3", "D4", "F#4", "B4"], ["D3", "A3", "C4", "F4"], ["Bb2", "F3", "A3", "D4"],
              ["F3", "C4", "E4", "A4"], ["G3", "D4", "F#4", "B4"], ["A2", "E3", "G3", "C#4"], ["A2", "E3", "G3", "C#4"]]
    arps = [["F5", "C6", "A5", "E6"], ["G5", "D6", "B5", "F#6"], ["D5", "A5", "F5", "C6"], ["Bb5", "F5", "D6", "A5"],
            ["A5", "E6", "C6", "F6"], ["B5", "F#6", "D6", "G6"], ["A5", "E6", "C#6", "G6"], ["E6", "C#6", "A5", "E5"]]
    return compose(96, chords, arps, 1.15, "free")


NEW_SFX = {"serve": sfx_serve, "bounce": sfx_bounce, "racket": sfx_racket, "pop": sfx_pop, "tiebreak": sfx_tiebreak}


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    if only:  # regenerate selected sounds only
        for k, fn in NEW_SFX.items():
            if k in only:
                export(k, fn())
        if "ambience" in only:
            export("ambience", amb_stadium(), loop=True)
        return
    for k, fn in NEW_SFX.items():
        export(k, fn())
    export("ambience", amb_stadium(), loop=True)
    export("button", sfx_button())
    export("reel_stop", sfx_reel_stop())
    export("spin_start", sfx_spin_start())
    export("spin_loop", sfx_spin_loop(), loop=True)
    for i in range(3):
        export(f"scatter_{i + 1}", sfx_scatter_land(i))
    export("wild_land", sfx_wild_land())
    for i in range(4):
        export(f"win_{i}", sfx_win(i))
    export("line_tick", sfx_line_tick())
    export("bonus_trigger", sfx_bonus_trigger())
    export("wind", sfx_wind())
    export("mult_up", sfx_mult_up())
    export("count_tick", sfx_count_tick())
    export("bonus_end", sfx_bonus_end())
    export("match_point", sfx_match_point())
    export("music_base", music_base(), loop=True)
    export("music_free", music_free(), loop=True)
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"audio written to {OUT} ({len(os.listdir(OUT))} files, {total / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
