# Package P0056K: LABB realistic DayAhead AI model restart

## Status

completed_WARN

## Package order

P0056K

## Label

```text
LABB
```

## Purpose

Restart the consumption-model comparison using a realistic DayAhead forecast protocol.

Earlier static results are no longer valid as DayAhead performance because P0056J showed that the static evaluation behaved more like row-wise/nowcast-style evaluation with fresh lag information per target row. Those results may still be useful for model ranking or upper-bound diagnostics, but they must not be used as realistic DayAhead/emulator performance.

P0056K must define a realistic DayAhead consumption forecast test and compare multiple AI/model families under that protocol.

## Core principle

At forecast origin, the model may only use information available at that forecast origin.

For DayAhead delivery, do not use future actual consumption inside lag, rolling or ramp features.

## Forecast scenario

Use a DayAhead scenario suitable for market-emulator consumption input.

Recommended primary protocol:

```text
forecast_origin = D-1 12:00 Europe/Stockholm
delivery_day = D 00:00 through D 23:00 Europe/Stockholm
horizon = target hour - forecast_origin
```

Also report if a 36h path is generated internally, but primary DayAhead metrics must be the delivery-day 24h block.

## Areas in scope

Primary restart scope:

```text
SE1
SE2
SE3
FI
```

Rationale:

```text
SE1/SE2 = difficult northern areas
SE3 = existing best-known reference area
FI = large control area with recent rolling weaknesses
```

Optional later expansion:

```text
all 18 P0056C areas
```

Do not run all 18 in this package unless runtime is clearly acceptable and progress/checkpointing is robust.

## Input data

Use existing prepared inputs:

```text
area_consumption_hourly_v1
area_weather_features_hourly_v1
P0056D/P0056F weather variants where selected
```

Weather protocol must be explicitly labeled:

```text
actual_weather_proxy_LABB
```

if future actual weather is used. Do not claim this is production weather forecast.

No spot price, flow, exchange, capacity/A61, or old physical_balance in this package.

Spot price and structural/exogenous features can be tested later after the DayAhead baseline is correctly rebuilt.

## Train/test period

Use holdout/emulation period:

```text
2025-06-01 onward through latest complete available period
```

For every forecast origin, train only on rows before the forecast origin.

Training-window variants should be minimal in this package. Prefer:

```text
TWX expanding from 2022-06-01
```

because P0056I found it slightly best and operationally simple for SE2.

Optionally include rolling 3.0 years as sensitivity if runtime allows.

## Feature protocol

Use feature families:

```text
calendar/time
holiday/weekend
known load history at forecast origin
horizon-safe lag proxies
weather proxy features
```

Forbidden in primary result:

```text
future actual load
lag features that require future actual load
rolling/ramp features that require future actual load
row-wise target features unavailable at forecast origin
```

Allowed lag strategies:

### DA-L1: known-at-origin lags only

Use only lag/rolling values that are fully known at forecast origin. If a feature is not known for a target hour, do not compute it from future target-period actuals.

### DA-L2: recursive lag path

For target hours where short lags refer to earlier forecasted delivery hours, use previous model predictions as inputs. This must be clearly labeled recursive and forecast-safe.

### DA-L3: seasonal lag fallback

Use safe seasonal lags such as previous week same hour when short lags are unavailable.

Primary model comparison should use one clearly selected forecast-safe lag protocol, preferably DA-L2 if implemented robustly; otherwise DA-L1/DA-L3 with explicit unavailable flags.

## Model families to test

Test at minimum:

```text
M0 seasonal naive / same-hour previous week baseline
M1 Linear/Ridge or ElasticNet baseline
M2 HistGradientBoosting / HGB
M3 ExtraTrees or RandomForest-style tree ensemble
M4 LightGBM
M5 XGBoost
M6 WeightedEnsemble_no_price
M7 HorizonBiasCorrected_WeightedEnsemble_no_price, if correction can be trained forecast-safely
```

Optional neural smoke tests if dependencies/runtime allow:

```text
M8 tabular MLP
M9 simple sequence model / TCN/N-HiTS style
```

Do not block the package on neural dependencies. If neural models are unavailable, document and proceed with tree/ensemble models.

## Bias correction rules

Horizon-bias correction is allowed only if trained without future data relative to the forecast origin.

For every forecast origin:

```text
bias correction fit window must end before forecast_origin
model selection and ensemble weights must be determined before forecast_origin
```

Do not reuse holdout-wide hindsight correction.

## Metrics

For each area, model and lag protocol report:

```text
origin_count
delivery_day_count
DayAhead hourly MAE
DayAhead RMSE
DayAhead bias
MAE percent of mean actual
MAE percent of median actual
absolute daily energy error MWh
signed daily energy error MWh
daily energy error percent of actual
p90 absolute error
p95 absolute error
weekday/weekend split
monthly split
cold/high-load/ramp regimes if available
```

Also report runtime:

```text
train seconds per origin/model
predict seconds
total runtime
```

## Required comparisons

Compare new realistic DayAhead results against:

```text
P0056C/P0056F static results, labeled old_static_not_representative_DA
P0056G weekly walk-forward
P0056H/P0056H2 36h rolling tests
P0056I SE2 train-window sensitivity
```

Do not use old static results as pass/fail targets. Treat them as upper-bound or model-ranking context.

## Required questions to answer

P0056K must answer:

```text
1. Which model family is best under realistic DayAhead constraints?
2. Do SE1/SE2 still underperform when tested with the correct DayAhead protocol?
3. Does horizon-bias correction still help when trained forecast-safely?
4. Does recursive lagging help or hurt in DayAhead delivery-day forecasts?
5. Which model should become the new baseline for market-emulator consumption input?
```

