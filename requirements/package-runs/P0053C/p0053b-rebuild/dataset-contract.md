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
    "holdout": 94765,
    "train": 247477,
    "validate": 39864
  },
  "split_policy": {
    "boundary_identity": "timestamp_utc",
    "context_only_lag_warmup": true,
    "fixed_cet_rule": "model_cet_timestamp = timestamp_utc + 1h all year; calendar feature only",
    "forecast_modeling_start_utc": "2022-06-01T00:00:00Z",
    "holdout_start_utc": "2025-06-01T00:00:00Z",
    "model_development_end_utc": "2025-05-31T23:00:00Z",
    "model_development_start_utc": "2022-06-01T00:00:00Z",
    "policy_version": "forecast_period_policy_v1_p0053c",
    "train_end_utc": "2024-12-31T23:00:00Z",
    "train_start_utc": "2022-06-01T00:00:00Z",
    "validation_end_utc": "2025-05-31T23:00:00Z",
    "validation_start_utc": "2025-01-01T00:00:00Z"
  }
}
```
