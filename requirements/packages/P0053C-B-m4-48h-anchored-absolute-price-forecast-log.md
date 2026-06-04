# Package P0053C-B: M4 48h anchored absolute price forecast log

## Status

planned

## Package order

P0053C-B

## Primary area

G2 / Mac tooling / spotprice V2 / M4 price-shape forecast / 48h price-history anchoring / absolute SE1 price reconstruction / forecast-origin log / leakage-safe price features

## Decision summary

P0053C-A rebuilt M4 under the global forecast period policy and created a forecast-origin log:

```text
m4_price_shape_forecast_origin_log_p0053ca_v1
```

The log is leakage-safe but contains only:

```text
prediction_kind = shape_index
prediction_unit = centered_shape_index
```

It does not contain absolute prices.

Earlier project work tested the idea of reconstructing 168h absolute prices by combining:

```text
M4 168h relative shape/index
+ latest known 48h actual price history before forecast-origin
```

P0053C-B must rebuild that anchoring idea under the new global split policy and with explicit forecast-origin semantics.

P0053C-B must create a new leakage-safe forecast-origin log with anchored absolute SE1 price forecasts, if the 48h anchor method passes validation/holdout checks.

## Preconditions

P0053C-B may start only after P0053C and P0053C-A PASS evidence exists.

Required facts:

```text
- P0053C created global forecast period policy.
- P0053C-A rebuilt M4 under that policy.
- P0053C-A forecast-origin log exists locally.
- P0053C-A leakage review passed.
- P0053C-A log contains shape/index, not absolute price.
```

Required source tables:

```text
m4_price_shape_forecast_origin_log_p0053ca_v1
historical actual SE1 price source used by P0043/P0044/P0045/P0053C-A
```

P0053C-B must STOP if it cannot prove that the 48h anchor uses only prices strictly before each forecast origin.

## Scope

P0053C-B owns:

```text
1. Locate and document historical evidence/code for the earlier 48h anchoring test if available.
2. Define one or more forecast-safe 48h anchoring formulas.
3. Apply anchors to M4 SE1 shape-index forecast-origin rows.
4. Create 168h anchored absolute SE1 price forecasts for validation and holdout origins.
5. Select anchoring formula using only train/validation, never holdout.
6. Evaluate anchored absolute forecasts on validation and holdout.
7. Create a durable local forecast-origin log suitable for later consumption-response testing.
8. Recommend whether P0053B-A2 should retry SE1 consumption price-response with anchored absolute prices.
```

## Hard non-goals

P0053C-B must not:

```text
- retrain M4 unless needed only to regenerate missing P0053C-A inputs
- use future actual prices inside the 168h target window as anchor/scale/level
- select anchoring formula on holdout
- create production API
- deploy any forecast model
- use A61 capacity/utilization/bottleneck margin
- ingest continental price levels
- train SE3/SE3-SE1 production forecast models
- touch Shelly/Home Assistant/KVS/devices
- touch M5/M6/M7 runtime/device paths
```

Local Mac historical anchoring/evaluation is allowed.

## Global split policy

Use P0053C policy:

