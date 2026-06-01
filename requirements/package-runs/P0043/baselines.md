# P0043 baselines

| target | baseline | val_MAE | holdout_MAE | holdout_spearman | top3 | bottom3 |
|---|---|---:|---:|---:|---:|---:|
| system_proxy_se1 | B0_flat_day | 0.715288 | 0.600354 | 0.181049 | 0.057471 | 0.308046 |
| system_proxy_se1 | B1_hour_of_day_mean | 0.643855 | 0.517274 | 0.481289 | 0.312644 | 0.291954 |
| system_proxy_se1 | B2_hour_weekday_mean | 0.628304 | 0.511452 | 0.510927 | 0.379310 | 0.324138 |
| system_proxy_se1 | B3_hour_weekday_season_smooth | 0.623449 | 0.474612 | 0.586519 | 0.351724 | 0.365517 |
| area_diff_proxy_se3 | B0_flat_day | 0.587855 | 0.510112 | 0.096816 | 0.103448 | 0.089655 |
| area_diff_proxy_se3 | B1_hour_of_day_mean | 0.537015 | 0.520900 | 0.175526 | 0.340230 | 0.096552 |
| area_diff_proxy_se3 | B2_hour_weekday_mean | 0.529146 | 0.524220 | 0.168834 | 0.289655 | 0.091954 |
| area_diff_proxy_se3 | B3_hour_weekday_season_smooth | 0.508146 | 0.484328 | 0.348546 | 0.356322 | 0.195402 |
