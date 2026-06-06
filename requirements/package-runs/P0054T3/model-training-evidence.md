# P0054T3 LABB

Status: `WARN`

```json
{
  "W0_weatherProxy__P0_noPrice_fullCoverage": {
    "ExtraTrees_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.67,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "HGB_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 2.973,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "LightGBM_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 6.262,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "XGBoost_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.424,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    }
  },
  "W0_weatherProxy__P0_noPrice_matchedPriceCoverage": {
    "ExtraTrees_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.613,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "HGB_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.056,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "LightGBM_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.655,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "XGBoost_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.213,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    }
  },
  "W0_weatherProxy__P1_p0054l2Price_matchedCoverage": {
    "ExtraTrees_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.68,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "HGB_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.952,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "LightGBM_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.937,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "XGBoost_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.316,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    }
  },
  "W1_tempNoise2C_seed1000__P0_noPrice_fullCoverage": {
    "ExtraTrees_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.738,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "HGB_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 2.907,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "LightGBM_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 6.228,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "XGBoost_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.468,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    }
  },
  "W1_tempNoise2C_seed1000__P0_noPrice_matchedPriceCoverage": {
    "ExtraTrees_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.594,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "HGB_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.878,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "LightGBM_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.89,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "XGBoost_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.216,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    }
  },
  "W1_tempNoise2C_seed1000__P1_p0054l2Price_matchedCoverage": {
    "ExtraTrees_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.677,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "HGB_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.953,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "LightGBM_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.947,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "XGBoost_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.319,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    }
  },
  "W1_tempNoise2C_seed1001__P0_noPrice_fullCoverage": {
    "ExtraTrees_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.75,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "HGB_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 2.948,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "LightGBM_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 6.213,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "XGBoost_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.473,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    }
  },
  "W1_tempNoise2C_seed1001__P0_noPrice_matchedPriceCoverage": {
    "ExtraTrees_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.604,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "HGB_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.9,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "LightGBM_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.883,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "XGBoost_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.219,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    }
  },
  "W1_tempNoise2C_seed1001__P1_p0054l2Price_matchedCoverage": {
    "ExtraTrees_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.662,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "HGB_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.952,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "LightGBM_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.96,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "XGBoost_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.324,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    }
  },
  "W1_tempNoise2C_seed1002__P0_noPrice_fullCoverage": {
    "ExtraTrees_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.792,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "HGB_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.154,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "LightGBM_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 6.244,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "XGBoost_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.466,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    }
  },
  "W1_tempNoise2C_seed1002__P0_noPrice_matchedPriceCoverage": {
    "ExtraTrees_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.586,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "HGB_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.878,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "LightGBM_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.87,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "XGBoost_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.209,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    }
  },
  "W1_tempNoise2C_seed1002__P1_p0054l2Price_matchedCoverage": {
    "ExtraTrees_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.651,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "HGB_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.948,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "LightGBM_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.948,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "XGBoost_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.314,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    }
  },
  "W1_tempNoise2C_seed1003__P0_noPrice_fullCoverage": {
    "ExtraTrees_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.789,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "HGB_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 2.918,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "LightGBM_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 6.251,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "XGBoost_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.468,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    }
  },
  "W1_tempNoise2C_seed1003__P0_noPrice_matchedPriceCoverage": {
    "ExtraTrees_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.609,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "HGB_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.871,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "LightGBM_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.872,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "XGBoost_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.216,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    }
  },
  "W1_tempNoise2C_seed1003__P1_p0054l2Price_matchedCoverage": {
    "ExtraTrees_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.687,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "HGB_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.957,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "LightGBM_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.964,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "XGBoost_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.326,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    }
  },
  "W1_tempNoise2C_seed1004__P0_noPrice_fullCoverage": {
    "ExtraTrees_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.76,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "HGB_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 2.97,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "LightGBM_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 6.233,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    },
    "XGBoost_P0_noPrice_fullCoverage": {
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
      "training_duration_seconds": 3.464,
      "training_rows": 38985,
      "variant": "P0_noPrice_fullCoverage"
    }
  },
  "W1_tempNoise2C_seed1004__P0_noPrice_matchedPriceCoverage": {
    "ExtraTrees_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.576,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "HGB_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.884,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "LightGBM_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.868,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    },
    "XGBoost_P0_noPrice_matchedPriceCoverage": {
      "feature_count": 60,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.211,
      "training_rows": 3310,
      "variant": "P0_noPrice_matchedPriceCoverage"
    }
  },
  "W1_tempNoise2C_seed1004__P1_p0054l2Price_matchedCoverage": {
    "ExtraTrees_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.661,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "HGB_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 0.973,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "LightGBM_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.949,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    },
    "XGBoost_P1_p0054l2Price_matchedCoverage": {
      "feature_count": 68,
      "holdout_rows": 12792,
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
      "training_duration_seconds": 1.325,
      "training_rows": 3310,
      "variant": "P1_p0054l2Price_matchedCoverage"
    }
  }
}
```
