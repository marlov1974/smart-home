# P0054I Implementation Design

## Package Interpretation

Define and apply a LABB-specific train-through-May-2025 split policy for the next P0054 SE1 consumption price-forecast ablation and related comparisons.

## Implementation Structure

Documentation and evidence only:

- create required P0054I package-run evidence files
- query P0054H's SQLite forecast table for coverage under the new split
- update the active package completion notes

No source code changes are needed because P0054I does not train or run models.

## Files Intended To Change

```text
requirements/packages/P0054I-labb-unified-holdout-train-through-may-2025.md
requirements/package-runs/P0054I/**
```

## Files Intentionally Not Changed

```text
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
src/**
tests/**
```

Reason: P0054I is a named LABB experiment-family policy, not a global replacement for the P0053C canonical policy and not a code package.

## Verification Strategy

Run direct local SQLite coverage checks for P0054H:

- target timestamp split coverage
- forecast origin split coverage
- required source filters

Review P0054H leakage evidence and record the downstream contract.

Final checks:

- `git diff --check`
- confirm no source/test/deploy/runtime files changed
- confirm no large package artifacts

## Risks And Uncertainties

The first available P0054H target timestamp is `2022-06-01T23:00:00Z`, not exactly `2022-06-01T00:00:00Z`, because 168h paths and fixed-CET source rows start at the first available complete origin after warmup. This is acceptable as a documented warmup/hour-boundary caveat and does not create leakage.
