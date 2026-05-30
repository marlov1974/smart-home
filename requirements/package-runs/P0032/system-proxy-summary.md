# P0032 system proxy summary

## Spotprice DB

```text
db_path = /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
view = spotprice_system_proxy_hourly
```

## SE1 coverage

```text
start_date = 2022-05-30
end_date = 2026-05-29
row_count = 35064
expected_count = 35064
first_utc_hour_start = 2022-05-29T22:00Z
last_utc_hour_start = 2026-05-29T21:00Z
gap_count = 0
duplicate_count = 0
negative_price_count = 1632
min_price_sek_per_kwh = -0.8172050000000001
max_price_sek_per_kwh = 6.42501
mean_price_sek_per_kwh = 0.41196685517910214
```

## SE3/SE1 alignment

```text
aligned_count = 35064
expected_aligned_count = 35064
missing_se1_for_se3 = 0
missing_se3_for_se1 = 0
```

## Derived proxies

```text
area_diff_proxy_se3 = SE3 - SE1
area_ratio_proxy_se3 = SE3 / SE1, NULL when abs(SE1) < 0.000001
area_ratio_null_count = 191
area_diff_min = -0.6091099999999999
area_diff_max = 8.15277
area_diff_mean = 0.2910081769050896
area_ratio_min = -4875.999999999999
area_ratio_max = 8569.583333333343
area_ratio_mean = 3.554136300488574
```

SE1 is a project-local practical system proxy. It is not official Nordic SYS. The SE3-SE1 diff is a realized area-diff proxy, not EPAD.
