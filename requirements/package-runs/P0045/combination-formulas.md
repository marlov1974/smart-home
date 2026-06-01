# P0045 combination formulas

Selected formulas by validation scaled MAE: {'system_proxy_se1': 'combined_scaled', 'area_diff_proxy_se3': 'combined_scaled'}

Scaled formula: `day_level_shape * exp(log_local_7d_scale) + hour_shape * exp(log_local_7d_scale) * exp(log_day_scale_index)`, centered over 168h.

Dimensionless formula: `day_level_shape + hour_shape * exp(log_day_scale_index)`, centered over 168h.
