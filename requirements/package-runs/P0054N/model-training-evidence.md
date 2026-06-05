# P0054N LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "feature_count": 60,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 0.597,
    "training_rows": 3313,
    "variant": "no_price"
  },
  "ExtraTrees_with_p0054n_exact_dayahead_advanced_price": {
    "feature_count": 68,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 0.676,
    "training_rows": 3313,
    "variant": "with_p0054n_exact_dayahead_advanced_price"
  },
  "HGB_no_price": {
    "feature_count": 60,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 0.949,
    "training_rows": 3313,
    "variant": "no_price"
  },
  "HGB_with_p0054n_exact_dayahead_advanced_price": {
    "feature_count": 68,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 1.265,
    "training_rows": 3313,
    "variant": "with_p0054n_exact_dayahead_advanced_price"
  },
  "LightGBM_no_price": {
    "feature_count": 60,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 1.906,
    "training_rows": 3313,
    "variant": "no_price"
  },
  "LightGBM_with_p0054n_exact_dayahead_advanced_price": {
    "feature_count": 68,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 1.942,
    "training_rows": 3313,
    "variant": "with_p0054n_exact_dayahead_advanced_price"
  },
  "XGBoost_no_price": {
    "feature_count": 60,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 1.227,
    "training_rows": 3313,
    "variant": "no_price"
  },
  "XGBoost_with_p0054n_exact_dayahead_advanced_price": {
    "feature_count": 68,
    "holdout_rows": 12874,
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
    "training_duration_seconds": 1.331,
    "training_rows": 3313,
    "variant": "with_p0054n_exact_dayahead_advanced_price"
  }
}
```
