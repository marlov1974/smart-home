# P0036 review

## Consistency result

PASS.

P0036 is consistent with the repository state and with `requirements/package-runs/P0035/m4-failure-analysis.md`.

## Evidence read

- `requirements/packages/P0036-train-clean-m1-and-bounded-hgb-m4-correction.md`
- `requirements/package-runs/P0035/m4-failure-analysis.md`
- P0033/P0034/P0035 package-run evidence
- `src/mac/services/spotprice_ml_model/core.py`
- `tests/mac/services/spotprice_ml_model/test_core.py`
- `requirements/packages/ML-holdout-evidence-policy.md`

## Findings

- Current M4 implementation still uses `PolynomialFeatures(degree=2) + Ridge` as the primary path when scikit-learn is available.
- Current feature schema includes `days_since_start_scaled`, which P0036 identifies as the unsafe extrapolation path when squared by polynomial expansion.
- Current M4 target uses full-period M1 from `m3ab_normalized_prices`, not a strict train-only M1 baseline.
- Current `train_m4()` promotes active artifacts unconditionally after training.

## Safety scope

P0036 is Mac/local ML only. No Shelly, Home Assistant, KVS, device, M5, M6, M7 or API changes are in scope.
