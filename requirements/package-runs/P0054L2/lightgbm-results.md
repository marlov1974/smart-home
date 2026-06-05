# P0054L2 LightGBM Results

```json
{
  "duration_seconds": 22.952,
  "leakage_status": "ok",
  "metrics": {
    "holdout": {
      "MAE": 0.314167187937004,
      "R2": 0.23517441859794974,
      "RMSE": 0.43277507232987955,
      "bias": -0.09306353323720254,
      "median_absolute_error": 0.2379098490042716,
      "p90_absolute_error": 0.6782765986320458,
      "p95_absolute_error": 0.843686481225074,
      "rows": 59136,
      "sMAPE": 0.6442731956776302
    },
    "internal_validation": {
      "MAE": 0.16935622636531758,
      "R2": 0.6317114136501079,
      "RMSE": 0.26634157407253645,
      "bias": -0.04395967434014703,
      "median_absolute_error": 0.1005422997175385,
      "p90_absolute_error": 0.41538992627263216,
      "p95_absolute_error": 0.5887603709690786,
      "rows": 14945,
      "sMAPE": 0.5535714756733872
    },
    "ranking_spike_ramp": {
      "bottom20_168h_precision": 0.38821022727272736,
      "forecast_price_spike_MAE": 0.6312678832455465,
      "high_price_regime_MAE": 1.2560090749537902,
      "large_price_ramp_MAE": 1.0755479879285652,
      "low_price_detection": {
        "f1": 0.14526315789473684,
        "fn": 3935,
        "fp": 125,
        "precision": 0.7340425531914894,
        "recall": 0.08060747663551401,
        "tp": 345
      },
      "low_price_regime_MAE": 0.28067823983160217,
      "ramp_detection": {
        "f1": 0.26321353065539116,
        "fn": 1208,
        "fp": 186,
        "precision": 0.5724137931034483,
        "recall": 0.17089910775566233,
        "tp": 249
      },
      "rows": 59136,
      "spearman": 0.5659957614834716,
      "spike_detection": {
        "f1": 0.056116722783389444,
        "fn": 1537,
        "fp": 145,
        "precision": 0.2564102564102564,
        "recall": 0.0315059861373661,
        "tp": 50
      },
      "top20_168h_precision": 0.3548295454545453
    },
    "weekly": {
      "MAE": 0.314167187937004,
      "MAE_full_168h": 0.314167187937004,
      "R2": 0.23517441859794974,
      "RMSE": 0.43277507232987955,
      "bias": -0.09306353323720254,
      "bias_full_168h": -0.09306353323720254,
      "complete_origins": 352,
      "median_absolute_error": 0.2379098490042716,
      "p90_absolute_error": 0.6782765986320458,
      "p90_full_path_absolute_error": 0.6782765986320458,
      "p95_absolute_error": 0.843686481225074,
      "p95_full_path_absolute_error": 0.843686481225074,
      "rows": 59136,
      "sMAPE": 0.6442731956776302
    }
  },
  "model_name": "LightGBM",
  "prediction_column": "predicted_price_lightgbm",
  "status": "completed",
  "training": {
    "duration_seconds": 22.486,
    "feature_count": 41,
    "holdout_rows": 59136,
    "hyperparameters": {
      "colsample_bytree": 0.85,
      "learning_rate": 0.045,
      "metric": "mae",
      "min_child_samples": 80,
      "n_estimators": 360,
      "n_jobs": -1,
      "num_leaves": 63,
      "objective": "regression_l1",
      "random_state": 542,
      "reg_lambda": 0.2,
      "subsample": 0.85
    },
    "internal_validation_rows": 14945,
    "model_artifact_persisted": false,
    "model_class": "LGBMRegressor",
    "model_family": "LightGBM",
    "package": "lightgbm",
    "train_rows": 182952
  }
}
```
