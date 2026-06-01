# P0045 forecast window policy

Primary origins are fixed-CET model days at hour 00. Each window covers D 00:00 through D+6 23:00 and is accepted only with exactly 168 hourly rows for the target series.

window_counts = {'system_proxy_se1': {'holdout': 135, 'validate': 365}, 'area_diff_proxy_se3': {'holdout': 135, 'validate': 365}}

Rolling windows overlap heavily; metrics are model-selection diagnostics rather than iid confidence estimates.
