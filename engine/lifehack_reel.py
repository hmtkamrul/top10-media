"""Life-hack Reel series (separate look from the news Reels; user's request 2026-10-24).

Festive, colourful animated background (orange, green, red, yellow, purple blobs, confetti, sparkles,
swinging bunting) and an upbeat festive music track. Text layout comes from kinetic.render
(hook headline + kicker, numbered tips one by one, GUIDE outro).

Usage: python3 lifehack_reel.py ../days/lifehack/<file>.json ../lifehack/<name>/
Writes post_01_reel.mp4 (first story in the file).
"""
import json, math, os, random, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kinetic
import music
import render3 as r

RW, RH, LOOP = kinetic.RW, kinetic.RH, kinetic.LOOP
PALETTE = [(255, 140, 0), (34, 197, 94), (232, 30, 60), (255, 206, 30), (150, 70, 230)]  # orange green red yellow purple


# ---------------- background ----------------
def _base():
    y = np.linspace(0, 1, RH)[:, None]
    top, bot = np.array([70, 18, 110]), np.array([150, 20, 80])          # deep purple -> festive magenta
    g = top + (bot - top) * y
    return np.repeat(g[:, None, :], RW, axis=1).reshape(RH, RW, 3)


def festive_loop(story=None, seed=7):
    rng = random.Random(seed)
    base = _base()
    blobs = [(rng.uniform(0, RW), rng.uniform(0, RH), rng.uniform(220, 380), PALETTE[i % 5], rng.uniform(0, 6.28),
              rng.choice([1, -1]) * rng.uniform(60, 140)) for i in range(10)]
    confetti = [(rng.uniform(0, RW), rng.uniform(0, RH), rng.choice(PALETTE), rng.uniform(0, 6.28),
                 rng.choice([1, 2]), rng.uniform(8, 14), rng.uniform(18, 30)) for _ in range(110)]
    stars = [(rng.uniform(40, RW - 40), rng.uniform(40, RH - 40), rng.uniform(0, 1), rng.uniform(6, 14)) for _ in range(40)]
    y = np.arange(RH)[:, None, None] / RH
    shade = 0.9 - 0.32 * np.exp(-((y - 0.36) / 0.22) ** 2)              # calmer behind the text block
    out = []
    for i in range(LOOP):
        ph = i / LOOP
        # soft colour blobs drifting in circles
        lay = Image.new("RGBA", (RW // 4, RH // 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for (x, yy, rad, c, th, orb) in blobs:
            cx = (x + orb * math.cos(2 * math.pi * ph + th)) / 4
            cy = (yy + orb * math.sin(2 * math.pi * ph + th)) / 4
            rr = rad / 4
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c + (150,))
        lay = lay.filter(ImageFilter.GaussianBlur(28)).resize((RW, RH), Image.BICUBIC)
        img = Image.fromarray(np.uint8(base)).convert("RGBA")
        img.alpha_composite(lay)
        # light rays from the top centre, slowly turning
        rays = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rays)
        for k in range(12):
            a = 2 * math.pi * (k / 12 + ph / 12)
            rd.polygon([(RW / 2, -200), (RW / 2 + 2600 * math.cos(a - 0.06), -200 + 2600 * math.sin(a - 0.06)),
                        (RW / 2 + 2600 * math.cos(a + 0.06), -200 + 2600 * math.sin(a + 0.06))], fill=(255, 255, 255, 14))
        img.alpha_composite(rays)
        # confetti falling (whole screen per loop -> seamless)
        cf = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
        for (x, yy, c, th, spd, w, h) in confetti:
            cy = (yy + spd * RH * ph) % (RH + 60) - 30
            cx = x + 26 * math.sin(2 * math.pi * ph + th)
            ang = math.degrees(th + 2 * math.pi * ph * spd)
            piece = Image.new("RGBA", (int(w), int(h)), c + (235,))
            piece = piece.rotate(ang, expand=True, resample=Image.BICUBIC)
            cf.alpha_composite(piece, (int(cx), int(cy)))
        img.alpha_composite(cf)
        # twinkling sparkles
        sd = ImageDraw.Draw(img)
        for (x, yy, off, s) in stars:
            a = 0.5 + 0.5 * math.sin(2 * math.pi * (ph * 2 + off))
            if a < 0.35:
                continue
            al = int(255 * a)
            sd.line([(x - s, yy), (x + s, yy)], fill=(255, 250, 220, al), width=3)
            sd.line([(x, yy - s), (x, yy + s)], fill=(255, 250, 220, al), width=3)
        # swinging bunting (two strings at the bottom)
        for row, (y0, sag) in enumerate([(1560, 70), (1700, 60)]):
            sw = 18 * math.sin(2 * math.pi * ph + row)
            pts = [(x, y0 + sag * math.sin(math.pi * x / RW) + sw * math.sin(math.pi * x / RW)) for x in range(-20, RW + 41, 20)]
            sd.line(pts, fill=(255, 240, 210, 230), width=4)
            for j, x in enumerate(range(10, RW, 72)):
                yy = y0 + sag * math.sin(math.pi * x / RW) + sw * math.sin(math.pi * x / RW)
                c = PALETTE[(j + row * 2) % 5]
                sd.polygon([(x - 26, yy), (x + 26, yy), (x, yy + 58)], fill=c + (255,))
        a = np.asarray(img.convert("RGB"), np.float32) * shade
        out.append(Image.fromarray(np.uint8(np.clip(a, 0, 255))))
    return out


