# P0031 weather dataset manifest summary

## Source

```text
source = Open-Meteo Historical Weather API
source_model = era5_seamless
timezone_request = GMT
local_timezone = Europe/Stockholm
latest_safe_complete_day_rule = today - 6 days
```

## Database

```text
db_path = /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
db_size_bytes = 49696768
```

## Coverage

```text
start_date = 2022-05-30
end_date = 2026-05-24
first_utc_hour_start = 2022-05-29T22:00Z
last_utc_hour_start = 2026-05-24T21:00Z
complete = true
```

## Locations and weights

```text
stockholm  59.3293  18.0686  0.35
goteborg   57.7089  11.9746  0.25
orebro     59.2753  15.2134  0.20
linkoping  58.4108  15.6214  0.20
```

## Required variables

```text
temperature_2m
apparent_temperature
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
```

## Counts

```text
location_row_count = 139776
location_expected_count = 139776
area_row_count = 34944
area_expected_count = 34944
location_gap_count = 0
area_gap_count = 0
duplicate_location_rows = 0
duplicate_area_rows = 0
```

## Per-year counts

Area proxy:

```text
2022 = 5185
2023 = 8760
2024 = 8784
2025 = 8760
2026 = 3455
```

Location observations:

```text
2022 = 20740
2023 = 35040
2024 = 35136
2025 = 35040
2026 = 13820
```

## Null counts

All required location variables and weighted area variables validated with null count 0.

## Weighted SE3 variable stats

```text
temperature_2m              min=-15.785  max=30.12   mean=8.225673935439684
apparent_temperature        min=-21.185  max=31.52   mean=5.389968521062268
wind_speed_10m              min=1.88     max=39.49   mean=12.781665951236214
wind_speed_100m             min=2.755    max=63.855  mean=22.089869934752628
wind_gusts_10m              min=5.21     max=85.075  mean=26.86257512019237
cloud_cover                 min=0.0      max=100.0   mean=66.80693967490814
shortwave_radiation         min=0.0      max=829.5   mean=116.13364955357201
precipitation               min=0.0      max=3.495   mean=0.08377747252747261
snowfall                    min=0.0      max=0.7315  mean=0.007913862179487207
relative_humidity_2m        min=27.25    max=100.0   mean=79.7753691620878
pressure_msl                min=962.625  max=1048.62 mean=1012.575755923756
```
