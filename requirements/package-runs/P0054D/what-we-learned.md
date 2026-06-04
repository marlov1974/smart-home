# P0054D LABB

P0054D separates weather proxy quality from model-family effects. The corrected proxy lets the SE4 experiment test whether P0054C's HGB win was caused by broad weather. Read `model-comparison.md` for the final answer and threshold interpretation.

```json
{
  "model_comparison": {
    "advanced_beats_hgb_direct_holdout": true,
    "best_advanced_minus_hgb_holdout_MAE": -3.2109234236413116,
    "best_advanced_model_by_direct_holdout_MAE": {
      "holdout_MAE": 18.610572862410447,
      "holdout_R2": 0.974251436737391,
      "model_name": "ExtraTrees_G4_se4_load_weather"
    },
    "best_advanced_relative_to_hgb_holdout_MAE_percent": -14.714497033339208,
    "best_model_by_direct_holdout_MAE": {
      "holdout_MAE": 18.610572862410447,
      "holdout_R2": 0.974251436737391,
      "model_name": "ExtraTrees_G4_se4_load_weather"
    },
    "best_model_by_weekly_MAE_full_168h": {
      "model_name": "ExtraTrees_G4_se4_load_weather",
      "weekly_MAE_full_168h": 19.605137961494325
    },
    "direct_holdout": [
      {
        "holdout_MAE": 21.821496286051758,
        "holdout_R2": 0.9676687711532018,
        "model_name": "HGB_G4_se4_load_weather"
      },
      {
        "holdout_MAE": 21.65082416112652,
        "holdout_R2": 0.9592596628738974,
        "model_name": "MLP_G4_se4_load_weather"
      },
      {
        "holdout_MAE": 18.610572862410447,
        "holdout_R2": 0.974251436737391,
        "model_name": "ExtraTrees_G4_se4_load_weather"
      }
    ],
    "weekly_168h": [
      {
        "model_name": "HGB_G4_se4_load_weather",
        "weekly_MAE_full_168h": 24.998676309000498
      },
      {
        "model_name": "MLP_G4_se4_load_weather",
        "weekly_MAE_full_168h": 22.467442520295915
      },
      {
        "model_name": "ExtraTrees_G4_se4_load_weather",
        "weekly_MAE_full_168h": 19.605137961494325
      }
    ]
  },
  "p0054c_old_vs_new_weather_comparison": {
    "available": true,
    "comparison_type": "evidence-summary comparison; old P0054C south_connected_weather vs new P0054D se4_load_weather",
    "corrected_weather_changes_p0054c_conclusion": true,
    "hgb_new_holdout_MAE": 21.821496286051758,
    "hgb_new_minus_old_holdout_MAE": -0.7287944791535175,
    "hgb_new_relative_change_percent": -3.231862891444554,
    "hgb_new_weekly_MAE_full_168h": 24.998676309000498,
    "hgb_old_holdout_MAE": 22.550290765205276,
    "hgb_old_weekly_MAE_full_168h": 28.173194514106815,
    "hgb_weekly_relative_change_percent": -11.267867417437449,
    "interpretation": "Corrected weather materially changes the P0054C MLP-vs-HGB picture: MLP no longer has the broad-weather penalty, but ExtraTrees is the strongest corrected-proxy model.",
    "mlp_new_holdout_MAE": 21.65082416112652,
    "mlp_new_minus_old_holdout_MAE": -5.305859223151668,
    "mlp_new_relative_change_percent": -19.68290812157618,
    "mlp_new_weekly_MAE_full_168h": 22.467442520295915,
    "mlp_old_holdout_MAE": 26.956683384278186,
    "mlp_old_weekly_MAE_full_168h": 28.48507022378669,
    "mlp_weekly_relative_change_percent": -21.125549827381874,
    "new_mlp_minus_hgb_holdout_MAE": -0.17067212492523964,
    "new_weekly_mlp_minus_hgb_MAE_full_168h": -2.531233788704583,
    "old_mlp_minus_hgb_holdout_MAE": 4.406392619072911,
    "old_weekly_mlp_minus_hgb_MAE_full_168h": 0.31187570967987455,
    "p0054c_weather_proxy": {
      "area_proxy": "south_connected_weather",
      "available": true,
      "end": "2026-05-29T21:00:00Z",
      "forecast_safety": "not_a_separate_forecast_model; LABB proxy only",
      "input_classification": "proxy",
      "proxy_label": "weather_actual_as_forecast_proxy",
      "rows": 35064,
      "start": "2022-05-29T22:00:00Z",
      "table": "weather_area_hourly"
    },
    "p0054d_weather_proxy": {
      "area_proxy": "se4_load_weather",
      "locations": [
        {
          "households_represented": 235000,
          "latitude": 55.605,
          "location_id": "se4_load_malmo",
          "longitude": 13.0038,
          "name": "Malmo",
          "weight": 0.6010230179028133
        },
        {
          "households_represented": 93000,
          "latitude": 56.0465,
          "location_id": "se4_load_helsingborg",
          "longitude": 12.6945,
          "name": "Helsingborg",
          "weight": 0.23785166240409208
        },
        {
          "households_represented": 63000,
          "latitude": 56.0294,
          "location_id": "se4_load_kristianstad",
          "longitude": 14.1567,
          "name": "Kristianstad",
          "weight": 0.16112531969309463
        }
      ],
      "proxy_label": "weather_actual_as_forecast_proxy",
      "source_table": "weather_locations/weather_observations/weather_area_hourly",
      "weight_sum": 1.0
    }
  }
}
```
