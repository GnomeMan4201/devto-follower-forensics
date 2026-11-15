import json, os, sys, time, urllib.request, urllib.error
from collections import Counter
KEY = open(".devto_key").read().strip()
B = "https://dev.to/api"
def get(path):
    req = urllib.request.Request(B + path, headers={
        "api-key": KEY, "accept": "application/vnd.forem.api-v1+json",
        "user-agent": "waves/0.1"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (attempt + 1)); continue
            print("HTTP", e.code, e.read()[:200]); sys.exit(1)
    print("rate limited, giving up"); sys.exit(1)

# 1. all followers
fol, page = [], 1
while True:
    batch = get(f"/followers/users?per_page=1000&page={page}&sort=-created_at")
    if not batch: break
    fol += batch; print(f"page {page}: {len(batch)}"); page += 1; time.sleep(1)
json.dump(fol, open("followers_all.json", "w")); os.chmod("followers_all.json", 0o600)

days = Counter(f["created_at"][:10] for f in fol if f.get("created_at"))
missing = sum(1 for f in fol if not f.get("created_at"))
dates = sorted(days)
print(f"\nfollowers: {len(fol)}  missing created_at: {missing}")
if dates:
    print(f"range: {dates[0]} -> {dates[-1]}  active days: {len(dates)}")
    vals = sorted(days.values()); med = vals[len(vals)//2]
    print(f"median follows/active day: {med}")
    print("\ntop 15 days:")
    for d, n in days.most_common(15):
        print(f"  {d}  {n:5d}  {'#' * min(n, 60)}")
    months = Counter(d[:7] for d in days.elements())
    print("\nby month:")
    for m in sorted(months):
        print(f"  {m}  {months[m]:5d}")

# 2. engagement totals (numbers only)
print("\nfollower_engagement:", get("/analytics/follower_engagement"))

# 3. history depth on your OLDEST published article
arts, p = [], 1
while True:
    b = get(f"/articles/me/published?per_page=1000&page={p}")
    if not b: break
    arts += b; p += 1
if arts:
    old = min(arts, key=lambda a: a["published_at"])
    h = get(f"/analytics/historical?start=2015-01-01&article_id={old['id']}")
    ks = sorted(h)
    print(f"\noldest article published {old['published_at'][:10]}: "
          f"{len(ks)} days of history, {ks[0] if ks else '-'} -> {ks[-1] if ks else '-'}")
    if ks: print("sample day fields:", sorted(h[ks[-1]]))
