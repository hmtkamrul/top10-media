"""Build the daily "আজকের সেরা ১০" roundup Reel (1080x1920) from a day's stories JSON.

Usage: python3 build_roundup.py ../days/<date>.json ../<date>/
Writes roundup_reel.mp4 and roundup.json (caption + first comment) into the output folder.
About 6 s per story + a 3 s intro and a 3 s outro, so 10 stories give a ~66 s video.
"""
import json, os, sys, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import render3 as r
from build_day import to_reel, PAGE, RW, RH

FPS = 12
PER_STORY = 6 * FPS
INTRO = OUTRO = 3 * FPS
BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def band_text(img, text, y, size, fill, font=None):
    d = ImageDraw.Draw(img)
    f = font or r.BN_HEAD
    w = r.width(d, text, f, r.EN_BLACK, size)
    r.draw_runs(d, (RW - w) / 2, y, text, f, r.EN_BLACK, size, fill)


def overlay(frame, k, n, t):
    """Top band: title + counter. Bottom band: progress bar across all stories."""
    band_text(frame, "আজকের সেরা ১০", 70, 64, r.WHITE)
    cnt = f"{k:02d} / {n:02d}".translate(BN)
    d = ImageDraw.Draw(frame)
    cw = r.width(d, cnt, r.BN_HEAD, r.EN_BLACK, 50) + 60
    d.rounded_rectangle([(RW - cw) / 2, 150, (RW + cw) / 2, 215], radius=32, fill=r.RED)
    band_text(frame, cnt, 154, 50, r.WHITE)
    # progress bar
    x0, x1, y = 80, RW - 80, 1640
    d.rounded_rectangle([x0, y, x1, y + 14], radius=7, fill=(60, 50, 50))
    p = ((k - 1) + t) / n
    if p > 0:
        bar = r.hgrad(max(2, int((x1 - x0) * p)), 14, r.RED, r.YELLOW)
        frame.paste(bar, (x0, y))
    return frame


def title_card(phase, lines, sub):
    base = to_reel(r.card({"cat": "intl", "scene": "abstract", "short_bn": "", "title_en": "roundup", "source": ""},
                          1, 10, "", PAGE, phase=phase))
    img = ImageEnhance.Brightness(base.filter(ImageFilter.GaussianBlur(10))).enhance(0.55)
    y = 700
    for i, ln in enumerate(lines):
        d = ImageDraw.Draw(img)
        w = r.width(d, ln, r.BN_HEAD, r.EN_BLACK, 120)
        r.grad_text(img, ((RW - w) / 2, y), ln, 120, r.SNOW if i == 0 else r.FIRE)
        y += 150
    band_text(img, sub, y + 30, 48, r.YELLOW, r.BN_SUB)
    return img


def _wav_len(path):
    import wave
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def _load(path, sr):
    import wave, numpy as np
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
        fr = w.getframerate()
    if fr != sr:                                   # linear resample to the music rate
        idx = np.linspace(0, len(x) - 1, int(len(x) * sr / fr))
        x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    return x


