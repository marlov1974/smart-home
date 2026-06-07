# P0055B2 function design

## New functions

`run_p0055b2_analysis`

- Purpose: orchestrate P0055B2 load, fit, normalization, persistence, forecast, evidence and status.
- Inputs: feature DB path and evidence directory.
- Outputs: package result dataclass.
- Side effects: writes LABB evidence files and local DB tables.
- Test coverage: exercised by package run; smaller helpers covered by unit tests.

`pava_non_decreasing`

- Purpose: fit a monotone non-decreasing sequence using pool-adjacent-violators.
- Inputs: ordered monthly shares.
- Outputs: fitted ordered shares.
- Side effects: none.
- Test coverage: monotone and flat/jump behavior.

`fit_cluster_specific_monotone_model`

- Purpose: build train-fit-only cluster-specific nonlinear monotone allocation model.
- Inputs: monthly allocation rows.
- Outputs: model dict with monthly rows, reference shares, per-cluster metrics and leakage flags.
- Side effects: none.
- Test coverage: train-fit/holdout reference isolation.

`cluster_delta_metrics`

- Purpose: calculate operator-required per-cluster monthly delta fields.
- Inputs: ordered share pairs.
- Outputs: monthly_share_start/end, delta series, positive/negative sums, max deltas, negative/flat counts, one-way score and monotone flag.
- Side effects: none.
- Test coverage: required keys and noisy series classification.

`reference_allocation_review`

- Purpose: document latest stable train-fit allocation window and holdout exclusion.
- Inputs: model metadata.
- Outputs: evidence-ready dict.
- Side effects: none.
- Test coverage: through model tests.

`write_p0055b2_evidence`

- Purpose: write compact Markdown/CSV/JSON package evidence.
- Inputs: summary dict.
- Outputs: map of evidence filenames to paths.
- Side effects: writes files under `requirements/package-runs/P0055B2`.
- Test coverage: package run.

## Changed functions

None planned in existing modules. P0055B2 will reuse prior helpers rather than mutating P0055B behavior.

## Removed functions

None.
