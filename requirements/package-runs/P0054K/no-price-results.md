# P0054K LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "holdout": {
      "MAE": 51.653732379500475,
      "MAE_percent_of_mean_actual": 2.372364072048875,
      "MAE_percent_of_median_actual": 2.435206782103869,
      "R2": 0.9798100898264168,
      "RMSE": 69.79941347496245,
      "bias": -26.407633684929507,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 39.22614804914747,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 113.84100570819197,
      "p95_absolute_error": 146.5574300292641,
      "row_count": 3872,
      "sMAPE": 0.02299234207714176
    },
    "model_family": "ExtraTrees",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "no_price"
  },
  "HGB_no_price": {
    "holdout": {
      "MAE": 60.14168733217584,
      "MAE_percent_of_mean_actual": 2.7622007488441382,
      "MAE_percent_of_median_actual": 2.835370032942841,
      "R2": 0.971819558165142,
      "RMSE": 82.46287630212083,
      "bias": -20.249118510849133,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 45.59222650028971,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 127.6168175378815,
      "p95_absolute_error": 160.89930450403244,
      "row_count": 3872,
      "sMAPE": 0.027103062688297676
    },
    "model_family": "HGB",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "no_price"
  },
  "LightGBM_no_price": {
    "holdout": {
      "MAE": 50.19482007339829,
      "MAE_percent_of_mean_actual": 2.305358824222091,
      "MAE_percent_of_median_actual": 2.366426599556503,
      "R2": 0.9767462544571661,
      "RMSE": 74.90848915867915,
      "bias": -13.568610214510917,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 36.69772846648766,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 103.11090662543596,
      "p95_absolute_error": 135.28663368038403,
      "row_count": 3872,
      "sMAPE": 0.022012910813485494
    },
    "model_family": "LightGBM",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "no_price"
  },
  "XGBoost_no_price": {
    "holdout": {
      "MAE": 48.01602472809628,
      "MAE_percent_of_mean_actual": 2.2052906285771785,
      "MAE_percent_of_median_actual": 2.2637076486254473,
      "R2": 0.9825497950076403,
      "RMSE": 64.89105671167339,
      "bias": -26.267043830425084,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 37.12401841796884,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 101.84733307968742,
      "p95_absolute_error": 132.36646845859386,
      "row_count": 3872,
      "sMAPE": 0.02141425912647329
    },
    "model_family": "XGBoost",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11935
    },
    "variant": "no_price"
  }
}
```
