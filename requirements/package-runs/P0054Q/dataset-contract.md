# P0054Q LABB

Status: `PASS`

```json
{
  "advanced_price": {
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
          "duration_seconds": 21.028,
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
          "duration_seconds": 13.615,
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
          "duration_seconds": 18.059,
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
          "duration_seconds": 11.446,
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
          "duration_seconds": 17.857,
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
          "duration_seconds": 9.827,
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
          "duration_seconds": 15.04,
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
          "duration_seconds": 10.782,
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
  },
  "dataset_kind": "offline_labb_corrected_entsoe_target_experiment_not_deployable",
  "target": {
    "area": "SE3",
    "area_scope": "bidding_zone_internal_consumption_or_load",
    "duplicates": 0,
    "end": "2026-06-05T10:00:00Z",
    "holdout_source_rows": 8859,
    "mean_mw": 9491.743430604978,
    "median_mw": 9128.0,
    "nonfinite_values": 0,
    "ok": true,
    "old_physical_balance_target_used": false,
    "rows": 35125,
    "source_table": "entsoe_consumption_area_hourly_v1",
    "source_type": "actual_total_load",
    "start": "2022-06-01T00:00:00Z",
    "target_column": "consumption_mw",
    "target_field": "target_consumption_se3_mw",
    "train_fit_source_rows": 26266,
    "unit": "MW hourly mean",
    "usable_for_consumption_target": true
  },
  "weather": {
    "area_proxy": "se3_load_weather",
    "available": true,
    "end": "2026-05-30T21:00:00Z",
    "input_classification": "proxy",
    "proxy_label": "weather_actual_as_forecast_proxy",
    "rows": 35088,
    "start": "2022-05-29T22:00:00Z",
    "table": "weather_area_hourly"
  },
  "weather_proxy_label": "weather_actual_as_forecast_proxy"
}
```
