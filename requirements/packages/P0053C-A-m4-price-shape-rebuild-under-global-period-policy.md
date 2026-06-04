# Package P0053C-A: M4 price-shape rebuild under global period policy

## Status

done

## Package order

P0053C-A

## Primary area

G2 / Mac tooling / spotprice V2 / M4 price-shape forecast / global split policy / leakage-safe holdout / synthetic price forecast log

## Decision summary

P0053C establishes the new global forecast period policy:

```text
forecast target rows start: 2022-06-01T00:00:00Z
model development:          2022-06-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:                    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

M4 also needs to be rebuilt under this policy.

Old M4/P0043/P0044/P0045 metrics used older split logic:

```text
train earliest..2024-12-31
validate 2025
holdout 2026
```

Those metrics are no longer the canonical basis for future forecast work. M4 must be regenerated/re-evaluated with no forecast targets before 2022-06-01 and with 2025-06-01..latest as holdout.

This package is an explicit M4 rebuild addendum to P0053C.

## Preconditions

P0053C-A may start after P0053C has created or is concurrently creating the global forecast-period policy.

Required facts:

```text
- The project-wide split policy is 2022-06-01 start and 2025-06-01 holdout.
- P0043/P0044/P0045 old metrics are stale for canonical comparison.
- P0053B-A stopped because old price predictions lacked forecast-origin provenance.
```

P0053C-A must STOP if it cannot locate the M4/P0045 regeneration path or cannot enforce the new split safely.

## Scope

P0053C-A owns:

```text
1. Locate the current M4/P0045 price-shape forecast code, configs, datasets and local model SQLite artifacts.
2. Audit M4 assumptions against the global period policy.
3. Rebuild M4 under the new period policy.
4. Re-evaluate M4 on validation and holdout under the new policy.
5. Produce a leakage-safe synthetic price forecast log for holdout if M4 outputs can be generated without using holdout target actuals in training/model selection.
6. Mark old M4/P0045 metrics as stale and provide new canonical metrics.
7. Recommend whether the rebuilt M4 forecast log can be used as G7 price-forecast input for SE1 consumption response testing.
```

## Hard non-goals

P0053C-A must not:

```text
- build a production API
- deploy M4
- use holdout actual prices for model selection or feature generation
- use actual future prices as consumption forecast features
- train SE3/SE3-SE1 production forecast models
- ingest continental price levels
- use A61 capacity/utilization/bottleneck margin
- touch Shelly/Home Assistant/KVS/devices
- touch M5/M6/M7 runtime/device paths
```

Local Mac historical rebuilds and evaluation are allowed.

## M4 rebuild target

Rebuild the M4/P0045 combined price-shape forecast for at least:

```text
system_proxy_se1
area_diff_proxy_se3
optional diagnostic recomposed_se3 = system_proxy_se1 + area_diff_proxy_se3
```

The primary focus for later consumption-response work is SE1 price/shape forecast output.

M4 must still be treated as a price-shape forecast unless an existing, documented anchoring path is explicitly included. Do not silently convert shape to absolute price without documenting the anchor/scale source and leakage-safety.

## Canonical split

Use:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

No target training/evaluation rows before 2022-06-01.

If lags/context require pre-2022-06 rows, they may be used as context-only warmup if:

```text
- target rows start at 2022-06-01 or later
- context rows are not scored
- context rows are not used as target training rows
- evidence labels this explicitly
```

Split boundary is based on `timestamp_utc`. Fixed-CET fields remain calendar/model features.

## Leakage rules

M4 rebuild must prove:

```text
- no holdout target actual prices are used for training
- no holdout target actual prices are used for model selection
- no holdout target actual prices are used for scaling/anchoring unless labeled oracle diagnostic and excluded
- no actual future prices are stored as forecast features
```

Any oracle diagnostics must be clearly labeled and excluded from deployable/canonical metrics.

## Synthetic price forecast log

If M4 can generate holdout predictions safely, P0053C-A must create or design a durable forecast log table/file with:

```text
forecast_run_id
model_name = M4 or exact rebuilt M4 name
model_version
split_policy_version = 2022-06_to_2025-05_train_holdout_from_2025-06
train_start_utc
train_end_utc
validation_start_utc
validation_end_utc
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hours
area_or_target
predicted_price_or_index
prediction_unit
prediction_kind = shape/index/absolute/anchored_absolute
created_at_utc
quality_flag
```

For the first safe rebuild, acceptable forecast-origin semantics are:

```text
forecast_origin_timestamp_utc = 2025-06-01T00:00:00Z
input_data_cutoff_utc = 2025-05-31T23:00:00Z
train_end_utc = 2025-05-31T23:00:00Z
predictions cover 2025-06-01T00:00:00Z .. latest
```

Better but optional if runtime allows:

```text
rolling weekly forecast origins inside holdout, each using only data before origin.
```

If the output is only shape/index and not absolute SE1 price, the log must say so. P0053B-A may then use it only if the feature engineering is compatible with shape/index values.

## Required M4 outputs

P0053C-A must report:

```text
- datasets used
- rows after 2022-06-01 filter
- split row/window counts
- model/config regeneration path
- selected AI-1/AI-2 components or fallbacks
- M4 formula used
- validation metrics under new policy
- holdout metrics under new policy
- comparison to old P0045 metrics labeled non-apples-to-apples
- whether forecast-origin log was created
- whether the log is suitable for G7 price forecast features
```

Required metrics should include P0045-style shape/rank metrics where available:

```text
shape_MAE_centered
shape_RMSE_centered
shape_MAE_scaled
shape_RMSE_scaled
spearman_168h_mean
top_10_percent_hit_rate
bottom_10_percent_hit_rate
top_20h_precision
bottom_20h_precision
best_8h_hit_rate
worst_8h_hit_rate
```

If absolute/anchored outputs are available safely, also report:

```text
MAE
RMSE
bias
p90_absolute_error
p95_absolute_error
sMAPE
```

## Required evidence files

P0053C-A must create:

```text
requirements/package-runs/P0053C-A/CHANGELOG.md
requirements/package-runs/P0053C-A/review.md
requirements/package-runs/P0053C-A/design.md
requirements/package-runs/P0053C-A/functions.md
requirements/package-runs/P0053C-A/m4-source-and-regeneration-path.md
requirements/package-runs/P0053C-A/global-split-application.md
requirements/package-runs/P0053C-A/m4-rebuild-results.md
requirements/package-runs/P0053C-A/holdout-metrics.md
requirements/package-runs/P0053C-A/forecast-origin-log-contract.md
requirements/package-runs/P0053C-A/forecast-origin-log-output.md
requirements/package-runs/P0053C-A/leakage-review.md
requirements/package-runs/P0053C-A/stale-old-m4-metrics.md
requirements/package-runs/P0053C-A/g7-readiness-for-consumption-response.md
requirements/package-runs/P0053C-A/next-package-recommendation.md
requirements/package-runs/P0053C-A/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053C-A/m4-rebuild-metrics.json
requirements/package-runs/P0053C-A/forecast-origin-log-sample.csv
requirements/package-runs/P0053C-A/forecast-origin-log-contract.json
```

Do not commit large raw prediction dumps or model binaries unless existing repo policy allows it. Prefer compact evidence and local SQLite tables.

## Required answers

P0053C-A must explicitly answer:

```text
1. Which M4/P0045 code/config/artifact path was used?
2. Was M4 rebuilt with target rows starting at 2022-06-01?
3. Were train/validation/holdout boundaries applied exactly as required?
4. Which old M4 metrics are stale?
5. What are the new validation metrics?
6. What are the new holdout metrics from 2025-06-01 onward?
7. Did the rebuild create a forecast-origin log?
8. Does the forecast-origin log contain absolute price, shape/index, or both?
9. Can the rebuilt M4 log be used as G7 price forecast input for P0053B-A retry?
10. What is the next package: retry price-response test, expand consumption SE1-SE4, or rebuild AI-1/AI-2 lower-level models first?
11. Confirm no production API, no devices, no A61 utilization, no future actual price leakage and no SE3 production model.
```

## Tests

Required automated tests:

```text
- split policy uses 2022-06-01 and 2025-06-01 boundaries
- no target rows before 2022-06-01
- holdout rows start at 2025-06-01
- validation rows end before 2025-06-01
- chronological splits are non-overlapping
- M4 rebuild does not use holdout target actuals for training/model selection
- forecast-origin log has forecast_origin_timestamp_utc and target_timestamp_utc
- forecast_origin_timestamp_utc <= target_timestamp_utc
- input_data_cutoff_utc <= forecast_origin_timestamp_utc
- no actual future price columns are exported as forecast features
- old metrics are labeled stale where split-incompatible
- no A61 utilization/margin created
- no API/device path touched
```

## Pass/fail interpretation

PASS requires:

```text
- M4 is rebuilt or a deterministic rebuild is executed under the new policy
- holdout metrics from 2025-06-01 onward are reported
- old M4 metrics are marked stale
- leakage review passes
- forecast-origin log is created or a precise blocker is documented
- recommendation for P0053B-A retry is explicit
```

WARN is acceptable if:

```text
- M4 can be rebuilt but only shape/index forecast log is produced
- rolling weekly forecast origins are deferred
- absolute price anchoring is not safe yet
- forecast-origin log creation is specified but not fully populated due to runtime limits
```

STOP if:

```text
- M4 rebuild cannot enforce the new split
- holdout actual prices contaminate training/model selection
- forecast-origin semantics cannot be represented
- Codex builds production/API/device work
- Codex uses future actual price or A61 utilization
```

## Expected Codex output

- PASS/WARN/STOP status
- M4 source/regeneration path
- global split application summary
- M4 validation and holdout metrics
- old-metrics stale classification
- forecast-origin log status and schema
- G7 readiness recommendation
- tests run
- files changed
- confirmation of no API/device/A61/leakage work
- commit SHA after push

## Completion notes

Completed 2026-06-04 with status `PASS`.

Used regeneration path:

```text
src/mac/services/spotprice_model_diagnostics/p0053ca.py
src/mac/services/spotprice_model_diagnostics/p0043.py
src/mac/services/spotprice_model_diagnostics/p0044.py
src/mac/services/spotprice_model_diagnostics/p0045.py
```

P0053C-A reused the old P0043/P0044/P0045 model functions and selected feature policies where possible, but applied the P0053C global split policy. Scored AI-2 target rows start at `2022-06-01T00:00:00Z`; train/validation/holdout boundaries are canonical P0053C boundaries. 168h windows that crossed split boundaries were skipped.

Selected formula for both `system_proxy_se1` and `area_diff_proxy_se3`:

```text
combined_scaled
```

New holdout metrics from `2025-06-01` onward:

```text
system_proxy_se1: windows=348, shape_MAE_scaled=1.077082, shape_MAE_centered=0.164976, spearman_168h=0.612268
area_diff_proxy_se3: windows=348, shape_MAE_scaled=0.829498, shape_MAE_centered=0.193085, spearman_168h=0.344933
```

Created local forecast-origin log table:

```text
m4_price_shape_forecast_origin_log_p0053ca_v1
rows=116928
prediction_kind=shape_index
prediction_unit=centered_shape_index
```

The log is not an absolute price forecast. It is suitable for a P0053B-A retry only for shape/index rank, top/bottom and relative-shape features. Absolute price-response features require a later safe anchoring package.

Old P0043/P0044/P0045/M4 metrics are stale for canonical comparison under the P0053C policy.

No production API, deployable model, Shelly, Home Assistant, KVS, device, A61 utilization, future actual price feature or SE3 production model work was performed.
