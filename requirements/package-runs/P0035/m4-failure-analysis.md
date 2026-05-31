# P0035 M4 failure analysis

## Scope

Analysis-only P0035/P0036-prep. No production model, M6/API, Shelly, Home Assistant, KVS or device calls.

Local inputs inspected:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
/Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3
```

## Summary

P0035 M4 is worse than M1 for three separate reasons:

1. M1 is advantaged by leakage: `m1_normal_price_v1` is built from the full local period, including 2026 holdout.
2. Even after recomputing a train-only M1-like baseline, M1 still beats P0035 M4. Leakage helps M1, but does not explain the M4 failure.
3. The P0035 M4 residual model is the main failure. It uses polynomial Ridge over calendar features, including `days_since_start_scaled`. For `area_diff_proxy_se3`, the fitted polynomial extrapolates holdout residuals to about `+1.95` when actual holdout residual mean is about `+0.13`, creating errors near `3.0`.

The residual target formula is broadly correct, but the feature/model class is not appropriate for the target. M3B is modestly helpful on special-day holdout, but the current evaluation adds M3B to both prediction and target, so global error is unchanged by addback.

## Target Definitions

P0035 feature target table:

```text
m3ab_normalized_prices
```

P0035 M4 loader in `src/mac/services/spotprice_ml_model/core.py` reads:

```sql
SELECT
  m3ab_normalized_price_se1 - normal_price_v1_se1 AS target_se1,
  m3ab_normalized_area_diff - normal_price_v1_area_diff AS target_area_diff,
  m3ab_normalized_se3 - normal_price_v1_se1 - normal_price_v1_area_diff AS target_se3,
  normal_price_v1_se1 AS baseline_se1,
  normal_price_v1_area_diff AS baseline_area_diff,
  m3b_special_day_delta_se1,
  m3b_special_day_delta_area_diff
FROM m3ab_normalized_prices
```

Feature-builder formulas:

```text
M3A_se1 = m3a_temperature_delta_se1
M3A_area = m3a_temperature_delta_area_diff
M3B_se1 = m3b_special_day_delta_se1
M3B_area = m3b_special_day_delta_area_diff

m3ab_normalized_price_se1 = actual_se1 - M3A_se1 - M3B_se1
m3ab_normalized_area_diff = actual_area_diff - M3A_area - M3B_area

M4 residual target SE1 = m3ab_normalized_price_se1 - M1_se1
M4 residual target area = m3ab_normalized_area_diff - M1_area

