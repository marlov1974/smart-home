# P0044 baselines

| series | target | baseline | val_MAE | holdout_MAE | rank_or_corr |
|---|---|---|---:|---:|---:|
| system_proxy_se1 | day_level_shape | B0_zero | 0.762994 | 0.497128 | 0.011905 |
| system_proxy_se1 | day_level_shape | B1_weekday_mean | 0.717743 | 0.476153 | 0.314550 |
| system_proxy_se1 | day_level_shape | B2_weekday_season_smooth | 0.745116 | 0.499067 | 0.230423 |
| system_proxy_se1 | day_level_shape | B3_special_day_mean | 0.713290 | 0.474955 | 0.265079 |
| system_proxy_se1 | log_day_scale_index | B0_zero | 0.681729 | 0.485789 | 0.060582 |
| system_proxy_se1 | log_day_scale_index | B1_weekday_mean | 0.693980 | 0.483438 | 0.249471 |
| system_proxy_se1 | log_day_scale_index | B2_special_day_mean | 0.698190 | 0.501592 | 0.151587 |
| system_proxy_se1 | log_local_7d_scale | B0_train_mean | 1.007206 | 0.709789 | 0.000000 |
| system_proxy_se1 | log_local_7d_scale | B1_season_smooth | 0.990648 | 0.679467 | -0.150670 |
| system_proxy_se1 | log_local_7d_scale | B2_weather_actual_or_delta_simple | 0.941690 | 0.568451 | 0.526891 |
| area_diff_proxy_se3 | day_level_shape | B0_zero | 0.391497 | 0.414882 | 0.002646 |
| area_diff_proxy_se3 | day_level_shape | B1_weekday_mean | 0.374337 | 0.411775 | 0.156614 |
| area_diff_proxy_se3 | day_level_shape | B2_weekday_season_smooth | 0.388365 | 0.429266 | 0.080159 |
| area_diff_proxy_se3 | day_level_shape | B3_special_day_mean | 0.379257 | 0.413055 | 0.083333 |
| area_diff_proxy_se3 | log_day_scale_index | B0_zero | 0.402232 | 0.394291 | 0.130952 |
| area_diff_proxy_se3 | log_day_scale_index | B1_weekday_mean | 0.436200 | 0.440008 | 0.164815 |
| area_diff_proxy_se3 | log_day_scale_index | B2_special_day_mean | 0.436973 | 0.441093 | 0.166667 |
| area_diff_proxy_se3 | log_local_7d_scale | B0_train_mean | 0.507897 | 0.465157 | -0.000000 |
| area_diff_proxy_se3 | log_local_7d_scale | B1_season_smooth | 0.572346 | 0.743668 | -0.565937 |
| area_diff_proxy_se3 | log_local_7d_scale | B2_weather_actual_or_delta_simple | 0.530160 | 0.489257 | -0.147464 |
