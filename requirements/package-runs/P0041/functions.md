# P0041 function design

## New module

`src/mac/services/spotprice_model_diagnostics/p0041.py`

## New/changed functions

`run_p0041_analysis(feature_db, price_db, weather_db, evidence_dir) -> P0041Result`

- Purpose: End-to-end P0041 dataset build and evidence generation.
- Inputs: Local DB paths and evidence directory.
- Outputs: Status, row counts, skipped windows and evidence path map.
- Side effects: Writes local feature DB tables and package-run evidence files.
- Tests: Integration execution plus unit coverage for called pure functions.

`robust_scale(values, fixed_min_scale=0.001) -> float`

- Purpose: Positive robust scale used by AI-1 and AI-2 target formulas.
- Inputs: Numeric values.
- Outputs: Strictly positive float.
- Side effects: None.
- Tests: Flat, near-zero and negative fixtures.

`safe_ratio(numerator, denominator, fixed_min_scale=0.001) -> float | None`

- Purpose: Diagnostic-only ratio with unsafe denominator handling.
- Inputs: Numerator and denominator.
- Outputs: Ratio or null.
- Side effects: None.
- Tests: Unsafe and safe denominator fixtures.

`local_window_dates(day) -> list[date]`

- Purpose: Define the AI-1 local seven-day window exactly as `D-2..D+4`.
- Inputs: Center date.
- Outputs: Seven dates.
- Side effects: None.
- Tests: Exact first/last/count.

`fit_m2_hourly_normals(rows, signal_name, field) -> list[dict]`

- Purpose: Build smooth cyclic day-of-year/hour normal rows for M2A/M2C/M2D.
- Inputs: Historical rows and signal field.
- Outputs: Normal rows.
- Side effects: None.
- Tests: M2 fields present via fixtures.

`attach_m2_features(rows, normals_by_signal) -> None`

- Purpose: Add hourly actual/normal/delta features to working rows.
- Inputs: Rows and normal maps.
- Outputs: Mutated rows.
- Side effects: Mutates local in-memory row dictionaries only.
- Tests: M2 field presence.

`build_daily_weather(rows) -> dict[date, dict]`

- Purpose: Aggregate hourly actual/normal/delta weather features and wind diagnostics by local date.
- Inputs: Enriched hourly rows.
- Outputs: Daily feature map.
- Side effects: None.
- Tests: Covered through dataset fixture tests.

`build_ai1_rows(rows, daily_weather) -> tuple[list[dict], dict]`

- Purpose: Build day-to-local-week target rows for both target series.
- Inputs: Enriched rows and daily weather map.
- Outputs: Dataset rows and skip summary.
- Side effects: None.
- Tests: Hand fixture formula, window behavior and cross-year window behavior.

`classify_skipped_center_dates(rows, daily_weather) -> list[dict]`

- Purpose: Explain each skipped AI-1 center date using package-approved reason categories.
- Inputs: Enriched hourly rows and daily weather map.
- Outputs: Skip details with reason, missing price/weather dates and local price-hour counts.
- Side effects: None.
- Tests: DST day classification and evidence regeneration.

`skip_reason(day, window, missing_price, missing_weather, by_day, min_day, max_day) -> str`

- Purpose: Map missing-window facts to one reason: `missing_price_hours`, `missing_weather_daily`, `dataset_start_boundary`, `dataset_end_boundary`, `year_boundary_bug`, `dst_or_timezone_issue` or `other`.
- Inputs: Center date, local window, missing facts, day map and dataset boundaries.
- Outputs: Reason string.
- Side effects: None.
- Tests: DST classifier and cross-year AI-1 fixture.

`build_ai2_rows(rows) -> list[dict]`

- Purpose: Build hour-to-day target rows for both target series.
- Inputs: Enriched rows.
- Outputs: Dataset rows.
- Side effects: None.
- Tests: Hand fixture formula and mean `hour_shape`.

`persist_p0041_tables(feature_db, m2_tables, ai1_rows, ai2_rows) -> None`

- Purpose: Store package output tables in local SQLite.
- Inputs: Feature DB path and generated rows.
- Outputs: None.
- Side effects: Writes local SQLite feature DB only.
- Tests: Exercised by package run; not committed.

`write_p0041_evidence(evidence_dir, ...) -> dict[str, str]`

- Purpose: Write required P0041 evidence files and compact JSON summaries.
- Inputs: Generated datasets and summaries.
- Outputs: Evidence path map.
- Side effects: Writes package-run evidence files.
- Tests: Exercised by package run.

## Removed functions

None.
