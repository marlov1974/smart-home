# Package P0045: Combine AI-1 + AI-2 into 168h shape forecast

## Status

implemented-pass

## Package order

P0045

## Primary area

G2 / Mac tooling / spotprice V2 / seven-day index forecast / AI-1 + AI-2 combination / 168h shape forecast

## Decision summary

P0045 combines the trained new-track models into a 168-hour shape forecast:

```text
AI-1 = day-to-local-week shape/scale model
AI-2 = hour-to-day shape model
```

P0045 must produce and evaluate a pure 168h curve-shape forecast, not an anchored absolute-price API.

The goal is to test whether AI-1 daily shape/scale plus AI-2 intraday shape can reconstruct useful relative 168h price structure.

## Preconditions

P0045 may start only after P0042, P0043 and P0044 evidence exists.

Required facts:

```text
P0042:
  - corrected fixed-CET datasets exist
  - timestamp_utc remains primary truth
  - model_cet_date/hour calendar is used
  - area_diff scale issue is corrected

P0043:
  - AI-2 trained on corrected fixed-CET dataset
  - system_proxy_se1 AI-2 selected feature group = F4_full
  - area_diff_proxy_se3 AI-2 selected feature group = F2_time_calendar_weather_actual

P0044:
  - AI-1 trained on corrected fixed-CET dataset
  - target usage policy is known
  - weak area_diff scale targets are flagged for fallback
```

P0045 must STOP if it cannot find the corrected P0042 datasets or if it falls back to pre-P0042/P0041 targets.

## Target usage policy from P0044

P0045 must not blindly use every AI-1 target.

Default policy:

```text
system_proxy_se1:
  day_level_shape:       use AI-1
  log_day_scale_index:   use AI-1
  log_local_7d_scale:    use AI-1

area_diff_proxy_se3:
  day_level_shape:       use AI-1, but mark weak-confidence
  log_day_scale_index:   use fallback/baseline/API-anchor placeholder
  log_local_7d_scale:    use fallback/baseline/API-anchor placeholder
```

The fallback for weak scale targets must be deterministic and documented.

Recommended initial fallbacks:

```text
area_diff log_day_scale_index fallback = 0.0
  meaning normal day scale relative to local week

area_diff log_local_7d_scale fallback = train mean or P0044 best baseline
  prefer the P0044 baseline that beat AI-1 on holdout
```

Codex may test alternatives, but must document exact formulas and compare them.

## Scope

P0045 owns:

```text
1. Load/use P0043 AI-2 predictions or regenerate AI-2 predictions deterministically from stored configs.
2. Load/use P0044 AI-1 predictions or regenerate AI-1 predictions deterministically from stored configs.
3. Combine daily AI-1 components with hourly AI-2 components into 168h shape curves.
4. Evaluate pure shape/rank/top-bottom quality against actual historical shape targets.
5. Compare against baselines.
6. Recommend whether the combined shape is ready for P0046 anchored absolute-price evaluation.
```

P0045 must not build a production API.

## Forecast window definition

P0045 must evaluate rolling 168h windows on the fixed-CET model calendar.

Preferred forecast origins:

```text
model_cet_date D at model_cet_hour 00
horizon = D 00:00 .. D+6 23:00 fixed-CET model time
168 hourly rows
```

If the intended product later forecasts from Monday 06, P0045 may add a diagnostic Monday-06 variant, but the primary shape-combination test should first use clean fixed-CET 7-day windows.

P0045 must document all forecast origins and row counts.

## Combination math

For each target series and fixed-CET model day D:

AI-1 provides:

```text
day_level_shape[D]
log_day_scale_index[D]
log_local_7d_scale[D]
```

AI-2 provides for each hour H in D:

```text
hour_shape[H]
```

Convert scale predictions:

```text
local_7d_scale[D] = exp(log_local_7d_scale[D])
day_scale_index[D] = exp(log_day_scale_index[D])
day_scale[D] = local_7d_scale[D] * day_scale_index[D]
```

Then build hourly shape value:

```text
combined_shape_raw[H] =
  day_level_shape[D] * local_7d_scale[D]
  + hour_shape[H] * day_scale[D]
```

Because this is still a pure shape forecast, P0045 must normalize each 168h window:

```text
combined_shape_168h = combined_shape_raw - mean(combined_shape_raw over 168h)
```

This yields a centered shape curve that can later be scaled/anchored in P0046.

P0045 must also test a dimensionless alternative:

```text
combined_shape_dimensionless[H] = day_level_shape[D] + hour_shape[H] * day_scale_index[D]
then center over 168h
```

The selected combination formula must be justified by validation/holdout shape metrics.

## Actual target for evaluation

P0045 must construct actual comparable 168h shape targets from historical prices.

For each 168h window and target series:

