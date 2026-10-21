"""Merge several day JSON files into one stories file (for the 22:00 roundup).

Usage: python3 merge_day.py [--order order.txt] <out.json> <in1.json> [<in2.json> ...]
  (missing inputs are skipped; max 10 stories)

--order order.txt: one article URL per line, best performer first (since 2026-10-21, user's idea).
  Stories whose url is listed come first in that order; every other story keeps its time order after them.
  So list the daytime Reels by views per hour and leave out the 20:00/21:00 Reels: they end up at 9 and 10.
"""
import json, os, sys

args = sys.argv[1:]
order = []
if args and args[0] == "--order":
    with open(args[1], encoding="utf-8") as f:
        order = [l.strip() for l in f if l.strip()]
    args = args[2:]
out, ins = args[0], args[1:]
stories, date_bn, seen = [], "", set()
for p in ins:
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding="utf-8"))
    date_bn = date_bn or d.get("date_bn", "")
    for s in d["stories"]:
        if s.get("url") not in seen:
            seen.add(s.get("url"))
            stories.append(s)
if order:
    rank = {u: i for i, u in enumerate(order)}
    ranked = sorted((s for s in stories if s.get("url") in rank), key=lambda s: rank[s["url"]])
    stories = ranked + [s for s in stories if s.get("url") not in rank]
json.dump({"date_bn": date_bn, "stories": stories[:10]}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"merged {len(stories[:10])} stories into {out}")
for i, s in enumerate(stories[:10], 1):
    print(i, s.get("short_bn", ""))
