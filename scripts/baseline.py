import json, os, re, time, random, urllib.request, urllib.error
from collections import Counter
KEY = open(".devto_key").read().strip()
B = "https://dev.to/api"
def get(path):
    req = urllib.request.Request(B + path, headers={
        "api-key": KEY, "accept": "application/vnd.forem.api-v1+json", "user-agent": "baseline/0.1"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(6 * (attempt + 1)); continue
            return {"_err": e.code}
        except Exception: time.sleep(3)
    return {"_err": "timeout"}
def save(fn, o): json.dump(o, open(fn, "w")); os.chmod(fn, 0o600)

fol = json.load(open("followers_all.json"))
fids = {f["user_id"] for f in fol}
d = lambda f: f["created_at"][:10]
def idrange(a, b):
    ids = sorted(f["user_id"] for f in fol if a <= d(f) <= b)
    return ids[len(ids)//20], ids[-len(ids)//20 - 1]   # trim 5% outliers each side
W = {"INV-001 block": (3_610_947, 3_619_885),
     "May 20-26":     idrange("2026-05-20", "2026-05-26"),
     "Nov 2-4":       idrange("2026-11-02", "2026-11-04"),
     "Nov 10-13":     idrange("2026-11-10", "2026-11-13")}

TARGET, MAXTRY = 40, 120
cache = json.load(open("baseline.json")) if os.path.exists("baseline.json") else {}
random.seed(11)
for name, (lo, hi) in W.items():
    pool = [i for i in range(lo, hi + 1) if i not in fids]
    random.shuffle(pool)
    got = sum(1 for k, v in cache.items() if lo <= int(k) <= hi and int(k) not in fids and "_err" not in v)
    tries = 0
    print(f"{name}: ids {lo}..{hi}  sampling non-followers...")
    for uid in pool:
        if got >= TARGET or tries >= MAXTRY: break
        if str(uid) in cache: continue
        cache[str(uid)] = get(f"/users/{uid}"); tries += 1
        if "_err" not in cache[str(uid)]: got += 1
        if tries % 25 == 0: save("baseline.json", cache); print(f"  tried {tries}, valid {got}")
        time.sleep(0.6)
save("baseline.json", cache)

# Follower side: same sample size per window, fetched by user id into profiles.json
# (the cache dig.py uses), so this script needs nothing that isn't in this repo.
pc = json.load(open("profiles.json")) if os.path.exists("profiles.json") else {}
random.seed(12)
for name, (lo, hi) in W.items():
    in_win = sorted(f["user_id"] for f in fol if lo <= f["user_id"] <= hi)
    random.shuffle(in_win)
    have = sum(1 for u in in_win if isinstance(pc.get(str(u)), dict) and "_err" not in pc[str(u)])
    todo = [u for u in in_win if str(u) not in pc][:max(0, TARGET - have)]
    if todo: print(f"{name}: fetching {len(todo)} follower profiles")
    for i, uid in enumerate(todo, 1):
        pc[str(uid)] = get(f"/users/{uid}")
        if i % 25 == 0: save("profiles.json", pc)
        time.sleep(0.6)
save("profiles.json", pc)
prof = {v["id"]: v for v in pc.values() if isinstance(v, dict) and "_err" not in v and v.get("id")}

def sig(p):
    u = p.get("username", "")
    return (bool(re.search(r"_[a-f0-9]{6,}$", u)), not (p.get("summary") or "").strip(),
            not any(p.get(k) for k in ("github_username", "website_url", "summary", "location", "twitter_username")))
def row(label, ps):
    if not ps: print(f"  {label:22s} n=0"); return
    s = [sig(p) for p in ps]; n = len(s)
    print(f"  {label:22s} n={n:3d}  hash:{sum(x[0] for x in s)*100//n:3d}%  "
          f"emptybio:{sum(x[1] for x in s)*100//n:3d}%  fully blank:{sum(x[2] for x in s)*100//n:3d}%")

print("\n== FOLLOWERS vs NON-FOLLOWERS created in the same ID windows ==")
for name, (lo, hi) in W.items():
    tried = [(int(k), v) for k, v in cache.items() if lo <= int(k) <= hi and int(k) not in fids]
    valid = [v for _, v in tried if "_err" not in v]
    miss = len(tried) - len(valid)
    fol_in = [f for f in fol if lo <= f["user_id"] <= hi]
    print(f"\n[{name}] window {lo}..{hi} ({hi-lo+1} ids)")
    row("non-followers", valid)
    row("your followers", [prof[f["user_id"]] for f in fol_in if f["user_id"] in prof])
    if tried:
        live = len(valid) / len(tried)
        est_accts = (hi - lo + 1) * live
        print(f"  non-follower ids missing/404: {miss}/{len(tried)} ({miss*100//len(tried)}%)")
        print(f"  est. live accounts in window: ~{est_accts:.0f}   following you: {len(fol_in)}  "
              f"-> ~{len(fol_in)/max(est_accts,1)*100:.0f}% of everyone created then follows you")

# what do profile image URLs look like now? (to fix the default-avatar check)
pats = Counter(re.sub(r"\d+", "N", re.sub(r"\?.*", "", (v.get("profile_image") or "")))[:90]
               for v in list(cache.values()) + list(prof.values()) if isinstance(v, dict) and "_err" not in v)
print("\nprofile_image URL patterns (digits->N):")
for p, c in pats.most_common(6): print(f"  {c:4d}  {p}")
