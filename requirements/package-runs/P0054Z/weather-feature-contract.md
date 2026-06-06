# P0054Z weather feature contract

Features:

```text
temperature_2m
apparent_temperature
wind_speed_100m
cloud_cover
relative_humidity
precipitation
snowfall
heating_degree_proxy
cooling_degree_proxy
temperature_2m_roll_mean_24h
```

Heating degree base: `17 C`.

Cooling degree base: `22 C`.

Time handling: UTC hourly rows from local weather history. Local DST fields remain in the source weather DB but P0054Z output is keyed by UTC hour.
