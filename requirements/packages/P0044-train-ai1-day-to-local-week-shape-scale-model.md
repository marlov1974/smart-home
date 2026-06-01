# Package P0044: Train AI-1 day-to-local-week shape/scale model

## Status

implemented-warn

## Package order

P0044

## Primary area

G2 / Mac tooling / spotprice V2 / seven-day index forecast / AI-1 day-to-local-week model / fixed-CET dataset

## Decision summary

P0044 trains the second model in the new seven-day index AI track:

```text
AI-1 = day-to-local-week shape/scale model
```

AI-1 answers, for each fixed-CET model date D:

```text
1. How expensive is day D relative to its local 7-day period D-2..D+4?
2. How volatile/stormy is day D relative to typical daily volatility in D-2..D+4?
3. How volatile/stormy is the local 7-day period itself?
```

P0044 must use the corrected P0042 fixed-CET dataset and must remain compatible with AI-2 from P0043.

P0044 trains AI-1 only. It must not retrain AI-2 except for loading P0043 metrics/artifact metadata as reference. It must not build the combined 168h forecast or the anchored absolute-price API.

## Preconditions

P0044 may start only after P0042 and P0043 PASS evidence exists.

Required P0042 facts:

```text
- timestamp_utc is primary storage/join truth.
- fixed-CET model calendar fields exist.
- AI-1 targets are built on model_cet_date.
- AI-1 local window is D-2..D+4 over model_cet_date.
- DST-caused skipped dates are removed.
- area_diff scale policy is corrected.
```

Required P0043 facts:

```text
- AI-2 is trained and evaluated on P0042 corrected fixed-CET dataset.
- SE1 AI-2 selected feature group: F4_full.
- area_diff AI-2 selected feature group: F2_time_calendar_weather_actual.
- AI-2 is ready for future combination with AI-1.
```

P0044 must STOP if it cannot find the corrected P0042 AI-1 dataset or if it falls back to the pre-correction P0041 dataset.

## Model scope

Train AI-1 separately for each target series:

```text
system_proxy_se1
area_diff_proxy_se3
```

Train target-specific models for each target:

```text
day_level_shape
log_day_scale_index
log_local_7d_scale
```

Conceptually this is one AI-1, but implementation should begin with separate target-specific models:

```text
2 target series × 3 targets = 6 fitted models
```

Do not train recomposed SE3 directly in P0044.

Do not train combined multi-output models unless Codex first implements the separate target-specific baseline and documents why multi-output is better.

## Model class

Primary model class:

```text
HistGradientBoostingRegressor
```

or closest available scikit-learn tabular gradient boosting tree ensemble.

Given that AI-1 has far fewer rows than AI-2, P0044 must strongly control model complexity.

Required complexity discipline:

```text
- small/max-limited tree depth or leaf count
- minimum samples per leaf tuned conservatively
- early stopping or validation-based selection if available
- no large hyperparameter search that overfits validation
```

Do not use neural networks, transformers, LSTM, seq2seq, AutoML or heavy external dependencies in P0044.

## Targets

Primary targets from corrected P0042 AI-1 dataset:

```text
day_level_shape =
  (day_mean_price - local_7d_mean_price) / local_7d_level_scale

log_day_scale_index =
  log(day_intraday_scale / local_7d_typical_day_scale)

log_local_7d_scale =
  log(local_7d_level_scale)
```

Do not train on absolute day price.

Do not train on ratio diagnostic targets.

Do not train on future anchored absolute-price errors.

The targets must be the corrected P0042 targets using:

```text
model_cet_date
D-2..D+4 local window
corrected area_diff scale policy
```

## Required input features

Use features from the corrected P0042 AI-1 dataset.

Required time/calendar features:

```text
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

Required daily weather features:

```text
daily_temperature_actual
daily_temperature_normal
daily_temperature_delta
daily_temperature_delta_minus_local_7d_mean_delta
daily_temperature_rank_in_local_7d

daily_solar_actual
daily_solar_normal
daily_solar_delta
daily_solar_delta_minus_local_7d_mean_delta
daily_solar_rank_in_local_7d

