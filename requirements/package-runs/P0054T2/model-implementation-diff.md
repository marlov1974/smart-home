# P0054T2 LABB

Status: `PASS`

```json
{
  "implementation_difference": "P0054T selected fewer base families and its P0054N exact-origin rowset leaves no internal validation rows for W0/P0, forcing equal weights and zero horizon bias.",
  "p0054r_base_families": [
    "HGB",
    "ExtraTrees",
    "LightGBM",
    "XGBoost"
  ],
  "p0054r_horizon_bias": {
    "feature_count": 50,
    "holdout_or_prediction_rows": 52173,
    "method": "horizon_bias_correction",
    "model_artifact_persisted": false,
    "model_family": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "training_rows": 3310,
    "variant": "no_price"
  },
  "p0054r_weighting": "inverse MAE on populated internal validation",
  "p0054t_base_families": [
    "HGB",
    "LightGBM",
    "XGBoost"
  ],
  "p0054t_horizon_bias": {
    "applied_rows": 16102,
    "base_model_key": "WeightedEnsemble_P0_noPrice",
    "fit_data": "internal_validation_horizon_mean_bias_only",
    "holdout_used_for_fit": false,
    "horizon_bias_mw": {
      "1": 0.0,
      "10": 0.0,
      "11": 0.0,
      "12": 0.0,
      "13": 0.0,
      "14": 0.0,
      "15": 0.0,
      "16": 0.0,
      "17": 0.0,
      "18": 0.0,
      "19": 0.0,
      "2": 0.0,
      "20": 0.0,
      "21": 0.0,
      "22": 0.0,
      "23": 0.0,
      "24": 0.0,
      "25": 0.0,
      "26": 0.0,
      "27": 0.0,
      "28": 0.0,
      "29": 0.0,
      "3": 0.0,
      "30": 0.0,
      "31": 0.0,
      "32": 0.0,
      "33": 0.0,
      "34": 0.0,
      "35": 0.0,
      "36": 0.0,
      "4": 0.0,
      "5": 0.0,
      "6": 0.0,
      "7": 0.0,
      "8": 0.0,
      "9": 0.0
    }
  },
  "p0054t_weighting": {
    "holdout_used_for_weights": false,
    "internal_validation_start": "2025-03-01T00:00:00Z",
    "method": "inverse_internal_validation_mae",
    "model_mae": {},
    "selection_data": "internal_validation_only",
    "weights": {
      "HGB_P0_noPrice": 0.3333333333333333,
      "LightGBM_P0_noPrice": 0.3333333333333333,
      "XGBoost_P0_noPrice": 0.3333333333333333
    }
  }
}
```
