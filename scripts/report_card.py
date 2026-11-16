#!/usr/bin/env python3
"""Print a comparable "report card" for a follower analysis, so results from
different accounts can be lined up. Run after waves.py (needs followers_all.json);
uses profile caches from dig.py / baseline.py / inv.py if present.

  python3 report_card.py            -> markdown block to paste into a comment

Three fixed sections:
  WINDOW  : first/last follow (UTC) and when the data was pulled
  RECORDS : what was counted, what was excluded and why
  BLANKS  : every missing/empty field counted separately, and how it was treated
No usernames are printed.
"""
import json, os
from datetime import datetime, timezone

def load(fn):
    return json.load(open(fn)) if os.path.exists(fn) else None

fol = load("followers_all.json")
if fol is None:
    raise SystemExit("followers_all.json not found - run waves.py first")

pulled = datetime.fromtimestamp(os.path.getmtime("followers_all.json"), timezone.utc)
stamps = sorted(f.get("created_at") for f in fol if f.get("created_at"))
no_ts = sum(1 for f in fol if not f.get("created_at"))
ids = [f.get("user_id") for f in fol]
dupes = len(ids) - len(set(ids))

eng = None
hist = load("hist_all.json")
# follower_engagement totals are not cached by the scripts; record if user saved them
fe = load("follower_engagement.json")
total_api = fe.get("total_followers") if isinstance(fe, dict) else None

profiles = {}
for fn in ("profiles.json", "by_username.json", "baseline.json"):
    d = load(fn) or {}
    for v in d.values():
        if isinstance(v, dict) and v.get("id"):
            profiles[v["id"]] = v
fids = {f["user_id"] for f in fol}
fp = [p for i, p in profiles.items() if i in fids]
errs = sum(1 for fn in ("profiles.json", "by_username.json") for v in (load(fn) or {}).values()
           if not isinstance(v, dict) or "_err" in v)

def blank(p, k):
    v = p.get(k)
    return v is None or (isinstance(v, str) and not v.strip())

print("```")
print("WINDOW")
print(f"  first follow (UTC) : {stamps[0] if stamps else 'n/a'}")
print(f"  last follow  (UTC) : {stamps[-1] if stamps else 'n/a'}")
print(f"  data pulled  (UTC) : {pulled:%Y-%m-%d %H:%M}")
print(f"  dating source      : follower-list created_at (not daily analytics, which has gaps)")
print("RECORDS")
print(f"  follower records   : {len(fol)}  (current followers only; unfollowed/removed accounts not included)")
if total_api is not None:
    print(f"  API total_followers: {total_api}  (gap {total_api - len(fol)} unexplained, not treated as unfollows)")
print(f"  excluded           : {dupes} duplicate ids, {no_ts} records without created_at")
print(f"  profiles fetched   : {len(fp)} of {len(fol)} followers ({errs} lookups failed and were dropped)")
print("BLANKS (followers with a fetched profile)")
if fp:
    for k, label in (("summary", "bio"), ("location", "location"), ("github_username", "github link"),
                     ("website_url", "website"), ("twitter_username", "twitter"), ("joined_at", "joined date")):
        n = sum(1 for p in fp if blank(p, k))
        print(f"  {label:<18} : {n} blank ({n * 100 // len(fp)}%)  -> kept as 'unknown', never filled")
    n = sum(1 for p in fp if not any(not blank(p, k) for k in ("summary", "location", "github_username", "website_url", "twitter_username")))
    print(f"  fully blank profile: {n} ({n * 100 // len(fp)}%)")
else:
    print("  no profile caches found (run dig.py / inv.py first)")
print("  follower/following/post counts: not returned by DEV's user API -> not measured (no defaults)")
print("```")
