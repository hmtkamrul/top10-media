from PIL import Image, ImageDraw, ImageFont
import math, os, random
F = "/home/claude/top10-media/engine/fonts/"
OUT = os.path.dirname(os.path.abspath(__file__))
def f(n, s): return ImageFont.truetype(F + n, s, layout_engine=ImageFont.Layout.RAQM)
NAVY = (18, 38, 82)
BLUE, LBLUE = (0, 158, 235), (120, 205, 255)
ORANGE, GREEN, RED = (255, 128, 0), (22, 176, 92), (235, 45, 60)
WHITE = (255, 255, 255)
BG1, BG2 = (255, 255, 255), (214, 238, 255)   # light background
OSW, BN_B, BN_H, BN_S = "oswald-latin-700-normal.ttf", "baloo-da-2-bengali-800-normal.ttf", "hind-siliguri-bengali-700-normal.ttf", "hind-siliguri-bengali-600-normal.ttf"

def grad(w, h, c1, c2, radial=False):
    im = Image.new("RGB", (w, h)); px = im.load()
    for y in range(h):
        for x in range(w):
            t = (math.hypot(x - w/2, y - h/2) / math.hypot(w/2, h/2)) if radial else y / h
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * min(1, t)) for i in range(3))
    return im

def briefcase(d, cx, cy, s, body=ORANGE, handle=NAVY, strap=(205, 90, 0), lock=WHITE):
    w, h = s, s * 0.72
    d.rounded_rectangle([cx - w*0.2, cy - h/2 - s*0.16, cx + w*0.2, cy - h/2 + s*0.04], radius=s*0.07, outline=handle, width=int(s*0.07))
    d.rounded_rectangle([cx - w/2, cy - h/2, cx + w/2, cy + h/2], radius=s*0.1, fill=body)
    d.rectangle([cx - w/2, cy - h*0.08, cx + w/2, cy - h*0.08 + s*0.05], fill=strap)
    d.rounded_rectangle([cx - s*0.09, cy - h*0.16, cx + s*0.09, cy + h*0.06], radius=s*0.03, fill=lock)

def bell(d, cx, cy, s, col=WHITE):
    d.ellipse([cx - s*0.08, cy - s*0.62, cx + s*0.08, cy - s*0.46], fill=col)
    d.pieslice([cx - s*0.42, cy - s*0.55, cx + s*0.42, cy + s*0.25], 180, 360, fill=col)
    d.rectangle([cx - s*0.42, cy - s*0.16, cx + s*0.42, cy + s*0.2], fill=col)
    d.polygon([(cx - s*0.42, cy + s*0.05), (cx - s*0.56, cy + s*0.3), (cx + s*0.56, cy + s*0.3), (cx + s*0.42, cy + s*0.05)], fill=col)
    d.ellipse([cx - s*0.13, cy + s*0.26, cx + s*0.13, cy + s*0.5], fill=col)

def ctext(d, x, y, t, fnt, fill): d.text((x, y), t, font=fnt, fill=fill, anchor="mm")

def confetti(lay, w, h, n, seed, keep_out=None):
    rnd = random.Random(seed); ld = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        if keep_out and keep_out[0] < x < keep_out[2] and keep_out[1] < y < keep_out[3]: continue
        c = rnd.choice([BLUE, ORANGE, GREEN, RED, LBLUE]); r = rnd.uniform(5, 13)
        if rnd.random() < 0.5: ld.ellipse([x - r, y - r, x + r, y + r], fill=c + (150,))
        else:
            a = rnd.uniform(0, math.pi); dx, dy = math.cos(a) * r * 1.6, math.sin(a) * r * 1.6
            ld.line([(x - dx, y - dy), (x + dx, y + dy)], fill=c + (160,), width=int(r * 0.8))

# ---------- Profile picture 1080x1080 (circle-safe) ----------
S = 1080
im = grad(S, S, BG1, BG2, radial=True).convert("RGBA")
lay = Image.new("RGBA", (S, S), (0, 0, 0, 0)); confetti(lay, S, S, 60, 7, keep_out=(170, 130, 910, 960))
im.alpha_composite(lay); d = ImageDraw.Draw(im)
for i, c in enumerate([BLUE, ORANGE, GREEN, RED]):   # 4-colour ring
    d.arc([55, 55, S-55, S-55], start=-90 + i*90 + 4, end=-90 + (i+1)*90 - 4, fill=c, width=26)
