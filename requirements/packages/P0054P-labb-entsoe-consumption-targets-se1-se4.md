# Package P0054P: LABB ENTSO-E consumption targets SE1-SE4

## Status

planned

## Package order

P0054P

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Build and validate new Swedish bidding-zone consumption targets from ENTSO-E load data for:

```text
SE1
SE2
SE3
SE4
```

This replaces the unverified SE3 target used in P0054K-P0054O:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
```

P0054K-P0054O showed suspiciously low SE3 load levels compared with the operator's expected SE3 magnitude. P0054P must verify a corrected ENTSO-E-based consumption target before further SE3 DayAhead/full_36h modeling is trusted.

The operator expectation for SE3 is grid-scale effect/load, interpreted as GW-level values:

```text
winter half-year: roughly 12-15 GW
summer half-year: roughly 6-8 GW
```

If earlier wording used kW, treat that as a unit typo for grid-scale load sanity checking.

## Scope boundary

This package is source construction and validation only.

It must not rerun consumption models. A later package should rerun SE3 DayAhead/full_36h modeling with the corrected target.

Recommended follow-up:

```text
P0054Q LABB SE3 DayAhead full_36h rerun with ENTSO-E target
```

## Core questions

P0054P must answer:

```text
1. Is there a local ENTSO-E load source usable for SE1-SE4 consumption targets?
2. Can hourly SE1, SE2, SE3 and SE4 consumption_mw targets be built from it?
3. Does SE3 have plausible winter and summer volume levels?
4. What are the corresponding volume levels for SE1, SE2 and SE4?
5. How different is ENTSO-E SE3 from physical_balance_se1_se4_hourly_v1.consumption_se3?
6. Should P0054K-P0054O be treated as proxy-target method experiments rather than total-SE3-load experiments?
7. What canonical table or view should downstream packages use?
```

## Source policy

Use only local/repository-available ENTSO-E data or local exports already present on the operator machine.

Do not perform external data fetching in this package. If the required ENTSO-E data is not locally available, STOP and document the missing local dataset/export needed.

Do not store secrets or raw large exports in the repository.

## Desired canonical output

Preferred table or view:

```text
entsoe_consumption_area_hourly_v1
```

Required semantics:

```text
timestamp_utc
area
consumption_mw
source_system = ENTSO-E
source_measure
source_area_code if available
resolution
unit
timezone_handling
package_id = P0054P
```

If a durable table already exists, P0054P may validate and document that table instead of recreating it.

## Period coverage

Required for future P0054Q model reruns:

```text
train_fit: 2022-06-01T00:00:00Z <= timestamp_utc < 2025-06-01T00:00:00Z
holdout:   timestamp_utc >= 2025-06-01T00:00:00Z
```

Preferred coverage continues to latest locally available timestamp.

STOP if SE3 cannot cover enough train_fit and holdout rows for a meaningful rerun.

WARN is acceptable if SE3 is complete but one of SE1, SE2 or SE4 has limited coverage.

## Volume sanity checks

Season definitions:

```text
winter_half_year = October through March
summer_half_year = April through September
```

For each area and season compute:

```text
row_count
mean_mw
median_mw
p05_mw
p25_mw
p75_mw
p95_mw
min_mw
max_mw
daily_energy_gwh_mean
daily_energy_gwh_median
```

SE3 must be checked against the operator expectation:

```text
winter: roughly 12_000..15_000 MW
summer: roughly 6_000..8_000 MW
```

Do not fail only because mean, median, p95 and peak differ. Explain which statistic best matches the expectation and whether the series is in the correct order of magnitude.

## Old-source comparison

Compare ENTSO-E targets against the old local source where columns exist:

```text
physical_balance_se1_se4_hourly_v1.consumption_se1
physical_balance_se1_se4_hourly_v1.consumption_se2
physical_balance_se1_se4_hourly_v1.consumption_se3
physical_balance_se1_se4_hourly_v1.consumption_se4
```

For each overlapping area and period compute:

```text
old_mean_mw
entsoe_mean_mw
ratio_entsoe_to_old
mean_difference_mw
correlation if timestamps align
overlap_rows
```

This comparison must explain why P0054O produced percent errors using an apparent DayAhead mean actual around 2.3 GW while expected total SE3 load is much higher.

## Data quality checks

Required:

```text
no duplicate area/timestamp rows
timestamps normalized to UTC
resolution documented
DST handling documented
no negative load values
missing-hour count by area and split
large gaps listed
area mapping documented
unit documented
```

## Downstream policy

If ENTSO-E passes validation, future Swedish consumption forecast packages must use the P0054P canonical ENTSO-E target instead of:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
```

