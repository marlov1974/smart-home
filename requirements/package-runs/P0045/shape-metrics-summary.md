# P0045 shape metrics summary

| series | split | predictor | windows | scaled_MAE | centered_MAE | spearman | day_spearman | intraday_spearman | oracle |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| system_proxy_se1 | validate | combined_scaled | 365.000000 | 1.563089 | 0.151484 | 0.601961 | 0.624755 | 0.576745 | False |
| system_proxy_se1 | validate | combined_dimensionless | 365.000000 | 6.376082 | 0.449101 | 0.611155 | 0.635616 | 0.576745 | False |
| system_proxy_se1 | validate | B0_flat_168h | 365.000000 | 0.985129 | 0.151696 | 0.013717 | 0.023581 | 0.158818 | False |
| system_proxy_se1 | validate | B1_AI2_only | 365.000000 | 5.731725 | 0.429932 | 0.373611 | -0.027104 | 0.576745 | False |
| system_proxy_se1 | validate | B2_AI1_day_only | 365.000000 | 1.104870 | 0.136475 | 0.512221 | 0.624755 | 0.158818 | False |
| system_proxy_se1 | validate | B3_time_profile_168h | 365.000000 | 1.523040 | 0.165130 | 0.400367 | 0.294814 | 0.496844 | False |
| system_proxy_se1 | holdout | combined_scaled | 135.000000 | 0.568437 | 0.193999 | 0.616628 | 0.621693 | 0.651242 | False |
| system_proxy_se1 | holdout | combined_dimensionless | 135.000000 | 1.662471 | 0.402189 | 0.619516 | 0.615079 | 0.651242 | False |
| system_proxy_se1 | holdout | B0_flat_168h | 135.000000 | 0.639685 | 0.243078 | 0.032976 | 0.015873 | 0.181289 | False |
| system_proxy_se1 | holdout | B1_AI2_only | 135.000000 | 1.604569 | 0.403338 | 0.400025 | 0.119577 | 0.651242 | False |
| system_proxy_se1 | holdout | B2_AI1_day_only | 135.000000 | 0.550570 | 0.208900 | 0.499120 | 0.621693 | 0.181289 | False |
| system_proxy_se1 | holdout | B3_time_profile_168h | 135.000000 | 0.656066 | 0.230644 | 0.362948 | 0.222222 | 0.511881 | False |
| area_diff_proxy_se3 | validate | combined_scaled | 365.000000 | 0.576878 | 0.213570 | 0.432550 | 0.416243 | 0.464063 | False |
| area_diff_proxy_se3 | validate | combined_dimensionless | 365.000000 | 0.893107 | 0.293372 | 0.432550 | 0.416536 | 0.464063 | False |
| area_diff_proxy_se3 | validate | B0_flat_168h | 365.000000 | 0.635915 | 0.238212 | 0.018801 | -0.004207 | 0.222427 | False |
| area_diff_proxy_se3 | validate | B1_AI2_only | 365.000000 | 0.818777 | 0.279212 | 0.332600 | 0.140411 | 0.464063 | False |
| area_diff_proxy_se3 | validate | B2_AI1_day_only | 365.000000 | 0.617067 | 0.228834 | 0.267220 | 0.415949 | 0.222427 | False |
| area_diff_proxy_se3 | validate | B3_time_profile_168h | 365.000000 | 0.713812 | 0.249192 | 0.278355 | 0.203620 | 0.352542 | False |
| area_diff_proxy_se3 | holdout | combined_scaled | 135.000000 | 1.250916 | 0.184298 | 0.269905 | 0.197619 | 0.329668 | False |
| area_diff_proxy_se3 | holdout | combined_dimensionless | 135.000000 | 3.430326 | 0.288822 | 0.269905 | 0.197884 | 0.329668 | False |
| area_diff_proxy_se3 | holdout | B0_flat_168h | 135.000000 | 0.864943 | 0.190544 | 0.028963 | 0.035979 | 0.091338 | False |
| area_diff_proxy_se3 | holdout | B1_AI2_only | 135.000000 | 2.515733 | 0.250096 | 0.239864 | 0.093651 | 0.329668 | False |
| area_diff_proxy_se3 | holdout | B2_AI1_day_only | 135.000000 | 1.162986 | 0.191947 | 0.124516 | 0.197354 | 0.091338 | False |
| area_diff_proxy_se3 | holdout | B3_time_profile_168h | 135.000000 | 2.145182 | 0.240038 | 0.095453 | 0.105291 | 0.131849 | False |
