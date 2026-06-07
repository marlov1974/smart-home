# Output Table Schema

Table: `area_weather_features_hourly_v1`

| column | type | description |
| --- | --- | --- |
| timestamp_utc | TEXT | UTC hour start |
| area_code | TEXT | P0056A primary area |
| temperature_2m | REAL | Weighted Celsius actual-weather proxy |
| apparent_temperature | REAL nullable | Weighted Celsius actual-weather proxy |
| wind_speed | REAL nullable | Weighted 100m wind speed proxy |
| cloud_cover | REAL nullable | Weighted cloud cover proxy |
| relative_humidity | REAL nullable | Weighted relative humidity proxy |
| precipitation | REAL nullable | Weighted precipitation proxy |
| snow_depth | REAL nullable | Null; source has snowfall, not snow depth |
| heating_degree_proxy | REAL | max(0, 17C - temperature_2m) |
| cooling_degree_proxy | REAL nullable | max(0, temperature_2m - 22C) |
| temperature_2m_roll_mean_24h | REAL | Current plus prior 23 UTC hours |
| source_station_or_proxy_ids | TEXT | JSON list of source IDs |
| missingness_flags | TEXT | Comma-separated source/fallback flags |
| generated_by_package | TEXT | P0056B |
