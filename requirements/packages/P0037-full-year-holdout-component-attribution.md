# Package P0037: Full-year holdout component attribution

## Status

planned

## Package order

P0037

## Primary area

G2 / Mac tooling / spotprice V2 / model diagnostics / full-year holdout / component attribution

## Decision summary

P0037 is a diagnostic package. It must create a strict full-year holdout evaluation and attribute errors to model components:

```text
M1: calm normal price baseline
M3A: extraordinary-temperature delta
M3B: special-day / holiday / bridge-day delta
M4: residual ML trend/model component
```

The goal is to answer:

```text
Is the remaining error mainly caused by:
- holiday/special-day analysis?
- temperature analysis?
- M4 residual analysis/modeling?
- or baseline M1 leakage / unfair holdout setup?
```

P0037 must not build M5, M6/API or M7.

## Why this package exists

P0036 produced the first PASS M4 by using train-only M1 and bounded HGB. However, the holdout period was only the available 2026 partial period.

A partial-year holdout can overstate or understate component behavior because it has incomplete seasonality, incomplete holiday coverage and partial weather regimes.

P0037 must therefore add at least one strict full-year holdout.

## Required full-year holdout

Primary full-year holdout:

```text
holdout_year = 2025
holdout_start = 2025-01-01
holdout_end = 2025-12-31
```

Recommended strict split:

```text
train:    2022-05-30..2023-12-31
validate: 2024-01-01..2024-12-31
holdout:  2025-01-01..2025-12-31
```

This split keeps the full 2025 holdout untouched for model/baseline fitting and selection.

P0037 may also report secondary checks:

```text
partial latest holdout: 2026-01-01..latest
optional 2024 holdout if enough train data exists
```

But the primary conclusion must be based on a full-year holdout.

## Strict no-leakage policy

For the primary 2025 full-year holdout, every component must be fit without 2025 data unless explicitly labeled as non-strict diagnostic.

Strict mode must include:

```text
train-only M1 learned without 2025 rows
M2 normals evaluated for leakage risk and documented
M3A temperature delta fitted without 2025 rows
M3B special-day delta fitted without 2025 rows
M4 residual model fitted without 2025 rows
candidate/model selection using validation year 2024 only
```

If any component cannot be recomputed in strict no-leakage mode, P0037 must say so and label the corresponding result WARN/diagnostic-only.

## Required evaluation targets

P0037 must report at least two target modes.

### Mode A: M3AB-normalized structural target

Purpose:

```text
Evaluate M1 + M4 after removing observed temperature and special-day effects.
```

Target:

```text
actual - observed_M3A - observed_M3B
```

Prediction variants:

```text
M1
M1 + M4
```

This isolates M4 residual/trend quality.

### Mode B: observed-reconstruction target

Purpose:

```text
Attribute component contribution against actual observed price using observed M3A/M3B deltas.
```

Target:

```text
actual
```

Prediction variants:

```text
M1
M1 + M3A
M1 + M3B
M1 + M3A + M3B
M1 + M4
M1 + M3A + M4
M1 + M3B + M4
M1 + M3A + M3B + M4
```

Because M5 forecast-time temperature model is not built yet, P0037 may use observed M3A temperature deltas only as diagnostic attribution, not as a deployable forecast claim.

## Component attribution matrix

P0037 must create an ablation matrix with exact deltas.

Required columns:

```text
holdout_year
target_mode
variant
target
MAE
RMSE
MAE_delta_vs_M1
RMSE_delta_vs_M1
MAE_delta_vs_previous_variant
winner_or_status
```

Required targets:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

Required variants:

```text
M1
M1+M3A
M1+M3B
M1+M3A+M3B
M1+M4
M1+M3A+M4
M1+M3B+M4
M1+M3A+M3B+M4
```

P0037 must explicitly say whether each component helps or hurts:

```text
M3A helps/hurts on full-year holdout, by target and subset.
M3B helps/hurts on full-year holdout, by target and subset.
M4 helps/hurts on full-year holdout, by target and subset.
```

## Subset attribution

P0037 must report component metrics for important subsets.

Required subsets:

```text
all_hours
special_day_hours
non_special_day_hours
fixed_public_holiday
movable_public_holiday
major_social_holiday
bridge_day_strong
bridge_day_weak
holiday_period_day
normal_weekday
normal_saturday
normal_sunday
```

Temperature subsets:

```text
extreme_cold
cold
normal_temperature
warm
extreme_warm
```

If available from M3A buckets, use exact M3A bucket labels. Otherwise define documented quantile/bucket thresholds from M2 anomaly.

Combined diagnostic subsets:

```text
special_day AND extreme_cold/cold
non_special_day AND extreme_cold/cold
normal_weekday AND extreme_cold/cold
```

