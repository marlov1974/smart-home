# P0054J LABB

Status: `PASS`

```json
{
  "ExtraTrees_with_p0054h_price_forecast": {
    "holdout": {
      "MAE": 12.69214947503782,
      "MAE_percent_of_mean_actual": 4.221052450422385,
      "MAE_percent_of_median_actual": 4.459380408445981,
      "R2": 0.8947304720963791,
      "RMSE": 16.3961274342979,
      "bias": 5.489239284763508,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.408475418431095,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 26.85295056068494,
      "p95_absolute_error": 32.07463345255516,
      "row_count": 3872,
      "sMAPE": 0.04144595872574155
    },
    "model_family": "ExtraTrees",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "with_p0054h_price_forecast"
  },
  "HGB_with_p0054h_price_forecast": {
    "holdout": {
      "MAE": 13.158787331721099,
      "MAE_percent_of_mean_actual": 4.3762430958120175,
      "MAE_percent_of_median_actual": 4.623333387413434,
      "R2": 0.8898068931122218,
      "RMSE": 16.775178942172705,
      "bias": 6.730232663074857,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.670396418863291,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 27.486725685695443,
      "p95_absolute_error": 33.14345927081095,
      "row_count": 3872,
      "sMAPE": 0.0435757897972173
    },
    "model_family": "HGB",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "with_p0054h_price_forecast"
  },
  "LightGBM_with_p0054h_price_forecast": {
    "holdout": {
      "MAE": 13.770280143260758,
      "MAE_percent_of_mean_actual": 4.579608430867486,
      "MAE_percent_of_median_actual": 4.8381810827583855,
      "R2": 0.8730149016970057,
      "RMSE": 18.008035046505842,
      "bias": 7.412060855085233,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 11.106316355512519,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 29.042610297205524,
      "p95_absolute_error": 35.16906510803116,
      "row_count": 3872,
      "sMAPE": 0.045274252919241746
    },
    "model_family": "LightGBM",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "with_p0054h_price_forecast"
  },
  "XGBoost_with_p0054h_price_forecast": {
    "holdout": {
      "MAE": 12.585281377945856,
      "MAE_percent_of_mean_actual": 4.185511122770264,
      "MAE_percent_of_median_actual": 4.421832355659723,
      "R2": 0.8958545417274755,
      "RMSE": 16.308353442509006,
      "bias": 5.345642062084347,
      "mean_actual_mw": 300.68684585446846,
      "median_absolute_error": 10.022129845703134,
      "median_actual_mw": 284.61688200000003,
      "p90_absolute_error": 26.951506131445306,
      "p95_absolute_error": 32.832194238476575,
      "row_count": 3872,
      "sMAPE": 0.04109020690182508
    },
    "model_family": "XGBoost",
    "row_set": {
      "features": 76,
      "holdout": 3872,
      "train_fit": 11858
    },
    "variant": "with_p0054h_price_forecast"
  }
}
```
