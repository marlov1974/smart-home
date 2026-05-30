# P0032 weather proxy summary

## Weather DB

```text
db_path = /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
db_size_bytes = 476868608
start_date = 2022-05-30
end_date = 2026-05-24
```

## Proxy groups

```text
se1_core_weather:
  locations = 12
  location_rows = 419328
  area_rows = 34944
  gaps = 0
  nulls = 0

nordic_connected_weather:
  locations = 6
  location_rows = 209664
  area_rows = 34944
  gaps = 0
  nulls = 0

south_connected_weather:
  locations = 4
  location_rows = 139776
  area_rows = 34944
  gaps = 0
  nulls = 0

se3_load_weather:
  locations = 12
  location_rows = 419328
  area_rows = 34944
  gaps = 0
  nulls = 0
```

## Gradients

```text
gradient_row_count = 34944
gradient_expected_count = 34944
gradient_null_count = 0
```

Fields:

```text
temp_gradient_se3_load_minus_se1_core
apparent_temp_gradient_se3_load_minus_se1_core
heating_degree_gradient_se3_load_minus_se1_core
wind_100m_gradient_nordic_connected_minus_se3_load
south_temp_gradient_minus_se1_core
```

## Rate-limit note

Open-Meteo returned HTTP 429 during the first full P0032 weather backfill attempt. The implementation was updated to skip location ranges already complete in the DB, then the backfill resumed and completed after waiting for the rate limit to clear.
