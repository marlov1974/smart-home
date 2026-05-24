# Weather Contract Tool

Last changed: P0015

## Module

```text
src.mac.tools.weather_contract.core
```

## Purpose

Mac-side Open-Meteo API/schema check before deploying Shelly weather runtime scripts.

## CLI

```bash
python3 -m src.mac.tools.weather_contract check-openmeteo
```

## Contract

The tool verifies the P0015 Open-Meteo response shape:

```text
daily.shortwave_radiation_sum[0]
daily.temperature_2m_mean[0]
daily.relative_humidity_2m_mean[0]
hourly.temperature_2m[0]
```

It reports response byte lengths and normalized G2 weather fields:

```text
solar_kwh_today
temp_now
temp_avg_today
humidity_avg_today
```

## Important Functions

`build_daily_url(day)` builds the daily Open-Meteo URL with P0015 fields and house coordinates.

`build_hourly_url()` builds the near-current hourly temperature URL.

`fetch_json(url, timeout, opener)` fetches and decodes JSON while preserving response length evidence.

`parse_daily(data)` validates and normalizes daily weather fields.

`parse_hourly(data)` validates and normalizes hourly temperature.

`check_openmeteo(day, timeout, opener)` performs the full pre-live API/schema check.
