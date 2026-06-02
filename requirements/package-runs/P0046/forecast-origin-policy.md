# P0046 forecast-origin policy

Primary policy: Monday 06:00 fixed-CET model time; 168 consecutive fixed-CET hours; validation=2025 origins, holdout=2026 origins.

window_counts = {'system_proxy_se1': {'holdout': 19, 'validate': 52}, 'area_diff_proxy_se3': {'holdout': 19, 'validate': 52}}

Each accepted window has exactly 168 hourly rows from Monday 06:00 through the following Monday 05:00 fixed-CET model time.
