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

r.SRC_BN.update({"Khaleej Times": "খালিজ টাইমস", "Reuters": "রয়টার্স", "BBC": "বিবিসি", "The Business Standard": "দ্য বিজনেস স্ট্যান্ডার্ড", "New Age": "নিউ এজ", "Outlook India": "আউটলুক ইন্ডিয়া", "The Quint": "দ্য কুইন্ট", "Dhaka Tribune": "ঢাকা ট্রিবিউন", "Fox News": "ফক্স নিউজ", "Onmanorama": "অনমনোরমা", "Maritime Gateway": "মেরিটাইম গেটওয়ে", "CBS News": "সিবিএস নিউজ"})
PAGE = "Top 10 Breaking News"
FRAMES, FPS, LOOPS = 36, 12, 3        # 3 s loop x 3 = 9 s video


def make_video(story, path):
    tmp = tempfile.mkdtemp()
    try:
        for i in range(FRAMES):
            to_reel(r.card(story, 1, 10, "", PAGE, phase=i / FRAMES)).save(f"{tmp}/f{i:03d}.png")
        once = f"{tmp}/once.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%03d.png",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", once], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", str(LOOPS - 1), "-i", once,
                        "-c", "copy", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    posts = []
    for i, s in enumerate(data["stories"], 1):
        if s.get("format") == "video":
            name = f"post_{i:02d}_reel.mp4"
            make_video(s, os.path.join(out, name))
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
