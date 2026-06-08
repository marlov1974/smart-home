# Package P0056H: LABB 36h walk-forward lag protocol

## Status

completed_warn

## Package order

P0056H

## Label

```text
LABB
```

## Purpose

Rerun the consumption forecast test in a way that compares apples to apples with the earlier DayAhead/full36 tests, while still using an emulator-style rolling protocol.

P0056G tested a 7-day weekly forecast. That is harder than the original P0056C/P0054 protocol because many short load-lag features become unavailable or recursive far into the week.

P0056H must instead test 36-hour forecasts with explicit, horizon-safe lag features. Forecast origins must occur every 5th day so the test covers all weekdays and all months over the holdout period without becoming a 7-day path forecast.

## Core hypothesis

The older static test may have performed better because it used explicit actual-load lag features for each DayAhead/full36 forecast origin.

The weekly emulator test may have degraded because lags became vague, unavailable or recursive over a 168-hour horizon.

P0056H tests whether 36h walk-forward forecasts with proper explicit lags recover the older performance while preserving rolling-origin realism.

## Areas in scope

Primary:

```text
SE1
SE2
SE3
FI
```

Optional if runtime allows:

```text
NO3
NO4
```

SE1/SE2 are primary because of weak northern performance. SE3/FI are controls.

## Baselines

Compare against:

```text
P0056C static holdout full36 and DayAhead
P0056D SE1/SE2/FI weather retune
P0056E north model variants
P0056F weather feature ablation
P0056G weekly 162h/168h walk-forward
```

Use the best current known baseline per area, and also report P0056C baseline separately.

Known reference values:

```text
SE1 P0056E V2: DayAhead MAE 125.220 MW, full36 MAE 123.509 MW
SE2 P0056F W12: DayAhead MAE 206.179 MW, full36 MAE 197.547 MW
SE3 P0056C: DayAhead MAE 258.869 MW, full36 MAE 250.928 MW
FI  P0056C: DayAhead MAE 332.717 MW, full36 MAE 311.189 MW
```

If local evidence differs, use latest committed evidence and document the exact source.

## Forecast-origin protocol

Generate forecast origins every 5th day over the holdout period.

Recommended:

```text
first_origin_local >= 2025-06-01 06:00 Europe/Stockholm
origin_time_local = 06:00 Europe/Stockholm
origin_step_days = 5
horizon = 36 hours
```

This makes origins rotate through weekdays:

```text
Monday -> Saturday -> Thursday -> Tuesday -> Sunday -> Friday -> Wednesday -> Monday ...
```

so all weekdays are covered, and over the year all months are sampled.

For each origin:

```text
training_cutoff = forecast_origin
forecast_window = origin through origin + 35 hours
```

No training row may have target timestamp at or after forecast_origin.

## Lag protocol

P0056H must include explicit load-lag features as real features, not only as historical training context.

Required base lags:

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
```

Required rolling/ramp features:

```text
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

## Horizon-safe lag handling

For each forecast target hour, classify every lag feature as one of:

```text
known_actual_at_origin
known_actual_before_origin
requires_recursive_forecast
forbidden_future_actual
```

Primary P0056H result must avoid future actual load leakage.

Allowed modes:

### L1 origin-known / horizon-safe lags

Use only lag values that are known at forecast_origin. For target hours where a short lag would point into the forecast window, do not use future actuals.

Allowed replacements:

```text
use recursive predicted lag
or use seasonal fallback lag such as lag_168h
or set explicit unavailable flag
```

Document exact approach.

### L2 recursive lags

For target hours whose lag references an earlier predicted hour in the same 36h forecast window, feed the model's own previous forecast back as lag.

This is forecast-safe and should be primary if implemented correctly.

### L3 oracle actual-lag sensitivity

Optional only. Use actual future lags to estimate upper bound. Must be labeled oracle/future-leaking sensitivity and cannot be used for default decisions.

## Required comparison modes

At minimum compare:

