# Package P0053B-A2: SE1 consumption response to anchored price forecast, weather and calendar

## Status

planned

## Package order

P0053B-A2

## Primary area

G2 / Mac tooling / spotprice V2 / SE1 consumption forecast / price-response modeling / anchored M4 price forecast / weather proxy / calendar / weekly holdout backtest

## Decision summary

P0053B proved that SE1 consumption can be forecast from calendar, weather and recent consumption history.

P0053C rebuilt the SE1 consumption warmup under the global forecast period policy:

```text
forecast target rows start = 2022-06-01T00:00:00Z
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

P0053B-A originally stopped because no forecast-safe historical price forecast source existed.

P0053C-A rebuilt M4 and created a shape-index forecast-origin log.

P0053C-B created a leakage-safe 48h-anchored absolute SE1 price forecast-origin log:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
```

The next step is to train/test a SE1 consumption AI model where consumption is modeled as a function of:

```text
anchored forecast spot price
weather
calendar/time
recent historical load state
```

Holdout must be tested weekly from June 2025 through May 2026/latest. Weather forecast is proxied by actual realized weather outcome for this offline experiment.

## Preconditions

P0053B-A2 may start only after:

```text
- P0053C PASS
- P0053C-A PASS
- P0053C-B PASS
```

Required local sources:

```text
- se1_consumption_forecast_warmup_v1 or source table rebuilt by P0053C
- physical_balance_se1_se4_hourly_v1 for consumption_se1 target
- m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
- weather fields already used by P0053B/P0053C consumption rebuild
- calendar/daytype/special-day features from existing forecast feature pipeline
```

P0053B-A2 must STOP if the anchored price forecast log is missing or lacks forecast-origin semantics.

## Scope

P0053B-A2 owns:

```text
1. Build a forecast-safe SE1 consumption modeling dataset with G7 anchored price forecast features.
2. Use P0053C global split policy.
3. Train SE1 consumption models using calendar, weather, recent load and anchored price forecast signals.
4. Run weekly holdout backtests from 2025-06-01 through 2026-05-31/latest.
5. Proxy weather forecast by actual realized weather outcome for this offline test, clearly labeled.
6. Compare models with and without price forecast features on identical rows.
7. Measure whether spot price forecast improves SE1 consumption forecast generally or conditionally during high-price/low-price hours.
8. Recommend whether price forecast features should be kept for SE1 consumption and later SE3/SE4 consumption.
```

## Hard non-goals

P0053B-A2 must not:

```text
- use actual future spot price as a feature
- use target-window actual price to construct price features
- use future actual A09/A11 flow/exchange as features
- forecast SE1 price
- train SE3 price or SE3-SE1 price model
- forecast production
- forecast export/import
- use A61 capacity/utilization/bottleneck margin
- ingest continental price levels
- build production API
- deploy a model artifact
- touch Shelly/Home Assistant/KVS/devices
- touch M5/M6/M7 runtime/device paths
```

Weather actuals may be used only as a clearly labeled offline proxy for weather forecast, not as a deployable claim.

## Target definition

Primary target:

```text
consumption_se1_mw
```

Source:

```text
physical_balance_se1_se4_hourly_v1 or the canonical source used by P0053C rebuild
```

Unit:

```text
MW hourly mean
```

Target rows must satisfy:

```text
target_timestamp_utc >= 2022-06-01T00:00:00Z
```

## Forecast origins and weekly holdout test

The holdout backtest must be weekly.

Primary weekly origins:

```text
origin cadence: weekly
first origin: first valid origin on or after 2025-06-01T00:00:00Z
last origin: latest origin with a complete 168h path, or 2026-05-31/latest documented
horizon: 168 hourly targets per origin
```

Preferred origin convention:

```text
forecast_origin_timestamp_utc = model week start or the same origin convention used by P0053C-B log
```

If P0053C-B log uses daily origins rather than weekly origins, P0053B-A2 must either:

```text
- select weekly subset origins deterministically, or
- evaluate daily origins but separately report weekly-origin subset metrics
```

Required output:

```text
weekly_origin_count
first_weekly_origin
last_weekly_origin
complete_168h_path_count
skipped_origins_with_reason
```

## Global split policy

Use P0053C policy:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

Validation may be used for model/feature selection.

Holdout must not be used for model selection, feature selection or hyperparameter selection.

## Weather proxy policy

For this package only, realized weather outcome may be used as a proxy for weather forecast in offline backtest.

It must be labeled:

```text
weather_actual_as_forecast_proxy
```

P0053B-A2 must report two readiness categories:

```text
offline_backtest_ready_with_weather_proxy
deployable_requires_weather_forecast_feed
```

Evidence must clearly state:

