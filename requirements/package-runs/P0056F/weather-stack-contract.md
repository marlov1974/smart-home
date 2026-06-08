# P0056F Weather Stack Contract

```json
[
  {
    "description": "W0 no weather",
    "stack_id": "W0",
    "weather_features": []
  },
  {
    "description": "W1 temperature only",
    "stack_id": "W1",
    "weather_features": [
      "weather_proxy_temperature_2m_area"
    ]
  },
  {
    "description": "W2 add heating degree",
    "stack_id": "W2",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area"
    ]
  },
  {
    "description": "W3 add temperature rolling mean",
    "stack_id": "W3",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area"
    ]
  },
  {
    "description": "W4 add temperature normal and delta",
    "stack_id": "W4",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area"
    ]
  },
  {
    "description": "W5 add cold spell flag",
    "stack_id": "W5",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area"
    ]
  },
  {
    "description": "W6 add apparent temperature",
    "stack_id": "W6",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area"
    ]
  },
  {
    "description": "W7 add wind speed",
    "stack_id": "W7",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area",
      "weather_proxy_wind_speed_area"
    ]
  },
  {
    "description": "W8 add snow depth",
    "stack_id": "W8",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area",
      "weather_proxy_wind_speed_area",
      "weather_proxy_snow_depth_area"
    ]
  },
  {
    "description": "W9 add precipitation",
    "stack_id": "W9",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area",
      "weather_proxy_wind_speed_area",
      "weather_proxy_snow_depth_area",
      "weather_proxy_precipitation_area"
    ]
  },
  {
    "description": "W10 add humidity",
    "stack_id": "W10",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area",
      "weather_proxy_wind_speed_area",
      "weather_proxy_snow_depth_area",
      "weather_proxy_precipitation_area",
      "weather_proxy_humidity_area"
    ]
  },
  {
    "description": "W11 add cloud cover",
    "stack_id": "W11",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area",
      "weather_proxy_wind_speed_area",
      "weather_proxy_snow_depth_area",
      "weather_proxy_precipitation_area",
      "weather_proxy_humidity_area",
      "weather_proxy_cloud_cover_area"
    ]
  },
  {
    "description": "W12 add cooling degree",
    "stack_id": "W12",
    "weather_features": [
      "weather_proxy_temperature_2m_area",
      "weather_proxy_heating_degree_hours_area",
      "weather_proxy_temperature_roll_mean_24h_area",
      "weather_proxy_train_normal_temperature_2m_area",
      "weather_proxy_temperature_delta_from_train_normal_area",
      "weather_proxy_cold_spell_flag_area",
      "weather_proxy_apparent_temperature_area",
      "weather_proxy_wind_speed_area",
      "weather_proxy_snow_depth_area",
      "weather_proxy_precipitation_area",
      "weather_proxy_humidity_area",
      "weather_proxy_cloud_cover_area",
      "weather_proxy_cooling_degree_hours_area"
    ]
  }
]
```
