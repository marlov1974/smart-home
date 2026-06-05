# P0054N LABB

Status: `PASS`

```json
{
  "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
  "policy_name": "LABB_P0054_TRAIN_THROUGH_MAY_2025",
  "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
  "train_side_advanced_price_training_cutoff": "2025-03-01T00:00:00Z minus one hour for train-side blocked predictions"
}
```
