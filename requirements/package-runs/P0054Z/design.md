# P0054Z implementation design

Status: `PASS`

## Interpretation

Create actual-weather proxy feature series for:

```text
SE3_EAST_COAST_MALARDALEN_STOCKHOLM
SE3_WEST_COAST_GOTHENBURG
SE3_NORTHERN_INLAND
SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
SE3_BROAD_PROXY
```

These series are LABB historical weather targets for later cluster/residual forecasting packages.

## Implementation structure

Add:

```text
src/mac/services/spotprice_model_diagnostics/p0054z.py
tests/mac/services/spotprice_model_diagnostics/test_p0054z.py
```

The module reads local `weather_history.sqlite3`, writes `se3_climate_zone_weather_hourly_v1` into the feature DB, and emits package evidence under `requirements/package-runs/P0054Z/`.

## Source selection

Use local weather observations:

```text
weather_observations
weather_area_hourly
weather_locations
```

Broad proxy:

```text
weather_area_hourly.area_proxy = se3_load_weather
```

Climate zones use weighted composites of existing `se3_load_*` point observations. No external download or new credential is used.

## Output table

Use long-table contract:

```text
timestamp_utc
climate_zone_id
feature_name
feature_value
feature_unit
source_station_or_proxy_ids
aggregation_method
missingness_flag
generated_by_package
```

## Features

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

## Test strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054z
PYTHONPYCACHEPREFIX=/private/tmp/p0054z-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054z.py tests/mac/services/spotprice_model_diagnostics/test_p0054z.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054z-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054z
git diff --check
```

## Risks

Zone selection is heuristic and based on existing local weather proxy points. It is suitable for LABB cluster/residual modeling tests, not a final meteorological station network.
