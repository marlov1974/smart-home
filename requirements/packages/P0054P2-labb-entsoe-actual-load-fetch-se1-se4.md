# Package P0054P2: LABB ENTSO-E actual load fetch SE1-SE4

## Status

completed

## Package order

P0054P2

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Retry P0054P by explicitly loading ENTSO-E actual load / consumption data for Swedish bidding zones SE1, SE2, SE3 and SE4 from 2022-06-01 onward.

P0054P stopped because no local ENTSO-E load/consumption source was found. The operator now requests loading the data from 2022-06-01 and forward.

Important clarification:

```text
The uploaded file named GUI_NET_CROSS_BORDER_PHYSICAL_FLOWS_202512312300-202612312300.csv is physical cross-border flow data, not consumption/load data.
It must not be used as SE1-SE4 consumption target.
It may be documented as a future candidate for the later flow/export-import level, but it is out of scope for this consumption-target package.
```

## Scope boundary

This package is source ingestion and validation only.

It must not rerun consumption forecast models. A later package should rerun SE3 DayAhead/full_36h modeling after the ENTSO-E actual load target is validated.

Recommended follow-up:

```text
P0054Q LABB SE3 DayAhead full_36h rerun with ENTSO-E actual load target
```

## Core questions

P0054P2 must answer:

```text
1. Can ENTSO-E actual load / total load data be loaded for SE1, SE2, SE3 and SE4 from 2022-06-01 onward?
2. What exact source/export/API convention was used?
3. What local canonical table/view should downstream packages use?
4. Do SE3 volumes match expected order of magnitude?
5. How do ENTSO-E SE1-SE4 targets compare with the old physical_balance source?
6. Does this explain the P0054O percent-error discrepancy?
7. Should P0054K-P0054O be relabeled as proxy-target experiments?
```

## Required source type

Use ENTSO-E load/consumption data, not physical flow data.

Acceptable source concepts:

```text
Actual Total Load
Total Load - Actual
Actual Load
ENTSO-E Transparency Platform load time series by bidding zone / area
```

Forbidden as consumption target:

```text
Net cross-border physical flows
A09/A11 flow or exchange data
A61 capacity data
production data
price data
```

## Data access policy

Operator-approved task for this package:

```text
Load ENTSO-E actual load data from 2022-06-01 onward for SE1, SE2, SE3 and SE4.
```

Codex may use an existing local project ingestion path, local exported files, or an already configured ENTSO-E load download workflow on the operator machine.

Do not commit credentials or raw large exports.

If access credentials or manual export steps are missing, STOP with exact instructions for what file/export is needed.

## Desired canonical output

Preferred table/view:

```text
entsoe_consumption_area_hourly_v1
```

Required semantics:

```text
timestamp_utc
area
consumption_mw
source_system = ENTSO-E
source_measure = actual_total_load or equivalent
source_area_code if available
resolution
unit
timezone_handling
package_id = P0054P2
```

If ENTSO-E provides 15-minute or other subhourly resolution, aggregate to hourly mean MW and document the conversion.

## Coverage requirements

Required period:

```text
start: 2022-06-01T00:00:00Z
end: latest_available_timestamp_utc
```

Coverage must include:

```text
train_fit: 2022-06-01T00:00:00Z <= timestamp_utc < 2025-06-01T00:00:00Z
holdout:   timestamp_utc >= 2025-06-01T00:00:00Z
```

SE3 must have sufficient train_fit and holdout coverage for a meaningful P0054Q rerun. SE1, SE2 and SE4 should also be loaded and validated.

## Volume sanity checks

Season definitions:

```text
winter_half_year = October through March
summer_half_year = April through September
```

For each area and season report:

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

SE3 expectation from operator:

```text
winter half-year: roughly 12_000..15_000 MW typical high/seasonal level
summer half-year: roughly 6_000..8_000 MW typical level
```

If those ranges align better with p75/p95/peak than with seasonal mean, document that. Do not fail only because mean and p95 differ; fail only if the series is clearly the wrong order of magnitude or wrong unit.

## Old-source comparison

Compare ENTSO-E targets with the old source where available:

```text
physical_balance_se1_se4_hourly_v1.consumption_se1
physical_balance_se1_se4_hourly_v1.consumption_se2
physical_balance_se1_se4_hourly_v1.consumption_se3
physical_balance_se1_se4_hourly_v1.consumption_se4
```

For each overlapping area compute:

```text
old_mean_mw
entsoe_mean_mw
ratio_entsoe_to_old
mean_difference_mw
correlation if timestamp-aligned
overlap_rows
```

Special SE3 diagnostic:

```text
Explain why P0054O used an apparent DayAhead mean actual around 2.3 GW while expected total SE3 load is much higher.
```

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

## Cross-border flow file handling

If the uploaded or local file is found:

```text
GUI_NET_CROSS_BORDER_PHYSICAL_FLOWS_202512312300-202612312300.csv
```

then classify it as:

```text
source_type = cross_border_physical_flow
usable_for_consumption_target = false
possible_future_use = flow/export-import forecast packages
```

Do not load it into `entsoe_consumption_area_hourly_v1`.

## Downstream policy

If P0054P2 validates ENTSO-E actual load targets, future Swedish consumption forecast packages must use:

```text
entsoe_consumption_area_hourly_v1
```

