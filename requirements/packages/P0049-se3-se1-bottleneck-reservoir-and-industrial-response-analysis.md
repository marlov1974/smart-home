# Package P0049: SE3-SE1 bottleneck reservoir and industrial-response analysis

## Status

verified

## Package order

P0049

## Primary area

G2 / Mac tooling / spotprice V2 / SE3-SE1 spread / bottleneck reservoir memory / industrial response hypothesis

## Decision summary

P0049 extends the P0048 SE3-SE1 bottleneck work with a new hypothesis:

```text
SE3-SE1 bottleneck behavior may be governed by an accumulated pressure/reservoir state.

Strong bottleneck-driving signals fill the reservoir.
Weak/normal signals drain it slowly.
Signals below normal or industrial demand response may drain it quickly.
```

P0049 must test whether this reservoir/memory framing explains why lagged SE3-SE1 was so powerful in P0048 and whether it helps forecast SE3-SE1 beyond immediate short-horizon persistence.

P0049 must also test the industrial-response hypothesis:

```text
Large flexible/price-sensitive industrial consumption in SE3 may dampen, delay, or reshape bottleneck behavior.
The delay/response may differ by weekday, Friday, weekend, holiday and hour.
```

P0049 is an analysis package. It must not build a production SE3 forecast, API, device integration or deployable model.

## Preconditions

P0049 may start only after P0048 PASS evidence exists.

Required P0048 facts:

```text
- se3_se1_bottleneck_training_dataset_v1 exists.
- Gradient features were created and no requested gradient fields remained missing.
- P0048 Stage-1 positive bottleneck classification was weak without lagged spread but strong with lagged spread.
- P0048 Stage-2 severity and continuous spread baselines were strongest with lagged spread.
- P0048 recommended comparing direct SE3 AI-1/AI-2 against the best bottleneck path later, not deploying yet.
```

P0049 must STOP if the P0048 bottleneck dataset cannot be found or if SE3-SE1 cannot be reconstructed as:

```text
se3_minus_se1 = se3_price - se1_price
```

## Core hypothesis

P0049 must formalize and test a reservoir model:

```text
bottleneck_pressure[t] =
  decay * bottleneck_pressure[t-1]
  + inflow_from_bottleneck_risk_signals[t]
  - outflow_from_relief_signals[t]
```

Interpretation:

```text
- Physical grid/load/weather signals fill the bottleneck-pressure reservoir.
- Relief signals drain it.
- Price-sensitive demand response may drain or cap it when prices exceed thresholds.
- Friday/weekend/holiday behavior may change fill/drain rates.
```

This is exploratory and diagnostic. It does not become deployable in P0049.

## Scope

P0049 owns:

```text
1. Build reservoir/memory features on top of P0048 dataset.
2. Build price-threshold and industrial-response proxy features.
3. Analyze lagged signal-to-spread response by horizon and day type.
4. Compare instantaneous, rolling, EMA/reservoir and lagged-spread models.
5. Test weekday/friday/weekend/holiday interaction hypotheses.
6. Determine how long current/lagged bottleneck state remains useful for forecasting.
7. Recommend whether P0050 should build a deployable bottleneck model, direct SE3 AI-1/AI-2, or compare both.
```

## Non-goals and hard prohibitions

P0049 must not:

```text
- anchor SE1 shape to SE3
- build SE3 forecast API
- build production SE3 forecast
- retrain or deploy SE1 AI-1/AI-2 product models
- create deployable SE3-SE1 model artifacts
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Exploratory models/configs are allowed as evidence only and must be labeled:

```text
exploratory only, not deployable
```

## Time model

Use the P0042 fixed-CET convention inherited by P0048:

```text
timestamp_utc = primary time identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

Do not use Europe/Stockholm civil time as a primary key.

## Dataset

Start from:

```text
se3_se1_bottleneck_training_dataset_v1
```

Create a derived analysis dataset:

```text
se3_se1_bottleneck_reservoir_analysis_v1
```