```text
forecast target rows start = 2022-06-01T00:00:00Z
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

Split boundary is based on `timestamp_utc`.

Validation may be used to choose anchoring formula. Holdout may only be used once for final reporting.

## Forecast-origin semantics

For every forecast row:

```text
forecast_origin_timestamp_utc = origin time when forecast is considered known
input_data_cutoff_utc <= forecast_origin_timestamp_utc
anchor_history_window = [forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)
target_timestamp_utc >= forecast_origin_timestamp_utc
target_timestamp_utc <= forecast_origin_timestamp_utc + 167h
```

P0053C-B must prove:

```text
anchor_price_timestamp_utc < forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
input_data_cutoff_utc <= forecast_origin_timestamp_utc
```

No target-window actual price may be used for anchoring.

## Anchoring formulas

P0053C-B must evaluate at least the following anchor candidates.

Let:

```text
shape[h] = M4 centered shape-index prediction for horizon h
hist48 = actual SE1 prices over [origin-48h, origin)
```

### A0 mean/std anchor

```text
level = mean(hist48)
scale = std(hist48)
pred_abs[h] = level + shape[h] * scale
```

### A1 median/MAD or IQR robust anchor

```text
level = median(hist48)
scale = robust_scale(hist48)  # MAD or IQR-derived, documented
pred_abs[h] = level + shape[h] * scale
```

### A2 last-24/last-48 blended level with robust scale

```text
level = 0.5 * mean(last24) + 0.5 * mean(hist48)
scale = robust_scale(hist48)
pred_abs[h] = level + shape[h] * scale
```

### A3 same-hour previous-day level adjustment

For target hour-of-day:

```text
level[h] = mean(actual prices from same model_cet_hour over previous 48h when available)
scale = robust_scale(hist48)
pred_abs[h] = level[h] + shape[h] * scale
```

### A4 validation-selected blend

Optional if kept simple and trained only on validation/train:

```text
pred_abs[h] = alpha * level_candidate + beta * shape[h] * scale_candidate
```

If A4 is used, coefficients must be fit only on train/validation and frozen before holdout.

## Output log schema

Create a local table, recommended:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
```

Required columns:

```text
forecast_run_id
source_shape_run_id
model_name
model_version
split_policy_version
anchor_method
anchor_level
anchor_scale
anchor_history_start_utc
anchor_history_end_utc
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hours
area = SE1
predicted_price
prediction_unit
prediction_kind = anchored_absolute_price
source_shape_value
created_at_utc
quality_flag
```

If any target row cannot be anchored due to insufficient history, set quality flag and exclude it from canonical metrics.

## Required feature readiness

P0053C-B must state whether the anchored log can support later G7 features:

```text
forecast_se1_price_target_hour
forecast_se1_price_rank_in_forecast_day
forecast_se1_price_rank_in_168h
forecast_se1_price_top4_forecast_day_flag
forecast_se1_price_top8_forecast_day_flag
forecast_se1_price_bottom4_forecast_day_flag
forecast_se1_price_relative_to_forecast_24h_mean
forecast_se1_price_relative_to_forecast_168h_mean
forecast_se1_price_daily_spread_forecast
forecast_se1_price_volatility_next_24h_forecast
```

All ranks/topN/relative features must be computed only from the forecast path available at origin.

## Evaluation

Evaluate anchored forecasts against actual SE1 prices for validation and holdout.

Required metrics by anchor method and split:

```text
MAE
RMSE
bias
median_absolute_error
p90_absolute_error
p95_absolute_error
sMAPE
correlation
spearman
```

Required 168h path metrics:

```text
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
MAE_full_168h
bias_full_168h
peak_hour_error
weekly_mean_error
```

Required rank/dispatch metrics:

```text
top4_day_precision
top8_day_precision
bottom4_day_precision
top20_168h_precision
bottom20_168h_precision
best8_168h_hit_rate
worst8_168h_hit_rate
```

Compare against baselines:

```text
B0 last48_mean_flat
B1 same_hour_previous_day
B2 same_hour_previous_week if available and forecast-safe
B3 train/validation hour-weekday profile
M4 shape-only rank metrics from P0053C-A
```

## Selection rule

Anchor method selection must be based only on validation metrics.

Required rule:

```text
select primary anchor by validation MAE_full_168h, with tie-breaker validation rank/top8 performance.
```

Holdout is report-only.

If validation-best anchor performs materially worse than simple baselines on holdout, classify anchored absolute log as `diagnostic_only_not_ready_for_G7_absolute_price`.

## Required evidence files

P0053C-B must create:

