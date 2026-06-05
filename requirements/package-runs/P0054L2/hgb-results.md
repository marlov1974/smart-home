# P0054L2 HGB Results

```json
{
  "duration_seconds": 14.113,
  "leakage_status": "ok",
  "metrics": {
    "holdout": {
      "MAE": 0.3080417094017496,
      "R2": 0.2995623536403551,
      "RMSE": 0.41415773312261767,
      "bias": -0.05047513526064345,
      "median_absolute_error": 0.24314069010642814,
      "p90_absolute_error": 0.6310489826927381,
      "p95_absolute_error": 0.7864467294834849,
      "rows": 59136,
      "sMAPE": 0.62941235721831
    },
    "internal_validation": {
      "MAE": 0.25251963238007213,
      "R2": 0.426329548954267,
      "RMSE": 0.3324115247804503,
      "bias": 0.031352837236605494,
      "median_absolute_error": 0.20386091583532714,
      "p90_absolute_error": 0.5315916998921277,
      "p95_absolute_error": 0.6704948571098162,
      "rows": 14945,
      "sMAPE": 0.7084388958831924
    },
    "ranking_spike_ramp": {
      "bottom20_168h_precision": 0.3727272727272725,
      "forecast_price_spike_MAE": 1.0433500221509293,
      "high_price_regime_MAE": 1.155285036492779,
      "large_price_ramp_MAE": 1.0640628958440497,
      "low_price_detection": {
        "f1": 0.05575379125780553,
        "fn": 4155,
        "fp": 79,
        "precision": 0.6127450980392157,
        "recall": 0.029205607476635514,
        "tp": 125
      },
      "low_price_regime_MAE": 0.30369873084239213,
      "ramp_detection": {
        "f1": 0.24482951369480155,
        "fn": 1238,
        "fp": 113,
        "precision": 0.6596385542168675,
        "recall": 0.15030885380919698,
        "tp": 219
      },
      "rows": 59136,
      "spearman": 0.5984922425482891,
      "spike_detection": {
        "f1": 0.01086366105377512,
        "fn": 1577,
        "fp": 244,
        "precision": 0.03937007874015748,
        "recall": 0.00630119722747322,
        "tp": 10
      },
      "top20_168h_precision": 0.3963068181818187
    },
    "weekly": {
      "MAE": 0.3080417094017496,
      "MAE_full_168h": 0.3080417094017496,
      "R2": 0.2995623536403551,
      "RMSE": 0.41415773312261767,
      "bias": -0.05047513526064345,
      "bias_full_168h": -0.05047513526064345,
      "complete_origins": 352,
      "median_absolute_error": 0.24314069010642814,
      "p90_absolute_error": 0.6310489826927381,
      "p90_full_path_absolute_error": 0.6310489826927381,
      "p95_absolute_error": 0.7864467294834849,
      "p95_full_path_absolute_error": 0.7864467294834849,
      "rows": 59136,
      "sMAPE": 0.62941235721831
    }
  },
  "model_name": "HGB",
  "prediction_column": "predicted_price_hgb",
  "status": "completed",
  "training": {
    "duration_seconds": 13.696,
    "feature_count": 41,
    "holdout_rows": 59136,
    "hyperparameters": {
      "learning_rate": 0.045,
      "max_iter": 180,
      "max_leaf_nodes": 31,
      "min_samples_leaf": 80,
      "random_state": 542
    },
    "internal_validation_rows": 14945,
    "model_artifact_persisted": false,
    "model_class": "HistGradientBoostingRegressor",
    "model_family": "HGB",
    "package": "scikit-learn",
    "train_rows": 182952
  }
}
```
