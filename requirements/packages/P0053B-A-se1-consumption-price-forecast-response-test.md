# Package P0053B-A: SE1 consumption price-forecast response test

## Status

stopped

## Package order

P0053B-A

## Primary area

G2 / Mac tooling / spotprice V2 / physical market signals / SE1 consumption forecast / price-response diagnostics / forecast-safe old price forecasts

## Decision summary

P0053B proved that SE1 consumption can be forecast safely and accurately using calendar, historical load lags and weather/proxy features.

Open question:

```text
Does an old forecast of SE1 price add useful information for forecasting SE1 consumption?
```

This package tests whether price-response exists in SE1 consumption when the price feature is a forecast that would have been known at the forecast origin.

Important distinction:

```text
Actual future spot price = forbidden leakage.
Old price forecast available at forecast-origin = allowed, if provenance is proven.
```

P0053B-A is an amendment/diagnostic package. It must not build a SE1 price model or deployable production component.

## Preconditions

P0053B-A may start only after P0053B PASS evidence exists.

Required P0053B facts:

```text
- target consumption_se1 from physical_balance_se1_se4_hourly_v1 is clean.
- se1_consumption_forecast_warmup_v1 exists.
- P0053B forecast-safe conclusion is true.
- best short-horizon model was M4 Ridge calendar + load lags + weather.
- longer-horizon direct model was strong with M7 HGB calendar + load lags + weather.
- no future actual A09/A11, production, price or A61 capacity was used.
```

P0053B-A must STOP if it cannot identify a historical price forecast source with forecast-origin timestamps.

## Scope

P0053B-A owns:

```text
1. Discover existing old SE1 price forecast artifacts/tables in the repo/database.
2. Verify forecast-origin semantics and horizon coverage.
3. Build forecast-safe price-forecast feature groups for SE1 consumption.
4. Compare P0053B best models without price forecast vs with price forecast.
5. Evaluate total MAE/RMSE/bias and price-event conditional errors.
6. Decide whether old price forecasts improve SE1 consumption forecasting enough to keep as a feature.
```

## Hard non-goals

P0053B-A must not:

```text
- use actual future spot price as a feature
- train a SE1 price model
- train a SE3 price model
- train a SE3-SE1 model
- forecast production
- forecast export/import or flow/exchange
- use future actual A09/A11 flow/exchange as feature leakage
- use A61 capacity for anything
- ingest continental price levels
- build production API
- anchor SE1 to SE3
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7 device/runtime work
- ingest futures/forward curves
```

Exploratory comparisons are allowed only for SE1 consumption forecast and must be labeled diagnostic unless forecast safety is proven.

## Price forecast source discovery

P0053B-A must search the repository and local database for historical SE1 price forecast outputs.

Candidate concepts:

```text
old spotprice forecast
legacy price forecast table
AI-1/AI-2 forecast artifacts
forecast run outputs with origin timestamp
stored price prediction per target timestamp/horizon
```

Required source metadata:

```text
source_table_or_file
forecast_origin_timestamp_utc
target_timestamp_utc
area/zone = SE1
predicted_price
unit
horizon_hours
created_at/ingested_at if available
model/version if available
coverage_start
coverage_end
missingness
```

If only final actual spot prices exist, STOP for this package because that is leakage.

If forecast-origin timestamp is missing, STOP or classify as non-forecast-safe diagnostic-only; do not use in deployable comparison.

## Forecast-safety rule

For each training example with forecast origin `t` and target timestamp `t+h`, price-forecast features may use only:

```text
price forecasts generated at or before t
for target timestamp t+h or windows after t
```

Forbidden:

```text
actual spot price at t+h
price forecasts generated after t
price forecast tables that were overwritten without origin history
future realized prices used to compute rank/topN features
```

P0053B-A must explicitly prove:

```text
forecast_origin_timestamp_utc <= example_origin_timestamp_utc
```

