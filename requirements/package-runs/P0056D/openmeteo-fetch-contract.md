# P0056D Open-Meteo Fetch Contract

```json
{
  "batching": "one representative location-period per request; 3-month chunks; upserted incrementally by chunk",
  "end_date": "2026-05-31",
  "endpoint": "https://archive-api.open-meteo.com/v1/archive",
  "minimum_required_variables": [
    "temperature_2m"
  ],
  "models": "best_match",
  "preferred_variables_missing": [
    "snow_depth"
  ],
  "preferred_variables_present": [
    "apparent_temperature",
    "wind_speed_10m",
    "cloud_cover",
    "relative_humidity_2m",
    "precipitation"
  ],
  "start_date": "2022-06-01",
  "timezone": "GMT",
  "utc_handling": "Open-Meteo GMT hourly timestamps parsed as UTC and stored with Z suffix",
  "variables": [
    "temperature_2m",
    "apparent_temperature",
    "wind_speed_10m",
    "wind_speed_100m",
    "wind_gusts_10m",
    "cloud_cover",
    "shortwave_radiation",
    "precipitation",
    "snowfall",
    "relative_humidity_2m",
    "pressure_msl"
  ]
}
```
