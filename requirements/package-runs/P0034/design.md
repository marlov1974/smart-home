# P0034 implementation design

## Inputs

P0034 reads:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
m3_temp_normalized_prices_v1
```

Target columns:

- `temp_normalized_price_v1_se1`
- `temp_normalized_area_diff_v1`

Diagnostic/baseline columns:

- `normal_price_v1_se1`
- `normal_price_v1_area_diff`
- `temp_normalized_price_v1_se3`

## Feature schema

Allowed calendar/slow-trend features only:

- `intercept`
- `hour_sin`, `hour_cos`
- `weekday_sin`, `weekday_cos`
- `day_of_year_sin`, `day_of_year_cos`
- `iso_week_sin`, `iso_week_cos`
- `month_sin`, `month_cos`
- `is_weekend`
- `week_of_month`
- `days_since_start_scaled`

Forbidden and excluded:

- temperature
- weather anomalies
- wind/solar/cloud/radiation
- weather gradients
- future prices
- short lag features
- SE3 monolithic primary target

## Target schema

Separate target models:

```text
system_proxy_se1      -> temp_normalized_price_v1_se1
area_diff_proxy_se3   -> temp_normalized_area_diff_v1
```

Recomposed diagnostic output:

```text
M4_normal_price_se3 = M4_normal_price_se1 + M4_normal_area_diff_proxy
```

## Model algorithms

Because `scikit-learn` is unavailable, P0034 uses a deterministic pure-Python Ridge linear model:

```text
beta = (X'X + lambda I)^-1 X'y
lambda = 1.0
```

The intercept is not regularized. Gaussian elimination with partial pivoting solves the normal equations.

## Level and curve components

Level model:

- weekly mean by target
- monthly mean by target
- yearly mean by target

Curve/index model:

- intra-week hour index = target / weekly mean with safe zero handling
- week index vs year = week mean / year mean
- week within month index = week mean / month mean
- month index vs year = month mean / year mean

Monthly clipped-week curve:

- for each calendar month, include only rows whose `local_date` falls inside that month.
- group included hours by intersecting ISO week.
- build clipped week curves from the included month hours only.
- re-normalize month curve so its mean over the calendar month is `1.0`.

## Train/validation/holdout split

Time-based split:

```text
train:    2022-05-30..2024-12-31
validate: 2025-01-01..2025-12-31
holdout:  2026-01-01..2026-05-24
```

No random split is used.

## Storage

Local generated model directory:

```text
~/.smart-home/data/spotprice_ml_models/m4/
```

Local generated DB:

```text
~/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3
```

Artifacts:

- `system_proxy_se1_model.json`
- `area_diff_proxy_se3_model.json`
- `m4_artifact_manifest.json`

## CLI

```bash
python3 -m src.mac.services.spotprice_ml_model build-features-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model train-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model backtest-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model validate-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
```

## Metrics

Report separately for:

- SE1
- area_diff
- recomposed SE3

Metrics:

- MAE
- RMSE
- level MAE/RMSE by weekly means
- weekly curve index MAE
- monthly curve index MAE
- baseline comparison against P0033 M1 normals

## Deferred work

M5/M6/M7, forecast API/server, temperature forecast delta, futures/forward data, launchd and device/control integration are deferred.
