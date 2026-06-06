# P0054V functions

Planned new module: `src/mac/services/spotprice_model_diagnostics/p0054v.py`.

## New functions

`run_p0054v_analysis(...)`

Purpose: orchestrate P0054V baseline gate, stitched price feature construction, M1 family evaluation and evidence writing.

Inputs: feature DB path, weather DB path, evidence directory.

Outputs: `P0054VResult` with status, row counts and evidence file paths.

Side effects: writes package evidence only.

Tests: covered indirectly by package run and unit tests for helper functions.

`run_baseline_gate(...)`

Purpose: reproduce P0054R M1 no-price DayAhead baseline in a temporary directory.

Inputs: feature DB path, weather DB path.

Outputs: compact gate result.

Side effects: temporary files only.

`build_full_contract_rows(...)`

Purpose: build corrected ENTSO-E SE3 P0054R direct/path rows with P0054R split/profile features.

Inputs: feature DB path, weather DB path.

Outputs: source rows, direct rows, path rows and contracts.

`load_actual_se3_spot_prices(...)`

Purpose: load reconstructed actual SE3 spot history from local SQLite.

Inputs: feature DB path.

Outputs: timestamp-to-price map plus source contract.

`build_price_forecast_rows(...)`

Purpose: create forecast-safe future SE3 price predictions for all P0054R origin/target rows.

Inputs: price rows, required origin/target pairs.

Outputs: forecast row mapping and price forecast source contract.

`build_anchor_features(...)`

Purpose: compute actual spot history features strictly before forecast origin.

Inputs: origin timestamp, actual price map.

Outputs: anchor feature values and source timestamp audit.

`build_stitched_price_features(...)`

Purpose: compute P0054V actual-history/forecast-future stitched price features for a row.

Inputs: modeling row, actual price map, forecast price map and train thresholds when needed.

Outputs: feature dictionary and leakage audit.

`attach_price_feature_families(...)`

Purpose: add P1/P2/P3/P4 feature columns to rows using identical full coverage.

Inputs: direct/path rows, actual prices, forecast prices, train-fit thresholds.

Outputs: price feature contract, coverage summary and leakage audit.

`fit_m1_for_family(...)`

Purpose: fit and evaluate the HorizonBiasCorrected WeightedEnsemble for one feature family.

Inputs: rows, path rows, feature names, model specs and family id.

Outputs: prediction column, training evidence and scored rows.

`score_family(...)`

Purpose: evaluate one family for DayAhead, full_36h and daily-energy metrics.

Inputs: scored path rows and prediction column.

Outputs: compact metric row.

`compare_price_families(...)`

Purpose: compute P1/P2/P3/P4 deltas versus P0 and classify default/conditional/excluded.

Inputs: family metrics and regime metrics.

Outputs: decision summary.

`write_p0054v_evidence(...)`

Purpose: write required Markdown, JSON and CSV evidence files.

Inputs: summary object.

Outputs: evidence file path mapping.

Side effects: writes package-run files only.

## Durable docs

Update `docs/functions/mac/spotprice-model-diagnostics.md` after implementation with the actual function set and limitations.
