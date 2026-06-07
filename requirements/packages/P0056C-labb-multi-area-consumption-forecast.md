# Package P0056C: LABB multi-area consumption forecast

## Status

planned

## Package order

P0056C

## Label

```text
LABB
```

## Purpose

Copy the best SE3 consumption-forecast method to all P0056A northern Europe price areas and evaluate each area on the final holdout year.

This package creates the multi-area consumption forecast layer for the market emulator.

## Area scope

Run all 18 P0056A primary areas:

```text
SE1
SE2
SE3
SE4
NO1
NO2
NO3
NO4
NO5
DK1
DK2
FI
EE
LV
LT
DE_LU
PL
NL
```

Do not silently skip an area. If an area fails, keep all completed results and document the failed area with reason and retry command.

## Required input tables

Use P0056A consumption targets:

```text
area_consumption_hourly_v1
```

Use P0056B area weather proxies:

```text
area_weather_features_hourly_v1
```

Use only corrected actual load/consumption targets. Do not use flow, exchange, capacity, net position, spot price or old physical_balance data as target or consumption feature.

## Forecast method

Use the latest best SE3 method as the default for every area:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

Feature families:

```text
calendar/time
holiday/weekend
historical area load lags
rolling area load statistics
area weather proxy features
```

Forbidden features:

```text
spot price
future actual area load
flows/exchanges/net positions
A61/capacity
old physical_balance target
holdout-derived weights or corrections
```

If a specific area cannot train the full model safely, use this fallback order and document it:

```text
F1: same method with reduced feature set
F2: WeightedEnsemble_no_price
F3: seasonal/same-hour same-week fallback
STOP only if target or feature construction is invalid
```

## Split policy

Use the same split as SE3 work:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation for model selection, ensemble weights and horizon-bias correction must be strictly inside train_fit.

Preferred internal validation start:

```text
2025-03-01T00:00:00Z
```

No holdout rows may be used for fitting, tuning, selection, correction or weighting.

## Job count and runtime policy

Run 18 areas with two visible job phases per area:

```text
18 * 2 = 36 jobs

for each area:
  1. learn/train job
  2. test/evaluate job
```

This package may take time. Runtime alone is not a reason to stop.

Codex must print and persist progress between every job so the run is visibly alive.

Required progress format:

```text
[P0056C progress] area=SE1 phase=learn job=1/36 status=start timestamp=...
[P0056C progress] area=SE1 phase=learn job=1/36 status=done elapsed_seconds=...
[P0056C progress] area=SE1 phase=test job=2/36 status=start timestamp=...
[P0056C progress] area=SE1 phase=test job=2/36 status=done elapsed_seconds=...
```

Also write a progress/checkpoint file or table after every phase:

```text
requirements/package-runs/P0056C/progress-log.md
```

or a compact local checkpoint table if DB support is preferred.

If the process is interrupted, return WARN with:

```text
completed_jobs
remaining_jobs
last_completed_area
last_completed_phase
resume_command
checkpoint_location
```

Do not discard completed area models/results if a later area fails.

## Forecast use cases

Evaluate both:

```text
DayAhead:
  forecast_origin = 12:00 Europe/Stockholm on D-1
  delivery_day = D 00:00..23:00 Europe/Stockholm

full_36h:
  complete 36-hour path from origin
```

Use the same horizon convention as P0054R/P0054T4/P0055A.

## Required outputs

Create forecast/evaluation outputs per area:

```text
area_code
model_name
train_fit_rows
holdout_rows
forecast_origins
dayahead_rows
full36_rows
status
fallback_used nullable
```

If repo database ownership allows, create or populate:

```text
area_consumption_forecast_log_p0056c_v1
area_consumption_forecast_metrics_p0056c_v1
```

Do not commit full prediction dumps or model binaries.

## Metrics per area

For each area compute:

```text
DayAhead hourly MAE
DayAhead RMSE
DayAhead bias
MAE percent of mean actual
MAE percent of median actual
absolute daily energy error MWh
signed daily energy error MWh
daily energy error percent of actual
full_36h MAE
full_36h RMSE
full_36h bias
p90 absolute error
p95 absolute error
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
weekday/weekend split
cold/high-load/ramp regimes where available
```

Also compute a cross-area summary:

