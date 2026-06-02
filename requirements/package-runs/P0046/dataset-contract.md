# P0046 dataset contract

used_tables = ['ai1_day_to_local_week_training_targets_v2', 'ai2_hour_to_day_training_targets_v2']

contract = {'ok': True, 'ai1_missing_fields': [], 'ai2_missing_fields': [], 'ai1_counts': {'system_proxy_se1': 1451, 'area_diff_proxy_se3': 1451}, 'ai2_counts': {'system_proxy_se1': 34968, 'area_diff_proxy_se3': 34968}, 'finite_ai1_targets': True, 'finite_ai2_targets': True, 'uses_p0042_v2_tables': True}

P0046 uses corrected P0042 fixed-CET v2 tables through P0045 loaders and fails rather than falling back to older datasets.
