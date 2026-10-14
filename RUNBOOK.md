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
3. **News research** (today's date, Dhaka time). Use WebSearch/WebFetch on sources such as
   prothomalo.com / en.prothomalo.com, thedailystar.net, bdnews24.com, tbsnews.net (Bangladesh), and
   aljazeera.com, bbc.com, reuters.com, apnews.com, espncricinfo.com, goal.com (international).
   - Bangladesh: at most 5 stories, ONLY positive/constructive ones (see the rules). No government,
     political, negative or controversial BD news, and no BD official's photo or name-led headline.
   - Fill the rest with the biggest international stories popular with Bangladeshi readers. Always 10 in total.
   - Verify every fact on the article page. Rewrite in your own Bangla words; never copy.
4. **Write `days/<YYYY-MM-DD>.json`** with the same shape as `days/2026-10-14.json`:
   ```
   {"date_bn": "...", "stories": [ {
      "cat": "bd" | "intl" | "econ" | "sports",
      "format": "video" | "image",
      "scene": "airport_fire"            (ONLY for an attack/fire at an airport or similar; otherwise omit),
      "motifs": ["smoke"] | ["plane"] | [] (optional extras for the generic scene),
      "short_bn": "card headline, max ~30 Bangla characters, so it fits 2 big lines",
      "title_bn": "full Bangla headline (first line of the caption)",
      "title_en": "English headline (used only as a random seed)",
      "caption_bn": "2-4 sentence Bangla summary, facts only, no opinion",
      "source": "Prothom Alo | The Daily Star | Al Jazeera | BBC | Reuters | ...",
      "url": "article URL" } ] }
   ```
   Order: biggest story first. Alternate video, image, video, image... so the 5 biggest are videos.
   For any new source name, add its Bangla spelling to `SRC_BN` in `engine/build_day.py`.
5. **Build:** `cd engine && python3 build_day.py ../days/<date>.json ../<date>/`
   This writes `post_01..10` (.mp4 for videos, .jpg for images), `posts.json` and `captions.txt`.
   Open 2-3 of the images with Read to check that the Bangla text fits and renders correctly.
6. **Publish media:** `git add -A && git commit -m "Posts for <date>" && git push origin HEAD:main`.
   Then `curl -s -o /dev/null -w "%{http_code}"` each raw URL. Every one must return 200 before you go on.
7. **Schedule on Metricool**, one `createScheduledPost` per post, using `posts.json`:
   - `blogId` "7426819"; date `<date>T19:00:00+06:00`, then +12 minutes for each following post.
   - info: `providers [{"network":"facebook"}]`, `text` = caption, `firstCommentText` = first_comment,
     `media` = [raw URL], `autoPublish` true, `draft` false,
     `facebookData` {"type":"POST"} (for videos also add "title": the short headline),
     `publicationDate` {dateTime, timezone "Asia/Dhaka"}, plus the other default fields.
   - If it is already past 19:00 when you get here, start 10 minutes from now instead.
8. **Report** with SendUserMessage, in Banglish: the 10 headlines with their times, and anything that went wrong.

## Never
- Post negative, government, political or controversial Bangladesh news.
- Post photos or AI-made faces of real people.
- Copy article text word for word.