daily_wind_actual
daily_wind_normal
daily_wind_delta
daily_wind_delta_minus_local_7d_mean_delta
daily_wind_rank_in_local_7d
```

Use corrected P0042 M2 normals built on fixed-CET day/hour buckets.

Optional wind gradient features for area_diff if available:

```text
daily_wind_system_proxy
daily_wind_south_proxy
daily_wind_central_proxy
daily_wind_north_proxy
daily_wind_south_minus_north
daily_wind_central_minus_north
```

Optional diagnostics/features if already available:

```text
stockholm_is_dst
stockholm_utc_offset_hours
stockholm_local_date
is_dst_transition_day
```

These must not replace fixed-CET model fields.

## Feature groups to compare

P0044 must evaluate feature ablations, at least:

```text
F0_time_only:
  model_cet weekday/year cyclic features

F1_time_plus_calendar:
  F0 + base/special-day features

F2_time_calendar_weather_actual:
  F1 + actual daily weather signals

F3_time_calendar_weather_delta:
  F1 + actual, normal and delta daily weather signals

F4_full:
  F3 + weather relative-to-local-7d features and ranks

F5_area_diff_wind_gradient_optional:
  F4 + wind gradient features, only if fields exist
```

Select the simplest feature group that materially improves validation/holdout metrics, unless a more complex group clearly wins without overfitting.

The selected feature group may differ by:

```text
target_series
target_name
```

## Training split

Use chronological splits. Do not shuffle time.

Recommended split based on available P0042 dataset:

```text
train:    earliest available .. 2024-12-31
validate: 2025-01-01 .. 2025-12-31
holdout:  2026-01-01 .. latest available complete fixed-CET model date
```

If 2026 data is too short for one of the daily targets, document the issue and keep 2026 as holdout if possible. Do not silently change split without evidence.

Codex must document the exact split and row counts per target series and per target.

P0044 must ensure no future target rows leak into training for validation/holdout.

## Baselines

P0044 must compare each AI-1 target against baselines.

Required baselines for `day_level_shape`:

```text
B0_zero:
  predict 0

B1_weekday_mean:
  mean day_level_shape by model_cet_weekday from train only

B2_weekday_season_smooth:
  smoothed model_cet_weekday × season profile from train only, if practical

B3_special_day_mean:
  train-only special_day/base_day fallback mean, if practical
```

Required baselines for `log_day_scale_index`:

```text
B0_zero:
  predict 0 = normal daily volatility relative to local week

B1_weekday_mean:
  mean log_day_scale_index by model_cet_weekday from train only

B2_special_day_mean:
  special/base-day fallback mean from train only, if practical
```

Required baselines for `log_local_7d_scale`:

```text
B0_train_mean:
  train mean log_local_7d_scale

B1_season_smooth:
  smoothed day-of-year/season scale from train only

B2_weather_actual_or_delta_simple:
  simple train-only weather bucket or linear baseline if practical
