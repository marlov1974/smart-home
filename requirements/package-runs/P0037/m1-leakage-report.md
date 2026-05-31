# P0037 M1 leakage report

| variant | target | MAE | RMSE |
|---|---|---:|---:|
| full_period_M1_existing | system_proxy_se1 | 0.238920 | 0.331111 |
| full_period_M1_existing | area_diff_proxy_se3 | 0.276268 | 0.432638 |
| full_period_M1_existing | recomposed_se3 | 0.308994 | 0.440256 |
| train_only_M1_for_2025_holdout | system_proxy_se1 | 0.371326 | 0.474105 |
| train_only_M1_for_2025_holdout | area_diff_proxy_se3 | 0.324620 | 0.488786 |
| train_only_M1_for_2025_holdout | recomposed_se3 | 0.384666 | 0.521048 |
| train_only_M1_m3ab_normalized_for_2025_holdout | system_proxy_se1 | 0.377452 | 0.480459 |
| train_only_M1_m3ab_normalized_for_2025_holdout | area_diff_proxy_se3 | 0.324554 | 0.488687 |
| train_only_M1_m3ab_normalized_for_2025_holdout | recomposed_se3 | 0.387574 | 0.523463 |

Full-period M1 includes the 2025 holdout and is leakage-advantaged. It is a production-reference diagnostic, not a strict holdout baseline.
