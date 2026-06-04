# P0053C-B forecast-origin contract

```json
{
  "anchor_history_window": "[forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)",
  "forecast_origin_timestamp_utc": "first target timestamp in each 168h rolling path",
  "input_data_cutoff_utc": "forecast_origin_timestamp_utc - 1h",
  "prediction_kind": "anchored_absolute_price",
  "prediction_unit": "source_hour_price_unit",
  "required_columns": [
    "forecast_run_id",
    "source_shape_run_id",
    "model_name",
    "model_version",
    "split_policy_version",
    "anchor_method",
    "anchor_level",
    "anchor_scale",
    "anchor_history_start_utc",
    "anchor_history_end_utc",
    "forecast_origin_timestamp_utc",
    "input_data_cutoff_utc",
    "target_timestamp_utc",
    "horizon_hours",
    "area",
    "predicted_price",
    "prediction_unit",
    "prediction_kind",
    "source_shape_value",
    "created_at_utc",
    "quality_flag"
  ],
  "selection_policy": "A0-A3 selected on validation MAE_full_168h only; holdout report-only",
  "table": "m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1",
  "target_window": "[forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]"
}
```