```

Baselines must be fit on train data only for each split.

## Primary evaluation metrics

Evaluate separately for:

```text
system_proxy_se1
area_diff_proxy_se3
```

and separately for:

```text
day_level_shape
log_day_scale_index
log_local_7d_scale
```

Primary regression metrics:

```text
MAE
RMSE
mean_signed_error
```

For `day_level_shape`, also evaluate local-window ranking metrics:

```text
spearman_rank_within_local_7d_mean
spearman_rank_within_local_7d_median
highest_day_hit_rate
lowest_day_hit_rate
top_2_days_precision
bottom_2_days_precision
```

For `log_day_scale_index`, also evaluate volatility ranking within local 7d:

```text
highest_volatility_day_hit_rate
lowest_volatility_day_hit_rate
top_2_volatility_days_precision
```

For `log_local_7d_scale`, ranking within local 7d is not meaningful because it is a local-window-level target repeated/associated per center date. Evaluate as a scale prediction:

```text
MAE
RMSE
signed bias
correlation if meaningful
```

Subset diagnostics:

```text
special_day_subset_metrics
normal_day_subset_metrics
bridge_day_subset_metrics
holiday_period_subset_metrics
summer_subset_metrics
winter_subset_metrics
high_temp_delta_subset_metrics
low_temp_delta_subset_metrics
high_solar_subset_metrics
low_wind_subset_metrics
high_wind_subset_metrics
```

P0044 must not use anchored absolute MAE as a primary model selection metric.

## Special caution: local-window overlap

AI-1 rows overlap heavily because each center date uses D-2..D+4.

P0044 must document this and avoid interpreting adjacent-day validation as independent samples.

Chronological validation is still required, but evidence must note:

```text
AI-1 has overlapping local-window targets.
Metrics are useful for model selection but not independent iid sample estimates.
```

P0044 must also ensure no target leakage through features that include actual target prices from the local window. Weather and calendar features for the local window are allowed only if they are intended to be forecast-time-known or proxy forecast-known.

Do not include actual future spot prices as features.

## Pass/fail interpretation

P0044 PASS requires:

```text
- Corrected P0042 AI-1 dataset is used.
- All six target-specific models or justified baselines are trained/evaluated.
- SE1 day_level_shape beats B0_zero on MAE and improves at least one ranking/top-bottom day metric.
- SE1 log_day_scale_index beats B0_zero or a simple baseline on MAE, or P0044 explains why volatility is mostly noise.
- SE1 log_local_7d_scale beats train-mean baseline or P0044 recommends API/anchor-derived week-scale fallback.
- area_diff targets are trainable without scale artifacts reappearing.
- No leakage.
- Evidence and tests are present.
```

WARN is acceptable if:

```text
- SE1 day_level_shape is useful but scale targets are weak.
- area_diff is weaker than SE1 but trainable.
- weather features help only subsets.
- log_local_7d_scale appears better handled later by anchor/API logic rather than AI-1.
```

STOP if:

```text
- P0042 corrected dataset is not used.
- target leakage is detected.
- SE1 day_level_shape cannot beat trivial B0_zero.
- area_diff scale artifacts reappear.
- absolute price target is used by mistake.
```

## Required outputs

P0044 may write small model artifacts if repository conventions allow, but must not commit large binary artifacts.

Preferred outputs:

```text
requirements/package-runs/P0044/model-config-ai1-system-proxy-se1-day-level-shape.json
requirements/package-runs/P0044/model-config-ai1-system-proxy-se1-log-day-scale-index.json
requirements/package-runs/P0044/model-config-ai1-system-proxy-se1-log-local-7d-scale.json
requirements/package-runs/P0044/model-config-ai1-area-diff-day-level-shape.json
requirements/package-runs/P0044/model-config-ai1-area-diff-log-day-scale-index.json
requirements/package-runs/P0044/model-config-ai1-area-diff-log-local-7d-scale.json
requirements/package-runs/P0044/feature-list-ai1.md
requirements/package-runs/P0044/metrics-summary.json
```

If trained model binaries are large, do not commit them. Instead document local artifact paths and regeneration command.

## Required evidence files

P0044 must create:

```text
requirements/package-runs/P0044/CHANGELOG.md
requirements/package-runs/P0044/review.md
requirements/package-runs/P0044/design.md
requirements/package-runs/P0044/functions.md
requirements/package-runs/P0044/dataset-contract.md
requirements/package-runs/P0044/training-split.md
requirements/package-runs/P0044/feature-groups.md
requirements/package-runs/P0044/baselines.md
requirements/package-runs/P0044/ai1-se1-day-level-results.md
requirements/package-runs/P0044/ai1-se1-day-scale-results.md
requirements/package-runs/P0044/ai1-se1-local-7d-scale-results.md
requirements/package-runs/P0044/ai1-area-diff-day-level-results.md
requirements/package-runs/P0044/ai1-area-diff-day-scale-results.md
requirements/package-runs/P0044/ai1-area-diff-local-7d-scale-results.md
requirements/package-runs/P0044/feature-ablation-results.md
requirements/package-runs/P0044/rank-and-top-bottom-day-results.md
requirements/package-runs/P0044/subset-results.md
requirements/package-runs/P0044/best-worst-days.md
requirements/package-runs/P0044/overlap-and-leakage-notes.md
requirements/package-runs/P0044/next-combination-plan.md
requirements/package-runs/P0044/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0044/metrics-summary.json
requirements/package-runs/P0044/feature-ablation-results.json
requirements/package-runs/P0044/best-worst-days.json
```

## Required answers

P0044 must explicitly answer:

```text
1. Which exact P0042 corrected dataset/table/view was used?
2. What chronological split was used?
3. Which feature group won for each target_series × target_name?
4. Does AI-1 beat simple baselines for SE1 day_level_shape?
5. Does AI-1 beat simple baselines for SE1 log_day_scale_index?
6. Does AI-1 beat simple baselines for SE1 log_local_7d_scale?
7. Does AI-1 beat simple baselines for area_diff day_level_shape?
8. Does AI-1 beat simple baselines for area_diff log_day_scale_index?
9. Does AI-1 beat simple baselines for area_diff log_local_7d_scale?
10. Do weather delta features improve over actual-only weather?
11. Do relative-to-local-7d weather/rank features help?
12. Which targets should be used in P0045 combination?
13. Should any AI-1 target be replaced by baseline/API-anchor fallback?
14. Confirm no AI-2 retraining, no combined 168h forecast, no M5/M6/M7/API/device actions.
```

## Tests

Required automated tests:

```text
- training uses P0042 corrected fixed-CET AI-1 dataset, not P0041 dataset
- model_cet_date is present and used as AI-1 day axis
- AI-1 local window is D-2..D+4 over model_cet_date
- target columns are day_level_shape, log_day_scale_index and log_local_7d_scale
- absolute price and ratio diagnostics are not used as targets
- train/validate/holdout splits are chronological and non-overlapping
- validation/holdout target rows are not used in training baselines or model fit
- baselines are fit on train data only
- categorical encoding is deterministic
- model can train separately for SE1 and area_diff
- target-specific models can train separately for all three targets
- predictions are finite
- area_diff corrected scale policy is present and no P0041-scale artifact reappears
- no AI-2 retraining is performed
- no combined 168h forecast is produced
- no M5/M6/M7/API/device path is touched
```

## Prediction post-processing

AI-1 predicts daily/local-window shape and scale values.

For `day_level_shape`, P0044 must check the implied local-window centering behavior. Because predictions are made per center date and local windows overlap, do not force naive global centering.

P0044 may test deterministic centering within each evaluated D-2..D+4 window for diagnostics only:

```text
pred_day_level_shape_centered = pred - mean(pred over evaluated local window)
```

If applied, report before/after metrics. Do not make centering the default for future P0045 unless evidence clearly supports it.

For scale predictions:

```text
pred_day_scale_index = exp(pred_log_day_scale_index)
pred_local_7d_scale = exp(pred_log_local_7d_scale)
```

Check that exponentiated scale predictions are finite and positive.

## Non-goals

- No AI-2 hour-to-day retraining.
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
- baseline comparison for each target_series × target_name
- rank/top-bottom day results for day_level_shape
- volatility ranking results for log_day_scale_index
- subset results
- best/worst days
- whether any diagnostic centering was tested/applied
- recommendation for P0045 combination
- tests run
- files changed
- no AI-2 retraining / no combined forecast / no M5/M6/M7/API/device confirmation
- commit SHA after push

## Completion notes

Implemented in P0044 as a Mac-only AI-1 diagnostic/training package.

Result: WARN.

Summary:

- Used corrected P0042 table `ai1_day_to_local_week_training_targets_v2`.
- Split: train earliest..2024-12-31, validate 2025-01-01..2025-12-31, holdout 2026-01-01..2026-05-21.
- Trained and evaluated six bounded `HistGradientBoostingRegressor` diagnostics.
- SE1 selected F5 for all three AI-1 targets and beat the required B0/train-mean baselines on holdout.
- area_diff `day_level_shape` selected F5 and only slightly beat B0 on holdout.
- area_diff `log_day_scale_index` selected F0 but did not beat B0 on holdout.
- area_diff `log_local_7d_scale` selected F5 but did not beat train-mean baseline on holdout.
- P0045 should use AI-1 for SE1 targets, may use area_diff `day_level_shape` cautiously, and should prefer baseline/API-anchor fallback for area_diff scale targets until improved.
- No AI-2 retraining, combined 168h forecast, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.

Evidence:

- `requirements/package-runs/P0044/component-attribution-summary.md`
- `requirements/package-runs/P0044/metrics-summary.json`
- `requirements/package-runs/P0044/next-combination-plan.md`
