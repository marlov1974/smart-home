# P0034 attempts

## Attempt 1

Status: in progress

Plan:

1. Bootstrap and consistency review.
2. Implement pure-Python Ridge M4 because scikit-learn is unavailable.
3. Build local feature/model DB artifacts.
4. Train and backtest.
5. Update evidence, docs, tests, commit and push.

Result:

- Implemented deterministic pure-Python Ridge M4 because scikit-learn is unavailable.
- Built local feature matrix and model DB under `/Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4`.
- Trained separate `system_proxy_se1` and `area_diff_proxy_se3` models.
- Validated recomposed SE3 predictions.
- Backtest completed, including P0033 M1 baseline comparison.
- Residual risk: Ridge M4 is weaker than P0033 M1 on holdout, so P0034 is a reproducible foundation rather than a replacement-quality normal model.

Knowhow promotion: skipped. The scikit-learn absence is recorded in P0034 review/evidence; it is not yet a general project rule.

## Attempt 2

Status: completed

Plan:

1. Install scikit-learn in the Mac user Python environment.
2. Replace preferred M4 training path with a scikit-learn model while keeping pure-Python Ridge as fallback.
3. Rebuild M4 local artifacts and backtest.
4. Persist explicit P0033 and P0034 holdout metrics in repo evidence.

Result:

- Installed `scikit-learn 1.6.1` with `numpy 2.0.2`, `scipy 1.13.1`, `joblib 1.5.3`, and `threadpoolctl 3.6.0`.
- Tried `HistGradientBoostingRegressor`; stopped it because it did not complete within a practical rebuild window.
- Switched to deterministic `PolynomialFeatures(degree=2, include_bias=False) + Ridge(alpha=1.0, fit_intercept=True)`.
- Rebuilt local M4 artifacts under `/Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4`.
- Added `requirements/package-runs/P0034/holdout-results.md`.
- Added `requirements/package-runs/P0033/holdout-results.md` for the M1 baseline.
- Holdout result remains `WARN`: M4 uses scikit-learn but does not beat P0033 M1 on key hourly and level metrics.

Knowhow promotion: skipped. The durable rule came from `requirements/packages/ML-holdout-evidence-policy.md`; this attempt only applies it to P0033/P0034 evidence.
