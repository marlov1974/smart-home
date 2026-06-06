# P0054R Model Checkpoints

No model binaries are persisted. Checkpoints are compact evidence records only.

```json
[
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "HGB_no_price",
    "status": "baseline_reproduced",
    "training": {
      "feature_count": 68,
      "holdout_rows": 13188,
      "hyperparameters": {
        "learning_rate": 0.055,
        "max_iter": 120,
        "max_leaf_nodes": 31,
        "min_samples_leaf": 80,
        "random_state": 54
      },
      "model_artifact_persisted": false,
      "model_class": "HistGradientBoostingRegressor",
      "model_family": "HGB",
      "package": "scikit-learn",
      "training_duration_seconds": 2.88,
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "ExtraTrees_no_price",
    "status": "baseline_reproduced",
    "training": {
      "feature_count": 68,
      "holdout_rows": 13188,
      "hyperparameters": {
        "bootstrap": true,
        "max_features": 0.75,
        "max_samples": 0.8,
        "min_samples_leaf": 4,
        "n_estimators": 180,
        "n_jobs": -1,
        "random_state": 54
      },
      "model_artifact_persisted": false,
      "model_class": "ExtraTreesRegressor",
      "model_family": "ExtraTrees",
      "package": "scikit-learn",
      "training_duration_seconds": 3.786,
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "LightGBM_no_price",
    "status": "baseline_reproduced",
    "training": {
      "feature_count": 68,
      "holdout_rows": 13188,
      "hyperparameters": {
        "colsample_bytree": 0.85,
        "learning_rate": 0.05,
        "metric": "mae",
        "min_child_samples": 80,
        "n_estimators": 450,
        "n_jobs": -1,
        "num_leaves": 63,
        "objective": "regression_l1",
        "random_state": 54,
        "reg_lambda": 0.2,
        "subsample": 0.85
      },
      "model_artifact_persisted": false,
      "model_class": "LGBMRegressor",
      "model_family": "LightGBM",
      "package": "lightgbm",
      "training_duration_seconds": 6.184,
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "XGBoost_no_price",
    "status": "baseline_reproduced",
    "training": {
      "feature_count": 68,
      "holdout_rows": 13188,
      "hyperparameters": {
        "colsample_bytree": 0.85,
        "eval_metric": "mae",
        "learning_rate": 0.05,
        "max_depth": 7,
        "min_child_weight": 8,
        "n_estimators": 450,
        "n_jobs": -1,
        "objective": "reg:squarederror",
        "random_state": 54,
        "reg_lambda": 1.0,
        "subsample": 0.85,
        "tree_method": "hist"
      },
      "model_artifact_persisted": false,
      "model_class": "XGBRegressor",
      "model_family": "XGBoost",
      "package": "xgboost",
      "training_duration_seconds": 3.416,
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "WeightedEnsemble_no_price",
    "status": "advanced_completed",
    "training": {
      "feature_count": 50,
      "holdout_or_prediction_rows": 52173,
      "method": "inverse_mae_weighted_ensemble",
      "model_artifact_persisted": false,
      "model_family": "WeightedEnsemble_no_price",
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "MedianEnsemble_no_price",
    "status": "advanced_completed",
    "training": {
      "feature_count": 50,
      "holdout_or_prediction_rows": 52173,
      "method": "median_ensemble",
      "model_artifact_persisted": false,
      "model_family": "MedianEnsemble_no_price",
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "ResidualCorrection_XGBoost_no_price",
    "status": "advanced_completed",
    "training": {
      "feature_count": 50,
      "holdout_or_prediction_rows": 52173,
      "method": "residual_correction",
      "model_artifact_persisted": false,
      "model_family": "ResidualCorrection_XGBoost_no_price",
      "training_rows": 3310,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "HorizonSpecialized_HGB_no_price",
    "status": "advanced_completed",
    "training": {
      "feature_count": 50,
      "holdout_or_prediction_rows": 52173,
      "method": "horizon_specialized",
      "model_artifact_persisted": false,
      "model_family": "HorizonSpecialized_HGB_no_price",
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "status": "advanced_completed",
    "training": {
      "feature_count": 50,
      "holdout_or_prediction_rows": 52173,
      "method": "horizon_bias_correction",
      "model_artifact_persisted": false,
      "model_family": "HorizonBiasCorrected_WeightedEnsemble_no_price",
      "training_rows": 3310,
      "variant": "no_price"
    }
  },
  {
    "checkpoint_kind": "metrics_and_evidence_only_no_model_binary",
    "model_key": "DayAheadSpecialized_HGB_no_price",
    "status": "advanced_completed",
    "training": {
      "feature_count": 50,
      "holdout_or_prediction_rows": 8592,
      "method": "dayahead_specialized",
      "model_artifact_persisted": false,
      "model_family": "DayAheadSpecialized_HGB_no_price",
      "training_rows": 25032,
      "variant": "no_price"
    }
  }
]
```
