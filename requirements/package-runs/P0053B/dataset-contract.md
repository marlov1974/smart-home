# P0053B dataset contract

```json
{
  "dataset_table": "se1_consumption_forecast_warmup_v1",
  "row_counts": {
    "direct_horizon_rows": 382106,
    "path_origins": 1006,
    "persisted_rows": 382106,
    "source_rows": 34968
  },
  "source": {
    "duplicates": 0,
    "end": "2026-05-25T22:00:00Z",
    "fixed_cet_missing": 0,
    "nonfinite_values": 0,
    "nonpositive_values": 0,
    "ok": true,
    "rows": 34968,
    "source_aggregation": "P0051 hourly mean from eSett quarter-hour production/consumption rows",
    "source_table": "physical_balance_se1_se4_hourly_v1",
    "start": "2022-05-29T23:00:00Z",
    "target": "consumption_se1",
    "unit": "MW hourly mean"
  },
  "split_counts": {
    "holdout": 38280,
    "train": 247466,
    "validate": 96360
  }
}
```
