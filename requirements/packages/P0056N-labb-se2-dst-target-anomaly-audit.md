# Package P0056N: LABB SE2 DST and target anomaly audit

## Status

completed

## Package order

P0056N

## Label

```text
LABB
```

## Purpose

Investigate whether SE2 DayAhead forecast errors and extreme target values around the spring daylight-saving-time transition are caused by time handling, duplicated/missing local hours, target aggregation errors, or source-data anomalies.

This package is a diagnostic/audit package before any further model changes.

## Background

P0056M found that SE2 M6 realistic DayAhead errors are worst during high-load/high-ramp periods and that the strongest suspicious case is:

```text
delivery_date = 2026-03-28
mean_actual_load_mw = 5487.607639
mean_forecast_load_mw = 1800.414999
hourly_MAE = 3708.638703
bias_mw = -3687.192640
daily_energy_error_percent = 67.191259
```

Neighboring P0056M day means were near normal SE2 levels:

```text
2026-03-25 ≈ 1827.781 MW
2026-03-26 ≈ 2224.083 MW
2026-03-27 ≈ 1829.590 MW
2026-03-28 ≈ 5487.608 MW
2026-03-29 ≈ 1822.521 MW
2026-03-30 ≈ 1929.917 MW
2026-03-31 ≈ 1984.622 MW
```

The Swedish/European DST switch to summer time occurs around the night 2026-03-29, so P0056N must audit the local-day and UTC handling around this period.

## Scope

Primary audit period:

```text
2026-03-25T00:00 Europe/Stockholm through 2026-03-31T23:00 Europe/Stockholm
```

Also audit the five worst P0056M days, especially December worst cases, if present in P0056M evidence.

Area:

```text
SE2
```

Model context:

```text
P0056K/P0056M M6 WeightedEnsemble_no_price
```

Do not retrain or improve the model in this package.

## Questions to answer

P0056N must answer:

```text
1. Does SE2 actual load around 2026-03-28 contain duplicate timestamps?
2. Does SE2 actual load around 2026-03-28 contain missing timestamps?
3. Does the local day 2026-03-29 correctly have 23 hours in Europe/Stockholm?
4. Are UTC timestamps unique and monotonic across the DST change?
5. Are local timestamps converted correctly from UTC to Europe/Stockholm?
6. Are delivery-day boundaries built correctly for 23/24/25-hour local days?
7. Is 2026-03-28 an actual source anomaly, aggregation bug, target-definition shift, or real load regime?
8. Does the 2026-03-28 extreme appear already in the raw/native source rows?
9. Does the hourly aggregation count/resolution look normal around the anomaly?
10. Are forecast-origin and target-hour rows aligned correctly through the DST change?
11. Do P0056M hour rows show duplicate-looking local times around 2026-03-29, and if so is it expected DST behavior or a bug?
12. Should 2026-03-28 and related rows be flagged/excluded/labeled in future model evaluation?
```

## Required data checks

For the primary audit window, report for SE2:

```text
raw/native row count per UTC day
raw/native row count per local day
hourly row count per UTC day
hourly row count per local day
unique UTC timestamp count
duplicate UTC timestamp count
missing UTC hours
local timestamp duplicate count
local timestamp missing/nonexistent hour handling
local day length in hours
min/max/mean actual load per day
largest hourly actual values
top 20 actual-load spikes
source resolution distribution if available
aggregation count per hourly row if available
```

## Required DST-specific checks

Explicitly verify:

```text
Europe/Stockholm 2026-03-29 has no local 02:00 hour after spring-forward.
UTC-to-local conversion does not create invalid local target rows.
DayAhead delivery-day extraction does not silently force 24 rows for a 23-hour local day.
If the emulator requires 24 delivery positions, document how the missing DST hour is represented.
```

If the project has chosen a UTC-based market-day representation, document that and verify the mapping is consistent.

## Required target anomaly checks

For 2026-03-28, compare:

```text
hourly actual series
raw/native series
aggregation counts
neighbor days
same weekday prior week
same weekday next week
same local hour prior week
weather conditions
holiday/day-type flags
known DST proximity
```

Classify the anomaly as one of:

```text
confirmed_target_source_anomaly
probable_target_source_anomaly
confirmed_time/DST_bug
probable_time/DST_bug
confirmed_real_load_regime
probable_real_load_regime
inconclusive
```

## Required forecast alignment checks

For P0056M/P0056K reconstructed M6 rows around 2026-03-25..2026-03-31:

```text
forecast_origin_utc
forecast_origin_local
delivery_date_local
target_timestamp_utc
target_timestamp_local
horizon_h
local_hour
is_duplicate_local_hour
is_missing_local_hour_expected_by_DST
actual_mw
forecast_mw
error_mw
```

Verify that horizons and local delivery-day rows make sense across the transition.

## Required evidence files

Create:

