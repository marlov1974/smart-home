# P0055B2 reconciled results

```json
{
  "metrics": {
    "daily_energy": {
      "absolute_daily_energy_error_MWh": 4977.100217383422,
      "daily_energy_error_percent_of_actual": 2.1411213922962142,
      "day_count": 358,
      "signed_daily_energy_error_MWh": -911.2522375771159
    },
    "dayahead": {
      "MAE_percent_of_mean_actual": 2.87914243069597,
      "MAE_percent_of_median_actual": 3.0158059190804933,
      "absolute_daily_energy_error_MWh": 4977.100217383418,
      "bias_delivery_day": -37.96884323237975,
      "cold_MAE": 367.9398637684607,
      "evening_peak_MAE": 287.2822137400435,
      "high_price_MAE": null,
      "holiday_MAE": 387.62546244642067,
      "hourly_MAE_delivery_day": 276.8095160402019,
      "hourly_RMSE_delivery_day": 379.71387718934403,
      "large_price_ramp_MAE": null,
      "mean_actual_mw": 9614.3043528864,
      "median_actual_mw": 9178.625,
      "morning_ramp_MAE": 269.5675612649053,
      "offpeak_MAE": 263.7941889842997,
      "p90_absolute_error": 587.5988973192817,
      "p95_absolute_error": 742.2310058240039,
      "peak_hour_error_MW": -220.4733318733277,
      "peak_hour_timing_error_hours": 2.377094972067039,
      "price_spike_MAE": null,
      "sMAPE": 0.02893378457664671,
      "signed_daily_energy_error_MWh": -911.2522375771142,
      "weekday_MAE": 286.0178479698465,
      "weekend_MAE": 253.0931755023073
    },
    "full36": {
      "MAE_0_12h": 251.6400113545003,
      "MAE_0_24h": 258.2922047394393,
      "MAE_0_6h": 237.34001374509197,
      "MAE_24_36h": 289.54834776781865,
      "MAE_full_36h": 268.7109190822324,
      "MAE_percent_of_mean_actual": 2.7575163697378064,
      "MAE_percent_of_median_actual": 2.9025249149250087,
      "RMSE_full_36h": 370.16283355580197,
      "bias_full_36h": -36.14750578812398,
      "daily_energy_error_proxy": 3774.4771949590663,
      "mean_actual_mw": 9744.671764461087,
      "median_actual_mw": 9257.833333333332,
      "p90_absolute_error": 567.0436525797413,
      "p90_full_36h": 567.0436525797413,
      "p95_absolute_error": 711.5838813993396,
      "p95_full_36h": 711.5838813993396,
      "peak_hour_error": 6.073033707865169
    },
    "regimes": {
      "cold_high_load": {
        "MAE": 355.2590279208565,
        "RMSE": 449.1269316186479,
        "bias": -175.19505766310806
      },
      "evening_peak": {
        "MAE": 287.2822137400435,
        "RMSE": 399.0268922156516,
        "bias": -34.36674548245953
      },
      "holiday": {
        "MAE": 387.62546244642067,
        "RMSE": 476.03762783653883,
        "bias": 185.88103150852916
      },
      "morning_ramp": {
        "MAE": 269.5675612649053,
        "RMSE": 374.2467102600001,
        "bias": 25.79582865619638
      },
      "offpeak": {
        "MAE": 261.4023731277383,
        "RMSE": 352.2446897125377,
        "bias": -86.62969059989506
      },
      "ramp": {
        "MAE": 284.66828014614686,
        "RMSE": 384.3726265512455,
        "bias": -8.66885332664342
      },
      "weekday": {
        "MAE": 286.0178479698465,
        "RMSE": 387.7507351159486,
        "bias": -47.15255320776316
      },
      "weekend": {
        "MAE": 253.0931755023073,
        "RMSE": 358.1853506676299,
        "bias": -14.315917290786738
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
    "internal_validation_mae_mw": 103.75398818272043,
    "internal_validation_rows": 3310,
    "status": "run",
    "weights": {
      "bias": -4.0116684730769644e-14,
      "decomposition": 1.0,
      "direct": 0.0
    }
  }
}
```
