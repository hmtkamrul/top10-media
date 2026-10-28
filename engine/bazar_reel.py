"""Daily 10:00 "বাজার দর" Reel (Dhaka kacha bazar prices; user's request 2026-10-28).

5-6 frames: a hook card, 4-5 price boards (vegetables, fish, chicken & eggs, meat, onion/potato/spices), and an
end card with the sources. Prices come from the LATEST published Dhaka market report(s); the report date is
always shown, never presented as a price survey of our own.

Common items to cover every day when a report has them (user, 2026-10-28): কাঁচা মরিচ, ধনিয়া পাতা, লেবু, টমেটো,
seasonal vegetables; রুই, পাঙাশ, তেলাপিয়া, চিংড়ি; ব্রয়লার, সোনালি, দেশি মুরগি, ডিম, গরু/খাসির মাংস;
চাল, ডাল, তেল, আটা, ময়দা; পেঁয়াজ, আলু, আদা, রসুন. Put a unit in the item name when it differs from the board
unit, e.g. "লেবু (হালি)", "সয়াবিন তেল (লিটার)", "আটা (২ কেজি প্যাকেট)".

Usage: python3 -W ignore bazar_reel.py ../days/bazar/<date>.json ../<date>_bazar/
Writes bazar_reel.mp4 and post.json (caption + first comment).

JSON:
{"date_bn": "২৯ অক্টোবর ২০২৬",              post date
 "report_date_bn": "২২ অক্টোবর",           date of the newest report used (kept for records; dates show only on the end card)
 "hook_bn": "শিমের দাম কমল ৪০ টাকা",          big hook line (the most surprising change)
 "kicker_bn": "মুরগি-ডিম এখনো চড়া",          optional second line (red)
 "sections": [{"title": "সবজি", "unit": "প্রতি কেজি", "items": [
      {"name": "শিম", "price": "১৪০-১৫০", "chg": "down", "note": "৪০ টাকা কম"}, ...]}],   max 6 items, chg up|down|""
 "sources": [{"name": "দ্য বিজনেস স্ট্যান্ডার্ড", "date_bn": "২২ অক্টোবর", "url": "..."}],
 "question_bn": "আপনার এলাকায় শিমের দাম কত?"}
"""
import json, math, os, random, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kinetic as k
import music
import render3 as r

RW, RH, FPS = 1080, 1920, 24
HOOK_S, BOARD_S, ROW_S, END_S = 3.6, 5.6, 0.32, 4.0
GREEN = (60, 200, 90)
CAT_COL = [(255, 226, 30), (228, 22, 30), (255, 150, 40), (60, 200, 90), (255, 226, 30), (228, 22, 30)]


def bn(x):
    return str(x).translate(r.BN_DIGITS)


