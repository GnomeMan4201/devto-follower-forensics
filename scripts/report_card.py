#!/usr/bin/env python3
"""Print a comparable "report card" for a follower analysis, so results from
different accounts can be lined up. Run after waves.py (needs followers_all.json);
uses profile caches from dig.py / baseline.py if present.

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
no_id = sum(1 for f in fol if f.get("user_id") is None)
no_ts = sum(1 for f in fol if f.get("user_id") is not None and not f.get("created_at"))
seen, kept, dupes = set(), [], 0
for f in fol:
    uid = f.get("user_id")
    if uid is None or not f.get("created_at"):
        continue
    if uid in seen:
        dupes += 1
        continue
    seen.add(uid); kept.append(f)
stamps = sorted(f["created_at"] for f in kept)
# follower_engagement totals are not cached by the scripts; record if user saved them
fe = load("follower_engagement.json")
total_api = fe.get("total_followers") if isinstance(fe, dict) else None

profiles = {}
for fn in ("profiles.json", "by_username.json", "baseline.json"):
    d = load(fn) or {}
    for v in d.values():
        if isinstance(v, dict) and v.get("id"):
            profiles[v["id"]] = v
fids = {f["user_id"] for f in kept}
fp = [p for i, p in profiles.items() if i in fids]
pc = load("profiles.json") or {}   # dig.py keys this by follower user_id
errs = sum(1 for k, v in pc.items() if k.isdigit() and int(k) in fids
           and (not isinstance(v, dict) or "_err" in v))

def blank(p, k):
    v = p.get(k)
    return v is None or (isinstance(v, str) and not v.strip())

print("```")
print("WINDOW")
print(f"  first follow (UTC) : {stamps[0] if stamps else 'n/a'}")
print(f"  last follow  (UTC) : {stamps[-1] if stamps else 'n/a'}")
print(f"  data pulled  (UTC) : {pulled:%Y-%m-%d %H:%M}  (followers_all.json modified time)")
print(f"  dating source      : follower-list created_at (not daily analytics, which has gaps)")
print("RECORDS")
print(f"  rows returned      : {len(fol)}  (current followers only; unfollowed/removed accounts not included)")
print(f"  excluded           : {dupes} duplicate ids, {no_ts} without created_at, {no_id} without user_id")
print(f"  counted            : {len(kept)}  (window and profiles use only these)")
if total_api is not None:
    print(f"  API total_followers: {total_api}  (gap {total_api - len(kept)} unexplained, not treated as unfollows)")
print(f"  profiles fetched   : {len(fp)} of {len(kept)} counted ({errs} follower lookups failed and were dropped)")
print("BLANKS (counted followers with a fetched profile; this is the scripts' sample,")
print("        weighted toward burst days by dig.py, not a random sample of all followers)")
if fp:
    for k, label in (("summary", "bio"), ("location", "location"), ("github_username", "github link"),
                     ("website_url", "website"), ("twitter_username", "twitter"), ("joined_at", "joined date")):
        n = sum(1 for p in fp if blank(p, k))
        print(f"  {label:<18} : {n} blank ({n * 100 // len(fp)}%)  -> kept as 'unknown', never filled")
    n = sum(1 for p in fp if not any(not blank(p, k) for k in ("summary", "location", "github_username", "website_url", "twitter_username")))
    print(f"  fully blank profile: {n} ({n * 100 // len(fp)}%)")
else:
    print("  no profile caches found (run dig.py first)")
print("  follower/following/post counts: not returned by DEV's user API -> not measured (no defaults)")
print("```")
