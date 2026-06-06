# P0054T3 LABB

Status: `WARN`

```json
{
  "p0_full": {
    "internal_split_counts": {
      "internal_train": 35675,
      "internal_validation": 3310,
      "not_train_fit": 13188
    },
    "origins": 1451,
    "rows": 52173,
    "split_counts": {
      "holdout": 13188,
      "train_fit": 38985
    },
    "target_end": "2026-06-04T21:00:00Z",
    "target_start": "2022-06-08T10:00:00Z"
  },
  "p0_matched_price_coverage": {
    "internal_split_counts": {
      "internal_train": 0,
      "internal_validation": 3310,
      "not_train_fit": 12792
    },
    "origins": 448,
    "rows": 16102,
    "split_counts": {
      "holdout": 12792,
      "train_fit": 3310
    },
    "target_end": "2026-05-24T21:00:00Z",
    "target_start": "2025-03-01T00:00:00Z"
  },
  "p1_price_coverage": {
    "internal_split_counts": {
      "internal_train": 0,
      "internal_validation": 3310,
      "not_train_fit": 12792
    },
    "origins": 448,
    "rows": 16102,
    "split_counts": {
      "holdout": 12792,
      "train_fit": 3310
    },
    "target_end": "2026-05-24T21:00:00Z",
    "target_start": "2025-03-01T00:00:00Z"
  },
  "p1_target_contract": {
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
  "source_rows": 35125,
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
  }
}
```
