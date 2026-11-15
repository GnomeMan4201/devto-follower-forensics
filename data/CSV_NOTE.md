# Data note: `devto_bot_audit_full.csv` (correction, 2026-11-15)

This file is kept unchanged as the historical record behind the May 2026
"897 fake followers" post. Several columns hold **code defaults, not data**.

## Columns that are defaults

`devto_audit_core.py` read fields that DEV's `/api/users/by_username` does not
return, and filled in a default when they were missing:

| Column | Value in all 1,409 rows | Source line (old code) |
| --- | --- | --- |
| `Following` | 1 | `profile.get("followed_users_count", 1)` |
| `Followers` | 0 | `profile.get("followers_count", 0)` |
| `PostCount` | 0 | `profile.get("public_articles_count", 0)` |
| `AvatarDefault` | False | `endswith("default_profile_image.png")` never matches DEV's proxied image URLs |

Treat these four columns as **unknown**. In particular, `Following=1` does not
show that any account followed only one user.

## Effect on `HeuristicScore`

"No posts" fired on every row because `PostCount` defaulted to 0.

| Score | Rows | Reasons |
| --- | --- | --- |
| 1 | 510 | No posts |
| 2 | 877 | Empty bio; No posts |
| 3 | 22 | Suspicious username; Empty bio; No posts |

The published 897 = rows scoring >= 2 (899) minus 2 false positives. In
effect it counts followers with an empty bio, which is not a bot signal on its
own: 65-80% of new DEV accounts that do not follow the author also have empty
bios (baseline sampled 2026-11-15).

## Usable columns

`Username`, `Bio`, `AvatarURL` (the path embeds the account ID) and
`JoinedDate` are real API values.

## Fix

`devto_audit_core.py` now records missing fields as blank and lists them in a
`MissingFields` column; scores only use fields the API returned. Regression
tests: `tests/test_audit_core.py`.