M4 normalized prediction SE1 = M1_se1 + predicted_residual_se1
M4 normalized prediction area = M1_area + predicted_residual_area
```

Example holdout rows:

| utc_hour_start | local_date | hour | actual_se1 | M1_se1 | M3A_se1 | M3B_se1 | m3ab_se1 | actual_area | M1_area | M3A_area | M3B_area | m3ab_area | special_day_type |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2025-12-31T23:00Z | 2026-01-01 | 0 | 0.286735 | 0.280681 | 0.113984 | -0.181778 | 0.354528 | 0.120035 | 0.0 | 0.0 | -0.042728 | 0.162763 | fixed_public_holiday |
| 2026-01-01T00:00Z | 2026-01-01 | 1 | 0.235885 | 0.272995 | 0.113984 | -0.181778 | 0.303678 | 0.104912 | 0.0 | 0.0 | -0.042728 | 0.147640 | fixed_public_holiday |
| 2026-01-01T01:00Z | 2026-01-01 | 2 | 0.153900 | 0.275195 | 0.113984 | -0.181778 | 0.221693 | 0.036372 | 0.0 | 0.0 | -0.042728 | 0.079100 | fixed_public_holiday |

Interpretation: the residual target is correctly formed from M3AB minus M1. The problem is not a simple sign inversion in the target formula.

## Holdout Fairness

Current M1 baseline is not strict out-of-sample. `compute_m1_calm_normal_price(...)` builds normal buckets over all rows passed into the feature build. The local P0035 build used the full available interval through `2026-05-24`, so holdout dates influence their own M1 calendar medians.

This means the current M1-vs-M4 holdout comparison is not fully fair.

Train-only M1-like recomputation still beats P0035 M4:

| baseline variant | holdout MAE vs M3AB target |
|---|---:|
| SE1 train-only M1 from raw actual | 0.4008237064627432 |
| SE1 train-only M1 from M3AB-normalized target | 0.3821561815264117 |
| SE1 full-period M1 | 0.33685564669429213 |
| SE1 P0035 M4 | 0.6079521874402215 |
| area train-only M1 from raw actual | 0.2419584103138793 |
| area train-only M1 from M3AB-normalized target | 0.24110757561494914 |
| area full-period M1 | 0.20279122565396646 |
| area P0035 M4 | 1.8269617292981122 |

Conclusion: M1 is favored by leakage, but M4 remains much worse than a train-only M1-like baseline, especially for `area_diff_proxy_se3`.

## Residual Distribution

Residual here means:

```text
m3ab_normalized_target - M1
```

| split | target | count | mean | std | min | p1 | p5 | p50 | p95 | p99 | max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | SE1 | 22729 | 0.185785 | 0.551259 | -1.169736 | -0.489956 | -0.256790 | 0.045525 | 1.060460 | 2.656552 | 5.658871 |
| train | area_diff | 22729 | 0.192921 | 0.738248 | -0.871675 | -0.425779 | -0.275073 | 0.000000 | 1.564926 | 3.636166 | 7.783650 |
| validate | SE1 | 8760 | -0.097621 | 0.305212 | -1.161321 | -0.671805 | -0.476299 | -0.125305 | 0.477656 | 1.005554 | 2.557460 |
| validate | area_diff | 8760 | 0.231854 | 0.358384 | -0.845305 | -0.342435 | -0.132874 | 0.159257 | 0.898772 | 1.467248 | 4.050455 |
| holdout | SE1 | 3455 | 0.185493 | 0.438836 | -0.652749 | -0.474645 | -0.335573 | 0.051916 | 0.968199 | 1.448252 | 3.651976 |
| holdout | area_diff | 3455 | 0.126159 | 0.264702 | -0.939805 | -0.406679 | -0.250548 | 0.064346 | 0.593389 | 0.967680 | 1.583662 |

Per year:

| year | target | count | mean | std | min | p50 | p95 | p99 | max |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | SE1 | 5185 | 0.58056 | 0.92806 | -0.43596 | 0.20355 | 2.55131 | 4.17270 | 5.65887 |
| 2022 | area_diff | 5185 | 0.73041 | 1.30463 | -0.67417 | 0.00000 | 3.37023 | 5.73235 | 7.78365 |
| 2023 | SE1 | 8760 | 0.14815 | 0.29675 | -0.88647 | 0.07055 | 0.70658 | 1.11517 | 2.43645 |
| 2023 | area_diff | 8760 | 0.04176 | 0.28638 | -0.63008 | 0.00000 | 0.65931 | 1.19959 | 2.32200 |
| 2024 | SE1 | 8784 | -0.00971 | 0.24181 | -1.16974 | -0.01325 | 0.34484 | 0.63411 | 5.06856 |
| 2024 | area_diff | 8784 | 0.02640 | 0.32050 | -0.87167 | 0.00000 | 0.50212 | 1.17468 | 7.68754 |
| 2025 | SE1 | 8760 | -0.09762 | 0.30521 | -1.16132 | -0.12530 | 0.47766 | 1.00555 | 2.55746 |
| 2025 | area_diff | 8760 | 0.23185 | 0.35838 | -0.84530 | 0.15926 | 0.89877 | 1.46725 | 4.05045 |
| 2026 | SE1 | 3455 | 0.18549 | 0.43884 | -0.65275 | 0.05192 | 0.96820 | 1.44825 | 3.65198 |
| 2026 | area_diff | 3455 | 0.12616 | 0.26470 | -0.93981 | 0.06435 | 0.59339 | 0.96768 | 1.58366 |

Per holdout month:

| month | target | count | mean | std | min | p50 | p95 | p99 | max |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | SE1 | 744 | 0.29754 | 0.44141 | -0.65275 | 0.31156 | 1.02545 | 1.50867 | 2.18202 |
| 1 | area_diff | 744 | 0.05079 | 0.26735 | -0.72983 | 0.00537 | 0.57466 | 0.99029 | 1.25863 |
| 2 | SE1 | 672 | 0.43405 | 0.50369 | -0.53542 | 0.37607 | 1.21574 | 2.27936 | 3.65198 |
| 2 | area_diff | 672 | -0.01156 | 0.19841 | -0.93981 | -0.00386 | 0.35187 | 0.50517 | 0.66604 |
| 3 | SE1 | 743 | -0.09997 | 0.17001 | -0.52125 | -0.10059 | 0.19246 | 0.49198 | 0.72164 |
| 3 | area_diff | 743 | 0.22734 | 0.27134 | -0.48900 | 0.19657 | 0.76278 | 1.10896 | 1.58366 |
| 4 | SE1 | 720 | -0.05953 | 0.25485 | -0.62488 | -0.09019 | 0.50546 | 0.75896 | 0.92934 |
| 4 | area_diff | 720 | 0.22380 | 0.25596 | -0.36379 | 0.18297 | 0.74349 | 1.06244 | 1.26407 |
| 5 | SE1 | 576 | 0.42528 | 0.40378 | -0.33500 | 0.37374 | 1.16919 | 1.42923 | 2.04580 |
| 5 | area_diff | 576 | 0.13160 | 0.22483 | -0.59063 | 0.06378 | 0.53782 | 0.60707 | 0.68380 |

Special vs non-special holdout:

| subset | target | rows | M4 MAE | M1 MAE |
|---|---|---:|---:|---:|
| special | SE1 | 312 | 0.5427799929122432 | 0.20080614568519725 |
| special | area_diff | 312 | 1.8599008355085278 | 0.1499576029950441 |
| non_special | SE1 | 3143 | 0.6144217148639353 | 0.3503610378221438 |
| non_special | area_diff | 3143 | 1.8236919230182347 | 0.2080359250715878 |

## Area Diff Problem

Component distributions:

| split | component | count | mean | std | min | p50 | p95 | p99 | max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | actual_area_diff | 22729 | 0.28519 | 0.76076 | -0.60911 | 0.00000 | 1.69153 | 3.85743 | 8.15277 |
| train | M1_area_diff | 22729 | 0.08573 | 0.13103 | 0.00000 | 0.00453 | 0.36943 | 0.51538 | 0.87167 |
| train | M3A_area_delta | 22729 | 0.00656 | 0.02156 | -0.00126 | 0.00000 | 0.04459 | 0.04459 | 0.18591 |
| train | M3B_area_delta | 22729 | -0.00002 | 0.01421 | -0.12102 | 0.00000 | 0.00000 | 0.00051 | 0.35000 |
| train | residual_target | 22729 | 0.19292 | 0.73825 | -0.87167 | 0.00000 | 1.56493 | 3.63617 | 7.78365 |
| validate | residual_target | 8760 | 0.23185 | 0.35838 | -0.84530 | 0.15926 | 0.89877 | 1.46725 | 4.05045 |
| holdout | residual_target | 3455 | 0.12616 | 0.26470 | -0.93981 | 0.06435 | 0.59339 | 0.96768 | 1.58366 |

Model predicted residual distributions show the real failure:

| split | target | predicted residual mean | predicted min | predicted p50 | predicted p95 | predicted max | actual residual mean | actual residual max |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| train | SE1 | 0.18578 | -0.84542 | 0.12463 | 0.87047 | 1.63812 | 0.18578 | 5.65887 |
| train | area_diff | 0.19292 | -0.54275 | 0.07342 | 1.12438 | 2.39703 | 0.19292 | 7.78365 |
| validate | area_diff | 0.65678 | -0.26543 | 0.60204 | 1.44439 | 2.02604 | 0.23185 | 4.05045 |
| holdout | area_diff | 1.95310 | 0.85180 | 1.96180 | 2.58713 | 2.98837 | 0.12616 | 1.58366 |

The area target is not simply broken. Actual holdout area residuals are moderate. The model predicts a massive positive residual for nearly every holdout row.

Top coefficients in the area model include large terms on `days_since_start_scaled`:

| feature term | coefficient |
|---|---:|
| days_since_start_scaled^2 | 5.149586566015636 |
| days_since_start_scaled | -1.8458960063126535 |
| intercept days_since_start_scaled | -1.8458960063123644 |
| month_cos days_since_start_scaled | 1.5262542483216954 |
| week_of_month days_since_start_scaled | -1.183748276634047 |

This is the direct mechanism for the area_diff blow-up: a polynomial model trained on 2022-2024 extrapolates into 2026 using a squared time feature. The input also includes a constant `intercept` feature while Ridge also uses `fit_intercept=True`; polynomial expansion then duplicates intercept-like terms and interactions.

M3A/M3B signs are not the main area failure. M3A area deltas are tiny in holdout (`mean 0.00666`, max `0.04459`), and M3B area deltas are mostly zero in holdout (`mean -0.00131`, max `0.0`, min `-0.07999`).

## M3B Effect

Special-day holdout M3B effect:

| target | rows | M1 MAE before M3B | M1 + M3B MAE | mean M3B delta |
|---|---:|---:|---:|---:|
| SE1 | 312 | 0.2708146854967948 | 0.20080614568519725 | 0.006389871646735519 |
| area_diff | 312 | 0.15556660256410257 | 0.1499576029950441 | -0.01445442905623789 |

M3B helps on special-day holdout, especially SE1. It is not the source of the M4 failure.

However, the P0035 `holdout-results.md` addback comparison is not very informative because it adds M3B to both `eval_prediction` and `eval_target`. That preserves identical absolute error. For raw observed evaluation, future packages should compare:

```text
raw_target = actual
raw_prediction = M1 + M3A_forecast_or_observed_delta + M3B_delta + M4_residual
```

P0035 cannot do true forecast-time temperature evaluation because M5 is not built.

## Model Features

Current M4 feature matrix:

```text
intercept
hour_sin
hour_cos
weekday_sin
weekday_cos
day_of_year_sin
day_of_year_cos
iso_week_sin
iso_week_cos
month_sin
month_cos
is_weekend
week_of_month
days_since_start_scaled
```

Missing for the stated P0035 goal:

- target-specific trend features
- robust year/regime level features
- market-level index or smoothed trailing normalized-price level
- separate SE1 vs area_diff trend controls
- holiday-normalized trend features
- monotonic or bounded trend handling

The only long-run feature is `days_since_start_scaled`. With degree-2 polynomial expansion it becomes an extrapolating time parabola. That is unsafe for residual forecasting.

## Model Class Controls

Small controls using the current M4 feature matrix:

| candidate | target | elapsed | holdout residual MAE |
|---|---|---:|---:|
| Ridge | SE1 | 0.0174s | 0.7506802571935143 |
| HGB max_iter=50 | SE1 | 0.2833s | 0.38624856314668077 |
| HGB max_iter=100 | SE1 | 0.5328s | 0.40628133321576404 |
| Ridge | area_diff | 0.0106s | 0.8476434366786488 |
| HGB max_iter=50 | area_diff | 0.2452s | 0.2827911392627795 |
| HGB max_iter=100 | area_diff | 0.4543s | 0.2844308117690702 |

HGB does not hang at these bounded settings. The earlier long run was likely parameterization/runtime handling rather than an inherent blocker. HGB is much better than Ridge for residuals, but still not enough to beat fair M1 on area_diff without better features/target handling.

## Top 20 Holdout Errors: SE1

| local_date | hour | special_day_type | actual | M1 | M3A | M3B | M4_pred | abs_error | signed_error |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-02-19 | 07 | normal_weekday | 4.11453 | 0.46255 | 0.11398 | 0.0 | -0.02032 | 4.13484 | 4.13484 |
| 2026-02-19 | 08 | normal_weekday | 3.41915 | 0.49834 | 0.11398 | 0.0 | -0.02888 | 3.44803 | 3.44803 |
| 2026-02-10 | 08 | normal_weekday | 3.33912 | 0.52575 | 0.11398 | 0.0 | -0.09607 | 3.43519 | 3.43519 |
| 2026-02-19 | 06 | normal_weekday | 3.44182 | 0.46945 | 0.11398 | 0.0 | 0.03247 | 3.40934 | 3.40934 |
| 2026-02-10 | 07 | normal_weekday | 3.25793 | 0.45575 | 0.11398 | 0.0 | -0.12911 | 3.38704 | 3.38704 |
| 2026-01-20 | 07 | normal_weekday | 2.78060 | 0.59857 | 0.0 | 0.0 | -0.17301 | 2.95361 | 2.95361 |
| 2026-02-10 | 09 | normal_weekday | 2.80370 | 0.52611 | 0.11398 | 0.0 | -0.12683 | 2.93053 | 2.93053 |
| 2026-01-20 | 15 | normal_weekday | 2.85286 | 0.71559 | 0.0 | 0.0 | -0.06778 | 2.92064 | 2.92064 |
| 2026-02-10 | 06 | normal_weekday | 2.80535 | 0.44312 | 0.11398 | 0.0 | -0.10187 | 2.90723 | 2.90723 |
| 2026-01-20 | 16 | normal_weekday | 2.67725 | 0.63133 | 0.0 | 0.0 | -0.09694 | 2.77419 | 2.77419 |
| 2026-02-10 | 16 | normal_weekday | 2.84834 | 0.59588 | 0.11398 | 0.0 | 0.07781 | 2.77053 | 2.77053 |
| 2026-02-10 | 17 | normal_weekday | 2.87515 | 0.59147 | 0.11398 | 0.0 | 0.13085 | 2.74430 | 2.74430 |
| 2026-02-10 | 10 | normal_weekday | 2.53773 | 0.55385 | 0.11398 | 0.0 | -0.12099 | 2.65871 | 2.65871 |
| 2026-01-20 | 06 | normal_weekday | 2.45734 | 0.53617 | 0.0 | 0.0 | -0.19329 | 2.65062 | 2.65062 |
| 2026-02-10 | 11 | normal_weekday | 2.53874 | 0.58766 | 0.11398 | 0.0 | -0.09663 | 2.63537 | 2.63537 |
| 2026-01-20 | 08 | normal_weekday | 2.36473 | 0.62056 | 0.0 | 0.0 | -0.19089 | 2.55562 | 2.55562 |
| 2026-02-09 | 16 | normal_weekday | 2.58864 | 0.36925 | 0.0 | 0.0 | 0.14202 | 2.44662 | 2.44662 |
| 2026-02-10 | 15 | normal_weekday | 2.42716 | 0.60115 | 0.11398 | 0.0 | 0.02756 | 2.39960 | 2.39960 |
| 2026-02-19 | 09 | normal_weekday | 2.33803 | 0.51754 | 0.11398 | 0.0 | -0.04904 | 2.38708 | 2.38708 |
| 2026-01-27 | 16 | normal_weekday | 2.19322 | 0.56889 | 0.11398 | 0.0 | -0.01003 | 2.20325 | 2.20325 |

## Top 20 Holdout Errors: Area Diff

| local_date | hour | special_day_type | actual | M1 | M3A | M3B | M4_pred | abs_error | signed_error |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-05 | 00 | movable_public_holiday | -0.05583 | 0.0 | 0.0 | -0.01504 | 2.98837 | 3.04420 | -3.04420 |
| 2026-04-05 | 01 | movable_public_holiday | -0.05012 | 0.0 | 0.0 | -0.01504 | 2.98680 | 3.03692 | -3.03692 |
| 2026-04-05 | 23 | movable_public_holiday | -0.05859 | 0.0 | 0.0 | -0.01504 | 2.96680 | 3.02539 | -3.02539 |
| 2026-05-02 | 01 | normal_saturday | 0.0 | 0.03279 | 0.0 | 0.0 | 3.00840 | 3.00840 | -3.00840 |
| 2026-04-05 | 02 | movable_public_holiday | -0.04739 | 0.0 | 0.0 | -0.01504 | 2.96060 | 3.00799 | -3.00799 |
| 2026-05-02 | 00 | normal_saturday | 0.0 | 0.02735 | 0.0 | 0.0 | 2.99990 | 2.99990 | -2.99990 |
| 2026-05-02 | 23 | normal_saturday | 0.0 | 0.04434 | 0.0 | 0.0 | 2.99118 | 2.99118 | -2.99118 |
| 2026-04-05 | 22 | movable_public_holiday | -0.05764 | 0.0 | 0.0 | -0.01504 | 2.92178 | 2.97942 | -2.97942 |
| 2026-05-02 | 22 | normal_saturday | 0.0 | 0.07105 | 0.0 | 0.0 | 2.96952 | 2.96952 | -2.96952 |
| 2026-05-02 | 02 | normal_saturday | 0.0 | 0.00339 | 0.0 | 0.0 | 2.95761 | 2.95761 | -2.95761 |
| 2026-04-05 | 03 | movable_public_holiday | -0.04477 | 0.0 | 0.0 | -0.01504 | 2.90700 | 2.95177 | -2.95177 |
| 2026-04-04 | 01 | special_weekend_day | -0.00858 | 0.0 | 0.0 | 0.0 | 2.94144 | 2.95002 | -2.95002 |
| 2026-04-04 | 02 | special_weekend_day | -0.01985 | 0.0 | 0.0 | 0.0 | 2.91706 | 2.93692 | -2.93692 |
| 2026-05-03 | 01 | normal_sunday | 0.0 | 0.0 | 0.0 | 0.0 | 2.92140 | 2.92140 | -2.92140 |
| 2026-05-03 | 00 | normal_sunday | 0.0 | 0.0 | 0.0 | 0.0 | 2.91986 | 2.91986 | -2.91986 |
| 2026-05-02 | 03 | normal_saturday | 0.0 | 0.0 | 0.0 | 0.0 | 2.90529 | 2.90529 | -2.90529 |
| 2026-05-03 | 02 | normal_sunday | 0.0 | 0.0 | 0.0 | 0.0 | 2.89776 | 2.89776 | -2.89776 |
| 2026-04-05 | 20 | movable_public_holiday | -0.03805 | 0.10293 | 0.0 | -0.01504 | 2.85799 | 2.89604 | -2.89604 |
| 2026-05-03 | 23 | normal_sunday | 0.00100 | 0.00050 | 0.0 | 0.0 | 2.89535 | 2.89435 | -2.89435 |
| 2026-04-04 | 03 | special_weekend_day | -0.01237 | 0.0 | 0.0 | 0.0 | 2.86624 | 2.87860 | -2.87860 |

## Holdout Error By Month

| month | rows | SE1 M4 MAE | SE1 M1 MAE | area M4 MAE | area M1 MAE |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 744 | 0.93492 | 0.41608 | 1.69344 | 0.18006 |
| 2026-02 | 672 | 0.79028 | 0.49981 | 2.04525 | 0.13729 |
| 2026-03 | 743 | 0.36669 | 0.15206 | 1.82903 | 0.26090 |
| 2026-04 | 720 | 0.49706 | 0.19975 | 1.79884 | 0.24263 |
| 2026-05 | 576 | 0.42274 | 0.45416 | 1.77724 | 0.18381 |

## Conclusions

### Is M1 vs M4 comparison correct?

Partly. It is correct for measuring the current local artifacts, but not as a strict out-of-sample benchmark because M1, M3A and M3B were all fit on the full period including holdout. P0036 should implement time-split-safe normalizer rebuilding for honest model comparison.

### Is M1 favored by leakage?

Yes. Full-period M1 holdout MAE is better than train-only M1-like baselines:

```text
SE1 full-period M1: 0.3369 vs train-only 0.3822-0.4008
area full-period M1: 0.2028 vs train-only 0.2411-0.2420
```

But leakage is not enough to explain M4 failure. Train-only M1 still beats P0035 M4 by a wide margin.

### Is the M4 target right?

The formula is right for P0035's intended normalized residual:

```text
M4_target = actual - M3A - M3B - M1
```

But the current implementation has two evaluation/modeling weaknesses:

1. Evaluation columns called `actual_*` in `m4_hourly_predictions` are M3AB-normalized actuals, not raw observed actual prices.
2. M3B addback currently adds the same value to prediction and target, so it cannot change error. It only demonstrates recomposition algebra, not raw-price forecast skill.

### Is area_diff target broken or just hard?

The area_diff target is difficult and has spikes, especially in 2022 training, but the catastrophic holdout error is model-induced. P0035 polynomial Ridge predicts holdout area residual around `+1.95` even though actual holdout residual mean is `+0.13`. That comes from unsafe time-polynomial extrapolation, not from M3A/M3B sign error.

### Is M3B helpful?

Yes, modestly. On special-day holdout:

```text
SE1 M1 MAE improves 0.2708 -> 0.2008 with M3B.
area_diff M1 MAE improves 0.1556 -> 0.1500 with M3B.
```

M3B is not the main source of the M4 problem.

### What should the next package do?

Recommended P0036-prep direction:

1. Build time-split-safe evaluation: M1/M2/M3A/M3B must be refit using train-only data for holdout comparisons.
2. Remove polynomial extrapolation on `days_since_start_scaled`; do not use degree-2 Ridge as the promoted M4 residual model.
3. Use bounded tree models such as `HistGradientBoostingRegressor` with explicit max_iter/time budget, because small tests show it trains quickly and avoids the area_diff blow-up.
4. Add residual clipping or robust target handling for `area_diff_proxy_se3`; separate model parameters per target.
5. Add proper trend/regime features if M4 is expected to learn market structure, but make them bounded and leakage-safe.
6. Separate normalized-target evaluation from raw observed evaluation. Raw observed evaluation needs M5 for forecast-time temperature addback, or an explicit diagnostic that uses observed M3A.

P0035 should remain `WARN`; do not promote it as a replacement-quality M4.
