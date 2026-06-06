# P0054T3 LABB

Status: `WARN`

```json
{
  "actual_future_spot_price_used": false,
  "base_skipped_windows": {
    "cross_split_path": 7,
    "incomplete_168h_path": 6,
    "pre_policy_origin": 3
  },
  "forecast_origins": 450,
  "holdout_model_status": {
    "model_status": {
      "ExtraTrees": {
        "duration_seconds": 18.969,
        "feature_count": 41,
        "hyperparameters": {
          "bootstrap": true,
          "max_features": 0.8,
          "max_samples": 0.8,
          "min_samples_leaf": 3,
          "n_estimators": 160,
          "n_jobs": -1,
          "random_state": 542
        },
        "predicted_rows": 12874,
        "status": "completed",
        "train_rows": 182952
      },
      "HGB": {
        "duration_seconds": 10.772,
        "feature_count": 41,
        "hyperparameters": {
          "learning_rate": 0.045,
          "max_iter": 180,
          "max_leaf_nodes": 31,
          "min_samples_leaf": 80,
          "random_state": 542
        },
        "predicted_rows": 12874,
        "status": "completed",
        "train_rows": 182952
      },
      "LightGBM": {
        "duration_seconds": 17.145,
        "feature_count": 41,
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
        "predicted_rows": 12874,
        "status": "completed",
        "train_rows": 182952
      },
      "XGBoost": {
        "duration_seconds": 10.286,
        "feature_count": 41,
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
        "predicted_rows": 12874,
        "status": "completed",
        "train_rows": 182952
      }
    },
    "ok": true,
    "protocol": "trainfit_price_before_2025_06",
    "rows": 12874
  },
  "holdout_rows": 12874,
  "matrix_review": {
    "all_lag_rolling_history_timestamps_strictly_before_origin": true,
    "feature_count": 41,
    "forbidden_feature_names": [],
    "no_production_flow_export_import_a61_features": true,
    "no_target_window_actual_price_used_as_input": true,
    "ok": true,
    "source_timestamp_error_count": 0,
    "source_timestamp_errors": []
  },
  "ok": true,
  "p0054l2_holdout_source_used_as_train_feature": false,
  "persisted": false,
  "protocol": "p0054n_exact_origin_blocked_train_plus_trainfit_holdout",
  "reason_for_package_local_extension": "P0054M/P0054L2 persisted logs have only 23:00Z origins; P0054N requires 12:00 Europe/Stockholm D-1.",
  "rows": 16187,
  "target_end": "2026-05-24T21:00:00Z",
  "target_start": "2025-03-01T00:00:00Z",
  "train_fit_rows": 3313,
  "train_model_status": {
    "model_status": {
      "ExtraTrees": {
        "duration_seconds": 16.375,
        "feature_count": 41,
        "hyperparameters": {
          "bootstrap": true,
          "max_features": 0.8,
          "max_samples": 0.8,
          "min_samples_leaf": 3,
          "n_estimators": 160,
          "n_jobs": -1,
          "random_state": 542
        },
        "predicted_rows": 3313,
        "status": "completed",
        "train_rows": 168007
      },
      "HGB": {
        "duration_seconds": 10.543,
        "feature_count": 41,
        "hyperparameters": {
          "learning_rate": 0.045,
          "max_iter": 180,
          "max_leaf_nodes": 31,
          "min_samples_leaf": 80,
          "random_state": 542
        },
        "predicted_rows": 3313,
        "status": "completed",
        "train_rows": 168007
      },
      "LightGBM": {
        "duration_seconds": 13.889,
        "feature_count": 41,
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
        "predicted_rows": 3313,
        "status": "completed",
        "train_rows": 168007
      },
      "XGBoost": {
        "duration_seconds": 9.346,
        "feature_count": 41,
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
        "predicted_rows": 3313,
        "status": "completed",
        "train_rows": 168007
      }
    },
    "ok": true,
    "protocol": "blocked_train_price_before_2025_03",
    "rows": 3313
  }
}
```
