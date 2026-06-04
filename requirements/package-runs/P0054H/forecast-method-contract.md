# P0054H forecast method contract

```json
{
  "anchor_history_window": "[forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)",
  "area": "SE1",
  "forecast_origin_timestamp_utc": "first target timestamp in each complete daily 168h path",
  "input_data_cutoff_utc": "forecast_origin_timestamp_utc - 1h",
  "m4_compatible": false,
  "m4_reason": "does not use P0045 AI1/AI2 shape predictions; origin-local historical baseline only",
  "method_name": "previous_week_same_hour_else_hist48_same_hour_else_hist48_median",
  "prediction_kind": "anchored_absolute_price",
  "prediction_unit": "source_hour_price_unit",
  "required_columns": [
    "forecast_run_id",
    "model_name",
    "model_version",
    "split_policy_version",
    "package_id",
    "source_model_family",
    "method_name",
    "training_protocol",
    "training_cutoff_utc",
    "prediction_rule",
    "prediction_source_timestamp_utc",
    "anchor_method",
    "anchor_level",
    "anchor_scale",
    "anchor_window_start_utc",
    "anchor_window_end_utc",
    "forecast_origin_timestamp_utc",
    "input_data_cutoff_utc",
    "target_timestamp_utc",
    "horizon_hours",
    "area",
    "predicted_price",
    "prediction_unit",
    "prediction_kind",
    "created_at_utc",
    "quality_flag"
  ],
  "source_model_family": "P0054H_origin_local_history_baseline",
  "table": "anchored_absolute_price_forecast_log_p0054h_se1_v1",
  "target_window": "[forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]",
  "training_protocol": "origin_local_no_fit_pre_origin_history"
}
```
