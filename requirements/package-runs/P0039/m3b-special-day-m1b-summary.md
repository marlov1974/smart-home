# P0039 M3B M1B special-day summary

| subset | rows | M1+M3A_m1b MAE | M1+M3A_m1b+M3B_m1b MAE | delta |
|---|---:|---:|---:|---:|
| special_day_hours | 576 | 0.396680 | 0.340024 | -0.056655 |
| non_special_day_hours | 8184 | 0.375317 | 0.375317 | 0.000000 |
| holiday_weekday_hours | 456 | 0.425639 | 0.364188 | -0.061451 |

M3B_m1b target formula: `actual - M1B - M3A_m1b`, fitted on train special-day rows only.