```text
Weather performance may be optimistic because actual realized weather is used as forecast proxy.
```

If forecast-safe weather forecast data exists separately, it may be used and labeled accordingly, but do not block if only realized weather proxy exists.

## Price forecast feature source

Use:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
```

Required join keys/constraints:

```text
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
area = SE1
prediction_kind = anchored_absolute_price
```

Required safety checks:

```text
forecast_origin_timestamp_utc <= target_timestamp_utc
input_data_cutoff_utc <= forecast_origin_timestamp_utc
price anchor history was already validated by P0053C-B
price feature rows come only from forecast log, not actual price table
```

## G7 anchored price forecast features

Create feature group:

```text
G7_m4_48h_anchored_price_forecast
```

Required target-hour features:

```text
forecast_se1_price_target_hour
forecast_se1_price_horizon_h
forecast_se1_price_relative_to_forecast_24h_mean
forecast_se1_price_relative_to_forecast_168h_mean
forecast_se1_price_rank_in_168h
forecast_se1_price_rank_in_forecast_day
forecast_se1_price_top4_forecast_day_flag
forecast_se1_price_top8_forecast_day_flag
forecast_se1_price_bottom4_forecast_day_flag
forecast_se1_price_daily_spread_forecast
forecast_se1_price_volatility_next_24h_forecast
forecast_se1_price_is_daily_peak_half_flag
forecast_se1_price_is_daily_low_half_flag
```

All rank/top/bottom/relative features must be computed only from predictions sharing the same forecast origin.

Do not compute rank/topN from actual prices.

## Base feature groups

Compare against P0053C/P0053B rebuilt base feature groups.

Minimum groups:

```text
G0_calendar_only
G1_calendar_plus_recent_load_lags
G4_calendar_load_lags_weather_proxy
G7_price_only_diagnostic
G4_plus_G7_calendar_load_weather_price
```

Expected production-candidate comparison:

```text
base = calendar + load lags + weather proxy
plus_price = calendar + load lags + weather proxy + G7 anchored price forecast
```

## Models

Train lightweight, interpretable or already dependency-safe models.

Required comparisons:

```text
M4_base_Ridge_G4
M4_plus_G7_Ridge_G4_price
M7_base_HGB_G4
M7_plus_G7_HGB_G4_price
```

Allowed additional models:

```text
ElasticNet
HistGradientBoostingRegressor
RandomForestRegressor if already dependency-safe
simple residual model where price features predict residual consumption after base model
```

Not allowed:

```text
neural nets
transformers
AutoML
heavy new dependencies
production deployment artifacts
```

## Evaluation modes

### Direct horizon evaluation

Evaluate horizons:

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

### Weekly 168h path evaluation

For each weekly forecast origin, predict:

```text
origin .. origin + 167h
```

Report full path metrics and segment metrics.

## Metrics

Required metrics by model, feature group, split and horizon:

```text
MAE
RMSE
bias
median_absolute_error
p90_absolute_error
p95_absolute_error
sMAPE
MAE_percent_of_mean_actual
MAE_percent_of_median_actual
relative_improvement_vs_base_same_rows
```

Weekly path metrics:

```text
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
MAE_full_168h
bias_full_168h
p90_abs_error_full_168h
p95_abs_error_full_168h
daily_energy_error_proxy
peak_load_hour_error
```

Conditional price-response metrics:

```text
forecast_price_top4_day_hours
forecast_price_top8_day_hours
forecast_price_bottom4_day_hours
forecast_price_high_168h_rank_hours
forecast_price_low_168h_rank_hours
cold_plus_forecast_top8_hours
weekday_forecast_top8_hours
weekend_forecast_top8_hours
holiday_forecast_top8_hours
```

Purpose:

```text
Price features may not improve average consumption MAE much, but may improve load-shift hours.
```

## Required interpretation categories

Classify the result as one of:

```text
no_price_response_detected
small_average_effect_only
conditional_effect_on_high_or_low_price_hours
material_general_improvement
degrades_model_due_to_price_noise
inconclusive_due_to_weather_proxy_or_coverage
```

Decision guidance:

```text
If total holdout MAE improves <1% and conditional metrics do not improve, classify no_price_response_detected.
If total MAE improves <1% but top/bottom price conditional error improves >=3%, classify conditional_effect_on_high_or_low_price_hours.
If total holdout MAE improves >=2% across several horizons or weekly path segments, classify material_general_improvement.
If plus_G7 worsens holdout metrics, classify degrades_model_due_to_price_noise unless conditional metrics clearly improve.
```

## Leakage and fairness rules

Base and plus-price models must be compared on identical rows.

Required checks:

```text
- no actual future price columns in feature matrix
- all G7 features from anchored forecast log only
- all G7 features share same forecast_origin as example
- all rank/topN features computed within forecast path from predictions only
- realized weather proxy explicitly labeled
- no future actual A09/A11 flow/exchange
- no future production
- no A61 utilization/margin
- holdout not used for selection
- identical row sets for base vs plus_G7
```

## Required evidence files

P0053B-A2 must create:

```text
requirements/package-runs/P0053B-A2/CHANGELOG.md
requirements/package-runs/P0053B-A2/review.md
requirements/package-runs/P0053B-A2/design.md
requirements/package-runs/P0053B-A2/functions.md
requirements/package-runs/P0053B-A2/dataset-contract.md
requirements/package-runs/P0053B-A2/forecast-origin-join-review.md
requirements/package-runs/P0053B-A2/weather-proxy-policy.md
requirements/package-runs/P0053B-A2/feature-groups.md
requirements/package-runs/P0053B-A2/leakage-review.md
requirements/package-runs/P0053B-A2/direct-horizon-results.md
requirements/package-runs/P0053B-A2/weekly-168h-path-results.md
requirements/package-runs/P0053B-A2/conditional-price-response-results.md
requirements/package-runs/P0053B-A2/base-vs-price-feature-comparison.md
requirements/package-runs/P0053B-A2/feature-importance.md
requirements/package-runs/P0053B-A2/interpretation.md
requirements/package-runs/P0053B-A2/forecast-readiness-assessment.md
requirements/package-runs/P0053B-A2/next-package-recommendation.md
requirements/package-runs/P0053B-A2/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053B-A2/metrics-summary.json
requirements/package-runs/P0053B-A2/weekly-path-metrics.csv
requirements/package-runs/P0053B-A2/conditional-metrics.csv
requirements/package-runs/P0053B-A2/modeling-dataset-sample.csv
```

Do not commit large datasets or model binaries.

## Required answers

P0053B-A2 must explicitly answer:

```text
1. Which consumption target source was used?
2. Which anchored price forecast log was used?
3. Were weekly holdout origins from June 2025 through May 2026/latest created?
4. How was weather forecast proxied?
5. Which G7 anchored price features were created?
6. Did plus_G7 improve Ridge vs base on holdout?
7. Did plus_G7 improve HGB vs base on holdout?
8. Did plus_G7 improve weekly 168h path metrics?
9. Did plus_G7 improve top4/top8/bottom4 price-hour conditional errors?
10. Is price response detectable in SE1 consumption?
11. Should price forecast features be kept for SE1 consumption?
12. Should the same test be repeated for SE2/SE3/SE4 consumption?
13. Is the result deployable or only offline due to realized-weather proxy?
14. Confirm no actual future price leakage, no future A09/A11 leakage, no production/export/import model, no A61 utilization, no API and no device actions.
```

## Tests

Required automated tests:

```text
- anchored price forecast log exists
- forecast_origin_timestamp_utc <= target_timestamp_utc
- input_data_cutoff_utc <= forecast_origin_timestamp_utc
- G7 features derive only from forecast rows sharing same origin
- rank/topN features do not use actual price
- base and plus_G7 evaluations use identical row sets
- weather actual proxy is labeled
- chronological splits follow P0053C policy
- holdout starts at 2025-06-01
- weekly 168h origins have complete paths or are documented skipped
- no actual future price features are present
- no future actual A09/A11 flow/exchange is used
- no future production is used
- no A61 capacity is used
- no API/device path touched
```

## Pass/fail interpretation

PASS requires:

```text
- G7 anchored price features are built leakage-safely
- base vs plus_G7 comparisons are made on identical rows
- weekly holdout backtest is reported
- direct horizon and path metrics are reported
- conditional price-response metrics are reported
- interpretation and next-package recommendation are explicit
- forbidden API/device/A61/future actual leakage work is not done
```

WARN is acceptable if:

```text
- weather is only actual-as-forecast proxy
- price response appears only conditionally
- weekly origins cover less than full year due to data end
- plus_G7 helps Ridge but not HGB, or vice versa
```

STOP if:

```text
- anchored price log is missing
- G7 features cannot be joined by forecast-origin safely
- actual future price leakage is detected
- holdout is used for model selection
- Codex builds production/API/device work
- Codex uses A61 utilization or future A09/A11/production
```

## Expected Codex output

- PASS/WARN/STOP status
- consumption target and anchored price log sources
- weekly origin coverage
- weather proxy statement
- G7 feature summary
- direct horizon results
- weekly 168h path results
- conditional price-response results
- interpretation category
- forecast readiness assessment
- next package recommendation
- tests run
- files changed
- confirmation of no leakage/API/device/A61 work
- commit SHA after push

## Completion notes

To be filled after implementation.
