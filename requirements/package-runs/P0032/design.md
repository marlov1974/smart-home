# P0032 design

## Price history

Use existing DB:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

Store SE1 rows in `spot_prices(area='SE1', ...)`. Keep SE3 behavior intact.

Add a deterministic SQLite view:

```text
spotprice_system_proxy_hourly
```

Fields:

```text
utc_hour_start
local_date
local_hour
se3_price
se1_system_proxy_price
area_diff_proxy_se3
area_ratio_proxy_se3
source_coverage_status
```

Terminology:

- `system_proxy_price` means SE1 spot price.
- `area_diff_proxy` means SE3 minus SE1.
- It is not official Nordic SYS and not EPAD.

Ratio denominator policy:

```text
area_ratio_proxy_se3 = NULL when abs(SE1) < 0.000001
```

Daily ingest strategy:

- Extend `spotprice_history ingest-daily` to ingest both `SE3` and `SE1` by default.
- Existing launchd label and plist stay the same.

## Weather proxy groups

Use existing DB:

```text
~/.smart-home/data/weather_history.sqlite3
```

Register P0032 group-specific locations using `area_proxy` values:

```text
se1_core_weather
nordic_connected_weather
south_connected_weather
se3_load_weather
```

Compute weighted hourly rows in existing `weather_area_hourly`. Add stable views:

```text
weather_proxy_se1_core_hourly
weather_proxy_nordic_connected_hourly
weather_proxy_south_connected_hourly
weather_proxy_se3_load_hourly
```

Add materialized gradient table:

```text
weather_proxy_gradients_hourly
```

Gradient fields:

```text
temp_gradient_se3_load_minus_se1_core
apparent_temp_gradient_se3_load_minus_se1_core
heating_degree_gradient_se3_load_minus_se1_core
wind_100m_gradient_nordic_connected_minus_se3_load
south_temp_gradient_minus_se1_core
```

Backfill and daily ingest:

- `weather_history backfill` fetches all active proxy-group locations by default.
- `weather_history ingest-daily` ingests all active proxy groups and recomputes gradients.
- Launchd label and plist stay the same.

## Date intervals

Price:

```text
2022-05-30..2026-05-29
```

Weather:

```text
2022-05-30..2026-05-24
```

Weather keeps P0031's `today - 6 days` safety rule.

## Non-goals

No ML, no weather-normalized price model, no optimizer/control changes and no device calls.
