# P0054L2 Split Policy

```json
{
  "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
  "holdout_used_for_selection_or_fitting": false,
  "internal_validation": "2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
  "policy": "LABB_P0054_TRAIN_THROUGH_MAY_2025",
  "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z"
}
```
