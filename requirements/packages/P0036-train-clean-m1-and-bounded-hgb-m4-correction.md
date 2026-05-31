# Package P0036: Train-clean M1 and bounded HGB M4 correction

## Status

planned

## Package order

P0036

## Primary area

G2 / Mac tooling / spotprice V2 / M4 correction / holdout fairness / bounded gradient boosting

## Decision summary

P0036 is a correction package based on the P0035 M4 failure analysis.

P0035 analysis showed:

```text
1. The existing M1 holdout baseline is not strict out-of-sample because M1 was built from the full local period, including 2026 holdout.
2. Even a train-only M1-like baseline still beats P0035 M4.
3. The main P0035 M4 failure is polynomial Ridge extrapolation, especially for SE3-SE1 area_diff_proxy.
4. HistGradientBoostingRegressor with bounded settings does not hang and is much better than Ridge in quick controls.
5. M3A/M3B target formulas are broadly correct and are not the main cause of failure.
```

P0036 must therefore:

```text
- build strict train-only M1 baselines for fair holdout evaluation
- replace PolynomialFeatures + Ridge as the primary M4 model
- use bounded HistGradientBoostingRegressor as the primary M4 residual candidate
- forbid unsafe polynomial time extrapolation
- keep M3A/M3B as built in P0035
- produce honest holdout evidence against both train-only and full-period M1 baselines
```

P0036 must not build M5, M6/API or M7.

## Scope

P0036 owns:

```text
1. Strict train-only M1 baseline implementation/evidence for holdout fairness.
2. Corrected M4 residual feature/model design.
3. Bounded HGB residual training for SE1 and SE3-SE1.
4. Candidate comparison and timing evidence.
5. Safe active/staging model promotion only if quality gates pass.
```

P0036 must not change the fundamental P0035 data foundation unless an explicit bug is found:

```text
M2 smooth climate normals
M3A extraordinary-temperature deltas
M3B special-day deltas
M3AB normalized prices
Swedish special-day calendar
```

## Required inputs

