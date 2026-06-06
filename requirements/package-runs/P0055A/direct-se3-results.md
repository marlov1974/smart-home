# P0055A direct SE3 results

```json
{
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
      "bias": -157.59625315553112,
      "rows": 1587
    },
    "evening_peak": {
      "MAE": 278.8457198197081,
      "RMSE": 384.54991713374744,
      "bias": -74.26945762197136,
      "rows": 1790
    },
    "holiday": {
      "MAE": 318.12285387852387,
      "RMSE": 402.01347442393944,
      "bias": 56.27350688601407,
      "rows": 384
    },
    "morning_ramp": {
      "MAE": 248.82480814806613,
      "RMSE": 340.5091118578107,
      "bias": 9.317843733367454,
      "rows": 1432
    },
    "offpeak": {
      "MAE": 257.3338709723122,
      "RMSE": 344.7718966005968,
      "bias": -120.30398987897439,
      "rows": 2864
    },
    "ramp": {
      "MAE": 273.6819631079534,
      "RMSE": 370.4625196737229,
      "bias": -39.83238153263149,
      "rows": 4128
    },
    "weekday": {
      "MAE": 276.60670238474245,
      "RMSE": 369.92991162995503,
      "bias": -77.87793255447171,
      "rows": 6189
    },
    "weekend": {
      "MAE": 243.88026135538888,
      "RMSE": 352.21278308201016,
      "bias": -29.948648840827023,
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