# ---------------- music ----------------
SR = music.SR
BPM = 124
BEAT = 60 / BPM
N = lambda m: 440.0 * 2 ** ((m - 69) / 12)                                # midi -> Hz
CHORDS = [(60, 64, 67), (67, 71, 74), (69, 72, 76), (65, 69, 72)]        # C  G  Am  F (bright, happy)
MELODY = [76, 79, 81, 79, 76, 74, 72, 74, 76, 74, 72, 71, 72, 74, 76, 79]  # simple bell hook, 8ths x 2 bars


def _bell(f, dur=0.6, amp=0.22):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9)
    return amp * x * np.exp(-t * 3.2) * np.minimum(1, t / 0.002)


def _shaker(rng):
    n = int(0.05 * SR)
    x = np.diff(rng.standard_normal(n), prepend=0)
    return x * np.exp(-np.arange(n) / SR / 0.015) * 0.12


def _swoosh(dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    x = music._lowpass(rng.standard_normal(n), 0.15)
    return x * np.sin(np.pi * t / dur) ** 2 * 0.5


def festive_track(seconds, hits=(), seed=3):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR) + SR
    buf = np.zeros(n)
    bars = int(seconds / (4 * BEAT)) + 2
    for b in range(bars):
        t0 = b * 4 * BEAT
        ch = CHORDS[b % 4]
        # bass on every beat (root, octave pop)
        for k in range(4):
            f = N(ch[0] - 24) * (2 if k % 2 else 1)
            music._add(buf, music._lowpass(music._note(f, BEAT * 0.9, "saw", 0.5, 0.18), 0.12), t0 + k * BEAT)
        # sparkly arpeggio 8ths
        for k in range(8):
            m = ch[k % 3] + (12 if k >= 4 else 0)
            music._add(buf, music._pluck(N(m), 0.4, 0.13), t0 + k * BEAT / 2)
        # bell hook (2-bar phrase), after the intro bar
        if b >= 1:
            for k in range(8):
                m = MELODY[(b % 2) * 8 + k]
                if k in (3, 7) and b % 2:
                    continue
                music._add(buf, _bell(N(m)), t0 + k * BEAT / 2)
        # drums: four-on-the-floor kick, clap on 2 & 4, shaker 16ths, dhol-style toms on the last beat
        for k in range(4):
            music._add(buf, music._kick() * 0.85, t0 + k * BEAT)
            if k in (1, 3):
                music._add(buf, music._clap(rng) * 1.1, t0 + k * BEAT)
        for k in range(16):
            music._add(buf, _shaker(rng) * (1.3 if k % 4 == 2 else 0.8), t0 + k * BEAT / 4)
        if b % 2 == 1:
            for k, f0 in enumerate((130, 110, 95, 80)):
                music._add(buf, music._tom(f0, 0.22) * 0.55, t0 + 3 * BEAT + k * BEAT / 4)
    music._add(buf, _swoosh(), 0.0)
    for h in hits:                                   # a bright "ding" as each tip appears
        music._add(buf, _bell(N(84), 0.8, 0.28) + _bell(N(91), 0.8, 0.14), h)
    buf = buf[: int(seconds * SR)]
    fade = int(1.2 * SR)
    buf[-fade:] *= np.linspace(1, 0, fade)
    buf[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    return (buf / (np.max(np.abs(buf)) + 1e-9) * 0.9).astype(np.float32)


# ---------------- build ----------------
def make_lifehack(story, path):
    from build_day import AUDIO_FX
    kinetic.scene_loop = lambda st: festive_loop(st, seed=sum(map(ord, st.get("title_en", ""))) % 97)
    tmp = tempfile.mkdtemp()
    try:
        n, dur, hits = kinetic.render(story, tmp)
        mix = festive_track(dur, hits=[h for h in hits if h > 1.0], seed=sum(map(ord, story.get("title_en", ""))) % 997)
        mix = np.tanh(mix * 1.8) / np.tanh(1.8)
        music.write_wav(f"{tmp}/m.wav", mix * 0.97)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(kinetic.FPS), "-i", f"{tmp}/f%05d.jpg",
                        "-i", f"{tmp}/m.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21",
                        "-af", AUDIO_FX, "-c:a", "aac", "-b:a", "192k", "-shortest", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dur


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    st = json.load(open(src, encoding="utf-8"))["stories"][0]
    d = make_lifehack(st, os.path.join(out, "post_01_reel.mp4"))
    print(f"built life-hack Reel: {d:.1f} s")
