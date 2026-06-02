# P0048 feature foundation

{
  "feature_contract": {
    "available_weather_actual_features": [
      "wind_south_proxy_actual",
      "wind_central_proxy_actual",
      "wind_north_proxy_actual",
      "wind_system_proxy_actual",
      "solar_south_proxy_actual",
      "solar_north_proxy_actual",
      "solar_system_proxy_actual",
      "temperature_south_proxy_actual",
      "temperature_north_proxy_actual",
      "temperature_system_proxy_actual",
      "wind_south_minus_north_actual",
      "wind_central_minus_north_actual",
      "wind_south_minus_system_actual",
      "wind_north_minus_system_actual",
      "solar_south_minus_north_actual",
      "solar_south_minus_system_actual",
      "solar_north_minus_system_actual",
      "temperature_south_minus_north_actual",
      "temperature_south_minus_system_actual",
      "temperature_north_minus_system_actual"
    ],
    "missing_requested_features": [],
    "missing_weather_timestamps": 0,
    "normal_strategy": "fixed-CET day-of-year/hour train-period seasonal median"
  },
  "weather_contract": {
    "area_proxy_counts": {
      "nordic_connected_weather": 34992,
      "p0038_central_wind_proxy": 34992,
      "p0038_north_solar_proxy": 34992,
      "p0038_north_wind_proxy": 34992,
      "p0038_se3_load_solar_proxy": 34992,
      "p0038_south_solar_proxy": 34992,
      "p0038_south_wind_proxy": 34992,
      "se1_core_weather": 34992,
      "se3_load_weather": 34992,
      "south_connected_weather": 34992
    },
    "source_table": "weather_area_hourly"
  }
}

Weather actuals are exploratory proxy-forecast-known inputs, not production forecast inputs.
