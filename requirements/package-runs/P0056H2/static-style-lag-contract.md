# P0056H2 Static-Style Lag Contract

```json
{
  "contract": "P0056C_static_style_origin_anchored_lags",
  "feature_names": [
    "area_consumption_lag_1h",
    "area_consumption_lag_2h",
    "area_consumption_lag_3h",
    "area_consumption_lag_6h",
    "area_consumption_lag_12h",
    "area_consumption_lag_24h",
    "area_consumption_lag_48h",
    "area_consumption_lag_72h",
    "area_consumption_lag_168h",
    "area_consumption_roll_mean_6h",
    "area_consumption_roll_mean_12h",
    "area_consumption_roll_mean_24h",
    "area_consumption_roll_mean_48h",
    "area_consumption_roll_mean_168h",
    "area_consumption_roll_min_24h",
    "area_consumption_roll_max_24h",
    "area_consumption_roll_std_24h",
    "area_consumption_ramp_1h",
    "area_consumption_ramp_24h",
    "area_consumption_same_hour_24h_vs_168h"
  ],
  "origin_lag_source": "known historical load before forecast origin",
  "same_feature_values_across_36h_horizon": true,
  "target_hour_actual_lags_used": false
}
```
