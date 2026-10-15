"""More illustrated, animated themes for news cards.

Every builder takes (phase, seed) and returns an RGB W x H image.
`phase` in [0, 1) loops: the same scene at phase 0 and phase 1.
Busy detail is placed in the top band (y < 470) and the bottom band (y > 930),
because the headline box covers the middle of the card.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scenes import W, H, S, BLACK, RED, ORANGE, YELLOW, CORE, _fire, _smoke, _plane

TAU = 2 * math.pi


# ---------------------------------------------------------------- helpers
def vgrad(stops, w=W, h=H):
    """Vertical gradient; stops = [(t, (r,g,b)), ...]."""
    t = np.linspace(0, 1, h)
    col = np.zeros((h, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        k = np.clip((t - t0) / max(t1 - t0, 1e-6), 0, 1)
        for i in range(3):
            col[:, i] = np.where(m, c0[i] + (c1[i] - c0[i]) * k, col[:, i])
    return Image.fromarray(np.repeat(col[:, None, :], w, 1).astype("uint8"))


def glow(img, spots, blur=90):
    """Add soft light blobs: spots = [(x, y, r, (r,g,b)), ...] in 1x coords."""
    g = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(g)
    for x, y, r, c in spots:
        gd.ellipse([x - r, y - r, x + r, y + r], fill=c)
    g = g.filter(ImageFilter.GaussianBlur(blur))
    if img.size != (W, H):
        g = g.resize(img.size)
    return ImageChops.add(img, g)


def sparks(img, phase, seed, n=80, y0=80, y1=1300, col=(255, 200, 90), speed=350):
    d = ImageDraw.Draw(img)
    r_ = random.Random(seed)
    span = y1 - y0
    for i in range(n):
        x, sp = r_.uniform(0, W), r_.uniform(0.5, 1.4)
        y = (r_.uniform(0, span) - phase * speed * sp) % span + y0
        x += math.sin(phase * TAU * sp + i) * 15
        r = r_.uniform(1.4, 3.4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(col[0], max(0, col[1] - r_.randint(0, 60)), col[2]))
    return img


def P(*xy):
    return [v * S for v in xy]


def up(img):
    return img.resize((W * S, H * S))


def down(img):
    return img.resize((W, H), Image.LANCZOS)


def skyline(d, base, hmin, hmax, col, seed, domes=True):
    r_ = random.Random(seed)
    x = -20
    while x < W + 20:
        bw, bh = r_.randint(40, 100), r_.randint(hmin, hmax)
        d.rectangle(P(x, base - bh, x + bw, base + 10), fill=col)
        if domes and r_.random() < 0.18:
            d.ellipse(P(x + 6, base - bh - bw * 0.4, x + bw - 6, base - bh + bw * 0.4), fill=col)
        elif r_.random() < 0.15:
            d.polygon(P(x + bw / 2 - 5, base - bh, x + bw / 2, base - bh - r_.randint(40, 90), x + bw / 2 + 5, base - bh), fill=col)
        x += bw - r_.randint(0, 10)


# ---------------------------------------------------------------- war / missiles
def scene_war(phase=0.0, seed=31):
    """Night sky with missile trails and interceptions over a city; burning skyline below."""
    img = vgrad([(0, (8, 6, 16)), (0.55, (60, 12, 20)), (0.85, (200, 60, 20)), (1, (40, 10, 8))])
    img = glow(img, [(300, 1100, 300, (180, 60, 10)), (800, 1150, 260, (160, 50, 10))])
    img = up(img)
    img = _smoke(img, 230, 1000, phase, 3, reach=800)
    img = _smoke(img, 760, 1050, phase + 0.5, 4, reach=700)
    d = ImageDraw.Draw(img)
    r_ = random.Random(seed)
    # missile trails: curved arcs across the top band, head moves with phase
    for k in range(4):
        sx, sy = r_.uniform(-100, 300), r_.uniform(300, 450)
        ex, ey = r_.uniform(600, 1150), r_.uniform(60, 250)
        cxp, cyp = (sx + ex) / 2, min(sy, ey) - r_.uniform(80, 200)
        prog = (phase + k / 4) % 1
        pts = []
        for i in range(41):
            t = prog * i / 40
            x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cxp + t ** 2 * ex
            y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cyp + t ** 2 * ey
            pts.append((x * S, y * S))
        if len(pts) > 1:
            d.line(pts, fill=(255, 220, 160), width=3 * S)
            hx, hy = pts[-1]
            d.ellipse([hx - 9 * S, hy - 9 * S, hx + 9 * S, hy + 9 * S], fill=(255, 250, 220))
    # flashes (interceptions) in the sky
    for k in range(3):
        fx, fy = r_.uniform(100, 980), r_.uniform(90, 380)
        a = max(0.0, math.sin((phase + k * 0.33) * TAU))
        rr = 20 + 60 * a
        d.ellipse([(fx - rr) * S, (fy - rr) * S, (fx + rr) * S, (fy + rr) * S], fill=(255, int(180 + 60 * a), 80))
    # city skyline with burning spots
    skyline(d, 1180, 80, 260, (20, 8, 10), seed)
    d.rectangle(P(0, 1180, W, H), fill=(18, 8, 8))
    _fire(d, 260, 1150, 160, 260, phase, 5)
    _fire(d, 820, 1170, 120, 200, (phase + 0.4) % 1, 6)
    img = down(img)
    return sparks(img, phase, seed + 1, n=70)


# ---------------------------------------------------------------- football
def scene_football(phase=0.0, seed=41):
    """Stadium at night: floodlight beams, crowd flashes, pitch and a ball in flight."""
    img = vgrad([(0, (10, 6, 12)), (0.6, (70, 14, 16)), (0.8, (20, 70, 30)), (1, (10, 40, 18))])
    img = glow(img, [(150, 230, 220, (200, 120, 40)), (930, 230, 220, (200, 120, 40))], blur=70)
    img = up(img)
    d = ImageDraw.Draw(img)
    # floodlight towers + beams
    beams = Image.new("L", img.size, 0)
    bd = ImageDraw.Draw(beams)
    for lx in (140, 940):
        sw = math.sin(phase * TAU) * 40
        bd.polygon(P(lx - 40, 250, lx + 40, 250, W / 2 + 260 + sw, 1300, W / 2 - 260 + sw, 1300), fill=60)
        d.rectangle(P(lx - 10, 250, lx + 10, 470), fill=(20, 10, 12))
        d.rectangle(P(lx - 70, 200, lx + 70, 260), fill=(30, 14, 16))
        for i in range(5):
            for j in range(2):
                d.ellipse(P(lx - 62 + i * 26, 206 + j * 26, lx - 44 + i * 26, 224 + j * 26), fill=(255, 245, 200))
    img = Image.composite(Image.new("RGB", img.size, (255, 230, 170)), img, beams.filter(ImageFilter.GaussianBlur(20 * S)))
    d = ImageDraw.Draw(img)
    # crowd stands: rows of dots with camera flashes
    r_ = random.Random(seed)
    for row in range(6):
        y = 960 + row * 22
        for x in range(0, W, 14):
            flash = r_.random() < 0.02 and (int(phase * 12) + x) % 5 == 0
            c = (255, 255, 230) if flash else (60 + r_.randint(0, 50), 18, 20)
            d.ellipse(P(x, y, x + 9, y + 9), fill=c)
    # pitch
    d.polygon(P(0, 1110, W, 1110, W, H, 0, H), fill=(22, 110, 40))
    for i in range(6):
        d.polygon(P(i * 200 - 60, 1110, i * 200 + 40, 1110, i * 260 - 20, H, i * 260 - 150, H), fill=(26, 124, 46))
    d.line(P(0, 1180, W, 1180), fill=(220, 240, 220), width=4 * S)
    d.ellipse(P(W / 2 - 160, 1150, W / 2 + 160, 1230), outline=(220, 240, 220), width=4 * S)
    # goal on the right
    d.rectangle(P(860, 1060, 1060, 1180), outline=(240, 240, 240), width=6 * S)
    for k in range(9):
        d.line(P(860 + k * 25, 1060, 860 + k * 25, 1180), fill=(200, 200, 200), width=1 * S)
    # ball flying toward goal (top band arc -> goal)
    t = phase
    bx = 120 + t * 840
    by = 1160 - math.sin(t * math.pi) * 760
    br = 34
    d.ellipse(P(bx - br, by - br, bx + br, by + br), fill=(250, 250, 250))
    for a in range(5):
        ang = a * TAU / 5 + phase * TAU
        px, py = bx + math.cos(ang) * br * 0.55, by + math.sin(ang) * br * 0.55
        d.ellipse(P(px - 8, py - 8, px + 8, py + 8), fill=(20, 20, 20))
    img = down(img)
    return sparks(img, phase, seed, n=40, y0=60, y1=470, col=(255, 230, 150))


# ---------------------------------------------------------------- cricket
def scene_cricket(phase=0.0, seed=51):
    """Cricket ground at dusk: floodlights, stumps, bat and a ball flying for six."""
    img = vgrad([(0, (16, 8, 14)), (0.55, (150, 40, 20)), (0.78, (255, 130, 40)), (0.8, (40, 100, 40)), (1, (20, 60, 24))])
    img = up(img)
    d = ImageDraw.Draw(img)
    skyline(d, 1080, 30, 90, (60, 14, 14), seed, domes=False)
    # stands
    d.rectangle(P(0, 1000, W, 1080), fill=(50, 12, 14))
    r_ = random.Random(seed)
    for x in range(0, W, 12):
        for row in range(3):
            if r_.random() < 0.8:
                d.ellipse(P(x, 1010 + row * 22, x + 8, 1018 + row * 22), fill=(110 + r_.randint(0, 60), 30, 24))
    # field + pitch strip
    d.rectangle(P(0, 1080, W, H), fill=(30, 110, 40))
    d.polygon(P(W / 2 - 70, 1080, W / 2 + 70, 1080, W / 2 + 160, H, W / 2 - 160, H), fill=(196, 170, 110))
    # stumps
    for k in (-28, 0, 28):
        d.rectangle(P(W / 2 + k - 7, 1150, W / 2 + k + 7, 1290), fill=(250, 236, 200))
    d.rectangle(P(W / 2 - 36, 1146, W / 2 + 36, 1154), fill=(250, 236, 200))
    # bat (swinging)
    ang = math.radians(-60 + 90 * (0.5 + 0.5 * math.sin(phase * TAU)))
    bx0, by0 = W / 2 + 140, 1180
    L = 240
    bx1, by1 = bx0 + math.cos(ang) * L, by0 + math.sin(ang) * L
    d.line(P(bx0, by0, bx1, by1), fill=(230, 200, 140), width=30 * S)
    d.line(P(bx0, by0, bx0 + math.cos(ang) * 70, by0 + math.sin(ang) * 70), fill=(30, 20, 20), width=12 * S)
    # ball soaring into the sky (top band)
    t = phase
    x = W / 2 + 120 - t * 700
    y = 1150 - math.sin(min(t, 1) * math.pi * 0.9) * 1000
    d.ellipse(P(x - 22, y - 22, x + 22, y + 22), fill=(210, 30, 30))
    d.arc(P(x - 22, y - 22, x + 22, y + 22), 200, 340, fill=(255, 240, 220), width=3 * S)
    # floodlights
    for lx in (90, 990):
        d.rectangle(P(lx - 8, 240, lx + 8, 470), fill=(24, 10, 12))
        d.rectangle(P(lx - 60, 200, lx + 60, 250), fill=(255, 240, 200))
    img = down(img)
    img = glow(img, [(90, 225, 120, (160, 120, 60)), (990, 225, 120, (160, 120, 60))], blur=50)
    return sparks(img, phase, seed, n=40, y0=60, y1=470, col=(255, 230, 160))


# ---------------------------------------------------------------- economy / growth
def scene_economy(phase=0.0, seed=61):
    """Rising bar chart, an upward arrow and falling coins on a dark grid."""
    img = vgrad([(0, (14, 8, 10)), (0.6, (60, 14, 14)), (1, (120, 40, 10))])
    img = up(img)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 60):
        d.line(P(x, 0, x, H), fill=(40, 14, 16), width=1 * S)
    for y in range(0, H, 60):
        d.line(P(0, y, W, y), fill=(40, 14, 16), width=1 * S)
    # bars in the bottom band, growing with phase
    n = 9
    grow = 0.85 + 0.15 * math.sin(phase * TAU)
    for i in range(n):
        h = (120 + i * 38) * grow
        x = 60 + i * 110
        c = ORANGE if i % 2 else RED
        d.rectangle(P(x, 1330 - h, x + 70, 1330), fill=c)
        d.rectangle(P(x, 1330 - h, x + 70, 1330 - h + 10), fill=YELLOW)
    # rising arrow line across the top band
    pts = []
    for i in range(10):
        x = 40 + i * 78
        y = 430 - i * 26 + (25 if i % 2 else -10)
        pts.append((x, y))
    d.line([(x * S, y * S) for x, y in pts], fill=(255, 220, 120), width=10 * S, joint="curve")
    ex, ey = pts[-1]
    d.polygon(P(ex + 40, ey - 30, ex - 20, ey - 40, ex + 10, ey + 20), fill=(255, 220, 120))
    # coins drifting down
    r_ = random.Random(seed)
    for k in range(14):
        cx = r_.uniform(40, W - 40)
        cy = (r_.uniform(0, 470) + phase * 470) % 470
        if cx > 780 and cy < 190:
            cy += 200
        rr = r_.uniform(16, 30)
        squash = abs(math.cos(phase * TAU * 2 + k))
        d.ellipse(P(cx - rr * squash - 2, cy - rr, cx + rr * squash + 2, cy + rr), fill=YELLOW)
        d.ellipse(P(cx - rr * squash * 0.6, cy - rr * 0.6, cx + rr * squash * 0.6, cy + rr * 0.6), outline=ORANGE, width=3 * S)
    img = down(img)
    return glow(img, [(820, 220, 200, (120, 80, 20))], blur=80)


# ---------------------------------------------------------------- USA politics
def scene_usa(phase=0.0, seed=71):
    """Domed capitol silhouette, waving stripes and twinkling stars."""
    img = vgrad([(0, (8, 10, 30)), (0.5, (60, 16, 40)), (0.85, (220, 70, 30)), (1, (30, 10, 10))])
    img = up(img)
    d = ImageDraw.Draw(img)
    r_ = random.Random(seed)
    # stars in the top band
    for k in range(40):
        x, y = r_.uniform(0, W), r_.uniform(20, 440)
        tw = 0.5 + 0.5 * math.sin(phase * TAU * 2 + k)
        rr = 2 + 4 * tw
        d.polygon([((x + rr * math.cos(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45)) * S,
                    (y + rr * math.sin(a * math.pi / 5 - math.pi / 2) * (1 if a % 2 == 0 else 0.45)) * S) for a in range(10)],
                  fill=(255, 250, 230))
    # waving stripes across the top band
    for i in range(7):
        pts_t, pts_b = [], []
        for xi in range(0, W + 1, 20):
            wv = math.sin(xi / 140 + phase * TAU + i * 0.3) * 18
            y = 190 + i * 40 + wv
            pts_t.append((xi * S, y * S))
            pts_b.append((xi * S, (y + 20) * S))
        d.polygon(pts_t + list(reversed(pts_b)), fill=(200, 30, 40) if i % 2 == 0 else (250, 240, 235))
    ov = Image.new("RGB", img.size, (8, 10, 30))
    img = Image.blend(img, ov, 0.35)
    d = ImageDraw.Draw(img)
    # capitol building at the bottom band
    cx, base = W / 2, 1290
    col = (16, 8, 14)
    d.rectangle(P(cx - 460, base - 120, cx + 460, base), fill=col)
    d.rectangle(P(cx - 200, base - 220, cx + 200, base - 110), fill=col)
    d.rectangle(P(cx - 120, base - 300, cx + 120, base - 210), fill=col)
    d.pieslice(P(cx - 120, base - 420, cx + 120, base - 180), 180, 360, fill=col)
    d.rectangle(P(cx - 14, base - 470, cx + 14, base - 400), fill=col)
    for k in range(-8, 9):
        d.rectangle(P(cx + k * 50 - 6, base - 110, cx + k * 50 + 6, base - 20), fill=(220, 120, 50))
    d.rectangle(P(0, base, W, H), fill=(14, 6, 8))
    img = down(img)
    return glow(img, [(W / 2, 1150, 300, (150, 60, 20))])


# ---------------------------------------------------------------- world / diplomacy
def scene_world(phase=0.0, seed=81):
    """Rotating globe with glowing connection arcs between cities."""
    img = vgrad([(0, (8, 6, 16)), (0.5, (40, 10, 20)), (1, (90, 20, 10))])
    img = up(img)
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, 1230, 520     # globe rises from the bottom
    d.ellipse(P(cx - R, cy - R, cx + R, cy + R), fill=(30, 14, 20), outline=(255, 120, 40), width=4 * S)
    # meridians that rotate
    for k in range(8):
        a = (k / 8 + phase / 8) * math.pi
        rx = abs(math.cos(a)) * R
        d.ellipse(P(cx - rx, cy - R, cx + rx, cy + R), outline=(120, 40, 30), width=2 * S)
    for k in range(1, 6):
        yy = cy - R + k * R / 3
        hw = math.sqrt(max(0, R ** 2 - (yy - cy) ** 2))
        d.line(P(cx - hw, yy, cx + hw, yy), fill=(120, 40, 30), width=2 * S)
    # connection arcs across the top band
    r_ = random.Random(seed)
    nodes = [(r_.uniform(80, W - 80), r_.uniform(120, 440)) for _ in range(6)]
    for i in range(len(nodes)):
        a, b = nodes[i], nodes[(i + 2) % len(nodes)]
        mx, my = (a[0] + b[0]) / 2, min(a[1], b[1]) - 120
        pts = []
        for j in range(31):
            t = j / 30
            pts.append((((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t ** 2 * b[0]) * S,
                        ((1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t ** 2 * b[1]) * S))
        d.line(pts, fill=(255, 150, 60), width=2 * S)
        t = (phase + i / 6) % 1
        px = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t ** 2 * b[0]
        py = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t ** 2 * b[1]
        d.ellipse(P(px - 7, py - 7, px + 7, py + 7), fill=(255, 240, 200))
    for x, y in nodes:
        pul = 8 + 6 * math.sin(phase * TAU * 2 + x)
        d.ellipse(P(x - pul, y - pul, x + pul, y + pul), fill=YELLOW)
    img = down(img)
    return glow(img, [(W / 2, 1000, 380, (140, 50, 10))])


# ---------------------------------------------------------------- bridge / development (good news)
def scene_bridge(phase=0.0, seed=91):
    """Sunrise over a river: cable-stayed bridge with a train crossing. Hopeful, warm."""
    img = vgrad([(0, (40, 10, 30)), (0.4, (200, 60, 40)), (0.7, (255, 170, 60)), (0.72, (120, 50, 20)), (1, (30, 20, 30))])
    img = glow(img, [(W / 2, 980, 260, (255, 200, 90))], blur=60)
    img = up(img)
    d = ImageDraw.Draw(img)
    # sun
    d.ellipse(P(W / 2 - 120, 860, W / 2 + 120, 1100), fill=(255, 230, 150))
    # river shimmer
    for k in range(18):
        y = 1000 + k * 20
        off = math.sin(phase * TAU + k) * 30
        d.line(P(W / 2 - 200 + off - k * 10, y, W / 2 + 200 + off + k * 10, y), fill=(255, 200, 120), width=3 * S)
    # pylons (tall, so their tops rise into the top band)
    col = (24, 10, 14)
    for px in (260, 820):
        d.polygon(P(px - 30, 1080, px + 30, 1080, px + 8, 200, px - 8, 200), fill=col)
        for k in range(10):
            d.line(P(px, 260 + k * 60, px - 260 + k * 8, 1050), fill=col, width=2 * S)
            d.line(P(px, 260 + k * 60, px + 260 - k * 8, 1050), fill=col, width=2 * S)
    d.rectangle(P(0, 1050, W, 1080), fill=col)
    # train crossing
    tx = (phase * (W + 600)) - 600
    for c in range(4):
        x0 = tx + c * 150
        d.rounded_rectangle(P(x0, 1005, x0 + 140, 1050), radius=10 * S, fill=(40, 16, 20))
        for w_ in range(4):
            d.rectangle(P(x0 + 12 + w_ * 32, 1015, x0 + 34 + w_ * 32, 1032), fill=(255, 210, 120))
    # birds
    for k in range(6):
        bx = (k * 170 + phase * 300) % W
        by = 120 + (k % 3) * 60 + math.sin(phase * TAU + k) * 10
        d.line(P(bx - 16, by - 8, bx, by, bx + 16, by - 8), fill=col, width=3 * S)
    return sparks(down(img), phase, seed, n=30, y0=60, y1=470, col=(255, 230, 170), speed=150)


# ---------------------------------------------------------------- abstract fallback
def scene_abstract(phase=0.0, seed=1):
    """Brand abstract: rotating rays, hexagon grid, flowing waves. Varies by seed."""
    r_ = random.Random(seed)
    hues = [((30, 6, 10), (180, 30, 30), (255, 120, 20)), ((14, 6, 20), (120, 20, 60), (255, 90, 40)),
            ((20, 8, 6), (170, 60, 10), (255, 180, 40))]
    a, b, c = hues[seed % 3]
    img = vgrad([(0, a), (0.5, b), (1, a)])
    img = up(img)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 700
    rays = Image.new("L", img.size, 0)
    rd = ImageDraw.Draw(rays)
    for k in range(18):
        ang = k * TAU / 18 + phase * TAU / 18
        rd.polygon(P(cx, cy, cx + math.cos(ang - 0.06) * 1600, cy + math.sin(ang - 0.06) * 1600,
                     cx + math.cos(ang + 0.06) * 1600, cy + math.sin(ang + 0.06) * 1600), fill=40)
    img = Image.composite(Image.new("RGB", img.size, c), img, rays.filter(ImageFilter.GaussianBlur(6 * S)))
    d = ImageDraw.Draw(img)
    # hexagon grid that pulses
    hs = 46
    for row in range(-1, 32):
        for col in range(-1, 14):
            hx = col * hs * 1.75 + (row % 2) * hs * 0.87
            hy = row * hs * 1.5
            if 470 < hy < 930:
                continue
            pul = 0.5 + 0.5 * math.sin(phase * TAU + (hx + hy) / 200 + seed)
            if pul < 0.55:
                continue
            pts = [((hx + hs * 0.8 * math.cos(math.pi / 3 * i + math.pi / 6)) * S,
                    (hy + hs * 0.8 * math.sin(math.pi / 3 * i + math.pi / 6)) * S) for i in range(6)]
            d.polygon(pts, outline=c, width=2 * S)
    # flowing waves at the bottom
    for k in range(5):
        pts = []
        for xi in range(0, W + 1, 15):
            y = 1050 + k * 50 + math.sin(xi / 120 + phase * TAU + k) * 30
            pts.append((xi * S, y * S))
        d.line(pts, fill=(255, 160 - k * 20, 60), width=(4 - k // 2) * S)
    return sparks(down(img), phase, seed, n=60)


SCENE_BUILDERS2 = {
    "war": scene_war,
    "football": scene_football,
    "cricket": scene_cricket,
    "economy": scene_economy,
    "usa": scene_usa,
    "world": scene_world,
    "bridge": scene_bridge,
    "abstract": scene_abstract,
}
