"""Kinetic news Reel (1080x1920, ~16-20 s): built to keep people watching.

frame 0 = cover (ribbon + full headline, Facebook uses it as the thumbnail);
0.04 s  "ব্রেকিং নিউজ" ribbon slams in, headline pops in word by word
2.4 s   headline moves up; 3-4 key facts ("points_bn") slide in one by one, ~3.4 s each
end     follow card: "পুরো খবর কমেন্টে" + "ফলো করুন"
Background: the story's animated themed scene (same builders as the cards), darkened.
"""
import math, os, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import render3 as r

RW, RH = 1080, 1920
FPS = 24
LOOP = 36
HOOK = 2.4
PER_POINT = 3.4
OUTRO = 2.6
MAXW = RW - 140


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def back(t):
    t = max(0.0, min(1.0, t))
    c = 1.7
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


# ---------- background ----------
def photo_loop(story):
    """Static photo background with a slow push-in, for stories with "bg_image" (1080x1920)."""
    base = Image.open(story["bg_image"]).convert("RGB").resize((RW, RH))
    yy = np.arange(RH)[:, None, None] / RH                  # darken the text area, keep the face bright
    shade = 0.5 + 0.5 * np.clip((yy - 0.52) / 0.12, 0, 1)
    base = Image.fromarray(np.uint8(np.asarray(base, np.float32) * shade))
    out = []
    for i in range(LOOP):
        z = 1.0 + 0.015 * (0.5 - 0.5 * math.cos(2 * math.pi * i / LOOP))
        w, h = int(RW * z), int(RH * z)
        im = base.resize((w, h), Image.BICUBIC)
        ox, oy = (w - RW) // 2, (h - RH)
        out.append(im.crop((ox, oy, ox + RW, oy + RH)))
    return out


def scene_loop(story):
    if story.get("bg_image"):
        return photo_loop(story)
    from scenes import SCENE_BUILDERS
    from scenes2 import SCENE_BUILDERS2
    builders = {**SCENE_BUILDERS, **SCENE_BUILDERS2}
    seed = sum(map(ord, story.get("title_en", "") or story.get("short_bn", "")))
    name = story.get("scene")
    if name not in builders:
        name = {"sports": "football", "econ": "economy"}.get(story.get("cat"), "abstract")
    fn = builders[name]
    shade = np.ones((RH, 1, 1), np.float32)
    y = np.arange(RH)[:, None, None] / RH
    shade = 0.62 - 0.22 * np.exp(-((y - 0.45) / 0.28) ** 2)           # darker behind the text block
    out = []
    for i in range(LOOP):
        try:
            img = fn(i / LOOP, seed)
        except TypeError:
            img = fn(i / LOOP)
        img = r.place_people(img, story.get("people"))
        sc = RH / img.height
        img = img.resize((int(img.width * sc), RH), Image.LANCZOS)
        ox = (img.width - RW) // 2
        img = img.crop((ox, 0, ox + RW, RH))
        a = np.asarray(img, np.float32) * shade
        out.append(Image.fromarray(np.uint8(np.clip(a, 0, 255))))
    return out


# ---------- sprites (rendered once, moved per frame) ----------
def _sp(text):
    return text.replace("  ", " ").replace(" ", "  ")


def text_sprite(lines, font_bn, font_en, size, fill=None, stops=None, lh=1.18, shadow=True):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    ws = [r.width(d, l, font_bn, font_en, size) for l in lines]
    w, h = int(max(ws)) + 40, int(size * lh * (len(lines) - 1) + size * 1.6)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for l, lw in zip(lines, ws):
        x = (w - lw) / 2
        if stops:
            r.grad_text(im, (x, y - size * 0.1), l, size, stops, shadow=shadow)
        else:
            if shadow:
                sh = Image.new("L", (w, h), 0)
                r.draw_runs(ImageDraw.Draw(sh), x + 3, y + 5, l, font_bn, font_en, size, 255)
                im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(6)).point(lambda p: int(p * .8)))
            r.draw_runs(ImageDraw.Draw(im), x, y, l, font_bn, font_en, size, fill)
        y += size * lh
    return im


def headline_lines(story):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    txt = story["short_bn"].replace("  ", " ")
    for size in (124, 116, 108, 100, 94, 88, 82, 76):
        lines = [_sp(l) for l in r.wrap_balanced(d, txt, r.BN_HEAD, r.EN_BLACK, size, MAXW - 40)]
        if len(lines) <= 2 and all(r.width(d, l, r.BN_HEAD, r.EN_BLACK, size) <= MAXW for l in lines):
            return lines, size
    return lines, size


def ribbon_sprite(text="ব্রেকিং  নিউজ"):
    t = text
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    tw = r.width(d, t, r.BN_HEAD, r.EN_BLACK, 56)
    w, h = int(tw + 110), 96
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=18, fill=r.RED + (255,))
    dd.ellipse([24, 36, 48, 60], fill=(255, 255, 255, 255))                 # live dot
    r.draw_runs(dd, 66, 10, t, r.BN_HEAD, r.EN_BLACK, 56, (255, 255, 255, 255))
    return im