Required base columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
model_cet_weekday
model_cet_day_of_year
se1_price
se3_price
se3_minus_se1
spread_regime
is_near_zero
is_positive_bottleneck
is_positive_spike
weather proxy/gradient features from P0048
calendar/special-day features
```

Required new calendar/industrial-response proxy columns:

```text
is_monday
is_tuesday
is_wednesday
is_thursday
is_friday
is_weekend
is_saturday
is_sunday
is_holiday
is_bridge_day
is_holiday_period
hours_until_weekend
hours_since_week_start
hours_since_last_workday_start
is_workday_business_hour
is_evening_peak
is_morning_peak
```

If holiday/bridge features are unavailable in the P0048 dataset, join from the P0042/P0041 special-day schedule if available, otherwise document missing fields.

## Price-response features

P0049 must test whether SE1 and/or SE3 price level acts as a signal for future spread behavior.

Required price features:

```text
se1_price
se3_price
se1_price_delta_from_train_median_by_hour
se3_price_delta_from_train_median_by_hour
se1_price_rank_rolling_7d
se3_price_rank_rolling_7d
se1_price_rank_rolling_30d
se3_price_rank_rolling_30d
se1_price_above_train_p75
se1_price_above_train_p90
se1_price_above_train_p95
se3_price_above_train_p75
se3_price_above_train_p90
se3_price_above_train_p95
hours_since_se1_crossed_p90
hours_since_se3_crossed_p90
hours_above_se1_p90_last_6h
hours_above_se1_p90_last_12h
hours_above_se1_p90_last_24h
hours_above_se3_p90_last_6h
hours_above_se3_p90_last_12h
hours_above_se3_p90_last_24h
```

Thresholds must be fit on train only.

P0049 must explicitly test both hypotheses:

```text
Hypothesis A:
  high SE1 price increases SE3-SE1 risk because it indicates system stress.

Hypothesis B:
  high SE1 price decreases SE3-SE1 risk because the north/south gap compresses.
```

Do not assume direction before analysis.

## Rolling and accumulated signal features

For each relevant signal family, create rolling features over multiple lookback windows.

Required windows:

```text
3h
6h
12h
24h
48h
72h
168h
```

Required signal families:

```text
se3_minus_se1
is_positive_bottleneck
is_positive_spike
se1_price
se3_price
wind_south_minus_north_actual
wind_central_minus_north_actual
wind_south_minus_system_actual
wind_north_minus_system_actual
solar_south_minus_north_actual
temperature_south_minus_north_actual
```

Where available, also include anomaly/delta versions from P0048:

```text
*_delta
*_delta_minus_normal
```

Required rolling feature types:

```text
rolling_mean
rolling_max
rolling_min
rolling_std
rolling_sum for binary regimes
rolling_share for binary regimes
trend = recent_short_mean - previous_window_mean
```

All rolling features must be strictly backward-looking. The current/future target hour must not leak into feature windows unless a clearly documented forecast-origin setup says it is known.

## Reservoir / bucket features

P0049 must create explicit reservoir-pressure indices.

Candidate reservoir formulas must include at least:

```text
R0_weather_pressure_ema_6h
R1_weather_pressure_ema_12h
R2_weather_pressure_ema_24h
R3_weather_pressure_ema_48h
R4_weather_pressure_ema_72h
R5_weather_pressure_ema_168h
```

Each reservoir index must be built from normalized bottleneck-risk signals, for example:

```text
positive normalized wind/solar/temp gradient pressure
+ evening/morning load-risk proxy
+ price-pressure proxy
- relief signals such as strong south wind/solar or falling spread
```

Codex must document the exact formula and normalization.

P0049 must also test at least one data-driven reservoir feature:

```text
learned_pressure_score = simple train-only linear/logistic score from risk features
then EMA/rolling memory applied to the score
```

This may remain exploratory.

## Industrial-response hypotheses

P0049 must explicitly test whether response differs by day type.

Required day-type groups:

```text
monday_to_thursday
friday
saturday
sunday
holiday
bridge_day
holiday_period
```

Required analysis:

```text
- lag between strong risk signal and positive spread by day type
- decay of lagged spread usefulness by day type
- spread after SE1/SE3 price exceeds p90/p95 by day type
- whether Friday afternoon/evening has lower spread persistence than Monday-Thursday
- whether weekends/holidays show more direct physical bottleneck response with less smoothing
```

Required interaction features:

```text
reservoir_pressure × is_friday
reservoir_pressure × is_weekend
reservoir_pressure × is_holiday
price_above_threshold × is_friday
price_above_threshold × is_weekend
price_above_threshold × is_workday_business_hour
lagged_spread × is_friday
lagged_spread × is_weekend
```

P0049 must not treat this as proven unless evidence supports it.

## Horizon analysis

P0049 must evaluate predictability by forecast horizon.

Required horizons:

```text
1h
3h
6h
12h
24h
48h
72h
168h
```

For each horizon H, target should be shifted forward:

```text
classification target at t+H:
  is_positive_bottleneck[t+H]
  is_positive_spike[t+H]

