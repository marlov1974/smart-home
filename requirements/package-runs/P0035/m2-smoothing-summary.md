# P0035 M2 smoothing summary

M2 method changed from narrow day-window median to broader cyclic robust smoothing:

```text
method = smooth_cyclic_robust_same_hour_day_plus_minus_7_21
normal = 0.70 * median(day +/- 7) + 0.30 * mean(day +/- 21)
```

Properties:

- no year feature
- cyclic day-of-year distance
- same local hour only
- `bucket_year_count` retained
- smoother than sharp week/day buckets

Backfill counts:

```text
m2_climate_normals = 314496
m2_climate_anomalies = 314496
```