```text
best_area_by_percent_MAE
worst_area_by_percent_MAE
weighted_mean_MAE_percent_by_mean_load
total_northern_europe_actual_load
sum_of_area_forecasts
aggregate_forecast_error
```

## Required questions to answer

P0056C must answer:

```text
1. Does the SE3 method train and evaluate successfully for all 18 areas?
2. Which areas forecast best and worst?
3. Are any areas unsuitable for this method without special handling?
4. Does the summed multi-area consumption forecast look sane?
5. Is the output ready for production forecast and flow/price emulator layers?
```

## Required evidence files

Create:

```text
requirements/package-runs/P0056C/CHANGELOG.md
requirements/package-runs/P0056C/review.md
requirements/package-runs/P0056C/design.md
requirements/package-runs/P0056C/functions.md
requirements/package-runs/P0056C/labb-label.md
requirements/package-runs/P0056C/input-source-contract.md
requirements/package-runs/P0056C/split-policy-applied.md
requirements/package-runs/P0056C/model-method-contract.md
requirements/package-runs/P0056C/progress-log.md
requirements/package-runs/P0056C/checkpoint-resume.md
requirements/package-runs/P0056C/component-job-status.md
requirements/package-runs/P0056C/area-training-evidence.md
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056C/dayahead-results.md
requirements/package-runs/P0056C/full-36h-results.md
requirements/package-runs/P0056C/daily-energy-error-results.md
requirements/package-runs/P0056C/cross-area-summary.md
requirements/package-runs/P0056C/aggregate-load-forecast-results.md
requirements/package-runs/P0056C/leakage-review.md
requirements/package-runs/P0056C/data-quality-limitations.md
requirements/package-runs/P0056C/what-we-learned.md
requirements/package-runs/P0056C/next-package-recommendation.md
```

Optional compact evidence:

```text
area-results.csv
job-status.csv
metrics-summary.json
cross-area-summary.csv
```

Do not commit model binaries, full prediction dumps, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0054V2/decision.md
requirements/package-runs/P0056A/CHANGELOG.md
requirements/package-runs/P0056A/coverage-and-missingness.md
requirements/package-runs/P0056A/se3-target-consistency-check.md
requirements/package-runs/P0056B/CHANGELOG.md
requirements/package-runs/P0056B/weather-proxy-validation.md
requirements/package-runs/P0056B/se3-proxy-consistency-check.md
src/mac/** relevant forecast/model scripts
tests/mac/** relevant tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056C-labb-multi-area-consumption-forecast.md
requirements/package-runs/P0056C/**
src/mac/** narrowly scoped multi-area forecast/evaluation code if needed
tests/mac/** narrowly scoped tests for split, leakage, aggregation, progress/checkpointing if code is added
docs/functions/mac/** if durable docs need updating
local database forecast-log/metrics tables if repo owns them and only for P0056C outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No external live data integration.
No forecast use of spot price.
No old physical_balance target.
No flow/exchange/A61/capacity features.
No future actual load leakage.
No holdout fitting or selection.
No large prediction/model artifacts committed.
```

## Verification

Codex must define final commands in design.md and run equivalent checks for:

```text
P0056A consumption input available for all 18 areas
P0056B weather input available for all 18 areas
split policy applied
36 jobs completed or checkpointed
all completed area results persisted
no holdout fitting/selection
no forbidden features
aggregate forecast equals sum of area forecasts
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP

PASS requires:

```text
all 18 areas trained/tested or safe fallback documented
DayAhead and full_36h metrics reported for all areas
cross-area and aggregate summaries reported
progress/checkpoint evidence present
leakage review passes
```

WARN is acceptable if:

```text
one or more areas require fallback
one or more areas have partial input coverage but results are still usable
optional aggregate forecast detail is limited but per-area metrics are complete
```

STOP if:

```text
P0056A or P0056B inputs are missing for many areas
split/leakage safety cannot be verified
forecast aggregation cannot be computed
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
completed job count out of 36
areas trained/tested/fallbacked/failed
direct method used per area
best/worst areas by MAE percent
area results summary
aggregate forecast summary
whether output is ready for emulator layers
tests/commands run
files changed
confirmation no spot price/no old target/no flow/A61/no external integration/no large artifacts
```

## Completion notes

To be filled after implementation.