P0054K-P0054O should then be labeled:

```text
proxy-target methodology experiments, not validated total-SE3-load forecast experiments
```

unless P0054P proves the old source is equivalent.

## Required evidence files

Create:

```text
requirements/package-runs/P0054P/CHANGELOG.md
requirements/package-runs/P0054P/review.md
requirements/package-runs/P0054P/design.md
requirements/package-runs/P0054P/functions.md
requirements/package-runs/P0054P/labb-label.md
requirements/package-runs/P0054P/source-discovery.md
requirements/package-runs/P0054P/entsoe-source-contract.md
requirements/package-runs/P0054P/area-code-mapping.md
requirements/package-runs/P0054P/table-schema.md
requirements/package-runs/P0054P/coverage-by-area.md
requirements/package-runs/P0054P/volume-sanity-by-area-season.md
requirements/package-runs/P0054P/se3-volume-check.md
requirements/package-runs/P0054P/old-source-comparison.md
requirements/package-runs/P0054P/data-quality-review.md
requirements/package-runs/P0054P/downstream-contract-for-p0054q.md
requirements/package-runs/P0054P/impact-on-p0054k-through-p0054o.md
requirements/package-runs/P0054P/what-we-learned.md
requirements/package-runs/P0054P/next-package-recommendation.md
```

Optional compact evidence:

```text
coverage-summary.json
volume-sanity-summary.json
old-source-comparison.csv
area-season-volume-summary.csv
missing-hours-by-area.csv
```

Do not commit large raw ENTSO-E exports. Commit compact summaries only.

## Files to inspect

```text
requirements/package-runs/P0054K/dataset-contract.md
requirements/package-runs/P0054N/dataset-contract.md
requirements/package-runs/P0054O/percent-error-results.md
requirements/package-runs/P0054O/review.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local SQLite metadata for feature database
local files/docs/scripts mentioning ENTSO-E, entsoe, load, actual total load
```

## Files allowed to change

```text
requirements/packages/P0054P-labb-entsoe-consumption-targets-se1-se4.md
requirements/package-runs/P0054P/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped local ENTSO-E target discovery/build/validation code if needed
tests/mac/** narrowly scoped tests for timestamp/area/schema/volume validation if code changes are made
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No DayAhead/Nord Pool/workplace integration.
No model retraining in this package.
No external data fetching in this package.
No large raw data commits.
No broad refactor unrelated to P0054P.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
local ENTSO-E source exists or STOP reason is clear
SE1-SE4 targets exist or limitations are documented
schema/table/view contract documented
coverage by area and split computed
volume sanity by area and season computed
SE3 checked against winter/summer expectation
old physical_balance source compared to ENTSO-E where possible
no duplicate area/timestamp rows
no negative loads
DST/timezone handling documented
git diff --check
no large raw data artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- ENTSO-E-based hourly targets for SE1, SE2, SE3 and SE4 are available or built locally.
- train_fit and holdout coverage are sufficient for future modeling.
- SE3 volume sanity is in the correct order of magnitude and documented.
- canonical downstream table/view contract is explicit.
- old-source comparison explains the P0054K-P0054O discrepancy.
```

WARN is acceptable if:

```text
- SE3 is complete and usable but one of SE1/SE2/SE4 has coverage limitations.
- source is a local ENTSO-E export rather than a pre-existing database table, if a validated table/view is created.
- operator expected ranges align better with p95/peak than seasonal mean and this is documented.
```

STOP if:

```text
- no local ENTSO-E source is available.
- SE3 cannot be built with enough train_fit and holdout coverage.
- volumes remain clearly wrong or unit/timestamp semantics cannot be resolved.
```

## Expected Codex output

```text
PASS/WARN/STOP status
ENTSO-E source used
canonical table/view name
SE1-SE4 coverage summary
SE1-SE4 seasonal volume sanity summary
SE3 winter/summer sanity result
comparison against old physical_balance source
impact on P0054K-P0054O interpretation
whether P0054Q should rerun SE3 DayAhead/full_36h models
commands/tests run
files changed
confirmation no external fetch/device/runtime/NordPool/workplace integration
confirmation no large raw data committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