severity target at t+H:
  se3_minus_se1[t+H]
  positive severity conditional on positive regime at t+H
```

Feature rows must use only data available at time t.

This horizon analysis must answer:

```text
How long does observed current/lagged SE3-SE1 remain useful?
When does reservoir/weather/calendar/price response dominate over current spread?
```

## Exploratory model groups

Evaluate at least these feature groups for each horizon:

```text
G0_time_calendar
G1_instant_weather_gradient
G2_rolling_weather_gradient
G3_reservoir_pressure
G4_price_response
G5_lagged_spread_only
G6_lagged_spread_plus_reservoir
G7_lagged_spread_plus_reservoir_plus_industrial_interactions
```

Models may include:

```text
HistGradientBoostingClassifier
HistGradientBoostingRegressor
LogisticRegression / linear baseline
shallow decision tree for interpretability
```

Keep complexity conservative. No neural nets, transformers, AutoML or heavy dependencies.

## Baselines

Required classification baselines:

```text
B0_time_calendar_profile
B1_previous_hour_regime_persistence
B2_train_regime_prior_by_hour_weekday
B3_P0048_best_nonlagged_model
B4_P0048_lagged_diagnostic_model
```

Required regression/severity baselines:

```text
R0_train_mean_or_regime_mean
R1_time_calendar_profile
R2_previous_hour_spread
R3_P0048_continuous_spread_baseline
R4_P0048_lagged_spread_diagnostic
```

## Metrics

Stage/regime classification metrics per horizon:

```text
precision
recall
F1
PR-AUC
ROC-AUC if meaningful
confusion matrix
calibration/reliability table
```

Severity/regression metrics per horizon:

```text
MAE
RMSE
median_absolute_error
p90_absolute_error
p95_absolute_error
bias
spearman/rank correlation
```

Hypothesis diagnostics:

```text
lag-response curves by day type
reservoir pressure vs future spread plots/tables
price threshold response curves
Friday vs Monday-Thursday persistence comparison
weekend/holiday vs workday persistence comparison
feature ablation deltas by horizon
```

## Feature attribution

P0049 must report whether each family helps:

```text
time/calendar
instant weather gradient
rolling weather gradient
explicit reservoir pressure
SE1 price level/thresholds
SE3 price level/thresholds
lagged spread/regime
industrial-response interactions
holiday/bridge features
```

Use at least:

```text
ablation comparison by horizon
feature importance or permutation importance
simple group correlation / response tables
```

## Required evidence files

P0049 must create:

```text
requirements/package-runs/P0049/CHANGELOG.md
requirements/package-runs/P0049/review.md
requirements/package-runs/P0049/design.md
requirements/package-runs/P0049/functions.md
requirements/package-runs/P0049/dataset-contract.md
requirements/package-runs/P0049/reservoir-feature-definitions.md
requirements/package-runs/P0049/price-response-features.md
requirements/package-runs/P0049/industrial-response-hypotheses.md
requirements/package-runs/P0049/training-split.md
requirements/package-runs/P0049/horizon-analysis-results.md
requirements/package-runs/P0049/stage1-regime-by-horizon.md
requirements/package-runs/P0049/stage2-severity-by-horizon.md
requirements/package-runs/P0049/daytype-lag-response.md
requirements/package-runs/P0049/price-threshold-response.md
requirements/package-runs/P0049/feature-ablation-by-horizon.md
requirements/package-runs/P0049/feature-attribution.md
requirements/package-runs/P0049/calibration-and-error-review.md
requirements/package-runs/P0049/spike-case-review.md
requirements/package-runs/P0049/next-package-recommendation.md
requirements/package-runs/P0049/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0049/metrics-summary.json
requirements/package-runs/P0049/horizon-results.json
requirements/package-runs/P0049/daytype-lag-response.csv
requirements/package-runs/P0049/price-threshold-response.csv
requirements/package-runs/P0049/feature-importance.json
requirements/package-runs/P0049/modeling-dataset-sample.csv
```

Do not commit large generated datasets or model binaries.

## Required answers

P0049 must explicitly answer:

```text
1. Which P0048 dataset/table/view was used?
2. Which reservoir formulas were tested?
3. Do rolling/accumulated weather-gradient signals improve over instantaneous weather-gradient signals?
4. Does explicit reservoir pressure improve over rolling features?
5. Does SE1 price level increase or decrease future SE3-SE1 risk?
6. Does SE3 price level behave differently from SE1 price level?
7. Are there price thresholds where spread later falls, suggesting industrial demand response?
8. Does lag/decay differ between Monday-Thursday, Friday, weekend, holiday and bridge days?
9. Is Friday less persistent or less bottleneck-prone after price spikes?
10. Are weekends/holidays more direct/less smoothed than weekdays?
11. How long does current observed SE3-SE1 remain useful: 1h, 3h, 6h, 12h, 24h, 48h, 72h, 168h?
12. At what horizon do reservoir/weather/calendar features become more useful than lagged spread?
13. Is the bottleneck-reservoir path promising enough for P0050?
14. Should P0050 compare against direct SE3 AI-1/AI-2, build a deployable bottleneck prototype, or run more data analysis?
15. Confirm no SE1-to-SE3 anchoring, no API, no production model, no device actions.
```

## Tests

Required automated tests:

```text
- SE3-SE1 equals se3_price - se1_price in the derived dataset
- timestamp_utc and fixed-CET fields are present
- rolling features are strictly backward-looking
- horizon targets are shifted forward correctly
- no future spread/prices leak into features
- price thresholds are fit on train only
- reservoir formulas are documented and reproducible
- day-type interaction fields are deterministic
- chronological splits are non-overlapping
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- reservoir/memory features are built and documented
- price-response and industrial-response hypotheses are tested
- horizon-by-horizon lag/decay behavior is measured
- feature family ablations are reported
- next architecture recommendation is explicit
- forbidden anchoring/API/device work is not done
```

WARN is acceptable if:

```text
- industrial-response evidence is suggestive but not decisive
- reservoir helps only some horizons
- lagged spread dominates short horizons but not long horizons
- Friday/weekend effects are noisy due to limited data
```

STOP if:

```text
- leakage is detected
- rolling/horizon features cannot be trusted
- SE3-SE1 cannot be reconstructed reliably
- Codex anchors SE1 to SE3
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- dataset and split used
- reservoir formulas tested
- price threshold definitions
- horizon-by-horizon metric summary
- day-type lag/response summary
- SE1/SE3 price response conclusion
- industrial-response hypothesis conclusion
- feature attribution conclusion
- recommendation for P0050
- tests run
- files changed
- no SE1-to-SE3 anchoring / no API / no device confirmation
- commit SHA after push

