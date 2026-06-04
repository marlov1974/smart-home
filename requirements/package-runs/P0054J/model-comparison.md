# P0054J LABB

Status: `PASS`

```json
{
  "best_no_price_by_holdout_MAE": {
    "holdout_MAE": 12.60041062463637,
    "model": "XGBoost_no_price"
  },
  "best_no_price_by_weekly_MAE_full_168h": {
    "model": "XGBoost_no_price",
    "weekly_MAE_full_168h": 13.831126605961474
  },
  "best_with_price_by_holdout_MAE": {
    "holdout_MAE": 12.585281377945856,
    "model": "XGBoost_with_p0054h_price_forecast"
  },
  "best_with_price_by_weekly_MAE_full_168h": {
    "model": "XGBoost_with_p0054h_price_forecast",
    "weekly_MAE_full_168h": 13.650342019254719
  },
  "direct_holdout": [
    {
      "holdout_MAE": 13.042352312888172,
      "model": "HGB_no_price"
    },
    {
      "holdout_MAE": 13.158787331721099,
      "model": "HGB_with_p0054h_price_forecast"
    },
    {
      "holdout_MAE": 12.679515980941702,
      "model": "ExtraTrees_no_price"
    },
    {
      "holdout_MAE": 12.69214947503782,
      "model": "ExtraTrees_with_p0054h_price_forecast"
    },
    {
      "holdout_MAE": 13.913560205866226,
      "model": "LightGBM_no_price"
    },
    {
      "holdout_MAE": 13.770280143260758,
      "model": "LightGBM_with_p0054h_price_forecast"
    },
    {
      "holdout_MAE": 12.60041062463637,
      "model": "XGBoost_no_price"
    },
    {
      "holdout_MAE": 12.585281377945856,
      "model": "XGBoost_with_p0054h_price_forecast"
    }
  ],
  "weekly_168h": [
    {
      "model": "HGB_no_price",
      "weekly_MAE_full_168h": 14.668238986296489
    },
    {
      "model": "HGB_with_p0054h_price_forecast",
      "weekly_MAE_full_168h": 14.34193300676965
    },
    {
      "model": "ExtraTrees_no_price",
      "weekly_MAE_full_168h": 14.15633798981931
    },
    {
      "model": "ExtraTrees_with_p0054h_price_forecast",
      "weekly_MAE_full_168h": 14.087739965590865
    },
    {
      "model": "LightGBM_no_price",
      "weekly_MAE_full_168h": 14.884969765383296
    },
    {
      "model": "LightGBM_with_p0054h_price_forecast",
      "weekly_MAE_full_168h": 14.764305508844332
    },
    {
      "model": "XGBoost_no_price",
      "weekly_MAE_full_168h": 13.831126605961474
    },
    {
      "model": "XGBoost_with_p0054h_price_forecast",
      "weekly_MAE_full_168h": 13.650342019254719
    }
  ]
}
```
