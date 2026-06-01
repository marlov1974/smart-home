# P0044 area_diff_proxy_se3 day_level_shape

selected_feature_group = F5_area_diff_wind_gradient_optional
model_class = HistGradientBoostingRegressor
holdout_model_MAE = 0.409364
holdout_B0_zero_MAE = 0.414882
holdout_model_rank_or_corr = 0.202910
diagnostic_centering = {'applied_to_future_default': False, 'tested': True, 'centered_rows': 141, 'raw_holdout': {'MAE': 0.40936444424934326, 'RMSE': 0.5757524158853526, 'mean_signed_error': -0.030286903858424235, 'local_window_count': 135.0, 'spearman_rank_within_local_7d_mean': 0.20291005291005287, 'spearman_rank_within_local_7d_median': 0.32142857142857145, 'highest_day_hit_rate': 0.17037037037037037, 'lowest_day_hit_rate': 0.14814814814814814, 'top_2_days_precision': 0.3592592592592593, 'bottom_2_days_precision': 0.43333333333333335}, 'centered_holdout': {'MAE': 0.4129147474895437, 'RMSE': 0.5709705737271428, 'mean_signed_error': 0.001910241777164411, 'local_window_count': 135.0, 'spearman_rank_within_local_7d_mean': 0.21772486772486777, 'spearman_rank_within_local_7d_median': 0.32142857142857145, 'highest_day_hit_rate': 0.16296296296296298, 'lowest_day_hit_rate': 0.24444444444444444, 'top_2_days_precision': 0.36666666666666664, 'bottom_2_days_precision': 0.42592592592592593}}