```text
requirements/package-runs/P0053C-B/CHANGELOG.md
requirements/package-runs/P0053C-B/review.md
requirements/package-runs/P0053C-B/design.md
requirements/package-runs/P0053C-B/functions.md
requirements/package-runs/P0053C-B/prior-48h-anchor-evidence.md
requirements/package-runs/P0053C-B/anchor-method-definitions.md
requirements/package-runs/P0053C-B/forecast-origin-contract.md
requirements/package-runs/P0053C-B/leakage-review.md
requirements/package-runs/P0053C-B/anchor-validation-results.md
requirements/package-runs/P0053C-B/anchor-holdout-results.md
requirements/package-runs/P0053C-B/baseline-comparison.md
requirements/package-runs/P0053C-B/selected-anchor.md
requirements/package-runs/P0053C-B/forecast-origin-log-output.md
requirements/package-runs/P0053C-B/g7-readiness-for-consumption-response.md
requirements/package-runs/P0053C-B/next-package-recommendation.md
requirements/package-runs/P0053C-B/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053C-B/anchor-metrics.json
requirements/package-runs/P0053C-B/forecast-origin-log-sample.csv
requirements/package-runs/P0053C-B/g7-feature-readiness.json
```

Do not commit large raw forecast dumps or model binaries. Prefer compact samples and local SQLite tables.

## Required answers

P0053C-B must explicitly answer:

```text
1. Was prior 48h anchoring evidence/code found? If yes, where?
2. Which M4 forecast-origin log was used as shape source?
3. Which historical SE1 price source was used for 48h anchoring?
4. How was leakage avoided?
5. Which anchor methods were evaluated?
6. Which anchor was selected on validation?
7. What are validation metrics for the selected anchor?
8. What are holdout metrics for the selected anchor?
9. Does the selected anchor beat simple price baselines?
10. Was a durable anchored absolute forecast-origin log created?
11. Does the log contain absolute SE1 price or only shape/index?
12. Is it ready for P0053B-A2 SE1 consumption price-response retry?
13. Confirm no production API, no devices, no A61 utilization, no future actual price leakage and no SE3 production model.
```

## Tests

Required automated tests:

```text
- input M4 shape log exists and has forecast_origin_timestamp_utc
- anchor history uses only timestamps < forecast_origin_timestamp_utc
- no target-window actual prices used for anchor level/scale
- forecast_origin_timestamp_utc <= target_timestamp_utc
- horizon_hours is non-negative and within expected 0..167 or 1..168 convention documented
- split policy uses 2022-06-01 and 2025-06-01 boundaries
- validation selection excludes holdout rows
- output log has all required schema fields
- prediction_kind = anchored_absolute_price for canonical output
- rank/topN features, if materialized, are computed from forecast path only
- no actual future price exported as feature
- no A61 utilization/margin created
- no API/device path touched
```

## Pass/fail interpretation

PASS requires:

```text
- 48h anchoring is implemented leakage-safely
- at least A0/A1/A2/A3 are evaluated
- anchor selection uses validation only
- holdout metrics are reported
- durable anchored absolute forecast-origin log is created
- G7 readiness decision is explicit
- forbidden API/device/A61/leakage work is not done
```

WARN is acceptable if:

```text
- anchored absolute forecast exists but does not beat simple baselines robustly
- log is suitable only for diagnostic G7 tests
- prior 48h anchor evidence cannot be found, but method is rebuilt and documented cleanly
- some forecast origins are skipped due to insufficient pre-origin price history
```

STOP if:

```text
- anchor cannot be computed without future price leakage
- M4 shape log is missing or lacks forecast-origin semantics
- historical SE1 price source is unavailable
- holdout is used for anchor selection
- Codex builds production/API/device work
- Codex uses A61 utilization or future actual prices as features
```

## Expected Codex output

- PASS/WARN/STOP status
- source M4 log and price history source
- leakage review result
- anchor methods and selected anchor
- validation/holdout metrics
- baseline comparison
- output log table name and row count
- G7 readiness recommendation
- tests run
- files changed
- confirmation of no API/device/A61/leakage work
- commit SHA after push

## Completion notes

To be filled after implementation.
