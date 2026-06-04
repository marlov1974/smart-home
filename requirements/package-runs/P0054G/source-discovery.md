# P0054G Source Discovery

Local SQLite database inspected:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
```

Forecast/price/M4/prediction-like tables found:

| table | relevance | coverage summary |
|---|---|---|
| `m4_price_shape_forecast_origin_log_p0053ca_v1` | M4 shape/index forecast-origin log | one holdout origin only, target range 2025-06-01T23:00:00Z..2026-05-21T22:00:00Z |
| `m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1` | anchored absolute SE1 price forecast-origin log | validation and holdout only, zero train rows |
| `m1_normal_price_v1` | historical/normalized price data | not a forecast-origin log |
| `m1b_holiday_clean_normal_price` | historical/normalized price data | not a forecast-origin log |
| `m3_temp_normalized_prices_v1` | historical/normalized price data | not a forecast-origin log |
| `m3ab_normalized_prices` | historical/normalized price data | not a forecast-origin log |
| `m3abcd_normalized_prices` | historical/normalized price data | not a forecast-origin log |
| `m3abcd_normalized_prices_m1b` | historical/normalized price data | not a forecast-origin log |
| `se1_consumption_forecast_warmup_v1` | consumption warmup | not a price forecast log |

Source target availability also exists for SE1:

| table | filter | range |
|---|---|---|
| `ai2_hour_to_day_training_targets_v2` | `target_series='system_proxy_se1'` | 2022-05-29T23:00:00+00:00..2026-05-25T22:00:00+00:00 |
| `ai1_day_to_local_week_training_targets_v2` | `target_series='system_proxy_se1'` | 2022-06-01..2026-05-21 |

Those are target/training tables, not ready forecast-origin logs for train-period downstream features.

## Result

No existing local table provides forecast-origin-safe SE1 anchored absolute price rows across train, validation and holdout.
