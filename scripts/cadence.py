import json, statistics as st, urllib.request
from collections import Counter, defaultdict
from datetime import date, timedelta
KEY = open(".devto_key").read().strip()
def get(path):
    req = urllib.request.Request("https://dev.to/api" + path, headers={
        "api-key": KEY, "accept": "application/vnd.forem.api-v1+json", "user-agent": "cadence2/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

# follows dated by the follower list's own timestamps (analytics daily data has gaps)
follows = Counter(f["created_at"][:10] for f in json.load(open("followers_all.json")))
src = "current follower list"

arts = []; p = 1
while True:
    b = get(f"/articles/me/published?per_page=1000&page={p}")
    if not b: break
    arts += b; p += 1
pubs = sorted(date.fromisoformat(a["published_at"][:10]) for a in arts)
tags_by_day = defaultdict(list)
for a in arts: tags_by_day[a["published_at"][:10]] += a.get("tag_list") or []

start, end = pubs[0], date(2026, 11, 14)
rows, d = [], start
while d <= end:
    prev = [x for x in pubs if x <= d]
    gap = (d - prev[-1]).days if prev else None
    rows.append((d, gap, follows.get(d.isoformat(), 0)))
    d += timedelta(days=1)

print(f"source: {src}; posts: {len(pubs)}; days: {len(rows)}\n")
print("days since your last post | days | mean follows/day | median | share of all follows")
total = sum(r[2] for r in rows) or 1
for lo, hi, lab in ((0, 0, "same day"), (1, 3, "1-3"), (4, 7, "4-7"), (8, 14, "8-14"), (15, 30, "15-30"), (31, 9999, "31+")):
    v = [r[2] for r in rows if r[1] is not None and lo <= r[1] <= hi]
    if v: print(f"  {lab:24s} | {len(v):4d} | {st.mean(v):8.1f} | {st.median(v):6.0f} | {sum(v)*100/total:5.1f}%")

print("\nlongest stretches with zero follows, and your posting in them:")
runs, cur = [], []
for r in rows:
    if r[2] == 0: cur.append(r)
    else:
        if len(cur) >= 10: runs.append(cur)
        cur = []
if len(cur) >= 10: runs.append(cur)
for c in sorted(runs, key=len, reverse=True)[:5]:
    inside = [x for x in pubs if c[0][0] <= x <= c[-1][0]]
    print(f"  {c[0][0]} -> {c[-1][0]} ({len(c)} days): posts published inside: {len(inside)}")

print("\ntags on posts published within 3 days before each of the 10 biggest follow days:")
for d0, n in sorted(follows.items(), key=lambda x: -x[1])[:10]:
    dd = date.fromisoformat(d0)
    t = Counter(t for k in range(0, 4) for t in tags_by_day.get((dd - timedelta(days=k)).isoformat(), []))
    print(f"  {d0} ({n} follows): {dict(t.most_common(5)) or 'no post in prior 3 days'}")
