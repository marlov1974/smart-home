# P0044 next combination plan

P0045 can combine AI-1 with P0043 AI-2 only after reviewing which P0044 targets beat train-only baselines. Recommended target usage:
- system_proxy_se1 day_level_shape: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.355845, B0_zero_MAE=0.497128, recommendation=use AI-1 target.
- system_proxy_se1 log_day_scale_index: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.464121, B0_zero_MAE=0.485789, recommendation=use AI-1 target.
- system_proxy_se1 log_local_7d_scale: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.564496, B0_train_mean_MAE=0.709789, recommendation=use AI-1 target.
- area_diff_proxy_se3 day_level_shape: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.409364, B0_zero_MAE=0.414882, recommendation=use AI-1 target.
- area_diff_proxy_se3 log_day_scale_index: selected=F0_time_only, model_MAE=0.413623, B0_zero_MAE=0.394291, recommendation=prefer baseline/API-anchor fallback until improved.
- area_diff_proxy_se3 log_local_7d_scale: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.658178, B0_train_mean_MAE=0.465157, recommendation=prefer baseline/API-anchor fallback until improved.

No combined 168h forecast or anchored absolute API was built in P0044.
