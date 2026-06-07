# P0055B2 raw decomposition reference

```json
{
  "available": true,
  "p0055a_comparison_vs_direct": {
    "daily_energy_delta_vs_direct_percent": 21.064109532801677,
    "decomposition_beats_direct_threshold": false,
    "decomposition_delta_vs_direct_MW": 33.75685603759189,
    "decomposition_delta_vs_direct_percent": 12.62156476221414,
    "full36_delta_vs_direct_percent": 13.38647198448312,
    "reconciled_beats_direct_threshold": false,
    "reconciled_delta_vs_direct_MW": 33.75913930489685,
    "reconciled_delta_vs_direct_percent": 12.622418467491874
  },
  "p0055a_decomposition_total": {
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
        "bias": -343.39999507908
      },
      "evening_peak": {
        "MAE": 318.2414064001063,
        "RMSE": 433.46441332330585,
        "bias": -85.43626284315903
      },
      "holiday": {
        "MAE": 401.1190802224469,
        "RMSE": 486.2828273013063,
        "bias": 187.7792960762911
      },
      "morning_ramp": {
        "MAE": 287.94730208729413,
        "RMSE": 401.12864028555293,
        "bias": -16.246247984869317
      },
      "offpeak": {
        "MAE": 286.93901659245614,
        "RMSE": 392.17533272297266,
        "bias": -127.09575819444804
      },
      "ramp": {
        "MAE": 306.95880902557633,
        "RMSE": 412.6094761355052,
        "bias": -58.878312699259546
      },
      "weekday": {
        "MAE": 309.9511905731585,
        "RMSE": 418.9579829301883,
        "bias": -90.59267557460736
      },
      "weekend": {
        "MAE": 278.69918340153646,
        "RMSE": 391.68264232903005,
        "bias": -64.02293866973422
      }
    },
    "row_counts": {
      "dayahead_selected_rows": 8592,
      "full36_selected_rows": 12816,
      "input_rows": 33582
    }
  },
  "p0055a_direct_se3": {
    "daily_energy": {
      "absolute_daily_energy_error_MWh": 4723.58095371893,
      "daily_energy_error_percent_of_actual": 2.049876645989931,
      "day_count": 358,
      "signed_daily_energy_error_MWh": -1547.3551054305378
    },
    "dayahead": {
      "MAE_percent_of_mean_actual": 2.781832171766024,
      "MAE_percent_of_median_actual": 2.913876659958274,
      "absolute_daily_energy_error_MWh": 4723.5809537189325,
      "bias_delivery_day": -64.47312939293926,
      "cold_MAE": 328.4264947779028,
      "evening_peak_MAE": 278.8457198197081,
      "high_price_MAE": null,
      "holiday_MAE": 318.12285387852387,
      "hourly_MAE_delivery_day": 267.45381158009513,
      "hourly_RMSE_delivery_day": 365.06142884609807,
      "large_price_ramp_MAE": null,
      "mean_actual_mw": 9614.3043528864,
      "median_actual_mw": 9178.625,
      "morning_ramp_MAE": 248.82480814806613,
      "offpeak_MAE": 258.6035735558606,
      "p90_absolute_error": 574.5093795634917,
      "p95_absolute_error": 721.5416936529132,
      "peak_hour_error_MW": -232.13001246299407,
      "peak_hour_timing_error_hours": 2.276536312849162,
      "price_spike_MAE": null,
      "sMAPE": 0.028145362051772968,
      "signed_daily_energy_error_MWh": -1547.3551054305378,
      "weekday_MAE": 276.60670238474245,
      "weekend_MAE": 243.88026135538888
    },
    "full36": {
      "MAE_0_12h": 241.97148128838978,
      "MAE_0_24h": 247.4778406530914,
      "MAE_0_6h": 231.56099844726802,
      "MAE_24_36h": 283.4621862253338,
      "MAE_full_36h": 259.4726225105069,
      "MAE_percent_of_mean_actual": 2.6627128012336554,
      "MAE_percent_of_median_actual": 2.8027359444489197,
      "RMSE_full_36h": 356.40991296039033,
      "bias_full_36h": -65.08297157849462,
      "daily_energy_error_proxy": 3594.475748921103,
      "mean_actual_mw": 9744.671764461087,
      "median_actual_mw": 9257.833333333332,
      "p90_absolute_error": 552.2839429650976,
      "p90_full_36h": 552.2839429650976,
      "p95_absolute_error": 692.4665322885689,
      "p95_full_36h": 692.4665322885689,
      "peak_hour_error": 6.179775280898877
    },
    "regimes": {
      "cold_high_load": {
        "MAE": 316.4201473533067,
        "RMSE": 405.04412318222643,
        "bias": -157.59625315553112
      },
      "evening_peak": {
        "MAE": 278.8457198197081,
        "RMSE": 384.54991713374744,
        "bias": -74.26945762197136
      },
      "holiday": {
        "MAE": 318.12285387852387,
        "RMSE": 402.01347442393944,
        "bias": 56.27350688601407
      },
      "morning_ramp": {
        "MAE": 248.82480814806613,
        "RMSE": 340.5091118578107,
        "bias": 9.317843733367454
      },
      "offpeak": {
        "MAE": 257.3338709723122,
        "RMSE": 344.7718966005968,
        "bias": -120.30398987897439
      },
      "ramp": {
        "MAE": 273.6819631079534,
        "RMSE": 370.4625196737229,
        "bias": -39.83238153263149
      },
      "weekday": {
        "MAE": 276.60670238474245,
        "RMSE": 369.92991162995503,
        "bias": -77.87793255447171
      },
      "weekend": {
        "MAE": 243.88026135538888,
        "RMSE": 352.21278308201016,
        "bias": -29.948648840827023
      }
    },
    "row_counts": {
      "dayahead_selected_rows": 8592,
      "full36_selected_rows": 12816,
      "input_rows": 33582
    }
  }
}
```
