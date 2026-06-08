# P0056D Open-Meteo Fetch Contract

- Endpoint: `https://archive-api.open-meteo.com/v1/archive`
- Period: `2022-06-01..2026-05-31`
- Timezone: `GMT`
- Model: `best_match`
- Fetch cadence: one representative location per request.
- Storage: location-hour rows in `area_weather_zone_openmeteo_hourly_p0056d_v1`.
- Required variable: `temperature_2m`.
- Preferred variables requested by existing helper: `apparent_temperature`, `wind_speed_10m`, `cloud_cover`, `relative_humidity_2m`, `precipitation`.
- Optional missing variable: `snow_depth`.