for all price forecast feature joins.

## Feature group

Create a new feature group:

```text
G7_forecast_price_signal
```

Candidate features:

```text
forecast_se1_price_target_hour
forecast_se1_price_horizon_h
forecast_se1_price_relative_to_forecast_24h_mean
forecast_se1_price_relative_to_forecast_168h_mean
forecast_se1_price_rank_in_forecast_day
forecast_se1_price_top4_forecast_day_flag
forecast_se1_price_top8_forecast_day_flag
forecast_se1_price_bottom4_forecast_day_flag
forecast_se1_price_daily_spread_forecast
forecast_se1_price_rolling_mean_next_24h_forecast
forecast_se1_price_rolling_max_next_24h_forecast
forecast_se1_price_volatility_next_24h_forecast
```

Rank/topN features must be computed only inside the forecasted price path available at origin, not using actual prices.

If old price forecasts are only available for shorter horizons, restrict the comparison to horizons where forecast price features are available and document coverage.

## Models to compare

P0053B-A must compare at least:

```text
M4_base = P0053B Ridge calendar + load lags + weather
M4_plus_G7 = same + forecast price features

M7_base = P0053B HistGradientBoosting calendar + load lags + weather
M7_plus_G7 = same + forecast price features
```

If implementation cannot exactly reuse P0053B model objects, recreate them with the same splits, targets and feature definitions.

No heavy new modeling framework is allowed.

## Horizons

Evaluate the same direct horizons as P0053B where price forecast coverage exists:

```text
1h
3h
6h
12h
24h
48h
72h
96h
120h
144h
168h
```

If old price forecasts do not cover all horizons, report:

```text
horizon_available
horizon_missing_reason
```

## Metrics

Required total metrics by horizon/model:

```text
MAE
RMSE
median_absolute_error
p90_absolute_error
p95_absolute_error
bias
sMAPE or MAPE if safe
relative_improvement_vs_base
```

Required conditional metrics:

```text
forecast_price_top4_hours
forecast_price_top8_hours
forecast_price_bottom4_hours
forecast_price_high_daily_spread_days
cold_plus_high_forecast_price_rank
weekday_top_price_hours
weekend_top_price_hours
```

Purpose:

```text
Price features may not improve average error much, but may improve high-price response hours.
```

## Evaluation splits

Use the same chronological split as P0053B unless impossible due to price-forecast coverage.

Preferred:

```text
train: earliest .. 2024-12-31
validation: 2025-01-01 .. 2025-12-31
holdout: 2026-01-01 .. latest
```

If coverage is shorter, use the largest chronological split possible and document the limitation.

No random split is allowed.

## Required interpretation

P0053B-A must answer whether price forecast features show:

```text
no_effect
small_average_effect_only
conditional_effect_on_high_price_hours
material_general_improvement
degrades_model_due_to_noise
inconclusive_due_to_coverage
```

Decision rules:

```text
If holdout MAE improves <1% and conditional high-price metrics do not improve, classify no_effect.
If total MAE improves <1% but high-price/topN error improves >=3%, classify conditional_effect_on_high_price_hours.
If total holdout MAE improves >=2% across several horizons, classify material_general_improvement.
If holdout worsens, classify degrades_model_due_to_noise unless conditional metrics strongly improve.
```

## Required evidence files

P0053B-A must create:

