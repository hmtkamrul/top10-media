"""Bangla voice-over with the AI4Bharat Indic-TTS FastPitch + HiFiGAN model (Coqui TTS).

The model (~1.5 GB) lives outside the repo. setup_voice() downloads it once:
  https://github.com/AI4Bharat/Indic-TTS/releases/download/v1-checkpoints-release/bn.zip
"""
import os, re, json, subprocess, zipfile

MODEL_DIR = os.environ.get("BN_TTS_DIR", "/home/claude/tts/bn")
URL = "https://github.com/AI4Bharat/Indic-TTS/releases/download/v1-checkpoints-release/bn.zip"

ONES = ["শূন্য", "এক", "দুই", "তিন", "চার", "পাঁচ", "ছয়", "সাত", "আট", "নয়", "দশ", "এগারো", "বারো", "তেরো",
        "চৌদ্দ", "পনেরো", "ষোলো", "সতেরো", "আঠারো", "উনিশ", "বিশ", "একুশ", "বাইশ", "তেইশ", "চব্বিশ", "পঁচিশ",
        "ছাব্বিশ", "সাতাশ", "আটাশ", "ঊনত্রিশ", "ত্রিশ", "একত্রিশ", "বত্রিশ", "তেত্রিশ", "চৌত্রিশ", "পঁয়ত্রিশ",
        "ছত্রিশ", "সাঁইত্রিশ", "আটত্রিশ", "ঊনচল্লিশ", "চল্লিশ", "একচল্লিশ", "বিয়াল্লিশ", "তেতাল্লিশ", "চুয়াল্লিশ",
        "পঁয়তাল্লিশ", "ছেচল্লিশ", "সাতচল্লিশ", "আটচল্লিশ", "ঊনপঞ্চাশ", "পঞ্চাশ", "একান্ন", "বাহান্ন", "তিপ্পান্ন",
        "চুয়ান্ন", "পঞ্চান্ন", "ছাপ্পান্ন", "সাতান্ন", "আটান্ন", "ঊনষাট", "ষাট", "একষট্টি", "বাষট্টি", "তেষট্টি",
        "চৌষট্টি", "পঁয়ষট্টি", "ছেষট্টি", "সাতষট্টি", "আটষট্টি", "ঊনসত্তর", "সত্তর", "একাত্তর", "বাহাত্তর",
        "তিয়াত্তর", "চুয়াত্তর", "পঁচাত্তর", "ছিয়াত্তর", "সাতাত্তর", "আটাত্তর", "ঊনআশি", "আশি", "একাশি", "বিরাশি",
        "তিরাশি", "চুরাশি", "পঁচাশি", "ছিয়াশি", "সাতাশি", "আটাশি", "ঊননব্বই", "নব্বই", "একানব্বই", "বিরানব্বই",
        "তিরানব্বই", "চুরানব্বই", "পঁচানব্বই", "ছিয়ানব্বই", "সাতানব্বই", "আটানব্বই", "নিরানব্বই"]
BN2EN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def num_words(n):
    n = int(n)
    if n < 100:
        return ONES[n]
    parts = []
    for size, name in ((10 ** 7, "কোটি"), (10 ** 5, "লাখ"), (1000, "হাজার"), (100, "শো")):
        if n >= size:
            q, n = divmod(n, size)
            parts.append((num_words(q) if size != 100 else ONES[q]) + (" " if size != 100 else "") + name)
    if n:
        parts.append(ONES[n])
    return " ".join(parts)


def spoken(text):
    """Turn a headline/caption into text the model can read: numbers to words, drop symbols it lacks."""
    t = text.translate(BN2EN)
    t = re.sub(r"(\d+)\.(\d+)", lambda m: num_words(m.group(1)) + " দশমিক " + " ".join(ONES[int(c)] for c in m.group(2)), t)
    t = re.sub(r"(\d[\d,]*)", lambda m: num_words(m.group(1).replace(",", "")), t)
    t = t.replace("%", " শতাংশ").replace("$", " ডলার")
    t = re.sub(r"[‘’“”\"'()\[\]]", "", t)
    t = re.sub(r"[:;—–\-]", ", ", t)
    t = re.sub(r"[A-Za-z]+", "", t)          # the model has no Latin letters
    t = re.sub(r"\s+", " ", t).strip(" ,")
    if t and t[-1] not in "।?!":
        t += "।"
    return t


def setup_voice():
    if os.path.exists(os.path.join(MODEL_DIR, "fastpitch", "best_model.pth")):
        return
    root = os.path.dirname(MODEL_DIR)
    os.makedirs(root, exist_ok=True)
    z = os.path.join(root, "bn.zip")
    subprocess.run(["curl", "-sL", "--max-time", "1800", "-o", z, URL], check=True)
    zipfile.ZipFile(z).extractall(root)
    os.remove(z)


_SYN = None


def synth(text, path, speaker="male"):
    """Write a 22.05 kHz WAV of `text` to `path`."""
    global _SYN
    import warnings
    warnings.filterwarnings("ignore")
    if _SYN is None:
        setup_voice()
        cfg = os.path.join(MODEL_DIR, "fastpitch", "config.json")
        c = json.load(open(cfg))
        spk = os.path.join(MODEL_DIR, "fastpitch", "speakers.pth")
        if c.get("speakers_file") != spk:
            c["speakers_file"] = spk
            c.setdefault("model_args", {})["speakers_file"] = spk
            json.dump(c, open(cfg, "w"), ensure_ascii=False, indent=1)
        from TTS.utils.synthesizer import Synthesizer
        _SYN = Synthesizer(tts_checkpoint=os.path.join(MODEL_DIR, "fastpitch", "best_model.pth"), tts_config_path=cfg,
                           tts_speakers_file=spk, vocoder_checkpoint=os.path.join(MODEL_DIR, "hifigan", "best_model.pth"),
                           vocoder_config=os.path.join(MODEL_DIR, "hifigan", "config.json"), use_cuda=False)
    wav = _SYN.tts(spoken(text), speaker_name=speaker)
    _SYN.save_wav(wav, path)
    return path
