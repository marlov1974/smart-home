# P0051 function design

## New module

`src.mac.services.spotprice_model_diagnostics.p0051`

## New functions

`run_p0051_ingestion(feature_db=..., evidence_dir=...)`

- Orchestrates discovery evidence, fetch, parse, aggregation, persistence, validation and diagnostics.
- Side effects: writes local SQLite tables and package evidence files.

`fetch_json(url, timeout=...)`

- Fetches JSON using Python standard-library `urllib`.
- Tests use injected/static parser helpers instead of network.

`load_existing_ranges(conn)`

- Inspects current price/weather/modeling ranges from local SQLite tables.

`fetch_esett_period(start, end, zones)`

- Fetches eSett consumption and production quarter-hour responses for all SE1-SE4 zones.

`parse_esett_consumption(payload, zone)` / `parse_esett_production(payload, zone)`

- Converts eSett JSON items into canonical source observations.
- Consumption source sign is normalized to positive MW demand.

`aggregate_hourly(observations)`

- Aggregates quarter-hour observations into hourly mean MW rows by timestamp/source/zone/measure/production_type.

`build_wide_hourly(hourly_rows)`

- Builds SE1-SE4 wide rows with consumption, production, net-load and north/south aggregates.

`persist_physical_balance(conn, hourly_rows, wide_rows)`

- Recreates package-owned local SQLite tables.
- Idempotent by deterministic rebuild.

`validate_physical_balance(hourly_rows, wide_rows, expected_range)`

- Checks duplicates, missingness, finite values, units, row counts and join coverage.

`run_initial_diagnostics(conn, wide_rows)`

- Produces explanatory correlations/events against existing SE3 price and SE3-SE1 diagnostics.

`write_p0051_evidence(evidence_dir, summary)`

- Writes required Markdown/CSV/JSON evidence files.

## Changed functions

None planned.

## Removed functions

None planned.
