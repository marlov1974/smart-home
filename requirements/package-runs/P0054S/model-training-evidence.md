# P0054S LABB

Status: `PASS`

```json
{
  "DayAheadSpecialized_HGB": {
    "feature_count": 6,
    "method": "dayahead_specialized",
    "model_artifact_persisted": false,
    "model_family": "DayAheadSpecialized_HGB"
  },
  "ExtraTrees": {
    "duration_seconds": 20.806,
    "feature_count": 41,
    "holdout_rows": 59136,
    "hyperparameters": {
      "bootstrap": true,
      "max_features": 0.8,
      "max_samples": 0.8,
      "min_samples_leaf": 3,
      "n_estimators": 160,
      "n_jobs": -1,
      "random_state": 542
    },
    "internal_validation_rows": 14945,
    "model_artifact_persisted": false,
    "model_class": "ExtraTreesRegressor",
    "model_family": "ExtraTrees",
    "package": "scikit-learn",
    "train_rows": 182952
  },
  "HGB": {
    "duration_seconds": 11.259,
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
  },
  "HorizonBiasCorrected_WeightedEnsemble": {
    "feature_count": 4,
    "method": "horizon_bias_correction",
    "model_artifact_persisted": false,
    "model_family": "HorizonBiasCorrected_WeightedEnsemble"
  },
  "HorizonBucket_HGB": {
    "feature_count": 3,
    "method": "horizon_bucket_specialized",
    "model_artifact_persisted": false,
    "model_family": "HorizonBucket_HGB"
  },
  "LightGBM": {
    "duration_seconds": 14.138,
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
  },
  "LinearStack": {
    "feature_count": 5,
    "method": "linear_stack_internal_validation",
    "model_artifact_persisted": false,
    "model_family": "LinearStack"
  },
  "MedianEnsemble": {
    "feature_count": 1,
    "method": "median_completed_base_models",
    "model_artifact_persisted": false,
    "model_family": "MedianEnsemble"
  },
  "ResidualCorrection_LightGBM": {
    "feature_count": 5,
    "method": "residual_correction",
    "model_artifact_persisted": false,
    "model_family": "ResidualCorrection_LightGBM"
  },
  "WeightedEnsemble": {
    "feature_count": 4,
    "method": "inverse_internal_validation_mae",
    "model_artifact_persisted": false,
    "model_family": "WeightedEnsemble"
  },
  "XGBoost": {
    "duration_seconds": 10.73,
    "feature_count": 41,
    "holdout_rows": 59136,
    "hyperparameters": {
      "colsample_bytree": 0.85,
      "eval_metric": "mae",
      "learning_rate": 0.045,
      "max_depth": 6,
      "min_child_weight": 8,
      "n_estimators": 300,
      "n_jobs": -1,
      "objective": "reg:squarederror",
      "random_state": 542,
      "reg_lambda": 1.0,
      "subsample": 0.85,
      "tree_method": "hist"
    },
    "internal_validation_rows": 14945,
    "model_artifact_persisted": false,
    "model_class": "XGBRegressor",
    "model_family": "XGBoost",
    "package": "xgboost",
    "train_rows": 182952
  }
}
```
