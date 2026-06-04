# P0053C-A Implementation Design

## Package Interpretation

P0053C-A rebuilds P0045-style M4 price-shape diagnostics under the P0053C global split policy and creates a forecast-origin-safe holdout log for shape/index predictions.

## Implementation Structure

- Add `src/mac/services/spotprice_model_diagnostics/p0053ca.py` as a package wrapper.
- Reuse P0045 input loading, input validation, AI-1/AI-2 prediction regeneration, combination formulas and metrics.
- Assign splits with `forecast_period_policy.canonical_split_for_timestamp(...)`.
- Filter target rows so no scored/trained target timestamp is before `2022-06-01T00:00:00Z`.
- Build 168h windows only when all hourly target rows are inside the same canonical split.
- Persist a local SQLite forecast-origin log table for holdout selected-formula shape/index predictions.
- Write P0053C-A evidence files and a compact forecast-origin log sample CSV.

## Deliberate Refactoring Decisions

Old P0043/P0044/P0045 modules are left as historical package implementations. The new wrapper centralizes P0053C-A policy behavior without rewriting old package evidence semantics.

## Test Strategy

- Unit tests cover split filtering, non-overlap, forecast-origin log schema and timestamp ordering.
- Run the P0053C-A rebuild locally.
- Run focused tests plus the existing P0045 tests.
- Run `git diff --check`.

## Risks And Uncertainties

- The forecast-origin log contains `prediction_kind=shape_index`, not absolute prices.
- Rolling weekly origins are deferred; the first safe log uses one holdout origin/cutoff.
- Validation and holdout windows are overlapping rolling 168h windows, so metrics are diagnostics rather than iid confidence estimates.
