# P0053B-A2 forecast-origin join review

```json
{
  "anchored_price_log": "m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1",
  "constraints": {
    "area": "SE1",
    "forecast_origin_timestamp_utc_lte_target_timestamp_utc": true,
    "input_data_cutoff_utc_lte_forecast_origin_timestamp_utc": true,
    "prediction_kind": "anchored_absolute_price"
  },
  "coverage_warning": "price_log_has_validation_and_holdout_only; plus_G7 fit uses validation-origin rows as development training",
  "join_keys": [
    "forecast_origin_timestamp_utc",
    "target_timestamp_utc"
  ],
  "price_feature_source": "P0053C-B forecast log only; actual price table is not read by P0053B-A2"
}
```
