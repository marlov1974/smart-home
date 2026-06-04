# P0053C-B Function Design

New module: `src/mac/services/spotprice_model_diagnostics/p0053cb.py`

Planned new functions:

- `run_p0053cb_anchoring(feature_db, evidence_dir)`: orchestrates validation, M4 shape regeneration, anchoring, metrics, persistence and evidence writing. Inputs are paths. Outputs a result dataclass. Side effects: writes SQLite table and package evidence.
- `validate_preconditions(conn)`: checks P0053C-A predecessor table and actual SE1 source table. Inputs are a SQLite connection. Outputs a dict. Side effects: none.
- `prepare_shape_windows(feature_db)`: loads corrected inputs, applies P0053C policy splits, regenerates AI-1/AI-2 predictions and returns SE1 validation/holdout windows plus selected shape formula. Side effects: model fitting in memory only.
- `load_actual_prices(feature_db)`: reads SE1 actual hourly prices and normalizes timestamps to UTC `Z`. Outputs a timestamp keyed dict plus row metadata. Side effects: none.
- `build_anchor_state(origin_utc, prices_by_ts)`: returns hist48, last24, timestamps and leakage-safe anchor window metadata. Side effects: none.
- `anchor_prediction(method, shape_value, row, anchor_state)`: computes A0-A3 anchored absolute prediction for one row. Outputs predicted value and anchor metadata. Side effects: none.
- `evaluate_anchor_methods(windows, shape_predictions, prices_by_ts)`: creates row/path metric inputs for A0-A3 and baselines. Outputs rows and metrics. Side effects: none.
- `select_anchor_method(metrics)`: selects among A0-A3 using validation `MAE_full_168h`, with validation rank/top8 tie-break. Side effects: none.
- `build_forecast_origin_rows(evaluated_rows, selected_method)`: creates rows for the durable SQLite log. Side effects: none.
- `persist_forecast_origin_log(feature_db, rows)`: writes `m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1`. Side effects: replaces local SQLite diagnostics table.
- `leakage_review(rows, anchor_evidence)`: proves timestamp inequalities and no future target-window price use. Side effects: none.
- `aggregate_metrics(rows)`: computes required scalar and path metrics by split/method. Side effects: none.
- `write_p0053cb_evidence(evidence_dir, summary, log_rows)`: writes required package-run files, JSON and sample CSV. Side effects: file writes under `requirements/package-runs/P0053C-B/`.

Changed functions:

- None planned in existing modules.

Removed functions:

- None.

Durable function catalog:

No cross-package function catalog update is planned initially because P0053C-B anchoring helpers are package-specific diagnostics. If a later package reuses anchored absolute forecast logs as a general interface, the forecast-origin table contract should be promoted to `docs/functions/` or a forecast log contract document then.
