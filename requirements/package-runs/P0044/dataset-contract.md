# P0044 dataset contract

used_table = `ai1_day_to_local_week_training_targets_v2`

contract = {'ok': True, 'missing_fields': [], 'row_counts': {'system_proxy_se1': 1451, 'area_diff_proxy_se3': 1451}, 'unique_model_cet_dates_per_target': {'system_proxy_se1': 1451, 'area_diff_proxy_se3': 1451}, 'local_7d_row_count_all_168_hours': True, 'targets_are_finite': True, 'uses_p0042_v2_table': True, 'absolute_or_ratio_columns_present_but_not_targets': ['day_mean_price', 'day_ratio_index_diagnostic'], 'target_columns_used': ['day_level_shape', 'log_day_scale_index', 'log_local_7d_scale']}

P0044 fails rather than falling back to P0041 pre-correction data. Absolute price and ratio diagnostic columns may exist in the input table for traceability, but the target list used for model training is exactly `day_level_shape, log_day_scale_index, log_local_7d_scale`.
