"""News cards in the 'cinematic + gold framed headline' style (1080x1350).

Usage: python3 render2.py stories_YYYY-MM-DD.json out_dir/
"""
import json, os, sys, random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(HERE, "fonts", n)
BN_HEAD = F("anek-bangla-bengali-800-normal.ttf")
BN_SUB = F("anek-bangla-bengali-600-normal.ttf")
OSWALD = F("oswald-latin-700-normal.ttf")
BN_SMALL = F("hind-siliguri-bengali-600-normal.ttf")
EN_SEMI = F("inter-latin-600-normal.ttf")
EN_BLACK = F("inter-latin-800-normal.ttf")
SERIF = F("playfair-display-latin-700-normal.ttf")

W, H = 1080, 1350
BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
SRC_BN = {"Al Jazeera": "আল জাজিরা", "Prothom Alo": "প্রথম আলো", "The Daily Star": "দ্য ডেইলি স্টার",
          "BBC": "বিবিসি", "Reuters": "রয়টার্স", "AP": "এপি", "bdnews24": "বিডিনিউজ২৪"}

# Per-category scene palettes: sky top, sky mid, horizon glow, silhouette
SCENES = {
    "bd":     dict(top=(26, 4, 8), mid=(205, 36, 24), glow=(255, 150, 40), sil=(10, 6, 8), tag="বাংলাদেশ", accent=(226, 28, 40)),
    "intl":   dict(top=(18, 4, 10), mid=(196, 30, 30), glow=(255, 128, 20), sil=(8, 6, 8), tag="আন্তর্জাতিক", accent=(255, 98, 0)),
    "econ":   dict(top=(24, 10, 4), mid=(214, 70, 10), glow=(255, 190, 40), sil=(10, 8, 6), tag="অর্থনীতি", accent=(255, 140, 0)),
    "sports": dict(top=(22, 4, 14), mid=(200, 24, 60), glow=(255, 120, 60), sil=(10, 6, 8), tag="খেলা", accent=(236, 20, 80)),
}

NAVY = (12, 10, 12)          # box background is now near-black
BLACK = (12, 10, 12)
RED = (232, 30, 40)
ORANGE = (255, 112, 0)
YELLOW = (255, 200, 30)
GOLD_LIGHT, GOLD_MID, GOLD_DARK = YELLOW, ORANGE, RED
WHITE = (255, 255, 255)

_cm, _fc = {}, {}


def font(p, s):
    if (p, s) not in _fc:
        _fc[(p, s)] = ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
    return _fc[(p, s)]


def has(p, ch):
    if p not in _cm:
        _cm[p] = TTFont(p).getBestCmap()
    return ord(ch) in _cm[p]


def runs(text, bn, en):
    out = []
    for ch in text:
        if ch == " " and out:
            p = out[-1][1]
        elif not ch.isascii() and has(bn, ch):
            p = bn
        else:
            p = en
        if out and out[-1][1] == p:
            out[-1][0] += ch
        else:
            out.append([ch, p])
    return out


def width(d, text, bn, en, size):
    return sum(d.textlength(t, font=font(p, size)) for t, p in runs(text, bn, en))


def draw_runs(d, x, y, text, bn, en, size, fill):
    for t, p in runs(text, bn, en):
        f = font(p, size)
        d.text((x, y + (int(size * 0.18) if p != bn else 0)), t, font=f, fill=fill)
        x += d.textlength(t, font=f)