## Required diagnostic questions

P0037 must answer these explicitly in `component-attribution-summary.md`:

```text
1. Does M3A improve full-year observed reconstruction versus M1?
2. Does M3A reduce temperature-correlated residuals?
3. Does M3A overcorrect or undercorrect extreme cold/warm periods?
4. Does M3B improve special-day hours versus M1?
5. Does M3B hurt non-special-day hours?
6. Does M4 improve the M3AB-normalized structural target versus train-only M1?
7. Does M4 improve recomposed SE3 over a full-year holdout?
8. Which component is most responsible for remaining large errors?
9. Are errors concentrated in temperature extremes, special days, area_diff spikes, SE1 level shifts, or M4 residual behavior?
10. Is the prior P0036 PASS still valid under a full-year holdout?
```

## M1 fairness and leakage report

P0037 must include a dedicated M1 baseline report.

Compare:

```text
full_period_M1_existing
train_only_M1_for_2025_holdout
train_only_M1_m3ab_normalized_for_2025_holdout
```

Report leakage effect:

```text
full_period_M1 MAE - train_only_M1 MAE
```

If full-period M1 wins materially due to leakage, mark it as production-reference only, not strict holdout baseline.

## M3A temperature diagnostics

For M3A, report:

```text
before_M3A_residual_vs_temperature_anomaly_corr
after_M3A_residual_vs_temperature_anomaly_corr
MAE by temperature bucket before/after M3A
mean signed error by temperature bucket before/after M3A
largest 20 M3A-related errors
```

M3A is suspect if:

```text
- residual temperature correlation does not decrease
- extreme cold/warm MAE worsens materially
- signed error shows systematic overcorrection or undercorrection
```

## M3B holiday diagnostics

For M3B, report:

```text
MAE by special_day_type before/after M3B
mean signed error by special_day_type before/after M3B
sample_count and shrinkage per special_day bucket
largest 20 special-day errors
```

M3B is suspect if:

```text
- it does not improve special-day hours
- it creates errors on bridge days or major social holidays
- shrinkage/caps erase real effects
- deltas have wrong sign for major holidays
```

## M4 residual diagnostics

For M4, report:

```text
M4 structural-target MAE vs train-only M1
M4 observed-reconstruction MAE when added to M1+M3A+M3B
predicted residual distribution vs actual residual distribution
largest 20 M4-worsened rows
largest 20 M4-improved rows
feature importance or equivalent if available
```

M4 is suspect if:

```text
- it worsens M3AB-normalized target
- it improves area_diff but worsens SE1 enough to hurt recomposed SE3
- residual predictions collapse to a constant that does not help full-year behavior
- residuals correlate with temperature or special-day effects, indicating M3A/M3B leakage into M4
```

## Evidence files

P0037 must create:

```text
requirements/package-runs/P0037/CHANGELOG.md
requirements/package-runs/P0037/review.md
requirements/package-runs/P0037/design.md
requirements/package-runs/P0037/functions.md
requirements/package-runs/P0037/full-year-holdout-summary.md
requirements/package-runs/P0037/component-attribution-matrix.md
requirements/package-runs/P0037/m1-leakage-report.md
requirements/package-runs/P0037/m3a-temperature-attribution.md
requirements/package-runs/P0037/m3b-special-day-attribution.md
requirements/package-runs/P0037/m4-residual-attribution.md
requirements/package-runs/P0037/component-attribution-summary.md
```

Machine-readable summaries may also be added:

```text
requirements/package-runs/P0037/component-attribution-matrix.json
```

Do not commit large prediction dumps.

## Expected implementation areas

P0037 may add analysis-only code, for example:

```text
src/mac/services/spotprice_model_diagnostics/**
```

or extend:

```text
src/mac/services/spotprice_ml_model/analysis.py
```

Do not make broad production refactors unless needed for the diagnostic.

## Tests

Required tests:

```text
- full-year 2025 holdout has 8760 rows
- 2025 holdout rows are not used when fitting strict train-only components
- ablation variants are computed from the same row set
- recomposed SE3 = SE1 + area_diff for every variant
- component-attribution matrix contains all required variants and targets
- special-day subset metrics are computed
- temperature bucket subset metrics are computed
- no M5/M6/M7/API/device code path is touched
```

## Non-goals

- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.
- No wind/solar M3C/M3D implementation.
- No production model promotion unless explicitly justified by diagnostic result and already covered by safe promotion policy.

## Expected Codex output

- full-year holdout split used
- row counts
- strict/no-leakage status
- component attribution matrix
- answer: M3A helps/hurts and where
- answer: M3B helps/hurts and where
- answer: M4 helps/hurts and where
- answer: which component is currently most suspect
- answer: whether P0036 PASS remains valid under full-year holdout
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
