# P0054D LABB

```json
{
  "metrics": {
    "holdout": {
      "MAE": 18.610572862410447,
      "MAE_percent_of_mean": 2.990139641910286,
      "MAE_percent_of_median": 3.141181505805451,
      "R2": 0.974251436737391,
      "RMSE": 25.323108630837304,
      "bias": 1.6550352084183046,
      "mean_actual_mw": 622.3981181869106,
      "median_absolute_error": 13.417440177204071,
      "median_actual_mw": 592.470471,
      "p10_actual_mw": 434.57770725,
      "p90_absolute_error": 43.10353395540919,
      "p90_actual_mw": 857.8460184999999,
      "p95_absolute_error": 54.477605704509,
      "row_count": 94765,
      "sMAPE": 0.02902538422584566
    },
    "model_class": "ExtraTreesRegressor",
    "row_set": {
      "features": 69,
      "holdout": 94765,
      "train": 247477,
      "validate": 39864
    },
    "validate": {
      "MAE": 20.017556549507837,
      "MAE_percent_of_mean": 3.0138286989753564,
      "MAE_percent_of_median": 3.0819668256196415,
      "R2": 0.9602611143184695,
      "RMSE": 25.9723741218998,
      "bias": 2.831011297775306,
      "mean_actual_mw": 664.1902559463124,
      "median_absolute_error": 16.388705673964466,
      "median_actual_mw": 649.505905875,
      "p10_actual_mw": 495.4336015,
      "p90_absolute_error": 40.359853523442794,
      "p90_actual_mw": 848.1894834999998,
      "p95_absolute_error": 50.20192583557192,
      "row_count": 39864,
      "sMAPE": 0.03075150750468377
    }
  },
  "training": {
    "advanced_model_type": "ExtraTreesRegressor",
    "early_stopping_reason": "not_applicable",
    "feature_group": "G4_calendar_load_lags_rollups_weather_proxy",
    "holdout_rows": 94765,
    "hyperparameters": {
      "bootstrap": true,
      "max_features": 0.75,
      "max_samples": 0.8,
      "min_samples_leaf": 4,
      "n_estimators": 180,
      "n_jobs": -1
    },
    "random_seed": 54,
    "resource_limits": "sklearn dependency-safe ensemble; no model artifact persisted",
    "training_duration_seconds": 32.851,
    "training_rows": 247477,
    "validation_rows": 39864,
    "weather_proxy_name": "se4_load_weather"
  }
}
```
