# P0055B direct SE3 results

```json
{
  "daily_energy": {
    "absolute_daily_energy_error_MWh": 4723.58095371893,
    "daily_energy_error_percent_of_actual": 2.049876645989931,
    "day_count": 358,
    "signed_daily_energy_error_MWh": -1547.355105430538
  },
  "dayahead": {
    "MAE_percent_of_mean_actual": 2.7818321717660255,
    "MAE_percent_of_median_actual": 2.9138766599582757,
    "absolute_daily_energy_error_MWh": 4723.5809537189325,
    "bias_delivery_day": -64.47312939293917,
    "cold_MAE": 328.4264947779032,
    "evening_peak_MAE": 278.84571981970805,
    "high_price_MAE": null,
    "holiday_MAE": 318.1228538785239,
    "hourly_MAE_delivery_day": 267.45381158009525,
    "hourly_RMSE_delivery_day": 365.0614288460981,
    "large_price_ramp_MAE": null,
    "mean_actual_mw": 9614.3043528864,
    "median_actual_mw": 9178.625,
    "morning_ramp_MAE": 248.82480814806627,
    "offpeak_MAE": 258.6035735558608,
    "p90_absolute_error": 574.5093795634917,
    "p95_absolute_error": 721.5416936529157,
    "peak_hour_error_MW": -232.1300124629935,
    "peak_hour_timing_error_hours": 2.276536312849162,
    "price_spike_MAE": null,
    "sMAPE": 0.028145362051772982,
    "signed_daily_energy_error_MWh": -1547.3551054305374,
    "weekday_MAE": 276.6067023847424,
    "weekend_MAE": 243.88026135538914
  },
  "full36": {
    "MAE_0_12h": 241.97148128838995,
    "MAE_0_24h": 247.47784065309168,
    "MAE_0_6h": 231.56099844726796,
    "MAE_24_36h": 283.4621862253339,
    "MAE_full_36h": 259.4726225105068,
    "MAE_percent_of_mean_actual": 2.662712801233655,
    "MAE_percent_of_median_actual": 2.8027359444489193,
    "RMSE_full_36h": 356.4099129603904,
    "bias_full_36h": -65.08297157849461,
    "daily_energy_error_proxy": 3594.4757489211042,
    "mean_actual_mw": 9744.671764461087,
    "median_actual_mw": 9257.833333333332,
    "p90_absolute_error": 552.2839429650967,
    "p90_full_36h": 552.2839429650967,
    "p95_absolute_error": 692.4665322885708,
    "p95_full_36h": 692.4665322885708,
    "peak_hour_error": 6.179775280898877
  },
  "regimes": {
    "cold_high_load": {
      "MAE": 316.42014735330713,
      "RMSE": 405.04412318222654,
      "bias": -157.59625315553157
    },
    "evening_peak": {
      "MAE": 278.84571981970805,
      "RMSE": 384.5499171337475,
      "bias": -74.26945762197161
    },
    "holiday": {
      "MAE": 318.1228538785239,
      "RMSE": 402.0134744239393,
      "bias": 56.27350688601407
    },
    "morning_ramp": {
      "MAE": 248.82480814806627,
      "RMSE": 340.5091118578108,
      "bias": 9.317843733368335
    },
    "offpeak": {
      "MAE": 257.3338709723122,
      "RMSE": 344.77189660059696,
      "bias": -120.30398987897465
    },
    "ramp": {
      "MAE": 273.6819631079534,
      "RMSE": 370.4625196737229,
      "bias": -39.83238153263152
    },
    "weekday": {
      "MAE": 276.6067023847424,
      "RMSE": 369.92991162995526,
      "bias": -77.87793255447166
    },
    "weekend": {
      "MAE": 243.88026135538914,
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
```
