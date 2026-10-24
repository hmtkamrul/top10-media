# Life Skill Series ("লাইফ স্কিল সিরিজ · পর্ব N"; was "life-hack") (separate from the news Reels; user's request 2026-10-24)

- 40-60 s Reel, 10 tips shown one by one, festive look and music (engine/lifehack_reel.py), NOT the news style.
- Hook headline + kicker at the start, no source at the start; at the end: "পেজটি ফলো করে কমেন্টে লিখুন GUIDE",
  "এমন জরুরি লাইফ হ্যাকের জন্য পেজে একটি ফলো দিয়ে সাথে থাকুন", and "সূত্র: বিভিন্ন অনলাইন প্রতিবেদন".
- Story file: days/lifehack/<date>_<slug>.json (kept out of days/ root so the roundup never picks it up).
  Build: `cd engine && python3 -W ignore lifehack_reel.py ../days/lifehack/<file>.json ../lifehack/<date>_<slug>/`
- PDF guide: lifehack/<date>_<slug>/guide.html rendered to PDF with Playwright Chromium (Bangla shaping works;
  reportlab does not shape Bangla). Fonts in lifehack/fonts. Full sources on the last page.
- Tips must come from real published articles/experts; write in our own words.

## Rules from the user (2026-10-25)
- Branding: ribbon "লাইফ স্কিল সিরিজ · পর্ব N" (N = episode number), teaser at the start
  "শেষ পর্যন্ত দেখুন, সবচেয়ে কাজের উপায়টা শেষে"; the most useful, unusual tip goes LAST.
- Prefer unusual, practical hacks over generic advice ("make a list", "eat out less" are too common).
- End card: "ফ্রি গাইড বুক পেতে পেজটি ফলো করুন / তারপর কমেন্টে লিখুন GUIDE / আপনার মেসেজে বিস্তারিত গাইড বুকটি চলে যাবে / এমন জরুরি লাইফ স্কিলের জন্য
  পেজে একটি ফলো দিয়ে সাথে থাকুন / সূত্র: ইন্টারনেট থেকে সংকলিত".
- Guide book: no named outlets or experts in the body ("বিশেষজ্ঞদের মতে"); sources only in the appendix
  ("পরিশিষ্ট: তথ্যসূত্র", introduced as compiled from the internet). Cover keeps the red design.
- DIGNITY (all books): never suggest things that can hurt people's self-respect in Bangladesh, e.g. sharing
  groceries or bulk packs with relatives/neighbours, borrowing clothes or jewellery, splitting costs with
  others, second-hand shopping as a must, or anything that sounds like charity.
- Each Reel gets a ready caption in caption.txt (Day N line, hook, teaser, follow + GUIDE steps, a genuine
  question, source line, hashtags).

## Comment keyword + Messenger automation (user's rule, 2026-10-25)
- Each episode has its OWN topic keyword and its own Meta Business Suite automation (Inbox → Automations →
  "Comment to message"), named "Comment to message - Life Skill <KEYWORD> book". Porbo 1 = GUIDE
  (keywords guide, GUIDE, Guide, গাইড; links Top10_LifeSkill_Day1_Guide.pdf). Planned: SALES, PROGRESS, WALK, food topic.
- Pick keywords that are NOT short words hidden inside other words (Facebook matches "contains": "eat" would
  fire on great/beat/heat → use FOOD/DIET) and NOT common comment words (good, nice, help). Add case variants
  + the Bangla spelling (SALES/সেলস, PROGRESS/প্রগ্রেস, WALK/হাঁটা). Suggest the keyword when the script is
  finalised; set the automation only after the user OKs it. The Reel end-card pill and caption use that keyword.
- Automations apply to every post on the Page, so a keyword must never clash with an earlier episode's.
- Comment reply: "ধন্যবাদ! 📩 গাইড বুকটি আপনার মেসেজে পাঠিয়ে দিয়েছি।" Message: thanks + episode name + PDF raw
  link + one-line book summary + follow line.
- Workflow: the user reviews each week's guide books by hand ("human touch"). Record every correction the user
  makes in this file so later episodes need fewer changes.
