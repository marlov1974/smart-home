# P0033 M1/M2 anti-year-memorization evidence

## Requirement

M1 normal price v1 and M2 normal climate must smooth between years. They must not create year-specific normals that memorize one year's weather or price shocks.

## Implementation rule

M1 and M2 do not include `year` as a model key.

Year is used only as a diagnostic coverage count stored in:

```text
m1_normal_price_v1.bucket_year_count
m2_climate_normals.bucket_year_count
```

The normal values are robust medians over all available years in the calendar bucket and smoothing window.

## M1 bucket definition

Bucket key:

```text
target + local_hour + weekday + ISO week circular smoothing window
```

Smoothing window:

```text
same local_hour
same weekday
ISO week distance <= 2
```

Estimator:

```text
median(target price over all rows in the bucket)
```

Forbidden in M1:

```text
year key
weather inputs
temperature inputs
wind/cloud/precipitation inputs
lagged price features
rolling current-event price features
```

## M2 bucket definition

Bucket key:

```text
signal + local_hour + day_of_year circular smoothing window
```

Smoothing window:

```text
same local_hour
day-of-year distance <= 7
```

Estimator:

```text
median(signal value over all rows in the bucket)
```

M2 uses year only to count how many calendar years contributed to the bucket. The normal itself is not conditioned on year.

## Local feature DB evidence

Command:

```bash
sqlite3 /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 "select target, min(bucket_year_count), max(bucket_year_count), avg(bucket_year_count), min(sample_count), max(sample_count) from m1_normal_price_v1 group by target order by target; select signal, min(bucket_year_count), max(bucket_year_count), avg(bucket_year_count), min(sample_count), max(sample_count) from m2_climate_normals group by signal order by signal;"
```

Result columns:

```text
name|min_years|max_years|avg_years|min_samples|max_samples
```

Result:

```text
area_diff_proxy_se3|4|5|4.1043956043956|16|24
system_proxy_se1|4|5|4.1043956043956|16|24
apparent_temp_gradient_se3_load_minus_se1_core|4|5|4.05494505494505|55|64
heating_degree_gradient_se3_load_minus_se1_core|4|5|4.05494505494505|55|64
se1_system_apparent_temperature|4|5|4.05494505494505|55|64
se1_system_cooling_degree|4|5|4.05494505494505|55|64
se1_system_heating_degree|4|5|4.05494505494505|55|64
se1_system_temperature|4|5|4.05494505494505|55|64
se3_load_temperature|4|5|4.05494505494505|55|64
south_temp_gradient_minus_se1_core|4|5|4.05494505494505|55|64
temp_gradient_se3_load_minus_se1_core|4|5|4.05494505494505|55|64
```

Assessment: every M1/M2 normal bucket in the rebuilt local P0033 feature DB aggregates across at least 4 years. No M1/M2 normal is year-specific.
