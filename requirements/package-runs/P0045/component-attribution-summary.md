# P0045 component attribution summary

Status: PASS
1. Corrected datasets used: ['ai1_day_to_local_week_training_targets_v2', 'ai2_hour_to_day_training_targets_v2'].
2. AI-2 predictions regenerated from P0043 selected groups; AI-1 predictions regenerated/applied from P0044 target policy.
3. Selected formulas: {'system_proxy_se1': 'combined_scaled', 'area_diff_proxy_se3': 'combined_scaled'}.
4. Window counts: {'system_proxy_se1': {'holdout': 135, 'validate': 365}, 'area_diff_proxy_se3': {'holdout': 135, 'validate': 365}}.
system_proxy_se1: selected=combined_scaled, scaled_MAE=0.568437, B0=0.639685, AI2_only=1.604569, AI1_only=0.550570, spearman=0.616628.
area_diff_proxy_se3: selected=combined_scaled, scaled_MAE=1.250916, B0=0.864943, AI2_only=2.515733, AI1_only=1.162986, spearman=0.269905.
Oracle diagnostics are labeled and excluded from deployable selection.
No new AI hyperparameter search/training, anchored absolute API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
