# Spotprice ML Normal Model

Last changed: P0035

## Module

```text
src.mac.services.spotprice_ml_model
```

## Purpose

Mac-only local M4 normal spot model tooling.

P0035 consumes the P0035 M3AB-normalized feature DB and trains separate M1-anchored residual models for:

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

P0035 M4 target is residual:

```text
residual = m3ab_normalized_price - M1_normal_price
prediction = M1_normal_price + residual_prediction
evaluation_addback = prediction + M3B_special_day_delta
```

The current implementation uses `scikit-learn`:

```text
PolynomialFeatures(degree=2, include_bias=False)
Ridge(alpha=1.0, fit_intercept=True)
```

The model writes joblib estimator artifacts and JSON metadata for each primary target. A pure-Python Ridge normal-equation implementation remains as fallback if sklearn cannot import, but the fallback is not the preferred M4 result.

Feature schema:

```text
intercept
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
days_since_start_scaled
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

`train_m4_target_model(...)` trains the sklearn residual target model or fallback Ridge model.

`fit_ridge(x, y, ridge_lambda)` is the pure-Python fallback Ridge solver.

`train_m4(...)` builds features, trains separate SE1 and area-diff residual models, writes artifacts and predictions, then promotes validated artifacts to `active/`.

`backtest_m4(...)` trains and reports hourly, level, curve-index and M1-baseline metrics.

`validate_m4_outputs(...)` validates generated artifacts, row counts, split counts and absence of forbidden weather features.

## Safety

This module reads local SQLite data and writes local model artifacts. It does not start a server, install launchd jobs, call devices, call Shelly, call Home Assistant, write KVS, expose an API, or implement M5/M6/M7.
