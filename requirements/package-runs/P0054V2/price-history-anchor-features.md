# P0054V2 LABB

Status: `PASS`

```json
{
  "coverage": {
    "complete": true,
    "holdout_rows": 13188,
    "missing_examples": [],
    "missing_stitched_price_rows": 0,
    "origins": 1451,
    "rows": 52173,
    "train_fit_rows": 38985
  },
  "features": [
    "actual_spot_lag_1h",
    "actual_spot_lag_24h",
    "actual_spot_lag_48h",
    "actual_spot_history_0_24h_mean",
    "actual_spot_history_24_48h_mean",
    "actual_spot_history_48h_mean",
    "actual_spot_history_48h_min",
    "actual_spot_history_48h_max",
    "actual_spot_history_48h_spread",
    "actual_spot_last_known_value"
  ],
  "required_minimum": "previous 48h when available",
  "strictly_before_origin": true
}
```
