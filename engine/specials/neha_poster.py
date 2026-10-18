"""Neha Bora concept poster: red watercolour protest scene, a faceless silhouette that suggests her look
(hair tied back, black glasses, orange kurta with white flower print, furry stage mic), quote headline.
No real photo, no real face.

Usage: python3 specials/neha_poster.py <out_dir>   (run from engine/)
"""
import math, os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import render3 as r

W, H = 1080, 1350
HEAD = ["‘আটকই এখন আমার", "বিশ্রামের সময়’"]
SUB = ["বারবার আটক হয়েও রাজপথ ছাড়েননি,", "দিল্লির তরুণ আন্দোলনের মুখ নেহা বোরা"]
BY = "— নেহা বোরা, ভারতের ছাত্রনেত্রী"
SRC = "সূত্র:  দ্য  নিউজ  মিনিট"


def watercolor_bg(seed=7):
    rng = random.Random(seed)
    img = Image.new("RGB", (W, H), (205, 22, 28))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cols = [(235, 45, 40), (175, 8, 20), (250, 95, 60), (150, 0, 18), (255, 130, 90), (215, 30, 60)]
    for _ in range(420):
        x, y = rng.uniform(-80, W + 80), rng.uniform(-80, H + 80)
        rr = rng.uniform(25, 150)
        c = rng.choice(cols)
        d.ellipse([x - rr, y - rr * rng.uniform(.6, 1.2), x + rr, y + rr * rng.uniform(.6, 1.2)], fill=c + (55,))
    img.paste(lay.filter(ImageFilter.GaussianBlur(16)), (0, 0), lay.filter(ImageFilter.GaussianBlur(16)))
    return img


