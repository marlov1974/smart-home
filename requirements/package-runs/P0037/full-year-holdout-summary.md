# P0037 full-year holdout summary

Status: WARN

```text
train = 2022-05-30..2023-12-31
validate = 2024-01-01..2024-12-31
holdout = 2025-01-01..2025-12-31
train_rows = 13945
validate_rows = 8784
holdout_rows = 8760
strict_no_leakage = M1/M2/M3A/M3B/M4 fit without 2025 holdout rows
m3a_weather_mode = observed-weather diagnostic attribution only; no M5 forecast claim
```

## structural target mode

| holdout_year | target_mode | variant | target | MAE | RMSE | MAE_delta_vs_M1 | RMSE_delta_vs_M1 | MAE_delta_vs_previous_variant | winner_or_status |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 2025 | structural | M1 | system_proxy_se1 | 0.362448 | 0.461737 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | structural | M1 | area_diff_proxy_se3 | 0.324534 | 0.488748 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | structural | M1 | recomposed_se3 | 0.376549 | 0.512052 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | structural | M1+M4 | system_proxy_se1 | 0.363589 | 0.455624 | 0.001141 | -0.006114 | 0.001141 | not_better_than_M1 |
| 2025 | structural | M1+M4 | area_diff_proxy_se3 | 0.307435 | 0.465910 | -0.017100 | -0.022838 | -0.017100 | improves_M1 |
| 2025 | structural | M1+M4 | recomposed_se3 | 0.392919 | 0.523644 | 0.016371 | 0.011592 | 0.016371 | not_better_than_M1 |

## observed target mode

| holdout_year | target_mode | variant | target | MAE | RMSE | MAE_delta_vs_M1 | RMSE_delta_vs_M1 | MAE_delta_vs_previous_variant | winner_or_status |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 2025 | observed | M1 | system_proxy_se1 | 0.377452 | 0.480459 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | observed | M1 | area_diff_proxy_se3 | 0.324554 | 0.488687 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | observed | M1 | recomposed_se3 | 0.387574 | 0.523463 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | observed | M1+M3A | system_proxy_se1 | 0.367575 | 0.466615 | -0.009877 | -0.013844 | -0.009877 | improves_M1 |
| 2025 | observed | M1+M3A | area_diff_proxy_se3 | 0.324554 | 0.488687 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | observed | M1+M3A | recomposed_se3 | 0.379889 | 0.513923 | -0.007685 | -0.009540 | -0.007685 | improves_M1 |
| 2025 | observed | M1+M3B | system_proxy_se1 | 0.372170 | 0.475575 | -0.005281 | -0.004884 | 0.004595 | improves_M1 |
| 2025 | observed | M1+M3B | area_diff_proxy_se3 | 0.324534 | 0.488748 | -0.000020 | 0.000061 | -0.000020 | improves_M1 |
| 2025 | observed | M1+M3B | recomposed_se3 | 0.384018 | 0.521638 | -0.003556 | -0.001826 | 0.004129 | improves_M1 |
| 2025 | observed | M1+M3A+M3B | system_proxy_se1 | 0.362448 | 0.461737 | -0.015003 | -0.018722 | -0.009722 | improves_M1 |
| 2025 | observed | M1+M3A+M3B | area_diff_proxy_se3 | 0.324534 | 0.488748 | -0.000020 | 0.000061 | 0.000000 | improves_M1 |
| 2025 | observed | M1+M3A+M3B | recomposed_se3 | 0.376549 | 0.512052 | -0.011026 | -0.011411 | -0.007469 | improves_M1 |
| 2025 | observed | M1+M4 | system_proxy_se1 | 0.377550 | 0.470361 | 0.000098 | -0.010098 | 0.015101 | not_better_than_M1 |
| 2025 | observed | M1+M4 | area_diff_proxy_se3 | 0.307328 | 0.465795 | -0.017225 | -0.022892 | -0.017206 | improves_M1 |
| 2025 | observed | M1+M4 | recomposed_se3 | 0.402941 | 0.532889 | 0.015366 | 0.009426 | 0.026392 | not_better_than_M1 |
| 2025 | observed | M1+M3A+M4 | system_proxy_se1 | 0.367512 | 0.459418 | -0.009940 | -0.021041 | -0.010038 | improves_M1 |
| 2025 | observed | M1+M3A+M4 | area_diff_proxy_se3 | 0.307328 | 0.465795 | -0.017225 | -0.022892 | 0.000000 | improves_M1 |
| 2025 | observed | M1+M3A+M4 | recomposed_se3 | 0.395375 | 0.524940 | 0.007800 | 0.001477 | -0.007566 | not_better_than_M1 |
| 2025 | observed | M1+M3B+M4 | system_proxy_se1 | 0.373142 | 0.466505 | -0.004309 | -0.013954 | 0.005630 | improves_M1 |
| 2025 | observed | M1+M3B+M4 | area_diff_proxy_se3 | 0.307435 | 0.465910 | -0.017119 | -0.022777 | 0.000106 | improves_M1 |
| 2025 | observed | M1+M3B+M4 | recomposed_se3 | 0.400016 | 0.531624 | 0.012442 | 0.008160 | 0.004642 | not_better_than_M1 |
| 2025 | observed | M1+M3A+M3B+M4 | system_proxy_se1 | 0.363589 | 0.455624 | -0.013862 | -0.024835 | -0.009553 | improves_M1 |
| 2025 | observed | M1+M3A+M3B+M4 | area_diff_proxy_se3 | 0.307435 | 0.465910 | -0.017119 | -0.022777 | 0.000000 | improves_M1 |
| 2025 | observed | M1+M3A+M3B+M4 | recomposed_se3 | 0.392919 | 0.523644 | 0.005345 | 0.000181 | -0.007097 | not_better_than_M1 |