def main(src, out, speaker="male", voice=False):
    import numpy as np
    import music
    data = json.load(open(src, encoding="utf-8"))
    st = data["stories"]
    n = len(st)
    os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        # 1) voice-over script and clips
        ORD = ["", "এক", "দুই", "তিন", "চার", "পাঁচ", "ছয়", "সাত", "আট", "নয়", "দশ"]
        script = [("intro", "আজকের সেরা দশ খবর। চলুন দেখে নিই।")]
        for i, s in enumerate(st, 1):
            first = s.get("caption_bn", "").split("।")[0]
            script.append((f"s{i}", f"{ORD[i] if i < len(ORD) else i} নম্বর খবর। {s['title_bn']}। {first}।"))
        script.append(("outro", "প্রতিদিনের সেরা খবর পেতে, টপ টেন ব্রেকিং নিউজ পেজটি ফলো করুন।"))
        clips = {}
        if voice:
            import voice_bn
            for key, text in script:
                clips[key] = voice_bn.synth(text, f"{tmp}/{key}.wav", speaker)
        lead, tail = 0.6, 0.9
        dur = {k: (max(3.0, _wav_len(clips[k]) + lead + tail) if k in clips else (3.0 if k in ("intro", "outro") else 6.0))
               for k, _ in script}
        # 2) frames
        k = 0
        def save(img):
            nonlocal k
            img.save(f"{tmp}/f{k:05d}.jpg", quality=90)
            k += 1
        LOOP = 36   # animation loop length in frames; render each loop once and reuse it
        intro = [title_card(i / LOOP, ["আজকের", "সেরা ১০ খবর"], data.get("date_bn", "")) for i in range(LOOP)]
        for i in range(int(dur["intro"] * FPS)):
            save(intro[i % LOOP])
        for si, s in enumerate(st, 1):
            loop = [to_reel(r.card(s, si, n, "", PAGE, phase=i / LOOP)) for i in range(LOOP)]
            nf = int(dur[f"s{si}"] * FPS)
            for i in range(nf):
                save(overlay(loop[i % LOOP].copy(), si, n, i / nf))
        outro = [title_card(i / LOOP, ["প্রতিদিন রাতে", "সেরা ১০ খবর"], "ফলো করুন: Top 10 Breaking News") for i in range(LOOP)]
        for i in range(int(dur["outro"] * FPS)):
            save(outro[i % LOOP])
        total = k / FPS
        # 3) audio: music bed with stingers at each story start, voice on top, music ducked under voice
        starts, t = {}, 0.0
        for key, _ in script:
            starts[key] = t
            t += int(dur[key] * FPS) / FPS
        SR = music.SR
        bed = music.news_bed(total, hits=[starts[f"s{i}"] for i in range(1, n + 1)])
        vo = np.zeros_like(bed)
        for key, path in clips.items():
            x = _load(path, SR)
            i0 = int((starts[key] + lead) * SR)
            j = min(len(vo), i0 + len(x))
            vo[i0:j] += x[: j - i0] / (np.max(np.abs(x)) + 1e-9) * 0.95
        env = np.abs(vo)
        win = int(0.25 * SR)
        env = np.convolve(env, np.ones(win) / win, mode="same")
        duck = 1 - 0.72 * np.clip(env / 0.08, 0, 1)
        mix = bed * (0.55 if clips else 0.9) * duck + vo
        mix = mix / (np.max(np.abs(mix)) + 1e-9)
        if not clips:                                   # music only: push it louder with a soft limiter
            mix = np.tanh(mix * 2.2) / np.tanh(2.2)
        music.write_wav(f"{tmp}/audio.wav", mix * 0.97)
        path = os.path.join(out, "roundup_reel.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%05d.jpg",
                        "-i", f"{tmp}/audio.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
                        "-af", "acompressor=threshold=-20dB:ratio=4:attack=5:release=120:makeup=6dB,loudnorm=I=-11:TP=-1:LRA=7", "-c:a", "aac", "-b:a", "192k", "-shortest", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lines = "\n".join(f"{str(i).translate(BN)}. {s['title_bn']}" for i, s in enumerate(st, 1))
    caption = (f"📺 আজকের সেরা {str(n).translate(BN)} খবর, এক ভিডিওতে ({data.get('date_bn', '')})\n\n{lines}\n\n"
               f"💬 আজকের কোন খবরটা আপনার কাছে সবচেয়ে বড় মনে হলো? কমেন্টে জানান 👇\n\n"
               f"প্রতিদিন রাতে সেরা খবর পেতে পেজটি ফলো করুন ✅\n\n#Top10BreakingNews #BreakingNewsBD #আজকের_খবর")
    links = "\n".join(f"{str(i).translate(BN)}. {r.SRC_BN.get(s['source'], s['source'])}: {s['url']}" for i, s in enumerate(st, 1))
    json.dump({"file": "roundup_reel.mp4", "facebook_type": "REEL", "title": "আজকের সেরা ১০ খবর",
               "caption": caption, "first_comment": "📰 সব খবরের সূত্র:\n" + links},
              open(os.path.join(out, "roundup.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"built roundup_reel.mp4: {n} stories, {total:.0f} s")


if __name__ == "__main__":
    # voice-over is off by default (the Bangla TTS mispronounces too much); pass "voice" as 3rd arg to enable
    main(sys.argv[1], sys.argv[2], voice=(len(sys.argv) > 3 and sys.argv[3] == "voice"))
