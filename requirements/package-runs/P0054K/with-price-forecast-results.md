# P0054K LABB

Status: `PASS`

```json
{
  "ExtraTrees_with_p0054k_se3_price_forecast": {
    "holdout": {
      "MAE": 52.44091533936922,
      "MAE_percent_of_mean_actual": 2.408517985543475,
      "MAE_percent_of_median_actual": 2.472318394262795,
      "R2": 0.979440496124624,
      "RMSE": 70.4353853730275,
      "bias": -26.642010665059512,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 39.82556915764383,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 116.94634730260275,
      "p95_absolute_error": 145.66472970272724,
      "row_count": 3872,
      "sMAPE": 0.023373329068060743
    },
    "model_family": "ExtraTrees",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "with_p0054k_se3_price_forecast"
  },
  "HGB_with_p0054k_se3_price_forecast": {
    "holdout": {
      "MAE": 59.46934763950201,
      "MAE_percent_of_mean_actual": 2.7313213823853304,
      "MAE_percent_of_median_actual": 2.8036726878710896,
      "R2": 0.9746459237845694,
      "RMSE": 78.2183185321131,
      "bias": -23.547141387996234,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 46.54507919595744,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 129.36704573175174,
      "p95_absolute_error": 159.79727798212178,
      "row_count": 3872,
      "sMAPE": 0.027053051557974373
    },
    "model_family": "HGB",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "with_p0054k_se3_price_forecast"
  },
  "LightGBM_with_p0054k_se3_price_forecast": {
    "holdout": {
      "MAE": 48.3202873218118,
      "MAE_percent_of_mean_actual": 2.2192648684345397,
      "MAE_percent_of_median_actual": 2.2780520589443927,
      "R2": 0.9820410420603627,
      "RMSE": 65.83019575843156,
      "bias": -19.640548955998185,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 36.32596306671678,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 102.80545923331802,
      "p95_absolute_error": 132.15649436582382,
      "row_count": 3872,
      "sMAPE": 0.021527496910828777
    },
    "model_family": "LightGBM",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "with_p0054k_se3_price_forecast"
  },
  "XGBoost_with_p0054k_se3_price_forecast": {
    "holdout": {
      "MAE": 48.491100583964595,
      "MAE_percent_of_mean_actual": 2.227110017806971,
      "MAE_percent_of_median_actual": 2.2861050223084276,
      "R2": 0.9822673567433271,
      "RMSE": 65.4140921517535,
      "bias": -26.03603421310039,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 37.40248583203129,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 104.45251459375,
      "p95_absolute_error": 134.55523291093738,
      "row_count": 3872,
      "sMAPE": 0.021655323495092568
    },
    "model_family": "XGBoost",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "with_p0054k_se3_price_forecast"
  }
}
```