```text
A. Static baseline from P0056C/E/F
B. 36h rolling origin every 5th day with horizon-safe explicit lags
C. P0056G weekly 162h/168h result as a harder 7-day comparison
```

If runtime allows, also compare:

```text
D. 36h recursive lags
E. 36h oracle actual-lag sensitivity
```

## Model methods

Use the best current method per area or current best general method:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

For SE1 also include if practical:

```text
WeightedEnsemble_no_price from P0056E V2
```

For SE2 include current best:

```text
P0056F W12 weather stack or P0056D/P0056E near-best equivalent
```

Keep this package focused on lag protocol and 36h horizon, not broad model search.

## Weather protocol

Use the best current weather proxy/feature stack per area.

Allowed:

```text
P0056B area weather features
P0056D revised weather for SE1/SE2/FI where selected
P0056F selected weather stacks if implemented
```

If future weather actual proxy is used for forecast hours, label:

```text
weather_protocol = actual_weather_proxy_LABB
```

Do not claim production forecast weather.

## Metrics

For each area, origin and mode report:

```text
forecast_origin_local
forecast_origin_utc
forecast_rows
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
weekday/month of origin
```

Aggregate by area/mode:

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

P0056H must answer:

```text
1. Does 36h rolling-origin testing with explicit lags match or beat the old static P0056C/E/F results?
2. Was P0056G worse mainly because 168h forecasts degrade lag features?
3. Do SE1/SE2 improve more than controls under proper 36h lag protocol?
4. Which lag protocol is best: origin-known, recursive, or oracle sensitivity?
5. Should emulator consumption forecasts use 36h rolling forecasts rather than weekly 168h forecasts?
```

## Decision rules

36h lag-aware protocol is candidate emulator default if:

```text
mean_MAE_0_36h is within 1 percent of static full36 baseline
or improves static full36 by >= 1 percent
and is materially better than P0056G weekly 162h/168h for the same areas
```

If recursive lags are worse but oracle lags are much better, recommend a dedicated multi-step lag strategy package.

If 36h lag-aware still underperforms static, investigate feature construction/leakage/test-definition mismatch.

## Runtime and checkpointing

Codex must print and persist progress per area, mode and origin.

Create:

```text
requirements/package-runs/P0056H/progress-log.md
requirements/package-runs/P0056H/checkpoint-resume.md
requirements/package-runs/P0056H/job-status.md
```

Progress format:

```text
[P0056H progress] area=SE1 mode=L2 origin=2025-06-06T06:00+02:00 phase=train status=start
[P0056H progress] area=SE1 mode=L2 origin=2025-06-06T06:00+02:00 phase=test status=done elapsed_seconds=...
```

If interrupted, return WARN with completed/remaining origins and resume command.

## Required evidence files

Create:

```text
requirements/package-runs/P0056H/CHANGELOG.md
requirements/package-runs/P0056H/review.md
requirements/package-runs/P0056H/design.md
requirements/package-runs/P0056H/functions.md
requirements/package-runs/P0056H/labb-label.md
requirements/package-runs/P0056H/baseline-review.md
requirements/package-runs/P0056H/origin-schedule.md
requirements/package-runs/P0056H/lag-protocol-contract.md
requirements/package-runs/P0056H/lag-availability-review.md
requirements/package-runs/P0056H/input-source-contract.md
requirements/package-runs/P0056H/weather-protocol.md
requirements/package-runs/P0056H/model-method-contract.md
requirements/package-runs/P0056H/progress-log.md
requirements/package-runs/P0056H/checkpoint-resume.md
requirements/package-runs/P0056H/job-status.md
requirements/package-runs/P0056H/origin-results.md
requirements/package-runs/P0056H/area-summary-results.md
requirements/package-runs/P0056H/comparison-vs-static-baseline.md
requirements/package-runs/P0056H/comparison-vs-p0056g-weekly.md
requirements/package-runs/P0056H/oracle-lag-sensitivity.md if run
requirements/package-runs/P0056H/leakage-review.md
requirements/package-runs/P0056H/decision.md
requirements/package-runs/P0056H/what-we-learned.md
requirements/package-runs/P0056H/next-package-recommendation.md
```