def paper(seed=3):
    rs = np.random.default_rng(seed)
    n = rs.normal(0, 1, (H // 3, W // 3)).astype(np.float32)
    im = Image.fromarray(np.uint8(np.clip(128 + n * 30, 0, 255))).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(im, np.float32) / 255
    return 0.88 + 0.24 * a          # multiplier around 1


def crowd(phase):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = random.Random(11)
    tones = [(235, 160, 150), (200, 120, 120), (150, 120, 140), (240, 190, 170), (120, 90, 110), (210, 170, 150)]
    for row, (y0, sc, alpha) in enumerate([(640, .8, 120), (760, 1.0, 165)]):
        for i in range(9):
            x = 40 + i * 125 + rng.uniform(-30, 30) + row * 55
            if 380 < x < 700 and row == 1:
                continue
            c = rng.choice(tones)
            police = rng.random() < .25
            if police:
                c = (170, 150, 110)
            hr = 42 * sc
            bob = 6 * math.sin(2 * math.pi * (phase + i * .13))
            hy = y0 + bob
            d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=c + (alpha,))
            d.rounded_rectangle([x - hr * 2.1, hy + hr * .9, x + hr * 2.1, H], radius=int(hr), fill=c + (alpha,))
            if police:
                d.rectangle([x - hr * 1.1, hy - hr * 1.15, x + hr * 1.1, hy - hr * .55], fill=(110, 95, 70, alpha))
            elif rng.random() < .55:          # raised fist or flag
                ax = x + hr * 1.6
                top = hy - hr * 3.2 + 10 * math.sin(2 * math.pi * (phase * 2 + i * .21))
                d.line([ax, hy + hr, ax + 10, top], fill=c + (alpha,), width=int(hr * .6))
                if rng.random() < .5:
                    d.ellipse([ax - hr * .45, top - hr * .5, ax + hr * .65, top + hr * .5], fill=c + (alpha,))
                else:
                    pts = []
                    for k in range(13):
                        t = k / 12
                        pts.append((ax + 10 + t * 150, top + 18 * math.sin(2 * math.pi * (t * 1.2 - phase * 2))))
                    pts += [(px, py + 85) for px, py in reversed(pts)]
                    d.polygon(pts, fill=(185, 15, 25, alpha + 40))
                    d.line([ax + 10, top - 10, ax + 10, top + 180], fill=(80, 50, 50, alpha), width=5)
    return lay.filter(ImageFilter.GaussianBlur(3))


def flower(d, x, y, s, col=(255, 248, 235)):
    for k in range(6):
        a = k * math.pi / 3
        px, py = x + math.cos(a) * s * .55, y + math.sin(a) * s * .55
        d.ellipse([px - s * .32, py - s * .32, px + s * .32, py + s * .32], fill=col)
    d.ellipse([x - s * .22, y - s * .22, x + s * .22, y + s * .22], fill=(200, 70, 30))


def figure(phase):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = 540
    sway = 6 * math.sin(2 * math.pi * phase)
    kurta = (226, 92, 34)
    # body / kurta
    body = [(cx - 330, H), (cx - 300, 1050), (cx - 240, 975), (cx - 120, 945), (cx + 120, 945), (cx + 240, 975),
            (cx + 300, 1050), (cx + 330, H)]
    d.polygon(body, fill=kurta)
    # square neckline (skin in shadow)
    skin = (96, 58, 44)
    d.rectangle([cx - 70 + sway, 860, cx + 70 + sway, 930], fill=skin)                 # neck
    d.polygon([(cx - 120, 945), (cx + 120, 945), (cx + 105, 1040), (cx - 105, 1040)], fill=skin)
    # white flower print
    rng = random.Random(5)
    msk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(msk).polygon(body, fill=255)
    ImageDraw.Draw(msk).polygon([(cx - 120, 945), (cx + 120, 945), (cx + 105, 1040), (cx - 105, 1040)], fill=0)
    pr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pr)
    for yy in range(960, H + 40, 62):
        for xx in range(cx - 360, cx + 380, 70):
            off = 35 if (yy // 62) % 2 else 0
            flower(pd, xx + off + rng.uniform(-6, 6), yy + rng.uniform(-6, 6), 30)
    lay.paste(pr, (0, 0), ImageChops.multiply(pr.split()[3], msk))
    d = ImageDraw.Draw(lay)
    # head: faceless shadow
    hx = cx + sway
    d.ellipse([hx - 105, 600, hx + 105, 870], fill=(88, 52, 40))
    # hair: dark, pulled back, loose strands at the sides and a bun behind
    hair = (24, 16, 16)
    d.chord([hx - 120, 570, hx + 120, 800], 180, 360, fill=hair)
    d.ellipse([hx - 125, 610, hx - 70, 820], fill=hair)
    d.ellipse([hx + 70, 640, hx + 120, 780], fill=hair)
    d.ellipse([hx - 190, 690, hx - 95, 800], fill=hair)              # bun / tie at the back
    for k in range(5):                                                # loose strands
        y = 780 + k * 14
        d.arc([hx - 160 + k * 6, y - 40, hx - 90, y + 60], 90, 200, fill=hair, width=6)
    # glasses: thick black rectangular frames
    gy = 715
    for gx in (hx - 82, hx + 8):
        d.rounded_rectangle([gx, gy, gx + 74, gy + 56], radius=16, outline=(12, 12, 14), width=11)
        d.line([gx + 14, gy + 14, gx + 30, gy + 10], fill=(255, 255, 255, 120), width=4)
    d.line([hx - 8, gy + 20, hx + 8, gy + 20], fill=(12, 12, 14), width=8)
    d.line([hx - 82, gy + 18, hx - 104, gy + 12], fill=(12, 12, 14), width=8)
    d.line([hx + 82, gy + 18, hx + 104, gy + 12], fill=(12, 12, 14), width=8)
    # stage mic with furry windscreen on a stand, in front at the right
    mx, my = cx + 175, 905
    d.line([mx + 20, my + 40, mx + 70, H], fill=(20, 20, 22), width=14)       # stand
    d.line([mx + 20, my + 40, mx - 30, my - 5], fill=(30, 30, 32), width=22)  # mic body
    fr = random.Random(2)
    for _ in range(140):                                                       # fur
        a, rr = fr.uniform(0, 2 * math.pi), fr.uniform(0, 46)
        px, py = mx - 55 + math.cos(a) * rr, my - 25 + math.sin(a) * rr * .8
        g = fr.randint(120, 190)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(g, g, g))
    return lay


def painterly(img):
    m = img.filter(ImageFilter.ModeFilter(7))
    m = Image.blend(m, m.filter(ImageFilter.GaussianBlur(2.5)), .45)
    edges = img.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.5))
    e = np.asarray(edges, np.float32) / 255
    a = np.asarray(m, np.float32) * (1 - 0.35 * e[..., None])
    return Image.fromarray(np.uint8(np.clip(a, 0, 255)))


