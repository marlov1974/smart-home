# P0056D Function Design

## New Module

`src/mac/services/spotprice_model_diagnostics/p0056d.py`

## New Functions

`weather_zones()`

- Purpose: return the immutable SE1/SE2/FI zone catalog.
- Inputs: none.
- Outputs: list of zone definitions.
- Side effects: none.
- Test coverage: catalog and area/zone membership tests.

`representative_locations()`

- Purpose: return Open-Meteo representative locations with coordinates and zone membership.
- Inputs: none.
- Outputs: list of location definitions.
- Side effects: none.
- Test coverage: location coverage and zone coverage tests.

`zone_weights()`

- Purpose: return documented deterministic area-zone weights.
- Inputs: none.
- Outputs: list of weight definitions.
- Side effects: none.
- Test coverage: weights sum to 1.0 per area.

`create_schema(conn)`

- Purpose: create P0056D-only SQLite output tables.
- Inputs: SQLite connection.
- Outputs: none.
- Side effects: creates tables and commits.
- Test coverage: package runner integration.

`fetch_and_store_openmeteo(conn, start_date, end_date)`

- Purpose: fetch archive weather one location-period chunk at a time and upsert location-hour rows.
- Inputs: SQLite connection, date range.
- Outputs: fetch evidence summary with completion/rate-limit status.
- Side effects: network calls to Open-Meteo and local SQLite writes.
- Test coverage: not unit-tested with live network; evidence validates live run.

`fetch_chunks(start_date, end_date)`

- Purpose: split the required Open-Meteo period into resumable quarterly chunks.
- Inputs: start and end dates.
- Outputs: ordered `(period_start, period_end)` tuples.
- Side effects: none.
- Test coverage: chunk coverage test.

`location_period_row_count(conn, location_id, period_start, period_end)`

- Purpose: count already loaded rows for one location-period chunk.
- Inputs: SQLite connection, location id, period range.
- Outputs: row count.
- Side effects: none.
- Test coverage: package runner integration.

`write_fetch_checkpoint_evidence(evidence_dir, checkpoint_rows, summary)`

- Purpose: persist checkpoint/progress/resume evidence after completed or failed chunks.
- Inputs: evidence path, checkpoint rows, fetch summary.
- Outputs: evidence file paths.
- Side effects: writes package-run markdown files.
- Test coverage: filesystem evidence in live run.

`upsert_location_observations(conn, location, observations, fetched_at_utc)`

- Purpose: persist parsed Open-Meteo rows into P0056D location table.
- Inputs: connection, location definition, observations, fetch timestamp.
- Outputs: row count.
- Side effects: SQLite writes.
- Test coverage: aggregation unit tests use representative row structures.

`build_area_weather_features(conn)`

- Purpose: aggregate location rows into zone and area weather proxy/features rows.
- Inputs: SQLite connection.
- Outputs: coverage summary.
- Side effects: SQLite writes to proxy/features tables.
- Test coverage: deterministic aggregation test.

`load_p0056d_area_weather_rows(conn)`

- Purpose: load P0056D feature table into the P0056C-compatible weather row format.
- Inputs: SQLite connection.
- Outputs: weather rows and source contract.
- Side effects: none.
- Test coverage: forbidden feature and contract tests.

`run_forecast_retest(conn, evidence_dir)`

- Purpose: retrain/retest SE1, SE2 and FI with the P0056C model method and P0056D weather.
- Inputs: SQLite connection and evidence path.
- Outputs: model/metric summary.
- Side effects: writes P0056D forecast/metrics tables.
- Test coverage: live package run evidence.

`compare_against_p0056c(area_results)`

- Purpose: compute metric deltas and candidate-default decisions.
- Inputs: P0056D area result summaries.
- Outputs: comparison rows and decision summary.
- Side effects: none.
- Test coverage: decision-rule unit tests.

`write_evidence(evidence_dir, summary)`

- Purpose: write all required compact P0056D evidence files.
- Inputs: evidence path and run summary.
- Outputs: map of evidence file paths.
- Side effects: writes package-run markdown/csv/json files.
- Test coverage: live package run and filesystem evidence.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Function Catalog

No cross-package durable function catalog update is planned because P0056D is package-scoped LABB code.
