# Aggregate results (snapshot 2026-11-14)

Everything here is aggregate. No usernames, follower lists or per-account rows are published.

## Follower totals

| Measure | Value |
| --- | --- |
| Current follower records (`/api/followers/users`) | 9,638 |
| `total_followers` (`/api/analytics/follower_engagement`) | 10,235 |
| `engaged_followers` | 55 |
| Sum of daily `follows` from `/api/analytics/historical` | 10,235 |
| Days where every article reports the same `follows` value | 82 of 82 |

The gap between 10,235 and 9,638 is not explained. It is not treated as unfollows.

## Original audit CSV (1,409 rows)

| Column | Value in every row | Cause |
| --- | --- | --- |
| Following | 1 | `profile.get("followed_users_count", 1)`; field not returned by the API |
| Followers | 0 | default for a missing field |
| PostCount | 0 | default for a missing field |
| AvatarDefault | False | `endswith()` check never matches DEV's proxied image URLs |

| HeuristicScore | Rows | Reasons |
| --- | --- | --- |
| 1 | 510 | No posts |
| 2 | 877 | Empty bio; No posts |
| 3 | 22 | Suspicious username; Empty bio; No posts |

Rows scoring >= 2: 899. The saved flagged list also holds 899 names, including the two accounts the original post said were removed. The published 897 cannot be reproduced from the saved files.

## November 2025 ID block (user IDs 3,610,947 to 3,619,885)

| Measure | Value |
| --- | --- |
| Current followers in the block | 338 |
| Exact ID matches with the original audit | 338 of 338 |
| Follow timestamps in November 2025 | 338 of 338 (Nov 14 to 20) |
| Followers in equal-sized neighbouring ID ranges | 0, 1, 0, 0 |
| Account IDs consistent with avatar-path IDs (all followers) | 9,620 of 9,620 |

## Followers vs non-followers created in the same ID windows

Non-follower samples: 40 accounts per window. Treat profile percentages as rough.

| ID window | Fully blank: followers | Fully blank: non-followers | Hash username: followers | Hash username: non-followers | Share of accounts in range that follow |
| --- | --- | --- | --- | --- | --- |
| Nov 2025 block | 52% | 65% | 30% | 50% | ~4% |
| May 20-26, 2026 | 49% | 57% | 51% | 47% | ~21% |
| Nov 2-4, 2026 | 55% | 60% | 38% | 37% | ~16% |
| Nov 10-13, 2026 | 51% | 60% | 37% | 50% | ~12% |

## Account age at follow

| Burst | Followers | Account created within 7 days before following |
| --- | --- | --- |
| May 20-26, 2026 | 2,328 | 2,323 |
| Nov 2-4, 2026 | 950 | 946 |
| Nov 10-13, 2026 | 945 | 942 |

Creation dates estimated from user ID, calibrated on 404 profiles (median error 0 days, 90th percentile 1 day).

## Follows vs days since last post (follower-list timestamps)

| Days since last post | Share of follows |
| --- | --- |
| Same day | 28.4% |
| 1-3 | 58.5% |
| 4-7 | 13.0% |
| 8-14 | 0.0% |
| 15-30 | 0.2% |
| 31+ | 0.0% |

Post dates shuffled within each month (3,000 shuffles) give a median of 49-59% of follows within 0-3 days after a post, against 86.8% observed (0 of 3,000 reached it). Excluding May and November 2026: 75.6% observed against ~30% expected. This is a timing association, not proof of mechanism.

## Known data problem

DEV's daily analytics has gaps: some days report views for posts published later, and follows that the follower list dates several days later. Date follows with the follower list's `created_at`, not the analytics.
