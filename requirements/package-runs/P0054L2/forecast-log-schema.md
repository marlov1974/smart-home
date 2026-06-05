# P0054L2 Forecast Log Schema

```json
{
  "fields": [
    "forecast_origin_timestamp_utc",
    "input_data_cutoff_utc",
    "target_timestamp_utc",
    "horizon_hours",
    "area",
    "predicted_price",
    "prediction_kind",
    "quality_flag"
  ],
  "prediction_kind": "advanced_absolute_price",
  "quality_flag": "holdout_safe_advanced_price_forecast_not_train_feature",
  "table": "advanced_spotprice_forecast_log_p0054l2_se3_v1"
}
```
