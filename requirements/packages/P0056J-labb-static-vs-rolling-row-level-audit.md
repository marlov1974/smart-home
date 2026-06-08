# Package P0056J: LABB static vs rolling row-level audit

## Status

completed - WARN

## Package order

P0056J

## Label

```text
LABB
```

## Purpose

Audit why the old static holdout evaluation still outperforms the newer rolling/origin evaluations even after testing:

```text
P0056G weekly walk-forward
P0056H 36h lag protocol
P0056H2 static-style lag comparison
P0056I train-window sensitivity
```

The package must compare the old static pipeline and the rolling/origin pipeline row by row, using the same target timestamps and horizon rows where possible.

The goal is to stop guessing and locate the exact source of the metric gap.

## Primary area

Start with:

```text
SE2
```

SE2 is the main northern-area problem and has already been tested in P0056I.

Optional controls if the SE2 audit is small enough:

```text
SE3
FI
```

## Baseline facts to explain

Known SE2 results:

```text
P0056F W12 static full36 baseline: 197.547 MW
P0056H L2 recursive 36h: 242.579 MW
P0056H2 static-style lag comparison: 228.549 MW
P0056I TWX expanding 3.X: 228.549 MW
P0056G weekly: 207.757 MW
```

The audit must explain why static-style / rolling-origin results do not recover the static full36 baseline.

## Required audit design

Select a compact but representative sample of origins from P0056H2/P0056I:

```text
at least 10 origins
include multiple weekdays
include multiple months/seasons
include both high-error and low-error origins
include at least one late-period origin
```

For every selected origin, compare rows for:

```text
forecast_origin_local
forecast_origin_utc
target_timestamp_utc
horizon_h
actual_consumption_mw
static_pipeline_prediction_mw if available/reproducible
rolling_pipeline_prediction_mw
prediction_delta_mw
absolute_error_static
absolute_error_rolling
error_delta
```

If static predictions are not persisted, recreate the old static pipeline for the exact same rows or document why it cannot be recreated.

## Required row-level feature comparison

For every compared row, diff the feature values used by both pipelines.

At minimum compare:

```text
horizon_h
target_model_cet_hour
target_model_cet_weekday
target_model_cet_day_of_year
target_month
holiday flags
area_consumption_lag_1h
area_consumption_lag_2h
area_consumption_lag_3h
area_consumption_lag_6h
area_consumption_lag_12h
area_consumption_lag_24h
area_consumption_lag_48h
area_consumption_lag_72h
area_consumption_lag_168h
rolling load features
ramp features
weather features
temperature/heating degree features
normal temperature / delta features
cold spell flag
```

For every feature, report:

```text
rows_compared
exact_match_count
mismatch_count
max_abs_delta
mean_abs_delta
example_mismatches
```

## Required training and model comparison

For the same sample, compare:

```text
train_start
train_end
train_row_count
validation_start
validation_end
validation_row_count
model_name
model_family
hyperparameters if available
ensemble weights if available
horizon-bias correction values
feature_count
feature_order / column order
missing-value handling
```

If exact model artifacts are not persisted, document what can be reconstructed and what cannot.

## Required target/horizon alignment audit

Verify whether the static and rolling evaluations use the same target rows.

Report:

```text
row_count_static
row_count_rolling
intersection_row_count
static_only_rows
rolling_only_rows
horizon_distribution_static
horizon_distribution_rolling
local-hour_distribution_static
local-hour_distribution_rolling
weekday_distribution_static
weekday_distribution_rolling
month_distribution_static
month_distribution_rolling
```

This is critical because the old static metric may not be evaluating the same horizon mix as rolling 36h.

## Required metric reconstruction

Recompute metrics on the exact row intersection only:

```text
static_MAE_on_intersection
rolling_MAE_on_intersection
delta_on_intersection
```

Then compare with original metrics:

```text
static_original_MAE
rolling_original_MAE
static_intersection_delta_vs_original
rolling_intersection_delta_vs_original
```

If the gap disappears on the intersection, the issue is row selection/horizon distribution.

If the gap remains, the issue is feature/model construction.

## Required hypotheses to test

P0056J must explicitly test these possible causes:

```text
H1: static and rolling evaluate different target rows / horizon mix
H2: static and rolling use different lag-feature construction
H3: static and rolling use different weather-feature construction
H4: static and rolling use different horizon-bias correction
H5: static and rolling use different train/validation windows
H6: static metric is row-wise holdout prediction, not origin-realistic forecast
H7: rolling pipeline has a target/horizon alignment bug
H8: rolling feature column order or missing handling differs
```

For each hypothesis, conclude:

```text
supported / rejected / inconclusive
```

## Required evidence files

Create:

```text
requirements/package-runs/P0056J/CHANGELOG.md
requirements/package-runs/P0056J/review.md
requirements/package-runs/P0056J/design.md
requirements/package-runs/P0056J/functions.md
requirements/package-runs/P0056J/labb-label.md
requirements/package-runs/P0056J/baseline-review.md
requirements/package-runs/P0056J/origin-sample.md
requirements/package-runs/P0056J/target-row-intersection.md
requirements/package-runs/P0056J/row-level-prediction-diff.md
requirements/package-runs/P0056J/feature-diff-summary.md
requirements/package-runs/P0056J/lag-feature-diff.md
requirements/package-runs/P0056J/weather-feature-diff.md
requirements/package-runs/P0056J/calendar-feature-diff.md
requirements/package-runs/P0056J/model-training-diff.md
requirements/package-runs/P0056J/horizon-bias-correction-diff.md
requirements/package-runs/P0056J/metric-reconstruction.md
requirements/package-runs/P0056J/hypothesis-review.md
requirements/package-runs/P0056J/interpretation.md
requirements/package-runs/P0056J/decision.md
requirements/package-runs/P0056J/what-we-learned.md
requirements/package-runs/P0056J/next-package-recommendation.md
```

