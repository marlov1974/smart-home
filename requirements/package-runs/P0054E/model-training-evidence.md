# P0054E LABB

```json
{
  "environment": {
    "imports": {
      "lightgbm": {
        "ok": true,
        "version": "4.6.0"
      },
      "xgboost": {
        "ok": true,
        "version": "2.1.4"
      }
    },
    "libomp": "libomp 22.1.7",
    "packages": {
      "lightgbm": "4.6.0",
      "numpy": "2.0.2",
      "scikit-learn": "1.6.1",
      "scipy": "1.13.1",
      "xgboost": "2.1.4"
    },
    "pip": "pip 21.2.4 from /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages/pip (python 3.9)",
    "python": {
      "base_prefix": "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9",
      "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
      "machine": "arm64",
      "platform": "macOS-26.4.1-arm64-arm-64bit",
      "prefix": "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9",
      "venv": false,
      "version": "3.9.6 (default, Apr 17 2026, 18:15:52)  [Clang 21.0.0 (clang-2100.1.1.101)]"
    }
  },
  "training": {
    "ExtraTrees_G4_se4_load_weather": {
      "feature_group": "G4_calendar_load_lags_rollups_weather_proxy",
      "holdout_rows": 94765,
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
      "model_name": "ExtraTrees_G4_se4_load_weather",
      "package": "scikit-learn",
      "random_seed": 54,
      "training_duration_seconds": 33.148,
      "training_rows": 247477,
      "validation_rows": 39864,
      "weather_proxy_name": "se4_load_weather"
    },
    "LightGBM_G4_se4_load_weather": {
      "feature_group": "G4_calendar_load_lags_rollups_weather_proxy",
      "holdout_rows": 94765,
      "hyperparameters": {
        "colsample_bytree": 0.85,
        "learning_rate": 0.045,
        "metric": "mae",
        "min_child_samples": 80,
        "n_estimators": 650,
        "n_jobs": -1,
        "num_leaves": 63,
        "objective": "regression_l1",
        "random_state": 54,
        "reg_lambda": 0.2,
        "subsample": 0.85,
        "subsample_freq": 1
      },
      "model_artifact_persisted": false,
      "model_class": "LGBMRegressor",
      "model_name": "LightGBM_G4_se4_load_weather",
      "package": "lightgbm",
      "random_seed": 54,
      "training_duration_seconds": 23.052,
      "training_rows": 247477,
      "validation_rows": 39864,
      "weather_proxy_name": "se4_load_weather"
    },
    "XGBoost_G4_se4_load_weather": {
      "feature_group": "G4_calendar_load_lags_rollups_weather_proxy",
      "holdout_rows": 94765,
      "hyperparameters": {
        "colsample_bytree": 0.85,
        "eval_metric": "mae",
        "learning_rate": 0.045,
        "max_depth": 7,
        "min_child_weight": 8,
        "n_estimators": 650,
        "n_jobs": -1,
        "objective": "reg:squarederror",
        "random_state": 54,
        "reg_lambda": 1.0,
        "subsample": 0.85,
        "tree_method": "hist"
      },
      "model_artifact_persisted": false,
      "model_class": "XGBRegressor",
      "model_name": "XGBoost_G4_se4_load_weather",
      "package": "xgboost",
      "random_seed": 54,
      "training_duration_seconds": 18.195,
      "training_rows": 247477,
      "validation_rows": 39864,
      "weather_proxy_name": "se4_load_weather"
    }
  }
}
```
