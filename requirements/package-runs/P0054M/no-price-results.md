# P0054M LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "holdout": {
      "MAE": 144.69949632494485,
      "MAE_percent_of_mean_actual": 6.645790546223973,
      "MAE_percent_of_median_actual": 6.821834136372379,
      "R2": 0.839879593592856,
      "RMSE": 196.5657834864121,
      "bias": -56.77953632578941,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 102.84261962996402,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 316.4838200232464,
      "p95_absolute_error": 419.55590694114017,
      "row_count": 3872,
      "sMAPE": 0.0652602710910236
    },
    "model_family": "ExtraTrees",
    "row_set": {
      "features": 60,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "no_price"
  },
  "HGB_no_price": {
    "holdout": {
      "MAE": 183.5473101816055,
      "MAE_percent_of_mean_actual": 8.430001553360404,
      "MAE_percent_of_median_actual": 8.653307979900344,
      "R2": 0.7401764521829997,
      "RMSE": 250.39395169321017,
      "bias": -99.44483449545804,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 123.05659915056174,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 439.44035487386674,
      "p95_absolute_error": 560.6330427025478,
      "row_count": 3872,
      "sMAPE": 0.08168694968920148
    },
    "model_family": "HGB",
    "row_set": {
      "features": 60,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "no_price"
  },
  "LightGBM_no_price": {
    "holdout": {
      "MAE": 187.22555827648063,
      "MAE_percent_of_mean_actual": 8.598936947307406,
      "MAE_percent_of_median_actual": 8.826718385969187,
      "R2": 0.7215985751424847,
      "RMSE": 259.1912324289509,
      "bias": -105.2024952670463,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 118.85671382823034,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 465.69240140772797,
      "p95_absolute_error": 597.6198948415304,
      "row_count": 3872,
      "sMAPE": 0.08315378310544934
    },
    "model_family": "LightGBM",
    "row_set": {
      "features": 60,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "no_price"
  },
  "XGBoost_no_price": {
    "holdout": {
      "MAE": 154.77299216360825,
      "MAE_percent_of_mean_actual": 7.108448296335815,
      "MAE_percent_of_median_actual": 7.296747453489106,
      "R2": 0.8087336913253345,
      "RMSE": 214.8343974157444,
      "bias": -85.89339476920637,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 100.43879791406255,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 370.7461239890624,
      "p95_absolute_error": 479.28224109765574,
      "row_count": 3872,
      "sMAPE": 0.06938933159559088
    },
    "model_family": "XGBoost",
    "row_set": {
      "features": 60,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "no_price"
  }
}
```
