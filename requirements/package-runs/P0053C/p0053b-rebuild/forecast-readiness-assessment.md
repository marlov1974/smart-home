# P0053B forecast readiness assessment

```json
{
  "best_baseline": {
    "baseline": "pred_B0_same_hour_previous_day",
    "holdout_MAE": 12.329647719239716,
    "horizon_h": 1
  },
  "best_forecast_safe_model": {
    "holdout_MAE": 6.431734387224803,
    "horizon_h": 1,
    "model": "M4_Ridge_G4_calendar_load_lags_weather"
  },
  "forecast_safe_intermediate_signal": true,
  "non_deployable_groups": [
    "G6_diagnostic_historical_only_non_deployable"
  ],
  "path_168h_summary": {
    "B1_same_hour_previous_week_path": {
      "holdout": {
        "MAE_0_24h": 21.339417461825285,
        "MAE_24_48h": 21.320286966293796,
        "MAE_48_72h": 21.37152217776397,
        "MAE_72_168h": 21.337973525804923,
        "MAE_full_168h": 21.340445815586108,
        "bias_full_168h": 0.4463877930871209,
        "daily_energy_error_proxy": 469.7850668703333,
        "origin_count": 352,
        "peak_hour_error": 53.04525435156258
      },
      "validate": {
        "MAE_0_24h": 25.932914812775948,
        "MAE_24_48h": 25.790509124310162,
        "MAE_48_72h": 25.510950835747803,
        "MAE_72_168h": 24.816638903180205,
        "MAE_full_168h": 25.214418626507804,
        "bias_full_168h": 5.07103831465823,
        "daily_energy_error_proxy": 575.2122345390256,
        "origin_count": 151,
        "peak_hour_error": 64.96930941887419
      }
    },
    "B4_recent_24h_adjusted_path": {
      "holdout": {
        "MAE_0_24h": 17.298530999353904,
        "MAE_24_48h": 19.570159360354456,
        "MAE_48_72h": 20.824722182823095,
        "MAE_72_168h": 23.170172955151333,
        "MAE_full_168h": 21.482014909019526,
        "bias_full_168h": 0.26384750683083025,
        "daily_energy_error_proxy": 385.0728221738584,
        "origin_count": 352,
        "peak_hour_error": 55.90134365232905
      },
      "validate": {
        "MAE_0_24h": 18.695953041770647,
        "MAE_24_48h": 20.992303255121595,
        "MAE_48_72h": 22.425475260945618,
        "MAE_72_168h": 25.857876695992633,
        "MAE_full_168h": 23.64931976311549,
        "bias_full_168h": 3.4741553123849727,
        "daily_energy_error_proxy": 431.6027431550519,
        "origin_count": 151,
        "peak_hour_error": 62.71159185389184
      }
    }
  },
  "recommendation": "Forecast SE2/SE3/SE4 consumption next before production/export-import; consumption is the cleanest physical intermediate.",
  "relative_improvement_vs_best_baseline": 0.47835213676150323,
  "weather_improvement_summary": {
    "1": {
      "actual_weather_diagnostic_MAE": 6.552154406931581,
      "diagnostic_minus_safe": 0.12042001970677774,
      "forecast_safe_weather_MAE": 6.431734387224803
    },
    "168": {
      "actual_weather_diagnostic_MAE": 30.8221835431935,
      "diagnostic_minus_safe": 2.9871444293183664,
      "forecast_safe_weather_MAE": 27.835039113875133
    },
    "24": {
      "actual_weather_diagnostic_MAE": 14.483356463460026,
      "diagnostic_minus_safe": 1.1840423711577124,
      "forecast_safe_weather_MAE": 13.299314092302314
    },
    "48": {
      "actual_weather_diagnostic_MAE": 19.688996510238848,
      "diagnostic_minus_safe": 1.9952847045778483,
      "forecast_safe_weather_MAE": 17.693711805661
    }
  }
}
```
