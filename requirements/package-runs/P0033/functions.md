# P0033 function design

## New module

```text
src.mac.services.spotprice_temperature_normalization
```

## Functions and responsibilities

`default_feature_db_path()`

- Purpose: return `~/.smart-home/data/spotprice_model_features.sqlite3`.
- Inputs: none.
- Outputs: `Path`.
- Side effects: none.
- Tests: CLI/default path smoke coverage.

`open_feature_database(path)`

- Purpose: open a SQLite feature DB with row factory and foreign keys enabled.
- Inputs: path.
- Outputs: SQLite connection.
- Side effects: opens local DB file.
- Tests: schema tests.

`initialize_schema(conn)`

- Purpose: create P0033 feature tables and indexes.
- Inputs: feature DB connection.
- Outputs: none.
- Side effects: creates/migrates local generated DB tables.
- Tests: required tables exist.

`load_price_targets(conn, price_db, weather_db, start_date, end_date)`

- Purpose: attach source DBs and load joined SE1, SE3 and SE3-SE1 target rows over the complete overlap.
- Inputs: feature DB connection, price/weather DB paths, date bounds.
- Outputs: list of input rows.
- Side effects: temporary SQLite attachments only.
- Tests: synthetic join completeness.

`load_weather_proxy_features(conn, price_db, weather_db, start_date, end_date)`

- Purpose: expose P0032 weather proxy values and gradients for M2/M3.
- Inputs: feature DB connection, source DB paths, date bounds.
- Outputs: merged weather features inside input rows.
- Side effects: temporary SQLite attachments only.
- Tests: synthetic row feature extraction.

`dump_p0032_location_weights(weather_db)`

- Purpose: read actual P0032 location weights from `weather_locations`.
- Inputs: weather DB path.
- Outputs: list of weight rows.
- Side effects: none.
- Tests: TC1.

`select_m2_target_weights()`

- Purpose: return the P0033 Level 2 model signal weights and rationale.
- Inputs: none.
- Outputs: structured weight definitions.
- Side effects: none.
- Tests: TC4.

`compute_m1_calm_normal_price(rows)`

- Purpose: build weather-blind robust calendar medians for SE1 and area-diff targets.
- Inputs: joined input rows with calendar fields and target prices.
- Outputs: M1 baseline rows, including `sample_count` and diagnostic `bucket_year_count`.
- Side effects: none.
- Tests: TC2.

`compute_m2_climate_normals(rows)`

- Purpose: compute smoothed climate normals for selected SE1 climate signals and area-diff gradients.
- Inputs: joined input rows with weather proxy features.
- Outputs: normal rows, including `sample_count` and diagnostic `bucket_year_count`.
- Side effects: none.
- Tests: TC3.

`compute_m2_climate_anomalies(rows, normals)`

- Purpose: compute `actual - normal` anomaly rows.
- Inputs: input rows and M2 normal rows.
- Outputs: anomaly rows.
- Side effects: none.
- Tests: TC3.

`compute_m3_statistical_temperature_delta(rows, m1_rows, anomaly_rows)`

- Purpose: estimate conservative bucketed deltas from M1 residuals and selected temperature anomalies.
- Inputs: input rows, M1 baseline rows, M2 anomaly rows.
- Outputs: delta rows and bucket summary rows.
- Side effects: none.
- Tests: TC5 and TC6.

`build_temp_normalized_training_series(rows, m1_rows, delta_rows)`

- Purpose: create normalized SE1, area-diff and recomposed SE3 training series.
- Inputs: input rows, M1 rows and M3 deltas.
- Outputs: normalized series rows.
- Side effects: none.
- Tests: TC7.

`validate_training_foundation(conn)`

- Purpose: validate row counts, date coverage, join completeness and required table presence.
- Inputs: feature DB connection.
- Outputs: validation summary.
- Side effects: none.
- Tests: TC8.

`summarize_temperature_normalization(conn)`

- Purpose: compute residual, anomaly, delta and before/after association diagnostics.
- Inputs: feature DB connection.
- Outputs: diagnostics summary.
- Side effects: none.
- Tests: TC9.

`build_training_foundation(...)`

- Purpose: orchestrate schema init, source loading, M1/M2/M3 computation, persistence and manifest writes.
- Inputs: source DB paths, feature DB path and date bounds.
- Outputs: build summary.
- Side effects: writes generated local feature DB only.
- Tests: end-to-end synthetic fixture test.

`main(argv=None)`

- Purpose: CLI entry point with `build`, `validate`, `diagnostics` and `dump-weights`.
- Inputs: argv.
- Outputs: process exit code and JSON/text summaries.
- Side effects: build writes generated DB; other commands read local DBs.
- Tests: command parser smoke coverage.
