# P0054J LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "holdout": {
      "MAE": 12.679515980941702,
      "MAE_percent_of_mean_actual": 4.216850905103628,
      "MAE_percent_of_median_actual": 4.45494163657576,
      "R2": 0.8954316833818714,
      "RMSE": 16.341428036544887,
      "bias": 5.23652742149672,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.321063965816307,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 26.77395004193008,
      "p95_absolute_error": 32.34450254674201,
      "row_count": 3872,
      "sMAPE": 0.04146699073785803
    },
    "model_family": "ExtraTrees",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "no_price"
  },
  "HGB_no_price": {
    "holdout": {
      "MAE": 13.042352312888172,
      "MAE_percent_of_mean_actual": 4.337520078680339,
      "MAE_percent_of_median_actual": 4.5824240014294615,
      "R2": 0.8917097471326947,
      "RMSE": 16.62970829968426,
      "bias": 5.530706178916702,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.59879205804394,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 27.49952694045073,
      "p95_absolute_error": 32.67272623519772,
      "row_count": 3872,
      "sMAPE": 0.042997953814874194
    },
    "model_family": "HGB",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "no_price"
  },
  "LightGBM_no_price": {
    "holdout": {
      "MAE": 13.913560205866226,
      "MAE_percent_of_mean_actual": 4.6272593556022565,
      "MAE_percent_of_median_actual": 4.888522461526447,
      "R2": 0.8689612272733375,
      "RMSE": 18.293207302551124,
      "bias": 6.8801757879019005,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.97846926043087,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 28.82841468954768,
      "p95_absolute_error": 36.60485995411749,
      "row_count": 3872,
      "sMAPE": 0.045388839320160995
    },
    "model_family": "LightGBM",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "no_price"
  },
  "XGBoost_no_price": {
    "holdout": {
      "MAE": 12.60041062463637,
      "MAE_percent_of_mean_actual": 4.190542685307534,
      "MAE_percent_of_median_actual": 4.427148008963281,
      "R2": 0.8952531692908221,
      "RMSE": 16.355370745543,
      "bias": 5.302784032884329,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.040031733398422,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 26.622717535351548,
      "p95_absolute_error": 32.27895350263667,
      "row_count": 3872,
      "sMAPE": 0.04117122553821574
    },
    "model_family": "XGBoost",
    "row_set": {
      "features": 68,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "no_price"
  }
}
```
