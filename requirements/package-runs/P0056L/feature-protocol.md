# P0056L Feature Protocol

```json
{
  "base_protocol": {
    "features": [
      "safe_same_hour_lag_168h",
      "safe_same_hour_lag_336h",
      "safe_same_hour_delta_168_336h",
      "origin_consumption_lag_1h",
      "origin_consumption_lag_24h",
      "origin_consumption_lag_168h",
      "origin_roll_mean_24h",
      "origin_roll_mean_168h",
      "origin_roll_std_24h"
    ],
    "future_actual_load_used": false,
    "lag_protocol": "DA-L3 seasonal_safe"
  },
  "future_actual_load_used": false,
  "sequence_features": {
    "N2_SequenceMLP_168h": "168 known-at-origin historical load values"
  }
}
```
