# Daily run — Top 10 Breaking News (Facebook)

Schedule since 2026-10-24 (user's rule, 2026-10-23; data 19-22 Oct: 13:00-18:00 Reels get 170-990 views,
12:00 and 19:00-22:00 Reels mostly under 50). 11 Reels a day, all between 12:30 and 18:30:
- **News Reels at 12:30, 13:00, 14:00, 15:00, 17:00, 17:20, 17:40, 18:00, 18:15, 18:30** (10 a day).
- **16:00 = roundup** "২৪ ঘণ্টার সেরা ১০": the 10 best news Reels of the PREVIOUS day, best first by views.
- Nothing before 12:30 and nothing after 18:30.
- ONE batch task makes them, 2 runs a day on Sonnet: 11:30 → 12:30, 13:00, 14:00, 15:00 + the 16:00 roundup;
  15:30 → 17:00, 17:20, 17:40, 18:00, 18:15, 18:30 (+ the daily report). Each run writes one
  days/<date>_<first HHMM>.json with its news stories in slot order.
- The old "evening run of 7 posts" no longer exists. Steps 1-9 below still describe how to build and schedule.
Read `engine/EDITORIAL_RULES.md` first. Every rule there is mandatory.

## Fixed settings
- Metricool brand/blog id: **7426819** (Facebook Page connected). Timezone Asia/Dhaka.
- Media repo: `hmtkamrul/top10-media`, branch `main`.
- Public media URL: `https://raw.githubusercontent.com/hmtkamrul/top10-media/main/<YYYY-MM-DD>/<file>`

## Steps
1. **Repo.** Call `add_repo` (owner `hmtkamrul`, repo `top10-media`, access `push`), clone to `/home/claude/top10-media`,
   then `git config user.name Claude && git config user.email noreply@anthropic.com`.
2. **Tools.** Check `python3 -c "import PIL, numpy, fontTools"` and `ffmpeg -version`.
   If anything is missing: `pip install --break-system-packages pillow numpy fonttools`.
3. **Avoid repeats.** Call Metricool `getScheduledPosts` for today and yesterday (brandId 7426819, Asia/Dhaka)
   and do not pick any story that is already scheduled or posted.
