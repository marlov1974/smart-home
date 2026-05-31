# P0039 full-year holdout results

| holdout_year | variant | target | MAE | RMSE | signed_error | MAE_delta_vs_M1 | MAE_delta_vs_previous_variant |
|---:|---|---|---:|---:|---:|---:|---:|
| 2025 | M1 | system_proxy_se1 | 0.371326 | 0.474105 | 0.286880 | 0.000000 | 0.000000 |
| 2025 | M1 | area_diff_proxy_se3 | 0.324620 | 0.488786 | -0.218774 | 0.000000 | 0.000000 |
| 2025 | M1 | recomposed_se3 | 0.384666 | 0.521048 | 0.068106 | 0.000000 | 0.000000 |
| 2025 | M1B_training_base_only | system_proxy_se1 | 0.395991 | 0.518789 | 0.314199 | 0.024664 | 0.024664 |
| 2025 | M1B_training_base_only | area_diff_proxy_se3 | 0.327647 | 0.493348 | -0.196476 | 0.003027 | 0.003027 |
| 2025 | M1B_training_base_only | recomposed_se3 | 0.422423 | 0.587098 | 0.117723 | 0.037758 | 0.037758 |
| 2025 | M1_existing_M3A_M3B | system_proxy_se1 | 0.357308 | 0.457318 | 0.268070 | -0.014018 | -0.038683 |
| 2025 | M1_existing_M3A_M3B | area_diff_proxy_se3 | 0.324600 | 0.488847 | -0.218047 | -0.000020 | -0.003046 |
| 2025 | M1_existing_M3A_M3B | recomposed_se3 | 0.374846 | 0.511458 | 0.050023 | -0.009819 | -0.047577 |
| 2025 | M1_M3A_m1b | system_proxy_se1 | 0.361636 | 0.460286 | 0.273674 | -0.009691 | 0.004328 |
| 2025 | M1_M3A_m1b | area_diff_proxy_se3 | 0.324620 | 0.488786 | -0.218774 | 0.000000 | 0.000020 |
| 2025 | M1_M3A_m1b | recomposed_se3 | 0.376722 | 0.511981 | 0.054900 | -0.007944 | 0.001876 |
| 2025 | M1_M3A_m1b_M3B_m1b | system_proxy_se1 | 0.356132 | 0.455309 | 0.264845 | -0.015194 | -0.005503 |
| 2025 | M1_M3A_m1b_M3B_m1b | area_diff_proxy_se3 | 0.325359 | 0.489380 | -0.219541 | 0.000739 | 0.000739 |
| 2025 | M1_M3A_m1b_M3B_m1b | recomposed_se3 | 0.372997 | 0.509537 | 0.045304 | -0.011669 | -0.003725 |
