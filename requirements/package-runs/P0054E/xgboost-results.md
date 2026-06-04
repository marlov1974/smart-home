# P0054E LABB

```json
{
  "metrics": {
    "holdout": {
      "MAE": 18.130349153087128,
      "MAE_percent_of_mean": 2.9129826429909698,
      "MAE_percent_of_median": 3.0601270511399257,
      "R2": 0.9692659389751597,
      "RMSE": 27.6662624315107,
      "bias": 3.07821217754932,
      "mean_actual_mw": 622.3981181869106,
      "median_absolute_error": 12.8035785585937,
      "median_actual_mw": 592.470471,
      "p10_actual_mw": 434.57770725,
      "p90_absolute_error": 38.630617200781245,
      "p90_actual_mw": 857.8460184999999,
      "p95_absolute_error": 50.00458251875007,
      "row_count": 94765,
      "sMAPE": 0.028670030462740987
    },
    "model_class": "XGBRegressor",
    "row_set": {
      "features": 69,
      "holdout": 94765,
      "train": 247477,
      "validate": 39864
    },
    "validate": {
      "MAE": 21.237454162382946,
      "MAE_percent_of_mean": 3.1974955929042723,
      "MAE_percent_of_median": 3.2697861513318056,
      "R2": 0.9453299052597706,
      "RMSE": 30.463424401042296,
      "bias": 6.210295179971235,
      "mean_actual_mw": 664.1902559463124,
      "median_absolute_error": 16.531155250000012,
      "median_actual_mw": 649.505905875,
      "p10_actual_mw": 495.4336015,
      "p90_absolute_error": 41.39149776289064,
      "p90_actual_mw": 848.1894834999998,
      "p95_absolute_error": 52.029206638476595,
      "row_count": 39864,
      "sMAPE": 0.03242372819928665
    }
  },
  "training": {
    "feature_group": "G4_calendar_load_lags_rollups_weather_proxy",
    "holdout_rows": 94765,
    "hyperparameters": {
      "colsample_bytree": 0.85,
      "eval_metric": "mae",
      "learning_rate": 0.045,
      "max_depth": 7,
      "min_child_weight": 8,
      "n_estimators": 650,
      "n_jobs": -1,
      "objective": "reg:squarederror",
      "random_state": 54,
      "reg_lambda": 1.0,
      "subsample": 0.85,
      "tree_method": "hist"
    },
    "model_artifact_persisted": false,
    "model_class": "XGBRegressor",
    "model_name": "XGBoost_G4_se4_load_weather",
    "package": "xgboost",
    "random_seed": 54,
    "training_duration_seconds": 18.195,
    "training_rows": 247477,
    "validation_rows": 39864,
    "weather_proxy_name": "se4_load_weather"
  }
}
```
