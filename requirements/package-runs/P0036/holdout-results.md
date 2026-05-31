# P0036 holdout results

## Identity

```text
package_id = P0036
model_version = m4_hgb_train_only_m1_v1
model_class = sklearn HistGradientBoostingRegressor
status = PASS
reason = P0036 HGB beats train-only M1 on recomposed SE3 holdout without area_diff blow-up
feature_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
model_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3
split = train<=2024-12-31, validate=2025, holdout>=2026
train_rows = 22729
validate_rows = 8760
holdout_rows = 3455
random_seed = 36
leakage_control = train_only_M1_m3ab_normalized fitted on train rows only
```

## Holdout hourly metrics

| variant | target | MAE | RMSE |
|---|---|---:|---:|
| P0036_HGB_residual | system_proxy_se1 | 0.394878 | 0.512292 |
| P0036_HGB_residual | area_diff_proxy_se3 | 0.220307 | 0.304649 |
| P0036_HGB_residual | recomposed_se3 | 0.377318 | 0.488575 |
| train_only_M1_m3ab_normalized | system_proxy_se1 | 0.382156 | 0.493545 |
| train_only_M1_m3ab_normalized | area_diff_proxy_se3 | 0.241108 | 0.350126 |
| train_only_M1_m3ab_normalized | recomposed_se3 | 0.402603 | 0.520408 |
| train_only_M1_raw_actual | system_proxy_se1 | 0.400824 | 0.507047 |
| train_only_M1_raw_actual | area_diff_proxy_se3 | 0.241958 | 0.350864 |
| train_only_M1_raw_actual | recomposed_se3 | 0.401715 | 0.520428 |
| full_period_M1_existing | system_proxy_se1 | 0.336856 | 0.476429 |
| full_period_M1_existing | area_diff_proxy_se3 | 0.202791 | 0.293229 |
| full_period_M1_existing | recomposed_se3 | 0.383175 | 0.497192 |

## Special-day subset

| variant | target | MAE | RMSE |
|---|---|---:|---:|
| P0036_HGB_residual | system_proxy_se1 | 0.275826 | 0.331108 |
| P0036_HGB_residual | area_diff_proxy_se3 | 0.181790 | 0.236783 |
| P0036_HGB_residual | recomposed_se3 | 0.335689 | 0.411224 |
| train_only_M1_m3ab_normalized | system_proxy_se1 | 0.287889 | 0.347771 |
| train_only_M1_m3ab_normalized | area_diff_proxy_se3 | 0.170480 | 0.262498 |
| train_only_M1_m3ab_normalized | recomposed_se3 | 0.323321 | 0.413098 |
| train_only_M1_raw_actual | system_proxy_se1 | 0.326552 | 0.386560 |
| train_only_M1_raw_actual | area_diff_proxy_se3 | 0.171992 | 0.263944 |
| train_only_M1_raw_actual | recomposed_se3 | 0.347162 | 0.436117 |
| full_period_M1_existing | system_proxy_se1 | 0.200806 | 0.288632 |
| full_period_M1_existing | area_diff_proxy_se3 | 0.149958 | 0.215974 |
| full_period_M1_existing | recomposed_se3 | 0.276567 | 0.368121 |

## Non-special-day subset

| variant | target | MAE | RMSE |
|---|---|---:|---:|
| P0036_HGB_residual | system_proxy_se1 | 0.406696 | 0.526889 |
| P0036_HGB_residual | area_diff_proxy_se3 | 0.224131 | 0.310578 |
| P0036_HGB_residual | recomposed_se3 | 0.381450 | 0.495596 |
| train_only_M1_m3ab_normalized | system_proxy_se1 | 0.391514 | 0.505729 |
| train_only_M1_m3ab_normalized | area_diff_proxy_se3 | 0.248119 | 0.357655 |
| train_only_M1_m3ab_normalized | recomposed_se3 | 0.410473 | 0.529876 |
| train_only_M1_raw_actual | system_proxy_se1 | 0.408196 | 0.517479 |
| train_only_M1_raw_actual | area_diff_proxy_se3 | 0.248904 | 0.358344 |
| train_only_M1_raw_actual | recomposed_se3 | 0.407130 | 0.528063 |
| full_period_M1_existing | system_proxy_se1 | 0.350361 | 0.491169 |
| full_period_M1_existing | area_diff_proxy_se3 | 0.208036 | 0.299814 |
| full_period_M1_existing | recomposed_se3 | 0.393758 | 0.508219 |

