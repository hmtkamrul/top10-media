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
