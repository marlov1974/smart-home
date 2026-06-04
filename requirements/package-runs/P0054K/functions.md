# P0054K Function Design

## New Module

```text
src.mac.services.spotprice_model_diagnostics.p0054k
```

## New Functions

`run_p0054k_analysis(...)`

- Purpose: orchestrate Phase A SE3 price forecast generation and Phase B SE3 consumption ablation.
- Inputs: feature DB path, weather DB path, evidence directory.
- Outputs: `P0054KResult` with status, row counts and evidence paths.
- Side effects: writes local SQLite forecast log table and package-run evidence.
- Test coverage: generator command and targeted unit tests.

`load_se3_price_source_rows(...)`

- Purpose: reconstruct SE3 absolute hourly prices from `system_proxy_se1 + area_diff_proxy_se3`.
- Inputs: local feature DB path.
- Outputs: timestamp-ordered reconstructed price rows.
- Side effects: none.
- Test coverage: unit test for reconstruction.

`build_se3_price_forecast_rows(...)`

- Purpose: create forecast-origin-safe SE3 price forecast rows using P0054H-style origin-local history.
- Inputs: daily 168h windows and reconstructed prices.
- Outputs: forecast log rows for `anchored_absolute_price_forecast_log_p0054k_se3_v1`.
- Side effects: none.
- Test coverage: generator verification and leakage checks.

`persist_se3_price_forecast_log(...)`

- Purpose: persist the Phase A forecast log table.
- Inputs: feature DB path and forecast rows.
- Outputs: row count.
- Side effects: writes/replaces local SQLite table through the existing `persist_rows` helper.
- Test coverage: generator verification.

`validate_se3_price_leakage(...)`

- Purpose: enforce Phase A origin/cutoff/source timestamp leakage contract.
- Inputs: forecast log rows.
- Outputs: leakage review dictionary.
- Side effects: none.
- Test coverage: unit test rejects source timestamps at or after origin.

`load_se3_consumption_rows(...)`

- Purpose: read and normalize `physical_balance_se1_se4_hourly_v1.consumption_se3`.
- Inputs: feature DB path.
- Outputs: normalized SE3 target rows.
- Side effects: none.
- Test coverage: generator verification.

`load_se3_weather_proxy_rows(...)`

- Purpose: read `weather_area_hourly` rows for `se3_load_weather`.
- Inputs: weather DB path.
- Outputs: weather rows keyed by UTC timestamp plus contract metadata.
- Side effects: none.
- Test coverage: generator verification.

`load_se3_price_forecast_rows(...)`

- Purpose: read P0054K forecast-safe SE3 price forecast rows for Phase B.
- Inputs: feature DB path.
- Outputs: normalized price forecast rows plus source contract metadata.
- Side effects: none.
- Test coverage: generator verification.

`build_modeling_rows(...)`

- Purpose: join SE3 target, weather proxy and forecast-origin price rows into direct/weekly modeling examples.
- Inputs: source rows, weather rows, price rows, horizons.
- Outputs: modeling rows with forecast-safe features.
- Side effects: none.
- Test coverage: generator verification.

`feature_group_contract(...)`

- Purpose: define no-price and with-price feature sets and input classifications.
- Inputs: none.
- Outputs: feature contract dictionary.
- Side effects: none.
- Test coverage: unit test for variant naming and forbidden feature exclusion.

`write_p0054k_evidence(...)`

- Purpose: write required P0054K Markdown, JSON and compact CSV evidence.
- Inputs: scored rows, weekly path rows, summary.
- Outputs: evidence path map.
- Side effects: writes files under `requirements/package-runs/P0054K/`.
- Test coverage: generator verification.

## Changed Functions

None outside P0054K.

## Removed Functions

None.

## Durable Function Catalog

After implementation, update:

```text
docs/functions/mac/spotprice-model-diagnostics.md
```

with a P0054K section.
