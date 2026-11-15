import json, re, bisect, statistics as st
from collections import Counter, defaultdict
from datetime import datetime, timedelta

fol = json.load(open("followers_all.json"))
prof = json.load(open("profiles.json"))
fd = lambda f: datetime.strptime(f["created_at"][:10], "%Y-%m-%d")

# ---------- 1. INV-001 November 2025 cohort ID range ----------
LO, HI = 3_610_947, 3_619_885
inr = [f for f in fol if LO <= f["user_id"] <= HI]
print(f"== 1. followers with user_id in INV-001 Nov-2025 range {LO}..{HI} ==")
print(f"  count: {len(inr)}  (range holds {HI-LO+1} ids)")
if inr:
    m = Counter(f["created_at"][:7] for f in inr)
    print("  followed you, by month:", dict(sorted(m.items())))
    d = Counter(f["created_at"][:10] for f in inr)
    print("  top follow days:", d.most_common(8))
# density check: how packed is this range vs neighbouring ranges of the same width?
w = HI - LO + 1
for name, lo in (("range-2w", LO - 2*w), ("range-1w", LO - w), ("INV-001", LO), ("range+1w", LO + w), ("range+2w", LO + 2*w)):
    print(f"    {name:9s} {lo}..{lo+w-1}: {sum(1 for f in fol if lo <= f['user_id'] < lo+w)} followers")

# ---------- 2. estimate every follower's creation date from user_id ----------
def jdate(p):
    s = (p or {}).get("joined_at") or ""
    for fmt in ("%b %d, %Y", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try: return datetime.strptime(s.strip(), fmt)
        except Exception: pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return datetime.strptime(m.group(1), "%Y-%m-%d") if m else None
cal = sorted((int(k), jdate(v)) for k, v in prof.items() if v and jdate(v))
# enforce monotonic (ids are assigned in creation order)
ids, dates, best = [], [], datetime(2000, 1, 1)
for i, d in cal:
    best = max(best, d); ids.append(i); dates.append(best)
print(f"\n== 2. creation-date model from {len(ids)} profiles: id {ids[0]}..{ids[-1]} ==")
def est(uid):
    j = bisect.bisect_left(ids, uid)
    if j == 0 or j >= len(ids): return None          # outside calibrated range
    i0, i1 = ids[j-1], ids[j]; d0, d1 = dates[j-1], dates[j]
    if i1 == i0: return d0
    return d0 + (d1 - d0) * ((uid - i0) / (i1 - i0))
# accuracy check: leave-one-out on calibration points
errs = []
for k in range(1, len(ids) - 1):
    i0, i1 = ids[k-1], ids[k+1]
    if i1 == i0: continue
    g = dates[k-1] + (dates[k+1] - dates[k-1]) * ((ids[k] - i0) / (i1 - i0))
    errs.append(abs((g - dates[k]).days))
if errs: print(f"  model error (leave-one-out): median {st.median(errs):.0f} days, 90th pct {sorted(errs)[int(len(errs)*.9)]} days")

# dormancy = follow date - estimated account creation date
by_month = defaultdict(list)
for f in fol:
    e = est(f["user_id"])
    if e: by_month[f["created_at"][:7]].append((fd(f) - e).days)
print("\n  follow month | n (in model) | median dormancy | share dormant >30d | >90d")
for m in sorted(by_month):
    v = by_month[m]
    print(f"  {m}      | {len(v):5d}        | {st.median(v):6.0f}d         | "
          f"{sum(x>30 for x in v)/len(v)*100:5.1f}%            | {sum(x>90 for x in v)/len(v)*100:5.1f}%")

# ---------- 3. burst windows specifically ----------
wins = {"May 20-26 2026": ("2026-05-20", "2026-05-26"),
        "Nov 2-4 2026": ("2026-11-02", "2026-11-04"),
        "Nov 10-13 2026": ("2026-11-10", "2026-11-13")}
print("\n== 3. burst windows: how old were the accounts? ==")
for name, (a, b) in wins.items():
    fs = [f for f in fol if a <= f["created_at"][:10] <= b]
    v = [(fd(f) - est(f["user_id"])).days for f in fs if est(f["user_id"])]
    if not v: continue
    v.sort()
    buckets = Counter("0-7d" if x <= 7 else "8-30d" if x <= 30 else "31-180d" if x <= 180 else ">180d" for x in v)
    print(f"  {name}: n={len(fs)} modelled={len(v)}  median age {st.median(v):.0f}d  "
          f"buckets {dict(buckets)}")
    created = Counter((est(f['user_id'])).strftime('%Y-%m') for f in fs if est(f['user_id']))
    print(f"    estimated creation months: {created.most_common(5)}")
