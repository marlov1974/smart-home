# P0055A reconciled results

```json
{
  "metrics": {
    "daily_energy": {
      "absolute_daily_energy_error_MWh": 5718.630750178589,
      "daily_energy_error_percent_of_actual": 2.3739707767096614,
      "day_count": 358,
      "signed_daily_energy_error_MWh": -1996.1452287426175
    },
    "dayahead": {
      "MAE_percent_of_mean_actual": 3.132966669549649,
      "MAE_percent_of_median_actual": 3.2816783656047828,
      "absolute_daily_energy_error_MWh": 5718.630750178587,
      "bias_delivery_day": -83.17271786427547,
      "cold_MAE": 461.01503388326927,
      "evening_peak_MAE": 318.2440939264375,
      "high_price_MAE": null,
      "holiday_MAE": 401.1151724708099,
      "hourly_MAE_delivery_day": 301.212950884992,
      "hourly_RMSE_delivery_day": 411.51402103317236,
      "large_price_ramp_MAE": null,
      "mean_actual_mw": 9614.3043528864,
      "median_actual_mw": 9178.625,
      "morning_ramp_MAE": 287.9475332392145,
      "offpeak_MAE": 289.54055579773683,
      "p90_absolute_error": 659.1385946873799,
      "p95_absolute_error": 823.527867828021,
      "peak_hour_error_MW": -276.390003148363,
      "peak_hour_timing_error_hours": 2.142458100558659,
      "price_spike_MAE": null,
      "sMAPE": 0.03082097143807608,
      "signed_daily_energy_error_MWh": -1996.145228742616,
      "weekday_MAE": 309.9538059176426,
      "weekend_MAE": 278.70061139390924
    },
    "full36": {
      "MAE_0_12h": 278.6653442420676,
      "MAE_0_24h": 282.0134530548498,
      "MAE_0_6h": 261.55335416077475,
      "MAE_24_36h": 318.60045939879615,
      "MAE_full_36h": 294.2091218361652,
      "MAE_percent_of_mean_actual": 3.019179393082779,
      "MAE_percent_of_median_actual": 3.177947919810235,
      "RMSE_full_36h": 402.60772772218763,
      "bias_full_36h": -84.22204457077643,
      "daily_energy_error_proxy": 4344.887494769263,
      "mean_actual_mw": 9744.671764461087,
      "median_actual_mw": 9257.833333333332,
      "p90_absolute_error": 639.7131839888125,
      "p90_full_36h": 639.7131839888125,
      "p95_absolute_error": 803.5925169375305,
      "p95_full_36h": 803.5925169375305,
      "peak_hour_error": 5.957865168539326
    },
    "regimes": {
      "cold_high_load": {
        "MAE": 469.1516913275117,
        "RMSE": 569.460717101009,
        "bias": -343.4110287307603,
        "rows": 1587
      },
      "evening_peak": {
        "MAE": 318.2440939264375,
        "RMSE": 433.4665882018926,
        "bias": -85.44729649483975,
        "rows": 1790
      },
      "holiday": {
        "MAE": 401.1151724708099,
        "RMSE": 486.27856673639445,
        "bias": 187.76826242461058,
        "rows": 384
      },
      "morning_ramp": {
        "MAE": 287.9475332392145,
        "RMSE": 401.12908731474556,
        "bias": -16.257281636550022,
        "rows": 1432
      },
      "offpeak": {
        "MAE": 286.9423451801131,
        "RMSE": 392.17890863580055,
        "bias": -127.10679184612874,
        "rows": 2864
      },
      "ramp": {
        "MAE": 306.96071746242285,
        "RMSE": 412.61105075378833,
        "bias": -58.88934635094,
        "rows": 4128
      },
      "weekday": {
        "MAE": 309.9538059176426,
        "RMSE": 418.9603689118191,
        "bias": -90.60370922628813,
        "rows": 6189
      },
      "weekend": {
        "MAE": 278.70061139390924,
        "RMSE": 391.6844459985647,
        "bias": -64.03397232141478,
        "rows": 2403
      }
    },
    "row_counts": {
      "dayahead_selected_rows": 8592,
      "full36_selected_rows": 12816,
      "input_rows": 33582
    }
  },
  "reconciliation": {
    "fit_data": "internal_validation_only",
    "holdout_used_for_weights_or_bias": false,
    "internal_validation_mae_mw": 103.50939222842052,
    "internal_validation_rows": 3310,
    "status": "run",
    "weights": {
      "bias": 0.011033651680422998,
      "decomposition": 1.0,
      "direct": 0.0
    }
  }
}
```
