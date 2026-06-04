# P0053C Function Design

## New Functions

### `canonical_split_for_timestamp(timestamp_utc)`

- Purpose: classify a UTC timestamp into `train`, `validate` or `holdout`.
- Inputs: UTC timestamp text or datetime.
- Outputs: split string.
- Side effects: none.
- Reason: reusable global split policy.
- Test coverage: boundary unit tests.

### `is_modeling_target_timestamp(timestamp_utc)`

- Purpose: decide whether a row can be scored/trained/evaluated under the global modeling period.
- Inputs: UTC timestamp text or datetime.
- Outputs: boolean.
- Side effects: none.
- Reason: enforce `timestamp_utc >= 2022-06-01T00:00:00Z`.
- Test coverage: pre-start filtering test.

### `policy_summary()`

- Purpose: expose policy metadata for evidence files.
- Inputs: none.
- Outputs: dictionary with boundaries and rules.
- Side effects: none.
- Reason: evidence and later package reuse.
- Test coverage: constants checked through split tests.

## Changed Functions

### `build_direct_horizon_rows(...)`

- Change: skip target rows earlier than the policy modeling start while allowing prior source rows as context-only lag warmup.
- Reason: P0053C dataset filtering rule.
- Test coverage: new context-only lag warmup test.

### `assign_chronological_splits(...)`

- Change: classify rows by `target_timestamp_utc` via the global policy instead of fixed-CET date constants.
- Reason: P0053C says `timestamp_utc` is primary split identity.
- Test coverage: updated chronological split test.

### `split_for_date(...)`

- Change: replace use sites with timestamp-based policy or keep as a compatibility wrapper only if needed.
- Reason: holdout starts `2025-06-01T00:00:00Z`, not 2026.
- Test coverage: path-origin split test.

### `regression_metric_from_predictions(...)`

- Change: add `mean_actual_mw`, `median_actual_mw`, `p10_actual_mw`, `p90_actual_mw`, `MAE_percent_of_mean` and `MAE_percent_of_median`.
- Reason: P0053C relative error requirement.
- Test coverage: relative metrics unit test.

## Removed Functions

None.

## Function Catalog

`docs/functions/mac/spotprice-model-diagnostics.md` will be updated if the policy module becomes durable cross-package interface.