Optional compact evidence:

```text
row-level-prediction-diff.csv
feature-diff-summary.csv
target-row-intersection.csv
hypothesis-review.json
metrics-summary.json
```

Do not commit full prediction dumps for all holdout rows. Keep evidence compact and sampled.

## Files to inspect

```text
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056F/feature-ablation-results.md
requirements/package-runs/P0056H/area-summary-results.md
requirements/package-runs/P0056H2/area-summary-results.md
requirements/package-runs/P0056I/window-summary-results.md
requirements/package-runs/P0056I/comparison-vs-baselines.md
requirements/package-runs/P0056E/feature-group-comparison.md
src/mac/** forecast/model/feature/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056J-labb-static-vs-rolling-row-level-audit.md
requirements/package-runs/P0056J/**
src/mac/** narrowly scoped audit/reconstruction code if needed
tests/mac/** narrowly scoped tests for row intersection, feature diff and horizon alignment if code is added
local DB/query views if repo owns them and only for P0056J audit outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No large full prediction dumps committed.
No changing existing forecast results to make metrics match.
```

## Pass / WARN / STOP

PASS requires:

```text
SE2 audit completed
row intersection computed
feature diff summary completed
metric reconstruction completed
hypotheses H1-H8 reviewed
clear root-cause or narrowed explanation produced
```

WARN is acceptable if:

```text
static predictions must be reconstructed rather than loaded
some exact model artifacts are unavailable
some hypotheses remain inconclusive but next diagnostic is clear
```

STOP if:

```text
static pipeline cannot be located or reconstructed at all
rolling pipeline rows cannot be mapped to target timestamps
feature columns cannot be compared
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
origins sampled
rows compared
intersection row count
static vs rolling MAE on row intersection
largest feature mismatches
which hypothesis explains the gap best
whether old static test is origin-realistic or row-wise
recommended next package
tests/commands run
files changed
confirmation no device/runtime/no large artifacts/no result rewriting
```

## Completion notes

Implemented as SE2-only LABB row-level audit.

Result summary:

```text
status = WARN
persisted_static_rows = 12240
persisted_rolling_rows = 2556
exact_origin_target_intersection_rows = 0
target_aligned_reconstructed_rows = 2556
sampled_origins = 12
sampled_row_diff_rows = 432
feature_pairs = 432
```

Key metric reconstruction:

```text
alignment_mode = target_timestamp_closest_static_horizon
static_MAE_on_aligned_intersection = 213.229 MW
rolling_MAE_on_aligned_intersection = 228.549 MW
rolling_minus_static_delta = 15.320 MW
static_original_MAE = 197.547 MW
rolling_original_MAE = 228.549 MW
```

Main finding:

```text
The persisted static and rolling evaluations have zero exact origin+target row intersection.
The old static metric is not the same 06:00 every-fifth-day origin-realistic 36h grid as P0056I.
When the static W12 method is reconstructed and aligned by target timestamp to P0056I TWX rows, static remains better by 15.320 MW, but it is worse than its original static metric by 15.682 MW.
```

Largest sampled feature mismatches:

```text
horizon_h mismatch on 432/432 sampled rows
area_consumption_lag_1h mismatch on 432/432 sampled rows, max_abs_delta 5235.000 MW
area_consumption_lag_2h mismatch on 432/432 sampled rows, max_abs_delta 4734.000 MW
area_consumption_lag_3h mismatch on 432/432 sampled rows, max_abs_delta 4909.500 MW
area_consumption_lag_6h mismatch on 432/432 sampled rows, max_abs_delta 5051.667 MW
weather actual features mostly match; train-normal and delta features differ because training/profile context differs.
```

Hypothesis review:

```text
H1 supported: static and rolling evaluate different target rows / horizon mix.
H2 supported in target-aligned audit: lag features differ because static and rolling are not on the same origin/horizon row.
H3 supported: weather normal/delta features differ by training/profile construction, though raw weather values match.
H4 supported: static W12 uses horizon-bias correction; P0056I TWX does not.
H5 supported: static uses global train/internal-validation/holdout; rolling uses per-origin train ending at forecast origin.
H6 supported: old static test is row-wise holdout/path evaluation, not the rolling-origin production-realistic grid.
H7 rejected: rolling rows map cleanly to targets; no target/horizon alignment bug was found in P0056I.
H8 inconclusive: exact model artifacts and full missing-value objects are not persisted.
```

Decision:

```text
The best explanation is combined row-selection/horizon-mix plus model-method/protocol differences.
The audit narrows the next diagnostic to an exact static weighted-ensemble+bias method rerun on the P0056I origin grid.
Recommended next package: P0056K.
```

No API, devices, runtime changes, production activation, result rewriting, spot price features, flow/exchange/A61/capacity features, old physical_balance target or large artifacts.
