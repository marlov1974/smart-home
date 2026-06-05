# P0054N Function Design

## New Functions

`run_p0054n_analysis(...)`

- Purpose: orchestrate P0054N exact-origin 36h/DayAhead evaluation and evidence writing.
- Inputs: feature DB path, weather DB path, evidence directory.
- Outputs: `P0054NResult`.
- Side effects: writes package-run evidence only.
- Tests: exercised by package command; unit tests cover helper behavior.

`dayahead_origin_utc_for_delivery_day(...)`

- Purpose: convert Swedish DayAhead decision time `12:00 Europe/Stockholm D-1` to UTC.
- Inputs: delivery date.
- Outputs: normalized UTC timestamp text.
- Side effects: none.
- Tests: DST conversion unit tests.

`delivery_day_target_utc_hours(...)`

- Purpose: list local delivery day target hours converted to UTC.
- Inputs: delivery date.
- Outputs: 24 normalized UTC timestamp texts, except documented DST edge behavior.
- Side effects: none.
- Tests: unit test for ordinary and DST-adjacent days.

`build_p0054n_exact_origin_price_rows(...)`

- Purpose: create in-memory advanced SE3 price forecasts for exact 12:00-local origins and horizons 0..35.
- Inputs: SE3 price source rows.
- Outputs: forecast rows plus contract.
- Side effects: none.
- Tests: safety properties covered by matrix safety and command evidence.

`build_exact_origin_price_examples(...)`

- Purpose: create P0054L2-compatible price examples for caller-provided origins.
- Inputs: price source rows, origin timestamps, horizons.
- Outputs: examples with P0054L2 feature dicts.
- Side effects: none.
- Tests: command evidence validates row counts and cutoffs.

`evaluate_full_36h_paths(...)`

- Purpose: calculate complete-origin full_36h metrics and per-origin compact rows.
- Inputs: scored path rows and prediction columns.
- Outputs: summary and per-origin metrics.
- Side effects: none.
- Tests: complete-origin filtering unit test.

`evaluate_dayahead_delivery_days(...)`

- Purpose: calculate DayAhead delivery-day 24h metrics using exact local decision times.
- Inputs: scored path rows and prediction columns.
- Outputs: summary and compact per-day metrics.
- Side effects: none.
- Tests: row selection unit test.

`compare_advanced_price_ablation_36h(...)`

- Purpose: compare paired no-price and with-advanced-price metrics for direct, full_36h and DayAhead results.
- Inputs: model results, full_36h summary, DayAhead summary.
- Outputs: ablation summary.
- Side effects: none.
- Tests: delta convention unit test.

`write_p0054n_evidence(...)`

- Purpose: write required P0054N Markdown, JSON and compact CSV evidence.
- Inputs: summary and compact rows.
- Outputs: map of evidence file paths.
- Side effects: package-run file writes.
- Tests: package command verifies output.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Docs

Update `docs/functions/mac/spotprice-model-diagnostics.md` to add P0054N function summary after implementation.
