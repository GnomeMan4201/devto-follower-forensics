# DEV onboarding clarification — 2026-11-20

**Status:** Additive evidence update to the November 14, 2026 follower snapshot. Historical analysis is preserved.

## Primary-source status

[demonstrated here] On November 20, 2026, DEV Community support replied to the researcher's inquiry about follower acquisition and described current onboarding behavior, including its configuration in May and November 2026. This correspondence is retained privately; the raw email and screenshots are deliberately **not** published in this repository. DEV's [March 2018 onboarding announcement](https://dev.to/ben/changelog-suggested-follows-on-onboarding-3ifb) publicly documents the origin of the feature, but is not evidence of its exact 2026 settings.

## What DEV staff reported

- [demonstrated here] On DEV.to, new members select tags and see **up to 20 suggested authors, all preselected by default**. DEV says this was in place during May and November 2026. Its root-community pathway recommends communities rather than authors and is not the DEV.to pathway.
- [demonstrated here] Suggested authors are selected randomly from authors of **recent, high-scoring posts** in the selected tags. Staff said a well-performing post could put its author in that pool temporarily.
- [demonstrated here] DEV says it **does not retain which authors appeared in each user's suggestions**. Follow records do not identify a source, so the platform cannot provide counts separating onboarding from manual follows, even in aggregate.

The staff reply is a source for **platform behavior**, not an impression log or proof of account-specific exposure.

## Measured or reported follower patterns

- [reported by me] The November 14 snapshot contained **9,638** current follow records.
- [reported by me] The follow-up analysis found **7,809 / 9,638 = 81.02%** of records timestamped within a **rolling 72-hour period after a publication**, against **50.30% median** across 3,000 shuffled publication calendars that preserved month, weekday and time of day.
- [unknown] The above shuffle result has **not been independently rerun for this addendum**; underlying random seeds, inputs and code should be attached for third-party reproduction.

**Definition warning:** The original [aggregate results](../results/summary.md) also report **86.8%** within **0–3 calendar days since the last post**, versus a **49–59%** median in an earlier shuffle. A rolling 72-hour window and a calendar-day bin are not interchangeable; the two reported analyses must not be combined or silently substituted.

## Corrected interpretation

[demonstrated here] The platform has a recommendation mechanism capable of producing publication-proximate follows without any coordinated fake-account activity. [assumed] That mechanism **could** account for some of this account's bursts.

[unknown] Neither DEV nor this research has established that **@GnomeMan4201 was displayed** in suggestions on the relevant dates, what share of follows came through onboarding, or which accounts (if any) were automated.

**Conclusion:** The data support a strong temporal association between publishing and follow timestamps. The DEV reply supplies a plausible alternative mechanism but does **not** establish causation or an onboarding percentage. Temporal concentration alone cannot support a numerical fake-follower count or attribution to an organized campaign. The existing [public correction](https://dev.to/gnomeman4201/correcting-897-fake-followers-what-my-own-follower-data-actually-shows-f1p) remains controlling over claims in the original May report.

## Next test and kill criterion

Request the definitions and time bounds for `recent`, `high-scoring`, and author eligibility; ask whether eligibility can be reconstructed from public post metadata. Pre-register eligibility predictions **before** examining future follower timestamps, and compare predicted 72-hour follower changes with a posting-cadence-preserving baseline.

**Kill criterion:** If independently specified eligibility fails to improve out-of-sample prediction relative to the baseline, stop treating onboarding eligibility as the leading account-specific explanation. If eligibility cannot be observed, the causal test remains **unresolved**, not negative.

## Evidence handling

Original support email: received **2026-11-20 20:23 UTC**, with screenshots and source identifiers retained privately by the researcher. No personal follower records or private mail screenshots are committed here.