## Residual prediction distribution

| split | target | actual_mean | actual_min | actual_p50 | actual_p95 | actual_max | pred_mean | pred_min | pred_p50 | pred_p95 | pred_max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | system_proxy_se1 | 0.121234 | -1.476666 | 0.000000 | 0.974497 | 5.435676 | 0.121277 | -0.369350 | 0.044409 | 0.816631 | 2.918558 |
| train | area_diff_proxy_se3 | 0.232074 | -1.403160 | 0.000000 | 1.587820 | 8.135580 | 0.232852 | 0.111280 | 0.111280 | 0.807088 | 3.672301 |
| validate | system_proxy_se1 | -0.165047 | -1.475976 | -0.198536 | 0.444794 | 2.489670 | -0.067777 | -0.369350 | -0.058259 | 0.041519 | 0.144915 |
| validate | area_diff_proxy_se3 | 0.274505 | -1.324960 | 0.210560 | 1.012760 | 4.269770 | 0.111280 | 0.111280 | 0.111280 | 0.111280 | 0.111280 |
| holdout | system_proxy_se1 | 0.103502 | -0.879956 | -0.015258 | 0.960006 | 3.616690 | -0.032533 | -0.135646 | -0.031042 | 0.066176 | 0.140700 |
| holdout | area_diff_proxy_se3 | 0.189435 | -1.020385 | 0.118885 | 0.721758 | 1.777827 | 0.111280 | 0.111280 | 0.111280 | 0.111280 | 0.111280 |

## Largest holdout errors

### SE1

| local_date | hour | special_day_type | actual | train_only_M1 | M4_pred | abs_error | signed_error |
|---|---:|---|---:|---:|---:|---:|---:|
| 2026-02-19 | 8 | normal_weekday | 4.114526 | 0.497836 | 0.468924 | 3.645601 | -3.645601 |
| 2026-02-19 | 7 | normal_weekday | 3.441816 | 0.496326 | 0.467415 | 2.974401 | -2.974401 |
| 2026-02-19 | 9 | normal_weekday | 3.419153 | 0.492212 | 0.463301 | 2.955852 | -2.955852 |
| 2026-02-10 | 9 | normal_weekday | 3.339118 | 0.510062 | 0.481151 | 2.857967 | -2.857967 |
| 2026-02-10 | 8 | normal_weekday | 3.257931 | 0.499902 | 0.470991 | 2.786940 | -2.786940 |
| 2026-02-10 | 18 | normal_weekday | 2.875148 | 0.531476 | 0.502565 | 2.372584 | -2.372584 |
| 2026-02-10 | 7 | normal_weekday | 2.805353 | 0.475942 | 0.447031 | 2.358322 | -2.358322 |
| 2026-02-10 | 17 | normal_weekday | 2.848338 | 0.540901 | 0.511990 | 2.336349 | -2.336349 |
| 2026-01-20 | 16 | normal_weekday | 2.852857 | 0.578908 | 0.527052 | 2.325805 | -2.325805 |
| 2026-02-10 | 10 | normal_weekday | 2.803701 | 0.512917 | 0.484006 | 2.319695 | -2.319695 |
| 2026-01-20 | 8 | normal_weekday | 2.780600 | 0.625451 | 0.573596 | 2.207004 | -2.207004 |
| 2026-01-20 | 17 | normal_weekday | 2.677252 | 0.586288 | 0.534432 | 2.142820 | -2.142820 |
| 2026-02-09 | 17 | normal_weekday | 2.588640 | 0.487771 | 0.458860 | 2.129780 | -2.129780 |
| 2026-05-07 | 20 | normal_weekday | 2.284673 | 0.286857 | 0.255634 | 2.029038 | -2.029038 |
| 2026-02-10 | 11 | normal_weekday | 2.537726 | 0.540307 | 0.511396 | 2.026330 | -2.026330 |
| 2026-02-10 | 12 | normal_weekday | 2.538741 | 0.547344 | 0.518432 | 2.020308 | -2.020308 |
| 2026-01-20 | 7 | normal_weekday | 2.457335 | 0.563051 | 0.511196 | 1.946139 | -1.946139 |
| 2026-02-10 | 16 | normal_weekday | 2.427163 | 0.532089 | 0.503177 | 1.923986 | -1.923986 |
| 2026-02-19 | 10 | normal_weekday | 2.338033 | 0.464158 | 0.435246 | 1.902787 | -1.902787 |
| 2026-01-20 | 9 | normal_weekday | 2.364730 | 0.639786 | 0.587931 | 1.776799 | -1.776799 |

