# P0054L2 P0054K Baseline Results

```json
{
  "comparable_holdout_origins": 352,
  "comparable_holdout_rows": 59136,
  "holdout": {
    "MAE": 0.34918660925661843,
    "R2": -0.017559263867389374,
    "RMSE": 0.499184269362603,
    "bias": -0.012247495096049346,
    "median_absolute_error": 0.24964625000000001,
    "p90_absolute_error": 0.7933275000000002,
    "p95_absolute_error": 1.0239875,
    "rows": 59136,
    "sMAPE": 0.7490229933477137
  },
  "label": "forecast_safe_origin_local_baseline_not_m4",
  "model_name": "P0054K_origin_local_history_baseline",
  "ok": true,
  "ranking_spike_ramp": {
    "bottom20_168h_precision": 0.31235795454545423,
    "forecast_price_spike_MAE": 1.1412882630076173,
    "high_price_regime_MAE": 0.9900511877756792,
    "large_price_ramp_MAE": 1.7180335706932024,
    "low_price_detection": {
      "f1": 0.2916140874153952,
      "fn": 3009,
      "fp": 3166,
      "precision": 0.2864548118097814,
      "recall": 0.2969626168224299,
      "tp": 1271
    },
    "low_price_regime_MAE": 0.226879251752336,
    "ramp_detection": {
      "f1": 0.0,
      "fn": 1457,
      "fp": 0,
      "precision": 0.0,
      "recall": 0.0,
      "tp": 0
    },
    "rows": 59136,
    "spearman": 0.5299723887225151,
    "spike_detection": {
      "f1": 0.14163768574138474,
      "fn": 1363,
      "fp": 1352,
      "precision": 0.14213197969543148,
      "recall": 0.14114681789540012,
      "tp": 224
    },
    "top20_168h_precision": 0.30213068181818203
  },
  "table": "anchored_absolute_price_forecast_log_p0054k_se3_v1",
  "weekly": {
    "MAE": 0.34918660925661843,
    "MAE_full_168h": 0.34918660925661843,
    "R2": -0.017559263867389374,
    "RMSE": 0.499184269362603,
    "bias": -0.012247495096049346,
    "bias_full_168h": -0.012247495096049346,
    "complete_origins": 352,
    "median_absolute_error": 0.24964625000000001,
    "p90_absolute_error": 0.7933275000000002,
    "p90_full_path_absolute_error": 0.7933275000000002,
    "p95_absolute_error": 1.0239875,
    "p95_full_path_absolute_error": 1.0239875,
    "rows": 59136,
    "sMAPE": 0.7490229933477137
  }
}
```
