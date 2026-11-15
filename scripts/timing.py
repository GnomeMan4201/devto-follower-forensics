import json, statistics as st
from collections import Counter, defaultdict
from datetime import datetime
fol = json.load(open("followers_all.json"))
def ts(f): return datetime.strptime(f["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
byday = defaultdict(list)
for f in fol: byday[f["created_at"][:10]].append(f)
med = sorted(len(v) for v in byday.values())[len(byday)//2]
def burst(d): return ("2026-05-20" <= d <= "2026-05-26") or ("2026-11-02" <= d <= "2026-11-04") \
    or ("2026-11-10" <= d <= "2026-11-13")

def analyze(label, days):
    gaps, same_sec, mono_up, mono_n, hours, runs = [], 0, 0, 0, Counter(), []
    hours_active = []
    for d in days:
        fs = sorted(byday[d], key=ts); t = [ts(f) for f in fs]
        hours.update(x.hour for x in t)
        hours_active.append(len({x.hour for x in t}))
        g = [(b - a).total_seconds() for a, b in zip(t, t[1:])]
        gaps += g; same_sec += sum(1 for x in g if x == 0)
        # longest run of follows each <=10s apart
        run = best = 1
        for x in g:
            run = run + 1 if x <= 10 else 1; best = max(best, run)
        runs.append(best)
        # does follower user_id rise with follow time? (new sign-ups get rising ids)
        u = [f["user_id"] for f in fs]
        mono_up += sum(1 for a, b in zip(u, u[1:]) if b > a); mono_n += len(u) - 1
    n = len(gaps)
    if not n: print(f"[{label}] no gaps"); return
    print(f"\n[{label}] days={len(days)} follows={n + len(days)}")
    print(f"  median gap: {st.median(gaps):.0f}s   gaps 0s: {same_sec/n*100:.1f}%   "
          f"<=5s: {sum(x<=5 for x in gaps)/n*100:.1f}%   <=60s: {sum(x<=60 for x in gaps)/n*100:.1f}%")
    print(f"  longest run (<=10s apart) per day, median/max: {st.median(runs):.0f}/{max(runs)}")
    print(f"  hours of day with any follow, median: {st.median(hours_active):.0f}/24")
    print(f"  consecutive follows where follower user_id increases: {mono_up/mono_n*100:.1f}%  (random order ~50%)")
    tot = sum(hours.values())
    print("  UTC hour profile:", " ".join(f"{h:02d}:{hours[h]*100//tot:>2d}" for h in range(24)))

bd = sorted(d for d in byday if burst(d))
qd = sorted(d for d in byday if not burst(d) and len(byday[d]) >= 10)
analyze("burst days", bd)
analyze("other days (>=10 follows)", qd)

# expected median gap if follows were spread randomly over 24h
for label, days in (("burst", bd), ("other", qd)):
    per = st.median(len(byday[d]) for d in days) if days else 0
    if per: print(f"\n{label}: median {per:.0f} follows/day -> random-arrival median gap ~{86400/per*0.693:.0f}s")

# user_id ranges: are burst followers a contiguous block of accounts?
ids = sorted(f["user_id"] for d in bd for f in byday[d])
if ids:
    span = ids[-1] - ids[0]
    print(f"\nburst follower user_id span: {ids[0]}..{ids[-1]} ({len(ids)} accounts across {span} ids)")