def point_sprite(text, n, size=54):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    lines = [_sp(l) for l in r.wrap_balanced(d, text.strip().rstrip("।") + "।", r.BN_SUB, r.EN_SEMI, size, MAXW - 150)]
    while len(lines) > 3 and size > 40:
        size -= 4
        lines = [_sp(l) for l in r.wrap_balanced(d, text.strip().rstrip("।") + "।", r.BN_SUB, r.EN_SEMI, size, MAXW - 150)]
    lh = size * 1.32
    h = int(lh * len(lines) + 46)
    w = MAXW
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, fill=(12, 8, 10, 215))
    dd.rounded_rectangle([0, 0, 12, h - 1], radius=6, fill=r.ORANGE + (255,))
    # number badge
    dd.ellipse([30, 22, 94, 86], fill=r.RED + (255,))
    num = str(n).translate(r.BN_DIGITS)
    nw = r.width(dd, num, r.BN_HEAD, r.EN_BLACK, 44)
    r.draw_runs(dd, 62 - nw / 2, 24, num, r.BN_HEAD, r.EN_BLACK, 44, (255, 255, 255, 255))
    y = 20
    for l in lines:
        r.draw_runs(dd, 118, y, l, r.BN_SUB, r.EN_SEMI, size, (255, 255, 255, 255))
        y += lh
    return im


def logo_sprite():
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    f1, f2 = r.font(r.OSWALD, 50), r.font(r.EN_BLACK, 24)
    wt, w10, ws = d.textlength("TOP", font=f1), d.textlength("10", font=f1), d.textlength("BREAKING NEWS BD", font=f2)
    w, h = int(26 + wt + 12 + w10 + 22 + 20 + ws + 30), 78
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=39, fill=(255, 255, 255, 240))
    x = 26
    dd.text((x, 5), "TOP", font=f1, fill=(12, 10, 12))
    x += wt + 12
    dd.rounded_rectangle([x - 2, 14, x + w10 + 20, h - 13], radius=8, fill=r.ORANGE)
    dd.text((x + 8, 5), "10", font=f1, fill=(12, 10, 12))
    x += w10 + 22 + 20
    dd.text((x, 25), "BREAKING NEWS BD", font=f2, fill=r.RED)
    return im


def points_of(story):
    pts = story.get("points_bn")
    if not pts:
        pts = [s.strip() for s in story.get("caption_bn", "").split("।") if len(s.strip()) > 8][:4]
    return pts[:story.get("max_points", 4)]


def paste(base, sp, x, y, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    if scale != 1.0:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.LANCZOS)
    if alpha < 0.999:
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda p: int(p * alpha)))
    base.alpha_composite(sp, (int(x), int(y)))


