# Top 10 Breaking News — Editorial rules

Page name: **Top 10 Breaking News**. Logo: "TOP 10" with "BREAKING NEWS BD" underneath.
Audience: people in Bangladesh. All captions and headlines are in Bangla only.

## Daily schedule (11 Reels, since 2026-10-24, user's rule)
- **News Reels at 12:30, 13:00, 14:00, 15:00, 17:00, 17:20, 17:40, 18:00, 18:15, 18:30** (10 a day).
- **16:00: "২৪ ঘণ্টার সেরা ১০" roundup** of the PREVIOUS day's 10 best news Reels by views, best first.
  See RUNBOOK step 8b.
- Nothing before 12:30 or after 18:30 (data 19-22 Oct: 12:00 and 19:00-22:00 Reels mostly got under 50 views,
  13:00-18:00 Reels got 170-990).

## Daily content plan (user's instructions, 2026-10-20; data 17-20 Oct: 12:00-20:00 posts got 150-577 views)
- **Bangladesh: at least 3, at most 5 good Bangladesh-related news Reels every day** (user's rule, 2026-10-23),
  out of the 10 news Reels. Counts: positive Bangladesh news (economy, remittance, exports, development projects,
  sports wins, achievements), probashi/expat news (jobs abroad, flights to and from Bangladesh, Bangladeshis in the
  Gulf/Malaysia/Europe), and what foreign leaders/media say about Bangladesh. All of them must pass the Bangladesh
  filter below (good news only, no politics). Aim for 1-2 in the 11:30 batch; the 15:30 batch tops up to at least 3
  and never goes above 5 for the day. Spread them out, never two Bangladesh Reels back to back.
- **2-3 war stories every day, in prime time 14:00-18:30 (16:00 is the roundup):** the Iran war, the US/Israel-Palestine war, Hormuz,
  the Houthi-Saudi war. Facts from reliable outlets.
- **At least ONE every day:** an analysis/opinion piece from a well-known outlet (Foreign Affairs, Al Jazeera,
  The Guardian, Middle East Eye, Responsible Statecraft, Prothom Alo's translated columns, etc.) or by a named
  diplomat/analyst that argues Iran is holding its own or winning, or is critical of the US/Israel war; OR real
  news that is bad for the US in this war (losses, costs, allies pulling back, failed goals). Rules: the piece
  must really exist and say that; attribute it ("বিশ্লেষণ: <name>") and label opinion as opinion in the caption;
  never invent claims or quotes. Use the Iran leaders painting as the background:
  `"bg_image": "assets/bg_iran_leaders.jpg"`.
- **Painted photo backgrounds (engine/assets, from the user's photos, 2026-10-21).** When a story is mainly
  about one of these people or places, ALWAYS set `"bg_image"` to one of their files (rotate the variants so
  back-to-back Reels don't look the same; check today's posts):
  | Story about | bg_image files |
  |---|---|
  | Donald Trump | assets/bg_trump.jpg, bg_trump_2.jpg, bg_trump_3.jpg, bg_trump_4.jpg |
  | Vladimir Putin | assets/bg_putin_1.jpg, bg_putin_2.jpg |
  | Kim Jong Un | assets/bg_kim.jpg |
  | Xi Jinping | assets/bg_xi.jpg |
  | Narendra Modi | assets/bg_modi_1.jpg, bg_modi_2.jpg |
  | Neha Bora / Delhi Gen-Z protest | assets/bg_neha.jpg, bg_neha_2.jpg, bg_neha_3.jpg |
  | Abhijeet Dipke / Cockroach Janta Party | assets/bg_abhijit_1.jpg, bg_abhijit_2.jpg |
  | Mojtaba Khamenei (Iran's Supreme Leader) | assets/bg_mojtaba_1.jpg, bg_mojtaba_2.jpg |
  | Masoud Pezeshkian (Iran's President) | assets/bg_pezeshkian.jpg |
  | Abbas Araghchi (Iran's FM) | assets/bg_araghchi.jpg |
  | Pro-Iran analysis / Iran leadership in general | assets/bg_iran_leaders.jpg |
  | Iran war / Hormuz / Iran vs US-Israel (art poster: Iran leader, Xi, Putin, Trump, Netanyahu, Hormuz; user's image 2026-10-23) | assets/bg_iran_hormuz_war.jpg |
  | Bangladesh (country-level good news, Bangladesh abroad) | assets/bg_bangladesh.jpg |
  | Dhaka (city news) | assets/bg_dhaka.jpg |
  If several people fit, use the one the headline is about. For Iran-war/Hormuz stories with no single main person, rotate bg_iran_hormuz_war.jpg and bg_iran_leaders.jpg. Wide scene photos (not one person) are painted with specials/paint_wide.py. New photos from the user: paint them with
  specials/neha_poster.py (`reel_background`, see /tmp batch script pattern in git history) and add a row here.
- Fill the other slots with what works: Saudi/Gulf + probashi news (best performer), Bangladesh big breaking news
  (per the user's instructions), Delhi protest. Skip analysis pieces with no Bangladesh or war angle.
- The user will send more photos to paint; when one arrives, use it (painted with specials/neha_poster.py
  reel_background, as done for Neha, Ishraque, Trump and the Iran leaders).

## Daily mix
- **Bangladesh angle first.** Page data (14-17 Oct) shows the most views and watch time on stories that touch
  Bangladesh: Neha Bora saying "Bangladesh showed us the way", Saudi flight cancellations stranding Bangladeshi
  passengers, and the Delhi Cockroach protest. Look first for: Bangladeshi expats/probashi (Gulf, Malaysia, Italy…),
  flights, what foreign leaders/media say about Bangladesh, Bangladeshis abroad, positive Bangladesh news.
- **3-5 Bangladesh** stories a day (see "Daily content plan"), and only ones that pass the Bangladesh filter below.
- Fill every remaining slot with **international** stories, so the evening total is always 7.
- **All posts are motion Reels (videos).** No still images: Reels reach 2-3x more people than images on this Page
  (checked 2026-10-17), so every story uses format "video" with its animated theme.
  Every Reel has original news-style background music, same style as the 22:00 roundup (added 2026-10-18).
- **Music (since 2026-10-19):** every Reel and the roundup start with the same ~1.6 s "Top 10" signature jingle
  (brand sound). The bed underneath follows the story's mood (engine/music.py mood_of): tense = war/attacks,
  hopeful = good Bangladesh/economy/development news, protest = protests/US politics, sports = football/cricket,
  calm = quote posts and diplomacy. A story can force one with "mood": "tense|hopeful|protest|sports|calm".
- **Reels must hold attention** (viewers were leaving after 2-5 s with the old 9 s static loop). Each story has
  `points_bn`: 3-4 short, punchy facts that appear one by one, most surprising first, with numbers where possible.

## Bangladesh filter (strict)
ONLY include:
- Positive, constructive, good-vibes stories: achievements, success stories, happy news.
- Positive economy news: export growth, remittance up, new investment, jobs, records.
- Good promises and progress: new opportunities, people helping people.
- Positive development projects, even when the government runs them: a new railway, bridge,
  metro, road, port or power plant approved, opened or progressing. Report only the project
  facts (route, benefit, cost, timeline). Never praise or criticise a party or politician, and
  never use a minister's or official's name or photo as the headline.
- Good positive news is always encouraged.
- Sports wins, science/tech/education achievements, culture and celebrations.

NEVER include:
- Negative BD news (crime, accidents, disasters, crises, bank troubles, price hikes, bad forecasts).
- Government/political news (politics, elections, party statements, policy rows), political
  criticism, controversial stories. Exception: the positive development projects allowed above.
- No comment or opinion on any of the above.
- No photo of any Bangladeshi Prime Minister, President, minister or government official. No person photos for BD stories at all.

## International (the BD filter does NOT apply)
Pick the day's biggest stories, favouring what is popular with the Bangladeshi audience:
- Donald Trump and US politics; USA, Russia (Putin), China, North Korea.
- Ukraine war; the current Middle East war; Muslim countries.
- Protest movements: Nepal, Sri Lanka, India's "cockroach" protests.
- India politics, including stories critical of BJP / Modi.
- Middle East, Malaysia, Singapore, Japan, Korea.
- Football and cricket.

### Quote posts (very popular in Bangladesh, use them often)
Pick 2–3 strong, newsworthy **quotes** every day from leaders and figures Bangladeshis follow, such as:
Donald Trump, Vladimir Putin, Xi Jinping, Kim Jong Un, Iran's Supreme Leader / President / FM,
Hamas leaders, Houthi leaders, Hezbollah, Erdoğan, Netanyahu, Rahul Gandhi, Arvind Kejriwal,
Mamata Banerjee, Neha Bora and other Indian student/Gen-Z leaders, Pakistan's PM Shehbaz Sharif
and army chief, Imran Khan, Zelensky, and similar.
- Quote card: `short_bn` = the quote in ‘single quotes’ (short, 2 lines max), `quote_by` = "<name>, <role>".
- Only use quotes that a reliable source actually reports. Translate faithfully; never invent or sharpen a quote.
- Quotes ABOUT Bangladesh (praise, ties, deals) are especially popular, so prioritise them.
- Bangladeshi politicians are NOT used for quote posts (Bangladesh rules above still apply).

### Cockroach movement / India Gen-Z protests
The "Cockroach Janta Party" (CJP) and the Gen-Z protests in Delhi (against CEC Gyanesh Kumar / SIR)
are very popular. Check for new developments every day and include the biggest one when there is
real news (detentions, marches, statements, court or Election Commission moves). Use the "protest" theme.

Tone: report facts from the source only. Do not add our own opinion, insults or one-sided wording, even on political stories.

## Every post
- Image/video headline: short and punchy, 2 lines max, in large type in the centre of the card.
- Card shows the source name ("সূত্র: …"). No category/rank tag.
- Caption in Bangla: headline + 2–4 lines of summary + "📰 সূত্র: <source> (লিংক কমেন্টে 👇)" + hashtags.
- First comment: "📰 বিস্তারিত পড়ুন (<source>):" + article link.
- Captions are always rewritten in our own words, never copied.
- Every card has an animated, illustrated theme that matches the story (war, protest, USA, world,
  economy, bridge, football, cricket, airport_fire, or abstract). Never a plain background.
- Symbolic illustrated scenes only. No AI-made faces of real people, and no copyrighted news photos.
