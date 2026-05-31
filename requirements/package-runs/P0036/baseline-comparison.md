# P0036 baseline comparison

Primary fair baseline is `train_only_M1_m3ab_normalized`.

| variant | target | MAE | RMSE |
|---|---|---:|---:|
| P0036_HGB_residual | system_proxy_se1 | 0.394878 | 0.512292 |
| P0036_HGB_residual | area_diff_proxy_se3 | 0.220307 | 0.304649 |
| P0036_HGB_residual | recomposed_se3 | 0.377318 | 0.488575 |
| train_only_M1_m3ab_normalized | system_proxy_se1 | 0.382156 | 0.493545 |
| train_only_M1_m3ab_normalized | area_diff_proxy_se3 | 0.241108 | 0.350126 |
| train_only_M1_m3ab_normalized | recomposed_se3 | 0.402603 | 0.520408 |
| train_only_M1_raw_actual | system_proxy_se1 | 0.400824 | 0.507047 |
| train_only_M1_raw_actual | area_diff_proxy_se3 | 0.241958 | 0.350864 |
| train_only_M1_raw_actual | recomposed_se3 | 0.401715 | 0.520428 |
| full_period_M1_existing | system_proxy_se1 | 0.336856 | 0.476429 |
| full_period_M1_existing | area_diff_proxy_se3 | 0.202791 | 0.293229 |
| full_period_M1_existing | recomposed_se3 | 0.383175 | 0.497192 |

Historical reference from committed evidence:

| reference | system_proxy_se1 MAE | area_diff_proxy_se3 MAE | recomposed_se3 MAE | note |
|---|---:|---:|---:|---|
| P0034 M4 | see `requirements/package-runs/P0034/holdout-results.md` | see evidence | see evidence | pre-P0035 model |
| P0035 M4 | 0.6079521874402215 | 1.8269617292981122 | 1.6662037682642874 | polynomial Ridge residual blow-up |
