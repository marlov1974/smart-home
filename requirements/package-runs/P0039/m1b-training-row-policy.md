# P0039 M1B training row policy

Policy: exclude all rows whose `special_day_type` is not `normal_weekday`, `normal_saturday`, or `normal_sunday`, and exclude any row flagged `is_special_day`.

Midsummer Day is excluded because the Swedish calendar classifies it as `major_social_holiday`.

| split | included | excluded |
|---|---:|---:|
| train | 12817 | 1128 |
| validate | 8065 | 719 |
| holdout | 8064 | 696 |

| special_day_type | included | excluded |
|---|---:|---:|
| bridge_day_strong | 0 | 192 |
| bridge_day_weak | 0 | 72 |
| fixed_public_holiday | 0 | 576 |
| holiday_eve | 0 | 96 |
| holiday_period_day | 0 | 384 |
| major_social_holiday | 0 | 384 |
| movable_public_holiday | 0 | 503 |
| normal_saturday | 4536 | 0 |
| normal_sunday | 4537 | 0 |
| normal_weekday | 23040 | 0 |
| post_holiday_recovery_day | 0 | 96 |
| pre_holiday_transition_day | 0 | 264 |
| special_weekend_day | 0 | 288 |
