# Package P0054B: LABB SE3 consumption advanced AI without price

## Status

planned

## Package order

P0054B

## Label

```text
LABB
```

This is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Build the next consumption lab for SE3. Start clean: no price input. The goal is to learn how well SE3 consumption can be forecast from weather, calendar/time and historical load state before adding price, production, flow or export/import.

## Hypothesis

SE3 consumption has stronger and more complex temporal/weather dynamics than SE1. A more advanced AI model may learn dynamics that HGB does not fully capture, especially around:

```text
- cold spells
- rapid weather transitions
- holidays and bridge days
- weekday/weekend differences
- morning ramps
- evening peaks
- seasonal load regimes
```

## Required comparison

P0054B must compare:

```text
HGB benchmark
vs
one more advanced AI model
```

Both must be evaluated on identical rows where compared.

Codex must not rush or silently weaken the advanced model. It must either:

```text
- run a meaningful advanced model to completion, or
- stop/report WARN with exact runtime/dependency/resource blocker.
```

It must not replace the advanced model with a trivial variant and call it advanced.

## Target

Primary target:

```text
consumption_se3_mw
```

Source:

```text
physical_balance_se1_se4_hourly_v1
```

or the canonical physical-balance source used by P0053C.

Unit:

```text
MW hourly mean
```

Required target evidence:

```text
- exact source
- coverage
- missingness
- mean/median/p10/p90 actual MW
- timestamp semantics
```

## Period and split

Use P0053C global policy:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

No target rows before 2022-06-01.

Context-only lag warmup before 2022-06-01 is allowed only if target rows start at or after 2022-06-01 and warmup rows are not scored/trained as targets.

## Inputs

Allowed feature groups:

```text
G0_calendar_only
G1_calendar_plus_load_lags
G2_calendar_plus_load_lags_rollups
G3_calendar_weather_proxy
G4_calendar_load_lags_rollups_weather_proxy
```

Allowed inputs:

```text
- calendar/time known in advance
- SE3 historical consumption lags and rollups before forecast origin
- weather forecast if available
- realized weather as LABB proxy if clearly labeled weather_actual_as_forecast_proxy
```

Forbidden inputs in this package:

```text
- spot price
- M4 anchored price forecast
- actual future spot price
- production
- export/import
- future actual A09/A11 flow/exchange
- A61 capacity/utilization/margin
- continental prices
```

## Feature examples

Calendar:

```text
target_model_cet_hour, weekday, month, day-of-year, weekend, holiday, bridge day, season, sin/cos encodings
```

SE3 load state:

```text
lags: 1h, 2h, 3h, 6h, 12h, 24h, 48h, 72h, 168h
rollups: mean 6h/12h/24h/48h/168h, min/max/std 24h
ramps: 1h, 24h, same-hour-vs-168h
```

Weather:

```text
temperature, wind, solar, temperature delta from normal, heating-degree proxy, rapid temperature change, cold-spell proxy
```

## Baselines

Required baselines:

```text
B0 same-hour previous day
B1 same-hour previous week
B2 calendar hour-weekday profile, train only
B3 seasonal hour-weekday profile, train only
B4 recent 24h mean adjusted by hour profile
```

## Models

Required:

```text
HGB = HistGradientBoostingRegressor benchmark
```

Advanced AI candidate priority:

```text
1. sequence-aware model such as GRU/LSTM/TCN if feasible
2. small MLP if sequence model is blocked
3. ExtraTrees/RandomForest fallback only if neural path is blocked and documented
```

Advanced model evidence must include:

```text
advanced_model_type
architecture_summary
training_rows
validation_rows
holdout_rows
training_duration_seconds
epochs_or_iterations_completed
early_stopping_reason
resource_limits_if_any
```

Codex should use a sufficiently large runtime budget for this package. If the advanced model needs longer than normal, it should continue rather than prematurely simplifying, within local practical limits. If it cannot complete, document the blocker honestly.

## Evaluation

Direct horizons:

```text
1h, 3h, 6h, 12h, 24h, 48h, 72h, 96h, 120h, 144h, 168h
```

Weekly 168h path evaluation on holdout:

```text
weekly origins from 2025-06-01 onward where complete 168h paths exist
```

Required weekly evidence:

```text
weekly_origin_count
first_weekly_origin
last_weekly_origin
complete_168h_path_count
skipped_origins_with_reason
```

## Metrics

Direct metrics:

```text
MAE, RMSE, bias, median absolute error, p90, p95, sMAPE, MAE percent of mean/median actual
```

Path metrics:

```text
MAE_0_24h, MAE_24_48h, MAE_48_72h, MAE_72_168h, MAE_full_168h, bias_full_168h, p90/p95 full path, daily energy error proxy, peak load hour error
```

