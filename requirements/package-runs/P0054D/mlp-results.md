# P0054D LABB

```json
{
  "metrics": {
    "holdout": {
      "MAE": 21.65082416112652,
      "MAE_percent_of_mean": 3.4786133711645677,
      "MAE_percent_of_median": 3.6543296621320587,
      "R2": 0.9592596628738974,
      "RMSE": 31.85318227343623,
      "bias": 1.0659130944356263,
      "mean_actual_mw": 622.3981181869106,
      "median_absolute_error": 16.88514862204181,
      "median_actual_mw": 592.470471,
      "p10_actual_mw": 434.57770725,
      "p90_absolute_error": 43.82587526728357,
      "p90_actual_mw": 857.8460184999999,
      "p95_absolute_error": 54.39464914759352,
      "row_count": 94765,
      "sMAPE": 0.035291709396111655
    },
    "model_class": "MLPRegressor",
    "row_set": {
      "features": 69,
      "holdout": 94765,
      "train": 247477,
      "validate": 39864
    },
    "validate": {
      "MAE": 25.51920768179296,
      "MAE_percent_of_mean": 3.8421532766141215,
      "MAE_percent_of_median": 3.9290185741135097,
      "R2": 0.9107872034802398,
      "RMSE": 38.915031315434916,
      "bias": 5.433642957930933,
      "mean_actual_mw": 664.1902559463124,
      "median_absolute_error": 20.165022453175766,
      "median_actual_mw": 649.505905875,
      "p10_actual_mw": 495.4336015,
      "p90_absolute_error": 49.43330213954572,
      "p90_actual_mw": 848.1894834999998,
      "p95_absolute_error": 60.592879816548106,
      "row_count": 39864,
      "sMAPE": 0.03934239579569908
    }
  },
  "training": {
    "advanced_ai_type": "small_mlp",
    "advanced_model_type": "MLPRegressor",
    "architecture_summary": "sklearn MLPRegressor hidden_layer_sizes=(64, 32), relu, adam, early_stopping=True",
    "early_stopping_reason": "stopped_by_sklearn_early_stopping_or_max_iter",
    "epochs_or_iterations_completed": 56,
    "hidden_layer_sizes": [
      64,
      32
    ],
    "holdout_rows": 94765,
    "loss_observed": 1420.6094448157987,
    "max_iter": 70,
    "n_iter_observed": 56,
    "random_seed": 54,
    "sequence_model_status": "blocked_missing_torch_tensorflow_keras",
    "training_duration_seconds": 22.993,
    "training_rows": 247477,
    "validation_rows": 39864,
    "warnings": []
  }
}
```
