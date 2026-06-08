# Package P0056G: LABB weekly walk-forward consumption emulator

## Status

completed

## Package order

P0056G

## Label

```text
LABB
```

## Purpose

Change the consumption forecast evaluation from one static one-year holdout to a market-emulator style weekly walk-forward simulation.

The emulator goal is to produce a high-quality spot-price forecast for one week. Therefore consumption forecasts should be evaluated in the same cadence the emulator will use:

```text
Every week:
  train using all data available through Sunday 24:00 local time
  at Monday 06:00 local time create a 7-day consumption forecast
  evaluate the following Monday-Sunday delivery week
```

This package tests whether weekly retraining helps areas such as SE1/SE2 where structural load changes, industrial expansion, data center expansion or other yearly changes may make a static one-year holdout unfair or too stale.

## Core hypothesis

SE1/SE2 may change too much year-to-year for a model trained once before the holdout year to be optimal.

Potential causes:

```text
industrial load changes
data center build-out
grid/large customer changes
mine or plant operational changes
new large load connections
structural demand trend
```

A weekly walk-forward retrain may adapt better than a static model.

## Areas in scope

Primary:

```text
SE1
SE2
```

Required controls:

```text
SE3
FI
```

Optional if runtime allows:

```text
NO3
NO4
```

Do not run all 18 areas unless runtime is clearly acceptable and progress/checkpointing is implemented.

## Baselines

Compare against latest committed results:

```text
P0056C multi-area static holdout
P0056D Open-Meteo weather retune
P0056E north model variants
P0056F weather feature ablation
```

Use the best current known candidate per area as static baseline:

```text
SE1: P0056E V2 or P0056F best, document exact chosen baseline
SE2: P0056D/P0056E/P0056F best, document exact chosen baseline
SE3: P0056C static baseline
FI:  P0056C/P0056D result, document exact chosen baseline
```

## Weekly emulation protocol

Use Europe/Stockholm local-time scheduling.

For each simulated week:

```text
training_cutoff = Sunday 24:00 Europe/Stockholm
forecast_origin = Monday 06:00 Europe/Stockholm
delivery_window = Monday 00:00 through Sunday 23:00 Europe/Stockholm
horizon = 168 delivery hours
```

Important: although forecast is created Monday 06:00, the delivery week starts at Monday 00:00. The package must explicitly document how the first 6 hours are handled:

```text
Option A: include Monday 00:00-05:00 as nowcast/backcast hours if actuals would be known by 06:00
Option B: evaluate Monday 06:00 through Sunday 23:00 only for pure forward forecast
Option C: report both
```

Preferred: report both:

```text
full_week_168h including Monday 00-05
forward_162h from Monday 06 onward
```

## Simulation period

Primary simulation period:

```text
2025-06-01 onward through latest complete available year/period
```

If 2026 data is available, also report a separate 2026-to-date or latest rolling period.

Use a minimum training history requirement:

```text
at least 365 days before first forecast_origin
preferred all available data since 2022-06-01
```

## Input data

Use existing prepared inputs:

```text
area_consumption_hourly_v1
area_weather_features_hourly_v1
P0056D weather features for SE1/SE2 if selected
```

If weather_actual_proxy is used, label it clearly as actual-weather proxy / LABB. Do not claim production forecast weather.

No spot price, no flow/exchange, no capacity/A61, no old physical_balance in this package.

## Forecast method variants

At minimum run:

```text
A. current static best model method for each area
B. weekly retrain version of the same method
```

For SE1/SE2 also run if practical:

```text
C. simpler WeightedEnsemble_no_price weekly retrain
D. best compact weather stack from P0056F weekly retrain
```

Keep the first P0056G package focused. Do not combine neural networks, spot price features and production/emulator layers in the same package.

## Training and leakage rules

For each forecast_origin:

```text
train rows must have target_timestamp_utc <= training_cutoff
features must be constructible as of forecast_origin
future actual load is forbidden
future actual weather is allowed only if explicitly labeled actual-weather proxy LABB sensitivity
```

If actual weather is used for future delivery hours, label results:

```text
weather_protocol = actual_weather_proxy
```

Later production-like packages must replace this with weather forecast/noise protocol.

No fitting, weighting, selection or correction may use data after the current weekly training_cutoff.

## Runtime and checkpointing

This package may be expensive because it retrains weekly.

Codex must print and persist progress after every area-week-model job.

Required progress format:

```text
[P0056G progress] area=SE1 week=2025-W23 model=A phase=train status=start timestamp=...
[P0056G progress] area=SE1 week=2025-W23 model=A phase=train status=done elapsed_seconds=...
[P0056G progress] area=SE1 week=2025-W23 model=A phase=test status=done elapsed_seconds=...
```

Create:

```text
requirements/package-runs/P0056G/progress-log.md
requirements/package-runs/P0056G/checkpoint-resume.md
requirements/package-runs/P0056G/job-status.md
```

If interrupted, return WARN with:

```text
completed_jobs
remaining_jobs
last_completed_area
last_completed_week
last_completed_model
resume_command
checkpoint_location
```

Do not discard completed weekly results.

## Metrics

For each area, week and model variant report:

```text
week_start_local
forecast_origin_local
training_cutoff_local
train_rows
forecast_rows_168h
forecast_rows_162h
weekly_MAE_168h
weekly_RMSE_168h
weekly_bias_168h
weekly_MAE_162h
weekly_RMSE_162h
weekly_bias_162h
weekly_energy_abs_error_MWh
weekly_energy_signed_error_MWh
weekly_energy_error_percent
p90_absolute_error
p95_absolute_error
weekday/weekend split if relevant
cold/high-load/ramp regime split if available
```

