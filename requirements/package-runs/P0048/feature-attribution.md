# P0048 feature attribution

{
  "continuous_validate": {
    "S0_time_calendar_baseline": {
      "MAE": 0.27297607938067714,
      "RMSE": 0.38163521911772175,
      "bias": -0.04237441695702894,
      "median_absolute_error": 0.21248049074074077,
      "p90_absolute_error": 0.5380151703703705,
      "p95_absolute_error": 0.7149109407407408,
      "row_count": 8760,
      "spearman": 0.23660204469997978
    },
    "S1_weather_gradient_regression": {
      "MAE": 0.3054126909912295,
      "RMSE": 0.5333711383105222,
      "bias": -0.04869003032040786,
      "median_absolute_error": 0.17741146436416727,
      "p90_absolute_error": 0.6986004250944833,
      "p95_absolute_error": 1.0421682878324074,
      "row_count": 8760,
      "spearman": 0.3599515925140351
    },
    "S2_with_lagged_spread_features_diagnostic": {
      "MAE": 0.09374424013635566,
      "RMSE": 0.155419230438039,
      "bias": -0.0020038894863094988,
      "median_absolute_error": 0.05287793599333939,
      "p90_absolute_error": 0.22389628794705482,
      "p95_absolute_error": 0.3197779605679991,
      "row_count": 8760,
      "spearman": 0.9118888558940238
    }
  },
  "gradient_improvement_over_system_weather_f1": -0.01251207847827196,
  "lagged_improvement_over_gradient_f1": 0.6064174775738277,
  "stage1_positive_validate_by_group": {
    "C0_time_calendar_baseline": {
      "confusion_matrix": {
        "0": {
          "0": 3709,
          "1": 0
        },
        "1": {
          "0": 5051,
          "1": 0
        }
      },
      "f1": 0.0,
      "fn": 5051,
      "fp": 0,
      "positive_label": 1,
      "precision": 0.0,
      "recall": 0.0,
      "tn": 3709,
      "tp": 0
    },
    "C1_time_calendar_weather_actual": {
      "confusion_matrix": {
        "0": {
          "0": 3540,
          "1": 169
        },
        "1": {
          "0": 4156,
          "1": 895
        }
      },
      "f1": 0.29272281275551926,
      "fn": 4156,
      "fp": 169,
      "positive_label": 1,
      "pr_auc": 0.7346958314037191,
      "precision": 0.8411654135338346,
      "recall": 0.17719263512175806,
      "roc_auc": 0.676983978837801,
      "tn": 3540,
      "tp": 895
    },
    "C2_time_calendar_weather_gradient": {
      "confusion_matrix": {
        "0": {
          "0": 3537,
          "1": 172
        },
        "1": {
          "0": 4200,
          "1": 851
        }
      },
      "f1": 0.2802107342772473,
      "fn": 4200,
      "fp": 172,
      "positive_label": 1,
      "pr_auc": 0.7350765744819783,
      "precision": 0.8318670576735093,
      "recall": 0.16848148881409622,
      "roc_auc": 0.6839684129936124,
      "tn": 3537,
      "tp": 851
    },
    "C3_time_calendar_weather_anomaly_gradient": {
      "confusion_matrix": {
        "0": {
          "0": 3568,
          "1": 141
        },
        "1": {
          "0": 4208,
          "1": 843
        }
      },
      "f1": 0.27937033968516983,
      "fn": 4208,
      "fp": 141,
      "positive_label": 1,
      "pr_auc": 0.7400803400120641,
      "precision": 0.8567073170731707,
      "recall": 0.16689764403088497,
      "roc_auc": 0.6826813789719623,
      "tn": 3568,
      "tp": 843
    },
    "C4_with_lagged_spread_features_diagnostic": {
      "confusion_matrix": {
        "0": {
          "0": 3452,
          "1": 257
        },
        "1": {
          "0": 824,
          "1": 4227
        }
      },
      "f1": 0.886628211851075,
      "fn": 824,
      "fp": 257,
      "positive_label": 1,
      "pr_auc": 0.9676088570732957,
      "precision": 0.9426851025869759,
      "recall": 0.8368639873292417,
      "roc_auc": 0.9602805228673461,
      "tn": 3452,
      "tp": 4227
    }
  },
  "stage2_positive_severity_validate": {
    "R0_regime_mean_baseline": {
      "MAE": 0.7216842272892269,
      "RMSE": 0.7719497200777901,
      "bias": 0.6646183181064463,
      "median_absolute_error": 0.8093130171759382,
      "p90_absolute_error": 0.9641755171759382,
      "p95_absolute_error": 0.9845817671759383,
      "row_count": 5051,
      "spearman": -0.07544499932908412
    },
    "R1_time_calendar_baseline": {
      "MAE": 0.5149403205674515,
      "RMSE": 0.8199367357949798,
      "bias": 0.27462850029055924,
      "median_absolute_error": 0.29532766300747815,
      "p90_absolute_error": 1.2382113927801444,
      "p95_absolute_error": 1.6024058974413031,
      "row_count": 5051,
      "spearman": 0.1279736012770398
    },
    "R2_weather_gradient_regressor": {
      "MAE": 0.504713428999341,
      "RMSE": 0.8075809897357257,
      "bias": 0.30961746123757905,
      "median_absolute_error": 0.27643249964316563,
      "p90_absolute_error": 1.232397925315895,
      "p95_absolute_error": 1.8079972699240305,
      "row_count": 5051,
      "spearman": 0.19002415506701242
    },
    "R3_weather_anomaly_gradient_regressor": {
      "MAE": 0.522257917336551,
      "RMSE": 0.8500423463427199,
      "bias": 0.34257707020540906,
      "median_absolute_error": 0.2817488511825322,
      "p90_absolute_error": 1.306123635096069,
      "p95_absolute_error": 1.958160319033242,
      "row_count": 5051,
      "spearman": 0.22621622517977316
    },
    "R4_with_lagged_spread_features_diagnostic": {
      "MAE": 0.14071298286546702,
      "RMSE": 0.21086624906849127,
      "bias": 0.07549149799396097,
      "median_absolute_error": 0.09668715770809741,
      "p90_absolute_error": 0.2968471620698254,
      "p95_absolute_error": 0.47803097314021176,
      "row_count": 5051,
      "spearman": 0.7777480224510491
    }
  }
}

Gradient improvement is measured as Stage-1 positive-bottleneck validation F1 delta from actual-weather group to gradient group. Lagged improvement is validation F1 delta from gradient group to lagged diagnostic group.
