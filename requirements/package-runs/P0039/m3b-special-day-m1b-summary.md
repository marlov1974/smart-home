# P0039 M3B M1B special-day summary

| subset | rows | M1B+M3A MAE | M1B+M3A+M3B MAE | delta |
|---|---:|---:|---:|---:|
| special_day_hours | 576 | 0.573232 | 0.479876 | -0.093356 |
| non_special_day_hours | 8184 | 0.403145 | 0.403145 | 0.000000 |
| holiday_weekday_hours | 456 | 0.633350 | 0.542317 | -0.091033 |

M3B_m1b target formula: `actual - M1B - M3A_m1b`, fitted on train special-day rows only.
