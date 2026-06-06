# P0054T LABB

Status: `PASS`

```json
{
  "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
  "holdout_tuning_policy": "holdout not used for fitting, early stopping, feature selection, hyperparameter selection, ensemble weights, correction fitting, or model-family selection",
  "internal_train": "train_fit and target_timestamp_utc < 2025-03-01T00:00:00Z",
  "internal_validation": "2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
  "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z"
}
```
