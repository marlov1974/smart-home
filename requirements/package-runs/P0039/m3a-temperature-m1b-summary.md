# P0039 M3A M1B temperature summary

| target | bucket | rows | delta_median | avg_model_delta |
|---|---|---:|---:|---:|
| system_proxy_se1 | extreme_cold | 56 | -0.264650 | 0.256348 |
| system_proxy_se1 | cold | 1145 | -0.232410 | 0.007991 |
| system_proxy_se1 | normal | 4672 | -0.232454 | 0.000000 |
| system_proxy_se1 | warm | 2574 | -0.405489 | -0.027367 |
| system_proxy_se1 | extreme_warm | 313 | -0.882020 | -0.219627 |
| area_diff_proxy_se3 | extreme_cold | 87 | 0.156015 | 0.000000 |
| area_diff_proxy_se3 | cold | 1408 | 0.227035 | 0.000000 |
| area_diff_proxy_se3 | normal | 6167 | 0.194080 | 0.000000 |
| area_diff_proxy_se3 | warm | 1001 | 0.053090 | 0.000000 |
| area_diff_proxy_se3 | extreme_warm | 97 | 0.060080 | 0.000000 |

M3A_m1b target formula: `actual - M1B`, fitted on holiday-clean train rows only.
