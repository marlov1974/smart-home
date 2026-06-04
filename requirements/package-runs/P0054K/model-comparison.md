# P0054K LABB

Status: `PASS`

```json
{
  "best_no_price_by_holdout_MAE": {
    "holdout_MAE": 48.01602472809628,
    "model": "XGBoost_no_price"
  },
  "best_no_price_by_weekly_MAE_full_168h": {
    "model": "XGBoost_no_price",
    "weekly_MAE_full_168h": 108.51610764072525
  },
  "best_with_price_by_holdout_MAE": {
    "holdout_MAE": 48.3202873218118,
    "model": "LightGBM_with_p0054k_se3_price_forecast"
  },
  "best_with_price_by_weekly_MAE_full_168h": {
    "model": "XGBoost_with_p0054k_se3_price_forecast",
    "weekly_MAE_full_168h": 109.81910335762592
  },
  "direct_holdout": [
    {
      "holdout_MAE": 60.14168733217584,
      "model": "HGB_no_price"
    },
    {
      "holdout_MAE": 59.46934763950201,
      "model": "HGB_with_p0054k_se3_price_forecast"
    },
    {
      "holdout_MAE": 51.653732379500475,
      "model": "ExtraTrees_no_price"
    },
    {
      "holdout_MAE": 52.44091533936922,
      "model": "ExtraTrees_with_p0054k_se3_price_forecast"
    },
    {
      "holdout_MAE": 50.19482007339829,
      "model": "LightGBM_no_price"
    },
    {
      "holdout_MAE": 48.3202873218118,
      "model": "LightGBM_with_p0054k_se3_price_forecast"
    },
    {
      "holdout_MAE": 48.01602472809628,
      "model": "XGBoost_no_price"
    },
    {
      "holdout_MAE": 48.491100583964595,
      "model": "XGBoost_with_p0054k_se3_price_forecast"
    }
  ],
  "weekly_168h": [
    {
      "model": "HGB_no_price",
      "weekly_MAE_full_168h": 139.69562531377375
    },
    {
      "model": "HGB_with_p0054k_se3_price_forecast",
      "weekly_MAE_full_168h": 140.01017318713457
    },
    {
      "model": "ExtraTrees_no_price",
      "weekly_MAE_full_168h": 133.9244361545914
    },
    {
      "model": "ExtraTrees_with_p0054k_se3_price_forecast",
      "weekly_MAE_full_168h": 136.27570932382733
    },
    {
      "model": "LightGBM_no_price",
      "weekly_MAE_full_168h": 136.84047230038857
    },
    {
      "model": "LightGBM_with_p0054k_se3_price_forecast",
      "weekly_MAE_full_168h": 132.89188052486935
    },
    {
      "model": "XGBoost_no_price",
      "weekly_MAE_full_168h": 108.51610764072525
    },
    {
      "model": "XGBoost_with_p0054k_se3_price_forecast",
      "weekly_MAE_full_168h": 109.81910335762592
    }
  ]
}
```