briefcase(d, S/2 - 30, 330, 250)
d.ellipse([S/2 + 50, 165, S/2 + 210, 325], fill=RED, outline=WHITE, width=9)
bell(d, S/2 + 130, 250, 95)
fo = f(OSW, 175); wt, wj = d.textlength("TOP ", font=fo), d.textlength("JOB", font=fo); x0 = S/2 - (wt + wj)/2
d.text((x0, 575), "TOP ", font=fo, fill=BLUE, anchor="lm"); d.text((x0 + wt, 575), "JOB", font=fo, fill=NAVY, anchor="lm")
d.rounded_rectangle([S/2 - 230, 680, S/2 + 230, 820], radius=28, fill=GREEN)
ctext(d, S/2, 745, "ALERT", f(OSW, 120), WHITE)
ctext(d, S/2, 892, "B A N G L A D E S H", f("inter-latin-800-normal.ttf", 44), RED)
im.convert("RGB").save(f"{OUT}/profile_picture.png")

# ---------- Cover 1640x924 (content inside the y 150-774 band desktop shows) ----------
W, H = 1640, 924
cv = grad(W, H, BG1, BG2).convert("RGBA")
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
for (x, y, r, c) in [(-60, 120, 260, LBLUE), (1700, 160, 280, ORANGE), (40, 900, 300, GREEN), (1620, 880, 260, RED), (820, -330, 380, LBLUE)]:
    ld.ellipse([x - r, y - r, x + r, y + r], fill=c + (60,))
confetti(lay, W, H, 120, 3, keep_out=(250, 180, 1390, 760))
cv.alpha_composite(lay)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
briefcase(ld, 140, 470, 190, body=ORANGE + (230,), handle=NAVY + (230,), strap=(205, 90, 0, 230), lock=(255, 255, 255, 230))
ld.ellipse([1410, 370, 1600, 560], fill=RED + (235,), outline=(255, 255, 255, 255), width=8); bell(ld, 1505, 470, 110)
cv.alpha_composite(lay); d = ImageDraw.Draw(cv)

fo = f(OSW, 118); words = [("TOP", BLUE), ("JOB", ORANGE), ("ALERT", RED), ("BD", GREEN)]
sp = 34; ws = [d.textlength(w, font=fo) for w, _ in words]; x = W/2 - (sum(ws) + sp*3)/2
for (w, c), wd in zip(words, ws): d.text((x, 255), w, font=fo, fill=c, anchor="lm"); x += wd + sp
ctext(d, W/2, 385, "প্রতিদিনের যাচাই করা চাকরির খবর", f(BN_B, 74), NAVY)
pf = f(BN_H, 44); pills = [("সরকারি", BLUE), ("বেসরকারি", ORANGE), ("ব্যাংক", GREEN), ("এনজিও", RED)]
pw = [d.textlength(t, font=pf) + 70 for t, _ in pills]; gap = 26; x = W/2 - (sum(pw) + gap*3)/2
for (t, c), w in zip(pills, pw):
    d.rounded_rectangle([x, 455, x + w, 535], radius=40, fill=c); ctext(d, x + w/2, 494, t, pf, WHITE); x += w + gap
tf = f(BN_H, 38); t1, t2 = "✔", None
line = "আবেদন শুধু অফিসিয়াল লিংকে"; line2 = "আমরা কোনো টাকা নিই না"
w1, w2 = d.textlength(line, font=tf), d.textlength(line2, font=tf); tot = w1 + w2 + 80
d.rounded_rectangle([W/2 - tot/2 - 50, 580, W/2 + tot/2 + 50, 656], radius=38, fill=WHITE, outline=GREEN, width=5)
x = W/2 - tot/2; d.text((x, 617), line, font=tf, fill=GREEN, anchor="lm"); x += w1 + 40
d.ellipse([x - 8, 609, x + 8, 625], fill=RED); x += 40; d.text((x, 617), line2, font=tf, fill=RED, anchor="lm")
ctext(d, W/2, 712, "চাকরির খবর মিস না করতে পেজটি ফলো করুন", f(BN_S, 38), (70, 90, 130))
cv.convert("RGB").save(f"{OUT}/cover_photo.png")
