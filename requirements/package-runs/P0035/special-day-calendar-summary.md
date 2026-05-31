# P0035 special-day calendar summary

Generated file:

```text
data/calendar/se_special_days_2022_2035.csv
```

Result:

```text
start = 2022-01-01
end = 2035-12-31
row_count = 5113
leap_days = 2024-02-29, 2028-02-29, 2032-02-29
```

The package text expected 5114 rows, but the correct inclusive interval count is 5113 because 2036 is outside scope.

Training-period special-day rows after local backfill:

```text
special hours = 2855
fixed_public_holiday = 576
movable_public_holiday = 503
major_social_holiday = 384
holiday_period_day = 384
special_weekend_day = 288
pre_holiday_transition_day = 264
bridge_day_strong = 192
post_holiday_recovery_day = 96
holiday_eve = 96
bridge_day_weak = 72
```
