# Spotprice ML Normal Model

Last changed: P0044

## Module

```text
src.mac.services.spotprice_ml_model
```

## Purpose

Mac-only local M4 normal spot model tooling.

P0039 formalizes the Spotprice V2 component taxonomy:

```text
M1  = current calm normal price baseline
M1B = holiday-clean normal price baseline

A = temperature       -> M2A normal, M3A delta
B = special days      -> no M2B normal, M3B delta
C = solar potential   -> M2C normal, M3C delta
D = wind potential    -> M2D normal, M3D delta
```

No M2B is expected because special days are deterministic calendar features, not a weather-normalized signal.

P0036 consumes the P0035/P0036 M3AB-normalized feature DB and trains separate train-only-M1-anchored residual models for:

```text
system_proxy_se1
area_diff_proxy_se3
```

SE3 is recomposed only as:

```text
M4_normalized_price_se3 = M4_normalized_price_se1 + M4_normalized_area_diff_proxy
```

## Inputs

```text
~/.smart-home/data/spotprice_model_features.sqlite3
m3ab_normalized_prices
```

Target columns:

```text
m3ab_normalized_price_se1
m3ab_normalized_area_diff
m3ab_normalized_se3
normal_price_v1_se1
normal_price_v1_area_diff
m3b_special_day_delta_se1
m3b_special_day_delta_area_diff
```

M4 does not use temperature, weather, wind, solar, cloud, radiation or weather-gradient features.

## Local Artifacts

```text
~/.smart-home/data/spotprice_ml_models/m4/
  m4_model.sqlite3
  system_proxy_se1_model.json
  system_proxy_se1_model.joblib
  area_diff_proxy_se3_model.json
  area_diff_proxy_se3_model.joblib
  m4_artifact_manifest.json
```

The repo commits code, tests and docs, not generated model artifacts.

## CLI

```bash
python3 -m src.mac.services.spotprice_ml_model build-features-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model train-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model backtest-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model validate-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
```

## Model

P0039 M1B diagnostics define the forward residual contract:

```text
M1B = holiday-clean baseline
M3A target = actual - M1B
M3B target = actual - M1B - M3A
M3C target = actual - M1B - M3A - M3B
M3D target = actual - M1B - M3A - M3B - M3C
M4 target = actual - M1B - M3A - M3B - M3C - M3D
```

M1B is not the forecast baseplate. It is a holiday-clean training and normalization surface used to learn cleaner component deltas. Until a later package explicitly changes production policy, prediction/evaluation chains keep M1 as the base price and apply M1B-trained deltas on top:

```text
prediction = M1 + M3A_m1b + M3B_m1b + ...
```

M1B training rows include only:

```text
normal_weekday
normal_saturday
normal_sunday
```

Rows classified as public holidays, major social holidays, holiday eves, bridge days, holiday period days, pre/post holiday transitions or special weekend days are excluded from M1B fitting. Midsummer Day is not treated as an ordinary Saturday.

P0036 M4 target is residual:

```text
train_only_M1_m3ab_normalized = robust train-period M1-like median surface
residual = m3ab_normalized_price - train_only_M1_m3ab_normalized
prediction = train_only_M1_m3ab_normalized + residual_prediction
evaluation_addback = prediction + M3B_special_day_delta
```

The current implementation uses `scikit-learn`:

```text
HistGradientBoostingRegressor with bounded max_iter/learning_rate/leaf/l2 grid
```

PolynomialFeatures/Ridge with unbounded time extrapolation is forbidden as the primary M4 model. A pure-Python Ridge normal-equation implementation remains only as diagnostic/fallback utility code and is not a P0036 production promotion path.

The model writes joblib estimator artifacts and JSON metadata for each primary target. Active artifacts are promoted only after the P0036 quality gate passes; WARN/STOP leaves the existing `active/` directory untouched.

Feature schema:

```text
hour_sin
hour_cos
weekday_sin
weekday_cos
day_of_year_sin
day_of_year_cos
iso_week_sin
iso_week_cos
month_sin
month_cos
is_weekend
week_of_month
train_year_index_clipped
```

## Split

```text
train:    2022-05-30..2024-12-31
validate: 2025-01-01..2025-12-31
holdout:  2026-01-01..latest P0033 coverage
```

No random split is used.

## Important Functions

`load_p0033_training_series(feature_db)` loads P0033 normalized targets.

`build_calendar_features(rows)` creates the allowed calendar-only feature matrix.

`build_level_targets(rows)` computes week/month/year target levels.

`build_curve_targets(rows, level_targets)` computes intra-week curve indexes.

`build_week_of_year_indexes(rows)` computes week-vs-year and week-within-month indexes.

`build_clipped_month_curves(rows, level_targets)` builds calendar-month clipped curves and renormalizes each month to mean `1.0`.

`compute_train_only_m1_predictions(...)` fits an M1-like surface on train rows only and applies it to validate/holdout.

`train_m4_target_model(...)` trains bounded HGB candidates and selects by validation residual MAE.

`fit_ridge(x, y, ridge_lambda)` is the pure-Python fallback Ridge solver.

`train_m4(...)` builds train-only M1 features, trains separate SE1 and area-diff residual models, writes artifacts and predictions, then promotes validated artifacts to `active/` only on PASS.

`backtest_m4(...)` trains and reports hourly, level, curve-index and M1-baseline metrics.

`validate_m4_outputs(...)` validates generated artifacts, row counts, split counts and absence of forbidden weather features.

## Safety

This module reads local SQLite data and writes local model artifacts. It does not start a server, install launchd jobs, call devices, call Shelly, call Home Assistant, write KVS, expose an API, or implement M5/M6/M7.

## P0040 Weekly Anchored Diagnostics

