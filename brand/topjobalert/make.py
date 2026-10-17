from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
import math, os
F = "/home/claude/top10-media/engine/fonts/"
OUT = os.path.dirname(os.path.abspath(__file__))
def f(n, s): return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)
NAVY1, NAVY2 = (10, 22, 48), (22, 48, 96)
ORANGE, ORANGE2, RED = (255, 122, 0), (255, 170, 30), (230, 40, 50)
WHITE = (255, 255, 255)

def grad(w, h, c1, c2, radial=False):
    im = Image.new("RGB", (w, h)); px = im.load()
    for y in range(h):
        for x in range(w):
            t = (math.hypot(x - w/2, y - h/2) / math.hypot(w/2, h/2)) if radial else y / h
            px[x, y] = tuple(int(c2[i] + (c1[i] - c2[i]) * min(1, t)) for i in range(3))
    return im

def briefcase(d, cx, cy, s, body=ORANGE, handle=WHITE):
    w, h = s, s * 0.72
    d.rounded_rectangle([cx - w*0.2, cy - h/2 - s*0.16, cx + w*0.2, cy - h/2 + s*0.04], radius=s*0.07, outline=handle, width=int(s*0.07))
    d.rounded_rectangle([cx - w/2, cy - h/2, cx + w/2, cy + h/2], radius=s*0.1, fill=body)
    d.rectangle([cx - w/2, cy - h*0.08, cx + w/2, cy - h*0.08 + s*0.05], fill=(200, 85, 0))
    d.rounded_rectangle([cx - s*0.09, cy - h*0.16, cx + s*0.09, cy + h*0.06], radius=s*0.03, fill=handle)

def bell(d, cx, cy, s, col=WHITE):
    d.ellipse([cx - s*0.08, cy - s*0.62, cx + s*0.08, cy - s*0.46], fill=col)
    d.pieslice([cx - s*0.42, cy - s*0.55, cx + s*0.42, cy + s*0.25], 180, 360, fill=col)
    d.rectangle([cx - s*0.42, cy - s*0.16, cx + s*0.42, cy + s*0.2], fill=col)
    d.polygon([(cx - s*0.42, cy + s*0.05), (cx - s*0.56, cy + s*0.3), (cx + s*0.56, cy + s*0.3), (cx + s*0.42, cy + s*0.05)], fill=col)
    d.ellipse([cx - s*0.13, cy + s*0.26, cx + s*0.13, cy + s*0.5], fill=col)

def ctext(d, x, y, t, fnt, fill, anchor="mm"): d.text((x, y), t, font=fnt, fill=fill, anchor=anchor)

# ---------- Profile picture 1080x1080 (circle-safe) ----------
S = 1080
im = grad(S, S, NAVY1, NAVY2, radial=True)
d = ImageDraw.Draw(im)
d.ellipse([60, 60, S-60, S-60], outline=ORANGE, width=14)
briefcase(d, S/2 - 30, 330, 250)
# alert badge with bell
d.ellipse([S/2 + 50, 165, S/2 + 210, 325], fill=RED, outline=WHITE, width=8)
bell(d, S/2 + 130, 250, 95)
ctext(d, S/2, 575, "TOP JOB", f("oswald-latin-700-normal.ttf", 175), WHITE)
d.rounded_rectangle([S/2 - 230, 680, S/2 + 230, 820], radius=24, fill=ORANGE)
ctext(d, S/2, 745, "ALERT", f("oswald-latin-700-normal.ttf", 120), WHITE)
ctext(d, S/2, 890, "B A N G L A D E S H", f("inter-latin-800-normal.ttf", 44), ORANGE2)
im.save(f"{OUT}/profile_picture.png")
# circle preview
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S, S], fill=255)
pv = Image.new("RGB", (S, S), (240, 242, 245)); pv.paste(im, (0, 0), m); pv.save(f"{OUT}/_preview_circle.png")

# ---------- Cover 1640x924 (FB recommended; content kept inside the y 150-774 band desktop shows) ----------
W, H = 1640, 924
cv = grad(W, H, NAVY2, NAVY1)
d = ImageDraw.Draw(cv)
for x in range(-H, W, 70): d.line([(x, H), (x + H, 0)], fill=(18, 40, 82), width=18)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
briefcase(ld, 120, 640, 200, body=(255, 122, 0, 45), handle=(255, 255, 255, 45))
bell(ld, 1530, 640, 170, col=(255, 255, 255, 40))
cv.paste(lay, (0, 0), lay); d = ImageDraw.Draw(cv)
d.rectangle([0, 150, W, 158], fill=ORANGE); d.rectangle([0, 766, W, 774], fill=ORANGE)

def seg_line(y, parts, fnt, fill, gap=46, dot=10, dotcol=ORANGE):
    ws = [d.textlength(p, font=fnt) for p in parts]
    total = sum(ws) + gap * 2 * (len(parts) - 1)
    x = W/2 - total/2
    for i, (p, w) in enumerate(zip(parts, ws)):
        d.text((x, y), p, font=fnt, fill=fill, anchor="lm"); x += w
        if i < len(parts) - 1:
            d.ellipse([x + gap - dot, y - dot, x + gap + dot, y + dot], fill=dotcol); x += gap * 2

ctext(d, W/2, 255, "TOP JOB ALERT BD", f("oswald-latin-700-normal.ttf", 116), WHITE)
d.rectangle([W/2 - 160, 330, W/2 + 160, 337], fill=ORANGE)
ctext(d, W/2, 405, "প্রতিদিনের যাচাই করা চাকরির খবর", f("baloo-da-2-bengali-800-normal.ttf", 74), ORANGE2)
seg_line(498, ["সরকারি", "বেসরকারি", "ব্যাংক", "এনজিও"], f("hind-siliguri-bengali-700-normal.ttf", 50), WHITE)
pf = f("hind-siliguri-bengali-700-normal.ttf", 40)
t1, t2 = "আবেদন শুধু অফিসিয়াল লিংকে", "আমরা কোনো টাকা নিই না"
pw = d.textlength(t1, font=pf) + d.textlength(t2, font=pf) + 92
d.rounded_rectangle([W/2 - pw/2 - 50, 575, W/2 + pw/2 + 50, 657], radius=41, fill=RED)
seg_line(614, [t1, t2], pf, WHITE, dotcol=WHITE, dot=8)
ctext(d, W/2, 715, "চাকরির খবর মিস না করতে পেজটি ফলো করুন", f("hind-siliguri-bengali-600-normal.ttf", 38), (200, 210, 230))
cv.save(f"{OUT}/cover_photo.png")
print(features.check("raqm"))
