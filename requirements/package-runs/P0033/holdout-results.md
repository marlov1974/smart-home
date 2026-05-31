# P0033 holdout results

## Identity

```text
package_id = P0033
model_id = M1/M2/M3 training foundation
reported_model = M1 normal_price_v1 baseline used by P0034
status = PASS as baseline evidence
```

This file persists the P0033 M1 holdout metrics used as the required baseline for P0034.

## Inputs

```text
feature_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
input_table = m3_temp_normalized_prices_v1
holdout = 2026-01-01..2026-05-24
holdout_rows = 3455
time_split_method = same fixed chronological holdout as P0034
```

## Holdout hourly metrics

| target | M1 MAE | M1 RMSE |
|---|---:|---:|
| system_proxy_se1 | 0.3430024913169314 | 0.48352073558571185 |
| area_diff_proxy_se3 | 0.20408917583212727 | 0.29430242065818596 |
| recomposed_se3 | 0.39073463277858034 | 0.5037357192319121 |

## Holdout level metrics

| target | scope | M1 MAE | M1 RMSE |
|---|---|---:|---:|
| system_proxy_se1 | week | 0.277581889525318 | 0.35468130617359367 |
| system_proxy_se1 | month | 0.2644712680472346 | 0.3068883190278867 |
| area_diff_proxy_se3 | week | 0.15250283211319704 | 0.1784245975631708 |
| area_diff_proxy_se3 | month | 0.12877349115751635 | 0.15667058475188234 |

## Holdout curve-index metrics

| target | scope | M1 MAE | M1 RMSE |
|---|---|---:|---:|
| system_proxy_se1 | week | 0.4737497337069649 | 0.6588152814779519 |
| system_proxy_se1 | month | 0.5427705767162805 | 0.7438427018373691 |
| area_diff_proxy_se3 | week | 1.1646626040015942 | 1.9490726728797394 |
| area_diff_proxy_se3 | month | 1.0552730780183368 | 1.553164003188756 |

## Notes

These metrics were computed by the P0034 backtest pipeline from the P0033 M1 baseline columns:

```text
normal_price_v1_se1
normal_price_v1_area_diff
normal_price_v1_se1 + normal_price_v1_area_diff
```
