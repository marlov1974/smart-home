# P0054L2 Ensemble Checkpoint

Status: `completed`

```json
{
  "leakage_status": "ok",
  "metrics": {
    "holdout": {
      "MAE": 0.3033978235888772,
      "R2": 0.3078524372214625,
      "RMSE": 0.4116995401036644,
      "bias": -0.06047327557645194,
      "median_absolute_error": 0.23795538678655626,
      "p90_absolute_error": 0.6299626381452149,
      "p95_absolute_error": 0.7861617221535853,
      "rows": 59136,
      "sMAPE": 0.6198473887058029
    },
    "ranking_spike_ramp": {
      "bottom20_168h_precision": 0.408522727272727,
      "forecast_price_spike_MAE": 0.9751497079305887,
      "high_price_regime_MAE": 1.1991714559732758,
      "large_price_ramp_MAE": 1.0618789171235719,
      "low_price_detection": {
        "f1": 0.05054151624548737,
        "fn": 4168,
        "fp": 40,
        "precision": 0.7368421052631579,
        "recall": 0.026168224299065422,
        "tp": 112
      },
      "low_price_regime_MAE": 0.29742715955810123,
      "ramp_detection": {
        "f1": 0.23862375138734737,
        "fn": 1242,
        "fp": 130,
        "precision": 0.6231884057971014,
        "recall": 0.14756348661633492,
        "tp": 215
      },
      "rows": 59136,
      "spearman": 0.6116733985652962,
      "spike_detection": {
        "f1": 0.003482298316889147,
        "fn": 1584,
        "fp": 133,
        "precision": 0.022058823529411766,
        "recall": 0.001890359168241966,
        "tp": 3
      },
      "top20_168h_precision": 0.39786931818181837
    },
    "weekly": {
      "MAE": 0.3033978235888772,
      "MAE_full_168h": 0.3033978235888772,
      "R2": 0.3078524372214625,
      "RMSE": 0.4116995401036644,
      "bias": -0.06047327557645194,
      "bias_full_168h": -0.06047327557645194,
      "complete_origins": 352,
      "median_absolute_error": 0.23795538678655626,
      "p90_absolute_error": 0.6299626381452149,
      "p90_full_path_absolute_error": 0.6299626381452149,
      "p95_absolute_error": 0.7861617221535853,
      "p95_full_path_absolute_error": 0.7861617221535853,
      "rows": 59136,
      "sMAPE": 0.6198473887058029
    }
  },
  "model_name": "Ensemble",
  "training": {
    "feature_count": 4,
    "holdout_rows": 59136,
    "hyperparameters": {
      "method": "simple mean of completed model predictions",
      "source_models": [
        "HGB",
        "ExtraTrees",
        "LightGBM",
        "XGBoost"
      ]
    },
    "internal_validation_rows": 0,
    "model_artifact_persisted": false,
    "model_family": "Ensemble",
    "train_rows": 0
  }
}
```
