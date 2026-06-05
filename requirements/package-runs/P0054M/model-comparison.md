# P0054M LABB

Status: `PASS`

```json
{
  "best_no_price_by_holdout_MAE": {
    "holdout_MAE": 144.69949632494485,
    "model": "ExtraTrees_no_price"
  },
  "best_no_price_by_weekly_MAE_full_168h": {
    "model": "XGBoost_no_price",
    "weekly_MAE_full_168h": 213.72331614362525
  },
  "best_with_advanced_price_by_holdout_MAE": {
    "holdout_MAE": 140.54830097681355,
    "model": "ExtraTrees_with_p0054l2_ensemble_price_forecast"
  },
  "best_with_advanced_price_by_weekly_MAE_full_168h": {
    "model": "XGBoost_with_p0054l2_ensemble_price_forecast",
    "weekly_MAE_full_168h": 206.2574365420684
  },
  "direct_holdout": [
    {
      "holdout_MAE": 183.5473101816055,
      "model": "HGB_no_price"
    },
    {
      "holdout_MAE": 183.7926532645518,
      "model": "HGB_with_p0054l2_ensemble_price_forecast"
    },
    {
      "holdout_MAE": 144.69949632494485,
      "model": "ExtraTrees_no_price"
    },
    {
      "holdout_MAE": 140.54830097681355,
      "model": "ExtraTrees_with_p0054l2_ensemble_price_forecast"
    },
    {
      "holdout_MAE": 187.22555827648063,
      "model": "LightGBM_no_price"
    },
    {
      "holdout_MAE": 177.17913389860513,
      "model": "LightGBM_with_p0054l2_ensemble_price_forecast"
    },
    {
      "holdout_MAE": 154.77299216360825,
      "model": "XGBoost_no_price"
    },
    {
      "holdout_MAE": 148.0499748921278,
      "model": "XGBoost_with_p0054l2_ensemble_price_forecast"
    }
  ],
  "weekly_168h": [
    {
      "model": "HGB_no_price",
      "weekly_MAE_full_168h": 260.3336081158239
    },
    {
      "model": "HGB_with_p0054l2_ensemble_price_forecast",
      "weekly_MAE_full_168h": 254.03817469365512
    },
    {
      "model": "ExtraTrees_no_price",
      "weekly_MAE_full_168h": 230.9739024433725
    },
    {
      "model": "ExtraTrees_with_p0054l2_ensemble_price_forecast",
      "weekly_MAE_full_168h": 223.4480812536409
    },
    {
      "model": "LightGBM_no_price",
      "weekly_MAE_full_168h": 263.84906818301783
    },
    {
      "model": "LightGBM_with_p0054l2_ensemble_price_forecast",
      "weekly_MAE_full_168h": 255.67817133888175
    },
    {
      "model": "XGBoost_no_price",
      "weekly_MAE_full_168h": 213.72331614362525
    },
    {
      "model": "XGBoost_with_p0054l2_ensemble_price_forecast",
      "weekly_MAE_full_168h": 206.2574365420684
    }
  ]
}
```
