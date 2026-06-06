# P0054R LABB

Status: `PASS`

```json
{
  "advanced_price": "not_used_in_primary_p0054r_models_no_price_only",
  "dataset_kind": "offline_labb_corrected_entsoe_target_advanced_ai_experiment_not_deployable",
  "target": {
    "area": "SE3",
    "area_scope": "bidding_zone_internal_consumption_or_load",
    "duplicates": 0,
    "end": "2026-06-05T10:00:00Z",
    "holdout_source_rows": 8859,
    "mean_mw": 9491.743430604978,
    "median_mw": 9128.0,
    "nonfinite_values": 0,
    "ok": true,
    "old_physical_balance_target_used": false,
    "rows": 35125,
    "source_table": "entsoe_consumption_area_hourly_v1",
    "source_type": "actual_total_load",
    "start": "2022-06-01T00:00:00Z",
    "target_column": "consumption_mw",
    "target_field": "target_consumption_se3_mw",
    "train_fit_source_rows": 26266,
    "unit": "MW hourly mean",
    "usable_for_consumption_target": true
  },
  "weather": {
    "area_proxy": "se3_load_weather",
    "available": true,
    "end": "2026-05-30T21:00:00Z",
    "input_classification": "proxy",
    "proxy_label": "weather_actual_as_forecast_proxy",
    "rows": 35088,
    "start": "2022-05-29T22:00:00Z",
    "table": "weather_area_hourly"
  },
  "weather_proxy_label": "weather_actual_as_forecast_proxy"
}
```
