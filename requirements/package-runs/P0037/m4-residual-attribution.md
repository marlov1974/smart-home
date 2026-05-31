# P0037 M4 residual attribution

# P0037 component attribution matrix

| holdout_year | target_mode | variant | target | MAE | RMSE | MAE_delta_vs_M1 | RMSE_delta_vs_M1 | MAE_delta_vs_previous_variant | winner_or_status |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 2025 | structural | M1 | system_proxy_se1 | 0.362448 | 0.461737 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | structural | M1 | area_diff_proxy_se3 | 0.324534 | 0.488748 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | structural | M1 | recomposed_se3 | 0.376549 | 0.512052 | 0.000000 | 0.000000 | 0.000000 | not_better_than_M1 |
| 2025 | structural | M1+M4 | system_proxy_se1 | 0.363589 | 0.455624 | 0.001141 | -0.006114 | 0.001141 | not_better_than_M1 |
| 2025 | structural | M1+M4 | area_diff_proxy_se3 | 0.307435 | 0.465910 | -0.017100 | -0.022838 | -0.017100 | improves_M1 |
| 2025 | structural | M1+M4 | recomposed_se3 | 0.392919 | 0.523644 | 0.016371 | 0.011592 | 0.016371 | not_better_than_M1 |

## Selected HGB candidates

| target | candidate_id | validate_mae | elapsed_seconds | parameters |
|---|---|---:|---:|---|
| system_proxy_se1 | p0037_system_proxy_se1_006 | 0.265399 | 0.229495 | `{"early_stopping": true, "l2_regularization": 0.1, "learning_rate": 0.03, "max_iter": 100, "max_leaf_nodes": 15, "min_samples_leaf": 100, "random_state": 37}` |
| area_diff_proxy_se3 | p0037_area_diff_proxy_se3_005 | 0.205711 | 0.133022 | `{"early_stopping": true, "l2_regularization": 0.1, "learning_rate": 0.03, "max_iter": 100, "max_leaf_nodes": 7, "min_samples_leaf": 100, "random_state": 37}` |

## Largest M4-worsened recomposed SE3 rows

| local_date | hour | special_day_type | actual_structural_se3 | M1 | M1+M4 | MAE_delta |
|---|---:|---|---:|---:|---:|---:|
| 2025-11-24 | 16 | normal_weekday | 2.393665 | 2.297436 | 1.857594 | 0.439841 |
| 2025-11-24 | 17 | normal_weekday | 2.645717 | 2.261508 | 1.821667 | 0.439841 |
| 2025-11-24 | 18 | normal_weekday | 2.302945 | 2.030833 | 1.590992 | 0.439841 |
| 2025-11-24 | 19 | normal_weekday | 1.878555 | 1.743033 | 1.303192 | 0.439841 |
| 2025-11-24 | 20 | normal_weekday | 1.519970 | 1.365191 | 0.925350 | 0.439841 |
| 2025-11-24 | 21 | normal_weekday | 1.367845 | 1.199976 | 0.760135 | 0.439841 |
| 2025-11-24 | 22 | normal_weekday | 1.236180 | 1.173631 | 0.733790 | 0.439841 |
| 2025-11-25 | 20 | normal_weekday | 1.641660 | 1.269138 | 0.853577 | 0.415561 |
| 2025-11-25 | 21 | normal_weekday | 1.276900 | 1.149801 | 0.734240 | 0.415561 |
| 2025-11-25 | 22 | normal_weekday | 1.114305 | 1.097071 | 0.681510 | 0.415561 |
| 2025-11-24 | 23 | normal_weekday | 1.054333 | 1.070541 | 0.630700 | 0.407424 |
| 2025-12-21 | 6 | normal_sunday | 0.488225 | 0.471721 | 0.104992 | 0.366729 |
| 2025-12-21 | 22 | normal_sunday | 0.545297 | 0.545079 | 0.178350 | 0.366729 |
| 2025-12-21 | 23 | normal_sunday | 0.515715 | 0.474979 | 0.108250 | 0.366729 |
| 2025-11-25 | 19 | normal_weekday | 2.357635 | 1.548716 | 1.192374 | 0.356342 |
| 2025-11-24 | 15 | normal_weekday | 2.014620 | 2.057891 | 1.618050 | 0.353299 |
| 2025-06-29 | 13 | normal_sunday | -0.236144 | 0.025808 | 0.374564 | 0.348756 |
| 2025-06-29 | 22 | normal_sunday | -0.010464 | 0.318965 | 0.667721 | 0.348756 |
| 2025-06-29 | 1 | normal_sunday | 0.000000 | 0.094338 | 0.443093 | 0.348756 |
| 2025-06-29 | 2 | normal_sunday | -0.001560 | 0.037277 | 0.386033 | 0.348756 |

## Largest M4-improved recomposed SE3 rows

| local_date | hour | special_day_type | actual_structural_se3 | M1 | M1+M4 | MAE_delta |
|---|---:|---|---:|---:|---:|---:|
| 2025-12-18 | 2 | normal_weekday | 0.375500 | 0.948701 | 0.477533 | -0.471168 |
| 2025-12-18 | 4 | normal_weekday | 0.237233 | 0.941018 | 0.469850 | -0.471168 |
| 2025-12-18 | 0 | normal_weekday | 0.468265 | 0.963266 | 0.492098 | -0.471168 |
| 2025-12-18 | 1 | normal_weekday | 0.427658 | 0.950516 | 0.479348 | -0.471168 |
| 2025-12-18 | 3 | normal_weekday | 0.307462 | 0.926126 | 0.454958 | -0.471168 |
| 2025-12-18 | 21 | normal_weekday | 0.483490 | 1.066668 | 0.595500 | -0.471168 |
| 2025-12-18 | 22 | normal_weekday | 0.452533 | 1.053643 | 0.582475 | -0.471168 |
| 2025-12-18 | 23 | normal_weekday | 0.276905 | 0.893638 | 0.422470 | -0.471168 |
| 2025-12-18 | 5 | normal_weekday | 0.222027 | 0.985303 | 0.514135 | -0.471168 |
| 2025-12-18 | 20 | normal_weekday | 0.543520 | 1.161358 | 0.690190 | -0.471168 |
| 2025-12-20 | 0 | normal_saturday | 0.150527 | 0.663149 | 0.195843 | -0.467307 |
| 2025-12-20 | 8 | normal_saturday | 0.162142 | 0.707329 | 0.240023 | -0.467307 |
| 2025-12-20 | 9 | normal_saturday | 0.168665 | 0.733430 | 0.266123 | -0.467307 |
| 2025-12-20 | 10 | normal_saturday | 0.167137 | 0.767315 | 0.300008 | -0.467307 |
| 2025-12-20 | 12 | normal_saturday | 0.160125 | 0.825935 | 0.358628 | -0.467307 |
| 2025-12-20 | 13 | normal_saturday | 0.163617 | 0.844439 | 0.377133 | -0.467307 |
| 2025-12-20 | 15 | normal_saturday | 0.179412 | 0.887410 | 0.420103 | -0.467307 |
| 2025-12-20 | 16 | normal_saturday | 0.202732 | 0.899280 | 0.431973 | -0.467307 |
| 2025-12-20 | 6 | normal_saturday | 0.146217 | 0.650120 | 0.182813 | -0.467307 |
| 2025-12-20 | 7 | normal_saturday | 0.152270 | 0.695749 | 0.228443 | -0.467307 |
