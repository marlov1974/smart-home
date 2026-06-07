# Package P0055B2: LABB SE3 nonlinear monotone settlement-migration redo

## Status

planned

## Package order

P0055B2

## Label

```text
LABB
```

This package is a forward-moving redo/fix for P0055B after the operator clarification in:

```text
requirements/packages/P0055B-operator-clarification-nonlinear-monotone-migration.md
```

It does not replace P0055B history. It records a new package-scoped implementation and evidence run.

## Purpose

Rebuild the P0055B settlement-migration normalized SE3 decomposition test with cluster-specific, nonlinear and monotone migration treatment.

The package must:

- evaluate every non-zero profiled/load-profile cluster separately
- keep zero clusters at zero
- use train-fit-only migration fitting and reference allocation
- avoid holdout/future allocation leakage
- normalize component history so components sum exactly to SE3 total
- regenerate validation/holdout metrics for the normalized decomposition
- produce the operator-requested migration evidence files

## Required non-zero clusters

```text
C11 C12 C13 C21 C22 C31 C32 C33 C42 C43 C44
```

Zero clusters remain zero unless source data becomes non-zero.

## Method requirements

Use a cluster-specific nonlinear monotone monthly share fit. Smoothness is not required; jumps and flat stretches are acceptable.

The primary fit must be forecast-safe:

- fit only on `train_fit`
- use a latest stable allocation window inside `train_fit`
- hold the reference allocation constant for holdout simulation
- do not use holdout actual shares for primary model or reference

## Evidence requirements

Create or update:

```text
requirements/package-runs/P0055B2/review.md
requirements/package-runs/P0055B2/design.md
requirements/package-runs/P0055B2/functions.md
requirements/package-runs/P0055B2/cluster-specific-migration-rates.md
requirements/package-runs/P0055B2/monthly-delta-analysis.md
requirements/package-runs/P0055B2/nonlinear-monotone-fit-review.md
requirements/package-runs/P0055B2/reference-allocation-review.md
requirements/package-runs/P0055B2/monotonicity-review.md
```

## Restrictions

No API calls, no devices, no runtime activation, no A61/utilization, no flow/capacity features, no spot-price features and no future actual price or load leakage.
