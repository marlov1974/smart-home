# P0056D Weather Feature Contract

```json
{
  "feature_table": "area_weather_features_hourly_p0056d_v1",
  "input_classification": "historical_observed_only_weather_actual_proxy",
  "model_feature_names": [
    "weather_proxy_temperature_2m_area",
    "weather_proxy_apparent_temperature_area",
    "weather_proxy_wind_speed_area",
    "weather_proxy_cloud_cover_area",
    "weather_proxy_humidity_area",
    "weather_proxy_precipitation_area",
    "weather_proxy_snow_depth_area",
    "weather_proxy_heating_degree_hours_area",
    "weather_proxy_cooling_degree_hours_area",
    "weather_proxy_temperature_roll_mean_24h_area",
    "weather_proxy_train_normal_temperature_2m_area",
    "weather_proxy_temperature_delta_from_train_normal_area",
    "weather_proxy_cold_spell_flag_area"
  ],
  "production_weather_forecast": false,
  "snow_depth": "unavailable; stored null in table and zero-filled only for P0056C-compatible model matrix",
  "units": {
    "apparent_temperature": "degC",
    "cloud_cover": "percent",
    "precipitation": "mm",
    "relative_humidity": "percent",
    "snowfall": "cm per Open-Meteo hourly variable",
    "temperature_2m": "degC",
    "wind_speed": "km/h from Open-Meteo wind_speed_10m"
  },
  "weather_proxy_version": "P0056D"
}
```
