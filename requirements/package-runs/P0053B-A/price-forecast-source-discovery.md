# P0053B-A Price Forecast Source Discovery

## Result

No historical SE1 price forecast source with forecast-origin timestamps was found.

## Sources Checked

| Source | Finding | Forecast-safe for P0053B-A |
| --- | --- | --- |
| `~/.smart-home/data/spotprice_history.sqlite3` | Tables include `spot_prices` and `spotprice_system_proxy_hourly`. These are actual historical prices/proxies, not old forecasts. | No |
| `~/.smart-home/data/spotprice_model_features.sqlite3` | Tables include AI-1/AI-2 targets, normalized prices, and `se1_consumption_forecast_warmup_v1`. Price tables contain actual or normalized historical prices; P0053B warmup contains consumption forecast rows, not price forecasts. | No |
| `~/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3` | `m4_hourly_predictions`, `m4_level_predictions`, and `m4_curve_predictions` contain predicted values and splits, but no `forecast_origin_timestamp_utc` or equivalent origin field. | No |
| `~/.smart-home/data/spotprice_ml_models/m4/active/m4_model.sqlite3` | Same schema as non-active M4 DB; no forecast-origin column. | No |
| `src/mac/services/spot_forecast/` | Current weekly forecast service predicts a period-index/shape from requested week context. Discovery did not find persisted historical forecast runs with per-target origin timestamps. | No |
| `requirements/package-runs/P0040/` | Anchored backtest evidence uses forecast origins internally, but stored evidence is aggregate/window diagnostic output, not a durable source table with per-target SE1 predicted price and origin timestamps. | No |
| `requirements/package-runs/P0045/` | Forecast-window diagnostics document model days and regenerated evaluation predictions. They are model-selection diagnostics, not a local price-forecast source that can be joined to P0053B examples with required provenance. | No |

## M4 Schema Evidence

`m4_hourly_predictions` columns:

```text
utc_hour_start
local_date
split
actual_se1
pred_se1
baseline_se1
actual_area_diff
pred_area_diff
baseline_area_diff
actual_se3
pred_se3
baseline_se3
```

`m4_level_predictions` columns:

```text
target
period_type
period_key
actual_level
predicted_level
split
```

`m4_curve_predictions` columns:

```text
target
curve_type
curve_key
actual_index
predicted_index
split
```

These predictions may be evaluation artifacts, but they do not carry a forecast origin. They therefore cannot satisfy the package safety proof.

## Required Source Not Found

No source was found with:

```text
source_table_or_file
forecast_origin_timestamp_utc
target_timestamp_utc
area/zone = SE1
predicted_price
unit
horizon_hours
coverage_start
coverage_end
missingness
```
