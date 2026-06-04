# P0054H validation/holdout comparison to P0053C-B

```json
{
  "available": true,
  "mae_full_168h_delta_p0054h_minus_p0053cb": {
    "holdout": 0.04570666444785437,
    "validate": 0.06588332694089136
  },
  "p0053cb_metrics": {
    "holdout": {
      "MAE": 0.25021924557311376,
      "MAE_full_168h": 0.250219245573114,
      "RMSE": 0.40444815142136514,
      "bias": -0.04168908794300807,
      "bottom20_168h_precision": 0.39971264367816106,
      "median_absolute_error": 0.11675163104567078,
      "p90_absolute_error": 0.7017761508310183,
      "p95_absolute_error": 0.9032568354136948,
      "path_count": 348.0,
      "row_count": 58464.0,
      "sMAPE": 0.8395566010811096,
      "spearman": 0.5637053097728821,
      "top20_168h_precision": 0.48591954022988487,
      "top8_day_precision": 0.607399425287356
    },
    "validate": {
      "MAE": 0.1850976299870175,
      "MAE_full_168h": 0.1850976299870186,
      "RMSE": 0.36024459143844734,
      "bias": -0.045676026372354336,
      "bottom20_168h_precision": 0.4413194444444442,
      "median_absolute_error": 0.055883166063130624,
      "p90_absolute_error": 0.5570998729956447,
      "p95_absolute_error": 0.9046402357699809,
      "path_count": 144.0,
      "row_count": 24192.0,
      "sMAPE": 1.035371008421124,
      "spearman": 0.11433732871830263,
      "top20_168h_precision": 0.4472222222222222,
      "top8_day_precision": 0.5489831349206347
    }
  },
  "p0053cb_table": "m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1",
  "p0054h_metrics": {
    "holdout": {
      "MAE": 0.2959259100209702,
      "MAE_full_168h": 0.29592591002096835,
      "RMSE": 0.4776910226818078,
      "bias": -0.010375605045995879,
      "bottom20_168h_precision": 0.20610795454545452,
      "median_absolute_error": 0.14341500000000004,
      "p90_absolute_error": 0.80691125,
      "p95_absolute_error": 1.0702725000000002,
      "path_count": 352.0,
      "row_count": 59136.0,
      "sMAPE": 0.9397087102779336,
      "spearman": 0.46206338585925777,
      "top20_168h_precision": 0.15213068181818182,
      "top8_day_precision": 0.49457183441558444
    },
    "validate": {
      "MAE": 0.2509809569279067,
      "MAE_full_168h": 0.25098095692790995,
      "RMSE": 0.4573020277213024,
      "bias": 0.002706062748016034,
      "bottom20_168h_precision": 0.1840277777777778,
      "median_absolute_error": 0.08135,
      "p90_absolute_error": 0.79569,
      "p95_absolute_error": 1.16054,
      "path_count": 144.0,
      "row_count": 24192.0,
      "sMAPE": 1.1872632850260196,
      "spearman": -0.02413824066986483,
      "top20_168h_precision": 0.12569444444444453,
      "top8_day_precision": 0.431919642857143
    }
  }
}
```
