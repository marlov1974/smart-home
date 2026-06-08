# P0056E Split Policy Applied

```json
{
  "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
  "holdout_used_for_fit_or_selection": "false",
  "internal_selection_data": "internal_validation_only",
  "internal_validation": "2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
  "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z"
}
```
