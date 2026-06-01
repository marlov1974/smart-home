# P0041 AI-2 hour-to-day dataset

row_grain = timestamp x target_series
day_window = fixed local 00:00..23:00
max_abs_mean_hour_shape_by_day_target = 0.000000

| target_series | rows |
|---|---:|
| area_diff_proxy_se3 | 34800 |
| system_proxy_se1 | 34800 |

SE1 and SE3-SE1 are stored as separate target series throughout.