```text
requirements/package-runs/P0056N/CHANGELOG.md
requirements/package-runs/P0056N/review.md
requirements/package-runs/P0056N/design.md
requirements/package-runs/P0056N/functions.md
requirements/package-runs/P0056N/labb-label.md
requirements/package-runs/P0056N/p0056m-baseline-review.md
requirements/package-runs/P0056N/audit-window.md
requirements/package-runs/P0056N/raw-native-row-audit.md
requirements/package-runs/P0056N/hourly-row-audit.md
requirements/package-runs/P0056N/dst-local-day-audit.md
requirements/package-runs/P0056N/utc-local-mapping-audit.md
requirements/package-runs/P0056N/target-anomaly-2026-03-28.md
requirements/package-runs/P0056N/neighbor-day-comparison.md
requirements/package-runs/P0056N/forecast-row-alignment-audit.md
requirements/package-runs/P0056N/top-spikes.md
requirements/package-runs/P0056N/classification.md
requirements/package-runs/P0056N/decision.md
requirements/package-runs/P0056N/what-we-learned.md
requirements/package-runs/P0056N/next-package-recommendation.md
```

Optional compact evidence:

```text
raw-native-row-audit.csv
hourly-row-audit.csv
dst-local-day-audit.csv
forecast-row-alignment-audit.csv
top-spikes.csv
classification.json
```

Do not commit large raw source dumps.

## Files to inspect

```text
requirements/package-runs/P0056M/forecast-error-interpretation.md
requirements/package-runs/P0056M/day-level-results.md
requirements/package-runs/P0056M/top-5-worst-tests.md
requirements/package-runs/P0056M/hour-level-summary.md
requirements/package-runs/P0056M/leakage-review.md
requirements/package-runs/P0056K/dayahead-protocol.md
requirements/package-runs/P0056K/lag-protocol.md
requirements/package-runs/P0056K/area-model-results.md
src/mac/** consumption ingestion, hourly aggregation, timezone and DayAhead forecast code
tests/mac/** timezone/DST and forecast-row alignment tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056N-labb-se2-dst-target-anomaly-audit.md
requirements/package-runs/P0056N/**
src/mac/** narrowly scoped audit/timezone diagnostics if needed
tests/mac/** narrowly scoped timezone/DST/audit tests if code is added
local DB audit views/tables if repo owns them and only for P0056N outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No model retraining or model logic changes.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No result rewriting to hide bad rows.
No large raw source dumps committed.
```

## Pass / WARN / STOP

PASS requires:

```text
primary audit window completed
DST/local-day behavior explicitly verified
2026-03-28 anomaly classified
raw/native and hourly target rows audited
forecast-row alignment across DST checked
clear decision on whether to flag/exclude/keep suspicious rows
```

WARN is acceptable if:

```text
raw/native source rows are unavailable but hourly rows can be audited
classification remains inconclusive but next diagnostic is clear
some optional December worst cases are deferred
```

STOP if:

```text
SE2 target rows for the audit window cannot be loaded
UTC/local mapping cannot be reconstructed
DayAhead delivery-day rows cannot be mapped to target timestamps
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
whether DST handling is correct
whether 2026-03-29 has correct 23-hour local day handling
whether duplicate/missing UTC/local timestamps exist
2026-03-28 anomaly classification
raw/native vs hourly evidence
forecast-row alignment result
recommendation: flag/exclude/keep rows
recommended next package
files changed
tests/commands run
confirmation no runtime/device/model/production changes
```

## Completion notes

Completed by Codex in package-run evidence:

```text
requirements/package-runs/P0056N/
```

Result:

```text
PASS
```

Rows audited:

```text
native_rows = 1235
hourly_rows = 311
p0056m_hour_rows = 168
forecast_alignment_rows = 168
```

DST result:

```text
Europe/Stockholm 2026-03-29 has 23 valid local hours.
Local 02:00 does not exist.
P0056K currently emits 24 delivery positions.
P0056K/P0056M duplicate one UTC target on 2026-03-29.
```

2026-03-28 anomaly classification:

```text
classification = probable_target_source_anomaly
source_observed_in_native_rows = true
hourly_timestamp_shape_normal_for_day = true
hourly_coverage_complete_for_day = false
top_spike_actual_mw = 7279.0
native_mean_mw = 5505.787234042553
hourly_mean_actual_mw = 5487.60763888889
```

Decision:

```text
Flag 2026-03-28 as probable source anomaly and exclude it from model selection until independently verified.
Fix or special-case DayAhead delivery-day generation for 23h/25h local days before future realistic DayAhead comparisons.
No model changes are authorized by P0056N.
```

Safety:

```text
No API.
No devices.
No runtime changes.
No model retraining.
No production activation.
No spot-price, flow/exchange/A61/capacity or old physical_balance features.
No result rewriting to hide bad rows.
```
