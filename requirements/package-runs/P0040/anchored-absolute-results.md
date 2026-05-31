# P0040 aggregate results

| anchor | variant | weeks | MAE | RMSE | signed | daily_mean_MAE | p90_MAE | shape_MAE | spearman | top10 | bottom10 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| anchor_16h_mean | V0_naive_flat_week | 50 | 0.333955 | 0.421096 | 0.009426 | 0.260025 | 0.488475 | 0.287086 | -0.249096 | 0.037500 | 0.091250 |
| anchor_16h_median | V0_naive_flat_week | 50 | 0.342462 | 0.434564 | 0.015918 | 0.280221 | 0.498011 | 0.287086 | -0.249096 | 0.037500 | 0.091250 |
| anchor_16h_robust | V0_naive_flat_week | 50 | 0.342462 | 0.434564 | 0.015918 | 0.280221 | 0.498011 | 0.287086 | -0.249096 | 0.037500 | 0.091250 |
| anchor_16h_mean | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 50 | 0.353274 | 0.444247 | -0.055066 | 0.276051 | 0.508360 | 0.298010 | 0.482182 | 0.330000 | 0.247500 |
| anchor_16h_robust | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 50 | 0.360711 | 0.453327 | -0.065304 | 0.289196 | 0.531282 | 0.298010 | 0.482180 | 0.330000 | 0.247500 |
| anchor_16h_mean | V5_diagnostic_with_M3C | 50 | 0.364172 | 0.456976 | -0.052342 | 0.289352 | 0.537426 | 0.303757 | 0.448441 | 0.327500 | 0.222500 |
| anchor_16h_mean | V3_M1_plus_M3A_m1b_M3B_m1b | 50 | 0.364194 | 0.457027 | -0.052418 | 0.289471 | 0.537229 | 0.303704 | 0.448764 | 0.326250 | 0.221250 |
| anchor_16h_mean | V2_M1_plus_existing_M3A_M3B | 50 | 0.365197 | 0.458676 | -0.049374 | 0.291712 | 0.545351 | 0.304509 | 0.447373 | 0.317500 | 0.217500 |
| anchor_16h_median | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 50 | 0.365232 | 0.456375 | -0.060169 | 0.290050 | 0.510924 | 0.298010 | 0.482182 | 0.330000 | 0.247500 |
| anchor_16h_mean | V6_diagnostic_with_M4_area_diff | 50 | 0.365819 | 0.458262 | -0.049449 | 0.290803 | 0.550947 | 0.304423 | 0.452237 | 0.330000 | 0.227500 |
| anchor_16h_robust | V5_diagnostic_with_M3C | 50 | 0.372610 | 0.466705 | -0.059150 | 0.303285 | 0.535950 | 0.303757 | 0.448443 | 0.327500 | 0.222500 |
| anchor_16h_robust | V3_M1_plus_M3A_m1b_M3B_m1b | 50 | 0.373007 | 0.467168 | -0.059660 | 0.303953 | 0.534867 | 0.303704 | 0.448758 | 0.326250 | 0.221250 |
| anchor_16h_mean | V1_M1_shape_only | 50 | 0.373741 | 0.469609 | -0.053856 | 0.300364 | 0.570434 | 0.307993 | 0.422818 | 0.306250 | 0.207500 |
| anchor_16h_robust | V2_M1_plus_existing_M3A_M3B | 50 | 0.374476 | 0.469516 | -0.056343 | 0.305582 | 0.542990 | 0.304509 | 0.447368 | 0.317500 | 0.217500 |
| anchor_16h_robust | V6_diagnostic_with_M4_area_diff | 50 | 0.374758 | 0.468865 | -0.055920 | 0.305951 | 0.548579 | 0.304423 | 0.452237 | 0.330000 | 0.227500 |
| anchor_16h_median | V5_diagnostic_with_M3C | 50 | 0.376733 | 0.469670 | -0.060344 | 0.305460 | 0.528544 | 0.303757 | 0.448443 | 0.327500 | 0.222500 |
| anchor_16h_median | V3_M1_plus_M3A_m1b_M3B_m1b | 50 | 0.376992 | 0.469985 | -0.060745 | 0.305988 | 0.528860 | 0.303704 | 0.448758 | 0.326250 | 0.221250 |
| anchor_16h_median | V2_M1_plus_existing_M3A_M3B | 50 | 0.378014 | 0.471804 | -0.055943 | 0.307756 | 0.528434 | 0.304509 | 0.447368 | 0.317500 | 0.217500 |
| anchor_16h_median | V6_diagnostic_with_M4_area_diff | 50 | 0.378547 | 0.471123 | -0.059452 | 0.307741 | 0.545613 | 0.304423 | 0.452237 | 0.330000 | 0.227500 |
| anchor_16h_robust | V1_M1_shape_only | 50 | 0.387369 | 0.484432 | -0.061790 | 0.321811 | 0.564468 | 0.307993 | 0.422813 | 0.306250 | 0.207500 |
| anchor_16h_median | V1_M1_shape_only | 50 | 0.389366 | 0.485322 | -0.061466 | 0.321490 | 0.576682 | 0.307993 | 0.422813 | 0.306250 | 0.207500 |

