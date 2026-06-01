# Package P0043: Train AI-2 hour-to-day shape model

## Status

planned

## Package order

P0043

## Primary area

G2 / Mac tooling / spotprice V2 / seven-day index forecast / AI-2 hour-to-day model / fixed-CET dataset

## Decision summary

P0043 trains the first model in the new seven-day index AI track:

```text
AI-2 = hour-to-day shape model
```

AI-2 answers:

```text
For this fixed-CET model hour, how expensive is the hour relative to its fixed-CET model day mean and day volatility?
```

Target:

```text
hour_shape = (hour_price - day_mean_price) / day_intraday_scale
```

P0043 must use the corrected P0042 datasets:

```text
calendar = fixed-CET model calendar
primary timestamp = timestamp_utc
model day = model_cet_date
```

P0043 trains AI-2 only. It must not train AI-1 and must not build the 7-day API or absolute-price anchoring.

## Preconditions

P0043 may start only after P0042 PASS evidence exists.

Required P0042 facts:

```text
- UTC remains primary storage/join truth.
- fixed-CET model calendar fields exist.
- AI-2 targets are built on model_cet_date.
- DST-caused skipped dates are removed.
- area_diff scale issue is corrected with target-series-specific floor/policy.
- corrected AI-2 dataset is ready for training.
```

P0043 must fail/STOP if it cannot find the corrected P0042 AI-2 dataset or if it falls back to the P0041 pre-correction dataset.

## Model scope

Train AI-2 separately for each target series:

```text
system_proxy_se1
area_diff_proxy_se3
```

Do not train a combined SE1+area_diff model in P0043.

Do not train recomposed SE3 directly in P0043.

Recomposition is deferred.

## Model class

Primary model class:

```text
HistGradientBoostingRegressor
```

or closest available scikit-learn gradient boosting tree ensemble.

If `HistGradientBoostingRegressor` is unavailable, Codex may use another scikit-learn tabular gradient boosting model, but must document why.

Do not use neural networks, transformers, LSTM, seq2seq, AutoML or external heavy dependencies in P0043.

## Target

Primary target:

```text
hour_shape
```

Do not train on absolute price.

Do not train on ratio diagnostic targets.

Do not train on future anchored absolute-price errors.

The target must be the corrected P0042 target:

```text
hour_shape from fixed-CET model day
with corrected area_diff scale policy
```

## Required input features

Use features from the corrected P0042 AI-2 dataset.

Required time/calendar features:

```text
model_cet_hour
model_cet_hour_sin
model_cet_hour_cos
model_cet_weekday
model_cet_weekday_sin if available
model_cet_weekday_cos if available
model_cet_day_of_year
model_cet_day_of_year_sin
model_cet_day_of_year_cos
```

Required special-day features based on `model_cet_date`:

```text
base_day_type
special_day_type
special_day_name
is_special_day
is_bridge_day
is_holiday_period
is_major_social_holiday
```

If one-hot encoding is required, implement deterministic encoding and document categories.

Required weather features:

```text
hourly_temperature_actual
hourly_temperature_normal
hourly_temperature_delta
hourly_temperature_delta_minus_day_mean_delta
hourly_temperature_rank_in_day

hourly_solar_actual
hourly_solar_normal
hourly_solar_delta
hourly_solar_delta_minus_day_mean_delta
hourly_solar_rank_in_day

hourly_wind_actual
hourly_wind_normal
hourly_wind_delta
hourly_wind_delta_minus_day_mean_delta
hourly_wind_rank_in_day
```

Use corrected P0042 M2 normals built on fixed-CET day/hour buckets.

Optional diagnostics/features if already available:

```text
stockholm_is_dst
stockholm_utc_offset_hours
stockholm_local_hour
is_dst_transition_day
```

These must not replace fixed-CET model fields.

## Feature groups to compare

P0043 must evaluate feature ablations, at least:

