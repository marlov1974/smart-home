# P0053C-A Global Split Application

Policy:

```json
{
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
```

AI-1 split counts:

```json
{
  "holdout": 708,
  "train": 1890,
  "validate": 302
}
```

AI-2 split counts:

```json
{
  "holdout": 17230,
  "train": 45360,
  "validate": 7248
}
```

Window counts:

```json
{
  "area_diff_proxy_se3": {
    "holdout": 348,
    "validate": 144
  },
  "system_proxy_se1": {
    "holdout": 348,
    "validate": 144
  }
}
```

P0053C-A accepts only 168h windows where every hourly target timestamp belongs to the same canonical split. Cross-boundary windows are skipped to avoid validation/holdout overlap.
