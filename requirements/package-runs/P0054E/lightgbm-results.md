# P0054E LABB

```json
{
  "metrics": {
    "holdout": {
      "MAE": 17.70265003542135,
      "MAE_percent_of_mean": 2.844264710663074,
      "MAE_percent_of_median": 2.987937948289975,
      "R2": 0.9763197471954778,
      "RMSE": 24.284752673628432,
      "bias": 0.8044962521761403,
      "mean_actual_mw": 622.3981181869106,
      "median_absolute_error": 12.847339526121687,
      "median_actual_mw": 592.470471,
      "p10_actual_mw": 434.57770725,
      "p90_absolute_error": 39.731306850912894,
      "p90_actual_mw": 857.8460184999999,
      "p95_absolute_error": 52.07630235494152,
      "row_count": 94765,
      "sMAPE": 0.027694755104392208
    },
    "model_class": "LGBMRegressor",
    "row_set": {
      "features": 69,
      "holdout": 94765,
      "train": 247477,
      "validate": 39864
    },
    "validate": {
      "MAE": 19.37276746182499,
      "MAE_percent_of_mean": 2.9167497247040193,
      "MAE_percent_of_median": 2.9826930419864963,
      "R2": 0.9636734151445937,
      "RMSE": 24.832251209163566,
      "bias": 2.535552324473888,
      "mean_actual_mw": 664.1902559463124,
      "median_absolute_error": 15.900453619623931,
      "median_actual_mw": 649.505905875,
      "p10_actual_mw": 495.4336015,
      "p90_absolute_error": 40.200046307523095,
      "p90_actual_mw": 848.1894834999998,
      "p95_absolute_error": 49.028230692832686,
      "row_count": 39864,
      "sMAPE": 0.02972913880195043
    }
  },
  "training": {
    "feature_group": "G4_calendar_load_lags_rollups_weather_proxy",
    "holdout_rows": 94765,
    "hyperparameters": {
      "colsample_bytree": 0.85,
      "learning_rate": 0.045,
      "metric": "mae",
      "min_child_samples": 80,
      "n_estimators": 650,
      "n_jobs": -1,
      "num_leaves": 63,
      "objective": "regression_l1",
      "random_state": 54,
      "reg_lambda": 0.2,
      "subsample": 0.85,
      "subsample_freq": 1
    },
    "model_artifact_persisted": false,
    "model_class": "LGBMRegressor",
    "model_name": "LightGBM_G4_se4_load_weather",
    "package": "lightgbm",
    "random_seed": 54,
    "training_duration_seconds": 23.052,
    "training_rows": 247477,
    "validation_rows": 39864,
    "weather_proxy_name": "se4_load_weather"
  }
}
```