```text
F0_time_only:
  model_cet hour/day/year cyclic features

F1_time_plus_calendar:
  F0 + base/special-day features

F2_time_calendar_weather_actual:
  F1 + actual weather signals

F3_time_calendar_weather_delta:
  F1 + actual, normal and delta weather signals

F4_full:
  F3 + weather relative-to-day features and ranks
```

The selected model should be the simplest feature group that materially improves validation/holdout shape metrics, unless a more complex group clearly wins without overfitting.

## Training split

Use chronological splits. Do not shuffle time.

Recommended split based on available data:

```text
train:    earliest available .. 2024-12-31
validate: 2025-01-01 .. 2025-12-31
holdout:  2026-01-01 .. latest available complete fixed-CET model day
```

If 2026 data is too short for meaningful holdout, use:

```text
train:    earliest available .. 2024-06-30
validate: 2024-07-01 .. 2024-12-31
holdout:  2025-01-01 .. 2025-12-31
```

Codex must document the exact split chosen and why.

P0043 must ensure that no future target rows leak into training for validation/holdout.

## Baselines

P0043 must compare AI-2 against baselines.

Required baselines:

```text
B0_flat_day:
  predict hour_shape = 0 for every hour

B1_hour_of_day_mean:
  mean hour_shape by model_cet_hour from train only

B2_hour_weekday_mean:
  mean hour_shape by model_cet_weekday × model_cet_hour from train only

B3_hour_weekday_season_smooth:
  smoothed seasonal/hour profile from train only, if practical
```

Baselines must be fit on train data only for each split.

## Primary evaluation metrics

Evaluate separately for:

```text
system_proxy_se1
area_diff_proxy_se3
```

Primary metrics:

```text
hour_shape_MAE
hour_shape_RMSE
mean_signed_error
```

Rank/dispatch metrics per fixed-CET model day:

```text
daily_spearman_rank_mean
daily_spearman_rank_median
top_3h_hit_rate
bottom_3h_hit_rate
top_6h_precision
bottom_6h_precision
```

Shape stability diagnostics:

```text
p90_day_MAE
worst_20_days_by_MAE
best_20_days_by_MAE
special_day_subset_metrics
normal_day_subset_metrics
summer_subset_metrics
winter_subset_metrics
high_solar_subset_metrics
low_wind_subset_metrics
high_wind_subset_metrics
```

P0043 must not use anchored absolute MAE as a primary model selection metric.

## Pass/fail interpretation

P0043 PASS requires:

```text
- AI-2 beats B0_flat_day on hour_shape_MAE for SE1.
- AI-2 beats B1/B2 on at least one important rank or top/bottom metric for SE1, or explains why B1/B2 is already optimal.
- area_diff model is trainable and does not collapse due to scale artifacts.
- area_diff model beats B0_flat_day on at least one primary or rank metric, or P0043 clearly recommends fallback/diagnostic handling.
- no leakage.
- all evidence and tests are present.
```

WARN is acceptable if:

```text
- SE1 model is useful but area_diff remains weak.
- AI-2 improves rank/top-bottom metrics more than MAE.
- weather features help only specific subsets.
```

STOP if:

```text
- corrected P0042 dataset is not used.
- target leakage is detected.
- model does not beat trivial baselines on SE1.
- area_diff target scale artifacts reappear.
- absolute price target is used by mistake.
```

## Required outputs

P0043 may write small model artifacts if repository conventions allow, but must not commit large binary artifacts.

Preferred outputs:

```text
requirements/package-runs/P0043/model-config-ai2-se1.json
requirements/package-runs/P0043/model-config-ai2-area-diff.json
requirements/package-runs/P0043/feature-list-ai2.md
requirements/package-runs/P0043/metrics-summary.json
```

If trained model binaries are large, do not commit them. Instead document local artifact paths and regeneration command.

## Required evidence files

P0043 must create:

