# P0054O LABB

Status: `PASS`

```json
{
  "baseline": {
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
      "training_duration_seconds": 0.885,
      "training_rows": 3313,
      "variant": "no_price"
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
      "training_duration_seconds": 1.922,
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
      "training_duration_seconds": 1.929,
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
      "training_duration_seconds": 1.203,
      "training_rows": 3313,
      "variant": "no_price"
    }
  },
  "noisy_seed_runs": {
    "1000": {
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
        "training_duration_seconds": 0.887,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.922,
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
        "training_duration_seconds": 1.938,
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
        "training_duration_seconds": 1.205,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1001": {
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
        "training_duration_seconds": 0.884,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.896,
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
        "training_duration_seconds": 1.917,
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
        "training_duration_seconds": 1.211,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1002": {
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
        "training_duration_seconds": 0.89,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.935,
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
        "training_duration_seconds": 1.931,
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
        "training_duration_seconds": 1.206,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1003": {
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
        "training_duration_seconds": 0.882,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.927,
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
        "training_duration_seconds": 1.922,
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
        "training_duration_seconds": 1.205,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1004": {
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
        "training_duration_seconds": 0.887,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.927,
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
        "training_duration_seconds": 1.946,
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
        "training_duration_seconds": 1.212,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1005": {
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
        "training_duration_seconds": 0.881,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.933,
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
        "training_duration_seconds": 1.211,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1006": {
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
        "training_duration_seconds": 0.89,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.93,
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
        "training_duration_seconds": 1.947,
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
        "training_duration_seconds": 1.217,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1007": {
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
        "training_duration_seconds": 0.887,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.925,
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
        "training_duration_seconds": 1.21,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1008": {
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
        "training_duration_seconds": 0.877,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.802,
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
        "training_duration_seconds": 1.944,
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
        "training_duration_seconds": 1.213,
        "training_rows": 3313,
        "variant": "no_price"
      }
    },
    "1009": {
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
        "training_duration_seconds": 0.88,
        "training_rows": 3313,
        "variant": "no_price"
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
        "training_duration_seconds": 1.927,
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
        "training_duration_seconds": 1.949,
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
        "training_duration_seconds": 1.211,
        "training_rows": 3313,
        "variant": "no_price"
      }
    }
  }
}
```
