# P0054L2 Model Training Evidence

```json
{
  "Ensemble": {
    "leakage_status": "ok",
    "metrics": {
      "holdout": {
        "MAE": 0.3033978235888772,
        "R2": 0.3078524372214625,
        "RMSE": 0.4116995401036644,
        "bias": -0.06047327557645194,
        "median_absolute_error": 0.23795538678655626,
        "p90_absolute_error": 0.6299626381452149,
        "p95_absolute_error": 0.7861617221535853,
        "rows": 59136,
        "sMAPE": 0.6198473887058029
      },
      "ranking_spike_ramp": {
        "bottom20_168h_precision": 0.408522727272727,
        "forecast_price_spike_MAE": 0.9751497079305887,
        "high_price_regime_MAE": 1.1991714559732758,
        "large_price_ramp_MAE": 1.0618789171235719,
        "low_price_detection": {
          "f1": 0.05054151624548737,
          "fn": 4168,
          "fp": 40,
          "precision": 0.7368421052631579,
          "recall": 0.026168224299065422,
          "tp": 112
        },
        "low_price_regime_MAE": 0.29742715955810123,
        "ramp_detection": {
          "f1": 0.23862375138734737,
          "fn": 1242,
          "fp": 130,
          "precision": 0.6231884057971014,
          "recall": 0.14756348661633492,
          "tp": 215
        },
        "rows": 59136,
        "spearman": 0.6116733985652962,
        "spike_detection": {
          "f1": 0.003482298316889147,
          "fn": 1584,
          "fp": 133,
          "precision": 0.022058823529411766,
          "recall": 0.001890359168241966,
          "tp": 3
        },
        "top20_168h_precision": 0.39786931818181837
      },
      "weekly": {
        "MAE": 0.3033978235888772,
        "MAE_full_168h": 0.3033978235888772,
        "R2": 0.3078524372214625,
        "RMSE": 0.4116995401036644,
        "bias": -0.06047327557645194,
        "bias_full_168h": -0.06047327557645194,
        "complete_origins": 352,
        "median_absolute_error": 0.23795538678655626,
        "p90_absolute_error": 0.6299626381452149,
        "p90_full_path_absolute_error": 0.6299626381452149,
        "p95_absolute_error": 0.7861617221535853,
        "p95_full_path_absolute_error": 0.7861617221535853,
        "rows": 59136,
        "sMAPE": 0.6198473887058029
      }
    },
    "model_name": "Ensemble",
    "prediction_column": "predicted_price_ensemble",
    "status": "completed",
    "training": {
      "feature_count": 4,
      "holdout_rows": 59136,
      "hyperparameters": {
        "method": "simple mean of completed model predictions",
        "source_models": [
          "HGB",
          "ExtraTrees",
          "LightGBM",
          "XGBoost"
        ]
      },
      "internal_validation_rows": 0,
      "model_artifact_persisted": false,
      "model_family": "Ensemble",
      "train_rows": 0
    }
  },
  "ExtraTrees": {
    "duration_seconds": 22.808,
    "leakage_status": "ok",
    "metrics": {
      "holdout": {
        "MAE": 0.307732434030351,
        "R2": 0.300968778922162,
        "RMSE": 0.41374172564624745,
        "bias": -0.03306049393721666,
        "median_absolute_error": 0.24508564669096927,
        "p90_absolute_error": 0.6259841746196657,
        "p95_absolute_error": 0.7873063850273405,
        "rows": 59136,
        "sMAPE": 0.6187374247632932
      },
      "internal_validation": {
        "MAE": 0.08426444464056111,
        "R2": 0.9091533993848913,
        "RMSE": 0.13228151882224365,
        "bias": 0.0007661300427341327,
        "median_absolute_error": 0.05165388407668714,
        "p90_absolute_error": 0.20135823890407253,
        "p95_absolute_error": 0.2833377621639741,
        "rows": 14945,
        "sMAPE": 0.3822702004614344
      },
      "ranking_spike_ramp": {
        "bottom20_168h_precision": 0.4025568181818182,
        "forecast_price_spike_MAE": 0.88334027142338,
        "high_price_regime_MAE": 1.2009788014892446,
        "large_price_ramp_MAE": 1.08593115809146,
        "low_price_detection": {
          "f1": 0.025252525252525252,
          "fn": 4225,
          "fp": 21,
          "precision": 0.7236842105263158,
          "recall": 0.012850467289719626,
          "tp": 55
        },
        "low_price_regime_MAE": 0.33138767897769583,
        "ramp_detection": {
          "f1": 0.22886133032694478,
          "fn": 1254,
          "fp": 114,
          "precision": 0.6403785488958991,
          "recall": 0.1393273850377488,
          "tp": 203
        },
        "rows": 59136,
        "spearman": 0.5983748935964608,
        "spike_detection": {
          "f1": 0.009044657998869417,
          "fn": 1579,
          "fp": 174,
          "precision": 0.04395604395604396,
          "recall": 0.005040957781978576,
          "tp": 8
        },
        "top20_168h_precision": 0.37059659090909103
      },
      "weekly": {
        "MAE": 0.307732434030351,
        "MAE_full_168h": 0.307732434030351,
        "R2": 0.300968778922162,
        "RMSE": 0.41374172564624745,
        "bias": -0.03306049393721666,
        "bias_full_168h": -0.03306049393721666,
        "complete_origins": 352,
        "median_absolute_error": 0.24508564669096927,
        "p90_absolute_error": 0.6259841746196657,
        "p90_full_path_absolute_error": 0.6259841746196657,
        "p95_absolute_error": 0.7873063850273405,
        "p95_full_path_absolute_error": 0.7873063850273405,
        "rows": 59136,
        "sMAPE": 0.6187374247632932
      }
    },
    "model_name": "ExtraTrees",
    "prediction_column": "predicted_price_extratrees",
    "status": "completed",
    "training": {
      "duration_seconds": 22.337,
      "feature_count": 41,
      "holdout_rows": 59136,
      "hyperparameters": {
        "bootstrap": true,
        "max_features": 0.8,
        "max_samples": 0.8,
        "min_samples_leaf": 3,
        "n_estimators": 160,
        "n_jobs": -1,
        "random_state": 542
      },
      "internal_validation_rows": 14945,
      "model_artifact_persisted": false,
      "model_class": "ExtraTreesRegressor",
      "model_family": "ExtraTrees",
      "package": "scikit-learn",
      "train_rows": 182952
    }
  },
  "HGB": {
    "duration_seconds": 14.113,
    "leakage_status": "ok",
    "metrics": {
      "holdout": {
        "MAE": 0.3080417094017496,
        "R2": 0.2995623536403551,
        "RMSE": 0.41415773312261767,
        "bias": -0.05047513526064345,
        "median_absolute_error": 0.24314069010642814,
        "p90_absolute_error": 0.6310489826927381,
        "p95_absolute_error": 0.7864467294834849,
        "rows": 59136,
        "sMAPE": 0.62941235721831
      },
      "internal_validation": {
        "MAE": 0.25251963238007213,
        "R2": 0.426329548954267,
        "RMSE": 0.3324115247804503,
        "bias": 0.031352837236605494,
        "median_absolute_error": 0.20386091583532714,
        "p90_absolute_error": 0.5315916998921277,
        "p95_absolute_error": 0.6704948571098162,
        "rows": 14945,
        "sMAPE": 0.7084388958831924
      },
      "ranking_spike_ramp": {
        "bottom20_168h_precision": 0.3727272727272725,
        "forecast_price_spike_MAE": 1.0433500221509293,
        "high_price_regime_MAE": 1.155285036492779,
        "large_price_ramp_MAE": 1.0640628958440497,
        "low_price_detection": {
          "f1": 0.05575379125780553,
          "fn": 4155,
          "fp": 79,
          "precision": 0.6127450980392157,
          "recall": 0.029205607476635514,
          "tp": 125
        },
        "low_price_regime_MAE": 0.30369873084239213,
        "ramp_detection": {
          "f1": 0.24482951369480155,
          "fn": 1238,
          "fp": 113,
          "precision": 0.6596385542168675,
          "recall": 0.15030885380919698,
          "tp": 219
        },
        "rows": 59136,
        "spearman": 0.5984922425482891,
        "spike_detection": {
          "f1": 0.01086366105377512,
          "fn": 1577,
          "fp": 244,
          "precision": 0.03937007874015748,
          "recall": 0.00630119722747322,
          "tp": 10
        },
        "top20_168h_precision": 0.3963068181818187
      },
      "weekly": {
        "MAE": 0.3080417094017496,
        "MAE_full_168h": 0.3080417094017496,
        "R2": 0.2995623536403551,
        "RMSE": 0.41415773312261767,
        "bias": -0.05047513526064345,
        "bias_full_168h": -0.05047513526064345,
        "complete_origins": 352,
        "median_absolute_error": 0.24314069010642814,
        "p90_absolute_error": 0.6310489826927381,
        "p90_full_path_absolute_error": 0.6310489826927381,
        "p95_absolute_error": 0.7864467294834849,
        "p95_full_path_absolute_error": 0.7864467294834849,
        "rows": 59136,
        "sMAPE": 0.62941235721831
      }
    },
    "model_name": "HGB",
    "prediction_column": "predicted_price_hgb",
    "status": "completed",
    "training": {
      "duration_seconds": 13.696,
      "feature_count": 41,
      "holdout_rows": 59136,
      "hyperparameters": {
        "learning_rate": 0.045,
        "max_iter": 180,
        "max_leaf_nodes": 31,
        "min_samples_leaf": 80,
        "random_state": 542
      },
      "internal_validation_rows": 14945,
      "model_artifact_persisted": false,
      "model_class": "HistGradientBoostingRegressor",
      "model_family": "HGB",
      "package": "scikit-learn",
      "train_rows": 182952
    }
  },
  "LightGBM": {
    "duration_seconds": 22.952,
    "leakage_status": "ok",
    "metrics": {
      "holdout": {
        "MAE": 0.314167187937004,
        "R2": 0.23517441859794974,
        "RMSE": 0.43277507232987955,
        "bias": -0.09306353323720254,
        "median_absolute_error": 0.2379098490042716,
        "p90_absolute_error": 0.6782765986320458,
        "p95_absolute_error": 0.843686481225074,
        "rows": 59136,
        "sMAPE": 0.6442731956776302
      },
      "internal_validation": {
        "MAE": 0.16935622636531758,
        "R2": 0.6317114136501079,
        "RMSE": 0.26634157407253645,
        "bias": -0.04395967434014703,
        "median_absolute_error": 0.1005422997175385,
        "p90_absolute_error": 0.41538992627263216,
        "p95_absolute_error": 0.5887603709690786,
        "rows": 14945,
        "sMAPE": 0.5535714756733872
      },
      "ranking_spike_ramp": {
        "bottom20_168h_precision": 0.38821022727272736,
        "forecast_price_spike_MAE": 0.6312678832455465,
        "high_price_regime_MAE": 1.2560090749537902,
        "large_price_ramp_MAE": 1.0755479879285652,
        "low_price_detection": {
          "f1": 0.14526315789473684,
          "fn": 3935,
          "fp": 125,
          "precision": 0.7340425531914894,
          "recall": 0.08060747663551401,
          "tp": 345
        },
        "low_price_regime_MAE": 0.28067823983160217,
        "ramp_detection": {
          "f1": 0.26321353065539116,
          "fn": 1208,
          "fp": 186,
          "precision": 0.5724137931034483,
          "recall": 0.17089910775566233,
          "tp": 249
        },
        "rows": 59136,
        "spearman": 0.5659957614834716,
        "spike_detection": {
          "f1": 0.056116722783389444,
          "fn": 1537,
          "fp": 145,
          "precision": 0.2564102564102564,
          "recall": 0.0315059861373661,
          "tp": 50
        },
        "top20_168h_precision": 0.3548295454545453
      },
      "weekly": {
        "MAE": 0.314167187937004,
        "MAE_full_168h": 0.314167187937004,
        "R2": 0.23517441859794974,
        "RMSE": 0.43277507232987955,
        "bias": -0.09306353323720254,
        "bias_full_168h": -0.09306353323720254,
        "complete_origins": 352,
        "median_absolute_error": 0.2379098490042716,
        "p90_absolute_error": 0.6782765986320458,
        "p90_full_path_absolute_error": 0.6782765986320458,
        "p95_absolute_error": 0.843686481225074,
        "p95_full_path_absolute_error": 0.843686481225074,
        "rows": 59136,
        "sMAPE": 0.6442731956776302
      }
    },
    "model_name": "LightGBM",
    "prediction_column": "predicted_price_lightgbm",
    "status": "completed",
    "training": {
      "duration_seconds": 22.486,
      "feature_count": 41,
      "holdout_rows": 59136,
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
      "internal_validation_rows": 14945,
      "model_artifact_persisted": false,
      "model_class": "LGBMRegressor",
      "model_family": "LightGBM",
      "package": "lightgbm",
      "train_rows": 182952
    }
  },
  "XGBoost": {
    "duration_seconds": 15.933,
    "leakage_status": "ok",
    "metrics": {
      "holdout": {
        "MAE": 0.3129010449295325,
        "R2": 0.2705884515379823,
        "RMSE": 0.42263684180990596,
        "bias": -0.06529393987074708,
        "median_absolute_error": 0.2417662058734893,
        "p90_absolute_error": 0.6558563129472733,
        "p95_absolute_error": 0.8104093101787566,
        "rows": 59136,
        "sMAPE": 0.6396201100103697
      },
      "internal_validation": {
        "MAE": 0.2146265168037484,
        "R2": 0.5594473110126232,
        "RMSE": 0.2913021971857775,
        "bias": 0.014573282544340737,
        "median_absolute_error": 0.1634300717651844,
        "p90_absolute_error": 0.4620301958999634,
        "p95_absolute_error": 0.5936838422622679,
        "rows": 14945,
        "sMAPE": 0.6505688580406404
      },
      "ranking_spike_ramp": {
        "bottom20_168h_precision": 0.403835227272727,
        "forecast_price_spike_MAE": 0.9348498049818031,
        "high_price_regime_MAE": 1.1852621573739512,
        "large_price_ramp_MAE": 1.0434924319483878,
        "low_price_detection": {
          "f1": 0.09405196478419584,
          "fn": 4061,
          "fp": 158,
          "precision": 0.5809018567639257,
          "recall": 0.05116822429906542,
          "tp": 219
        },
        "low_price_regime_MAE": 0.27856450169130353,
        "ramp_detection": {
          "f1": 0.25504782146652494,
          "fn": 1217,
          "fp": 185,
          "precision": 0.5647058823529412,
          "recall": 0.16472203157172272,
          "tp": 240
        },
        "rows": 59136,
        "spearman": 0.5841218660486119,
        "spike_detection": {
          "f1": 0.018952062430323303,
          "fn": 1570,
          "fp": 190,
          "precision": 0.0821256038647343,
          "recall": 0.010712035286704474,
          "tp": 17
        },
        "top20_168h_precision": 0.39502840909090914
      },
      "weekly": {
        "MAE": 0.3129010449295325,
        "MAE_full_168h": 0.3129010449295325,
        "R2": 0.2705884515379823,
        "RMSE": 0.42263684180990596,
        "bias": -0.06529393987074708,
        "bias_full_168h": -0.06529393987074708,
        "complete_origins": 352,
        "median_absolute_error": 0.2417662058734893,
        "p90_absolute_error": 0.6558563129472733,
        "p90_full_path_absolute_error": 0.6558563129472733,
        "p95_absolute_error": 0.8104093101787566,
        "p95_full_path_absolute_error": 0.8104093101787566,
        "rows": 59136,
        "sMAPE": 0.6396201100103697
      }
    },
    "model_name": "XGBoost",
    "prediction_column": "predicted_price_xgboost",
    "status": "completed",
    "training": {
      "duration_seconds": 15.487,
      "feature_count": 41,
      "holdout_rows": 59136,
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
      "internal_validation_rows": 14945,
      "model_artifact_persisted": false,
      "model_class": "XGBRegressor",
      "model_family": "XGBoost",
      "package": "xgboost",
      "train_rows": 182952
    }
  }
}
```
