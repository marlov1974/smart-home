# P0056J Implementation Design

## Package Interpretation

P0056J audits the SE2 metric gap between the static holdout pipeline and rolling/origin pipelines by comparing sampled rows with the same `(forecast_origin_timestamp_utc, target_timestamp_utc)` keys.

The main comparison is:

- static pipeline: persisted P0056F W12 static forecast rows plus reconstructed P0056F/P0056E-style feature rows.
- rolling pipeline: persisted P0056I TWX forecast rows plus reconstructed P0056H2 static-style origin-row features.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0056j.py`.

The module will:

1. Load persisted P0056F W12 static forecast rows for SE2.
2. Load persisted P0056I TWX rolling forecast rows for SE2.
3. Reconstruct static P0056F W12 feature rows using existing P0056E/P0056F helpers.
4. Reconstruct rolling P0056I/TWX feature rows using existing P0056H2 helpers.
5. Select at least 10 origins covering multiple months, weekdays, high-error and low-error cases.
6. Compute row-level prediction diff, target-row intersection and feature-diff summaries.
7. Reconstruct metrics on the sampled row intersection and compare against original package metrics.
8. Review hypotheses H1-H8 and write compact evidence.

## Intended Changes

- New package-run evidence under `requirements/package-runs/P0056J/`.
- New audit module `p0056j.py`.
- New unit tests for row intersection and feature diff helpers.
- Update P0056J package completion notes after execution.

## Deliberate Refactoring Decisions

No shared model code will be refactored. P0056J is audit-only and can reuse existing helper functions without making a general audit framework.

## Test Strategy

- Unit-test row-key intersection.
- Unit-test numeric feature-diff summary.
- Compile the new module.
- Run the package module against local DB and compact evidence only.
- Verify required evidence, DB-independent result files, `git diff --check`, and no large artifacts.

## Risks and Uncertainties

- Static exact model artifacts, ensemble internals and horizon-bias objects are not persisted. Training/model comparison must document what can be known from code/evidence and what cannot.
- Static P0056F persisted rows include selected full36/dayahead holdout rows, not necessarily every rolling-origin row. This is part of the audit, not a blocker.
- The audit is SE2-only by design.