def outro_sprites(story):
    a = text_sprite([_sp(story.get("outro_top", "পুরো খবরের লিংক কমেন্টে"))], r.BN_SUB, r.EN_SEMI, 58, fill=(255, 255, 255, 255))
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    t = _sp(story.get("outro_pill", "ফলো করুন"))
    tw = r.width(d, t, r.BN_HEAD, r.EN_BLACK, 92)
    b = Image.new("RGBA", (int(tw + 120), 150), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bd.rounded_rectangle([0, 0, b.width - 1, 149], radius=75, fill=r.ORANGE + (255,))
    r.draw_runs(bd, 60, 14, t, r.BN_HEAD, r.EN_BLACK, 92, (12, 10, 12, 255))
    c = text_sprite([_sp(story.get("outro_sub", "প্রতিদিনের সেরা খবর পেতে"))], r.BN_SUB, r.EN_SEMI, 50, fill=(255, 210, 120, 255))
    return a, b, c


# ---------- render ----------
def render(story, out_dir):
    """Write frames to out_dir as JPEGs; return (n_frames, duration_s, hit_times)."""
    loop = scene_loop(story)
    lines, hsize = headline_lines(story)
    head = text_sprite(lines, r.BN_HEAD, r.EN_BLACK, hsize, stops=r.SNOW if story.get("bg_image") else r.FIRE)
    head_first = text_sprite(lines[:1], r.BN_HEAD, r.EN_BLACK, hsize, stops=r.SNOW) if len(lines) > 1 else None
    HOOK = story.get("hook_s", globals()["HOOK"])
    PER_POINT = story.get("per_point_s", globals()["PER_POINT"])
    OUTRO = story.get("outro_s", globals()["OUTRO"])
    qb = story.get("quote_by")
    by = text_sprite([_sp("— " + qb)], r.BN_SUB, r.EN_SEMI, 46, fill=r.YELLOW + (255,)) if qb else None
    if story.get("kicker_bn"):                       # sub-headline under the hook (life-hack Reels)
        by = text_sprite([_sp(story["kicker_bn"])], r.BN_HEAD, r.EN_BLACK, story.get("kicker_size", 50), fill=r.YELLOW + (255,))
    src = text_sprite([_sp("সূত্র: " + r.SRC_BN.get(story.get("source", ""), story.get("source", "")))],
                      r.BN_SUB, r.EN_SEMI, 40, fill=(255, 225, 200, 255))
    rib, logo = ribbon_sprite(story.get("ribbon_bn", "ব্রেকিং  নিউজ")), logo_sprite()
    plist = points_of(story)
    one = bool(story.get("bg_image")) or story.get("one_at_a_time", False)
    pts = [point_sprite(p, i + 1, story.get("point_size", 54 if len(plist) < 4 else 48)) for i, p in enumerate(plist)]
    oa, ob, oc = outro_sprites(story)
    words = [w for l in lines for w in l.split("  ")]

    dur = HOOK + PER_POINT * len(pts) + OUTRO
    n = int(dur * FPS)
    hits = [0.05] + [HOOK + PER_POINT * i for i in range(len(pts))]
    t_out = dur - OUTRO
    for f in range(n):
        t = f / FPS if f > 0 else HOOK - 0.35     # frame 0 is the cover: everything in place
        img = loop[(f // 2) % LOOP].convert("RGBA")
        d = ImageDraw.Draw(img)
        # progress bar (top) + logo
        d.rectangle([0, 0, RW, 10], fill=(40, 30, 30, 255))
        bar = r.hgrad(max(2, int(RW * t / dur)), 10, r.RED, r.YELLOW)
        img.paste(bar, (0, 0))
        paste(img, logo, RW - logo.width - 40, 90)
        # ribbon: slams in, stays at the top
        k = back(t / 0.35)
        paste(img, rib, (RW - rib.width) / 2, 220 - 40 * (1 - k), alpha=min(1, t / 0.15), scale=1.0 + 0.5 * (1 - ease(t / 0.35)))
        # headline: big in the middle during the hook, then up under the ribbon
        mv = ease((t - (HOOK - 0.3)) / 0.5)
        if t < t_out:
            sc = 1.0 - 0.28 * mv
            hy = 760 - head.height / 2 + (360 - (760 - head.height / 2)) * mv
            hx = (RW - head.width * sc) / 2
            if t < HOOK - 0.3:                       # word-by-word pop: reveal with a growing alpha
                shown = min(1.0, t / (HOOK - 0.8))
                paste(img, head, hx, hy + 30 * (1 - ease(t / 0.4)), alpha=shown, scale=sc)
            else:
                paste(img, head, hx, hy, scale=sc)
            if by is not None:
                paste(img, by, (RW - by.width) / 2, hy + head.height * sc - 10, alpha=ease((t - 0.8) / 0.4))
            paste(img, src, (RW - src.width) / 2, hy + head.height * sc + (by.height - 20 if by is not None else 0) - 8,
                  alpha=ease((t - 1.0) / 0.4) * (1 - 0.0 * mv))
            # points stack
            y = 360 + head.height * 0.72 + (by.height + 40 if by is not None else 70)
            photo = one
            for i, sp in enumerate(pts):
                t0 = HOOK + PER_POINT * i
                if t < t0:
                    break
                k = ease((t - t0) / 0.45)
                if photo:                              # one fact at a time; the previous one slides out
                    nxt = HOOK + PER_POINT * (i + 1)
                    if i < len(pts) - 1 and t >= nxt:
                        continue
                    out_k = ease((t - (nxt - 0.35)) / 0.35) if i < len(pts) - 1 else 0
                    paste(img, sp, 70 - 260 * (1 - k) + 300 * out_k, y, alpha=k * (1 - out_k))
                else:
                    paste(img, sp, 70 - 260 * (1 - k), y, alpha=k)
                    y += sp.height + (26 if len(pts) < 4 else 18)
        else:                                          # outro / follow card
            k = ease((t - t_out) / 0.4)
            dim = Image.new("RGBA", (RW, RH), (0, 0, 0, int(150 * k)))
            img.alpha_composite(dim)
            paste(img, oa, (RW - oa.width) / 2, 640, alpha=k)
            pulse = 1.0 + 0.05 * math.sin(2 * math.pi * (t - t_out) * 1.6)
            paste(img, oc, (RW - oc.width) / 2, 820, alpha=k)
            paste(img, ob, (RW - ob.width * pulse) / 2, 920 + 20 * (1 - k), alpha=k, scale=pulse)
        img.convert("RGB").save(f"{out_dir}/f{f:05d}.jpg", quality=88)
    return n, dur, hits


def make_kinetic(story, path):
    import music
    from build_day import AUDIO_FX
    tmp = tempfile.mkdtemp()
    try:
        n, dur, hits = render(story, tmp)
        bed = music.reel_track(dur, story, hits=hits, seed=sum(map(ord, story.get("title_en", ""))) % 997)  # jingle + mood bed
        mix = np.tanh(bed / (np.max(np.abs(bed)) + 1e-9) * 2.2) / np.tanh(2.2)
        music.write_wav(f"{tmp}/m.wav", mix * 0.97)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%05d.jpg",
                        "-i", f"{tmp}/m.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21",
                        "-af", AUDIO_FX, "-c:a", "aac", "-b:a", "192k", "-shortest", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dur
