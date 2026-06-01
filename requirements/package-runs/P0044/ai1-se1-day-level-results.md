# P0044 system_proxy_se1 day_level_shape

selected_feature_group = F5_area_diff_wind_gradient_optional
model_class = HistGradientBoostingRegressor
holdout_model_MAE = 0.355845
holdout_B0_zero_MAE = 0.497128
holdout_model_rank_or_corr = 0.617460
diagnostic_centering = {'applied_to_future_default': False, 'tested': True, 'centered_rows': 141, 'raw_holdout': {'MAE': 0.35584530992043517, 'RMSE': 0.4524386404501554, 'mean_signed_error': 0.032800373617058724, 'local_window_count': 135.0, 'spearman_rank_within_local_7d_mean': 0.6174603174603174, 'spearman_rank_within_local_7d_median': 0.6785714285714286, 'highest_day_hit_rate': 0.6074074074074074, 'lowest_day_hit_rate': 0.4148148148148148, 'top_2_days_precision': 0.6777777777777778, 'bottom_2_days_precision': 0.5962962962962963}, 'centered_holdout': {'MAE': 0.34125317991428783, 'RMSE': 0.4355407362652479, 'mean_signed_error': 0.009849775443826833, 'local_window_count': 135.0, 'spearman_rank_within_local_7d_mean': 0.6185185185185181, 'spearman_rank_within_local_7d_median': 0.6428571428571429, 'highest_day_hit_rate': 0.674074074074074, 'lowest_day_hit_rate': 0.34814814814814815, 'top_2_days_precision': 0.6777777777777778, 'bottom_2_days_precision': 0.6037037037037037}}
