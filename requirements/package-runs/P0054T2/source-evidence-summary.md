# P0054T2 LABB

Status: `PASS`

```json
{
  "p0054r_best_daily_energy": {
    "absolute_daily_energy_error_MWh": 4381.407120291999,
    "daily_energy_error_percent_of_actual": 1.9333789651384488,
    "day_count": 358,
    "model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "signed_daily_energy_error_MWh": 28.879972625696315
  },
  "p0054r_best_dayahead": {
    "MAE_percent_of_mean_actual": 2.6387829449358526,
    "hourly_MAE_delivery_day": 253.70062353819162,
    "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
  },
  "p0054r_best_full36": {
    "MAE_full_36h": 243.67666893537265,
    "MAE_percent_of_mean_actual": 2.500614436538169,
    "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
  },
  "p0054r_horizon_bias_training": {
    "feature_count": 50,
    "holdout_or_prediction_rows": 52173,
    "method": "horizon_bias_correction",
    "model_artifact_persisted": false,
    "model_family": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "training_rows": 3310,
    "variant": "no_price"
  },
  "p0054r_target": {
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
  "p0054t_price_contract": {
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
          "duration_seconds": 18.629,
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
          "duration_seconds": 10.751,
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
          "duration_seconds": 14.397,
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
          "duration_seconds": 9.976,
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
          "duration_seconds": 16.923,
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
          "duration_seconds": 9.714,
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
          "duration_seconds": 12.574,
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
          "duration_seconds": 8.918,
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
  "p0054t_target": {
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
  "p0054t_w0p0_m1": {
    "MAE_full_36h_max": 639.3018518489251,
    "MAE_full_36h_mean": 639.3018518489251,
    "MAE_full_36h_min": 639.3018518489251,
    "MAE_full_36h_std": 0.0,
    "absolute_daily_energy_error_MWh_max": 12819.954733521994,
    "absolute_daily_energy_error_MWh_mean": 12819.954733521994,
    "absolute_daily_energy_error_MWh_min": 12819.954733521994,
    "absolute_daily_energy_error_MWh_std": 0.0,
    "daily_energy_error_percent_of_actual_max": 5.245675157562151,
    "daily_energy_error_percent_of_actual_mean": 5.245675157562151,
    "daily_energy_error_percent_of_actual_min": 5.245675157562151,
    "daily_energy_error_percent_of_actual_std": 0.0,
    "hourly_MAE_delivery_day_max": 624.3881907571396,
    "hourly_MAE_delivery_day_mean": 624.3881907571396,
    "hourly_MAE_delivery_day_min": 624.3881907571396,
    "hourly_MAE_delivery_day_std": 0.0,
    "hourly_MAE_percent_of_mean_actual_max": 6.462887993090327,
    "hourly_MAE_percent_of_mean_actual_mean": 6.462887993090327,
    "hourly_MAE_percent_of_mean_actual_min": 6.462887993090327,
    "hourly_MAE_percent_of_mean_actual_std": 0.0,
    "model": "M1_HorizonBiasCorrectedWeightedEnsemble",
    "price_mode": "P0_noPrice",
    "seed_count": 1,
    "weather_mode": "W0_weatherProxy"
  },
  "p0054t_w0p0_m2": {
    "MAE_full_36h_max": 639.3018518489251,
    "MAE_full_36h_mean": 639.3018518489251,
    "MAE_full_36h_min": 639.3018518489251,
    "MAE_full_36h_std": 0.0,
    "absolute_daily_energy_error_MWh_max": 12819.954733521994,
    "absolute_daily_energy_error_MWh_mean": 12819.954733521994,
    "absolute_daily_energy_error_MWh_min": 12819.954733521994,
    "absolute_daily_energy_error_MWh_std": 0.0,
    "daily_energy_error_percent_of_actual_max": 5.245675157562151,
    "daily_energy_error_percent_of_actual_mean": 5.245675157562151,
    "daily_energy_error_percent_of_actual_min": 5.245675157562151,
    "daily_energy_error_percent_of_actual_std": 0.0,
    "hourly_MAE_delivery_day_max": 624.3881907571396,
    "hourly_MAE_delivery_day_mean": 624.3881907571396,
    "hourly_MAE_delivery_day_min": 624.3881907571396,
    "hourly_MAE_delivery_day_std": 0.0,
    "hourly_MAE_percent_of_mean_actual_max": 6.462887993090327,
    "hourly_MAE_percent_of_mean_actual_mean": 6.462887993090327,
    "hourly_MAE_percent_of_mean_actual_min": 6.462887993090327,
    "hourly_MAE_percent_of_mean_actual_std": 0.0,
    "model": "M2_WeightedEnsemble",
    "price_mode": "P0_noPrice",
    "seed_count": 1,
    "weather_mode": "W0_weatherProxy"
  },
  "p0054t_w0p0_training": {
    "base_model_keys": [
      "HGB_P0_noPrice",
      "LightGBM_P0_noPrice",
      "XGBoost_P0_noPrice"
    ],
    "duration_seconds": 6.222,
    "horizon_bias": {
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
    "label": "W0_weatherProxy__P0_noPrice",
    "prep": {
      "noise": {
        "applied": false
      },
      "price_mode": "P0_noPrice",
      "split_counts": {
        "holdout": 12792,
        "train_fit": 3310
      },
      "weather_mode": "W0_weatherProxy"
    },
    "price_mode": "P0_noPrice",
    "seed": null,
    "training": {
      "HGB_P0_noPrice": {
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
        "training_duration_seconds": 0.895,
        "training_rows": 3310,
        "variant": "P0_noPrice"
      },
      "LightGBM_P0_noPrice": {
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
        "training_duration_seconds": 1.915,
        "training_rows": 3310,
        "variant": "P0_noPrice"
      },
      "XGBoost_P0_noPrice": {
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
        "training_duration_seconds": 1.202,
        "training_rows": 3310,
        "variant": "P0_noPrice"
      }
    },
    "validation": {
      "HGB_P0_noPrice": {
        "MAE": null,
        "fallback": "equal_weights_and_zero_horizon_bias_inside_train_fit_only",
        "rows": 0,
        "selection_data": "unavailable_for_this_price_origin_coverage"
      },
      "LightGBM_P0_noPrice": {
        "MAE": null,
        "fallback": "equal_weights_and_zero_horizon_bias_inside_train_fit_only",
        "rows": 0,
        "selection_data": "unavailable_for_this_price_origin_coverage"
      },
      "XGBoost_P0_noPrice": {
        "MAE": null,
        "fallback": "equal_weights_and_zero_horizon_bias_inside_train_fit_only",
        "rows": 0,
        "selection_data": "unavailable_for_this_price_origin_coverage"
      }
    },
    "weather_mode": "W0_weatherProxy",
    "weights": {
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
}
```
