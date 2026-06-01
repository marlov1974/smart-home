# P0045 oracle diagnostics

| series | split | predictor | windows | scaled_MAE | centered_MAE | spearman | day_spearman | intraday_spearman | oracle |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| system_proxy_se1 | validate | B4_AI2_actual_day_scale_oracle | 365.000000 | 0.953422 | 0.146008 | 0.428826 | 0.017906 | 0.576745 | True |
| system_proxy_se1 | validate | B5_AI1_actual_hour_shape_oracle | 365.000000 | 2.024363 | 0.171642 | 0.699502 | 0.624755 | 0.999997 | True |
| system_proxy_se1 | holdout | B4_AI2_actual_day_scale_oracle | 135.000000 | 0.593509 | 0.223781 | 0.435908 | 0.063757 | 0.651242 | True |
| system_proxy_se1 | holdout | B5_AI1_actual_hour_shape_oracle | 135.000000 | 0.526679 | 0.179386 | 0.741801 | 0.621693 | 0.999999 | True |
| area_diff_proxy_se3 | validate | B4_AI2_actual_day_scale_oracle | 365.000000 | 0.584266 | 0.216988 | 0.323884 | 0.048924 | 0.464063 | True |
| area_diff_proxy_se3 | validate | B5_AI1_actual_hour_shape_oracle | 365.000000 | 0.445021 | 0.166863 | 0.763597 | 0.416830 | 0.999993 | True |
| area_diff_proxy_se3 | holdout | B4_AI2_actual_day_scale_oracle | 135.000000 | 0.891193 | 0.176908 | 0.238383 | 0.003439 | 0.329668 | True |
| area_diff_proxy_se3 | holdout | B5_AI1_actual_hour_shape_oracle | 135.000000 | 1.079092 | 0.147109 | 0.639460 | 0.193915 | 0.999995 | True |

Oracle diagnostics use actual historical target structure and are excluded from deployable model selection.