## Runtime and checkpointing

Codex must print and persist progress by area, model and origin batch.

Create:

```text
requirements/package-runs/P0056K/progress-log.md
requirements/package-runs/P0056K/job-status.md
requirements/package-runs/P0056K/checkpoint-resume.md
```

If interrupted, return WARN with completed models/areas and resume instructions.

## Required evidence files

Create:

```text
requirements/package-runs/P0056K/CHANGELOG.md
requirements/package-runs/P0056K/review.md
requirements/package-runs/P0056K/design.md
requirements/package-runs/P0056K/functions.md
requirements/package-runs/P0056K/labb-label.md
requirements/package-runs/P0056K/forecast-taxonomy.md
requirements/package-runs/P0056K/dayahead-protocol.md
requirements/package-runs/P0056K/input-source-contract.md
requirements/package-runs/P0056K/weather-protocol.md
requirements/package-runs/P0056K/lag-protocol.md
requirements/package-runs/P0056K/model-family-contract.md
requirements/package-runs/P0056K/bias-correction-contract.md
requirements/package-runs/P0056K/progress-log.md
requirements/package-runs/P0056K/job-status.md
requirements/package-runs/P0056K/area-model-results.md
requirements/package-runs/P0056K/model-ranking.md
requirements/package-runs/P0056K/comparison-vs-old-static.md
requirements/package-runs/P0056K/comparison-vs-rolling-tests.md
requirements/package-runs/P0056K/leakage-review.md
requirements/package-runs/P0056K/decision.md
requirements/package-runs/P0056K/what-we-learned.md
requirements/package-runs/P0056K/next-package-recommendation.md
```

Optional compact evidence:

```text
area-model-results.csv
model-ranking.csv
metrics-summary.json
job-status.csv
```

Do not commit model binaries, full prediction dumps, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056J/interpretation.md
requirements/package-runs/P0056J/hypothesis-review.md
requirements/package-runs/P0056J/feature-diff-summary.md
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056F/feature-ablation-results.md
requirements/package-runs/P0056G/area-summary-results.md
requirements/package-runs/P0056H/area-summary-results.md
requirements/package-runs/P0056H2/area-summary-results.md
requirements/package-runs/P0056I/window-summary-results.md
src/mac/** forecast/model/feature/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056K-labb-dayahead-realistic-ai-model-restart.md
requirements/package-runs/P0056K/**
src/mac/** narrowly scoped realistic DayAhead model comparison code if needed
tests/mac/** narrowly scoped tests for DayAhead origin safety, lag safety and leakage if code is added
local DB metrics tables if repo owns them and only for P0056K outputs
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
No future actual load in primary features.
No holdout-wide hindsight bias correction.
No large model/prediction artifacts committed.
No treating old static results as realistic DayAhead performance.
```

## Pass / WARN / STOP

PASS requires:

```text
realistic DayAhead protocol is implemented
SE1/SE2/SE3/FI evaluated
multiple model families are compared
feature/lag leakage review passes
new DayAhead model ranking is produced
old static results are relabeled correctly in evidence
```

WARN is acceptable if:

```text
neural models are skipped due to dependencies
one optional model fails but enough models complete
actual-weather proxy is used and clearly labeled LABB
one lag protocol is used and others deferred
```

STOP if:

```text
DayAhead origin safety cannot be verified
future actual load leakage is found in primary result
input data is missing for primary areas
most model families fail
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
areas evaluated
models evaluated
lag protocol used
weather protocol used
best model per area
overall best model
SE1/SE2 realistic DayAhead performance
comparison to old static, labeled not representative DayAhead
leakage review result
recommended new baseline for emulator consumption input
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

Completed in `requirements/package-runs/P0056K/` with status `WARN`.

WARN reasons:

```text
actual_weather_proxy_LABB is used and clearly labeled
DA-L3 seasonal_safe is the only lag protocol evaluated
optional neural models M8/M9 were skipped
no production weather forecast model is included
```

Runtime summary:

```text
areas evaluated: SE1, SE2, SE3, FI
models evaluated: M0, M1, M2, M3, M4, M5, M6, M7
origin counts: SE1=243, SE2=240, SE3=310, FI=365
origin/model rows: 9264
failures: 0
lag protocol: DA-L3 seasonal_safe
weather protocol: actual_weather_proxy_LABB
```

Best model per area by DayAhead hourly MAE:

```text
SE1: M6, 133.471 MW
SE2: M6, 232.693 MW
SE3: M7, 262.426 MW
FI: M7, 301.566 MW
overall: M7, 233.241 MW mean across scoped areas
```

SE1/SE2 realistic DayAhead performance:

```text
SE1 best: 133.471 MW MAE (M6)
SE2 best: 232.693 MW MAE (M6)
```

Decision:

```text
recommended_new_baseline_for_emulator_consumption_input: M7
production_ready: false
```

Leakage review passed for the implemented feature list:

```text
no spot price features
no flow/exchange/A61/capacity features
no old physical_balance target
no future actual load features
no holdout-wide hindsight bias correction
no API, devices, runtime changes or production activation
```

Primary evidence:

```text
requirements/package-runs/P0056K/area-model-results.md
requirements/package-runs/P0056K/model-ranking.md
requirements/package-runs/P0056K/leakage-review.md
requirements/package-runs/P0056K/decision.md
requirements/package-runs/P0056K/metrics-summary.json
```
