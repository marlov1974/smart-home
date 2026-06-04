# P0054D Function Design

Package: P0054D
Label: LABB

## Weather History Changes

`initialize_schema(path)` changed:

- Adds three `se4_load_weather` locations to default weather location registration.
- Adds view `weather_proxy_se4_load_hourly`.
- Side effects: only schema/config upsert in the local weather SQLite DB when called.

`validate_proxy_groups(conn, start_date, end_date, db_path)`

- Changed to validate all active configured area proxies instead of only the four P0032 proxies.
- Reason: P0054D adds `se4_load_weather` and validation must cover it.

## New P0054D Modeling Functions

`run_p0054d_analysis(feature_db, weather_db, evidence_dir)`

- Orchestrates the corrected SE4 LABB experiment and evidence writing.

`load_se4_consumption_rows(feature_db)`

- Reads canonical SE4 consumption target rows.

`load_weather_proxy_rows(weather_db)`

- Reads `weather_proxy_se4_load_hourly` / `se4_load_weather` rows.

`weather_proxy_definition()`

- Returns P0054D location/coordinate/weight definition for evidence and tests.

`fit_hgb_benchmark(rows, features)`, `fit_advanced_mlp(rows, features)`, `fit_extra_trees(rows, features)`

- Train deterministic HGB, MLP and ExtraTrees on identical train rows and score validation/holdout.

`compare_models(model_results, p0054c_summary)`

- Compares P0054D models and summarizes old P0054C evidence comparison.

Other helper functions mirror P0054C for row construction, leakage-safe lags/rollups, baseline scoring, direct horizon metrics, weekly path metrics, conditional metrics and evidence writing.

## Removed Functions

None.

## Durable Function Catalog

Update `docs/functions/mac/weather-history-dataset.md` because `se4_load_weather` becomes a durable weather-history proxy group.
