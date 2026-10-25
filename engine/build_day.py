"""Build a day's posts (images + looping videos + captions) from a stories JSON.

Usage: python3 build_day.py today_YYYY-MM-DD.json out_dir/
Each story may set "format": "video" or "image".
"""
import json, os, sys, subprocess, tempfile, shutil
import render3 as r
from PIL import Image, ImageFilter, ImageEnhance

RW, RH = 1080, 1920   # Reel (9:16)


def to_reel(card):
    """Put a 1080x1350 card on a 1080x1920 canvas: blurred, darkened card fills the background,
    the sharp card sits a little above centre (the bottom of a Reel is covered by Facebook's UI)."""
    sc = RH / card.height
    bg = card.resize((int(card.width * sc), RH), Image.LANCZOS)
    ox = (bg.width - RW) // 2
    bg = bg.crop((ox, 0, ox + RW, RH)).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    bg.paste(card, (0, 230))
    return bg

r.SRC_BN.update({"Khaleej Times": "খালিজ টাইমস", "Reuters": "রয়টার্স", "BBC": "বিবিসি", "The Business Standard": "দ্য বিজনেস স্ট্যান্ডার্ড", "New Age": "নিউ এজ", "Outlook India": "আউটলুক ইন্ডিয়া", "The Quint": "দ্য কুইন্ট", "Dhaka Tribune": "ঢাকা ট্রিবিউন", "Fox News": "ফক্স নিউজ", "Onmanorama": "অনমনোরমা", "Maritime Gateway": "মেরিটাইম গেটওয়ে", "CBS News": "সিবিএস নিউজ", "Anadolu Agency": "আনাদোলু এজেন্সি", "IANS": "আইএএনএস", "The Statesman": "দ্য স্টেটসম্যান", "Gulf News": "গালফ নিউজ", "The Logical Indian": "দ্য লজিক্যাল ইন্ডিয়ান", "RIBA Journal": "রিবা জার্নাল", "The Financial Express": "দ্য ফিন্যান্সিয়াল এক্সপ্রেস", "The Tribune": "দ্য ট্রিবিউন", "Middle East Eye": "মিডল ইস্ট আই", "ABC News": "এবিসি নিউজ", "The Nation": "দ্য নেশন", "Asharq Al-Awsat": "আশারক আল-আওসাত", "Aerospace Global News": "অ্যারোস্পেস গ্লোবাল নিউজ", "Euronews": "ইউরোনিউজ", "The National": "দ্য ন্যাশনাল", "La Voce di New York": "লা ভোচে দি নিউইয়র্ক", "Malay Mail": "মালয় মেইল", "Al Arabiya": "আল আরাবিয়া", "ThePrint": "দ্য প্রিন্ট", "NTV": "এনটিভি", "Middle East Monitor": "মিডল ইস্ট মনিটর", "Gulf Business": "গালফ বিজনেস", "Axios": "অ্যাক্সিওস", "Dawn": "ডন", "TIME": "টাইম", "UNB": "ইউএনবি", "Modern Diplomacy": "মডার্ন ডিপ্লোম্যাসি"})
r.SRC_BN.update({"Responsible Statecraft": "রেসপনসিবল স্ট্যাটক্রাফট", "Associated Press": "অ্যাসোসিয়েটেড প্রেস", "Daily Sun": "ডেইলি সান", "News.az": "নিউজ.এজেড", "Siasat Daily": "সিয়াসাত ডেইলি"})
r.SRC_BN.update({"ESPNcricinfo": "ইএসপিএনক্রিকইনফো", "ESPN": "ইএসপিএন", "Cricbuzz": "ক্রিকবাজ", "Goal": "গোল ডটকম", "BBC Sport": "বিবিসি স্পোর্ট", "Sky Sports": "স্কাই স্পোর্টস", "The Athletic": "দ্য অ্যাথলেটিক", "Kyiv Independent": "কিয়েভ ইনডিপেনডেন্ট", "The Guardian": "দ্য গার্ডিয়ান", "Politico Europe": "পলিটিকো ইউরোপ", "DW": "ডয়চে ভেলে", "France 24": "ফ্রান্স টোয়েন্টিফোর", "UEFA": "উয়েফা", "Premier League": "প্রিমিয়ার লিগ"})
r.SRC_BN.update({"Türkiye Today": "তুরস্ক টুডে", "Manchester City FC": "ম্যানচেস্টার সিটি এফসি", "ScienceDaily": "সায়েন্সডেইলি"})
r.SRC_BN.update({"The Star": "দ্য স্টার", "SBS News": "এসবিএস নিউজ", "BSS": "বিএসএস"})
PAGE = "Top 10 Breaking News"
FRAMES, FPS, LOOPS = 36, 12, 3        # 3 s loop x 3 = 9 s video


AUDIO_FX = "acompressor=threshold=-20dB:ratio=4:attack=5:release=120:makeup=6dB,loudnorm=I=-11:TP=-1:LRA=7"


def make_music(seconds, path, seed):
    """Original news-bed music (same style as the roundup) with a stinger at the start."""
    import numpy as np
    import music
    bed = music.news_bed(seconds, hits=[0.9], seed=seed)
    mix = np.tanh(bed / (np.max(np.abs(bed)) + 1e-9) * 2.2) / np.tanh(2.2)
    music.write_wav(path, mix * 0.97)


def make_video(story, path):
    tmp = tempfile.mkdtemp()
    try:
        for i in range(FRAMES):
            to_reel(r.card(story, 1, 10, "", PAGE, phase=i / FRAMES)).save(f"{tmp}/f{i:03d}.png")
        once = f"{tmp}/once.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%03d.png",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", once], check=True)
        looped = f"{tmp}/looped.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", str(LOOPS - 1), "-i", once,
                        "-c", "copy", looped], check=True)
        make_music(FRAMES * LOOPS / FPS, f"{tmp}/music.wav", seed=sum(map(ord, story.get("title_en", ""))) % 997)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", looped, "-i", f"{tmp}/music.wav",
                        "-c:v", "copy", "-af", AUDIO_FX, "-c:a", "aac", "-b:a", "192k", "-shortest", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    posts = []
    for i, s in enumerate(data["stories"], 1):
        if True:   # every post is a Reel with music (user's rule since 2026-10-18; "format" is ignored)
            name = f"post_{i:02d}_reel.mp4"
            import kinetic                     # 16-20 s kinetic Reel (since 2026-10-18); make_video = old 9 s loop
            kinetic.make_kinetic(s, os.path.join(out, name))
        else:
            name = f"post_{i:02d}.jpg"
            r.card(s, i, 10, "", PAGE).save(os.path.join(out, name), quality=92)
        posts.append({"n": i, "file": name, "facebook_type": "REEL" if name.endswith(".mp4") else "POST", "caption": r.caption(s), "first_comment": r.first_comment(s)})
        print("built", name)
    json.dump(posts, open(os.path.join(out, "posts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(os.path.join(out, "captions.txt"), "w", encoding="utf-8") as f:
        for p in posts:
            f.write(f"========== POST {p['n']} — {p['file']} ==========\n\n{p['caption']}\n\n"
                    f"----- FIRST COMMENT -----\n{p['first_comment']}\n\n\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
