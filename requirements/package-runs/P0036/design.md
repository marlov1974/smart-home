# P0036 design

## Package interpretation

P0036 corrects P0035 M4 by making the fair path use train-only M1 baselines and bounded `HistGradientBoostingRegressor` residual models.

The package must keep P0035's M3A/M3B normalized target foundation and must not build forecast-time M5/M6/M7 behavior.

## Implementation structure

- Extend the M4 feature build to load raw M3AB rows and compute train-only M1-like surfaces from training rows only.
- Store both compatibility full-period M1 baselines and train-only M1 variants in the model feature matrix.
- Train M4 residuals against `train_only_M1_m3ab_normalized`.
- Replace the primary estimator with bounded `HistGradientBoostingRegressor`.
- Keep Ridge only as pure fallback/diagnostic logic where needed by tests, not as the selected primary M4 model.
- Add quality-gated promotion: write staging artifacts and promote active only on PASS.
- Write P0036 holdout evidence files from the evaluated local training run.

## Feature design

Allowed HGB feature schema:

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
train_year_index_clipped
```

`train_year_index_clipped` is clipped to observed training years. Validate/holdout rows cannot extrapolate beyond the training maximum.

No polynomial expansion, `days_since_start_scaled`, squared time, raw weather, raw temperature, future price or leaky rolling feature is used.

## Train-only M1

P0036 uses the same bucket family as M1:

```text
iso_week +/- 2, same weekday, same local_hour, robust median
fallback: same local_hour median
```

The fitted buckets use only `split == train` rows. Predictions are then applied to train, validate and holdout.

Two train-only surfaces are computed:

```text
train_only_M1_raw_actual
train_only_M1_m3ab_normalized
```

The M4 residual target uses `train_only_M1_m3ab_normalized`.

## Model selection

Bounded HGB candidates are evaluated separately for:

```text
system_proxy_se1
area_diff_proxy_se3
```

The grid is deliberately compact for Codex/runtime safety and records wall-clock timing:

```text
max_iter: 50, 100, 200
learning_rate: 0.03, 0.05
max_leaf_nodes: 7, 15
min_samples_leaf: 50, 100
l2_regularization: 0.0, 0.1
```

The selected candidate minimizes validate MAE, with holdout reported for evidence only.

## Quality gate

PASS requires recomposed SE3 holdout MAE to beat `train_only_M1_m3ab_normalized`, no target to catastrophically degrade, and no area residual blow-up.

WARN keeps active model unchanged unless explicitly promoted as research. P0036 will not promote a worse model silently.

## Test strategy

- Unit tests for train-only M1 leakage behavior.
- Unit tests for train-only validate/holdout predictions.
- Unit tests that M4 fair targets use train-only M1.
- Unit tests that feature schema forbids squared/unbounded time features.
- Unit tests that HGB trains on fixture data.
- Unit tests that failed/WARN promotion does not replace active.
- Existing end-to-end validation adjusted for P0036 evidence paths.

## Risks

- HGB may improve P0035 M4 but still fail to beat fair M1. That is a WARN outcome, not a production promotion.
- Local scikit-learn is required for the primary model. If unavailable, P0036 must STOP instead of falling back to Ridge as production M4.
