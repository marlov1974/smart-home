# P0054N LABB

Status: `PASS`

```json
{
  "best_by_dayahead_daily_energy_error": {
    "absolute_daily_energy_error_MWh": 3088.67835726033,
    "model": "HGB_no_price"
  },
  "best_by_dayahead_hourly_MAE": {
    "hourly_MAE_delivery_day": 149.03724768647368,
    "model": "HGB_no_price"
  },
  "best_no_price_by_full36_MAE": {
    "MAE_full_36h": 150.42261836159255,
    "model": "HGB_no_price"
  },
  "best_with_advanced_price_by_full36_MAE": {
    "MAE_full_36h": 153.69412267688818,
    "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
  },
  "dayahead_daily_energy": [
    {
      "absolute_daily_energy_error_MWh": 3088.67835726033,
      "model": "HGB_no_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3172.203896079826,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3470.909572400596,
      "model": "ExtraTrees_no_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3391.7322965928884,
      "model": "ExtraTrees_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3558.7724059296515,
      "model": "LightGBM_no_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3486.9398243426167,
      "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3249.9564757081257,
      "model": "XGBoost_no_price"
    },
    {
      "absolute_daily_energy_error_MWh": 3287.5677984956105,
      "model": "XGBoost_with_p0054n_exact_dayahead_advanced_price"
    }
  ],
  "dayahead_hourly": [
    {
      "hourly_MAE_delivery_day": 149.03724768647368,
      "model": "HGB_no_price"
    },
    {
      "hourly_MAE_delivery_day": 152.9895970386096,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "hourly_MAE_delivery_day": 166.61097844826537,
      "model": "ExtraTrees_no_price"
    },
    {
      "hourly_MAE_delivery_day": 163.74070511715698,
      "model": "ExtraTrees_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "hourly_MAE_delivery_day": 161.20263771340532,
      "model": "LightGBM_no_price"
    },
    {
      "hourly_MAE_delivery_day": 158.00843969271494,
      "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "hourly_MAE_delivery_day": 151.9629052301118,
      "model": "XGBoost_no_price"
    },
    {
      "hourly_MAE_delivery_day": 156.4501914437264,
      "model": "XGBoost_with_p0054n_exact_dayahead_advanced_price"
    }
  ],
  "full36": [
    {
      "MAE_full_36h": 150.42261836159255,
      "model": "HGB_no_price"
    },
    {
      "MAE_full_36h": 153.69412267688818,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_full_36h": 168.61915663873685,
      "model": "ExtraTrees_no_price"
    },
    {
      "MAE_full_36h": 165.21780325752542,
      "model": "ExtraTrees_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_full_36h": 165.29492758744647,
      "model": "LightGBM_no_price"
    },
    {
      "MAE_full_36h": 160.0834829325839,
      "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
    },
    {
      "MAE_full_36h": 153.95677124793977,
      "model": "XGBoost_no_price"
    },
    {
      "MAE_full_36h": 158.5322812237651,
      "model": "XGBoost_with_p0054n_exact_dayahead_advanced_price"
    }
  ]
}
```
