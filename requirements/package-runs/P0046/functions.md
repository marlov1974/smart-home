# P0046 function design

## New functions

`run_p0046_backtest(feature_db, evidence_dir)`

- Purpose: orchestrate the P0046 anchored absolute-price backtest and evidence writing.
- Inputs: feature DB path, evidence directory path.
- Outputs: `P0046Result` with status, selected SE1 configuration, window counts and evidence paths.
- Side effects: reads local SQLite feature DB; writes P0046 evidence files.
- Test coverage: package verification plus unit tests for selected helpers.

`build_origin_windows(ai1_rows, ai2_rows)`

- Purpose: build accepted 168h forecast windows from Monday 06:00 fixed-CET model time.
- Inputs: corrected AI-1/AI-2 rows.
- Outputs: list of window dictionaries with hourly rows and split.
- Side effects: none.
- Test coverage: exact 168h window and split tests.

`window_shape_predictions(window, ai1_predictions, ai2_predictions, time_profiles)`

- Purpose: produce P0045 selected SE1 shape and required baseline shapes for one window.
- Inputs: one window and regenerated prediction maps.
- Outputs: mapping of predictor name to 168h shape list.
- Side effects: none.
- Test coverage: P0045 source and no-retraining guard tests.

`fit_anchor(method, actual_anchor, shape_anchor, anchor_count)`

- Purpose: fit L1/L2/L3 anchoring parameters using anchor hours only.
- Inputs: method name, anchor actual values, anchor shape values, anchor count.
- Outputs: finite anchor parameter dictionary.
- Side effects: none.
- Test coverage: finite forecast and guardrail tests.

`apply_anchor(params, shape)`

- Purpose: transform a shape forecast into absolute prices.
- Inputs: anchor parameter dictionary and 168h shape.
- Outputs: absolute forecast list.
- Side effects: none.
- Test coverage: finite forecast tests.

`evaluate_anchored_window(window, predictor, method, anchor_count, forecast)`

- Purpose: evaluate one anchored forecast on hours after the anchor region.
- Inputs: window, predictor name, anchor method, anchor count, forecast.
- Outputs: metric dictionary.
- Side effects: none.
- Test coverage: anchor exclusion and no-future-anchor tests.

`summarize_metrics(rows)`

- Purpose: aggregate window-level rows by target/split/predictor/anchor/method.
- Inputs: window result rows.
- Outputs: nested summary dictionary.
- Side effects: none.
- Test coverage: chronological separation tests.

`select_se1_configuration(summary)`

- Purpose: select deployable SE1 anchoring configuration from validation results only.
- Inputs: aggregated metrics.
- Outputs: selected predictor/method/anchor scenario.
- Side effects: none.
- Test coverage: validation-only selection test.

`write_p0046_evidence(evidence_dir, summary)`

- Purpose: write required Markdown and JSON evidence.
- Inputs: evidence directory and run summary.
- Outputs: mapping of evidence labels to paths.
- Side effects: creates/updates P0046 evidence files.
- Test coverage: package verification.

## Changed functions

None planned.

## Removed functions

None planned.

## Unchanged but relevant functions

`p0045.combine_window(...)`

- Purpose: source of the P0045 selected 168h shape formula used by P0046.
- Reason relevant: P0046 must prove it uses the P0045 selected SE1 shape source.

`p0045.regenerate_ai1_predictions(...)` and `p0045.regenerate_ai2_predictions(...)`

- Purpose: deterministic regeneration of P0045 evaluation artifacts from corrected train rows.
- Reason relevant: P0046 reuses these without adding new model search.
