# P0041 M2 normal weather foundation

smoothing_window_days = 14
hourly_bucket_definition = signal x day_of_year x local_hour
daily_bucket_definition = signal x day_of_year
normal_method = cyclic day-of-year/local-hour median over all available years, smoothed across neighboring calendar days

| table | rows | min_year_count | max_year_count | smoothing_window_days |
|---|---:|---:|---:|---:|
| m2a_temperature_normals_daily | 366 | 4 | 5 | 14 |
| m2a_temperature_normals_hourly | 8784 | 4 | 5 | 14 |
| m2c_solar_normals_daily | 366 | 4 | 5 | 14 |
| m2c_solar_normals_hourly | 8784 | 4 | 5 | 14 |
| m2d_wind_normals_daily | 366 | 4 | 5 | 14 |
| m2d_wind_normals_hourly | 8784 | 4 | 5 | 14 |

M2C solar proxy = `shortwave_radiation * (1 - 0.35 * cloud_cover/100)` from P0038. There is no explicit clear-sky/elevation variable in the current weather history; night and near-zero behavior comes from observed shortwave radiation.
M2D wind proxy = capped nonlinear `wind_speed_100m` transform from P0038.
Required wind proxy locations: Ange, Harnosand, Kalmar, Kristinehamn, Malmo, Pitea
