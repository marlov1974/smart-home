# P0045 daily allocation results

| series | split | predictor | day_mean_shape_MAE | day_rank_spearman | highest_day_hit_rate | lowest_day_hit_rate |
|---|---|---|---:|---:|---:|---:|
| system_proxy_se1 | validate | combined_scaled | 0.106423 | 0.624755 | 0.589041 | 0.378082 |
| system_proxy_se1 | validate | combined_dimensionless | 0.220865 | 0.635616 | 0.539726 | 0.364384 |
| system_proxy_se1 | validate | B0_flat_168h | 0.131059 | 0.023581 | 0.205479 | 0.191781 |
| system_proxy_se1 | validate | B1_AI2_only | 0.131059 | -0.027104 | 0.178082 | 0.098630 |
| system_proxy_se1 | validate | B2_AI1_day_only | 0.106423 | 0.624755 | 0.589041 | 0.378082 |
| system_proxy_se1 | validate | B3_time_profile_168h | 0.136148 | 0.294814 | 0.180822 | 0.356164 |
| system_proxy_se1 | holdout | combined_scaled | 0.153234 | 0.621693 | 0.585185 | 0.370370 |
| system_proxy_se1 | holdout | combined_dimensionless | 0.211554 | 0.615079 | 0.577778 | 0.414815 |
| system_proxy_se1 | holdout | B0_flat_168h | 0.203153 | 0.015873 | 0.140741 | 0.192593 |
| system_proxy_se1 | holdout | B1_AI2_only | 0.203153 | 0.119577 | 0.229630 | 0.155556 |
| system_proxy_se1 | holdout | B2_AI1_day_only | 0.153234 | 0.621693 | 0.585185 | 0.370370 |
| system_proxy_se1 | holdout | B3_time_profile_168h | 0.197477 | 0.222222 | 0.081481 | 0.214815 |
| area_diff_proxy_se3 | validate | combined_scaled | 0.137574 | 0.416243 | 0.326027 | 0.328767 |
| area_diff_proxy_se3 | validate | combined_dimensionless | 0.179385 | 0.416536 | 0.326027 | 0.336986 |
| area_diff_proxy_se3 | validate | B0_flat_168h | 0.153823 | -0.004207 | 0.158904 | 0.169863 |
| area_diff_proxy_se3 | validate | B1_AI2_only | 0.153823 | 0.140411 | 0.183562 | 0.230137 |
| area_diff_proxy_se3 | validate | B2_AI1_day_only | 0.137574 | 0.415949 | 0.326027 | 0.328767 |
| area_diff_proxy_se3 | validate | B3_time_profile_168h | 0.151526 | 0.203620 | 0.131507 | 0.238356 |
| area_diff_proxy_se3 | holdout | combined_scaled | 0.123974 | 0.197619 | 0.155556 | 0.237037 |
| area_diff_proxy_se3 | holdout | combined_dimensionless | 0.186587 | 0.197884 | 0.155556 | 0.244444 |
| area_diff_proxy_se3 | holdout | B0_flat_168h | 0.125727 | 0.035979 | 0.185185 | 0.192593 |
| area_diff_proxy_se3 | holdout | B1_AI2_only | 0.125727 | 0.093651 | 0.103704 | 0.148148 |
| area_diff_proxy_se3 | holdout | B2_AI1_day_only | 0.123974 | 0.197354 | 0.155556 | 0.207407 |
| area_diff_proxy_se3 | holdout | B3_time_profile_168h | 0.134716 | 0.105291 | 0.170370 | 0.177778 |