### Area Diff

| local_date | hour | special_day_type | actual | train_only_M1 | M4_pred | abs_error | signed_error |
|---|---:|---|---:|---:|---:|---:|---:|
| 2026-03-09 | 18 | normal_weekday | 1.955422 | 0.177595 | 0.288875 | 1.666547 | -1.666547 |
| 2026-03-19 | 19 | normal_weekday | 1.710655 | 0.029561 | 0.140842 | 1.569813 | -1.569813 |
| 2026-04-29 | 20 | normal_weekday | 1.662867 | 0.047856 | 0.159136 | 1.503731 | -1.503731 |
| 2026-03-20 | 7 | normal_weekday | 1.607868 | 0.000631 | 0.111912 | 1.495956 | -1.495956 |
| 2026-03-19 | 18 | normal_weekday | 1.653275 | 0.049756 | 0.161037 | 1.492238 | -1.492238 |
| 2026-03-20 | 6 | normal_weekday | 1.497067 | 0.000000 | 0.111280 | 1.385787 | -1.385787 |
| 2026-03-18 | 18 | normal_weekday | 1.596335 | 0.114650 | 0.225930 | 1.370405 | -1.370405 |
| 2026-03-09 | 17 | normal_weekday | 1.492428 | 0.081220 | 0.192500 | 1.299927 | -1.299927 |
| 2026-03-18 | 19 | normal_weekday | 1.502605 | 0.102805 | 0.214085 | 1.288520 | -1.288520 |
| 2026-04-29 | 21 | normal_weekday | 1.444853 | 0.049446 | 0.160726 | 1.284126 | -1.284126 |
| 2026-04-30 | 19 | normal_weekday | 1.353680 | 0.003357 | 0.114638 | 1.239042 | -1.239042 |
| 2026-03-19 | 6 | normal_weekday | 1.323250 | 0.000631 | 0.111912 | 1.211338 | -1.211338 |
| 2026-03-18 | 20 | normal_weekday | 1.312040 | 0.000000 | 0.111280 | 1.200760 | -1.200760 |
| 2026-03-17 | 7 | normal_weekday | 1.314705 | 0.006265 | 0.117545 | 1.197160 | -1.197160 |
| 2026-03-19 | 20 | normal_weekday | 1.288340 | 0.000631 | 0.111912 | 1.176428 | -1.176428 |
| 2026-03-20 | 18 | normal_weekday | 1.286198 | 0.000000 | 0.111280 | 1.174917 | -1.174917 |
| 2026-04-30 | 7 | normal_weekday | 1.284023 | 0.000000 | 0.111280 | 1.172742 | -1.172742 |
| 2026-01-08 | 15 | normal_weekday | 1.491232 | 0.213030 | 0.324310 | 1.166922 | -1.166922 |
| 2026-04-27 | 7 | normal_weekday | 1.426038 | 0.167910 | 0.279190 | 1.146847 | -1.146847 |
| 2026-02-03 | 17 | normal_weekday | -0.556705 | 0.463680 | 0.574960 | 1.131665 | 1.131665 |

## Not applicable

M5/M6/M7 forecast-time temperature/API metrics are out of scope for P0036.
