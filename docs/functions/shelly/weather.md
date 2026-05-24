# Shelly Weather Runtime

Last changed: P0015

## Source

```text
src/shelly/weather/weather.js
src/shelly/weather/manifest.json
```

## Built Artifact

```text
build/shelly/weather/weather_v0_9_0.js
```

## Purpose

`weather_v0_9_0` is a G2 pre-production one-shot weather runtime adapted from the G1 weather template.

It fetches compact Open-Meteo daily/hourly weather data and writes:

```text
g2.weather.act
```

## KVS Contract

```json
{
  "solar_kwh_today": 0,
  "temp_now": 0,
  "temp_avg_today": 0,
  "humidity_avg_today": 0
}
```

## Runtime Boundary

P0015 verified the script on dampers only. It is not production-activated and does not implement G2 brain/driver behavior.

The script must not write `ftx.weather.act` and must not perform actuator/output operations.
