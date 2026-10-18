"""Merge several day JSON files into one stories file (for the 22:00 roundup).

Usage: python3 merge_day.py <out.json> <in1.json> [<in2.json> ...]   (missing inputs are skipped; max 10 stories)
"""
import json, os, sys

out, ins = sys.argv[1], sys.argv[2:]
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
json.dump({"date_bn": date_bn, "stories": stories[:10]}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"merged {len(stories[:10])} stories into {out}")
