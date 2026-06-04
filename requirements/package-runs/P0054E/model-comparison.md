# P0054E LABB

```json
{
  "at_least_one_boosted_model_ran": true,
  "best_model_by_direct_holdout_MAE": {
    "holdout_MAE": 17.70265003542135,
    "holdout_R2": 0.9763197471954778,
    "model_name": "LightGBM_G4_se4_load_weather"
  },
  "best_model_by_weekly_MAE_full_168h": {
    "model_name": "XGBoost_G4_se4_load_weather",
    "weekly_MAE_full_168h": 18.251117862247646
  },
  "boosted_vs_extratrees": {
    "LightGBM_G4_se4_load_weather": {
      "p0054d_extratrees_relative_holdout_MAE_percent": -4.878532400380407,
      "p0054d_extratrees_relative_weekly_MAE_full_168h_percent": -5.778430422691697,
      "same_run_minus_extratrees_holdout_MAE": -0.9079228269890898,
      "same_run_minus_extratrees_weekly_MAE_full_168h": -1.13286925637766,
      "same_run_relative_to_extratrees_holdout_MAE_percent": -4.87853240038037,
      "same_run_relative_to_extratrees_weekly_MAE_full_168h_percent": -5.778430422691663
    },
    "XGBoost_G4_se4_load_weather": {
      "p0054d_extratrees_relative_holdout_MAE_percent": -2.5803811246094015,
      "p0054d_extratrees_relative_weekly_MAE_full_168h_percent": -6.906455348113622,
      "same_run_minus_extratrees_holdout_MAE": -0.4802237093233117,
      "same_run_minus_extratrees_weekly_MAE_full_168h": -1.3540200992466715,
      "same_run_relative_to_extratrees_holdout_MAE_percent": -2.5803811246093646,
      "same_run_relative_to_extratrees_weekly_MAE_full_168h_percent": -6.906455348113588
    }
  },
  "comparison_type": "same-run for ExtraTrees/LightGBM/XGBoost; P0054D ExtraTrees included as evidence-summary baseline",
  "conditional_improvement_summary": {
    "by_regime": {
      "cold_hours_temperature_p25_or_lower": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 28.3298340943822,
          "relative_to_extratrees_holdout_MAE_percent": -4.463546798667622
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 25.291525733296744,
          "relative_to_extratrees_holdout_MAE_percent": -14.70960766803282
        }
      },
      "evening_peak_16_20": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 17.846407012537654,
          "relative_to_extratrees_holdout_MAE_percent": -2.1420024696675495
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 17.36093730636059,
          "relative_to_extratrees_holdout_MAE_percent": -4.8040001073293555
        }
      },
      "holiday": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 21.663141243193024,
          "relative_to_extratrees_holdout_MAE_percent": 4.910345679135462
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 22.416098734438872,
          "relative_to_extratrees_holdout_MAE_percent": 8.556771181398098
        }
      },
      "morning_ramp_06_09": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 18.607417459039866,
          "relative_to_extratrees_holdout_MAE_percent": -6.740709730634553
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 19.723639264236965,
          "relative_to_extratrees_holdout_MAE_percent": -1.1462711920775308
        }
      },
      "rapid_temperature_drop_proxy_p10_or_lower": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 26.40136617579344,
          "relative_to_extratrees_holdout_MAE_percent": -12.236699364027661
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 28.891908313653875,
          "relative_to_extratrees_holdout_MAE_percent": -3.9576505854076447
        }
      },
      "summer_low_load_months": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 10.734664170977519,
          "relative_to_extratrees_holdout_MAE_percent": 0.07096745856997315
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 10.762939278749677,
          "relative_to_extratrees_holdout_MAE_percent": 0.3345544087239559
        }
      },
      "very_cold_hours_temperature_p10_or_lower": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 30.123775765302618,
          "relative_to_extratrees_holdout_MAE_percent": -4.154046978007283
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 25.418184746199035,
          "relative_to_extratrees_holdout_MAE_percent": -19.12600332476779
        }
      },
      "weekday": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 18.09839875783257,
          "relative_to_extratrees_holdout_MAE_percent": -3.0100647303640278
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 18.429954751583296,
          "relative_to_extratrees_holdout_MAE_percent": -1.2332448689812259
        }
      },
      "weekend": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 16.718643499405776,
          "relative_to_extratrees_holdout_MAE_percent": -9.56774430754237
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 17.38539698912154,
          "relative_to_extratrees_holdout_MAE_percent": -5.961230294132289
        }
      },
      "winter_high_load_months": {
        "LightGBM_G4_se4_load_weather": {
          "holdout_MAE": 25.526659310281723,
          "relative_to_extratrees_holdout_MAE_percent": -4.441412078178033
        },
        "XGBoost_G4_se4_load_weather": {
          "holdout_MAE": 22.891213166812697,
          "relative_to_extratrees_holdout_MAE_percent": -14.30715709999037
        }
      }
    },
    "interesting": {
      "LightGBM_G4_se4_load_weather": {
        "count": 7,
        "regimes_improved_by_at_least_3_percent": [
          "cold_hours_temperature_p25_or_lower",
          "very_cold_hours_temperature_p10_or_lower",
          "rapid_temperature_drop_proxy_p10_or_lower",
          "weekday",
          "weekend",
          "morning_ramp_06_09",
          "winter_high_load_months"
        ]
      },
      "XGBoost_G4_se4_load_weather": {
        "count": 6,
        "regimes_improved_by_at_least_3_percent": [
          "cold_hours_temperature_p25_or_lower",
          "very_cold_hours_temperature_p10_or_lower",
          "rapid_temperature_drop_proxy_p10_or_lower",
          "weekend",
          "evening_peak_16_20",
          "winter_high_load_months"
        ]
      }
    }
  },
  "direct_holdout": [
    {
      "holdout_MAE": 18.61057286241044,
      "holdout_R2": 0.974251436737391,
      "model_name": "ExtraTrees_G4_se4_load_weather"
    },
    {
      "holdout_MAE": 17.70265003542135,
      "holdout_R2": 0.9763197471954778,
      "model_name": "LightGBM_G4_se4_load_weather"
    },
    {
      "holdout_MAE": 18.130349153087128,
      "holdout_R2": 0.9692659389751597,
      "model_name": "XGBoost_G4_se4_load_weather"
    }
  ],
  "interpretation_category": "candidate_for_followup",
  "learning_threshold": {
    "conditional_percent": -3.0,
    "direct_or_weekly_percent": -2.0
  },
  "models_beating_p0054d_extratrees_by_at_least_2_percent_holdout_or_weekly": [
    "LightGBM_G4_se4_load_weather",
    "XGBoost_G4_se4_load_weather"
  ],
  "p0054d_extratrees_baseline": {
    "holdout_MAE": 18.610572862410447,
    "weekly_MAE_full_168h": 19.605137961494325
  },
  "weekly_168h": [
    {
      "model_name": "ExtraTrees_G4_se4_load_weather",
      "weekly_MAE_full_168h": 19.605137961494318
    },
    {
      "model_name": "LightGBM_G4_se4_load_weather",
      "weekly_MAE_full_168h": 18.472268705116658
    },
    {
      "model_name": "XGBoost_G4_se4_load_weather",
      "weekly_MAE_full_168h": 18.251117862247646
    }
  ]
}
```
