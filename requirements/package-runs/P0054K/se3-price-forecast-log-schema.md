# P0054K LABB

Status: `PASS`

```json
{
  "area": "SE3",
  "method_name": "previous_week_same_hour_else_hist48_same_hour_else_hist48_median",
  "not_m4": true,
  "prediction_kind": "anchored_absolute_price",
  "prediction_unit": "reconstructed_se3_hour_price_unit",
  "quality_flag": "forecast_safe_origin_local_baseline_not_m4",
  "required_semantics": [
    "forecast_origin_timestamp_utc",
    "input_data_cutoff_utc",
    "target_timestamp_utc",
    "horizon_hours",
    "predicted_price",
    "anchor_window_start_utc",
    "anchor_window_end_utc",
    "source_model_family",
    "package_id"
  ],
  "source_reconstruction": "system_proxy_se1 + area_diff_proxy_se3",
  "table": "anchored_absolute_price_forecast_log_p0054k_se3_v1",
  "training_protocol": "origin_local_no_fit_pre_origin_history"
}
```
