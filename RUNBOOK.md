# Daily run — Top 10 Breaking News (Facebook)

Schedule since 2026-10-18 (11 Reels a day):
- Daytime singles at **10:00, 13:00, 16:00** (separate task, see "Daytime single posts").
- Evening run at 18:18: **7 posts, one every 20 minutes from 19:00 to 21:00**.
- **22:00 roundup** "আজকের সেরা ১০" of the day's 10 stories (3 daytime + 7 evening).
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
   Grab frames at 1.8 s and ~12 s from 2-3 of the Reels (`ffmpeg -ss 12 -i post_XX_reel.mp4 -frames:v 1 frame.jpg`)
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
8b. **Daily roundup Reel ("আজকের সেরা ১০") at 22:00.** After the 7 posts are scheduled, merge the day's 10 stories
   (the 3 daytime files days/<date>_1000.json, _1300.json, _1600.json that exist, plus the 7 evening stories):
   `cd engine && python3 merge_day.py ../days/<date>_top10.json ../days/<date>_1000.json ../days/<date>_1300.json ../days/<date>_1600.json ../days/<date>.json`
   (missing files are skipped; biggest stories first is fine as is). Then
   `python3 -W ignore build_roundup.py ../days/<date>_top10.json ../<date>/` (music only, no voice-over;
   takes ~5 minutes). Push `<date>/roundup_reel.mp4`, check its raw URL returns 200, then schedule ONE
   Metricool post at `<date>T22:00:00+06:00` using `<date>/roundup.json`: text = caption,
   firstCommentText = first_comment (all 10 source links, numbered 1–10 in order), facebookData
   {"type": "REEL", "title": "আজকের সেরা ১০ খবর"}. Metricool allows only one first comment, so all links go in it.
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

## Daytime single posts (10:00, 13:00, 16:00)
A separate scheduled task runs at 09:40, 12:40 and 15:40 (Dhaka) and posts ONE story at 10:00, 13:00 or 16:00.
Each run:
1. Clones the repo as in step 1 and reads the editorial rules.
2. Calls getScheduledPosts for today and yesterday and skips any story already scheduled or posted.
3. Picks the single biggest fresh story of the moment that follows the rules, Bangladesh angle first (probashi,
   flights, Bangladesh in foreign news, good Bangladesh story), then a strong quote, a Cockroach/Delhi protest
   update, or breaking international news.
4. Writes `days/<date>_HHMM.json` with that one story (format "video", with points_bn), builds it with build_day.py into
   `<date>_HHMM/`, pushes, checks the raw URL returns 200, and schedules it as a REEL at that hour.
5. If a post is already scheduled within 15 minutes of that hour (for example one the user asked for), do nothing.
6. No report message is needed unless something failed.
The evening run (18:18) must not reuse any story from these daytime posts.