```text
requirements/package-runs/P0053B-A/CHANGELOG.md
requirements/package-runs/P0053B-A/review.md
requirements/package-runs/P0053B-A/design.md
requirements/package-runs/P0053B-A/functions.md
requirements/package-runs/P0053B-A/price-forecast-source-discovery.md
requirements/package-runs/P0053B-A/forecast-safety-review.md
requirements/package-runs/P0053B-A/dataset-contract.md
requirements/package-runs/P0053B-A/feature-groups.md
requirements/package-runs/P0053B-A/base-vs-price-feature-results.md
requirements/package-runs/P0053B-A/conditional-price-event-results.md
requirements/package-runs/P0053B-A/horizon-coverage.md
requirements/package-runs/P0053B-A/feature-importance.md
requirements/package-runs/P0053B-A/interpretation.md
requirements/package-runs/P0053B-A/next-package-recommendation.md
requirements/package-runs/P0053B-A/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053B-A/metrics-summary.json
requirements/package-runs/P0053B-A/conditional-metrics.csv
requirements/package-runs/P0053B-A/price-feature-coverage.json
requirements/package-runs/P0053B-A/modeling-dataset-sample.csv
```

Do not commit large generated datasets or model binaries.

## Required answers

P0053B-A must explicitly answer:

```text
1. Was a historical SE1 price forecast source found?
2. Does it have forecast-origin timestamps?
3. What period and horizons are covered?
4. How was leakage avoided?
5. Which G7 price forecast features were created?
6. Does adding G7 improve M4 Ridge total holdout metrics?
7. Does adding G7 improve M7 HGB total holdout metrics?
8. Does adding G7 improve errors on forecast top4/top8 price hours?
9. Is the effect stronger on cold + high forecast-price-rank hours?
10. Should price forecast features be kept for SE1 consumption?
11. Should the same test be repeated for SE3/SE4 consumption later?
12. Confirm no actual future price leakage, no SE1 price model, no SE3/SE3-SE1 model, no production/export/import model, no A61/utilization, no API and no device actions.
```

## Tests

Required automated tests:

```text
- price forecast source has forecast_origin_timestamp_utc
- price forecast join enforces forecast_origin <= example_origin
- no actual future spot price columns are used as features
- rank/topN price features are computed from forecast path only
- chronological splits are non-overlapping
- base model feature set matches P0053B as closely as practical
- G7 feature group can be toggled on/off
- metrics compare identical row subsets for base vs plus_G7
- no future actual A09/A11 flow/exchange is used
- no production/price target model is trained
- no A61 capacity is used
- no API/device path touched
```

## Pass/fail interpretation

PASS requires:

```text
- historical price forecast source with origin semantics is found
- leakage-safe G7 features are built
- base vs G7 models are compared on identical rows
- total and conditional metrics are reported
- recommendation is explicit
- forbidden price/export/production/API/device work is not done
```

WARN is acceptable if:

```text
- source coverage is partial but enough for a meaningful diagnostic
- price forecast improves only conditional high-price hours
- effect is inconclusive but leakage review is solid
```

STOP if:

```text
- only actual prices are available
- forecast-origin semantics cannot be proven
- leakage is detected
- Codex starts price/export/production modeling
- Codex uses A61/utilization or future actual A09/A11 as forecast features
- Codex creates API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- price forecast source and coverage
- forecast-safety proof
- G7 feature summary
- base vs G7 model metrics by horizon
- conditional top4/top8/cold+high-price metrics
- interpretation category
- recommendation for SE1 consumption and later SE3/SE4 consumption
- tests run
- files changed
- confirmation of no leakage / no price model / no export-production model / no A61 / no API / no device actions
- commit SHA after push

## Completion notes

Completed 2026-06-04 with status `STOP`.

Discovery found no historical SE1 price forecast source with provable forecast-origin timestamps. Candidate sources were actual spot-price history, originless M4 prediction/evaluation tables, current weekly forecast tooling without persisted historical forecast origins, and P0040/P0045 diagnostic evidence. None satisfied the required proof:

```text
forecast_origin_timestamp_utc <= example_origin_timestamp_utc
```

No G7 price features were created, no base-vs-G7 models were trained, and no metrics were computed. This avoided actual future price leakage and originless prediction leakage.

Evidence is stored under:

```text
requirements/package-runs/P0053B-A/
```

No source code, API, Shelly/Home Assistant/KVS/device path, A61/utilization, price model, export/import model or production model was changed.
