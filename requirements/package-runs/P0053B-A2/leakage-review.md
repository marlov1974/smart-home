# P0053B-A2 leakage review

```json
{
  "base_plus_identical_row_sets": true,
  "chronological_splits_follow_p0053c": true,
  "coverage_warning": "price_log_has_validation_and_holdout_only; plus_G7 fit uses validation-origin rows as development training",
  "fairness_error_count": 0,
  "forbidden_feature_names": [],
  "forecast_origin_timestamp_utc_lte_target_timestamp_utc": true,
  "g7_features_from_forecast_origin_groups_only": true,
  "grouping_error_count": 0,
  "holdout_starts_at_2025_06_01": true,
  "holdout_used_for_model_fit_or_selection": false,
  "input_data_cutoff_utc_lte_forecast_origin_timestamp_utc": true,
  "no_a61_capacity_or_utilization": true,
  "no_actual_future_price_features": true,
  "no_api_or_device_path_touched": true,
  "no_future_a09_a11_flow_exchange": true,
  "no_future_production": true,
  "ok": true,
  "order_error_count": 0,
  "rank_topn_features_use_predicted_price_only": true,
  "weather_actual_proxy_labeled": true
}
```