```text
actual_shape_168h = actual_hour_price - mean(actual_hour_price over 168h)
```

For scaled diagnostics, also compute:

```text
actual_shape_168h_scaled = actual_shape_168h / robust_scale(actual prices over 168h)
```

Primary comparison should include both:

```text
centered unscaled shape
robust scaled shape
```

Do not use anchored absolute MAE as a primary P0045 metric.

## Recomposition policy

P0045 must evaluate separately:

```text
system_proxy_se1
area_diff_proxy_se3
```

Optional diagnostic recomposition:

```text
se3_shape = se1_shape + area_diff_shape
```

If recomposition is evaluated, keep it diagnostic. Do not make SE3 production forecast in P0045.

## Baselines

P0045 must compare against baselines.

Required baselines:

```text
B0_flat_168h:
  predict zero shape for all 168 hours

B1_AI2_only:
  use AI-2 hour_shape only, no AI-1 day level/scale

B2_AI1_day_only:
  use AI-1 daily components repeated across each day, no AI-2 intraday shape

B3_time_profile_168h:
  train-only fixed-CET weekday/hour profile over 168h

B4_P0043_AI2_with_actual_day_scale_or_oracle_diagnostic:
  diagnostic upper-bound only, may use actual day scale but must be labeled oracle/not deployable

B5_P0044_AI1_with_actual_hour_shape_or_oracle_diagnostic:
  diagnostic upper-bound only, may use actual hour shape but must be labeled oracle/not deployable
```

Oracle diagnostics must never be used as deployable model selection baselines.

## Evaluation metrics

Evaluate separately for:

```text
system_proxy_se1
area_diff_proxy_se3
optional diagnostic recomposed_se3
```

Primary shape metrics per 168h window:

```text
shape_MAE_centered
shape_RMSE_centered
shape_MAE_scaled
shape_RMSE_scaled
signed_bias_after_centering
```

Rank/dispatch metrics per 168h window:

```text
spearman_168h_mean
spearman_168h_median
top_10_percent_hit_rate
bottom_10_percent_hit_rate
top_20h_precision
bottom_20h_precision
best_8h_hit_rate
worst_8h_hit_rate
```

Daily allocation metrics inside each 168h window:

```text
day_mean_shape_MAE
day_rank_spearman
highest_day_hit_rate
lowest_day_hit_rate
```

Intraday metrics inside each model day:

```text
hour_within_day_spearman_mean
top_3h_daily_hit_rate
bottom_3h_daily_hit_rate
```

Subset diagnostics:

```text
normal_week_subset
holiday_week_subset
bridge_day_week_subset
summer_subset
winter_subset
high_solar_week_subset
low_wind_week_subset
high_wind_week_subset
high_temp_delta_week_subset
```

## Chronological evaluation

Use chronological holdout logic consistent with P0043/P0044:

```text
train artifacts/configs from train period
validation windows in 2025
holdout windows in 2026
```

P0045 must not train new AI models.

If any lightweight calibration/combination coefficient is learned, it must be trained only on train/validate as explicitly documented, and holdout must remain untouched. Preferred first version: no learned calibrator.

## Model artifact policy

P0045 should reuse P0043/P0044 model configs/artifacts or regeneration commands.

If model binaries were not committed, P0045 must provide a deterministic regeneration path.

Do not commit large binaries.

Do not create an API endpoint.

## Required evidence files

P0045 must create:

```text
requirements/package-runs/P0045/CHANGELOG.md
requirements/package-runs/P0045/review.md
requirements/package-runs/P0045/design.md
requirements/package-runs/P0045/functions.md
requirements/package-runs/P0045/dataset-contract.md
requirements/package-runs/P0045/model-input-contract.md
requirements/package-runs/P0045/target-usage-policy.md
requirements/package-runs/P0045/combination-formulas.md
requirements/package-runs/P0045/forecast-window-policy.md
requirements/package-runs/P0045/baselines.md
requirements/package-runs/P0045/shape-metrics-summary.md
requirements/package-runs/P0045/rank-and-top-bottom-results.md
requirements/package-runs/P0045/daily-allocation-results.md
requirements/package-runs/P0045/intraday-results.md
requirements/package-runs/P0045/subset-results.md
requirements/package-runs/P0045/best-worst-windows.md
requirements/package-runs/P0045/oracle-diagnostics.md
requirements/package-runs/P0045/next-anchoring-plan.md
requirements/package-runs/P0045/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0045/metrics-summary.json
requirements/package-runs/P0045/window-results.json
requirements/package-runs/P0045/best-worst-windows.json
```

## Required answers

P0045 must explicitly answer:

```text
1. Which P0043 AI-2 model/config/prediction source was used?
2. Which P0044 AI-1 model/config/prediction source was used?
3. Which AI-1 targets were used vs replaced by fallback?
4. What exact fallback was used for area_diff scale targets?
5. Which combination formula was selected?
6. Does AI-1 + AI-2 beat B0_flat_168h for SE1 on shape/rank metrics?
7. Does AI-1 + AI-2 beat AI2-only for SE1?
8. Does AI-1 + AI-2 beat AI1-only for SE1?
9. Does area_diff combined shape help or harm versus fallback/baselines?
10. Are daily allocation and intraday shape both contributing?
11. Which weeks/windows fail worst and why?
12. Is the combined shape ready for P0046 anchored absolute-price backtest?
13. Confirm no new AI training unless explicitly documented as non-model calibration.
14. Confirm no API, M5/M6/M7, Shelly/device, HA, KVS action.
```

## Tests

Required automated tests:

```text
- P0045 uses fixed-CET model calendar and timestamp_utc-backed data
- each evaluated 168h window has exactly 168 hourly rows per target series
- no pre-P0042 dataset/table/view is used
- AI-2 target/prediction is hour_shape, not absolute price
- AI-1 targets/predictions are day_level_shape, log_day_scale_index, log_local_7d_scale
- P0044 target usage policy is applied and weak area_diff scale targets are not blindly used
- exponentiated scale predictions are finite and positive
- combined 168h shapes are centered to mean zero
- validation/holdout windows do not leak future target prices into model inputs
- oracle diagnostics are labeled and excluded from deployable model selection
- no AI-1 or AI-2 retraining occurs unless explicitly documented as artifact regeneration
- no anchored absolute price API is produced
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- SE1 combined shape beats B0_flat_168h on scaled shape MAE and rank metrics.
- SE1 combined shape beats at least one of AI2-only or AI1-only on a primary metric, or clearly explains why one component dominates.
- Area_diff combination is evaluated with the P0044 fallback policy.
- No weak area_diff scale AI targets are forced into the deployable combination.
- No leakage or target misuse is found.
- Evidence recommends whether P0046 should proceed.
```

WARN is acceptable if:

```text
- SE1 works but area_diff remains weak.
- Combined model improves rank/top-bottom more than MAE.
- AI2-only dominates AI1+AI2 for intraday metrics but AI1 improves daily allocation.
- P0046 can proceed only for SE1 first.
```

STOP if:

```text
- P0042/P0043/P0044 corrected artifacts are not used.
- actual future prices leak into features.
- combined shape does not beat trivial SE1 baselines.
- scale predictions are unstable/non-finite.
- P0045 accidentally builds absolute forecast API or device integration.
```

## Non-goals

- No new AI-1 training.
- No new AI-2 training.
- No production forecast API.
- No anchored absolute forecast as primary result.
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
- P0043/P0044 artifact sources
- target usage policy applied
- fallback formulas used
- combination formulas tested
- selected formula
- SE1 metrics vs baselines
- area_diff metrics vs baselines
- optional recomposed SE3 diagnostic metrics
- best/worst windows
- oracle diagnostic summary
- recommendation for P0046
- tests run
- files changed
- no new AI training / no API / no device confirmation
- commit SHA after push

## Completion notes

Implemented in P0045 as a Mac-only diagnostic/backtest package.

Result: PASS.

Summary:

- Used corrected P0042 tables `ai1_day_to_local_week_training_targets_v2` and `ai2_hour_to_day_training_targets_v2`.
- Regenerated P0043 AI-2 and P0044 AI-1 predictions from train-period rows and stored selected feature groups because binary artifacts were not committed.
- Applied P0044 area_diff weak-target fallback policy:
  - `log_day_scale_index = 0.0`
  - `log_local_7d_scale = train mean`
- Evaluated rolling fixed-CET 168h windows:
  - validation windows: 365 per target series
  - holdout windows: 135 per target series
- Selected formula by validation among deployable combination formulas: `combined_scaled` for both `system_proxy_se1` and `area_diff_proxy_se3`.
- SE1 holdout selected scaled MAE: `0.568437`, B0 flat: `0.639685`, AI2-only: `1.604569`, AI1-only: `0.550570`, Spearman: `0.616628`.
- area_diff holdout selected scaled MAE: `1.250916`, B0 flat: `0.864943`, AI2-only: `2.515733`, AI1-only: `1.162986`, Spearman: `0.269905`.
- Recommendation: P0046 may proceed as anchored absolute-price backtest for SE1 first. area_diff should remain diagnostic or fallback-constrained pending review.
- No new AI hyperparameter search/training, production API, anchored absolute API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.

Evidence:

- `requirements/package-runs/P0045/component-attribution-summary.md`
- `requirements/package-runs/P0045/shape-metrics-summary.md`
- `requirements/package-runs/P0045/next-anchoring-plan.md`
