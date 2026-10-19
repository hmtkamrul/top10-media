"""Original, royalty-free "breaking news" background music, synthesised with numpy.

Suspenseful D-minor pulse: kick on the beat, ticking hi-hats, a driving 8th-note bass,
a dark string pad, and a riser + impact ("stinger") at every hit time.
"""
import numpy as np
import wave

SR = 44100
BPM = 112
BEAT = 60 / BPM


def _env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def _note(f, dur, kind="saw", amp=1.0, d=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "saw":
        x = 2 * (t * f % 1) - 1
    elif kind == "sqr":
        x = np.sign(np.sin(2 * np.pi * f * t))
    else:
        x = np.sin(2 * np.pi * f * t)
    return amp * x * _env(n, 0.004, d)


def _kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def _hat(rng, open_=False):
    n = int((0.12 if open_ else 0.04) * SR)
    x = rng.standard_normal(n)
    x = np.diff(x, prepend=0)                   # crude high-pass
    return x * np.exp(-np.arange(n) / SR / (0.05 if open_ else 0.012)) * 0.35


def _lowpass(x, a=0.08):
    try:
        from scipy.signal import lfilter
        return lfilter([a], [1, -(1 - a)], x)
    except ImportError:          # fallback: simple moving average
        k = max(1, int(1 / a))
        return np.convolve(x, np.ones(k) / k, mode="same")


def _add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def news_bed(seconds, hits=(), seed=3):
    """Return a float32 mono track of `seconds` length. `hits` = times (s) for stingers."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    drums = np.zeros(n)
    bass = np.zeros(n)
    pad = np.zeros(n)
    fx = np.zeros(n)
    # D minor progression, one chord per bar: Dm - Bb - Gm - A
    roots = [73.42, 58.27, 98.0, 110.0]
    chords = [[293.66, 349.23, 440.0], [233.08, 293.66, 349.23], [196.0, 233.08, 293.66], [220.0, 277.18, 329.63]]
    bar = 4 * BEAT
    nb = int(seconds / bar) + 1
    for b in range(nb):
        t0 = b * bar
        r = roots[b % 4]
        for e in range(8):                       # driving 8th-note bass
            _add(bass, _note(r * (2 if e % 4 == 3 else 1), BEAT / 2, "saw", 0.5, 0.18), t0 + e * BEAT / 2)
        for k in range(4):
            _add(drums, _kick() * (1.0 if k % 2 == 0 else 0.8), t0 + k * BEAT)
            for s in range(4):                   # ticking 16th hats, accent on the off-beat
                _add(drums, _hat(rng, open_=(s == 2 and k % 2 == 1)) * (1 if s == 2 else 0.55), t0 + k * BEAT + s * BEAT / 4)
        # pad: slow swell
        for f in chords[b % 4]:
            m = int(bar * SR)
            tt = np.arange(m) / SR
            sw = np.sin(np.pi * np.clip(tt / bar, 0, 1)) ** 0.8
            _add(pad, (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)) * sw * 0.12, t0)
    bass = _lowpass(bass, 0.06)
    # stingers: 1 s noise riser into a low impact + high "ding"
    for h in hits:
        m = int(1.0 * SR)
        tt = np.arange(m) / SR
        riser = rng.standard_normal(m) * (tt / 1.0) ** 2 * 0.25
        _add(fx, riser, max(0, h - 1.0))
        imp = np.sin(2 * np.pi * 45 * np.arange(int(1.2 * SR)) / SR) * np.exp(-np.arange(int(1.2 * SR)) / SR * 3) * 0.9
        _add(fx, imp, h)
        _add(fx, _note(1174.66, 0.9, "sin", 0.25, 0.4) + _note(1760.0, 0.9, "sin", 0.12, 0.3), h)
    mix = 0.55 * drums + 0.5 * bass + 0.6 * pad + 0.7 * fx
    # fade in / out
    fi, fo = int(0.8 * SR), int(2.0 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    return (mix / (np.max(np.abs(mix)) + 1e-9) * 0.9).astype(np.float32)


def write_wav(path, x, sr=SR):
    x16 = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(x16.tobytes())


# ---------------------------------------------------------------------------
# Signature jingle + mood beds (since 2026-10-19)
# Every Reel starts with the SAME ~1.6 s "Top 10" jingle (brand sound); the bed under the
# rest of the Reel follows the story's mood so 11 Reels a day don't all sound the same.
# ---------------------------------------------------------------------------

def _clap(rng):
    n = int(0.09 * SR)
    x = rng.standard_normal(n)
    x = np.diff(x, prepend=0)
    env = np.exp(-np.arange(n) / SR / 0.025)
    return x * env * 0.45


def _tom(f0=95, dur=0.28):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 + 60 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)


def _pluck(f, dur=0.5, amp=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return amp * x * np.exp(-t * 6) * np.minimum(1, t / 0.003)


def jingle():
    """Fixed ~1.6 s brand sting: rising three-note brass stab (A4-D5-A5) + low hit + shimmer."""
    rng = np.random.default_rng(10)
    n = int(1.6 * SR)
    out = np.zeros(n)
    for i, (f, at, ln) in enumerate([(440.0, 0.0, 0.16), (587.33, 0.17, 0.16), (880.0, 0.36, 1.1)]):
        m = int(ln * SR)
        t = np.arange(m) / SR
        env = np.minimum(1, t / 0.01) * (np.exp(-t * 2.2) if i == 2 else np.exp(-t * 9))
        tone = sum(((2 * (t * f * k % 1) - 1) / k) for k in (1, 2)) + 0.6 * np.sign(np.sin(2 * np.pi * f * 0.5 * t))
        tone += 0.5 * (2 * (t * f * 1.005 % 1) - 1)                      # detuned layer
        _add(out, _lowpass(tone * env * 0.32, 0.25), at)
    hit = np.sin(2 * np.pi * 50 * np.arange(int(0.9 * SR)) / SR) * np.exp(-np.arange(int(0.9 * SR)) / SR * 4) * 0.9
    _add(out, hit, 0.36)
    _add(out, _kick(), 0.36)
    sh = rng.standard_normal(int(1.1 * SR))
    sh = np.diff(sh, prepend=0) * np.exp(-np.arange(len(sh)) / SR * 3) * 0.08
    _add(out, sh, 0.36)
    for f in (1760.0, 2637.0):
        _add(out, _note(f, 1.0, "sin", 0.08, 0.5), 0.38)
    out[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
    return (out / (np.max(np.abs(out)) + 1e-9) * 0.95).astype(np.float32)


MOODS = {
    # bpm, bass roots per bar, chord (pad) per bar, style
    "hopeful": (100, [65.41, 98.0, 110.0, 87.31],
                [[261.63, 329.63, 392.0], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63]], "hopeful"),
    "protest": (128, [82.41, 65.41, 73.42, 82.41],
                [[164.81, 196.0, 246.94], [130.81, 164.81, 196.0], [146.83, 185.0, 220.0], [164.81, 196.0, 246.94]], "protest"),
    "sports": (124, [98.0, 73.42, 82.41, 65.41],
               [[196.0, 246.94, 293.66], [146.83, 185.0, 220.0], [164.81, 196.0, 246.94], [130.81, 164.81, 196.0]], "sports"),
    "calm": (80, [55.0, 87.31, 65.41, 98.0],
             [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]], "calm"),
}


def mood_bed(seconds, mood="tense", hits=(), seed=3):
    if mood not in MOODS:
        return news_bed(seconds, hits=hits, seed=seed)
    bpm, roots, chords, style = MOODS[mood]
    beat = 60 / bpm
    bar = 4 * beat
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    drums, bass, pad, lead, fx = (np.zeros(n) for _ in range(5))
    for b in range(int(seconds / bar) + 1):
        t0 = b * bar
        root, ch = roots[b % 4], chords[b % 4]
        for k in range(4):
            tb = t0 + k * beat
            if style == "sports":
                _add(drums, _kick(), tb)
                if k % 2 == 1:
                    _add(drums, _clap(rng), tb)
                _add(drums, _hat(rng, open_=True) * 0.8, tb + beat / 2)
                for c in ch:                                      # offbeat saw stabs
                    _add(lead, _note(c * 2, beat / 3, "saw", 0.10, 0.08), tb + beat / 2)
            elif style == "protest":
                _add(drums, _kick() * (1 if k % 2 == 0 else 0.7), tb)
                for e in range(2):                                # driving 8th-note toms
                    _add(drums, _tom(110 if e == 0 else 85) * (0.55 if e else 0.4), tb + e * beat / 2)
                if k % 2 == 1:
                    _add(drums, _clap(rng) * 1.2, tb)
                for s in range(4):
                    _add(bass, _note(root, beat / 4, "saw", 0.45, 0.07), tb + s * beat / 4)
            elif style == "hopeful":
                if k % 2 == 0:
                    _add(drums, _kick() * 0.7, tb)
                _add(drums, _hat(rng) * 0.7, tb + beat / 2)
                for e in range(2):                                # rising arpeggio plucks
                    _add(lead, _pluck(ch[(k * 2 + e) % 3] * 2, 0.6, 0.22), tb + e * beat / 2)
            else:                                                 # calm
                if k == 0:
                    _add(drums, _kick() * 0.35, tb)
                _add(drums, _hat(rng) * 0.35, tb + beat / 2)
                _add(lead, _pluck(ch[k % 3] * 2, 1.2, 0.2), tb)
        if style in ("hopeful", "sports", "calm"):
            for e in range(8 if style != "calm" else 4):
                step = bar / (8 if style != "calm" else 4)
                _add(bass, _note(root, step, "sin" if style == "calm" else "saw", 0.5, 0.2), t0 + e * step)
        m = int(bar * SR)
        tt = np.arange(m) / SR
        sw = np.sin(np.pi * np.clip(tt / bar, 0, 1)) ** 0.8
        for f in ch:
            _add(pad, (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)) * sw * 0.12, t0)
    bass = _lowpass(bass, 0.06)
    for h in hits:                                                # soft "ding" on every new fact
        _add(fx, _note(1174.66, 0.9, "sin", 0.2, 0.4) + _note(1760.0, 0.9, "sin", 0.1, 0.3), h)
        if style in ("protest", "sports"):
            _add(fx, rng.standard_normal(int(0.6 * SR)) * (np.linspace(0, 1, int(0.6 * SR)) ** 2) * 0.18, max(0, h - 0.6))
    w = {"hopeful": (0.45, 0.45, 0.65, 0.7), "protest": (0.75, 0.55, 0.4, 0.4),
         "sports": (0.7, 0.5, 0.45, 0.6), "calm": (0.3, 0.4, 0.8, 0.7)}[style]
    mix = w[0] * drums + w[1] * bass + w[2] * pad + w[3] * lead + 0.6 * fx
    fi, fo = int(0.5 * SR), int(2.0 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    return (mix / (np.max(np.abs(mix)) + 1e-9) * 0.9).astype(np.float32)


def mood_of(story):
    """Pick the music mood from the story (explicit "mood" wins)."""
    if story.get("mood"):
        return story["mood"]
    scene, cat = story.get("scene"), story.get("cat")
    if story.get("quote_by"):
        return "calm"
    if scene in ("war", "airport_fire"):
        return "tense"
    if scene in ("football", "cricket") or cat == "sports":
        return "sports"
    if scene in ("protest", "usa"):
        return "protest"
    if cat in ("bd", "econ") or scene in ("bridge", "economy"):
        return "hopeful"
    if scene == "world":
        return "calm"
    return "tense"


def with_jingle(bed, lead_in=1.25):
    """Put the signature jingle at 0 s and duck the bed under it."""
    j = jingle()
    out = bed.astype(np.float64).copy()
    k = int(lead_in * SR)
    duck = np.ones(len(out))
    duck[:k] = np.linspace(0.0, 0.25, k)
    r = min(len(out) - k, int(0.6 * SR))
    if r > 0:
        duck[k:k + r] = np.linspace(0.25, 1.0, r)
    out *= duck
    m = min(len(out), len(j))
    out[:m] += j[:m] * 1.1
    return (out / (np.max(np.abs(out)) + 1e-9) * 0.9).astype(np.float32)


def reel_track(seconds, story, hits=(), seed=3):
    """Full music track for one Reel: jingle + mood bed (+ dings on hits)."""
    return with_jingle(mood_bed(seconds, mood_of(story), hits=[h for h in hits if h > 1.0], seed=seed))