Optional compact evidence:

```text
origin-results.csv
area-summary-results.csv
lag-availability-summary.csv
metrics-summary.json
```

Do not commit full prediction dumps, model binaries, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056E/area-variant-results.md
requirements/package-runs/P0056F/feature-ablation-results.md
requirements/package-runs/P0056G/area-summary-results.md
requirements/package-runs/P0056G/comparison-vs-static-baseline.md
requirements/package-runs/P0056G/weekly-emulation-protocol.md
src/mac/** forecast/model/feature scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056H-labb-36h-walk-forward-lag-protocol.md
requirements/package-runs/P0056H/**
src/mac/** narrowly scoped 36h walk-forward/lag protocol code if needed
tests/mac/** narrowly scoped tests for lag availability, recursive lags, split/leakage if code is added
local DB metrics tables if repo owns them and only for P0056H outputs
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
No future actual load leakage in primary result.
No fitting beyond each forecast origin.
No large prediction/model artifacts committed.
```

## Verification

Codex must define final commands in design.md and run equivalent checks for:

```text
origin schedule every 5th day covers weekdays/months
training cutoff before each origin
lag availability classified per horizon
no future actual load leakage in primary mode
recursive/oracle modes labeled correctly
metrics computed per origin and area
comparison vs static baseline computed
comparison vs P0056G weekly computed
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP

PASS requires:

```text
36h rolling-origin lag-aware protocol implemented
SE1/SE2/SE3/FI evaluated
lag availability and leakage review pass
comparisons against static and P0056G are reported
clear emulator recommendation is produced
```

WARN is acceptable if:

```text
optional oracle mode is skipped
some optional controls are skipped
actual-weather proxy is used and labeled LABB
one lag mode is implemented but another remains future work
```

STOP if:

```text
lag safety cannot be verified
inputs are missing
most origins fail
future actual load leakage is found in primary result
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
areas evaluated
origin count per area
lag protocol modes evaluated
36h MAE vs static baseline
36h MAE vs P0056G weekly
whether explicit lag protocol recovers old performance
recommended emulator consumption horizon/protocol
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

P0056H completed as `WARN` on 2026-06-08.

Implemented deterministic LABB-only 36h rolling-origin walk-forward evidence for SE1, SE2, SE3 and FI using strict forecast origins every fifth day at 06:00 Europe/Stockholm from 2025-06-01 through 2026-05-27.

Evaluated modes:

```text
L1_origin_known_fallback
L2_recursive_lags
```

Skipped:

```text
L3 oracle actual-lag sensitivity
NO3/NO4 optional controls
```

Row counts:

```text
scheduled_origin_mode_jobs = 584
expected_origin_results = 564
origin_results = 564
skipped_incomplete_origin_windows = 10
skipped_incomplete_origin_mode_jobs = 20
forecast_log_rows = 20304
metrics_rows = 12488
failed_jobs = 0
```

Ten strict 36h area-origin windows were skipped because existing local target/weather coverage had only 35 of 36 required rows. This is documented in `requirements/package-runs/P0056H/coverage-gaps.md`.

Aggregate mean MAE 0-36h:

```text
SE1 L1 = 172.754 MW, L2 = 138.317 MW
SE2 L1 = 307.044 MW, L2 = 242.579 MW
SE3 L1 = 638.040 MW, L2 = 361.881 MW
FI  L1 = 612.830 MW, L2 = 367.057 MW
```

Conclusion:

```text
L2 recursive lags materially improve over L1 fallback for every scoped area.
L2 does not recover old static full36 performance for SE1/SE2/SE3/FI.
FI L2 improves over P0056G weekly, but SE1/SE2/SE3 remain worse than P0056G.
```

Leakage and scope:

```text
No future actual load lag leakage found in primary modes.
No spot price, flow/exchange/A61/capacity, old physical_balance, API, device, runtime or production activation changes.
Weather protocol is actual_weather_proxy_LABB and not production forecast weather.
```