def logo_pill(img):
    d = ImageDraw.Draw(img)
    f1 = r.font(r.OSWALD, 54)
    f2 = r.font(r.EN_BLACK, 26)
    w_top = d.textlength("TOP", font=f1)
    w_10 = d.textlength("10", font=f1)
    w_sub = d.textlength("BREAKING NEWS BD", font=f2)
    pw = 30 + w_top + 12 + w_10 + 24 + 22 + w_sub + 34
    x0, y0, h = W - pw - 40, 40, 84
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + h], radius=42, fill=(255, 255, 255))
    x = x0 + 30
    d.text((x, y0 + 6), "TOP", font=f1, fill=(12, 10, 12))
    x += w_top + 12
    d.rounded_rectangle([x - 2, y0 + 16, x + w_10 + 22, y0 + h - 14], radius=8, fill=r.ORANGE)
    d.text((x + 9, y0 + 6), "10", font=f1, fill=(12, 10, 12))
    x += w_10 + 24 + 22
    d.text((x, y0 + 27), "BREAKING NEWS BD", font=f2, fill=r.RED)


def text_shadow(img, draw_fn, blur=10, strength=200):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(sh), (0, 0, 0, 255))
    a = sh.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, v * strength // 255))
    img.paste((0, 0, 0), (0, 0), a)


def poster(phase=0.0):
    bg = watercolor_bg()
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sc.alpha_composite(crowd(phase))
    sc.alpha_composite(figure(phase))
    # fade the scene into the red at the top
    fade = Image.new("L", (1, H), 0)
    for y in range(H):
        fade.putpixel((0, y), int(255 * min(1, max(0, (y - 520) / 220))))
    sc.putalpha(ImageChops.multiply(sc.split()[3], fade.resize((W, H))))
    img = bg.copy()
    img.paste(sc, (0, 0), sc)
    img = painterly(img)
    a = np.asarray(img, np.float32) * paper()[..., None]
    img = Image.fromarray(np.uint8(np.clip(a, 0, 255)))
    # bottom dark gradient for the byline
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        grad.putpixel((0, y), int(200 * min(1, max(0, (y - 1180) / 140))))
    img.paste((10, 6, 8), (0, 0), grad.resize((W, H)))
    logo_pill(img)
    d = ImageDraw.Draw(img)
    # headline
    for size in range(120, 70, -2):
        if r.width(d, HEAD.replace(" ", "  "), r.BN_HEAD, r.EN_BLACK, size) <= W - 90:
            break
    head = HEAD.replace(" ", "  ")
    hw = r.width(d, head, r.BN_HEAD, r.EN_BLACK, size)
    hy = 190
    text_shadow(img, lambda dd, f: r.draw_runs(dd, (W - hw) / 2, hy, head, r.BN_HEAD, r.EN_BLACK, size, f))
    r.grad_text(img, ((W - hw) / 2, hy - size * 0.1), head, size, r.SNOW)
    d = ImageDraw.Draw(img)
    y = hy + size * 1.35
    for ln in SUB:
        ln2 = ln.replace(" ", "  ")
        lw = r.width(d, ln2, r.BN_SUB, r.EN_SEMI, 54)
        text_shadow(img, lambda dd, f: r.draw_runs(dd, (W - lw) / 2, y, ln2, r.BN_SUB, r.EN_SEMI, 54, f), 8, 170)
        d = ImageDraw.Draw(img)
        r.draw_runs(d, (W - lw) / 2, y, ln2, r.BN_SUB, r.EN_SEMI, 54, (255, 238, 225))
        y += 70
    # byline + source at the bottom
    by = BY.replace(" ", "  ")
    bw = r.width(d, by, r.BN_SUB, r.EN_SEMI, 44)
    r.draw_runs(d, (W - bw) / 2, 1228, by, r.BN_SUB, r.EN_SEMI, 44, r.YELLOW)
    sw = r.width(d, SRC, r.BN_SUB, r.EN_SEMI, 34)
    r.draw_runs(d, (W - sw) / 2, 1288, SRC, r.BN_SUB, r.EN_SEMI, 34, (255, 255, 255))
    return img


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    poster(0.0).save(os.path.join(out, "neha_poster.jpg"), quality=92)
    print("ok")


# ---------- photo mode: the user's photo, painted like a watercolour ----------
_CUT = {}


def painted_person(path):
    if path in _CUT:
        return _CUT[path]
    import cv2, tempfile
    src = Image.open(path).convert("RGB")
    src = src.crop((150, 0, src.width, src.height))        # drop the camera at the left edge
    tmp = tempfile.mktemp(suffix=".png")
    src.save(tmp)
    cut = r.cutout(tmp)
    os.remove(tmp)
    rgb = np.asarray(cut.convert("RGB"))
    sm = cv2.edgePreservingFilter(rgb[..., ::-1], flags=1, sigma_s=40, sigma_r=0.25)
    st = cv2.stylization(sm, sigma_s=25, sigma_r=0.25)
    st = cv2.addWeighted(st, 0.6, sm, 0.4, 0)[..., ::-1]
    st = Image.fromarray(st)
    from PIL import ImageEnhance
    st = ImageEnhance.Color(st).enhance(1.15)
    st = ImageEnhance.Brightness(st).enhance(1.06)
    p = st.convert("RGBA")
    p.putalpha(cut.split()[3].filter(ImageFilter.GaussianBlur(2.5)))
    _CUT[path] = p
    return p