```text
requirements/package-runs/P0043/CHANGELOG.md
requirements/package-runs/P0043/review.md
requirements/package-runs/P0043/design.md
requirements/package-runs/P0043/functions.md
requirements/package-runs/P0043/dataset-contract.md
requirements/package-runs/P0043/training-split.md
requirements/package-runs/P0043/feature-groups.md
requirements/package-runs/P0043/baselines.md
requirements/package-runs/P0043/ai2-se1-results.md
requirements/package-runs/P0043/ai2-area-diff-results.md
requirements/package-runs/P0043/feature-ablation-results.md
requirements/package-runs/P0043/rank-and-top-bottom-results.md
requirements/package-runs/P0043/subset-results.md
requirements/package-runs/P0043/best-worst-days.md
requirements/package-runs/P0043/next-model-training-plan.md
requirements/package-runs/P0043/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0043/metrics-summary.json
requirements/package-runs/P0043/feature-ablation-results.json
requirements/package-runs/P0043/best-worst-days.json
```

## Required answers

P0043 must explicitly answer:

```text
1. Which exact P0042 corrected dataset/table/view was used?
2. What chronological split was used?
3. Which feature group won for SE1?
4. Which feature group won for area_diff?
5. Does AI-2 beat flat/hour/day baselines on SE1?
6. Does AI-2 beat flat/hour/day baselines on area_diff?
7. Do weather delta features improve over actual-only weather?
8. Do relative-to-day weather/rank features help?
9. Which hours/days/subsets remain difficult?
10. Is AI-2 ready for combination with future AI-1?
11. Should P0044 train AI-1 next, or should P0043 require another AI-2 correction first?
12. Confirm no AI-1 training, no M5/M6/M7/API/device actions.
```

## Tests

Required automated tests:

```text
- training uses P0042 corrected fixed-CET dataset, not P0041 dataset
- timestamp_utc is present and unique per target series
- model_cet_date/model_cet_hour are present
- AI-2 target is hour_shape, not absolute price or ratio diagnostic
- train/validate/holdout splits are chronological and non-overlapping
- validation/holdout target rows are not used in training baselines or model fit
- baselines are fit on train data only
- categorical encoding is deterministic
- model can train separately for SE1 and area_diff
- predictions are finite
- daily mean of predicted hour_shape is checked and optionally centered to zero per day
- no AI-1 training is performed
- no M5/M6/M7/API/device path is touched
```

## Prediction post-processing

AI-2 predicts hourly `hour_shape` values. Because the target is day-centered, predictions should be checked per fixed-CET model day:

```text
mean(predicted_hour_shape for model_cet_date) should be near 0
```

If raw predictions have non-zero daily mean, P0043 may apply deterministic day-centering:

```text
pred_hour_shape_centered = pred_hour_shape - mean(pred_hour_shape within model_cet_date)
```

If applied, report metrics both before and after centering and use centered predictions as the default for future combination.

## Non-goals

- No AI-1 day-to-local-week training.
- No combined 168-hour forecast.
- No anchored absolute forecast.
- No production forecast API.
- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No futures/forward ingestion.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No live device access.

## Expected Codex output

- PASS/WARN/STOP status
- corrected P0042 dataset used
- exact train/validate/holdout split
- model class and hyperparameters
- feature groups tested
- baseline comparison for SE1
- baseline comparison for area_diff
- rank/top-bottom results
- subset results
- best/worst days
- whether day-centering was applied
- recommendation for P0044
- tests run
- files changed
- no AI-1/M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

Implemented in package-run evidence under `requirements/package-runs/P0043/`.

Result: PASS. P0043 trained AI-2 diagnostics from `ai2_hour_to_day_training_targets_v2`, using chronological train/validate/holdout split, separate SE1 and area_diff targets, B0-B3 train-only baselines, F0-F4 feature groups, bounded `HistGradientBoostingRegressor`, and deterministic per-day prediction centering. No binary model artifacts were committed. No AI-1, M5/M6/M7/API/device, Shelly, Home Assistant or KVS action was performed.
