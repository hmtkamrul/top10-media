# Life-hack series (separate from the news Reels; user's request 2026-10-24)

- 40-60 s Reel, 10 tips shown one by one, festive look and music (engine/lifehack_reel.py), NOT the news style.
- Hook headline + kicker at the start, no source at the start; at the end: "পেজটি ফলো করে কমেন্টে লিখুন GUIDE",
  "এমন জরুরি লাইফ হ্যাকের জন্য পেজে একটি ফলো দিয়ে সাথে থাকুন", and "সূত্র: বিভিন্ন অনলাইন প্রতিবেদন".
- Story file: days/lifehack/<date>_<slug>.json (kept out of days/ root so the roundup never picks it up).
  Build: `cd engine && python3 -W ignore lifehack_reel.py ../days/lifehack/<file>.json ../lifehack/<date>_<slug>/`
- PDF guide: lifehack/<date>_<slug>/guide.html rendered to PDF with Playwright Chromium (Bangla shaping works;
  reportlab does not shape Bangla). Fonts in lifehack/fonts. Full sources on the last page.
- Tips must come from real published articles/experts; write in our own words.
