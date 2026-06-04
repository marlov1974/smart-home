# P0053C-B Selected Anchor

Selected anchor: `A1_median_iqr`

Selection rule:

```text
min validation MAE_full_168h over A0-A3, tie-break validation top8_day_precision and top20_168h_precision
```

Validation selected metrics:

```json
{
  "MAE": 0.1850976299870175,
  "MAE_full_168h": 0.1850976299870186,
  "RMSE": 0.36024459143844734,
  "RMSE_full_168h": 0.28533381599391494,
  "best8_168h_precision": 0.2907986111111111,
  "bias": -0.045676026372354336,
  "bias_full_168h": -0.04567602637235451,
  "bottom20_168h_precision": 0.4413194444444442,
  "bottom4_day_precision": 0.505704365079365,
  "correlation": 0.0265049268444313,
  "median_absolute_error": 0.055883166063130624,
  "p90_absolute_error": 0.5570998729956447,
  "p95_absolute_error": 0.9046402357699809,
  "path_count": 144.0,
  "row_count": 24192.0,
  "sMAPE": 1.035371008421124,
  "spearman": 0.11433732871830263,
  "top20_168h_precision": 0.4472222222222222,
  "top4_day_precision": 0.4000496031746033,
  "top8_day_precision": 0.5489831349206347,
  "worst8_168h_precision": 0.3211805555555556
}
```

Holdout selected metrics, report-only:

```json
{
  "MAE": 0.25021924557311376,
  "MAE_full_168h": 0.250219245573114,
  "RMSE": 0.40444815142136514,
  "RMSE_full_168h": 0.32437224839656836,
  "best8_168h_precision": 0.3074712643678161,
  "bias": -0.04168908794300807,
  "bias_full_168h": -0.04168908794300767,
  "bottom20_168h_precision": 0.39971264367816106,
  "bottom4_day_precision": 0.5482348111658458,
  "correlation": 0.5580959276834035,
  "median_absolute_error": 0.11675163104567078,
  "p90_absolute_error": 0.7017761508310183,
  "p95_absolute_error": 0.9032568354136948,
  "path_count": 348.0,
  "row_count": 58464.0,
  "sMAPE": 0.8395566010811096,
  "spearman": 0.5637053097728821,
  "top20_168h_precision": 0.48591954022988487,
  "top4_day_precision": 0.4278530377668309,
  "top8_day_precision": 0.607399425287356,
  "worst8_168h_precision": 0.2543103448275862
}
```
