"""Illustrated (flat cartoon) symbolic scenes for news cards.

scene_airport_fire(phase) -> RGB image W x H. `phase` in [0, 1) animates the
flames/smoke so frames can be looped into a short video.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 1080, 1350
S = 2  # supersample for smooth edges

BLACK = (10, 8, 10)
RED = (226, 32, 28)
DEEP = (120, 12, 14)
ORANGE = (255, 120, 10)
YELLOW = (255, 214, 60)
CORE = (255, 246, 200)


def _sky(horizon):
    ys = np.linspace(0, 1, H)[:, None]
    h = horizon / H
    top, mid, low = np.array([16, 6, 10.]), np.array([120, 16, 16.]), np.array([255, 110, 20.])
    t1 = np.clip(ys / h, 0, 1)
    col = np.where(t1 < 0.6, top + (mid - top) * (t1 / 0.6), mid + (low - mid) * ((t1 - 0.6) / 0.4))
    col = np.where(ys > h, np.array([22, 10, 10.]), col)
    return Image.fromarray(np.repeat(col[:, None, :] if col.ndim == 2 else col, W, 1).astype("uint8")).resize((W * S, H * S))


def _flame_poly(cx, base, w, h, phase, seed, n=40):
    """Teardrop flame outline with wobbling tongues."""
    rnd = random.Random(seed)
    k1, k2 = rnd.uniform(2, 4), rnd.uniform(5, 8)
    pts = []
    for i in range(n + 1):
        t = i / n                       # 0 bottom-left -> 1 bottom-right around the top
        ang = math.pi * t
        r = math.sin(ang)
        y = base - h * (math.sin(ang) ** 0.6) * (1 - 0.35 * abs(math.cos(ang)))
        x = cx - w / 2 * math.cos(ang) * (1 - 0.2 * (1 - r))
        wob = math.sin(t * k1 * math.pi * 2 + phase * 2 * math.pi) * w * 0.08 + math.sin(t * k2 * math.pi + phase * 4 * math.pi) * w * 0.05
        x += wob
        pts.append((x, y))
    # pointed tongues at the top
    tip_x = cx + math.sin(phase * 2 * math.pi + seed) * w * 0.12
    pts.insert(n // 2, (tip_x, base - h * 1.12))
    return pts


def _fire(d, cx, base, w, h, phase, seed):
    for scale, col in ((1.0, RED), (0.78, ORANGE), (0.55, YELLOW), (0.3, CORE)):
        d.polygon([(x * S, y * S) for x, y in _flame_poly(cx, base, w * scale, h * scale, phase, seed)], fill=col)
    # side tongues
    for j, off in enumerate((-0.38, 0.36)):
        ph = phase + 0.3 * (j + 1)
        d.polygon([(x * S, y * S) for x, y in _flame_poly(cx + off * w, base, w * 0.45, h * (0.55 + 0.1 * math.sin(ph * 6.28)), ph, seed + j + 7)], fill=RED)
        d.polygon([(x * S, y * S) for x, y in _flame_poly(cx + off * w, base, w * 0.28, h * (0.35 + 0.08 * math.sin(ph * 6.28)), ph, seed + j + 7)], fill=ORANGE)


def _smoke(img, cx, base, phase, seed, reach=1000):
    rnd = random.Random(seed)
    m = Image.new("L", (W * S, H * S), 0)
    md = ImageDraw.Draw(m)
    for i in range(60):
        t = ((i / 60) + phase * 0.15) % 1
        x = cx + t * 260 + math.sin(t * 6 + seed) * 50 + rnd.uniform(-20, 20)
        y = base - t * reach
        r = 40 + t * 170
        md.ellipse([(x - r) * S, (y - r * 0.8) * S, (x + r) * S, (y + r * 0.8) * S], fill=int(230 * (1 - t * 0.7)))
    m = m.filter(ImageFilter.GaussianBlur(14 * S))
    return Image.composite(Image.new("RGB", m.size, (34, 24, 26)), img, m)


def _plane(d, x, y, sc, col, tilt=0):
    """Side-view airliner, nose to the right. (x, y) = nose tip."""
    def P(px, py):
        a = math.radians(tilt)
        rx = px * math.cos(a) - py * math.sin(a)
        ry = px * math.sin(a) + py * math.cos(a)
        return ((x + rx * sc) * S, (y + ry * sc) * S)
    body = [P(0, 0), P(-30, -16), P(-120, -24), P(-600, -24), P(-690, -14), P(-700, 4), P(-600, 10), P(-120, 14), P(-30, 10)]
    d.polygon(body, fill=col)
    d.polygon([P(-560, -24), P(-645, -150), P(-695, -150), P(-670, -14)], fill=col)   # tail fin
    d.polygon([P(-610, -6), P(-660, -6), P(-720, 26), P(-690, 26)], fill=col)         # tailplane
    d.polygon([P(-280, 6), P(-200, 6), P(-370, 74), P(-420, 74)], fill=col)          # wing
    d.rounded_rectangle([*P(-300, 18), *P(-225, 44)], radius=8 * S, fill=col)       # engine
    for k in range(14):                                                              # windows
        cx, cy = P(-140 - k * 28, -8)
        d.ellipse([cx - 5 * S, cy - 5 * S, cx + 5 * S, cy + 5 * S], fill=(255, 190, 90))
    for gx in (-170, -330):                                                          # gear
        a, b = P(gx, 14), P(gx, 40)
        d.line([a, b], fill=col, width=6 * S)
        d.ellipse([b[0] - 9 * S, b[1] - 9 * S, b[0] + 9 * S, b[1] + 9 * S], fill=col)


def scene_airport_fire(phase=0.0, seed=7):
    rnd = random.Random(seed)
    horizon = 1150
    flick = 0.85 + 0.15 * math.sin(phase * 2 * math.pi * 3)

    # ---- background: sky, distant city, smoke, fire glow ----
    bg = _sky(horizon).resize((W, H))
    d = ImageDraw.Draw(bg)
    x = -10
    while x < W:
        bw, bh = rnd.randint(40, 90), rnd.randint(40, 140)
        d.rectangle([x, horizon - 120 - bh, x + bw, horizon], fill=(80, 16, 16))
        x += bw + rnd.randint(0, 10)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for (gx, gy, r) in ((300, 600, 380), (300, 1000, 300), (760, 1150, 200)):
        gd.ellipse([gx - r, gy - r, gx + r, gy + r], fill=tuple(int(v * flick) for v in (170, 70, 10)))
    bg = ImageChops.add(bg, glow.filter(ImageFilter.GaussianBlur(90)))
    bg = bg.resize((W * S, H * S))
    bg = _smoke(bg, 260, 400, phase, 1, reach=600)        # thick smoke above the box
    bg = _smoke(bg, 640, 380, phase + 0.4, 2, reach=520)
    img = bg
    d = ImageDraw.Draw(img)

    # ---- the big fire: tall enough that its tongues rise above the headline box ----
    _fire(d, 300, 1040, 520, 980, phase, 3)
    _fire(d, 590, 1040, 260, 560, (phase + 0.5) % 1, 5)

    # ---- control tower ----
    tx = 900
    d.rectangle([(tx - 22) * S, 360 * S, (tx + 22) * S, horizon * S], fill=BLACK)
    d.polygon([((tx - 90) * S, 360 * S), ((tx + 90) * S, 360 * S), ((tx + 70) * S, 290 * S), ((tx - 70) * S, 290 * S)], fill=BLACK)
    d.rectangle([(tx - 76) * S, 298 * S, (tx + 76) * S, 350 * S], fill=(255, 196, 90))
    for k in range(-66, 76, 19):
        d.line([((tx + k) * S, 298 * S), ((tx + k) * S, 350 * S)], fill=BLACK, width=4 * S)
    d.polygon([((tx - 62) * S, 290 * S), ((tx + 62) * S, 290 * S), (tx * S, 250 * S)], fill=BLACK)
    d.line([(tx * S, 250 * S), (tx * S, 190 * S)], fill=BLACK, width=5 * S)
    blink = (255, 40, 40) if phase < 0.5 else (120, 20, 20)
    d.ellipse([(tx - 9) * S, 180 * S, (tx + 9) * S, 198 * S], fill=blink)

    # ---- terminal: black building, arched roof, glass panels ----
    d.chord([-60 * S, 960 * S, 880 * S, 1080 * S], 180, 360, fill=BLACK)
    d.rectangle([0, 1018 * S, 820 * S, horizon * S], fill=BLACK)
    for wx in range(24, 800, 64):
        lit = rnd.random() < 0.8
        d.rectangle([wx * S, 1050 * S, (wx + 52) * S, 1118 * S], fill=(255, 168, 60) if lit else (70, 22, 14))
        d.line([(wx + 26) * S, 1050 * S, (wx + 26) * S, 1118 * S], fill=BLACK, width=3 * S)
        d.line([wx * S, 1084 * S, (wx + 52) * S, 1084 * S], fill=BLACK, width=3 * S)
    # fire bursting out of the terminal front
    _fire(d, 300, 1130, 260, 200, (phase + 0.2) % 1, 11)

    # ---- tarmac with orange reflection ----
    ys = np.linspace(0, 1, (H - horizon) * S)[:, None, None]
    tar = (np.array([110, 40, 12.]) * (1 - ys) + np.array([24, 10, 10.]) * ys)
    img.paste(Image.fromarray(np.repeat(tar, W * S, 1).astype("uint8")), (0, horizon * S))
    d = ImageDraw.Draw(img)
    for k in range(0, W, 120):
        d.rectangle([(k + 20) * S, 1312 * S, (k + 90) * S, 1322 * S], fill=(255, 200, 80))
    for k in range(0, W + 1, 54):
        c = ORANGE if (k // 54 + int(phase * 4)) % 2 else (255, 60, 40)
        d.ellipse([(k - 5) * S, (horizon + 10) * S, (k + 5) * S, (horizon + 20) * S], fill=c)

    # ---- airliner on the apron, wing on fire ----
    _plane(d, 1070, 1238, 1.0, BLACK)
    _fire(d, 760, 1262, 170, 250, (phase + 0.25) % 1, 9)

    img = img.resize((W, H), Image.LANCZOS)

    # embers drifting up
    ed = ImageDraw.Draw(img)
    er = random.Random(seed + 99)
    for i in range(130):
        bx, sp = er.uniform(60, 960), er.uniform(0.6, 1.4)
        by = er.uniform(100, 1150)
        y = (by - phase * 400 * sp) % 1100 + 80
        x = bx + math.sin(phase * 6.28 * sp + i) * 20
        r = er.uniform(1.5, 4)
        ed.ellipse([x - r, y - r, x + r, y + r], fill=(255, er.randint(150, 230), 60))
    return img


def _india_gate(d, cx, top, base, col):
    """Simplified India Gate style memorial arch silhouette."""
    w = 380
    x0, x1 = cx - w / 2, cx + w / 2
    d.rectangle([x0 * S, (top + 60) * S, x1 * S, base * S], fill=col)
    d.rectangle([(x0 - 14) * S, (top + 40) * S, (x1 + 14) * S, (top + 70) * S], fill=col)   # cornice
    d.rectangle([(cx - 120) * S, top * S, (cx + 120) * S, (top + 44) * S], fill=col)       # attic
    d.rectangle([(cx - 80) * S, (top - 26) * S, (cx + 80) * S, top * S], fill=col)
    d.ellipse([(cx - 40) * S, (top - 52) * S, (cx + 40) * S, (top - 10) * S], fill=col)    # dome cap
    # the arch opening (glowing sky shows through)
    aw = 150
    d.rectangle([(cx - aw / 2) * S, (top + 260) * S, (cx + aw / 2) * S, base * S], fill=(255, 140, 40))
    d.pieslice([(cx - aw / 2) * S, (top + 185) * S, (cx + aw / 2) * S, (top + 335) * S], 180, 360, fill=(255, 140, 40))


def _person(d, x, base, h, col, fist=False, sign=None, flag=None, phase=0.0, k=0):
    """Back-view protester silhouette: head, shoulders, optional raised fist / placard / flag."""
    bob = math.sin(phase * 2 * math.pi * 2 + k) * 6
    hw = h * 0.22
    d.ellipse([(x - hw * 0.45) * S, (base - h) * S, (x + hw * 0.45) * S, (base - h + hw * 0.95) * S], fill=col)
    d.rounded_rectangle([(x - hw) * S, (base - h + hw * 0.8) * S, (x + hw) * S, (base + 40) * S], radius=int(hw * 0.6 * S), fill=col)
    if fist:
        ax, ay = x + hw * 0.7, base - h + hw
        fx, fy = ax + 18, ay - h * 0.42 + bob
        d.line([(ax * S, ay * S), (fx * S, fy * S)], fill=col, width=int(hw * 0.3 * S))
        d.ellipse([(fx - hw * 0.3) * S, (fy - hw * 0.35) * S, (fx + hw * 0.3) * S, (fy + hw * 0.25) * S], fill=col)
    if sign:
        sx, sy = x - hw * 0.2, base - h - h * 0.12 + bob
        d.line([(sx * S, (sy + 40) * S), (sx * S, (base - h + hw) * S)], fill=col, width=int(5 * S))
        sw, sh = h * 0.62, h * 0.38
        d.rectangle([(sx - sw / 2) * S, (sy - sh / 2) * S, (sx + sw / 2) * S, (sy + sh / 2) * S], fill=sign)
        d.rectangle([(sx - sw / 2) * S, (sy - sh / 2) * S, (sx + sw / 2) * S, (sy - sh / 2 + sh * 0.22) * S], fill=RED)
        for j in range(2):
            ly = sy - sh * 0.05 + j * sh * 0.24
            d.rectangle([(sx - sw * 0.35) * S, ly * S, (sx + sw * (0.35 - 0.2 * j)) * S, (ly + sh * 0.09) * S], fill=(40, 30, 30))
    if flag:
        px, py = x + hw * 0.2, base - h - h * 0.35
        d.line([(px * S, py * S), (px * S, (base - h + hw) * S)], fill=col, width=int(5 * S))
        pts = []
        for i in range(21):
            t = i / 20
            pts.append(((px + t * h * 0.75) * S, (py + math.sin(t * 5 + phase * 6.28 + k) * 10 * t) * S))
        bot = [(xx, yy + h * 0.42 * S) for xx, yy in reversed(pts)]
        d.polygon(pts + bot, fill=flag)


def scene_protest(phase=0.0, seed=21):
    """Street protest at dusk in front of a memorial arch: crowd, fists, placards, flags, smoke."""
    rnd = random.Random(seed)
    horizon = 1080
    bg = _sky(horizon).resize((W, H))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W / 2 - 420, 300, W / 2 + 420, 1100], fill=(160, 60, 10))
    bg = ImageChops.add(bg, glow.filter(ImageFilter.GaussianBlur(110)))
    bg = bg.resize((W * S, H * S))
    bg = _smoke(bg, 180, 700, phase, 4, reach=650)        # tear-gas haze drifting up
    bg = _smoke(bg, 820, 760, phase + 0.5, 5, reach=600)
    img = bg
    d = ImageDraw.Draw(img)
    # distant trees / skyline
    x = -20
    while x < W:
        r = rnd.randint(30, 70)
        d.ellipse([(x - r) * S, (horizon - 150 - r) * S, (x + r) * S, (horizon - 150 + r) * S], fill=(70, 16, 14))
        x += r
    d.rectangle([0, (horizon - 150) * S, W * S, horizon * S], fill=(70, 16, 14))
    _india_gate(d, W / 2, 150, horizon, (34, 10, 12))
    # street
    d.rectangle([0, horizon * S, W * S, H * S], fill=(26, 10, 10))
    # crowd: three rows, back to front
    signs = [(255, 236, 200), (255, 214, 120), (255, 255, 255)]
    flags = [ORANGE, (240, 240, 240), (30, 140, 70), RED]
    k = 0
    for row, (base, h, col, n) in enumerate([(1120, 150, (40, 12, 12), 12), (1210, 200, (24, 8, 8), 9), (1330, 270, BLACK, 6)]):
        step = W / n
        for i in range(n):
            px = step * (i + 0.5) + rnd.uniform(-20, 20)
            kind = rnd.random()
            _person(d, px, base, h, col,
                    fist=kind < 0.35,
                    sign=signs[k % 3] if 0.35 <= kind < 0.6 else None,
                    flag=flags[k % 4] if 0.6 <= kind < 0.75 else None,
                    phase=phase, k=k)
            k += 1
    img = img.resize((W, H), Image.LANCZOS)
    # floating embers / dust in the light
    ed = ImageDraw.Draw(img)
    er = random.Random(seed + 5)
    for i in range(70):
        bx, sp = er.uniform(0, W), er.uniform(0.5, 1.3)
        y = (er.uniform(100, 1000) - phase * 300 * sp) % 1000 + 80
        r = er.uniform(1.5, 3.2)
        ed.ellipse([bx - r, y - r, bx + r, y + r], fill=(255, er.randint(160, 230), 90))
    return img


SCENE_BUILDERS = {"airport_fire": scene_airport_fire, "protest": scene_protest}
