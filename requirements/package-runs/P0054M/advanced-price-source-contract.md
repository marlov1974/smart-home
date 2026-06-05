# P0054M LABB

Status: `PASS`

```json
{
  "combined_rows": 74081,
  "holdout_rows": 59136,
  "holdout_source": {
    "forecast_origins": 352,
    "holdout_rows": 59136,
    "holdout_used_for_consumption_training": false,
    "model_name": "Ensemble",
    "ok": true,
    "rows": 59136,
    "table": "advanced_spotprice_forecast_log_p0054l2_se3_v1",
    "target_end": "2026-05-25T22:00:00Z",
    "target_start": "2025-06-01T23:00:00Z",
    "train_fit_rows": 0
  },
  "ok": true,
  "p0054l2_holdout_source_used_as_train_feature": false,
  "price_feature_protocol": "rolling_oof_train_plus_holdout",
  "train_fit_holdout_source_separated": true,
  "train_fit_rows": 14945,
  "train_source": {
    "coverage_warning": "train-side advanced price coverage is limited to 2025-03-01..2025-05-31",
    "forecast_origins": 92,
    "holdout_used_for_train_price_features": false,
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
    "model_status": {
      "ExtraTrees": {
        "duration_seconds": 16.991,
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
        "predicted_rows": 14945,
        "status": "completed",
        "train_rows": 168007
      },
      "HGB": {
        "duration_seconds": 9.929,
        "feature_count": 41,
        "hyperparameters": {
          "learning_rate": 0.045,
          "max_iter": 180,
          "max_leaf_nodes": 31,
          "min_samples_leaf": 80,
          "random_state": 542
        },
        "predicted_rows": 14945,
        "status": "completed",
        "train_rows": 168007
      },
      "LightGBM": {
        "duration_seconds": 16.145,
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
        "predicted_rows": 14945,
        "status": "completed",
        "train_rows": 168007
      },
      "XGBoost": {
        "duration_seconds": 9.496,
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
        "predicted_rows": 14945,
        "status": "completed",
        "train_rows": 168007
      }
    },
    "ok": true,
    "protocol": "rolling_oof_train_plus_holdout",
    "rows": 14945,
    "skipped_windows": {
      "cross_split_path": 7,
      "incomplete_168h_path": 6,
      "pre_policy_origin": 3
    },
    "table": "advanced_spotprice_forecast_log_p0054m_se3_train_blocked_oof_v1",
    "target_end": "2025-05-31T22:00:00Z",
    "target_rows_predicted": 14945,
    "target_start": "2025-03-01T00:00:00Z",
    "train_price_model_rows": 168007,
    "training_cutoff_utc": "2025-02-28T23:00:00Z"
  }
}
```
