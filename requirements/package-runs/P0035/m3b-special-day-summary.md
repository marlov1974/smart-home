# P0035 M3B special-day summary

M3B estimates special-day deltas after M1 and M3A:

```text
target_residual = actual - M1_normal_price - M3A_temperature_delta
```

Backfill counts:

```text
m3b_special_day_delta = 69888
m3b_special_day_delta_buckets = 68
m3ab_normalized_prices = 34944
```

Shrinkage:

```text
delta = median_residual * sample_count / (sample_count + 24)
```

Caps:

```text
system_proxy_se1 = +/-0.50
area_diff_proxy_se3 = +/-0.35
```
