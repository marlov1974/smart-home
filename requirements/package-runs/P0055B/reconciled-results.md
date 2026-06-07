# P0055B reconciled results

```json
{
  "metrics": {
    "daily_energy": {
      "absolute_daily_energy_error_MWh": 4770.043389541966,
      "daily_energy_error_percent_of_actual": 2.07432843679523,
      "day_count": 358,
      "signed_daily_energy_error_MWh": -713.8493341828415
    },
    "dayahead": {
      "MAE_percent_of_mean_actual": 2.811918612176803,
      "MAE_percent_of_median_actual": 2.9453912054380393,
      "absolute_daily_energy_error_MWh": 4770.043389541965,
      "bias_delivery_day": -29.74372225761851,
      "cold_MAE": 340.85248996027815,
      "evening_peak_MAE": 281.9140957909585,
      "high_price_MAE": null,
      "holiday_MAE": 363.6392262490581,
      "hourly_MAE_delivery_day": 270.3464135301372,
      "hourly_RMSE_delivery_day": 369.37820744784574,
      "large_price_ramp_MAE": null,
      "mean_actual_mw": 9614.3043528864,
      "median_actual_mw": 9178.625,
      "morning_ramp_MAE": 260.89900577762893,
      "offpeak_MAE": 257.9995423513361,
      "p90_absolute_error": 572.2306143041438,
      "p95_absolute_error": 715.8933629436035,
      "peak_hour_error_MW": -213.22742050993335,
      "peak_hour_timing_error_hours": 2.38268156424581,
      "price_spike_MAE": null,
      "sMAPE": 0.028441205086699558,
      "signed_daily_energy_error_MWh": -713.8493341828407,
      "weekday_MAE": 277.3437558608574,
      "weekend_MAE": 252.324544331293
    },
    "full36": {
      "MAE_0_12h": 246.07991003058365,
      "MAE_0_24h": 251.75704292844256,
      "MAE_0_6h": 232.09073700298165,
      "MAE_24_36h": 283.80399372646934,
      "MAE_full_36h": 262.439359861117,
      "MAE_percent_of_mean_actual": 2.6931575142247057,
      "MAE_percent_of_median_actual": 2.8347816428730663,
      "RMSE_full_36h": 360.65032277274497,
      "bias_full_36h": -29.721734746689354,
      "daily_energy_error_proxy": 3629.5715095556147,
      "mean_actual_mw": 9744.671764461087,
      "median_actual_mw": 9257.833333333332,
      "p90_absolute_error": 549.9200379336335,
      "p90_full_36h": 549.9200379336335,
      "p95_absolute_error": 686.8991689138243,
      "p95_full_36h": 686.8991689138243,
      "peak_hour_error": 6.264044943820225
    },
    "regimes": {
      "cold_high_load": {
        "MAE": 328.81552365348745,
        "RMSE": 414.2186048767858,
        "bias": -126.13101979831153
      },
      "evening_peak": {
        "MAE": 281.9140957909585,
        "RMSE": 390.63031749356423,
        "bias": -28.61190597205557
      },
      "holiday": {
        "MAE": 363.6392262490581,
        "RMSE": 446.0133567973639,
        "bias": 204.26788754395344
      },
      "morning_ramp": {
        "MAE": 260.89900577762893,
        "RMSE": 356.935998436447,
        "bias": 31.375182321625505
      },
      "offpeak": {
        "MAE": 255.9014011081564,
        "RMSE": 341.06665756506567,
        "bias": -75.4871560540304
      },
      "ramp": {
        "MAE": 281.0843910418408,
        "RMSE": 377.0045715296864,
        "bias": -7.075214351779395
      },
      "weekday": {
        "MAE": 277.3437558608574,
        "RMSE": 374.9265420052648,
        "bias": -41.01602485525793
      },
      "weekend": {
        "MAE": 252.324544331293,
        "RMSE": 354.68889989680446,
        "bias": -0.7115621341100975
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
    "internal_validation_mae_mw": 103.55142016675141,
    "internal_validation_rows": 3310,
    "status": "run",
    "weights": {
      "bias": 2.143220143150707e-14,
      "decomposition": 1.0,
      "direct": 0.0
    }
  }
}
```
