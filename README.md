# devto-follower-forensics

Evidence package for my correction of the May 2026 post "Found 897 Fake Followers on DEV.to".

The short version: three central claims in that post came from code defaults and a misread timeline, not from DEV's data. This repo has the code that caused it, the fix, the tests, and the aggregate numbers behind each finding, so you can check the correction or run the same analysis on your own account.

## November 20, 2026: DEV onboarding clarification

[demonstrated here] DEV Community support reports that new members on DEV.to see up to 20 tag-based suggested authors, preselected by default, and that this behavior was active in May and November 2026. [unknown] DEV cannot identify which authors each new user saw or how individual follows originated. This supports a plausible **platform-level explanation**, not proven attribution for this account. See the [evidence addendum](evidence/dev_onboarding_reply_2026-11-20.md) and [updated aggregate interpretation](results/summary.md). The private support email and screenshots are retained outside the public repository.

## What's here

| Path | What it is |
| --- | --- |
| `scoring/devto_audit_core_ORIGINAL.py` | Archival copy of the audit code behind the original post, unchanged apart from a header comment. The `Following=1` bug is the `followed_users_count` line. It also has an indentation error and does not run as-is; see the header. |
| `scoring/devto_audit_core_FIXED.py` | Fixed version: missing API fields are recorded as missing, never filled with defaults. |
| `tests/test_audit_core.py` | Regression tests for the fix. Run with `python3 -m pytest tests`. |
| `data/CSV_NOTE.md` | Which columns of the original audit CSV are defaults, and how the published count arose. |
| `results/summary.md` | Aggregate tables for every finding in the correction. |
| `scripts/` | The analysis scripts, runnable against your own DEV account. |

## What's deliberately not here

No usernames, follower lists, profile caches or the original 1,409-row CSV. The original post labelled real people as bots. Publishing their accounts here would repeat that harm.

## Running the scripts on your own account

Python 3 standard library only. Put your DEV API key (Settings, Extensions) in a file named `.devto_key` in the folder you run from. The scripts write their caches as JSON files there with owner-only permissions. `.gitignore` keeps both out of git.

Run in this order:

1. `waves.py` pulls your full follower list (`followers_all.json`) and shows follows per day.
2. `dig.py` checks whether `/analytics/historical` `follows` is account-wide, rebuilds the daily history, and compares profiles of burst-day and quiet-day followers.
3. `cohort.py` estimates each follower's account creation date from their user ID.
4. `baseline.py` samples accounts that do not follow you from the same ID ranges, for a real baseline.
5. `timing.py` looks at the spacing and order of follows on burst days.
6. `cadence.py` relates follows to days since your last post.
7. `report_card.py` prints a fixed-format summary (window, records, blanks) for comparing results across accounts. Post its output when you share numbers.

`cohort.py` and `baseline.py` have my burst windows and ID range written in as constants. Change them to your own.

## Caveats

- DEV's daily analytics has gaps: some days carry views and follows that belong to later days. Date follows with the follower list's own `created_at`.
- `/api/followers/users` returns a `created_at` per follow even though the docs don't list it. That could change.
- DEV's public user endpoints return no follower, following or post counts, so those signals can't be measured from outside.
- The link between follows and posting is a timing association. It doesn't show which DEV feature produced the follows.