Conditional metrics:

```text
cold hours, very cold hours, rapid temperature drop, weekday, weekend, holiday, morning ramp, evening peak, summer low load, winter high load
```

## Interpretation

Use P0054A interpretation categories.

Required question:

```text
Did advanced AI beat HGB enough to change our modeling direction?
```

Learning threshold:

```text
>= 2% improvement in holdout weekly MAE_full_168h
or >= 3% improvement in at least two important conditional regimes
```

This is a LABB learning threshold, not a production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054B/CHANGELOG.md
requirements/package-runs/P0054B/review.md
requirements/package-runs/P0054B/design.md
requirements/package-runs/P0054B/functions.md
requirements/package-runs/P0054B/labb-label.md
requirements/package-runs/P0054B/dataset-contract.md
requirements/package-runs/P0054B/input-classification.md
requirements/package-runs/P0054B/weather-proxy-policy.md
requirements/package-runs/P0054B/feature-groups.md
requirements/package-runs/P0054B/baseline-results.md
requirements/package-runs/P0054B/hgb-results.md
requirements/package-runs/P0054B/advanced-ai-design.md
requirements/package-runs/P0054B/advanced-ai-training-evidence.md
requirements/package-runs/P0054B/advanced-ai-results.md
requirements/package-runs/P0054B/hgb-vs-advanced-ai-comparison.md
requirements/package-runs/P0054B/direct-horizon-results.md
requirements/package-runs/P0054B/weekly-168h-path-results.md
requirements/package-runs/P0054B/conditional-regime-results.md
requirements/package-runs/P0054B/feature-importance-or-attribution.md
requirements/package-runs/P0054B/interpretation.md
requirements/package-runs/P0054B/what-we-learned.md
requirements/package-runs/P0054B/next-package-recommendation.md
requirements/package-runs/P0054B/component-attribution-summary.md
```

Optional compact machine-readable evidence:

```text
metrics-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
advanced-training-history.csv
modeling-dataset-sample.csv
```

Do not commit large raw datasets or large model binaries.

## Required answers

P0054B must answer:

```text
1. What is the exact SE3 consumption target source and coverage?
2. Which inputs were used and how were they classified?
3. Was realized weather used as forecast proxy?
4. Confirm no spot-price input was used.
5. Which baseline was strongest?
6. What is HGB performance by horizon and weekly 168h path?
7. What advanced AI model was trained?
8. Did the advanced AI model run to completion?
9. What runtime/epochs/early-stopping evidence exists?
10. Did advanced AI beat HGB on identical rows?
11. Where did advanced AI improve or fail by condition/regime?
12. What did we learn about SE3 consumption?
13. What is the recommended next package?
14. Confirm no price input, no future A09/A11, no production/export/import model, no A61 utilization, no API and no device actions.
```

## Verification checks

Required checks:

```text
- target consumption_se3_mw exists and is numeric/finite
- timestamp_utc unique and normalized
- split policy follows P0053C
- no target rows before 2022-06-01
- holdout starts at 2025-06-01
- lag/rollup features do not peek beyond forecast origin
- realized weather proxy is labeled if used
- no price columns/features are present in model feature matrix
- no future actual A09/A11 flow/exchange is used
- no future production is used
- HGB and advanced model comparisons use identical rows
- weekly 168h paths are complete or skipped with reason
- advanced model training evidence exists
- no API/device/runtime path touched
```

## Pass/fail interpretation

PASS requires:

```text
- SE3 consumption dataset built
- no price features used
- baselines and HGB evaluated
- advanced AI meaningfully trained or honest WARN/STOP blocker documented
- direct horizon and weekly 168h metrics reported
- fair HGB vs advanced comparison
- what-we-learned evidence explicit
```

WARN is acceptable if:

```text
- sequence model is blocked but fallback advanced model is trained with evidence
- weather is proxy-only
- advanced AI fails to beat HGB but teaches useful constraints
- runtime is long but completed or stopped honestly
```

STOP if:

```text
- price input leaks into features
- future actual target/flow/production leaks into features
- advanced AI is silently skipped or replaced by trivial model
- holdout is used for model selection
- API/device/runtime work is created
```

## Expected Codex output

- PASS/WARN/STOP status
- target/data coverage
- input classification summary
- strongest baseline
- HGB metrics
- advanced AI architecture/training evidence
- HGB vs advanced AI comparison
- weekly holdout results
- conditional/regime findings
- what we learned
- next-package recommendation
- tests run
- files changed
- confirmation of no price/API/device/A61/leakage work
- commit SHA after push

## Completion notes

To be filled after implementation.