4. **News research** (today's date, Dhaka time). Use WebSearch/WebFetch on sources such as
   prothomalo.com / en.prothomalo.com, thedailystar.net, bdnews24.com, tbsnews.net (Bangladesh), and
   aljazeera.com, bbc.com, reuters.com, apnews.com, espncricinfo.com, goal.com (international).
   - **Bangladesh angle first** (what gets views on this Page): Bangladeshi expats/probashi, flights to and from
     Bangladesh, what foreign leaders/media say about Bangladesh, Bangladeshis abroad, positive Bangladesh news,
     plus the Delhi Cockroach/Gen-Z protest. Then the biggest international stories.
   - Bangladesh: at most 3 stories in the evening 7, ONLY positive/constructive ones (see the rules). Positive
     development projects (railway, bridge, metro, road, port, power) ARE allowed and encouraged,
     facts only. No political, negative or controversial BD news, and no BD official's photo or
     name-led headline.
   - Fill the rest with the biggest international stories popular with Bangladeshi readers. Always 7 in total.
   - Each story needs its OWN article URL (no live-blog page reused for several stories); if two stories share one page, find a dedicated article or drop one.
   - Verify every fact on the article page. Rewrite in your own Bangla words; never copy.
5. **Write `days/<YYYY-MM-DD>.json`** with the same shape as `days/2026-10-14.json`:
   ```
   {"date_bn": "...", "stories": [ {
      "cat": "bd" | "intl" | "econ" | "sports",
      "format": "video"   (ALWAYS "video": every post is a motion Reel, no still images),
      "scene": EVERY story MUST get the theme that best matches it (no plain backgrounds):
               "war"          missiles/strikes/war (Middle East, Ukraine, Russia)
               "airport_fire" an attack or fire at an airport / facility
               "protest"      protests, movements, marches (Delhi, Nepal, Sri Lanka)
               "usa"          Trump, US politics, Washington
               "world"        diplomacy, summits, deals, China / North Korea / international relations
               "economy"      economy, trade, exports, remittance, markets, oil prices
               "bridge"       development projects: bridge, railway, metro, road, port, power (good news)
               "football"     football;  "cricket"  cricket
               "abstract"     anything else (still animated, never plain)
      "quote_by": "নেহা বোরা, ভারতের ছাত্রনেত্রী" (optional: when short_bn is a quote, who said it),
      "motifs": ["smoke"] | ["plane"] | [] (optional extras for the generic scene),
      "short_bn": "card headline, max ~30 Bangla characters, so it fits 2 big lines",
      "points_bn": ["3-4 short key facts, each one line of ~35-60 Bangla characters, shown one by one in the Reel",
                    "write them so a viewer keeps reading: the most surprising fact first, numbers, who/what/where"],
      "title_bn": "full Bangla headline (first line of the caption)",
      "title_en": "English headline (used only as a random seed)",
      "caption_bn": "2-4 sentence Bangla summary, facts only, no opinion",
      "question_bn": "one short, neutral question for readers that invites comments, e.g. 'এই যুদ্ধ কবে থামবে বলে মনে করেন?'",
      "source": "Prothom Alo | The Daily Star | Al Jazeera | BBC | Reuters | ...",
      "url": "article URL" } ] }
   ```
   Order: biggest story first. All 7 stories are "video" (motion Reels). Never use "image".
   For any new source name, add its Bangla spelling to `SRC_BN` in `engine/build_day.py`.
6. **Build:** `cd engine && python3 build_day.py ../days/<date>.json ../<date>/`
   This writes `post_XX_reel.mp4` for every story: a 16-20 s kinetic Reel (engine/kinetic.py) with a white flash +
   "ব্রেকিং নিউজ" hook, the headline, the points_bn facts sliding in one by one, a "ফলো করুন" end card, and original
   news-style music. ~45 s per Reel. Also writes `posts.json` and `captions.txt`.
   Frame 0 is the Reel's cover/thumbnail on Facebook (headline + ribbon, never a blank or white frame).
   Grab frames at 0 s and ~12 s from 2-3 of the Reels (`ffmpeg -ss 12 -i post_XX_reel.mp4 -frames:v 1 frame.jpg`)
   and open them with Read to check that the Bangla text fits and renders correctly.
7. **Publish media:** `git add -A && git commit -m "Posts for <date>" && git push origin HEAD:main`.
   Then `curl -s -o /dev/null -w "%{http_code}"` each raw URL. Every one must return 200 before you go on.
8. **Schedule on Metricool**, one `createScheduledPost` per post, using `posts.json`:
   - `blogId` "7426819"; date `<date>T19:00:00+06:00`, then +20 minutes for each following post (last at 21:00).
   - info: `providers [{"network":"facebook"}]`, `text` = caption, `firstCommentText` = first_comment,
     `media` = [raw URL], `autoPublish` true, `draft` false,
     `facebookData` {"type": posts.json "facebook_type"} — always "REEL" (every post is a Reel)
     (for Reels also add "title": the short headline),
     `publicationDate` {dateTime, timezone "Asia/Dhaka"}, plus the other default fields.
   - If it is already past 19:00 when you get here, start 10 minutes from now instead.
8b. **Roundup Reel ("২৪ ঘণ্টার সেরা ১০") at 16:00** (since 2026-10-24; was 14:00 on 23 Oct). Built in the 11:30 run,
   after the 12:30-15:00 news Reels. It covers YESTERDAY's news Reels (never a roundup itself).
   **Pick and order = best performers first (user's rule):** yesterday's Reels sorted by **total views**, top 10 only
   (if yesterday had more than 10 news Reels, the weakest drop out).
   - Get views from Metricool (`getAnalyticsDataByMetrics` with FBRE02 date+time (UTC), FBRE03 reel id,
     FBRE10 views; from/to = yesterday in Asia/Dhaka). Map each reel id to its story with `getScheduledPosts`
     for yesterday (providers[0].id = reel id; the article link is in firstCommentText).
   - Write the article URLs, best first, one per line, to `days/<yesterday>_order.txt` (max 10).
   - If view data can't be read, skip `--order` (time order) and say so in the report.
   `cd engine && python3 merge_day.py --order ../days/<yesterday>_order.txt ../days/<yesterday>_top10.json ../days/<yesterday>_[0-9][0-9][0-9][0-9].json`
   (the glob picks up every story file of that date; with --order only the listed stories matter, max 10). Then
   `python3 -W ignore build_roundup.py ../days/<yesterday>_top10.json ../<today>_roundup/` (music only, ~4 minutes).
   Check one frame, push `<today>_roundup/roundup_reel.mp4`, check its raw URL returns 200, then schedule ONE
   Metricool post at `<today>T16:00:00+06:00` using `<today>_roundup/roundup.json`: text = caption,
   firstCommentText = first_comment (all 10 source links, numbered 1–10 in order), facebookData
   {"type": "REEL", "title": "২৪ ঘণ্টার সেরা ১০ খবর"}. Metricool allows only one first comment, so all links go in it.
9. **Report** with SendUserMessage, in Banglish: the 7 evening headlines with their times, and anything that went wrong.
   End with a "📢 Group-e share korun" section: the 2 posts most likely to spread (big international/quote/protest
   stories first) with their Metricool plannerUrl, and for each the kind of Facebook group to share it in
   (e.g. international politics, Middle East/probashi, Indian politics, football/cricket, positive Bangladesh).
   Remind: max 1–2 groups per day, share by hand.

## Never
- Post negative, government, political or controversial Bangladesh news.
- Post photos or AI-made faces of real people.
- Copy article text word for word.

## Metricool plan
- The account is on a paid plan (upgraded 2026-10-17), so there is no 20-posts-a-month limit any more.
- If `createScheduledPost` still returns a plan/limit error, stop scheduling and tell the user which posts
  could not be scheduled.

## Single posts through the day (12:00-21:00, every hour)
One scheduled task runs at :40 from 11:40 to 20:40 (Dhaka) and posts ONE story at the next full hour.
Each run:
1. Clones the repo as in step 1 and reads the editorial rules (especially "Daily content plan").
2. Calls getScheduledPosts for today and yesterday; skips any story already scheduled or posted, and does nothing
   if a post is already scheduled within 10 minutes of the target slot (for example one the user asked for).
3. Decides what this slot needs from the "Daily content plan" (war stories in 14:00-18:30, the daily pro-Iran /
   anti-US-war analysis, probashi, etc.) by looking at what is already scheduled today, then picks the biggest
   fresh story of that kind.
4. Writes `days/<date>_HHMM.json` with that one story (format "video", with points_bn; add "bg_image" from
   engine/assets when the plan says so), builds it with build_day.py into `<date>_HHMM/`, pushes, checks the raw
   URL returns 200, and schedules it as a REEL at that hour.
5. No report message is needed unless something failed.
