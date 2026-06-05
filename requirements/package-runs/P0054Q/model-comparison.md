# P0054Q LABB

Status: `PASS`

```json
{
  "best_by_dayahead_daily_energy_error": {
    "absolute_daily_energy_error_MWh": 12862.665916660333,
    "daily_energy_error_percent_of_actual": 5.28283705993215,
    "day_count": 347,
    "model": "HGB_no_price",
    "signed_daily_energy_error_MWh": -5862.984144686694
  },
  "best_by_dayahead_hourly_MAE": {
    "MAE_percent_of_mean_actual": 6.549820972573629,
    "hourly_MAE_delivery_day": 632.7869013389628,
    "model": "LightGBM_no_price"
  },
  "best_no_price_by_full36_MAE": {
    "MAE_full_36h": 644.9873394113744,
    "MAE_percent_of_mean_actual": 6.585759056659982,
    "model": "LightGBM_no_price"
  },
  "best_with_advanced_price_by_full36_MAE": {
    "MAE_full_36h": 671.7222528712044,
    "MAE_percent_of_mean_actual": 6.858740691629407,
    "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
  },
  "dayahead_daily_energy": [
    {
      "absolute_daily_energy_error_MWh": 12862.665916660333,
      "daily_energy_error_percent_of_actual": 5.28283705993215,
      "day_count": 347,
      "model": "HGB_no_price",
      "signed_daily_energy_error_MWh": -5862.984144686694
    },
    {
      "absolute_daily_energy_error_MWh": 13536.985314235897,
      "daily_energy_error_percent_of_actual": 5.526520032298043,
      "day_count": 347,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price",
      "signed_daily_energy_error_MWh": -6996.2168259430055
    },
    {
      "absolute_daily_energy_error_MWh": 13475.538430293265,
      "daily_energy_error_percent_of_actual": 5.48783190879411,
      "day_count": 347,
      "model": "ExtraTrees_no_price",
      "signed_daily_energy_error_MWh": -6186.696048863144
    },
    {
      "absolute_daily_energy_error_MWh": 13642.463421368871,
      "daily_energy_error_percent_of_actual": 5.493425925793163,
      "day_count": 347,
      "model": "ExtraTrees_with_p0054n_exact_dayahead_advanced_price",
      "signed_daily_energy_error_MWh": -6579.428092467435
    },
    {
      "absolute_daily_energy_error_MWh": 13056.708339736175,
      "daily_energy_error_percent_of_actual": 5.3759869307074295,
      "day_count": 347,
      "model": "LightGBM_no_price",
      "signed_daily_energy_error_MWh": -6324.247144480078
    },
    {
      "absolute_daily_energy_error_MWh": 13905.479237984544,
      "daily_energy_error_percent_of_actual": 5.684368983592343,
      "day_count": 347,
      "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price",
      "signed_daily_energy_error_MWh": -7409.336488845436
    },
    {
      "absolute_daily_energy_error_MWh": 13096.229517047164,
      "daily_energy_error_percent_of_actual": 5.344598700349216,
      "day_count": 347,
      "model": "XGBoost_no_price",
      "signed_daily_energy_error_MWh": -6931.4644661646
    },
    {
      "absolute_daily_energy_error_MWh": 13843.741293021285,
      "daily_energy_error_percent_of_actual": 5.601152758762247,
      "day_count": 347,
      "model": "XGBoost_with_p0054n_exact_dayahead_advanced_price",
      "signed_daily_energy_error_MWh": -7653.6702563077915
    }
  ],
  "dayahead_hourly": [
    {
      "MAE_percent_of_mean_actual": 6.562125069472757,
      "hourly_MAE_delivery_day": 633.9756164783805,
      "model": "HGB_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 6.810563195012913,
      "hourly_MAE_delivery_day": 657.9775536753361,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_percent_of_mean_actual": 7.061326130067322,
      "hourly_MAE_delivery_day": 682.2040938064617,
      "model": "ExtraTrees_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 7.1007662870849195,
      "hourly_MAE_delivery_day": 686.0144597465375,
      "model": "ExtraTrees_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_percent_of_mean_actual": 6.549820972573629,
      "hourly_MAE_delivery_day": 632.7869013389628,
      "model": "LightGBM_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 6.793505854138917,
      "hourly_MAE_delivery_day": 656.3296213239123,
      "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_percent_of_mean_actual": 6.563194175073583,
      "hourly_MAE_delivery_day": 634.078904190088,
      "model": "XGBoost_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 6.89146694964973,
      "hourly_MAE_delivery_day": 665.7937728388355,
      "model": "XGBoost_with_p0054n_exact_dayahead_advanced_price"
    }
  ],
  "full36": [
    {
      "MAE_full_36h": 650.4293204412376,
      "MAE_percent_of_mean_actual": 6.641325381242881,
      "model": "HGB_no_price"
    },
    {
      "MAE_full_36h": 676.7427455267633,
      "MAE_percent_of_mean_actual": 6.9100033334750846,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_full_36h": 694.1610644264334,
      "MAE_percent_of_mean_actual": 7.08785620660277,
      "model": "ExtraTrees_no_price"
    },
    {
      "MAE_full_36h": 692.4397779933969,
      "MAE_percent_of_mean_actual": 7.070280702367568,
      "model": "ExtraTrees_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_full_36h": 644.9873394113744,
      "MAE_percent_of_mean_actual": 6.585759056659982,
      "model": "LightGBM_no_price"
    },
    {
      "MAE_full_36h": 671.7222528712044,
      "MAE_percent_of_mean_actual": 6.858740691629407,
      "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_full_36h": 648.0211775938925,
      "MAE_percent_of_mean_actual": 6.616736606242883,
      "model": "XGBoost_no_price"
    },
    {
      "MAE_full_36h": 683.0284216904856,
      "MAE_percent_of_mean_actual": 6.974184358734037,
      "model": "XGBoost_with_p0054n_exact_dayahead_advanced_price"
    }
  ],
  "workplace_reference_percent_error": "roughly 3-4 percent; P0054Q remains LABB because weather is actual_as_forecast_proxy"
}
```
