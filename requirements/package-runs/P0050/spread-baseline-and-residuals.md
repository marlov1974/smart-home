# P0050 spread baseline and residuals

selected_baseline = `B2_smoothed_hour_daytype_dayofyear`

Validation/holdout metrics:

```json
{
  "holdout": {
    "B0_hour_weekday": {
      "MAE": 0.24416744540229846,
      "RMSE": 0.3628414866845199,
      "bias": -0.22754565660919548,
      "median_absolute_error": 0.15353999999999987,
      "p90_absolute_error": 0.5978452500000001,
      "p95_absolute_error": 0.7501522499999975,
      "spearman": 0.2152243342328329
    },
    "B1_hour_daytype_season": {
      "MAE": 0.24373314080459735,
      "RMSE": 0.3528463422273885,
      "bias": -0.1974856537356322,
      "median_absolute_error": 0.16776375000000007,
      "p90_absolute_error": 0.5729582499999999,
      "p95_absolute_error": 0.7327687499999997,
      "spearman": 0.1376846272706451
    },
    "B2_smoothed_hour_daytype_dayofyear": {
      "MAE": 0.2393790109554596,
      "RMSE": 0.3451423354954789,
      "bias": -0.19570436203304611,
      "median_absolute_error": 0.1626996875,
      "p90_absolute_error": 0.5608985,
      "p95_absolute_error": 0.7122306249999999,
      "spearman": 0.12981223794127048
    }
  },
  "train": {
    "B0_hour_weekday": {
      "MAE": 0.2855269592573019,
      "RMSE": 0.8089095271942501,
      "bias": -0.28021684574093964,
      "median_absolute_error": 0.0,
      "p90_absolute_error": 0.906695,
      "p95_absolute_error": 1.6852119999999982,
      "spearman": 0.31891357658914493
    },
    "B1_hour_daytype_season": {
      "MAE": 0.28036215065117653,
      "RMSE": 0.7913487392012148,
      "bias": -0.2504006085005275,
      "median_absolute_error": 0.0,
      "p90_absolute_error": 0.8422335,
      "p95_absolute_error": 1.6272314999999968,
      "spearman": 0.3574139143439461
    },
    "B2_smoothed_hour_daytype_dayofyear": {
      "MAE": 0.279310687010514,
      "RMSE": 0.7742939834242302,
      "bias": -0.24054690871942172,
      "median_absolute_error": 0.0,
      "p90_absolute_error": 0.8126637999999997,
      "p95_absolute_error": 1.6072529937499995,
      "spearman": 0.40982178358932264
    }
  },
  "validate": {
    "B0_hour_weekday": {
      "MAE": 0.3280611475456618,
      "RMSE": 0.5013797050518705,
      "bias": -0.3225899940068486,
      "median_absolute_error": 0.24537000000000003,
      "p90_absolute_error": 0.787753,
      "p95_absolute_error": 1.0750154999999992,
      "spearman": 0.020793529199153758
    },
    "B1_hour_daytype_season": {
      "MAE": 0.3130066384132422,
      "RMSE": 0.4759057619839441,
      "bias": -0.2928628079337892,
      "median_absolute_error": 0.23586999999999997,
      "p90_absolute_error": 0.739782,
      "p95_absolute_error": 1.0028339999999998,
      "spearman": 0.13322656465340477
    },
    "B2_smoothed_hour_daytype_dayofyear": {
      "MAE": 0.30832445072773873,
      "RMSE": 0.4693890840982231,
      "bias": -0.28211166297088897,
      "median_absolute_error": 0.22792412499999998,
      "p90_absolute_error": 0.7353228250000002,
      "p95_absolute_error": 0.9997007874999991,
      "spearman": 0.20988089647205246
    }
  }
}
```
