# P0045 intraday results

| series | split | predictor | hour_within_day_spearman_mean | top_3h_daily_hit_rate | bottom_3h_daily_hit_rate |
|---|---|---|---:|---:|---:|
| system_proxy_se1 | validate | combined_scaled | 0.576745 | 0.344814 | 0.461057 |
| system_proxy_se1 | validate | combined_dimensionless | 0.576745 | 0.344814 | 0.461057 |
| system_proxy_se1 | validate | B0_flat_168h | 0.158818 | 0.067319 | 0.329811 |
| system_proxy_se1 | validate | B1_AI2_only | 0.576745 | 0.344814 | 0.461057 |
| system_proxy_se1 | validate | B2_AI1_day_only | 0.158818 | 0.067319 | 0.329811 |
| system_proxy_se1 | validate | B3_time_profile_168h | 0.496844 | 0.333986 | 0.335551 |
| system_proxy_se1 | holdout | combined_scaled | 0.651242 | 0.420106 | 0.437743 |
| system_proxy_se1 | holdout | combined_dimensionless | 0.651242 | 0.420106 | 0.437743 |
| system_proxy_se1 | holdout | B0_flat_168h | 0.181289 | 0.060317 | 0.313933 |
| system_proxy_se1 | holdout | B1_AI2_only | 0.651242 | 0.420106 | 0.437743 |
| system_proxy_se1 | holdout | B2_AI1_day_only | 0.181289 | 0.060317 | 0.313933 |
| system_proxy_se1 | holdout | B3_time_profile_168h | 0.511881 | 0.374603 | 0.319577 |
| area_diff_proxy_se3 | validate | combined_scaled | 0.464063 | 0.440052 | 0.218656 |
| area_diff_proxy_se3 | validate | combined_dimensionless | 0.464063 | 0.440052 | 0.218656 |
| area_diff_proxy_se3 | validate | B0_flat_168h | 0.222427 | 0.086758 | 0.183823 |
| area_diff_proxy_se3 | validate | B1_AI2_only | 0.464063 | 0.440052 | 0.218656 |
| area_diff_proxy_se3 | validate | B2_AI1_day_only | 0.222427 | 0.086758 | 0.183823 |
| area_diff_proxy_se3 | validate | B3_time_profile_168h | 0.352542 | 0.392694 | 0.192564 |
| area_diff_proxy_se3 | holdout | combined_scaled | 0.329668 | 0.368254 | 0.184832 |
| area_diff_proxy_se3 | holdout | combined_dimensionless | 0.329668 | 0.368254 | 0.184832 |
| area_diff_proxy_se3 | holdout | B0_flat_168h | 0.091338 | 0.099471 | 0.088889 |
| area_diff_proxy_se3 | holdout | B1_AI2_only | 0.329668 | 0.368254 | 0.184832 |
| area_diff_proxy_se3 | holdout | B2_AI1_day_only | 0.091338 | 0.099471 | 0.088889 |
| area_diff_proxy_se3 | holdout | B3_time_profile_168h | 0.131849 | 0.300882 | 0.097354 |
