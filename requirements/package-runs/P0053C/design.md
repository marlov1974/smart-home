# P0053C Implementation Design

## Package Interpretation

P0053C is a governance and rebuild package. It should make the split policy reusable, mark old metrics as stale where needed, and rebuild P0053B SE1 consumption diagnostics under the new policy.

## Implementation Structure

- Add `src/mac/services/spotprice_model_diagnostics/forecast_period_policy.py`.
- Add unit tests for split boundaries and context-only lag warmup semantics.
- Update `src/mac/services/spotprice_model_diagnostics/p0053b.py` to:
  - filter target/scored rows to `timestamp_utc >= 2022-06-01T00:00:00Z`
  - keep pre-start rows available only for lag/context lookup
  - split by target `timestamp_utc`, not fixed-CET date
  - include policy metadata and relative error metrics in evidence
- Update P0053B tests for the new holdout boundary.
- Create `memory/spotprice-forecast-period-policy.md`.
- Write P0053C evidence files including old-split audit, stale metric classification and rebuild metrics.

## Deliberate Refactoring Decisions

The policy gets its own module because later packages need the same constants and tests. P0053B keeps its package-specific modeling code; this package does not create a broad framework or rewrite old P0043/P0044/P0045 tools.

## Test Strategy

- Unit tests cover canonical split boundaries, no pre-start scored rows, context-only lag warmup, non-overlap and relative metrics.
- Rebuild P0053B analysis locally under the new policy.
- Run `git diff --check`.

## Risks And Uncertainties

- P0043/P0044/P0045 rebuild investigation may remain planning/audit only; P0053C-A appears to own the price-shape rebuild follow-up.
- P0053B model metrics after the split change are not apples-to-apples with old P0053B metrics and must be labeled stale/incompatible.