# P0040 subset breakdown

| subset | variant | weeks | MAE | shape_MAE | top10 | bottom10 |
|---|---|---:|---:|---:|---:|---:|
| all_forecast_weeks | V0_naive_flat_week | 50 | 0.333955 | 0.287086 | 0.037500 | 0.091250 |
| all_forecast_weeks | V1_M1_shape_only | 50 | 0.373741 | 0.307993 | 0.306250 | 0.207500 |
| all_forecast_weeks | V2_M1_plus_existing_M3A_M3B | 50 | 0.365197 | 0.304509 | 0.317500 | 0.217500 |
| all_forecast_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 50 | 0.364194 | 0.303704 | 0.326250 | 0.221250 |
| all_forecast_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 50 | 0.353274 | 0.298010 | 0.330000 | 0.247500 |
| all_forecast_weeks | V5_diagnostic_with_M3C | 50 | 0.364172 | 0.303757 | 0.327500 | 0.222500 |
| all_forecast_weeks | V6_diagnostic_with_M4_area_diff | 50 | 0.365819 | 0.304423 | 0.330000 | 0.227500 |
| holiday_weeks | V0_naive_flat_week | 10 | 0.356680 | 0.293502 | 0.093750 | 0.118750 |
| holiday_weeks | V1_M1_shape_only | 10 | 0.375294 | 0.294264 | 0.237500 | 0.200000 |
| holiday_weeks | V2_M1_plus_existing_M3A_M3B | 10 | 0.326612 | 0.283716 | 0.268750 | 0.275000 |
| holiday_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 10 | 0.316764 | 0.277923 | 0.306250 | 0.275000 |
| holiday_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 10 | 0.311136 | 0.276172 | 0.312500 | 0.300000 |
| holiday_weeks | V5_diagnostic_with_M3C | 10 | 0.317579 | 0.278198 | 0.300000 | 0.275000 |
| holiday_weeks | V6_diagnostic_with_M4_area_diff | 10 | 0.315467 | 0.275754 | 0.312500 | 0.275000 |
| non_holiday_weeks | V0_naive_flat_week | 40 | 0.328273 | 0.285483 | 0.023438 | 0.084375 |
| non_holiday_weeks | V1_M1_shape_only | 40 | 0.373353 | 0.311426 | 0.323437 | 0.209375 |
| non_holiday_weeks | V2_M1_plus_existing_M3A_M3B | 40 | 0.374843 | 0.309707 | 0.329688 | 0.203125 |
| non_holiday_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 40 | 0.376051 | 0.310149 | 0.331250 | 0.207813 |
| non_holiday_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 40 | 0.363809 | 0.303469 | 0.334375 | 0.234375 |
| non_holiday_weeks | V5_diagnostic_with_M3C | 40 | 0.375820 | 0.310147 | 0.334375 | 0.209375 |
| non_holiday_weeks | V6_diagnostic_with_M4_area_diff | 40 | 0.378407 | 0.311591 | 0.334375 | 0.215625 |
| bridge_weeks | V0_naive_flat_week | 3 | 0.351026 | 0.275749 | 0.020833 | 0.000000 |
| bridge_weeks | V1_M1_shape_only | 3 | 0.295420 | 0.260663 | 0.333333 | 0.270833 |
| bridge_weeks | V2_M1_plus_existing_M3A_M3B | 3 | 0.287089 | 0.284261 | 0.312500 | 0.270833 |
| bridge_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 3 | 0.264940 | 0.268902 | 0.416667 | 0.270833 |
| bridge_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 3 | 0.271421 | 0.272244 | 0.437500 | 0.250000 |
| bridge_weeks | V5_diagnostic_with_M3C | 3 | 0.265185 | 0.269180 | 0.416667 | 0.270833 |
| bridge_weeks | V6_diagnostic_with_M4_area_diff | 3 | 0.264940 | 0.268902 | 0.416667 | 0.270833 |
| cold_weeks | V0_naive_flat_week | 16 | 0.371635 | 0.303656 | 0.039062 | 0.093750 |
| cold_weeks | V1_M1_shape_only | 16 | 0.367881 | 0.306816 | 0.320312 | 0.218750 |
| cold_weeks | V2_M1_plus_existing_M3A_M3B | 16 | 0.353731 | 0.299930 | 0.343750 | 0.250000 |
| cold_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 16 | 0.350219 | 0.297551 | 0.363281 | 0.261719 |
| cold_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 16 | 0.344263 | 0.294564 | 0.378906 | 0.257812 |
| cold_weeks | V5_diagnostic_with_M3C | 16 | 0.350147 | 0.297588 | 0.363281 | 0.261719 |
| cold_weeks | V6_diagnostic_with_M4_area_diff | 16 | 0.356617 | 0.302015 | 0.367188 | 0.261719 |
| warm_weeks | V0_naive_flat_week | 7 | 0.218426 | 0.189318 | 0.053571 | 0.017857 |
| warm_weeks | V1_M1_shape_only | 7 | 0.322872 | 0.263061 | 0.267857 | 0.151786 |
| warm_weeks | V2_M1_plus_existing_M3A_M3B | 7 | 0.325916 | 0.263194 | 0.276786 | 0.142857 |
| warm_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 7 | 0.326928 | 0.264238 | 0.276786 | 0.142857 |
| warm_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 7 | 0.321606 | 0.262107 | 0.267857 | 0.169643 |
| warm_weeks | V5_diagnostic_with_M3C | 7 | 0.325621 | 0.264080 | 0.285714 | 0.142857 |
| warm_weeks | V6_diagnostic_with_M4_area_diff | 7 | 0.329864 | 0.265610 | 0.276786 | 0.160714 |
| high_wind_weeks | V0_naive_flat_week | 50 | 0.333955 | 0.287086 | 0.037500 | 0.091250 |
| high_wind_weeks | V1_M1_shape_only | 50 | 0.373741 | 0.307993 | 0.306250 | 0.207500 |
| high_wind_weeks | V2_M1_plus_existing_M3A_M3B | 50 | 0.365197 | 0.304509 | 0.317500 | 0.217500 |
| high_wind_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 50 | 0.364194 | 0.303704 | 0.326250 | 0.221250 |
| high_wind_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 50 | 0.353274 | 0.298010 | 0.330000 | 0.247500 |
| high_wind_weeks | V5_diagnostic_with_M3C | 50 | 0.364172 | 0.303757 | 0.327500 | 0.222500 |
| high_wind_weeks | V6_diagnostic_with_M4_area_diff | 50 | 0.365819 | 0.304423 | 0.330000 | 0.227500 |
| high_solar_weeks | V0_naive_flat_week | 19 | 0.275931 | 0.243263 | 0.042763 | 0.078947 |
| high_solar_weeks | V1_M1_shape_only | 19 | 0.346539 | 0.281680 | 0.273026 | 0.207237 |
| high_solar_weeks | V2_M1_plus_existing_M3A_M3B | 19 | 0.335734 | 0.279021 | 0.282895 | 0.213816 |
| high_solar_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 19 | 0.334502 | 0.278515 | 0.286184 | 0.207237 |
| high_solar_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 19 | 0.330225 | 0.276241 | 0.279605 | 0.256579 |
| high_solar_weeks | V5_diagnostic_with_M3C | 19 | 0.334274 | 0.278582 | 0.286184 | 0.210526 |
| high_solar_weeks | V6_diagnostic_with_M4_area_diff | 19 | 0.335472 | 0.278578 | 0.289474 | 0.213816 |
| low_solar_weeks | V0_naive_flat_week | 19 | 0.362415 | 0.300153 | 0.042763 | 0.098684 |
| low_solar_weeks | V1_M1_shape_only | 19 | 0.347360 | 0.290449 | 0.335526 | 0.246711 |
| low_solar_weeks | V2_M1_plus_existing_M3A_M3B | 19 | 0.336084 | 0.284691 | 0.351974 | 0.259868 |
| low_solar_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 19 | 0.333912 | 0.283192 | 0.368421 | 0.276316 |
| low_solar_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 19 | 0.325691 | 0.277494 | 0.384868 | 0.292763 |
| low_solar_weeks | V5_diagnostic_with_M3C | 19 | 0.333868 | 0.283219 | 0.368421 | 0.276316 |
| low_solar_weeks | V6_diagnostic_with_M4_area_diff | 19 | 0.338622 | 0.286167 | 0.375000 | 0.279605 |
| summer_weeks | V0_naive_flat_week | 13 | 0.232103 | 0.204362 | 0.024038 | 0.072115 |
| summer_weeks | V1_M1_shape_only | 13 | 0.339107 | 0.273692 | 0.293269 | 0.225962 |
| summer_weeks | V2_M1_plus_existing_M3A_M3B | 13 | 0.340606 | 0.273697 | 0.307692 | 0.211538 |
| summer_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 13 | 0.341481 | 0.274330 | 0.307692 | 0.197115 |
| summer_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 13 | 0.339171 | 0.275845 | 0.298077 | 0.235577 |
| summer_weeks | V5_diagnostic_with_M3C | 13 | 0.340601 | 0.274372 | 0.312500 | 0.197115 |
| summer_weeks | V6_diagnostic_with_M4_area_diff | 13 | 0.343089 | 0.274944 | 0.307692 | 0.206731 |
| winter_weeks | V0_naive_flat_week | 13 | 0.322762 | 0.274073 | 0.048077 | 0.115385 |
| winter_weeks | V1_M1_shape_only | 13 | 0.339219 | 0.286297 | 0.331731 | 0.259615 |
| winter_weeks | V2_M1_plus_existing_M3A_M3B | 13 | 0.328746 | 0.282253 | 0.355769 | 0.278846 |
| winter_weeks | V3_M1_plus_M3A_m1b_M3B_m1b | 13 | 0.325514 | 0.280075 | 0.379808 | 0.278846 |
| winter_weeks | V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D | 13 | 0.329994 | 0.281357 | 0.384615 | 0.274038 |
| winter_weeks | V5_diagnostic_with_M3C | 13 | 0.325558 | 0.280104 | 0.379808 | 0.278846 |
| winter_weeks | V6_diagnostic_with_M4_area_diff | 13 | 0.329377 | 0.284205 | 0.379808 | 0.278846 |