instead of:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
```

P0054K-P0054O should then be interpreted as:

```text
proxy-target methodology experiments, not validated total-SE3-load forecast experiments
```

unless P0054P2 proves the old source is equivalent.

## Required evidence files

Create:

```text
requirements/package-runs/P0054P2/CHANGELOG.md
requirements/package-runs/P0054P2/review.md
requirements/package-runs/P0054P2/design.md
requirements/package-runs/P0054P2/functions.md
requirements/package-runs/P0054P2/labb-label.md
requirements/package-runs/P0054P2/source-discovery.md
requirements/package-runs/P0054P2/entsoe-actual-load-source-contract.md
requirements/package-runs/P0054P2/area-code-mapping.md
requirements/package-runs/P0054P2/table-schema.md
requirements/package-runs/P0054P2/coverage-by-area.md
requirements/package-runs/P0054P2/volume-sanity-by-area-season.md
requirements/package-runs/P0054P2/se3-volume-check.md
requirements/package-runs/P0054P2/old-source-comparison.md
requirements/package-runs/P0054P2/cross-border-flow-file-classification.md
requirements/package-runs/P0054P2/data-quality-review.md
requirements/package-runs/P0054P2/downstream-contract-for-p0054q.md
requirements/package-runs/P0054P2/impact-on-p0054k-through-p0054o.md
requirements/package-runs/P0054P2/what-we-learned.md
requirements/package-runs/P0054P2/next-package-recommendation.md
```

Optional compact evidence:

```text
coverage-summary.json
volume-sanity-summary.json
old-source-comparison.csv
area-season-volume-summary.csv
missing-hours-by-area.csv
```

Do not commit raw large ENTSO-E exports.

## Files to inspect

```text
requirements/package-runs/P0054P/CHANGELOG.md
requirements/package-runs/P0054K/dataset-contract.md
requirements/package-runs/P0054N/dataset-contract.md
requirements/package-runs/P0054O/percent-error-results.md
requirements/package-runs/P0054O/review.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local SQLite metadata for feature database
local files/docs/scripts mentioning ENTSO-E, entsoe, load, actual total load
local operator-provided exports under accepted local data directories
```

## Files allowed to change

```text
requirements/packages/P0054P2-labb-entsoe-actual-load-fetch-se1-se4.md
requirements/package-runs/P0054P2/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped ENTSO-E actual-load ingestion/validation code if needed
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
No consumption model retraining in this package.
No cross-border flow file used as load target.
No credentials committed.
No large raw data commits.
No broad refactor unrelated to P0054P2.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
ENTSO-E actual load source exists or STOP reason is clear
SE1-SE4 targets exist or limitations are documented
schema/table/view contract documented
coverage by area and split computed
volume sanity by area and season computed
SE3 checked against winter/summer expectation
old physical_balance source compared to ENTSO-E where possible
cross-border flow file classified as not-load if present
no duplicate area/timestamp rows
no negative loads
DST/timezone handling documented
git diff --check
no large raw data artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- ENTSO-E actual-load hourly targets for SE1, SE2, SE3 and SE4 are available or built locally.
- train_fit and holdout coverage are sufficient for future modeling.
- SE3 volume sanity is in the correct order of magnitude and documented.
- canonical downstream table/view contract is explicit.
- old-source comparison explains the P0054K-P0054O discrepancy.
```

WARN is acceptable if:

```text
- SE3 is complete and usable but one of SE1/SE2/SE4 has coverage limitations.
- source requires operator-managed local export refresh but current export is sufficient.
- operator expected ranges align better with p95/peak than seasonal mean and this is documented.
```

STOP if:

```text
- no ENTSO-E actual load source can be accessed locally or through approved project workflow.
- SE3 cannot be built with enough train_fit and holdout coverage.
- volumes remain clearly wrong or unit/timestamp semantics cannot be resolved.
- only cross-border physical flow data is available.
```

## Expected Codex output

```text
PASS/WARN/STOP status
ENTSO-E actual load source used
canonical table/view name
SE1-SE4 coverage summary
SE1-SE4 seasonal volume sanity summary
SE3 winter/summer sanity result
comparison against old physical_balance source
classification of uploaded cross-border flow file if relevant
impact on P0054K-P0054O interpretation
whether P0054Q should rerun SE3 DayAhead/full_36h models
commands/tests run
files changed
confirmation no device/runtime/NordPool/workplace integration
confirmation no credentials or large raw data committed
commit SHA after push
```

## Completion notes

P0054P2 completed with PASS.

Implemented a package-scoped ENTSO-E Actual Total Load ingestion module and tests:

```text
src/mac/services/spotprice_model_diagnostics/p0054p2.py
tests/mac/services/spotprice_model_diagnostics/test_p0054p2.py
```

Canonical local table built:

```text
entsoe_consumption_area_hourly_v1
```

Loaded row counts:

```text
raw_rows = 192905
hourly_rows = 140175
```

Loaded area coverage:

```text
SE1 35001 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
SE2 35026 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
SE3 35125 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
SE4 35023 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
```

Source contract:

```text
documentType = A65
processType = A16
source_type = actual_total_load
area_scope = bidding_zone_internal_consumption_or_load
usable_for_consumption_target = true
```

Cross-border flow data was not used as consumption target. The named cross-border physical flow export was classified as not usable for `entsoe_consumption_area_hourly_v1`.

Old-source comparison found the old physical-balance source is not equivalent to ENTSO-E Actual Total Load. For SE3, ENTSO-E overlap mean was 9501.266 MW versus old-source mean 3933.028 MW, ratio 2.415764 and correlation 0.232260. P0054K-P0054O should be interpreted as proxy-target methodology experiments until rerun against the ENTSO-E actual-load target.

Recommended follow-up remains:

```text
P0054Q LABB SE3 DayAhead full_36h rerun with ENTSO-E actual load target
```
