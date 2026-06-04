# P0053B-A2 Function Design

New module: `src/mac/services/spotprice_model_diagnostics/p0053ba2.py`

Planned new functions:

- `run_p0053ba2_analysis(feature_db, weather_db, evidence_dir)`: orchestrates source validation, dataset build, model scoring, weekly path scoring and evidence writing. Side effects: writes package evidence only.
- `validate_preconditions(conn)`: checks required source tables and P0053C-B forecast-origin contract. Side effects: none.
- `load_price_forecast_rows(feature_db)`: reads selected SE1 anchored forecast rows and normalizes timestamps. Side effects: none.
- `build_modeling_rows(source_rows, weather_rows, price_rows)`: joins consumption, weather proxy, calendar/load state and G7 price features. Side effects: none.
- `compute_g7_features(path_rows)`: computes target-hour price, ranks, top/bottom flags, relative values, spread and volatility from rows sharing one forecast origin. Side effects: none.
- `select_weekly_holdout_origins(rows)`: returns deterministic complete weekly holdout origins and skipped-origin evidence. Side effects: none.
- `fit_required_models(rows, feature_contract)`: fits Ridge/HGB base and plus_G7 models on validation-origin rows and scores holdout. Side effects: none.
- `evaluate_direct_horizons(scored_rows)`: computes required horizon metrics. Side effects: none.
- `evaluate_weekly_paths(scored_rows, weekly_origins)`: computes required 168h path metrics. Side effects: none.
- `evaluate_conditional_price_response(scored_rows)`: computes top4/top8/bottom/high-rank/cold/weekday/weekend/holiday conditional metrics. Side effects: none.
- `compare_base_plus(metrics)`: computes relative improvements for base vs plus_G7 on identical rows. Side effects: none.
- `validate_leakage_and_fairness(rows, model_inputs)`: verifies no forbidden feature usage, origin grouping and identical row sets. Side effects: none.
- `interpret_result(summary)`: assigns required interpretation category and recommendation. Side effects: none.
- `write_p0053ba2_evidence(evidence_dir, summary, rows)`: writes required Markdown/JSON/CSV evidence. Side effects: file writes under package-run directory.

Changed functions:

- None planned in existing modules.

Removed functions:

- None.

Function catalog:

No durable cross-package function catalog update is planned. P0053B-A2 is an offline diagnostic module and does not introduce a deployable public API.
