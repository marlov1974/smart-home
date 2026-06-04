# P0054L Function Design

## New Module

```text
src.mac.services.spotprice_model_diagnostics.p0054l
```

## New Functions

`run_p0054l_analysis(...)`

- Purpose: orchestrate SE3 price target loading, feature construction, candidate model training/evaluation, baseline comparison, forecast-log persistence and evidence writing.
- Inputs: feature DB path and evidence directory.
- Outputs: `P0054LResult`.
- Side effects: writes local SQLite forecast log and package-run evidence.
- Test coverage: generator command and unit tests.

`load_se3_price_target_rows(...)`

- Purpose: reconstruct SE3 absolute spot price from local SE1 and SE3-SE1 rows.
- Inputs: feature DB path.
- Outputs: normalized timestamp-ordered price rows.
- Side effects: none.
- Test coverage: unit test.

`load_p0054k_baseline_rows(...)`

- Purpose: read comparable P0054K baseline forecast rows.
- Inputs: feature DB path.
- Outputs: normalized forecast rows keyed by origin/target/horizon.
- Side effects: none.
- Test coverage: generator verification.

`build_forecast_examples(...)`

- Purpose: create direct/path forecast examples with target values and origin-safe features.
- Inputs: target rows and baseline-origin cadence.
- Outputs: modeling examples.
- Side effects: none.
- Test coverage: unit test for source timestamp cutoff.

`price_history_features_at_origin(...)`

- Purpose: derive lag, rolling, volatility and anchor features from historical SE3 price before origin.
- Inputs: price values, origin index.
- Outputs: numeric feature dictionary plus feature source max timestamp.
- Side effects: none.
- Test coverage: unit test.

`model_specs(...)`

- Purpose: build bounded HGB, ExtraTrees, LightGBM and XGBoost candidate specs depending on imports.
- Inputs: import status.
- Outputs: model spec list.
- Side effects: imports optional model packages.
- Test coverage: generator verification.

`fit_candidate_model(...)`

- Purpose: train one candidate on internal_train/train_fit rows and score validation/holdout rows.
- Inputs: examples, features, model spec.
- Outputs: model result with metrics and predictions.
- Side effects: none; no artifact persistence.
- Test coverage: generator verification.

`evaluate_price_metrics(...)`, `evaluate_weekly_paths(...)`, `evaluate_ranking_spike_ramp(...)`

- Purpose: compute required broad, path, ranking, spike and ramp metrics.
- Inputs: scored rows and prediction columns.
- Outputs: metric dictionaries.
- Side effects: none.
- Test coverage: unit tests for ranking helper.

`compare_models(...)`

- Purpose: compare candidates and P0054K baseline under the learning threshold.
- Inputs: direct/path/ranking metrics.
- Outputs: model comparison and recommendation.
- Side effects: none.
- Test coverage: generator verification.

`persist_advanced_forecast_log(...)`

- Purpose: write the recommended holdout-safe advanced forecast table.
- Inputs: scored rows and recommended prediction column.
- Outputs: row count.
- Side effects: writes local SQLite table.
- Test coverage: generator verification.

`validate_leakage(...)`

- Purpose: verify cutoff/order/source timestamp restrictions and absence of forbidden feature groups.
- Inputs: examples and feature contract.
- Outputs: leakage review.
- Side effects: none.
- Test coverage: unit test.

`write_p0054l_evidence(...)`

- Purpose: write required Markdown, JSON and compact CSV evidence.
- Inputs: summary and compact row outputs.
- Outputs: evidence path map.
- Side effects: writes under `requirements/package-runs/P0054L/`.
- Test coverage: generator verification.

## Changed Functions

None outside P0054L.

## Removed Functions

None.

## Durable Function Catalog

After implementation, update:

```text
docs/functions/mac/spotprice-model-diagnostics.md
```