def wrap_balanced(d, text, bn, en, size, maxw):
    """Greedy wrap, then rebalance two-line headlines so lines are similar length."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if width(d, t, bn, en, size) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    if len(lines) == 2:
        best = None
        for i in range(1, len(words)):
            a, b = " ".join(words[:i]), " ".join(words[i:])
            wa, wb = width(d, a, bn, en, size), width(d, b, bn, en, size)
            if max(wa, wb) <= maxw and (best is None or abs(wa - wb) < best[0]):
                best = (abs(wa - wb), [a, b])
        if best:
            lines = best[1]
    return lines


# ---------------- scene ----------------

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def scene(cat, seed, motifs=()):
    rnd = random.Random(seed)
    pal = SCENES.get(cat, SCENES["bd"])
    SH = H
    # sky gradient
    ys = np.linspace(0, 1, SH)[:, None]
    top, mid, glow = [np.array(c, float) for c in (pal["top"], pal["mid"], pal["glow"])]
    t1 = np.clip(ys / 0.62, 0, 1) ** 1.3
    sky = top * (1 - t1[..., None]) + mid * t1[..., None]
    sky = np.repeat(sky, W, axis=1)
    # sun glow
    sx = W * (0.5 + rnd.uniform(-0.15, 0.15)); sy = SH * 0.6
    yy, xx = np.mgrid[0:SH, 0:W]
    dist = np.sqrt(((xx - sx) / 1.3) ** 2 + (yy - sy) ** 2)
    g = np.exp(-(dist / 260) ** 2)[..., None]
    g2 = np.exp(-(dist / 70) ** 2)[..., None]
    sky = sky * (1 - 0.85 * g) + glow * 0.85 * g
    sky = sky * (1 - g2) + np.array([255, 248, 225.0]) * g2
    img = Image.fromarray(np.clip(sky, 0, 255).astype("uint8"))

    # light rays
    rays = Image.new("L", (W, SH), 0)
    rd = ImageDraw.Draw(rays)
    for i in range(14):
        ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05)
        spread = rnd.uniform(0.02, 0.05)
        L = 1400
        p1 = (sx + L * math.cos(ang - spread), sy + L * math.sin(ang - spread))
        p2 = (sx + L * math.cos(ang + spread), sy + L * math.sin(ang + spread))
        rd.polygon([(sx, sy), p1, p2], fill=rnd.randint(25, 55))
    rays = rays.filter(ImageFilter.GaussianBlur(18))
    img = Image.composite(Image.new("RGB", (W, SH), pal["glow"]), img, rays)

    # clouds
    cl = Image.new("L", (W, SH), 0)
    cd = ImageDraw.Draw(cl)
    for i in range(38):
        cx, cy = rnd.uniform(-100, W + 100), rnd.uniform(40, SH * 0.45)
        rw, rh = rnd.uniform(80, 260), rnd.uniform(18, 50)
        cd.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=rnd.randint(40, 110))
    cl = cl.filter(ImageFilter.GaussianBlur(22))
    cloud_col = Image.new("RGB", (W, SH), lerp(pal["mid"], pal["glow"], 0.5))
    img = Image.composite(cloud_col, img, cl)

    # skyline silhouette (far + near layers)
    for layer, (base, hmin, hmax, col_t) in enumerate([(SH * 0.70, 60, 200, 0.55), (SH * 0.80, 90, 300, 0.0)]):
        sil = Image.new("L", (W, SH), 0)
        sd = ImageDraw.Draw(sil)
        x = -20
        while x < W + 20:
            bw = rnd.randint(40, 110)
            bh = rnd.randint(hmin, hmax)
            if abs(x - sx) < 160 and layer == 1:
                bh = int(bh * 0.5)  # keep the sun visible
            sd.rectangle([x, base - bh, x + bw, SH], fill=255)
            r = rnd.random()
            if r < 0.15:  # dome
                sd.ellipse([x + 5, base - bh - bw * 0.45, x + bw - 5, base - bh + bw * 0.45], fill=255)
            elif r < 0.25:  # spire
                sd.polygon([(x + bw / 2 - 6, base - bh), (x + bw / 2, base - bh - rnd.randint(40, 110)), (x + bw / 2 + 6, base - bh)], fill=255)
            x += bw - rnd.randint(2, 14)
        sil = sil.filter(ImageFilter.GaussianBlur(1.5 if layer else 3))
        colr = lerp(pal["sil"], pal["mid"], col_t)
        img = Image.composite(Image.new("RGB", (W, SH), colr), img, sil)

    # warm bokeh lights / crowd glow along the street
    bok = Image.new("RGB", (W, SH), (0, 0, 0))
    bd = ImageDraw.Draw(bok)
    for i in range(90):
        bx, by = rnd.uniform(0, W), rnd.uniform(SH * 0.72, SH * 0.98)
        r = rnd.uniform(4, 18)
        c = lerp(pal["glow"], (255, 200, 120), rnd.random())
        bd.ellipse([bx - r, by - r, bx + r, by + r], fill=tuple(int(v * k) for v in c) if (k := rnd.uniform(0.35, 0.85)) else c)
    bok = bok.filter(ImageFilter.GaussianBlur(5))
    img = ImageChops.add(img, bok)

    if "smoke" in motifs:
        sm = Image.new("L", (W, SH), 0)
        smd = ImageDraw.Draw(sm)
        bx = W * rnd.uniform(0.22, 0.32)
        for i in range(70):
            t = i / 70
            cx = bx + t * 160 + rnd.uniform(-30, 30)
            cy = SH * 0.72 - t * 560
            r = 30 + t * 120 + rnd.uniform(-10, 10)
            smd.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=int(215 * (1 - t * 0.55)))
        sm = sm.filter(ImageFilter.GaussianBlur(20))
        img = Image.composite(Image.new("RGB", (W, SH), (38, 34, 38)), img, sm)
        fire = Image.new("RGB", (W, SH), (0, 0, 0))
        ImageDraw.Draw(fire).ellipse([bx - 70, SH * 0.68 - 40, bx + 70, SH * 0.68 + 50], fill=(255, 120, 30))
        img = ImageChops.add(img, fire.filter(ImageFilter.GaussianBlur(28)))
    if "plane" in motifs:
        pl = Image.new("L", (900, 400), 0)
        pd = ImageDraw.Draw(pl)
        pd.ellipse([60, 170, 840, 230], fill=255)                      # fuselage
        pd.polygon([(780, 182), (870, 120), (880, 128), (830, 205)], fill=255)  # tail fin
        pd.polygon([(760, 200), (860, 245), (850, 255), (740, 215)], fill=255)  # tail plane
        pd.polygon([(380, 195), (560, 195), (330, 360), (290, 360)], fill=255)  # far wing
        pd.polygon([(400, 205), (560, 205), (430, 20), (390, 20)], fill=255)   # near wing
        pd.ellipse([410, 225, 490, 265], fill=255)                     # engine
        pl = pl.transpose(Image.FLIP_LEFT_RIGHT).resize((450, 200)).rotate(14, expand=True, resample=Image.BICUBIC)
        px, py = int(W * 0.56), int(SH * 0.12)
        img.paste(Image.new("RGB", pl.size, pal["sil"]), (px, py), pl)

    if "airport" in motifs:
        ad = ImageDraw.Draw(img)
        base = int(SH * 0.80)
        tc = (14, 14, 22)
        # control tower
        tx = int(W * 0.80)
        ad.rectangle([tx - 16, base - 330, tx + 16, base], fill=tc)
        ad.polygon([(tx - 70, base - 330), (tx + 70, base - 330), (tx + 52, base - 390), (tx - 52, base - 390)], fill=tc)
        ad.rectangle([tx - 58, base - 384, tx + 58, base - 340], fill=(255, 196, 110))  # lit cab
        for k in range(-50, 58, 14):
            ad.line([tx + k, base - 384, tx + k, base - 340], fill=tc, width=3)
        ad.polygon([(tx - 46, base - 390), (tx + 46, base - 390), (tx, base - 425)], fill=tc)
        ad.line([tx, base - 425, tx, base - 470], fill=tc, width=4)
        ad.ellipse([tx - 7, base - 478, tx + 7, base - 464], fill=(255, 60, 50))
        # terminal with lit windows
        ad.rectangle([0, base - 90, int(W * 0.72), base + 40], fill=tc)
        ad.polygon([(0, base - 90), (int(W * 0.72), base - 90), (int(W * 0.70), base - 120), (0, base - 120)], fill=tc)
        for wx in range(18, int(W * 0.70), 34):
            for wy in (base - 72, base - 38):
                if rnd.random() < 0.75:
                    ad.rectangle([wx, wy, wx + 20, wy + 20], fill=lerp((255, 190, 100), (255, 235, 180), rnd.random()))
        # palm trees
        for px in [int(W * 0.06), int(W * 0.17), int(W * 0.93)]:
            ph = rnd.randint(170, 230)
            for t in range(ph):
                ad.ellipse([px + int(14 * math.sin(t / 60)) - 7, base + 40 - t - 7, px + int(14 * math.sin(t / 60)) + 7, base + 40 - t + 7], fill=(10, 10, 16))
            topx, topy = px + int(14 * math.sin(ph / 60)), base + 40 - ph
            for a in range(0, 360, 36):
                r = math.radians(a)
                pts = [(topx, topy)]
                for q in range(1, 9):
                    L = q * 14
                    pts.append((topx + L * math.cos(r), topy + L * math.sin(r) * 0.45 + (q ** 2.1)))
                ad.line(pts, fill=(10, 10, 16), width=13, joint="curve")
        # runway lights
        for i in range(26):
            lx = i * (W / 25)
            ad.ellipse([lx - 6, base + 52, lx + 6, base + 64], fill=(255, 210, 120) if i % 2 else (255, 70, 40))
        glow_l = Image.new("RGB", (W, SH), (0, 0, 0))
        gd = ImageDraw.Draw(glow_l)
        for i in range(26):
            lx = i * (W / 25)
            gd.ellipse([lx - 22, base + 36, lx + 22, base + 80], fill=(150, 110, 50))
        gd.rectangle([tx - 70, base - 400, tx + 70, base - 320], fill=(120, 80, 30))
        img = ImageChops.add(img, glow_l.filter(ImageFilter.GaussianBlur(14)))
        # embers rising from the fire
        ed = ImageDraw.Draw(img)
        for i in range(70):
            ex = W * 0.27 + rnd.gauss(0, 70); ey = SH * 0.68 - abs(rnd.gauss(0, 200))
            r = rnd.uniform(1.5, 3.5)
            ed.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(255, rnd.randint(140, 220), 60))

    # punchier colour + contrast for a more vivid look
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(1.35)
    img = ImageEnhance.Contrast(img).enhance(1.12)

    canvas = Image.new("RGB", (W, H), NAVY)
    canvas.paste(img, (0, 0))
    # fade scene into navy at the bottom
    fade = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fade)
    for y in range(1250, H):
        fd.line([(0, y), (W, y)], fill=min(255, int(140 * ((y - 1250) / 100))))
    canvas = Image.composite(Image.new("RGB", (W, H), (12, 10, 12)), canvas, fade)
    # vignette
    vy, vx = np.mgrid[0:H, 0:W]
    v = np.clip(1 - 0.55 * (((vx - W / 2) / (W * 0.75)) ** 2 + ((vy - H * 0.4) / (H * 0.8)) ** 2), 0.45, 1)
    arr = (np.asarray(canvas, float) * v[..., None]).astype("uint8")
    return Image.fromarray(arr)


# ---------------- frame + text ----------------

def grad_text(base, xy, text, size, stops, shadow=True, vertical=True):
    x, y = xy
    tmp = ImageDraw.Draw(base)
    w = int(width(tmp, text, BN_HEAD, EN_BLACK, size)) + 20
    h = int(size * 1.6)
    mask = Image.new("L", (w, h), 0)
    draw_runs(ImageDraw.Draw(mask), 0, 0, text, BN_HEAD, EN_BLACK, size, 255)
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(7))
        base.paste(Image.new("RGB", (w, h), (0, 0, 0)), (int(x) + 4, int(y) + 6), sh.point(lambda p: int(p * 0.85)))
    n = h if vertical else w
    t = np.linspace(0, 1, n)
    col = np.zeros((n, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        k = np.clip((t - t0) / (t1 - t0), 0, 1)
        for i in range(3):
            col[:, i] = np.where(m, c0[i] + (c1[i] - c0[i]) * k, col[:, i])
    grad = np.repeat(col[:, None, :], w, 1) if vertical else np.repeat(col[None, :, :], h, 0)
    base.paste(Image.fromarray(grad.astype("uint8")), (int(x), int(y)), mask)


FIRE = [(0.0, YELLOW), (0.55, ORANGE), (1.0, RED)]
SNOW = [(0.0, WHITE), (1.0, (255, 226, 210))]


def hgrad(w, h, c0, c1):
    t = np.linspace(0, 1, w)[None, :, None]
    arr = np.array(c0, float) * (1 - t) + np.array(c1, float) * t
    return Image.fromarray(np.repeat(arr, h, 0).astype("uint8"))


def frame(img, box):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=BLACK)
    # thick red->orange border
    bw = 8
    border = hgrad(x1 - x0, y1 - y0, RED, ORANGE)
    m = Image.new("L", (x1 - x0, y1 - y0), 255)
    ImageDraw.Draw(m).rectangle([bw, bw, x1 - x0 - bw - 1, y1 - y0 - bw - 1], fill=0)
    img.paste(border, (x0, y0), m)
    # diagonal youth stripes in the bottom-right corner
    for k in range(4):
        ox = x1 - 40 - k * 26
        d.polygon([(ox, y1 - bw), (ox + 14, y1 - bw), (ox + 44, y1 - 40), (ox + 30, y1 - 40)], fill=ORANGE if k % 2 else RED)
    # slanted "BREAKING" ribbon sitting on the top edge
    rib = "ব্রেকিং নিউজ"
    f = font(BN_HEAD, 34)
    rw = d.textlength(rib, font=f) + 70
    rx, ry = x0 + 30, y0 - 30
    d.polygon([(rx + 16, ry), (rx + rw, ry), (rx + rw - 16, ry + 56), (rx, ry + 56)], fill=RED)
    d.polygon([(rx + rw + 6, ry), (rx + rw + 26, ry), (rx + rw + 10, ry + 56), (rx + rw - 10, ry + 56)], fill=ORANGE)
    d.ellipse([rx + 22, ry + 22, rx + 34, ry + 34], fill=WHITE)
    d.text((rx + 44, ry + 4), rib, font=f, fill=WHITE)


_RB = None


def cutout(path):
    """Return an RGBA cut-out of the person in a photo (background removed)."""
    global _RB
    from rembg import remove, new_session
    if _RB is None:
        _RB = new_session("u2net_human_seg")
    im = Image.open(path).convert("RGB")
    out = remove(im, session=_RB)
    bb = out.getbbox()
    return out.crop(bb) if bb else out


def placeholder_person(label):
    """Grey head-and-shoulders silhouette marking where a photo will go."""
    w, h = 520, 700
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = (150, 156, 170, 235)
    d.ellipse([w * 0.30, 40, w * 0.70, 40 + w * 0.46], fill=col)
    d.rounded_rectangle([w * 0.42, 250, w * 0.58, 330], radius=20, fill=col)
    d.rounded_rectangle([20, 300, w - 20, h + 120], radius=170, fill=col)
    f = font(BN_SUB, 46)
    tw = d.textlength(label, font=f)
    d.text(((w - tw) / 2, 470), label, font=f, fill=(40, 44, 60, 255))
    return im


def place_people(img, people):
    """Put up to two people side by side above the headline box, like a news poster."""
    if not people:
        return img
    base_y = 930  # feet hidden behind the headline box
    slots = [(0.02, 0.50, 760), (0.50, 0.98, 700)] if len(people) > 1 else [(0.20, 0.80, 780)]
    canvas = img.convert("RGBA")
    d = ImageDraw.Draw(canvas)
    for i, (person, (fx0, fx1, target_h)) in enumerate(zip(people, slots)):
        p = person.get("path")
        cut = cutout(p) if p and os.path.exists(p) else placeholder_person(person.get("label", "ছবি"))
        sc = target_h / cut.height
        if cut.width * sc > (fx1 - fx0) * W * 1.15:
            sc = (fx1 - fx0) * W * 1.15 / cut.width
        cut = cut.resize((int(cut.width * sc), int(cut.height * sc)), Image.LANCZOS)
        cx = int((fx0 + fx1) / 2 * W - cut.width / 2)
        cy = base_y - cut.height
        a = cut.split()[3]
        # warm rim glow behind the person
        glow = a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.65))
        canvas.paste((255, 90, 20, 255), (cx, cy), glow)
        canvas.alpha_composite(cut, (cx, cy))
        if person.get("credit"):
            cf = font(EN_SEMI, 15)
            d.text((cx + 12, base_y - 26), "Photo: " + person["credit"], font=cf, fill=(230, 230, 230, 220))
    return canvas.convert("RGB")


def card(story, rank, total, date_bn, page_name, phase=0.0):
    from scenes import SCENE_BUILDERS
    if story.get("scene") in SCENE_BUILDERS:
        img = SCENE_BUILDERS[story["scene"]](phase)
    else:
        img = scene(story["cat"], seed=sum(map(ord, story["title_en"])), motifs=story.get("motifs", ()))
        if phase:
            # slow push-in so still scenes also move in videos
            z = 1 + 0.07 * phase
            big = img.resize((int(W * z), int(H * z)), Image.LANCZOS)
            ox, oy = (big.width - W) // 2, (big.height - H) // 2
            img = big.crop((ox, oy, ox + W, oy + H))
    img = place_people(img, story.get("people"))
    d = ImageDraw.Draw(img)
    pal = SCENES.get(story["cat"], SCENES["bd"])

    # Logo, top-right: "TOP [10]" sized so it spans exactly the "BREAKING NEWS BD" line
    f2 = font(EN_SEMI, 16)
    sub = "BREAKING NEWS BD"
    track = 3.2                                   # letter spacing in px
    w3 = sum(d.textlength(c, font=f2) for c in sub) + track * (len(sub) - 1)
    pad, gap = 12, 10                             # inner padding of the orange box, gap after TOP
    for sz in range(90, 30, -1):
        f1 = font(OSWALD, sz)
        w1, w2 = d.textlength("TOP", font=f1), d.textlength("10", font=f1)
        if w1 + gap + w2 + 2 * pad <= w3:
            break
    top_w = w1 + gap + w2 + 2 * pad
    rx = W - 54 - w3
    ty = 22
    asc = f1.getbbox("TOP10")                     # visible glyph box (top, bottom)
    gh = asc[3] - asc[1]
    tx = rx + (w3 - top_w) / 2
    d.text((tx + 2, ty + 2), "TOP", font=f1, fill=(0, 0, 0))
    d.text((tx, ty), "TOP", font=f1, fill=WHITE)
    bx = tx + w1 + gap
    d.rounded_rectangle([bx, ty + asc[1] - 8, bx + w2 + 2 * pad, ty + asc[3] + 8], radius=8, fill=ORANGE)
    d.text((bx + pad, ty), "10", font=f1, fill=BLACK)
    ry = ty + asc[3] + 18
    d.rectangle([rx, ry, rx + w3, ry + 3], fill=RED)
    cx = rx
    for c in sub:
        d.text((cx, ry + 10), c, font=f2, fill=WHITE)
        cx += d.textlength(c, font=f2) + track

    # Headline box
    box = (36, 470, W - 36, 930)
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rectangle([box[0] + 6, box[1] + 14, box[2] + 6, box[3] + 14], fill=200)
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(18)))
    frame(img, box)
    d = ImageDraw.Draw(img)
    inner_w = box[2] - box[0] - 70
    txt = story["short_bn"].replace("  ", " ")
    for size in (128, 120, 112, 104, 98, 92, 86, 80):
        lines = [l.replace(" ", "  ") for l in wrap_balanced(d, txt, BN_HEAD, EN_BLACK, size, inner_w - 40)]
        if len(lines) <= 2 and all(width(d, l, BN_HEAD, EN_BLACK, size) <= inner_w for l in lines):
            break
    lh = int(size * 1.12)
    sub_size = 46
    block = len(lines) * lh + 52 + sub_size * 1.3
    y = box[1] + (box[3] - box[1] - block) / 2 + 4
    for i, ln in enumerate(lines):
        lw = width(d, ln, BN_HEAD, EN_BLACK, size)
        stops = SNOW if (i == 0 and len(lines) > 1) else FIRE
        grad_text(img, ((W - lw) / 2, y - size * 0.1), ln, size, stops)
        y += lh
    d = ImageDraw.Draw(img)
    y += 30
    bar = hgrad(220, 8, RED, YELLOW)
    img.paste(bar, (int(W / 2 - 110), int(y)))
    y += 22
    src = SRC_BN.get(story["source"], story["source"])
    lab, val = "সূত্র: ", src
    lw_ = width(d, lab, BN_SUB, EN_SEMI, sub_size)
    vw = width(d, val, BN_SUB, EN_SEMI, sub_size)
    sx = (W - lw_ - vw) / 2
    draw_runs(d, sx, y, lab, BN_SUB, EN_SEMI, sub_size, ORANGE)
    draw_runs(d, sx + lw_, y, val, BN_SUB, EN_SEMI, sub_size, WHITE)
    return img


def caption(story):
    src = SRC_BN.get(story["source"], story["source"])
    return (
        f"{story['title_bn']}\n\n"
        f"{story['caption_bn']}\n\n"
        f"📰 সূত্র: {src} (লিংক কমেন্টে 👇)\n\n"
        f"#Top10BreakingNews #BreakingNewsBD #আজকের_খবর"
    )


def first_comment(story):
    src = SRC_BN.get(story["source"], story["source"])
    return f"📰 বিস্তারিত পড়ুন ({src}):\n{story['url']}"


def main(src, out, page_name="Top 10 Breaking News"):
    data = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    st = data["stories"]
    caps = []
    for i, s in enumerate(st, 1):
        card(s, i, len(st), data["date_bn"], page_name).save(os.path.join(out, f"card_{i:02d}.jpg"), quality=92)
        caps.append({"rank": i, "image": f"card_{i:02d}.jpg", "caption": caption(s), "first_comment": first_comment(s)})
    json.dump(caps, open(os.path.join(out, "captions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(os.path.join(out, "captions.txt"), "w", encoding="utf-8") as f:
        for c in caps:
            f.write(f"===== POST {c['rank']:02d} ({c['image']}) =====\n{c['caption']}\n\n--- FIRST COMMENT ---\n{c['first_comment']}\n\n")
    print("rendered", len(st), "cards ->", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
