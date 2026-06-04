# Package P0054C: LABB SE4 consumption advanced AI without price

## Status

planned

## Package order

P0054C

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Repeat the P0054B SE3 consumption experiment for SE4, using the same clean setup:

```text
calendar/time + weather/weather proxy + historical load state
```

No price input.

The aim is to see whether the P0054B finding generalizes: in SE3, a small MLP beat HGB by about 2.34% on holdout MAE and about 1.6% on weekly 168h paths. P0054C checks whether SE4 shows the same pattern.

## Hypothesis

SE4 consumption may have even stronger nonlinear consumption dynamics than SE3 due to:

```text
- larger weather-sensitive household/commercial load share
- stronger heating/cooling seasonality
- different weekday/weekend behavior
- more pronounced morning/evening ramps
- potentially larger smart-home/price-optimization population later, though price is excluded in this package
```

Without price input, a more advanced AI model may beat HGB if SE4 load dynamics contain smooth nonlinear interactions that HGB does not capture optimally.

## Required comparison

Compare:

```text
HGB benchmark
vs
one more advanced AI model
```

Use the P0054B model family where practical:

```text
HGB_G4_calendar_load_lags_rollups_weather_proxy
MLP_G4_calendar_load_lags_rollups_weather_proxy
```

Both models must be evaluated on identical rows.

Codex must not rush or silently weaken the advanced model. It must either run a meaningful advanced model to completion or report WARN/STOP with exact blocker.

## Target

Primary target:

```text
consumption_se4_mw
```

Source:

```text
physical_balance_se1_se4_hourly_v1
```

or the canonical physical-balance source used by P0053C/P0054B.

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
- SE4 historical consumption lags and rollups before forecast origin
- weather forecast if available
- realized weather as LABB proxy if clearly labeled weather_actual_as_forecast_proxy
```

Forbidden inputs:

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

SE4 load state:

```text
lags: 1h, 2h, 3h, 6h, 12h, 24h, 48h, 72h, 168h
rollups: mean 6h/12h/24h/48h/168h, min/max/std 24h
ramps: 1h, 24h, same-hour-vs-168h
```

Weather:

```text
temperature, wind, solar, temperature delta from normal, heating-degree proxy, rapid temperature change, cold-spell proxy
```

Prefer SE4/south weather fields if available. If only broader south/system weather is available, document it.

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

Advanced model:

```text
Prefer the same deterministic sklearn MLP family used in P0054B for apples-to-apples comparison.
```

If sequence dependencies are now available, Codex may also test GRU/LSTM/TCN, but it must still include the comparable MLP-vs-HGB result.

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
Does SE4 confirm the SE3 pattern that MLP can beat HGB without price input?
```

Learning threshold:

```text
>= 2% improvement in holdout MAE or holdout weekly MAE_full_168h
or >= 3% improvement in at least two important conditional regimes
```

This is a LABB learning threshold, not a production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054C/CHANGELOG.md
requirements/package-runs/P0054C/review.md
requirements/package-runs/P0054C/design.md
requirements/package-runs/P0054C/functions.md
requirements/package-runs/P0054C/labb-label.md
requirements/package-runs/P0054C/dataset-contract.md
requirements/package-runs/P0054C/input-classification.md
requirements/package-runs/P0054C/weather-proxy-policy.md
requirements/package-runs/P0054C/feature-groups.md
requirements/package-runs/P0054C/baseline-results.md
requirements/package-runs/P0054C/hgb-results.md
requirements/package-runs/P0054C/advanced-ai-design.md
requirements/package-runs/P0054C/advanced-ai-training-evidence.md
requirements/package-runs/P0054C/advanced-ai-results.md
requirements/package-runs/P0054C/hgb-vs-advanced-ai-comparison.md
requirements/package-runs/P0054C/direct-horizon-results.md
requirements/package-runs/P0054C/weekly-168h-path-results.md
requirements/package-runs/P0054C/conditional-regime-results.md
requirements/package-runs/P0054C/feature-importance-or-attribution.md
requirements/package-runs/P0054C/interpretation.md
requirements/package-runs/P0054C/what-we-learned.md
requirements/package-runs/P0054C/next-package-recommendation.md
requirements/package-runs/P0054C/component-attribution-summary.md
```

Optional compact evidence:

```text
metrics-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
advanced-training-history.csv
modeling-dataset-sample.csv
```

Do not commit large raw datasets or large model binaries.

## Required answers

P0054C must answer:

```text
1. What is the exact SE4 consumption target source and coverage?
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
12. Does SE4 confirm or contradict the SE3 MLP-over-HGB pattern?
13. What did we learn about SE4 consumption?
14. What is the recommended next package?
15. Confirm no price input, no future A09/A11, no production/export/import model, no A61 utilization, no API and no device actions.
```

## Verification checks

Required checks:

```text
- target consumption_se4_mw exists and is numeric/finite
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
- SE4 consumption dataset built
- no price features used
- baselines and HGB evaluated
- advanced AI meaningfully trained or honest WARN/STOP blocker documented
- direct horizon and weekly 168h metrics reported
- fair HGB vs advanced comparison
- what-we-learned evidence explicit
```

WARN is acceptable if:

```text
- sequence model is blocked but MLP/fallback advanced model is trained with evidence
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
- whether SE4 confirms SE3 pattern
- next-package recommendation
- tests run
- files changed
- confirmation of no price/API/device/A61/leakage work
- commit SHA after push

## Completion notes

To be filled after implementation.