Use existing local feature/model data:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
~/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3
```

Use P0035 evidence as required analysis input:

```text
requirements/package-runs/P0035/m4-failure-analysis.md
requirements/package-runs/P0035/holdout-results.md
requirements/package-runs/P0035/baseline-comparison.md
requirements/package-runs/P0035/m3a-temperature-summary.md
requirements/package-runs/P0035/m3b-special-day-summary.md
requirements/package-runs/P0035/m2-smoothing-summary.md
```

## Required split

Use the same fixed chronological split unless design explicitly justifies a better one:

```text
train:    2022-05-30..2024-12-31
validate: 2025-01-01..2025-12-31
holdout:  2026-01-01..latest available P0035 feature coverage
```

No random row split may be used as primary validation.

## Train-only M1 baseline

P0036 must implement a strict train-only M1 baseline for fair comparison.

Requirements:

```text
- build M1-like normal surfaces using only training-period rows
- apply those learned surfaces to validate and holdout
- do not let validate/holdout rows affect their own M1 baselines
- support both SE1 and SE3-SE1 area_diff targets
- support M3AB-normalized target baseline, not just raw actual baseline
```

Minimum required baseline variants:

```text
full_period_M1_existing
train_only_M1_raw_actual
train_only_M1_m3ab_normalized
```

The key fair baseline for P0036 M4 is:

```text
train_only_M1_m3ab_normalized
```

Evidence must show all baseline variants clearly.

## Corrected M4 target

Keep the P0035 residual target definition:

```text
M4 residual target SE1 = m3ab_normalized_price_se1 - M1_baseline_se1
M4 residual target area = m3ab_normalized_area_diff - M1_baseline_area_diff
```

For the fair training/evaluation path, use train-only M1 baseline consistently:

```text
M4_train_target = train_m3ab_normalized - train_only_M1_prediction_for_train
M4_validate_prediction = train_only_M1_prediction_for_validate + predicted_residual_validate
M4_holdout_prediction = train_only_M1_prediction_for_holdout + predicted_residual_holdout
```

P0036 may also report the same residual model against full-period M1 for compatibility, but it must not use that as the primary fairness claim.

## Forbidden model behavior

P0036 must eliminate the P0035 failure mode:

```text
PolynomialFeatures(degree=2) + days_since_start_scaled^2 extrapolation
```

Forbidden as primary M4 model:

```text
PolynomialFeatures(degree=2) + Ridge with unbounded time trend
any model using squared time/trend extrapolation as a primary long-run correction
raw days_since_start_scaled^2 feature
high-degree polynomial expansion of time
unbounded extrapolating trend features
```

Polynomial/Ridge may remain as a diagnostic fallback only, and must be labeled as such.

## Required model candidate: bounded HGB

Primary candidate:

```text
sklearn.ensemble.HistGradientBoostingRegressor
```

Required bounded search space:

```text
max_iter: 50, 100, 200, 300, optionally 500 if timing is safe
learning_rate: 0.02, 0.03, 0.05, 0.08
max_leaf_nodes: 7, 15, 31
min_samples_leaf: 50, 100, 200
l2_regularization: 0.0, 0.01, 0.1, 1.0
early_stopping: true where supported and appropriate
random_state: fixed where applicable
```

Codex may reduce the grid if runtime requires it, but must record what was tested and why.

Separate model selection must be allowed for:

```text
system_proxy_se1
area_diff_proxy_se3
```

The best SE1 candidate need not be the best area_diff candidate.

## Feature design

Allowed core features:

```text
hour_sin
hour_cos
weekday_sin
weekday_cos
day_of_year_sin
day_of_year_cos
iso_week_sin
iso_week_cos
month_sin
month_cos
is_weekend
week_of_month
special_day flags only if used carefully for diagnostics; M3B should already remove special-day deltas
```

Allowed slow trend features only if bounded/non-extrapolating:

```text
year_index as categorical or clipped numeric by observed train years
train-period year/regime group
piecewise/clipped trend that does not extrapolate parabolically
long smooth level features derived without leakage, if design proves they are train-only
```

Forbidden features:

```text
raw temperature
weather anomaly
wind/solar/cloud/radiation
future prices
raw actual price lags that leak horizon
squared days_since_start_scaled
unbounded polynomial time interactions
holdout-derived rolling features
```

If a trend feature is used, Codex must document why it cannot create the P0035 extrapolation failure.

## HGB timing and runtime policy

P0036 must record candidate wall-clock timings.

Required columns:

```text
candidate_id
target
parameters
train_rows
feature_count
start_time
end_time
elapsed_seconds
status
reason_selected_or_rejected
holdout_mae
holdout_rmse
```

Runtime policy:

```text
interactive smoke/test budget: 2-5 minutes per small candidate group
production training budget: up to 60 minutes
manual research budget: up to 24 hours if explicitly run outside Codex
```

Do not reject HGB merely because an unbounded/poorly controlled run was slow. The P0035 analysis showed bounded HGB runs completed in under one second for small candidates.

## Quality gates

P0036 must classify result as PASS/WARN/STOP.

PASS requires:

```text
- HGB residual model beats train_only_M1_m3ab_normalized on holdout for recomposed SE3 hourly MAE or a clearly justified primary metric
- no target has catastrophic degradation vs train_only_M1_m3ab_normalized
- area_diff residual prediction no longer shows massive positive holdout blow-up
- model artifacts are promoted atomically only after validation
- all holdout evidence is persisted in repo
```

WARN if:

```text
- HGB is reproducible and improves vs P0035 M4 but does not beat train-only M1
- metrics are mixed or only improve secondary curve/index metrics
- HGB is better for one target but not the other
```

STOP if:

```text
- fair train-only M1 cannot be computed
- HGB cannot be run with bounded settings
- leakage is detected in M4 features
- target/evaluation formulas are inconsistent
- model artifacts cannot be safely staged/promoted
```

## Model promotion policy

P0036 must use staging/active promotion.

Required behavior:

```text
- train into staging run directory
- validate and write holdout evidence
- promote to active only if quality gate allows
- if quality gate is WARN, either do not promote or promote only as research/non-production candidate, clearly labeled
- failed training must keep current active model intact
```

P0036 must not silently replace an active model with a worse candidate.

## Holdout evidence policy

P0036 must follow:

```text
requirements/packages/ML-holdout-evidence-policy.md
```

Required evidence files:

```text
requirements/package-runs/P0036/holdout-results.md
requirements/package-runs/P0036/baseline-comparison.md
requirements/package-runs/P0036/candidate-timings.md
requirements/package-runs/P0036/model-selection.md
requirements/package-runs/P0036/model-promotion-summary.md
```

Holdout must report at least:

```text
SE1 system_proxy hourly MAE/RMSE
SE3-SE1 area_diff hourly MAE/RMSE
recomposed SE3 hourly MAE/RMSE
special-day subset metrics
non-special-day subset metrics
area_diff residual predicted-vs-actual distribution
largest 20 holdout errors for SE1 and area_diff if result is WARN/STOP
```

Required baseline comparison:

```text
full_period_M1_existing
train_only_M1_raw_actual
train_only_M1_m3ab_normalized
P0034 M4 if available
P0035 M4 residual if available
P0036 HGB residual candidate
```

## Diagnostics required

P0036 must specifically verify the P0035 failure is removed:

```text
- predicted residual mean/min/p50/p95/max by split and target
- actual residual mean/min/p50/p95/max by split and target
- area_diff holdout predicted residual mean must not be a large positive constant around +2 when actual is near +0.13
- feature importance or permutation/diagnostic equivalent for HGB if practical
- no squared time feature in feature schema
```

## Expected implementation areas

Expected paths, final paths may differ if documented:

```text
src/mac/services/spotprice_ml_model/**
tests/mac/services/spotprice_ml_model/**
requirements/package-runs/P0036/**
docs/functions/mac/spotprice-ml-normal-model.md
```

P0036 may add analysis utilities if needed:

```text
src/mac/services/spotprice_ml_model/analysis.py
```

## Tests

Required tests:

```text
- train-only M1 baseline does not use validate/holdout rows
- train-only M1 can produce validate/holdout predictions
- M4 residual target uses train-only M1 in fair mode
- feature schema forbids squared/unbounded polynomial time features
- HGB candidate training runs on fixture data
- area_diff residual prediction does not use Polynomial Ridge primary path
- staging active promotion keeps active model on failed candidate
- holdout evidence writer includes train-only M1 metrics
```

## Non-goals

- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term forecast.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.
- No changes to P0035 special-day calendar unless a bug is found and documented.
- No wind/solar M3C/M3D implementation.

## Expected Codex output

- PASS/WARN/STOP result
- train-only M1 method and metrics
- HGB candidate grid actually tested
- candidate timings
- selected model parameters per target
- holdout comparison table
- area_diff blow-up diagnostic result
- promotion decision and active/staging paths
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
