# P0045 function design

New module: `src.mac.services.spotprice_model_diagnostics.p0045`

Planned functions/classes:

- `run_p0045_combination(feature_db, evidence_dir)`: orchestrates data loading, prediction regeneration, 168h window evaluation and evidence writing.
- `load_corrected_inputs(feature_db)`: loads only P0042 v2 AI-1 and AI-2 tables.
- `validate_input_contract(ai1_rows, ai2_rows)`: verifies corrected table contracts, target columns, timestamp-backed hourly rows and required target series.
- `assign_splits(rows)`: applies P0043/P0044 chronological split policy.
- `regenerate_ai2_predictions(ai2_rows)`: regenerates selected AI-2 `hour_shape` predictions from P0043 selected groups.
- `regenerate_ai1_predictions(ai1_rows)`: regenerates selected/fallback AI-1 daily predictions from P0044 target usage policy.
- `build_forecast_windows(ai2_rows, ai1_rows)`: builds fixed-CET D 00 through D+6 23 windows with exactly 168 hourly rows.
- `combine_window(window, ai1_predictions, ai2_predictions, formula, series)`: produces centered 168h combined shape forecasts.
- `baseline_predictions(window, ...)`: produces B0-B5 predictions with oracle baselines labeled.
- `actual_shape(window)`: computes centered unscaled and robust-scaled actual 168h shape from historical hourly prices.
- `evaluate_window(actual, predicted)`: computes shape, rank, day allocation and intraday metrics.
- `summarize_metrics(window_results)`: summarizes validation/holdout metrics per series/formula/baseline.
- `select_formula(summary)`: selects deployable formula by validation scaled shape MAE, excluding oracle diagnostics.
- `subset_metrics(windows)`: reports normal/holiday/bridge/season/weather subset metrics.
- `best_worst_windows(window_results)`: lists best/worst holdout windows.
- `write_p0045_evidence(evidence_dir, summary)`: writes required markdown and JSON evidence.

Changed functions:

- `docs/functions/mac/spotprice-ml-normal-model.md` is updated with P0045 combination behavior.

Removed functions:

- None.

Side effects:

- Reads local SQLite feature DB.
- Writes package-run evidence under `requirements/package-runs/P0045/`.
- Does not write model binaries, APIs, device state, KVS, Shelly or Home Assistant.
