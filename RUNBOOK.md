# Daily run — Top 10 Breaking News (Facebook)

Runs every day at 18:30 Asia/Dhaka. Goal: 10 posts on the Facebook Page
"Top 10 Breaking News", one every 12 minutes from 19:00 to 20:48.
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
   - Bangladesh: at most 5 stories, ONLY positive/constructive ones (see the rules). Positive
     development projects (railway, bridge, metro, road, port, power) ARE allowed and encouraged,
     facts only. No political, negative or controversial BD news, and no BD official's photo or
     name-led headline.
   - Fill the rest with the biggest international stories popular with Bangladeshi readers. Always 10 in total.
   - Verify every fact on the article page. Rewrite in your own Bangla words; never copy.
5. **Write `days/<YYYY-MM-DD>.json`** with the same shape as `days/2026-10-14.json`:
   ```
   {"date_bn": "...", "stories": [ {
      "cat": "bd" | "intl" | "econ" | "sports",
      "format": "video" | "image",
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
      "title_bn": "full Bangla headline (first line of the caption)",
      "title_en": "English headline (used only as a random seed)",
      "caption_bn": "2-4 sentence Bangla summary, facts only, no opinion",
      "question_bn": "one short, neutral question for readers that invites comments, e.g. 'এই যুদ্ধ কবে থামবে বলে মনে করেন?'",
      "source": "Prothom Alo | The Daily Star | Al Jazeera | BBC | Reuters | ...",
      "url": "article URL" } ] }
   ```
   Order: biggest story first. Alternate video, image, video, image... so the 5 biggest are videos.
   For any new source name, add its Bangla spelling to `SRC_BN` in `engine/build_day.py`.
6. **Build:** `cd engine && python3 build_day.py ../days/<date>.json ../<date>/`
   This writes `post_XX_reel.mp4` (9:16 Reels) for videos and `post_XX.jpg` for images, plus `posts.json` and `captions.txt`.
   Open 2-3 of the images with Read to check that the Bangla text fits and renders correctly.
7. **Publish media:** `git add -A && git commit -m "Posts for <date>" && git push origin HEAD:main`.
   Then `curl -s -o /dev/null -w "%{http_code}"` each raw URL. Every one must return 200 before you go on.
8. **Schedule on Metricool**, one `createScheduledPost` per post, using `posts.json`:
   - `blogId` "7426819"; date `<date>T19:00:00+06:00`, then +12 minutes for each following post.
   - info: `providers [{"network":"facebook"}]`, `text` = caption, `firstCommentText` = first_comment,
     `media` = [raw URL], `autoPublish` true, `draft` false,
     `facebookData` {"type": posts.json "facebook_type"} — "REEL" for the .mp4 Reels, "POST" for images
     (for Reels also add "title": the short headline),
     `publicationDate` {dateTime, timezone "Asia/Dhaka"}, plus the other default fields.
   - If it is already past 19:00 when you get here, start 10 minutes from now instead.
9. **Report** with SendUserMessage, in Banglish: the 10 headlines with their times, and anything that went wrong.
   End with a "📢 Group-e share korun" section: the 2 posts most likely to spread (big international/quote/protest
   stories first) with their Metricool plannerUrl, and for each the kind of Facebook group to share it in
   (e.g. international politics, Middle East/probashi, Indian politics, football/cricket, positive Bangladesh).
   Remind: max 1–2 groups per day, share by hand.

## Never
- Post negative, government, political or controversial Bangladesh news.
- Post photos or AI-made faces of real people.
- Copy article text word for word.

## When Metricool can't take all posts (free plan: 20 posts per month)
- On **2026-10-16** only: pick, build and schedule just the **3 biggest** stories (19:00, 19:12, 19:24).
  Do not make the other 7 and do not hand anything over for manual posting.
- On any day, if `createScheduledPost` returns a plan/limit error, stop scheduling and tell the user in the report
  which posts could not be scheduled and that the paid Starter plan removes the limit.
