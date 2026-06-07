# P0055B2 direct SE3 results

```json
{
  "daily_energy": {
    "absolute_daily_energy_error_MWh": 4723.580953718932,
    "daily_energy_error_percent_of_actual": 2.0498766459899307,
    "day_count": 358,
    "signed_daily_energy_error_MWh": -1547.3551054305374
  },
  "dayahead": {
    "MAE_percent_of_mean_actual": 2.781832171766023,
    "MAE_percent_of_median_actual": 2.9138766599582726,
    "absolute_daily_energy_error_MWh": 4723.580953718931,
    "bias_delivery_day": -64.4731293929392,
    "cold_MAE": 328.42649477790286,
    "evening_peak_MAE": 278.845719819708,
    "high_price_MAE": null,
    "holiday_MAE": 318.12285387852415,
    "hourly_MAE_delivery_day": 267.453811580095,
    "hourly_RMSE_delivery_day": 365.061428846098,
    "large_price_ramp_MAE": null,
    "mean_actual_mw": 9614.3043528864,
    "median_actual_mw": 9178.625,
    "morning_ramp_MAE": 248.82480814806613,
    "offpeak_MAE": 258.6035735558604,
    "p90_absolute_error": 574.5093795634918,
    "p95_absolute_error": 721.5416936529132,
    "peak_hour_error_MW": -232.13001246299385,
    "peak_hour_timing_error_hours": 2.276536312849162,
    "price_spike_MAE": null,
    "sMAPE": 0.028145362051772958,
    "signed_daily_energy_error_MWh": -1547.3551054305358,
    "weekday_MAE": 276.6067023847422,
    "weekend_MAE": 243.88026135538894
  },
  "full36": {
    "MAE_0_12h": 241.9714812883899,
    "MAE_0_24h": 247.47784065309156,
    "MAE_0_6h": 231.56099844726782,
    "MAE_24_36h": 283.4621862253336,
    "MAE_full_36h": 259.47262251050665,
    "MAE_percent_of_mean_actual": 2.662712801233653,
    "MAE_percent_of_median_actual": 2.8027359444489175,
    "RMSE_full_36h": 356.4099129603903,
    "bias_full_36h": -65.0829715784946,
    "daily_energy_error_proxy": 3594.4757489211042,
    "mean_actual_mw": 9744.671764461087,
    "median_actual_mw": 9257.833333333332,
    "p90_absolute_error": 552.2839429650962,
    "p90_full_36h": 552.2839429650962,
    "p95_absolute_error": 692.4665322885689,
    "p95_full_36h": 692.4665322885689,
    "peak_hour_error": 6.179775280898877
  },
  "regimes": {
    "cold_high_load": {
      "MAE": 316.42014735330645,
      "RMSE": 405.0441231822262,
      "bias": -157.5962531555307
    },
    "evening_peak": {
      "MAE": 278.845719819708,
      "RMSE": 384.54991713374733,
      "bias": -74.26945762197113
    },
    "holiday": {
      "MAE": 318.12285387852415,
      "RMSE": 402.01347442393956,
      "bias": 56.273506886014125
    },
    "morning_ramp": {
      "MAE": 248.82480814806613,
      "RMSE": 340.5091118578107,
      "bias": 9.317843733367603
    },
    "offpeak": {
      "MAE": 257.33387097231207,
      "RMSE": 344.77189660059673,
      "bias": -120.30398987897425
    },
    "ramp": {
      "MAE": 273.68196310795327,
      "RMSE": 370.46251967372297,
      "bias": -39.83238153263137
    },
    "weekday": {
      "MAE": 276.6067023847422,
      "RMSE": 369.92991162995503,
      "bias": -77.87793255447154
    },
    "weekend": {
      "MAE": 243.88026135538894,
      "RMSE": 352.21278308201016,
      "bias": -29.948648840826877
    }
  },
  "row_counts": {
    "dayahead_selected_rows": 8592,
    "full36_selected_rows": 12816,
    "input_rows": 33582
  }
}
```
