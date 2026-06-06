# P0054V2 LABB

Status: `PASS`

```json
{
  "no_actual_future_spot_price_used_for_holdout_features": true,
  "no_holdout_data_for_price_model_fitting": true,
  "ok": true,
  "source": {
    "actual_future_spot_price_used": false,
    "holdout_used_for_price_model_fitting": false,
    "missing_examples": [],
    "missing_required_holdout_rows": 0,
    "model_status": {
      "model_status": {
        "ExtraTrees": {
          "duration_seconds": 3.434,
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
          "predicted_rows": 13188,
          "status": "completed",
          "train_rows": 38985
        },
        "HGB": {
          "duration_seconds": 3.387,
          "feature_count": 41,
          "hyperparameters": {
            "learning_rate": 0.045,
            "max_iter": 180,
            "max_leaf_nodes": 31,
            "min_samples_leaf": 80,
            "random_state": 542
          },
          "predicted_rows": 13188,
          "status": "completed",
          "train_rows": 38985
        },
        "LightGBM": {
          "duration_seconds": 5.284,
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
          "predicted_rows": 13188,
          "status": "completed",
          "train_rows": 38985
        },
        "XGBoost": {
          "duration_seconds": 2.556,
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
          "predicted_rows": 13188,
          "status": "completed",
          "train_rows": 38985
        }
      },
      "ok": true,
      "protocol": "p0054v2_trainfit_price_before_2025_06_predict_holdout",
      "rows": 13188
    },
    "ok": true,
    "persisted_table": null,
    "predict_examples": 13188,
    "price_model_family": "P0054N/P0054L2-compatible ensemble",
    "price_model_package_source": "P0054V2 using P0054L2 feature code and P0054N fit_price_ensemble",
    "protocol": "P0054V2_P0054L2_like_trainfit_safe_price_model_for_holdout_future_horizons",
    "required_holdout_rows": 13188,
    "rows": 13188,
    "train_examples": 38985
  }
}
```
