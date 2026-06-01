# P0044 component attribution summary

Status: WARN
1. Corrected P0042 dataset/table used: `ai1_day_to_local_week_training_targets_v2`.
2. Split: train earliest..2024-12-31, validate 2025, holdout 2026.
3. Model class: bounded HistGradientBoostingRegressor.
4. Feature groups tested: F0-F5.
system_proxy_se1 day_level_shape: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.355845, B0_zero_MAE=0.497128, rank_or_corr=0.617460.
system_proxy_se1 log_day_scale_index: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.464121, B0_zero_MAE=0.485789, rank_or_corr=0.422751.
system_proxy_se1 log_local_7d_scale: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.564496, B0_train_mean_MAE=0.709789, rank_or_corr=0.451583.
area_diff_proxy_se3 day_level_shape: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.409364, B0_zero_MAE=0.414882, rank_or_corr=0.202910.
area_diff_proxy_se3 log_day_scale_index: selected=F0_time_only, model_MAE=0.413623, B0_zero_MAE=0.394291, rank_or_corr=0.154762.
area_diff_proxy_se3 log_local_7d_scale: selected=F5_area_diff_wind_gradient_optional, model_MAE=0.658178, B0_train_mean_MAE=0.465157, rank_or_corr=-0.232052.
Weather delta and relative-to-local-7d/rank effects are visible in `feature-ablation-results.md`.
Targets weaker than their baseline should use baseline/API-anchor fallback in P0045 rather than being forced into the combined model.
No AI-2 retraining, combined 168h forecast, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
