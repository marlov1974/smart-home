# P0035 holdout results

## Identity

```text
package_id = P0035
model_id = M4 residual
model_version = m4_residual_m1_anchor_v1
model_class = scikit-learn PolynomialFeatures(degree=2) + Ridge(alpha=1.0)
status = WARN
```

`WARN` reason: P0035 rebuilt M4 as an M1-anchored residual model with M3B special-day normalization, but the residual model does not beat the M1 baseline on key holdout hourly metrics.

## Inputs and split

```text
feature_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
input_table = m3ab_normalized_prices
model_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3
train = 2022-05-30..2024-12-31, rows = 22729
validate = 2025-01-01..2025-12-31, rows = 8760
holdout = 2026-01-01..2026-05-24, rows = 3455
holdout_special_hours = 312
holdout_non_special_hours = 3143
```

Feature schema is the existing 14 calendar/slow-trend features. Weather, temperature, wind, solar and cloud features are excluded.

## Normalized holdout metrics without M3B addback

Because M3B is added to both prediction and evaluation target for special-day addback, the absolute errors are identical to the addback evaluation for this P0035 target definition.

| target | P0035 M4 MAE | P0035 M4 RMSE | M1 MAE | M1 RMSE | winner |
|---|---:|---:|---:|---:|---|
| system_proxy_se1 | 0.6079521874402215 | 0.7644348442048995 | 0.33685564669429213 | 0.47642915390238133 | M1 |
| area_diff_proxy_se3 | 1.8269617292981122 | 1.8773900197706685 | 0.20279122565396646 | 0.29322917847350166 | M1 |
| recomposed_se3 | 1.6662037682642874 | 1.8576351313078958 | 0.3831750317910952 | 0.4971918166163072 | M1 |

## Evaluation target with M3B addback

P0035 evaluation uses:

```text
eval_prediction = M1 + M4_residual_prediction + M3B_special_day_delta
eval_target = m3ab_normalized_target + M3B_special_day_delta
```

This preserves the same holdout error values as the normalized table above.

## Special-day holdout subset

| subset | target | P0035 M4 MAE | P0035 M4 RMSE | M1 MAE | M1 RMSE | winner |
|---|---|---:|---:|---:|---:|---|
| special | system_proxy_se1 | 0.5427799929122432 | 0.6821018921003492 | 0.20080614568519725 | 0.28863194666914227 | M1 |
| special | area_diff_proxy_se3 | 1.8599008355085278 | 1.9152671878627785 | 0.1499576029950441 | 0.21597422941913302 | M1 |
| special | recomposed_se3 | 1.780202844831425 | 1.9771665742593734 | 0.27656661807126687 | 0.36812050152079123 | M1 |

## Non-special-day holdout subset

| subset | target | P0035 M4 MAE | P0035 M4 RMSE | M1 MAE | M1 RMSE | winner |
|---|---|---:|---:|---:|---:|---|
| non_special | system_proxy_se1 | 0.6144217148639353 | 0.772129031419386 | 0.3503610378221438 | 0.49116925017326574 | M1 |
| non_special | area_diff_proxy_se3 | 1.8236919230182347 | 1.8735882417233372 | 0.2080359250715878 | 0.29981396253829573 | M1 |
| non_special | recomposed_se3 | 1.654887283412572 | 1.8453470616818217 | 0.39375785873369357 | 0.50821911764105 | M1 |

## Not applicable metrics

Rank accuracy and top/bottom quantile precision remain not implemented because P0035 does not expose optimizer selection behavior.
