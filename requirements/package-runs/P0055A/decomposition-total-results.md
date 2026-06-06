# P0055A decomposition total results

```json
{
  "daily_energy": {
    "absolute_daily_energy_error_MWh": 5718.561219680843,
    "daily_energy_error_percent_of_actual": 2.373946785493369,
    "day_count": 358,
    "signed_daily_energy_error_MWh": -1995.8804211022812
  },
  "dayahead": {
    "MAE_percent_of_mean_actual": 3.132942920901581,
    "MAE_percent_of_median_actual": 3.28165348968595,
    "absolute_daily_energy_error_MWh": 5718.561219680842,
    "bias_delivery_day": -83.16168421259505,
    "cold_MAE": 461.01015323194054,
    "evening_peak_MAE": 318.2414064001063,
    "high_price_MAE": null,
    "holiday_MAE": 401.1190802224469,
    "hourly_MAE_delivery_day": 301.210667617687,
    "hourly_RMSE_delivery_day": 411.511791120297,
    "large_price_ramp_MAE": null,
    "mean_actual_mw": 9614.3043528864,
    "median_actual_mw": 9178.625,
    "morning_ramp_MAE": 287.94730208729413,
    "offpeak_MAE": 289.537455279974,
    "p90_absolute_error": 659.1275610356989,
    "p95_absolute_error": 823.5168341763401,
    "peak_hour_error_MW": -276.3789694966822,
    "peak_hour_timing_error_hours": 2.142458100558659,
    "price_spike_MAE": null,
    "sMAPE": 0.0308207583284423,
    "signed_daily_energy_error_MWh": -1995.8804211022798,
    "weekday_MAE": 309.9511905731585,
    "weekend_MAE": 278.69918340153646
  },
  "full36": {
    "MAE_0_12h": 278.6631127170088,
    "MAE_0_24h": 282.0114178213461,
    "MAE_0_6h": 261.5513395895413,
    "MAE_24_36h": 318.59772164814535,
    "MAE_full_36h": 294.2068524302795,
    "MAE_percent_of_mean_actual": 3.019156104398044,
    "MAE_percent_of_median_actual": 3.1779234064516126,
    "RMSE_full_36h": 402.6054197225328,
    "bias_full_36h": -84.21101091909595,
    "daily_energy_error_proxy": 4344.834310088689,
    "mean_actual_mw": 9744.671764461087,
    "median_actual_mw": 9257.833333333332,
    "p90_absolute_error": 639.7021503371316,
    "p90_full_36h": 639.7021503371316,
    "p95_absolute_error": 803.598033763371,
    "p95_full_36h": 803.598033763371,
    "peak_hour_error": 5.957865168539326
  },
  "regimes": {
    "cold_high_load": {
      "MAE": 469.14519071987286,
      "RMSE": 569.4540633691081,
      "bias": -343.39999507908,
      "rows": 1587
    },
    "evening_peak": {
      "MAE": 318.2414064001063,
      "RMSE": 433.46441332330585,
      "bias": -85.43626284315903,
      "rows": 1790
    },
    "holiday": {
      "MAE": 401.1190802224469,
      "RMSE": 486.2828273013063,
      "bias": 187.7792960762911,
      "rows": 384
    },
    "morning_ramp": {
      "MAE": 287.94730208729413,
      "RMSE": 401.12864028555293,
      "bias": -16.246247984869317,
      "rows": 1432
    },
    "offpeak": {
      "MAE": 286.93901659245614,
      "RMSE": 392.17533272297266,
      "bias": -127.09575819444804,
      "rows": 2864
    },
    "ramp": {
      "MAE": 306.95880902557633,
      "RMSE": 412.6094761355052,
      "bias": -58.878312699259546,
      "rows": 4128
    },
    "weekday": {
      "MAE": 309.9511905731585,
      "RMSE": 418.9579829301883,
      "bias": -90.59267557460736,
      "rows": 6189
    },
    "weekend": {
      "MAE": 278.69918340153646,
      "RMSE": 391.68264232903005,
      "bias": -64.02293866973422,
      "rows": 2403
    }
  },
  "row_counts": {
    "dayahead_selected_rows": 8592,
    "full36_selected_rows": 12816,
    "input_rows": 33582
  }
}
```
