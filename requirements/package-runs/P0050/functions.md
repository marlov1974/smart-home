# P0050 function design

## New module

`src.mac.services.spotprice_model_diagnostics.p0050`

## New functions

`run_p0050_analysis(feature_db=..., evidence_dir=...)`

- Purpose: orchestrate the full P0050 diagnostic run.
- Inputs: local SQLite feature DB path and evidence directory.
- Outputs: `P0050Result`.
- Side effects: writes `se3_se1_demand_response_analysis_v1` and package evidence files.
- Tests: exercised by unit tests and package verification command.

`load_p0050_source_rows(feature_db)`

- Purpose: load P0048 source rows and join P0049 reservoir columns where available.
- Inputs: SQLite feature DB path.
- Outputs: ordered list of row dictionaries.
- Side effects: none.
- Tests: contract validation tests use synthetic rows; package run verifies real DB.

`validate_p0050_contract(rows)`

- Purpose: verify required fields, spread reconstruction and chronological split order.
- Inputs: source rows.
- Outputs: contract summary.
- Side effects: none.
- Tests: spread arithmetic, fixed-CET presence and split tests.

`fit_spread_baselines(train_rows)` / `apply_spread_baselines(rows, baselines)` / `select_spread_baseline(rows, baselines)`

- Purpose: train-only expected-spread baselines, residual calculation and validation selection.
- Inputs: chronological rows and baseline specs.
- Outputs: baseline specs, selected baseline id and residual fields.
- Side effects: mutates row dictionaries with baseline predictions and residuals.
- Tests: train-only baseline and residual tests.

`add_local_se3_rank_features(rows)`

- Purpose: add day and trailing 48h SE3 rank/top-N/bottom-N/percentile features.
- Inputs: rows ordered by `timestamp_utc`.
- Outputs: none.
- Side effects: mutates row dictionaries.
- Tests: deterministic rank tie handling and percentile flag tests.

`add_consumer_optimizer_response_features(rows)`

- Purpose: add backward-looking top/bottom event counts, hours-since counters and explicitly labeled oracle next recovery fields.
- Inputs: rows with rank flags.
- Outputs: none.
- Side effects: mutates row dictionaries.
- Tests: top-N counts and oracle label tests.

`add_heat_pump_pressure_features(rows, train_rows)`

- Purpose: add cold thresholds, cold/high-price interaction features and heat-debt EMA proxies.
- Inputs: rows and train rows.
- Outputs: formula/threshold summary.
- Side effects: mutates row dictionaries.
- Tests: heat pressure formula reproducibility.

`add_future_targets(rows, horizons)`

- Purpose: add future raw spread, residual spread and residual-regime targets.
- Inputs: rows and horizons.
- Outputs: none.
- Side effects: mutates row dictionaries.
- Tests: shifted target tests.

`evaluate_response_rebound(rows)` / `evaluate_model_groups(rows)` / `summarize_daytypes(rows)`

- Purpose: compute response/rebound, feature-family and day-type residual diagnostics.
- Inputs: feature rows.
- Outputs: dictionaries/lists for evidence.
- Side effects: none.
- Tests: covered by package run and focused helper tests where deterministic.

`persist_demand_response_dataset(feature_db, rows)`

- Purpose: write the derived local SQLite analysis table.
- Inputs: DB path and rows.
- Outputs: persisted row count.
- Side effects: drops/recreates `se3_se1_demand_response_analysis_v1`.
- Tests: verified by package command and SQLite query.

`write_p0050_evidence(evidence_dir, rows, summary)`

- Purpose: write required Markdown/CSV/JSON evidence files.
- Inputs: evidence directory, rows and summary.
- Outputs: path map.
- Side effects: writes package-run evidence.
- Tests: package verification checks generated files.

## Changed functions

None planned.

## Removed functions

None planned.
