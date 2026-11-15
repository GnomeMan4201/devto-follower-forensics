import json, os, sys, time, random, re, urllib.request, urllib.error
from collections import Counter, defaultdict
from datetime import datetime
KEY = open(".devto_key").read().strip()
B = "https://dev.to/api"
def get(path):
    req = urllib.request.Request(B + path, headers={
        "api-key": KEY, "accept": "application/vnd.forem.api-v1+json",
        "user-agent": "dig/0.1"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(6 * (attempt + 1)); continue
            if e.code == 404: return None
            print("HTTP", e.code, path); return None
        except Exception as e:
            time.sleep(3)
    return None
def total(v):
    if isinstance(v, dict): return v.get("total", 0) or 0
    return v or 0
def save(fn, obj):
    json.dump(obj, open(fn, "w")); os.chmod(fn, 0o600)

fol = json.load(open("followers_all.json"))
fdays = Counter(f["created_at"][:10] for f in fol)

# ---------- PART 1: is article "follows" really account-wide? ----------
print("== PART 1: verify follows field ==")
if os.path.exists("hist_all.json"):
    hist = json.load(open("hist_all.json"))
else:
    arts, p = [], 1
    while True:
        b = get(f"/articles/me/published?per_page=1000&page={p}")
        if not b: break
        arts += b; p += 1
    hist = {}
    for i, a in enumerate(arts, 1):
        hist[str(a["id"])] = get(f"/analytics/historical?start=2025-07-01&article_id={a['id']}") or {}
        if i % 10 == 0: print(f"  fetched {i}/{len(arts)}")
        time.sleep(0.5)
    save("hist_all.json", hist)

per_day = defaultdict(list)
for aid, h in hist.items():
    for d, v in h.items():
        per_day[d].append(total(v.get("follows")))
days_nonzero = [d for d in per_day if any(per_day[d])]
identical = [d for d in days_nonzero if len(set(per_day[d])) == 1]
print(f"days with follows>0: {len(days_nonzero)}  identical across all articles: {len(identical)}")
for d, _ in fdays.most_common(5):
    vals = per_day.get(d, [])
    print(f"  {d}: {len(vals)} articles, distinct values: {sorted(set(vals))[:6]}")

# reconstructed true daily follows = most common value across articles
true = {d: Counter(v).most_common(1)[0][0] for d, v in per_day.items() if any(v)}
print("\nRECONSTRUCTED vs CURRENT LIST, by month")
tm, lm = Counter(), Counter()
for d, n in true.items(): tm[d[:7]] += n
for d, n in fdays.items(): lm[d[:7]] += n
for m in sorted(set(tm) | set(lm)):
    gone = tm[m] - lm[m]
    print(f"  {m}  followed:{tm[m]:5d}  still here:{lm[m]:5d}  gone:{gone:5d}")
print(f"  TOTAL followed:{sum(tm.values())}  still here:{sum(lm.values())}")
print("\nDAYS WHERE MOST FOLLOWERS VANISHED (gone >= 50)")
vanish = sorted(((true[d] - fdays.get(d, 0), d) for d in true), reverse=True)
for g, d in vanish[:12]:
    if g < 50: break
    print(f"  {d}  followed:{true[d]:4d}  still here:{fdays.get(d,0):4d}  gone:{g}")

# ---------- PART 2: who are the burst followers? ----------
print("\n== PART 2: burst vs control follower profiles ==")
def in_burst(d):
    return ("2026-05-20" <= d <= "2026-05-26") or ("2026-11-02" <= d <= "2026-11-04") \
        or ("2026-11-10" <= d <= "2026-11-13")
med = sorted(fdays.values())[len(fdays)//2]
quiet = {d for d, n in fdays.items() if n <= med}
burst = [f for f in fol if in_burst(f["created_at"][:10])]
ctrl = [f for f in fol if f["created_at"][:10] in quiet]
random.seed(42)
N = 150
groups = {"burst": random.sample(burst, min(N, len(burst))),
          "control": random.sample(ctrl, min(N, len(ctrl)))}
print(f"burst pool {len(burst)}, control pool {len(ctrl)} (quiet days <= {med}/day); sampling {N} each")

prof = json.load(open("profiles.json")) if os.path.exists("profiles.json") else {}
todo = [f for g in groups.values() for f in g if str(f["user_id"]) not in prof]
for i, f in enumerate(todo, 1):
    prof[str(f["user_id"])] = get(f"/users/{f['user_id']}")
    if i % 25 == 0: print(f"  profiles {i}/{len(todo)}"); save("profiles.json", prof)
    time.sleep(0.6)
save("profiles.json", prof)

def joined(p):
    s = (p or {}).get("joined_at") or ""
    for fmt in ("%b %d, %Y", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try: return datetime.strptime(s.strip(), fmt)
        except Exception: pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return datetime.strptime(m.group(1), "%Y-%m-%d") if m else None

for name, g in groups.items():
    n = len(g); gone = blank = gh = web = summ = loc = digits = 0
    fresh = 0; jm = Counter(); ages = []
    for f in g:
        p = prof.get(str(f["user_id"]))
        if not p: gone += 1; continue
        if p.get("github_username"): gh += 1
        if p.get("website_url"): web += 1
        if p.get("summary"): summ += 1
        if p.get("location"): loc += 1
        if not any(p.get(k) for k in ("github_username","website_url","summary","location","twitter_username")): blank += 1
        if re.search(r"\d{3,}$", p.get("username","")): digits += 1
        j = joined(p)
        if j:
            jm[j.strftime("%Y-%m")] += 1
            fd = datetime.strptime(f["created_at"][:10], "%Y-%m-%d")
            age = (fd - j).days; ages.append(age)
            if 0 <= age <= 30: fresh += 1
    ok = n - gone; pct = lambda x: f"{x/ok*100:5.1f}%" if ok else "  n/a"
    ages.sort()
    print(f"\n[{name}] n={n}  profile 404/missing: {gone}")
    print(f"  fully blank profile: {pct(blank)}   github: {pct(gh)}   website: {pct(web)}   bio: {pct(summ)}   location: {pct(loc)}")
    print(f"  username ends in 3+ digits: {pct(digits)}")
    print(f"  account <=30 days old when it followed you: {pct(fresh)}")
    if ages: print(f"  median account age at follow: {ages[len(ages)//2]} days")
    print("  top join months:", ", ".join(f"{m}:{c}" for m, c in jm.most_common(6)))