P0040 adds a Mac-side diagnostic backtest for short-term 7-day forecasts. It does not build a production API.

The diagnostic emulates Monday 06:00 forecast origins:

```text
known spot context = Monday 00:00..15:00
horizon = 168 hours
primary anchor = additive 16h mean
weather = actual historical weather labeled as forecast proxy/oracle
```

P0040 confirms that M1 remains the baseplate and M1B is only a training/normalization surface for deltas. In the first full weekly anchored backtest, the naive flat anchored week beat component variants on absolute MAE, so the short-term stack still needs level-aware shape work before production API work.

## P0041 Seven-Day Index Dataset

P0041 starts a new seven-day index forecast dataset track. For this track, M1, M1B, M3A, M3B, M3C, M3D and M4 are legacy diagnostic/fallback components, not the primary architecture.

Active foundation for the new track:

```text
M2A = normal temperature / climate normal
M2C = normal solar generation potential
M2D = normal wind generation potential
SE1 and SE3-SE1 target split
Swedish special-day calendar
P0038 weather, solar and wind proxy locations
```

## P0044 AI-1 Day-To-Local-Week Diagnostics

P0044 trains the AI-1 daily/local-week shape and scale diagnostics on the corrected P0042 fixed-CET table:

```text
ai1_day_to_local_week_training_targets_v2
```

The AI-1 targets are:

```text
day_level_shape
log_day_scale_index
log_local_7d_scale
```

P0044 trains separate bounded `HistGradientBoostingRegressor` diagnostics for:

```text
system_proxy_se1
area_diff_proxy_se3
```

and each target above. The split is chronological:

```text
train:    earliest..2024-12-31
validate: 2025-01-01..2025-12-31
holdout:  2026-01-01..latest
```

P0044 uses time, calendar and weather-derived AI-1 features only. It does not use absolute day price, diagnostic ratio targets, AI-2 outputs, actual future spot prices, combined 168-hour forecasts or anchored absolute forecast errors as training targets/features.

The P0044 run status is `WARN`: SE1 targets are usable, area-diff `day_level_shape` is weak but trainable, and area-diff scale targets should use baseline/API-anchor fallback until improved. Evidence is stored under:

```text
requirements/package-runs/P0044/
```

No AI-2 retraining, combined 168-hour forecast, API, M5/M6/M7, Shelly, Home Assistant, KVS or device action is part of P0044.

Local output tables in `~/.smart-home/data/spotprice_model_features.sqlite3`:

```text
m2a_temperature_normals_hourly
m2a_temperature_normals_daily
m2c_solar_normals_hourly
m2c_solar_normals_daily
m2d_wind_normals_hourly
m2d_wind_normals_daily
ai1_day_to_local_week_training_targets
ai2_hour_to_day_training_targets
```

AI-1 rows are `date x target_series` with local window `D-2..D+4`. AI-2 rows are `timestamp x target_series` with fixed local day `00:00..23:00`. Both datasets keep `system_proxy_se1` and `area_diff_proxy_se3` separate; SE3 is recomposed later as `SE1 + (SE3-SE1)`.

P0041 does not train AI models, build an API, or touch optimizer, Shelly, Home Assistant, KVS or device paths.

## P0042 Corrected Seven-Day Index Dataset

P0042 corrects the P0041 datasets before AI training.

UTC remains the primary storage and join truth. P0042 adds a fixed-CET model calendar for AI datasets:

```text
model_cet_timestamp = timestamp_utc + 1 hour
model_cet_date      = date(model_cet_timestamp)
model_cet_hour      = hour(model_cet_timestamp)
```

This is fixed Swedish normal time all year, not Europe/Stockholm civil time. Stockholm-local fields remain diagnostics. The tradeoff is that summer civil-time holiday boundaries differ by one civil hour, while model days are stable 24-hour units.

Corrected local output tables:

```text
m2a_temperature_normals_hourly_v2
m2a_temperature_normals_daily_v2
m2c_solar_normals_hourly_v2
m2c_solar_normals_daily_v2
m2d_wind_normals_hourly_v2
m2d_wind_normals_daily_v2
ai1_day_to_local_week_training_targets_v2
ai2_hour_to_day_training_targets_v2
```

P0042 AI-1 uses `D-2..D+4` over `model_cet_date`. P0042 AI-2 groups by fixed-CET `model_cet_date` so DST transition dates still have 24 model hours.

Scale policy:

```text
system_proxy_se1: generic P0041 robust scale, floor 0.001
area_diff_proxy_se3: max(generic robust scale, historical median complete fixed-CET day scale)
```

The selected area-diff floor is recorded in P0042 evidence. P0042 does not train AI models, build an API, or touch optimizer, Shelly, Home Assistant, KVS or device paths.

## P0043 AI-2 Hour-To-Day Shape Model

P0043 trains AI-2 diagnostics on the corrected P0042 fixed-CET table:

```text
ai2_hour_to_day_training_targets_v2
```

AI-2 is trained separately for:

```text
system_proxy_se1
area_diff_proxy_se3
```

The target is `hour_shape`; P0043 does not train on absolute prices or ratio diagnostics. The split is chronological:

```text
train:    earliest..2024-12-31
validate: 2025-01-01..2025-12-31
holdout:  2026-01-01..latest complete fixed-CET model day
```

P0043 compares train-only baselines B0-B3 and feature groups F0-F4, then trains bounded `HistGradientBoostingRegressor` models. Predictions are day-centered per `model_cet_date` before default evaluation.

P0043 writes model configs and metrics under `requirements/package-runs/P0043/`. It does not commit binary model artifacts, train AI-1, build a production API, or touch optimizer, Shelly, Home Assistant, KVS or device paths.
