# P0054Z function design

Status: `PASS`

## New functions

`run_p0054z_weather_series(...)`

Purpose: orchestrate schema creation, source inventory, zone composite generation, validation and evidence writing.

Inputs: feature DB path, weather DB path and evidence directory.

Outputs: result object with status, row counts and evidence paths.

Side effects: writes P0054Z table rows and package evidence.

`create_schema(conn)`

Purpose: create `se3_climate_zone_weather_hourly_v1`.

`zone_station_weights()`

Purpose: return deterministic climate-zone station/proxy selections and weights.

`build_zone_weather_rows(...)`

Purpose: create long feature rows from local weather observations and broad proxy rows.

`validate_zone_weather(...)`

Purpose: compute coverage, missingness, temperature summary and distinctness versus broad proxy.

`write_evidence(...)`

Purpose: write required markdown, CSV and JSON evidence.
