# Package P0056H2: LABB 36h static-style lag comparison

## Status

completed - WARN

## Package order

P0056H2

## Label

```text
LABB
```

## Purpose

Rerun the P0056H 36h origin schedule, but build lag features in the same static-style way as the older P0056C/P0054 36h tests where lag and rolling load features are anchored at the forecast origin rather than recursively rebuilt per target hour.

The goal is to test whether older static performance returns when the 36h rolling-origin test receives the same lag information shape as the static tests.

## Scope

Required areas:

```text
SE1
SE2
SE3
FI
```

## Origin schedule

Use the same schedule as P0056H:

```text
origin_time_local = 06:00 Europe/Stockholm
origin_step_days = 5
horizon = 36 hours
first_origin_local >= 2025-06-01 06:00 Europe/Stockholm
```

## Static-style lag feature list

Use and confirm:

```text
area_consumption_lag_1h
area_consumption_lag_2h
area_consumption_lag_3h
area_consumption_lag_6h
area_consumption_lag_12h
area_consumption_lag_24h
area_consumption_lag_48h
area_consumption_lag_72h
area_consumption_lag_168h
area_consumption_roll_mean_6h
area_consumption_roll_mean_12h
area_consumption_roll_mean_24h
area_consumption_roll_mean_48h
area_consumption_roll_mean_168h
area_consumption_roll_min_24h
area_consumption_roll_max_24h
area_consumption_roll_std_24h
area_consumption_ramp_1h
area_consumption_ramp_24h
area_consumption_same_hour_24h_vs_168h
```

Static-style means these values are computed from the forecast origin's known historical load context, matching P0056C's `area_lag_features_at_origin` and `area_rolling_features_at_origin` behavior.

## Comparisons

Compare against:

```text
P0056C static baseline
P0056E best SE1 baseline
P0056F best SE2 baseline
P0056G weekly walk-forward
P0056H 36h lag-protocol run
```

Reference full36 values:

```text
SE1 123.509 MW
SE2 197.547 MW
SE3 250.928 MW
FI  311.189 MW
```

## Required evidence

Create:

```text
requirements/package-runs/P0056H2/CHANGELOG.md
requirements/package-runs/P0056H2/review.md
requirements/package-runs/P0056H2/design.md
requirements/package-runs/P0056H2/functions.md
requirements/package-runs/P0056H2/static-style-lag-contract.md
requirements/package-runs/P0056H2/lag-feature-list.md
requirements/package-runs/P0056H2/area-summary-results.md
requirements/package-runs/P0056H2/comparison-vs-static-baseline.md
requirements/package-runs/P0056H2/comparison-vs-p0056h.md
requirements/package-runs/P0056H2/comparison-vs-p0056g-weekly.md
requirements/package-runs/P0056H2/interpretation.md
requirements/package-runs/P0056H2/decision.md
requirements/package-runs/P0056H2/next-package-recommendation.md
```

Compact CSV/JSON evidence is allowed if useful.

## Files allowed to change

```text
requirements/packages/P0056H2-labb-36h-static-style-lag-comparison.md
requirements/package-runs/P0056H2/**
src/mac/services/spotprice_model_diagnostics/p0056h2.py
tests/mac/test_p0056h2_static_style_lags.py
```

## Forbidden changes

```text
No API.
No devices.
No runtime change.
No production activation.
No G2-KANDIDAT promotion.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No large model artifacts.
```

## Verification

Run equivalent checks for:

```text
origin schedule matches P0056H
static-style lag feature list is present
lag features are anchored at forecast origin
SE1/SE2/SE3/FI evaluated
metrics vs static baseline computed
metrics vs P0056H computed
metrics vs P0056G weekly computed
git diff --check
no large artifacts staged
```

## Expected Codex output

```text
PASS/WARN/STOP
commit SHA
areas evaluated
origin count per area
lag feature list confirmation
MAE vs static baseline
MAE vs P0056H
whether old static performance is recovered
interpretation and next recommendation
```

## Completion notes

Implemented as LABB-only diagnostic.

Result summary:

```text
status = WARN
areas = SE1, SE2, SE3, FI
scheduled_origin_jobs = 292
origin_results = 282
skipped_incomplete_origin_windows = 10
failed_jobs = 0
forecast_log_rows = 10152
metrics_rows = 6228
```

Origin count per area:

```text
SE1 67
SE2 71
SE3 71
FI  73
```

Mean MAE 0-36h:

```text
SE1 142.010 MW
SE2 228.549 MW
SE3 282.424 MW
FI  340.798 MW
```

Static-style lag feature count is 20 and the horizon-constant check passed.

Old static full36 performance was not recovered:

```text
SE1 +18.501 MW / +14.979% vs static baseline
SE2 +31.002 MW / +15.693% vs static baseline
SE3 +31.496 MW / +12.552% vs static baseline
FI  +29.609 MW /  +9.515% vs static baseline
```

P0056H2 improved over P0056H for SE2, SE3 and FI, but not SE1:

```text
SE1 +3.693 MW /  +2.670% vs P0056H
SE2 -14.030 MW / -5.784% vs P0056H
SE3 -79.457 MW / -21.957% vs P0056H
FI  -26.259 MW / -7.154% vs P0056H
```

Next recommendation: if the goal is to isolate the remaining gap to the old static result, run an exact P0056C weighted-ensemble rerun on the P0056H origin grid before more lag engineering.