def poster_photo(path, phase=0.0):
    bg = watercolor_bg()
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sc.alpha_composite(crowd(phase))
    fade = Image.new("L", (1, H), 0)
    for y in range(H):
        fade.putpixel((0, y), int(255 * min(1, max(0, (y - 520) / 220))))
    sc.putalpha(ImageChops.multiply(sc.split()[3], fade.resize((W, H))))
    img = bg.copy()
    img.paste(sc, (0, 0), sc)
    img = painterly(img)
    a = np.asarray(img, np.float32) * paper()[..., None]
    img = Image.fromarray(np.uint8(np.clip(a, 0, 255))).convert("RGBA")
    p = painted_person(path)
    s = 1.0 + 0.012 * math.sin(2 * math.pi * phase)        # gentle "breathing" zoom for the Reel
    tw = int(980 * s)
    th = int(p.height * tw / p.width)
    pp = p.resize((tw, th), Image.LANCZOS)
    top = 530
    pf = Image.new("L", (1, th), 0)                          # soften the very top of the hair into the red
    for y in range(th):
        pf.putpixel((0, y), int(255 * min(1, y / 40)))
    hf = Image.new("L", (tw, 1), 0)                          # soften the cut left/right photo edges
    for x in range(tw):
        hf.putpixel((x, 0), int(255 * min(1, x / 90, (tw - 1 - x) / 90)))
    m = ImageChops.multiply(pp.split()[3], pf.resize((tw, th)))
    pp.putalpha(ImageChops.multiply(m, hf.resize((tw, th))))
    img.alpha_composite(pp, ((W - tw) // 2 + 70, top))
    a = np.asarray(img.convert("RGB"), np.float32) * (0.75 + 0.25 * paper(9)[..., None])
    img = Image.fromarray(np.uint8(np.clip(a * 1.04, 0, 255)))
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        grad.putpixel((0, y), int(215 * min(1, max(0, (y - 1150) / 120))))
    img.paste((10, 6, 8), (0, 0), grad.resize((W, H)))
    return dress(img)


def dress(img):
    logo_pill(img)
    d = ImageDraw.Draw(img)
    heads = [h.replace(" ", "  ") for h in HEAD]
    for size in range(124, 60, -2):
        if all(r.width(d, h, r.BN_HEAD, r.EN_BLACK, size) <= W - 140 for h in heads):
            break
    y = 165
    for i, h in enumerate(heads):
        hw = r.width(d, h, r.BN_HEAD, r.EN_BLACK, size)
        yy = y
        text_shadow(img, lambda dd, f: r.draw_runs(dd, (W - hw) / 2, yy, h, r.BN_HEAD, r.EN_BLACK, size, f))
        r.grad_text(img, ((W - hw) / 2, yy - size * 0.1), h, size, r.SNOW if i == 0 else r.FIRE)
        y += size * 1.12
    d = ImageDraw.Draw(img)
    y += 18
    for ln in SUB:
        ln2 = ln.replace(" ", "  ")
        lw = r.width(d, ln2, r.BN_SUB, r.EN_SEMI, 54)
        text_shadow(img, lambda dd, f: r.draw_runs(dd, (W - lw) / 2, y, ln2, r.BN_SUB, r.EN_SEMI, 54, f), 8, 170)
        d = ImageDraw.Draw(img)
        r.draw_runs(d, (W - lw) / 2, y, ln2, r.BN_SUB, r.EN_SEMI, 54, (255, 238, 225))
        y += 70
    by = BY.replace(" ", "  ")
    bw = r.width(d, by, r.BN_SUB, r.EN_SEMI, 44)
    text_shadow(img, lambda dd, f: r.draw_runs(dd, (W - bw) / 2, 1228, by, r.BN_SUB, r.EN_SEMI, 44, f), 6, 220)
    d = ImageDraw.Draw(img)
    r.draw_runs(d, (W - bw) / 2, 1228, by, r.BN_SUB, r.EN_SEMI, 44, r.YELLOW)
    sw = r.width(d, SRC, r.BN_SUB, r.EN_SEMI, 34)
    r.draw_runs(d, (W - sw) / 2, 1288, SRC, r.BN_SUB, r.EN_SEMI, 34, (255, 255, 255))
    return img
