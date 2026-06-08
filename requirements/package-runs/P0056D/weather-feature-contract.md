# P0056D Weather Feature Contract

P0056D weather rows are classified as `historical_observed_only_weather_actual_proxy`.

They are LABB-only and not production weather forecasts. `snow_depth` is unavailable from the existing helper and must be treated as optional missing; P0056C-compatible model rows zero-fill it only to keep matrix shape compatible.

