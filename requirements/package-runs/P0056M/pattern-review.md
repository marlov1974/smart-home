# P0056M Pattern Review

- `10_error_mode`: isolated hourly spikes
- `11_worst_test_patterns`: Most common season: winter (4/5); weekday: Saturday (2/5); explanation tags: mild, high_load, high_ramp, underforecast_bias, hourly_spike (2/5).
- `12_best_test_patterns`: Most common season: summer (2/5); weekday: Friday (2/5); explanation tags: cold, high_load, high_ramp, underforecast_bias, distributed_error (1/5).
- `1_worst_weekday`: `Saturday` MAE `315.61303173687025` count `36`
- `2_best_weekday`: `Tuesday` MAE `193.08046986119035` count `33`
- `3_worst_month`: `March` MAE `341.3950702454978` count `31`
- `4_worst_season`: `winter` MAE `271.4100231609917` count `83`
- `5_cold_weather_increases_error`: cold MAE is 109.249 MW higher than warm/hot (265.850 vs 156.601 MW).
- `6_mild_weather_increases_error`: mild MAE is 50.551 MW higher than cold/warm average (261.777 vs 211.226 MW).
- `7_winter_vs_summer`: winter_half MAE is 107.678 MW higher than summer_half (283.840 vs 176.162 MW).
- `8_high_load_days_worse`: load_q4_high MAE is 134.490 MW higher than load_q1_low (322.869 vs 188.379 MW).
- `9_high_ramp_days_worse`: ramp_q4_high MAE is 162.673 MW higher than ramp_q1_low (324.748 vs 162.075 MW).
- `best_month`: `July` MAE `127.70761004306254` count `23`
- `best_season`: `summer` MAE `136.58010116535152` count `43`
- `worst_load_slice`: `load_q4_high` MAE `322.8689025556356` count `60`
- `worst_ramp_slice`: `ramp_q4_high` MAE `324.7484334243258` count `60`
