# P0047 dataset contract

used_tables = ['ai2_hour_to_day_training_targets_v2']

contract = {'ok': True, 'source_table': 'ai2_hour_to_day_training_targets_v2', 'missing_required_fields': [], 'missing_optional_available_fields': [], 'target_counts': {'system_proxy_se1': 34968, 'area_diff_proxy_se3': 34968}, 'finite_hour_price': True, 'uses_p0042_fixed_cet_v2_table': True}

SE3 is reconstructed as `se1_price + se3_minus_se1`; `se3_minus_se1` comes from P0042/P0045 target `area_diff_proxy_se3`.

Primary timestamp is `timestamp_utc`. Model calendar fields use P0042 fixed-CET: `model_cet_timestamp = timestamp_utc + 1h`.

Missing requested weather/gradient columns: ['temperature_se3_or_south_actual', 'temperature_south_minus_north', 'solar_se3_or_south_actual', 'solar_south_minus_north', 'wind_south_proxy', 'wind_central_proxy', 'wind_north_proxy', 'wind_south_minus_north', 'wind_central_minus_north']
