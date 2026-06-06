# P0054T4 LABB

Status: `WARN`

```json
{
  "base_models": {
    "ExtraTrees_no_price": {
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
      "training_duration_seconds": 3.762,
      "training_rows": 38985,
      "variant": "no_price"
    },
    "HGB_no_price": {
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
      "training_duration_seconds": 3.223,
      "training_rows": 38985,
      "variant": "no_price"
    },
    "LightGBM_no_price": {
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
      "training_duration_seconds": 6.206,
      "training_rows": 38985,
      "variant": "no_price"
    },
    "XGBoost_no_price": {
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
      "training_duration_seconds": 3.436,
      "training_rows": 38985,
      "variant": "no_price"
    }
  },
  "fit_protocol": "clean_train_fit_weather_only",
  "horizon_bias": {
    "applied_rows": 52173,
    "base_model_key": "WeightedEnsemble_no_price",
    "fit_data": "internal_validation_horizon_mean_bias_only",
    "holdout_used_for_fit": false,
    "horizon_bias_mw": {
      "1": -114.0845675877112,
      "10": -120.08602022539495,
      "11": -168.6924859848134,
      "12": -152.53499224570928,
      "13": -129.77833360007756,
      "14": -169.40136668061265,
      "15": -145.562111421671,
      "16": -118.29244673539563,
      "17": -121.42451798467178,
      "18": -114.91534112794979,
      "19": -21.520067330387086,
      "2": -67.19222754272243,
      "20": 61.52594632948614,
      "21": 14.938497372472709,
      "22": -30.68986141813721,
      "23": -63.0383643526182,
      "24": -83.1954972502007,
      "25": -100.16804168507834,
      "26": -55.00166540109542,
      "27": -10.434972584381967,
      "28": 30.922523675444697,
      "29": 38.716919256747296,
      "3": -20.546663178041094,
      "30": -101.79987554872368,
      "31": -114.67679161721325,
      "32": -70.61857454616084,
      "33": -81.78174113830954,
      "34": -97.03675915510311,
      "35": -146.52464173338313,
      "36": -112.17186072824816,
      "4": 23.785564391076495,
      "5": 32.4365349895547,
      "6": -111.82875284386571,
      "7": -127.3589482841536,
      "8": -87.30734018980985,
      "9": -95.40394334806636
    }
  },
  "model_reused_for_all_inference_noise_seeds": true,
  "validation": {
    "ExtraTrees_no_price": {
      "MAE": 313.08342263380865,
      "MAE_percent_of_mean_actual": 3.3694280041019016,
      "MAE_percent_of_median_actual": 3.4166358120129714,
      "R2": 0.9013398370506698,
      "RMSE": 393.4059902029519,
      "bias": -53.82098803458889,
      "mean_actual_mw": 9291.886404833836,
      "median_absolute_error": 268.193928039555,
      "median_actual_mw": 9163.5,
      "p90_absolute_error": 655.1196827431758,
      "p95_absolute_error": 764.5088586377989,
      "row_count": 3310,
      "sMAPE": 0.033840833593420654
    },
    "HGB_no_price": {
      "MAE": 292.8569732300242,
      "MAE_percent_of_mean_actual": 3.1517493915732095,
      "MAE_percent_of_median_actual": 3.1959073850605577,
      "R2": 0.9151795264124645,
      "RMSE": 364.7710814107889,
      "bias": -85.2009420792961,
      "mean_actual_mw": 9291.886404833836,
      "median_absolute_error": 251.6545638979137,
      "median_actual_mw": 9163.5,
      "p90_absolute_error": 595.2511760645954,
      "p95_absolute_error": 714.2055641343043,
      "row_count": 3310,
      "sMAPE": 0.03179144795831482
    },
    "LightGBM_no_price": {
      "MAE": 281.5606194933632,
      "MAE_percent_of_mean_actual": 3.030177159149184,
      "MAE_percent_of_median_actual": 3.0726318491118376,
      "R2": 0.922581391321291,
      "RMSE": 348.49193776348443,
      "bias": -83.71026886972444,
      "mean_actual_mw": 9291.886404833836,
      "median_absolute_error": 247.12888317215493,
      "median_actual_mw": 9163.5,
      "p90_absolute_error": 554.7271273644355,
      "p95_absolute_error": 665.0666101549864,
      "row_count": 3310,
      "sMAPE": 0.030636076439369605
    },
    "XGBoost_no_price": {
      "MAE": 280.5587719505287,
      "MAE_percent_of_mean_actual": 3.0193951984236063,
      "MAE_percent_of_median_actual": 3.0616988263275897,
      "R2": 0.9236355942028666,
      "RMSE": 346.11111195538496,
      "bias": -81.26108737726587,
      "mean_actual_mw": 9291.886404833836,
      "median_absolute_error": 242.89013671875,
      "median_actual_mw": 9163.5,
      "p90_absolute_error": 571.6795898437499,
      "p95_absolute_error": 671.4952636718749,
      "row_count": 3310,
      "sMAPE": 0.030447896992775194
    }
  },
  "weights": {
    "holdout_used_for_weights": false,
    "internal_validation_start": "2025-03-01T00:00:00Z",
    "method": "inverse_internal_validation_mae",
    "model_mae": {
      "ExtraTrees_no_price": 313.08342263380865,
      "HGB_no_price": 292.8569732300242,
      "LightGBM_no_price": 281.5606194933632,
      "XGBoost_no_price": 280.5587719505287
    },
    "selection_data": "internal_validation_only",
    "weights": {
      "ExtraTrees_no_price": 0.23272312870535253,
      "HGB_no_price": 0.24879637612006233,
      "LightGBM_no_price": 0.25877821192546985,
      "XGBoost_no_price": 0.25970228324911526
    }
  }
}
```