Aggregate across weeks:

```text
mean_weekly_MAE
median_weekly_MAE
weighted_MAE_percent_of_mean_load
mean_weekly_energy_error_percent
p90_weekly_MAE
worst_week
best_week
bias_over_period
trend_in_error_over_time
```

## Structural-change diagnostics

For SE1/SE2, compute diagnostics that indicate whether yearly structural changes matter:

```text
rolling mean actual load by week
rolling model bias by week
week-over-week load level change
year-over-year same-week load change if available
largest structural break weeks
whether weekly retraining reduces late-period bias
```

These diagnostics do not need to explain the cause, but should show whether static model staleness is a likely problem.

## Required questions to answer

P0056G must answer:

```text
1. Does weekly retraining improve SE1 and SE2 compared with static holdout training?
2. Does weekly retraining reduce bias or only MAE?
3. Is the improvement larger in late-period weeks, suggesting structural drift?
4. Do control areas SE3/FI show the same pattern or is the effect specific to north areas?
5. Is weekly consumption forecasting ready to become the emulator protocol?
```

## Decision rules

Weekly retraining is candidate default for an area if it improves the static baseline by:

```text
mean weekly MAE >= 2 percent relative
or weekly energy error >= 5 percent relative without worsening MAE
or late-period bias improves materially with MAE not worse by more than 1 percent
```

If weekly retraining helps SE1/SE2 but not controls, recommend using weekly retrain for north areas only.

If weekly retraining does not help, keep static/training protocol and focus on structural/exogenous features.

## Required evidence files

Create:

```text
requirements/package-runs/P0056G/CHANGELOG.md
requirements/package-runs/P0056G/review.md
requirements/package-runs/P0056G/design.md
requirements/package-runs/P0056G/functions.md
requirements/package-runs/P0056G/labb-label.md
requirements/package-runs/P0056G/baseline-review.md
requirements/package-runs/P0056G/weekly-emulation-protocol.md
requirements/package-runs/P0056G/input-source-contract.md
requirements/package-runs/P0056G/weather-protocol.md
requirements/package-runs/P0056G/model-variant-contract.md
requirements/package-runs/P0056G/progress-log.md
requirements/package-runs/P0056G/checkpoint-resume.md
requirements/package-runs/P0056G/job-status.md
requirements/package-runs/P0056G/weekly-results.md
requirements/package-runs/P0056G/area-summary-results.md
requirements/package-runs/P0056G/comparison-vs-static-baseline.md
requirements/package-runs/P0056G/structural-change-diagnostics.md
requirements/package-runs/P0056G/leakage-review.md
requirements/package-runs/P0056G/decision.md
requirements/package-runs/P0056G/what-we-learned.md
requirements/package-runs/P0056G/next-package-recommendation.md
```

Optional compact evidence:

```text
weekly-results.csv
area-summary-results.csv
comparison-vs-static-baseline.csv
job-status.csv
metrics-summary.json
```

Do not commit full prediction dumps, model binaries, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056D/area-results.md
requirements/package-runs/P0056E/area-variant-results.md
requirements/package-runs/P0056F/feature-ablation-results.md
requirements/package-runs/P0056F/peak-efficiency-decision.md
src/mac/** forecast/model scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056G-labb-weekly-walk-forward-consumption-emulator.md
requirements/package-runs/P0056G/**
src/mac/** narrowly scoped weekly walk-forward forecast code if needed
tests/mac/** narrowly scoped tests for weekly split, leakage and checkpointing if code is added
local DB forecast/metrics tables if repo owns them and only for P0056G outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No spot price features in this package.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No future actual load leakage.
No fitting beyond each weekly training cutoff.
No large prediction/model artifacts committed.
```

## Verification

Codex must define final commands in design.md and run equivalent checks for:

```text
weekly forecast origins generated correctly
training cutoff before each forecast origin
no future actual load leakage
features available under stated weather protocol
all planned area-week jobs completed or checkpointed
weekly metrics computed
comparison to static baseline computed
structural drift diagnostics computed
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP

PASS requires:

```text
weekly walk-forward protocol is implemented
SE1/SE2 and controls are evaluated
weekly and aggregate metrics are reported
comparison against static baseline is complete
leakage review passes
```

WARN is acceptable if:

```text
some optional controls are skipped
actual-weather proxy is used and clearly labeled LABB
runtime interruption leaves a resumable checkpoint
weekly retrain does not improve results
```

STOP if:

```text
weekly split/leakage safety cannot be verified
inputs are missing
most weekly jobs fail
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
areas and weeks evaluated
model variants evaluated
weather protocol used
weekly retrain delta vs static baseline for SE1/SE2/controls
whether SE1/SE2 improve with weekly retrain
structural drift diagnostics summary
emulator protocol recommendation
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

P0056G completed with `WARN` status on 2026-06-08.

Summary:

```text
areas evaluated: SE1, SE2, SE3, FI
weeks evaluated: 52, 2025-W23..2026-W22
area-week jobs: 208/208 completed, 0 failed
weather protocol: actual_weather_proxy, LABB only
model variant: B_weekly_HGB_no_price
forecast log rows: 34844
metrics rows: 6504
```

Weekly retrain did not beat the selected static baselines:

```text
SE1: +4.819 percent MAE vs P0056E_V2_static
SE2: +0.765 percent MAE vs P0056F_W12_static
SE3: +9.076 percent MAE vs P0056C_static
FI:  +26.932 percent MAE vs P0056C_static
```

Decision:

```text
Do not promote weekly retrain as default from P0056G.
Keep result LABB-only.
Next package should replace actual-weather proxy with production-like weather forecast/noise protocol before any G2-KANDIDAT evaluation.
```
