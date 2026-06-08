# P0056G Model Variant Contract

```json
{
  "A_static_baseline": {
    "FI": {
      "DayAhead_hourly_MAE": 332.717,
      "baseline_name": "P0056C_static",
      "full_36h_MAE": 311.189,
      "source": "P0056C area-results"
    },
    "SE1": {
      "DayAhead_hourly_MAE": 125.21953299342522,
      "baseline_name": "P0056E_V2_static",
      "full_36h_MAE": 123.509,
      "source": "P0056E area-variant-results"
    },
    "SE2": {
      "DayAhead_hourly_MAE": 206.179,
      "baseline_name": "P0056F_W12_static",
      "full_36h_MAE": 197.547,
      "source": "P0056F area-results"
    },
    "SE3": {
      "DayAhead_hourly_MAE": 258.869,
      "baseline_name": "P0056C_static",
      "full_36h_MAE": 250.928,
      "source": "P0056C area-results"
    }
  },
  "B_weekly_HGB_no_price": {
    "feature_counts_by_area": {
      "FI": 50,
      "SE1": 48,
      "SE2": 50,
      "SE3": 50
    },
    "feature_source": "P0056C/P0056F no-price feature family",
    "flow_exchange_a61_capacity_features": false,
    "model_artifacts_persisted": false,
    "model_family": "HGB",
    "model_name": "Weekly_HGB_no_price",
    "spot_price_features": false
  }
}
```
