# P0055B operator clarification: nonlinear monotone migration requirements

## Status

clarification for P0055B

## Operator intent

When reviewing P0055B results, do not accept an overly simple global linear migration model unless the data actually supports it.

The migration from residual/metred-non-profiled bucket into profiled/load-profile clusters is expected to be:

```text
heterogeneous by cluster/customer type
heterogeneous by retailer/grid-owner strategy
nonlinear and sometimes jumpy month-to-month
one-way or mostly one-way
largest historical correction early in the period
smallest correction near holdout
```

## Required interpretation

P0055B should not assume that every cluster converts at the same speed.

Different clusters may have different migration rates because:

```text
- different customer types have different conversion upside/downside
- local retailers may have different product phase-out strategy
- grid owners may handle metering/settlement conversion differently
- urban/suburban/rural/industrial mixes may convert at different pace
```

## Cluster-specific migration rates

P0055B must estimate or at least evaluate migration separately for each non-zero profiled cluster:

```text
C11
C12
C13
C21
C22
C31
C32
C33
C42
C43
C44
```

Zero clusters should remain zero unless new data appears.

Required per-cluster outputs:

```text
monthly_share_start
monthly_share_end
monthly_delta_series
positive_delta_sum
negative_delta_sum
max_monthly_positive_delta
max_monthly_negative_delta
number_of_negative_delta_months
number_of_zero_or_flat_months
one_way_score
is_monotone_enough
```

## Nonlinear / jumpy monthly deltas

The migration model may be piecewise or month-by-month.

Allowed:

```text
monthly deltas vary by month
step changes / jumps
piecewise constant rates
piecewise linear rates
monotone smoothing / isotonic regression
cluster-specific monotone share curves
```

Not required and not preferred:

```text
one global linear slope for all clusters
one constant monthly delta for all clusters
forcing smoothness if actual migration is jumpy
```

## Direction rule

Primary migration assumption:

```text
volume moves from residual into profiled/load-profile clusters
```

For the fitted historical correction, each cluster's cumulative allocation share should be non-decreasing unless there is strong evidence otherwise.

Negative monthly deltas are allowed only as:

```text
noise/measurement artefact
small correction after smoothing
explicitly documented exception
```

If a cluster's inferred allocation goes materially back and forth, P0055B must label that cluster's migration signal as not safely readable.

## Time-varying correction amount

The amount that must be redistributed before model training is not constant through time.

The historical correction should be largest near the start of the dataset:

```text
2022-06-01: maximum correction
```

and smallest near the holdout boundary/reference allocation:

```text
near 2025-06-01: minimal correction for primary forecast-safe train-fit reference
```

The method should effectively answer:

```text
If the near-holdout allocation had existed historically, how much load would need to be moved each earlier month from residual to each cluster?
```

## Forecast-safe reference allocation

For the primary P0055B result, use a reference allocation available before holdout, for example:

```text
latest stable allocation window inside train_fit
```

Do not use holdout/future shares to set the primary reference allocation.

Optional oracle/sensitivity may use latest full-history allocation, but must be clearly marked as non-production/oracle.

## Required evidence additions

P0055B must include:

```text
requirements/package-runs/P0055B/cluster-specific-migration-rates.md
requirements/package-runs/P0055B/monthly-delta-analysis.md
requirements/package-runs/P0055B/nonlinear-monotone-fit-review.md
requirements/package-runs/P0055B/reference-allocation-review.md
```

`monotonicity-review.md` must discuss per-cluster monotonicity, not only aggregate profiled/residual share.

## Review rule

When interpreting P0055B results:

```text
PASS is not credible if it only fits one global linear profiled share and ignores cluster-specific nonlinear migration.
```

WARN is acceptable if:

```text
- cluster-specific migration is noisy but documented
- monotone fit improves raw decomposition but direct SE3 still wins
- some clusters are too noisy and are left unadjusted
```

STOP is appropriate if:

```text
- the inferred allocation keys move back and forth so much that migration behavior cannot be read safely
- the method uses holdout/future shares for primary allocation
- normalized components cannot sum to SE3 total
```

## Relationship to main package

This clarification strengthens and amends:

```text
requirements/packages/P0055B-labb-se3-settlement-migration-normalized-decomposition.md
```

If there is any conflict, follow this clarification.
