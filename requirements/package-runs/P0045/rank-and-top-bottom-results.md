# P0045 rank and top/bottom results

| series | split | predictor | spearman_168h | top_10_percent_hit_rate | bottom_10_percent_hit_rate | top_20h_precision | bottom_20h_precision | best_8h_hit_rate | worst_8h_hit_rate |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| system_proxy_se1 | validate | combined_scaled | 0.601961 | 0.446253 | 0.418533 | 0.466849 | 0.441233 | 0.306507 | 0.310959 |
| system_proxy_se1 | validate | combined_dimensionless | 0.611155 | 0.449799 | 0.450282 | 0.462877 | 0.463151 | 0.299315 | 0.344178 |
| system_proxy_se1 | validate | B0_flat_168h | 0.013717 | 0.154553 | 0.136825 | 0.165342 | 0.140822 | 0.088014 | 0.104795 |
| system_proxy_se1 | validate | B1_AI2_only | 0.373611 | 0.213860 | 0.302337 | 0.239589 | 0.330822 | 0.120890 | 0.207877 |
| system_proxy_se1 | validate | B2_AI1_day_only | 0.512221 | 0.384045 | 0.250282 | 0.417534 | 0.258767 | 0.172603 | 0.171233 |
| system_proxy_se1 | validate | B3_time_profile_168h | 0.400367 | 0.236422 | 0.248187 | 0.261507 | 0.271233 | 0.100685 | 0.141781 |
| system_proxy_se1 | holdout | combined_scaled | 0.616628 | 0.484096 | 0.439216 | 0.513333 | 0.445185 | 0.382407 | 0.336111 |
| system_proxy_se1 | holdout | combined_dimensionless | 0.619516 | 0.491068 | 0.438344 | 0.522963 | 0.443333 | 0.397222 | 0.339815 |
| system_proxy_se1 | holdout | B0_flat_168h | 0.032976 | 0.122004 | 0.144662 | 0.137037 | 0.150741 | 0.060185 | 0.115741 |
| system_proxy_se1 | holdout | B1_AI2_only | 0.400025 | 0.270153 | 0.286275 | 0.294444 | 0.299630 | 0.191667 | 0.201852 |
| system_proxy_se1 | holdout | B2_AI1_day_only | 0.499120 | 0.431808 | 0.297603 | 0.462963 | 0.297778 | 0.199074 | 0.237037 |
| system_proxy_se1 | holdout | B3_time_profile_168h | 0.362948 | 0.301525 | 0.196514 | 0.327037 | 0.219630 | 0.206481 | 0.102778 |
| area_diff_proxy_se3 | validate | combined_scaled | 0.432550 | 0.381305 | 0.244480 | 0.400411 | 0.267397 | 0.266438 | 0.148630 |
| area_diff_proxy_se3 | validate | combined_dimensionless | 0.432550 | 0.381305 | 0.244480 | 0.400411 | 0.267397 | 0.266438 | 0.148630 |
| area_diff_proxy_se3 | validate | B0_flat_168h | 0.018801 | 0.133441 | 0.138759 | 0.145753 | 0.143425 | 0.096575 | 0.057534 |
| area_diff_proxy_se3 | validate | B1_AI2_only | 0.332600 | 0.308783 | 0.133763 | 0.330137 | 0.155068 | 0.185274 | 0.057534 |
| area_diff_proxy_se3 | validate | B2_AI1_day_only | 0.267220 | 0.236261 | 0.212732 | 0.262603 | 0.213699 | 0.186301 | 0.081164 |
| area_diff_proxy_se3 | validate | B3_time_profile_168h | 0.278355 | 0.287510 | 0.131829 | 0.308356 | 0.147397 | 0.187671 | 0.064726 |
| area_diff_proxy_se3 | holdout | combined_scaled | 0.269905 | 0.308932 | 0.173856 | 0.328148 | 0.197037 | 0.192593 | 0.121296 |
| area_diff_proxy_se3 | holdout | combined_dimensionless | 0.269905 | 0.308932 | 0.173856 | 0.328148 | 0.197037 | 0.192593 | 0.121296 |
| area_diff_proxy_se3 | holdout | B0_flat_168h | 0.028963 | 0.131590 | 0.151198 | 0.145556 | 0.155926 | 0.098148 | 0.037963 |
| area_diff_proxy_se3 | holdout | B1_AI2_only | 0.239864 | 0.295425 | 0.094118 | 0.332222 | 0.121481 | 0.200000 | 0.040741 |
| area_diff_proxy_se3 | holdout | B2_AI1_day_only | 0.124516 | 0.118519 | 0.185621 | 0.144815 | 0.193333 | 0.091667 | 0.004630 |
| area_diff_proxy_se3 | holdout | B3_time_profile_168h | 0.095453 | 0.237908 | 0.048802 | 0.252593 | 0.066296 | 0.152778 | 0.015741 |
