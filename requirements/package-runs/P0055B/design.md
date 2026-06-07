# P0055B implementation design

## Package interpretation

P0055B tests whether raw decomposition failed because profiled/load-profile clusters and residual are affected by administrative settlement/product migration rather than stable physical load segmentation.

The primary result must be forecast-safe:

- monthly allocation/share model fit only on `train_fit`,
- reference allocation taken from the latest train-fit month,
- holdout monthly allocation estimated by train-fit extrapolation,
- no holdout share/reference fitting.

## Implementation structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0055b.py
tests/mac/services/spotprice_model_diagnostics/test_p0055b.py
```

Reuse P0055A for:

- direct target loading,
- P0054Z weather feature loading,
- component modeling rows,
- P0054R-style `HorizonBiasCorrected_WeightedEnsemble_no_price`,
- aggregation and total metrics where possible.

## Normalization model

1. Build aligned hourly decomposition rows over timestamps where direct SE3, all clusters and residual are available.
2. Compute observed hourly shares and monthly observed allocation shares.
3. Fit a simple linear monthly share model per component on train-fit months only.
4. Renormalize fitted monthly shares so each month sums to 1 across clusters + residual.
5. Use latest train-fit month as reference allocation.
6. For each hour, adjust observed component shares by `reference_share / smoothed_month_share`, then renormalize all adjusted shares to sum to 1.
7. Set normalized component MW to `SE3 total MW * normalized_share`.

This preserves:

```text
sum(normalized clusters) + normalized residual = SE3 total
```

## Intended outputs

Write local DB tables:

```text
se3_component_monthly_allocation_v1
se3_profiled_cluster_normalized_hourly_v1
se3_residual_normalized_hourly_v1
se3_normalized_decomposition_hourly_v1
```

Write compact package-run evidence, not full prediction dumps.

## Forecasting

Run the P0055A no-price model family on:

- direct SE3 total,
- non-zero normalized clusters,
- normalized residual.

Zero clusters stay zero. Normalized decomposition total is the sum of normalized component forecasts.

## Test strategy

Unit tests cover:

- monotonicity metrics and direction reversals,
- monthly share renormalization sums to 1,
- hourly normalization sums to SE3 total,
- leakage review rejects holdout-fitted references.

Verification commands:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0055b
PYTHONPYCACHEPREFIX=/private/tmp/p0055b-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0055b.py tests/mac/services/spotprice_model_diagnostics/test_p0055b.py
PYTHONPYCACHEPREFIX=/private/tmp/p0055b-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0055b
git diff --check
```

## Risks and uncertainties

- Share migration may not be monotonic enough to support the operator hypothesis.
- Linear monthly extrapolation is intentionally simple and may underfit real settlement changes.
- Realized weather remains LABB proxy weather, not a deployable forecast feed.
- Full model training is moderately expensive because normalized components are forecast separately.
