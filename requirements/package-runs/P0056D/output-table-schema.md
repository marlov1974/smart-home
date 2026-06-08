# P0056D Output Table Schema

- `area_weather_zone_openmeteo_hourly_p0056d_v1`: representative location-hour Open-Meteo observations with zone membership.
- `area_weather_proxy_weights_p0056d_v1`: area-zone weights and confidence/rationale.
- `area_weather_proxy_hourly_p0056d_v1`: weighted area weather proxy rows.
- `area_weather_features_hourly_p0056d_v1`: P0056C-compatible weighted area weather feature rows.
- `area_consumption_forecast_log_p0056d_v1`: SE1/SE2/FI holdout selected forecast-origin predictions.
- `area_consumption_forecast_metrics_p0056d_v1`: SE1/SE2/FI retest metrics.

All tables are keyed by `generated_by_package='P0056D'` and do not overwrite P0056B or P0056C rows.
