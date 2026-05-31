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
