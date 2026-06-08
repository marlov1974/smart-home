# P0056G Function Design

## New Functions In `p0056g.py`

- `run_p0056g_weekly_walk_forward(feature_db, evidence_dir)`: Orchestrates schema creation, input loading, weekly jobs, persistence, evidence writing and status decision.
- `create_schema(conn)`: Creates P0056G forecast and metrics tables.
- `load_inputs(conn)`: Loads target and weather rows by required area and validates source contracts.
- `weekly_windows(target_contract, weather_contract)`: Produces complete Monday-Sunday windows from 2025-06 onward through the latest complete local week.
- `build_weekly_rows(area_code, target_rows, weather_rows, week)`: Builds 168 forecast rows for one area-week using only origin-time load lags and target-hour calendar/weather proxy features.
- `fit_weekly_hgb(rows, feature_names, spec)`: Fits deterministic HGB on train rows and predicts the weekly delivery rows.
- `score_week(rows, prediction_column)`: Computes full-week and forward-only MAE/RMSE/bias, energy error, p90/p95, weekday/weekend and regime metrics.
- `aggregate_area_results(weekly_results)`: Computes mean/median/p90/worst/best week, period bias and energy summaries.
- `compare_to_static_baseline(area_summaries)`: Calculates deltas against committed P0056 static baselines.
- `structural_diagnostics(weekly_results)`: Calculates rolling actual load, weekly bias, week-over-week and year-over-year load change diagnostics.
- `leakage_review(jobs, feature_names)`: Verifies cutoff/origin/target ordering and forbidden feature exclusion.
- `progress(evidence_dir, area_code, week_id, model_id, phase, status, ...)`: Prints and persists required progress lines.
- `write_evidence(evidence_dir, summary)`: Writes all package-required evidence files and compact CSV/JSON.
- `main()`: CLI entry point for package execution.

## Side Effects

- Writes only P0056G evidence files under `requirements/package-runs/P0056G/`.
- Writes compact P0056G forecast and metric rows to local feature DB P0056G tables.
- No API calls, no device writes, no runtime changes.

## Test Coverage

- Weekly window timestamps and 168/162 split.
- Leakage order and forbidden feature check.
- Weekly metric computation on deterministic synthetic rows.
