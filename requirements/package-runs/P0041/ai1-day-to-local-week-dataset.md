# P0041 AI-1 day-to-local-week dataset

row_grain = date x target_series
local_window = D-2..D+4
incomplete_windows = skipped
skipped_center_dates = 62

| target_series | rows |
|---|---:|
| area_diff_proxy_se3 | 1396 |
| system_proxy_se1 | 1396 |

SE1 and SE3-SE1 are stored as separate target series throughout.
