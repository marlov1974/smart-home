# P0042 function design

## New module

`src/mac/services/spotprice_model_diagnostics/p0042.py`

## New functions

`run_p0042_analysis(...) -> P0042Result`

- End-to-end corrected dataset/evidence builder.
- Writes local v2 SQLite tables and package-run evidence.

`parse_utc_timestamp(value) -> datetime`

- Parses source UTC timestamps as timezone-aware UTC datetimes.

`attach_time_fields(rows) -> None`

- Adds `timestamp_utc`, Stockholm diagnostic fields and fixed-CET model fields.

`build_m2_tables_v2(rows) -> dict`

- Builds M2A/M2C/M2D normal weather surfaces on fixed-CET model buckets.

`build_daily_weather_v2(rows) -> dict`

- Aggregates weather actual/normal/delta on fixed-CET model days.

`derive_scale_policy(rows) -> dict`

- Computes target-series-specific scale floors. SE1 keeps `0.001`; area_diff uses the median complete model-day generic area_diff scale.

`scale_for_target(values, target_series, policy) -> float`

- Applies generic robust scale plus target-specific floor.

`build_ai1_rows_v2(rows, daily_weather, policy) -> tuple`

- Builds corrected AI-1 rows over fixed-CET model dates.

`build_ai2_rows_v2(rows, policy) -> list`

- Builds corrected AI-2 rows over fixed-CET model dates.

`classify_skipped_center_dates_v2(rows, daily_weather) -> list`

- Audits remaining AI-1 skipped model center dates.

`compare_scale_policies(rows) -> dict`

- Compares candidate area_diff policies A-F for evidence.

`persist_p0042_tables(feature_db, ...) -> None`

- Writes corrected v2 local SQLite tables.

`write_p0042_evidence(...) -> dict`

- Writes required P0042 evidence files and JSON summaries.

## Changed functions

None in existing modules. P0042 is additive.

## Removed functions

None.
