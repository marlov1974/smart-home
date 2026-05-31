# P0034 holdout results

## Identity

```text
package_id = P0034
model_id = M4
model_version = m4_sklearn_polynomial_ridge_v2
model_class = scikit-learn PolynomialFeatures(degree=2) + Ridge(alpha=1.0)
status = WARN
```

`WARN` reason: scikit-learn is installed and used, but M4 does not beat the P0033 M1 baseline on the key holdout hourly and level metrics.

## Inputs and artifacts

```text
feature_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
input_table = m3_temp_normalized_prices_v1
model_dir = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
model_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3
metadata_artifacts = system_proxy_se1_model.json, area_diff_proxy_se3_model.json
estimator_artifacts = system_proxy_se1_model.joblib, area_diff_proxy_se3_model.joblib
```

Large generated artifacts remain local and are not committed.

## Schema

Feature schema version:

```text
m4_calendar_features_v1, expanded by sklearn PolynomialFeatures(degree=2)
```

Base features:

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

Target schema:

```text
system_proxy_se1 = temp_normalized_price_v1_se1
area_diff_proxy_se3 = temp_normalized_area_diff_v1
recomposed_se3 = system_proxy_se1 + area_diff_proxy_se3
```

Forbidden forecast-time weather/temperature features are not included.

## Split and leakage controls

```text
train = 2022-05-30..2024-12-31, rows = 22729
validate = 2025-01-01..2025-12-31, rows = 8760
holdout = 2026-01-01..2026-05-24, rows = 3455
excluded_rows = 0
random_seed = none used by Ridge; deterministic pipeline
time_split_method = fixed chronological split
leakage_controls = no random split, no actual/future prices as features, no weather/temperature features
```

## Holdout hourly metrics

| target | M4 MAE | M4 RMSE | P0033 M1 MAE | P0033 M1 RMSE | winner |
|---|---:|---:|---:|---:|---|
| system_proxy_se1 | 0.5955499675395327 | 0.7683190174304994 | 0.3430024913169314 | 0.48352073558571185 | P0033 M1 |
| area_diff_proxy_se3 | 1.8329536040834036 | 1.8847956763097777 | 0.20408917583212727 | 0.29430242065818596 | P0033 M1 |
| recomposed_se3 | 1.6277238925618174 | 1.8226038667974305 | 0.39073463277858034 | 0.5037357192319121 | P0033 M1 |

## Holdout level metrics

| target | scope | M4 MAE | M4 RMSE | P0033 M1 MAE | P0033 M1 RMSE | winner |
|---|---|---:|---:|---:|---:|---|
| system_proxy_se1 | week | 0.5122083103454314 | 0.641117004359569 | 0.277581889525318 | 0.35468130617359367 | P0033 M1 |
| system_proxy_se1 | month | 0.46691726105832004 | 0.577284981183712 | 0.2644712680472346 | 0.3068883190278867 | P0033 M1 |
| area_diff_proxy_se3 | week | 1.8204474183871173 | 1.8290741826451842 | 0.15250283211319704 | 0.1784245975631708 | P0033 M1 |
| area_diff_proxy_se3 | month | 1.833699195358216 | 1.8372697780570382 | 0.12877349115751635 | 0.15667058475188234 | P0033 M1 |

## Holdout curve-index metrics

| target | scope | M4 MAE | M4 RMSE | P0033 M1 MAE | P0033 M1 RMSE | winner |
|---|---|---:|---:|---:|---:|---|
| system_proxy_se1 | week | 2.2211370565726325 | 6.426912798459319 | 0.4737497337069649 | 0.6588152814779519 | P0033 M1 |
| system_proxy_se1 | month | 1.160191494454649 | 1.5632991141042716 | 0.5427705767162805 | 0.7438427018373691 | P0033 M1 |
| area_diff_proxy_se3 | week | 1.0644801606909382 | 1.8417655219874325 | 1.1646626040015942 | 1.9490726728797394 | M4 sklearn |
| area_diff_proxy_se3 | month | 0.9767511137275435 | 1.3696159141968047 | 1.0552730780183368 | 1.553164003188756 | M4 sklearn |

## Not applicable metrics

Rank accuracy for cheapest/most expensive hours and top/bottom quantile precision were not implemented in P0034 because this package builds the first M4 training/backtest foundation and does not expose a selection or optimizer surface.

Week-of-year and week-within-month behavior is represented through week/month level and curve-index metrics above. Monthly clipped-curve behavior is represented by month curve-index metrics.
