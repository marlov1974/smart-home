# P0042 area_diff scale policy comparison

selected_policy = F_hybrid_selected_policy
area_diff_scale_floor = 0.105683

| candidate | floor | p01 | p99 | min | max | std |
|---|---:|---:|---:|---:|---:|---:|
| A_current_policy_baseline | 0.001000 | -10.000000 | 32.616033 | -104.695000 | 230.000000 | 9.242008 |
| B_area_diff_higher_fixed_min_scale_0_01 | 0.010000 | -9.206625 | 11.440128 | -54.212625 | 146.763411 | 4.331474 |
| C_area_diff_quantile_floor_p50 | 0.105683 | -1.686771 | 2.908536 | -7.427686 | 16.973383 | 0.858910 |
| D_area_diff_winsorized_target_diagnostic | 0.105683 | -1.686556 | 2.908440 | -1.686771 | 2.908536 | 0.663884 |
| E_area_diff_clipped_target_diagnostic | 0.105683 | -1.686771 | 2.908536 | -7.427686 | 10.000000 | 0.837323 |
| F_hybrid_selected_policy | 0.105683 | -1.686771 | 2.908536 | -7.427686 | 16.973383 | 0.858910 |

Selected policy fixes the denominator first. Winsorization/clipping remain diagnostics only, not primary target construction.
