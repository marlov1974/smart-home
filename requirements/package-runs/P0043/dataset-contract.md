# P0043 dataset contract

used_table = `ai2_hour_to_day_training_targets_v2`
contract = {'ok': True, 'missing_fields': [], 'unique_timestamp_utc_per_target': {'system_proxy_se1': 34968, 'area_diff_proxy_se3': 34968}, 'row_counts': {'system_proxy_se1': 34968, 'area_diff_proxy_se3': 34968}, 'uses_p0042_v2_table': True}

P0043 fails rather than falling back to P0041 pre-correction data.
