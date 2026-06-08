# Package P0056I: LABB SE2 train-window sensitivity

## Status

planned

## Package order

P0056I

## Label

```text
LABB
```

## Purpose

Test whether SE2 forecast quality depends on training-window length.

The question is whether SE2 performs better with:

```text
rolling 2.0 years
rolling 3.0 years
expanding 3.X years from 2022-06-01
```

The package must keep everything else as close as possible to the latest 36h lag-comparison test, so the only intended variable is training-window length.

## Scope

Primary area:

```text
SE2
```

Do not run all areas in this package.

## Baseline to compare against

Compare against latest SE2 results from:

```text
P0056F W12 static full36 baseline: 197.547 MW
P0056H L2 recursive 36h: 242.579 MW
P0056H2 static-style lag comparison: 228.549 MW
P0056G weekly: 207.757 MW
```

If local evidence differs, use the latest committed package-run evidence and document it.

## Test protocol

Use the same protocol as P0056H2 unless explicitly documented:

```text
area = SE2
origin_time_local = 06:00 Europe/Stockholm
origin_step_days = 5
horizon = 36 hours
same origin schedule as P0056H/P0056H2
same target table
same weather protocol
same model method
same lag feature construction as P0056H2
same metrics
```

## Training-window variants

Run exactly these train-window variants:

### TW2 rolling 2.0 years

For each forecast origin:

```text
train_start = forecast_origin - 2 years
train_end = forecast_origin
```

### TW3 rolling 3.0 years

For each forecast origin:

```text
train_start = forecast_origin - 3 years
train_end = forecast_origin
```

### TWX expanding 3.X years

For each forecast origin:

```text
train_start = 2022-06-01T00:00:00Z
train_end = forecast_origin
```

This is the expanding window that grows beyond 3.0 years as the holdout period advances.

## Important comparison rule

Everything except `train_start` must remain fixed across TW2, TW3 and TWX.

Do not change:

```text
model method
feature set
lag feature construction
weather features
origin schedule
forecast horizon
metric definitions
```

If any difference is unavoidable, document it in the evidence and do not treat it as a clean train-window comparison.

## Lag features

Use the same lag list as P0056H2 / old static feature set:

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

## Metrics

For every origin and train-window variant report:

```text
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
MAE_0_36h
RMSE_0_36h
bias_0_36h
p90_absolute_error
p95_absolute_error
absolute_energy_error_MWh_36h
signed_energy_error_MWh_36h
energy_error_percent_36h
train_start
train_end
train_rows
```

Aggregate by train-window variant:

```text
origin_count
mean_MAE_0_36h
median_MAE_0_36h
mean_MAE_0_24h
mean_MAE_24_36h
weighted_MAE_percent_of_mean_load
mean_energy_error_percent
bias_over_period
weekday_split
monthly_split
```

## Required questions to answer

P0056I must answer:

```text
1. Is rolling 2.0 years better than rolling 3.0 years for SE2?
2. Is expanding 3.X better or worse than exact 3.0 years?
3. Does shorter training reduce bias or only MAE?
4. Does the best train-window explain any of the gap between P0056H2 and static baseline?
5. Which train-window should be used in the next emulator consumption protocol test?
```

## Decision rule

A train-window variant is preferred if it improves the best of TW2/TW3/TWX by at least:

```text
1 percent relative MAE_0_36h
or 3 percent relative energy error without worsening MAE by more than 0.5 percent
```

If differences are smaller, prefer the simpler and more stable protocol:

```text
TW3 rolling 3.0 years
```

unless expanding TWX is nearly equal and operationally simpler.

## Required evidence files

Create:

```text
requirements/package-runs/P0056I/CHANGELOG.md
requirements/package-runs/P0056I/review.md
requirements/package-runs/P0056I/design.md
requirements/package-runs/P0056I/functions.md
requirements/package-runs/P0056I/labb-label.md
requirements/package-runs/P0056I/baseline-review.md
requirements/package-runs/P0056I/origin-schedule.md
requirements/package-runs/P0056I/train-window-contract.md
requirements/package-runs/P0056I/lag-feature-list.md
requirements/package-runs/P0056I/input-source-contract.md
requirements/package-runs/P0056I/weather-protocol.md
requirements/package-runs/P0056I/model-method-contract.md
requirements/package-runs/P0056I/origin-results.md
requirements/package-runs/P0056I/window-summary-results.md
requirements/package-runs/P0056I/comparison-vs-baselines.md
requirements/package-runs/P0056I/interpretation.md
requirements/package-runs/P0056I/decision.md
requirements/package-runs/P0056I/what-we-learned.md
requirements/package-runs/P0056I/next-package-recommendation.md
```

Optional compact evidence:

```text
origin-results.csv
window-summary-results.csv
metrics-summary.json
```

Do not commit full prediction dumps, model binaries, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056H2/area-summary-results.md
requirements/package-runs/P0056H2/comparison-vs-static-baseline.md
requirements/package-runs/P0056H/area-summary-results.md
requirements/package-runs/P0056G/area-summary-results.md
requirements/package-runs/P0056F/feature-ablation-results.md
src/mac/** forecast/model/feature scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056I-labb-se2-train-window-sensitivity.md
requirements/package-runs/P0056I/**
src/mac/** narrowly scoped train-window comparison code if needed
tests/mac/** narrowly scoped tests if code is added
local DB metrics tables if repo owns them and only for P0056I outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No large model or prediction artifacts committed.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
SE2 origin count
train-window variants tested
TW2/TW3/TWX metrics
best train window
delta vs P0056H2
delta vs static baseline
interpretation and next recommendation
tests/commands run
files changed
confirmation diagnostic only and no large artifacts
```

## Completion notes

To be filled after implementation.
