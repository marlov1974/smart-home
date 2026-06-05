# P0054M LABB

Status: `PASS`

```json
{
  "ExtraTrees_with_p0054l2_ensemble_price_forecast": {
    "holdout": {
      "MAE": 140.54830097681355,
      "MAE_percent_of_mean_actual": 6.455133525979846,
      "MAE_percent_of_median_actual": 6.626126709243274,
      "R2": 0.8477737808862722,
      "RMSE": 191.6590408008817,
      "bias": -51.83512627857178,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 99.97650888387398,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 313.22611658026887,
      "p95_absolute_error": 400.9503516606546,
      "row_count": 3872,
      "sMAPE": 0.06322633689106091
    },
    "model_family": "ExtraTrees",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "with_p0054l2_ensemble_price_forecast"
  },
  "HGB_with_p0054l2_ensemble_price_forecast": {
    "holdout": {
      "MAE": 183.7926532645518,
      "MAE_percent_of_mean_actual": 8.441269724865052,
      "MAE_percent_of_median_actual": 8.664874639500923,
      "R2": 0.7400643267737388,
      "RMSE": 250.44797392529838,
      "bias": -99.12079396387567,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 121.56716764272801,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 439.3945604388207,
      "p95_absolute_error": 559.8892123236728,
      "row_count": 3872,
      "sMAPE": 0.08195946278391447
    },
    "model_family": "HGB",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "with_p0054l2_ensemble_price_forecast"
  },
  "LightGBM_with_p0054l2_ensemble_price_forecast": {
    "holdout": {
      "MAE": 177.17913389860513,
      "MAE_percent_of_mean_actual": 8.137522541248211,
      "MAE_percent_of_median_actual": 8.353081348452701,
      "R2": 0.7455902760283165,
      "RMSE": 247.77154748261512,
      "bias": -94.23003448968477,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 111.92291663390597,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 450.56794015721704,
      "p95_absolute_error": 554.241393151829,
      "row_count": 3872,
      "sMAPE": 0.0781779109957593
    },
    "model_family": "LightGBM",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "with_p0054l2_ensemble_price_forecast"
  },
  "XGBoost_with_p0054l2_ensemble_price_forecast": {
    "holdout": {
      "MAE": 148.0499748921278,
      "MAE_percent_of_mean_actual": 6.799672068638587,
      "MAE_percent_of_median_actual": 6.9797919015567516,
      "R2": 0.826044747180916,
      "RMSE": 204.8817870718837,
      "bias": -79.48815607382542,
      "mean_actual_mw": 2177.3105143549956,
      "median_absolute_error": 97.50328729296871,
      "median_actual_mw": 2121.1230503750003,
      "p90_absolute_error": 347.9901786031247,
      "p95_absolute_error": 463.5850670117188,
      "row_count": 3872,
      "sMAPE": 0.0663963739561295
    },
    "model_family": "XGBoost",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 966
    },
    "variant": "with_p0054l2_ensemble_price_forecast"
  }
}
```