## Completion notes

P0049 PASS.

Implemented `src.mac.services.spotprice_model_diagnostics.p0049` and built the local analysis table:

```text
se3_se1_bottleneck_reservoir_analysis_v1
```

from:

```text
se3_se1_bottleneck_training_dataset_v1
```

Row counts:

```text
source_rows = 34968
persisted_rows = 34968
train = 22728
validate = 8760
holdout = 3480
```

Main result:

```text
- Lagged SE3-SE1 remains the strongest Stage-1 classification signal through 168h in this split.
- Calendar/time baselines beat lagged spread by MAE at some longer horizons, but not by F1.
- Rolling weather gradients are a mild long-horizon correlation improvement over instantaneous gradients, but not a winning family.
- Explicit reservoir pressure did not beat rolling features or lagged spread in the deterministic P0049 diagnostic.
- SE1 price has weak negative future 6h spread correlation; SE3 price has positive future 6h spread correlation.
- Price/day-type response is suggestive only and does not prove industrial demand response.
```

Recommendation:

```text
P0050 should compare direct SE3 AI-1/AI-2 with a non-deployable reservoir/bottleneck prototype under proper forecast-origin validation. Do not build production SE3 API yet.
```

Confirmed:

```text
No SE1-to-SE3 anchoring, no SE3 API, no production model artifact, no M5/M6/M7, no Shelly, no Home Assistant, no KVS and no device actions.
```