# ---------- background: dark warm wood + drifting bokeh ----------
def bg_loop(n=48, seed=5):
    rnd = random.Random(seed)
    y = np.linspace(0, 1, RH)[:, None, None]
    top, bot = np.array([16, 10, 7.0]), np.array([58, 32, 16.0])
    base = top + (bot - top) * (y ** 1.4)
    base = np.repeat(base, RW, axis=1)
    # faint wood grain in the lower third
    xs = np.arange(RW)[None, :]
    grain = (np.sin(xs / 9.0 + np.sin(np.arange(RH)[:, None] / 37.0) * 3) * 0.5 + 0.5) * 10
    mask = np.clip((np.arange(RH)[:, None] / RH - 0.72) / 0.1, 0, 1)
    base = base + (grain * mask)[..., None] * np.array([1, 0.6, 0.3])
    lights = [(rnd.uniform(0, RW), rnd.uniform(0, RH * 0.7), rnd.uniform(28, 80), rnd.uniform(0.3, 0.85),
               rnd.choice([(255, 190, 110), (255, 160, 70), (255, 214, 140), (230, 200, 160)]), rnd.uniform(0, 6.28))
              for _ in range(34)]
    out = []
    for i in range(n):
        ph = i / n
        lay = Image.new("RGB", (RW // 4, RH // 4), (0, 0, 0))
        d = ImageDraw.Draw(lay)
        for (x, yy, rr, kk, c, th) in lights:
            cx = (x + 22 * math.sin(2 * math.pi * ph + th)) / 4
            cy = (yy + 14 * math.cos(2 * math.pi * ph + th)) / 4
            a = kk * (0.75 + 0.25 * math.sin(2 * math.pi * ph * 2 + th))
            d.ellipse([cx - rr / 4, cy - rr / 4, cx + rr / 4, cy + rr / 4], fill=tuple(int(v * a) for v in c))
        lay = np.asarray(lay.filter(ImageFilter.GaussianBlur(5)).resize((RW, RH), Image.BICUBIC), np.float32)
        img = 255 - (255 - base) * (1 - lay / 255.0)
        out.append(Image.fromarray(np.uint8(np.clip(img, 0, 255))))
    return out


# ---------- sprites ----------
def tri(d, x, y, s, up, col):
    if up:
        d.polygon([(x, y + s), (x + s, y + s), (x + s / 2, y)], fill=col)
    else:
        d.polygon([(x, y), (x + s, y), (x + s / 2, y + s)], fill=col)


def board_sprite(sec, idx, report_date):
    """Header pill + rows; returns (header_sprite, [row_sprites], unit_sprite)."""
    d0 = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    col = CAT_COL[idx % len(CAT_COL)]
    t = k._sp(sec["title"])
    tw = r.width(d0, t, r.BN_HEAD, r.EN_BLACK, 88)
    hd = Image.new("RGBA", (int(tw + 120), 140), (0, 0, 0, 0))
    hdd = ImageDraw.Draw(hd)
    hdd.rounded_rectangle([0, 0, hd.width - 1, 139], radius=30, fill=col + (255,))
    r.draw_runs(hdd, 60, 12, t, r.BN_HEAD, r.EN_BLACK, 88, (20, 12, 8, 255) if col != r.RED else (255, 255, 255, 255))
    ut = k._sp(f"{sec.get('unit', 'প্রতি কেজি')} · টাকায়")       # report date only on the end card (user, 2026-10-28)
    us = 40
    while us > 28 and r.width(d0, ut, r.BN_SUB, r.EN_SEMI, us) > RW - 120:
        us -= 2
    unit = k.text_sprite([ut], r.BN_SUB, r.EN_SEMI, us, fill=(255, 225, 200, 255))
    rows = []
    W = RW - 120
    for it in sec["items"][:6]:
        h = 168 if it.get("note") else 132
        im = Image.new("RGBA", (W, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.rounded_rectangle([0, 0, W - 1, h - 1], radius=24, fill=(14, 9, 6, 225))
        dd.rounded_rectangle([0, 0, 12, h - 1], radius=6, fill=col + (255,))
        name = k._sp(it["name"])
        ns = 60
        while ns > 44 and r.width(dd, name, r.BN_HEAD, r.EN_BLACK, ns) > W * 0.5:
            ns -= 2
        ny = (132 - ns * 1.35) / 2 + 4
        r.draw_runs(dd, 40, ny, name, r.BN_HEAD, r.EN_BLACK, ns, (255, 255, 255, 255))
        price = "৳ " + bn(it["price"]).replace("-", "–")
        ps = 66
        pw = r.width(dd, price, r.BN_HEAD, r.EN_BLACK, ps)
        chg = it.get("chg", "")
        right = W - 40 - (58 if chg else 0)
        r.draw_runs(dd, right - pw, (132 - ps * 1.35) / 2 + 2, price, r.BN_HEAD, r.EN_BLACK, ps, r.YELLOW + (255,))
        if chg in ("up", "down"):
            tri(dd, W - 76, 132 / 2 - 18, 36, chg == "up", (r.RED if chg == "up" else GREEN) + (255,))
        if it.get("note"):
            nt = k._sp(it["note"])
            r.draw_runs(dd, 40, 112, nt, r.BN_SUB, r.EN_SEMI, 36, (r.RED if chg == "up" else GREEN if chg == "down" else (255, 225, 200)) + (255,))
        rows.append(im)
    return hd, rows, unit


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    secs = data["sections"][:5]
    rep = f"{data['report_date_bn']}-এর প্রতিবেদন"
    loop = bg_loop()
    logo = k.logo_sprite()
    rib = k.ribbon_sprite(k._sp("বাজার দর · ঢাকা"))
    d0 = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    hs = 116
    hl = r.wrap_balanced(d0, data["hook_bn"], r.BN_HEAD, r.EN_BLACK, hs, RW - 160)
    while (len(hl) > 2 or any(r.width(d0, k._sp(l), r.BN_HEAD, r.EN_BLACK, hs) > RW - 140 for l in hl)) and hs > 76:
        hs -= 6
        hl = r.wrap_balanced(d0, data["hook_bn"], r.BN_HEAD, r.EN_BLACK, hs, RW - 160)
    hook = k.text_sprite([k._sp(l) for l in hl], r.BN_HEAD, r.EN_BLACK, hs, stops=r.FIRE, first_stops=r.SNOW)
    kick = k.text_sprite([k._sp(data["kicker_bn"])], r.BN_HEAD, r.EN_BLACK, 56, fill=r.RED + (255,)) if data.get("kicker_bn") else None
    datel = k.text_sprite([k._sp(data['date_bn'])],
                          r.BN_SUB, r.EN_SEMI, 42, fill=(255, 225, 200, 255))
    tl = [k._sp(" · ".join(x["title"] for x in secs))]
    if r.width(d0, tl[0], r.BN_SUB, r.EN_SEMI, 44) > RW - 100:          # too long: two lines
        h2 = (len(secs) + 1) // 2
        tl = [k._sp(" · ".join(x["title"] for x in secs[:h2])), k._sp(" · ".join(x["title"] for x in secs[h2:]))]
    teaser = k.text_sprite(tl, r.BN_SUB, r.EN_SEMI, 44, fill=r.YELLOW + (255,))
    boards = [board_sprite(s, i, rep) for i, s in enumerate(secs)]
    srcs = "\n".join(f"{s['name']} ({s['date_bn']})" for s in data["sources"])
    end_a = k.text_sprite([k._sp("তথ্যসূত্র")], r.BN_HEAD, r.EN_BLACK, 70, fill=r.YELLOW + (255,))
    end_b = k.text_sprite([k._sp(l) for l in srcs.split("\n")], r.BN_SUB, r.EN_SEMI, 46, fill=(255, 255, 255, 255))
    end_c = k.text_sprite([k._sp("এলাকা ও দোকানভেদে দাম কম-বেশি হতে পারে")], r.BN_SUB, r.EN_SEMI, 40, fill=(255, 225, 200, 255))
    pill_t = k._sp("প্রতিদিন সকাল ১০টায়")
    pw = r.width(d0, pill_t, r.BN_HEAD, r.EN_BLACK, 64)
    pill = Image.new("RGBA", (int(pw + 100), 116), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, pill.width - 1, 115], radius=58, fill=r.YELLOW + (255,))
    r.draw_runs(ImageDraw.Draw(pill), 50, 10, pill_t, r.BN_HEAD, r.EN_BLACK, 64, (20, 12, 8, 255))
    fol = k.text_sprite([k._sp("বাজারের খবর পেতে পেজটি ফলো করুন")], r.BN_HEAD, r.EN_BLACK, 52, fill=(255, 255, 255, 255))

    starts = [HOOK_S + i * BOARD_S for i in range(len(boards))]
    dur = HOOK_S + BOARD_S * len(boards) + END_S
    n = int(dur * FPS)
    tmp = tempfile.mkdtemp()
    try:
        for f in range(n):
            t = f / FPS if f > 0 else 2.6           # frame 0 = cover with the hook fully shown
            img = loop[(f // 2) % len(loop)].convert("RGBA")
            dd = ImageDraw.Draw(img)
            dd.rectangle([0, 0, RW, 10], fill=(40, 30, 30, 255))
            img.paste(r.hgrad(max(2, int(RW * t / dur)), 10, r.RED, r.YELLOW), (0, 0))
            k.paste(img, logo, RW - logo.width - 40, 70)
            kb = k.back(t / 0.35)
            k.paste(img, rib, (RW - rib.width) / 2, 190 - 60 * (1 - kb), alpha=min(1, t / 0.15))
            if t < HOOK_S:
                a = k.ease(t / 0.4)
                y0 = 560
                k.paste(img, hook, (RW - hook.width) / 2, y0 + 40 * (1 - a), alpha=a)
                y = y0 + hook.height + 10
                if kick:
                    a2 = k.ease((t - 0.5) / 0.4)
                    k.paste(img, kick, (RW - kick.width) / 2, y, alpha=a2)
                    y += kick.height + 20
                k.paste(img, datel, (RW - datel.width) / 2, y, alpha=k.ease((t - 0.8) / 0.4))
                k.paste(img, teaser, (RW - teaser.width) / 2, y + datel.height + 40,
                        alpha=k.ease((t - 1.2) / 0.4) * (0.7 + 0.3 * math.sin(t * 6)))
            elif t < dur - END_S:
                bi = int((t - HOOK_S) // BOARD_S)
                tb = t - starts[bi]
                hd, rows, unit = boards[bi]
                a = k.back(tb / 0.35)
                k.paste(img, hd, (RW - hd.width) / 2, 340, alpha=min(1, tb / 0.2), scale=0.85 + 0.15 * a)
                k.paste(img, unit, (RW - unit.width) / 2, 500, alpha=k.ease((tb - 0.2) / 0.3))
                y = 590
                for j, row in enumerate(rows):
                    ta = tb - 0.45 - j * ROW_S
                    e = k.ease(ta / 0.35)
                    k.paste(img, row, 60 + 120 * (1 - e) * (1 if j % 2 else -1), y, alpha=e)
                    y += row.height + 20
                if tb > BOARD_S - 0.25:                 # quick fade before the next board
                    pass
            else:
                te = t - (dur - END_S)
                k.paste(img, end_a, (RW - end_a.width) / 2, 420, alpha=k.ease(te / 0.3))
                k.paste(img, end_b, (RW - end_b.width) / 2, 540, alpha=k.ease((te - 0.2) / 0.3))
                yb = 540 + end_b.height + 20
                k.paste(img, end_c, (RW - end_c.width) / 2, yb, alpha=k.ease((te - 0.4) / 0.3))
                k.paste(img, pill, (RW - pill.width) / 2, yb + 170, scale=0.8 + 0.2 * k.back((te - 0.6) / 0.4),
                        alpha=k.ease((te - 0.6) / 0.2))
                k.paste(img, fol, (RW - fol.width) / 2, yb + 320, alpha=k.ease((te - 0.9) / 0.3))
            img.convert("RGB").save(f"{tmp}/f{f:05d}.jpg", quality=90)
        hits = [0.05] + starts + [dur - END_S]
        bed = music.with_jingle(music.news_bed(dur, hits=hits))
        bed = np.tanh(bed / (np.max(np.abs(bed)) + 1e-9) * 2.0) / np.tanh(2.0)
        music.write_wav(f"{tmp}/a.wav", bed * 0.95)
        from build_day import AUDIO_FX
        path = os.path.join(out, "bazar_reel.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%05d.jpg",
                        "-i", f"{tmp}/a.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21",
                        "-af", AUDIO_FX, "-c:a", "aac", "-b:a", "192k", "-shortest", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # caption + first comment
    lines = []
    for s in secs:
        items = ", ".join(f"{it['name']} {bn(it['price'])}" for it in s["items"][:6])
        lines.append(f"🔸 {s['title']} ({s.get('unit', 'প্রতি কেজি')}): {items}")
    src_names = ", ".join(f"{s['name']} ({s['date_bn']})" for s in data["sources"])
    caption = (f"🛒 ঢাকার বাজার দর | {data['date_bn']}\n{data['hook_bn']}\n\n" + "\n".join(lines) +
               f"\n\n📌 দাম টাকায়, সর্বশেষ বাজার প্রতিবেদন অনুযায়ী। এলাকা ও দোকানভেদে দাম কম-বেশি হতে পারে।\n\n"
               f"💬 {data.get('question_bn', 'আপনার এলাকায় আজ কোন জিনিসের দাম সবচেয়ে বেশি মনে হচ্ছে?')} কমেন্টে জানান 👇\n\n"
               f"📰 তথ্যসূত্র: {src_names} (লিংক কমেন্টে 👇)\n\n{r.FOLLOW_LINE}\n\n#বাজার_দর #ঢাকা #Top10BreakingNews")
    links = "\n".join(f"{s['name']} ({s['date_bn']}): {s['url']}" for s in data["sources"])
    json.dump({"file": "bazar_reel.mp4", "facebook_type": "REEL", "title": f"ঢাকার বাজার দর: {data['hook_bn']}",
               "caption": caption, "first_comment": "📰 তথ্যসূত্র:\n" + links + "\n\n" + r.FOLLOW_LINE},
              open(os.path.join(out, "post.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"built bazar_reel.mp4: {len(secs)} boards, {dur:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
