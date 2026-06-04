# Package P0053C: Global forecast period policy and rebuild

## Status

done

## Package order

P0053C

## Primary area

G2 / Mac tooling / spotprice V2 / forecast governance / chronological splits / market-regime cleanup / rebuild historical forecasts

## Decision summary

The spotprice/physical-forecast project needs a single global chronological policy before more forecasts are built.

New project rule:

```text
Use data from 2022-06-01 through 2025-05-31 for training/validation/model selection.
Use 2025-06-01 through latest available data as holdout.
Do not use data earlier than 2022-06-01 for forecast training/evaluation.
```

Rationale:

```text
- 2022-06 .. 2025-05 gives approximately three full years of post-crisis/post-invasion market-regime data for model development.
- 2025-06 .. latest gives approximately one full year of holdout for honest testing.
- Earlier history belongs to a materially different electricity market regime before the 2021-2022 energy volatility crisis and Russia's invasion of Ukraine.
- Mixing pre-2022-06 data into forecast training risks training on a regime that is not representative of the intended deployment period.
```

P0053C is a governance and rebuild package. It must update split contracts and rebuild/re-evaluate relevant forecast artifacts under the new period policy before more modeling packages proceed.

## Preconditions

P0053C may start after P0053B PASS and P0053B-A STOP evidence exists.

Relevant current facts:

```text
- P0043/P0044/P0045 used older split logic: train earliest..2024-12-31, validate 2025, holdout 2026.
- P0053B used train earliest..2024-12-31, validate 2025, holdout 2026 for SE1 consumption warmup.
- P0053B-A stopped because old price forecasts lacked forecast-origin provenance.
- P0053B showed SE1 consumption forecasting is feasible and forecast-safe, but its split policy must be rebuilt.
```

P0053C must not assume old P0043/P0044/P0045/P0053B metrics remain comparable after the policy change.

## Global period policy

Canonical project forecast period:

```text
forecast_modeling_start_utc = 2022-06-01T00:00:00Z
forecast_modeling_end_utc = latest_available_timestamp_utc
```

Canonical model-development period:

```text
model_development_start_utc = 2022-06-01T00:00:00Z
model_development_end_utc = 2025-05-31T23:00:00Z
```

Canonical holdout period:

```text
holdout_start_utc = 2025-06-01T00:00:00Z
holdout_end_utc = latest_available_timestamp_utc
```

Fixed-CET equivalents must also be documented using the existing rule:

```text
model_cet_timestamp = timestamp_utc + 1h all year
```

P0053C must decide and document whether boundary membership is based on `timestamp_utc` or `model_cet_timestamp`. Default:

```text
timestamp_utc is primary identity and split boundary.
model_cet_* fields are feature/calendar fields.
```

## Development split inside training period

Within 2022-06-01 .. 2025-05-31, P0053C must define a standard train/validation policy.

Default policy:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

Allowed alternative if a model requires rolling-origin validation:

```text
cross-validation origins inside 2022-06-01 .. 2025-05-31 only
holdout never touched for model selection
```

P0053C must make this policy reusable by later packages.

## Scope

P0053C owns:

```text
1. Create a canonical forecast period/split policy document in repo memory or requirements evidence.
2. Audit existing package evidence/code for old split assumptions.
3. Update requirements/package guidance so future packages use the new policy.
4. Rebuild or mark stale prior forecast metrics that used incompatible splits.
5. Rebuild P0053B SE1 consumption forecast warmup under the new policy.
6. Investigate whether P0043/P0044/P0045 price-shape forecast regeneration can be rerun under the new policy.
7. Define a leakage-safe synthetic price forecast log approach using the new holdout, but do not build it unless explicitly within this package scope and safe.
8. Recommend the next rebuild/modeling package order.
```

## Hard non-goals

P0053C must not:

```text
- build a production API
- deploy any forecast model
- call Shelly/Home Assistant/KVS/devices
- touch M5/M6/M7 runtime/device paths
- ingest continental price levels
- use A61 capacity/utilization/bottleneck margin
- use actual future prices as consumption features
- train SE3/SE3-SE1 production forecast models
- change physical device behavior
```

P0053C may run local Mac historical forecast rebuilds only.

## Required audit

P0053C must audit at least:

```text
requirements/package-runs/P0043/
requirements/package-runs/P0044/
requirements/package-runs/P0045/
requirements/package-runs/P0053B/
requirements/package-runs/P0053B-A/
requirements/packages/P0043*
requirements/packages/P0044*
requirements/packages/P0045*
requirements/packages/P0053B*
```

Find and report old assumptions:

```text
train earliest..2024-12-31
validate 2025
holdout 2026
any use of data before 2022-06-01
any metric that is no longer comparable
```

Create a stale-metrics classification:

```text
still_valid_under_new_policy
needs_rebuild_due_to_split_change
needs_rebuild_due_to_pre_2022_data
diagnostic_only_historical
obsolete_do_not_compare
```

## Dataset filtering

All rebuilt forecast datasets must apply:

```text
timestamp_utc >= 2022-06-01T00:00:00Z
```

for training/evaluation rows.

If a target requires context lags before 2022-06-01, lags may read pre-start history only as context if and only if:

```text
- target rows start at 2022-06-01 or later
- pre-start rows are not scored or used as training targets
- evidence labels this as context-only lag warmup
```

Example:

```text
consumption_se1_lag_168h for 2022-06-01 may need May 2022 values.
```

P0053C must document whether it allows context-only lag warmup. Default: allowed if no target leakage.

## Rebuild P0053B SE1 consumption

P0053C must rerun or specify a deterministic rerun of P0053B under the new split:

```text
train:      2022-06-01 .. 2024-12-31
validation: 2025-01-01 .. 2025-05-31
holdout:    2025-06-01 .. latest
```

Required outputs:

```text
- target coverage after 2022-06-01 filter
- baseline metrics under new split
- M4/M7 comparable metrics under new split
- 168h path metrics under new split
- percent error relative to target mean/median/p50/p90 volume
- comparison to old P0053B metrics labeled as non-apples-to-apples if relevant
```

P0053C must add relative error metrics that P0053B lacked:

```text
mean_actual_mw
median_actual_mw
p10_actual_mw
p90_actual_mw
MAE_percent_of_mean
MAE_percent_of_median
sMAPE
```

## Price forecast rebuild planning

P0053C must define the correct path for price forecast inputs used by later consumption tests.

Required concept:

```text
synthetic historical price forecast log
```

Minimum schema:

```text
forecast_run_id
model_name
model_version
train_start_utc
train_end_utc
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hours
area
predicted_price_or_index
prediction_unit
created_at_utc
split_policy_version
```

For the new holdout, acceptable first rebuild:

```text
train price model only on 2022-06-01 .. 2025-05-31
create predictions for 2025-06-01 .. latest
store them with forecast_origin/target timestamps
```

Better later rebuild:

```text
rolling/weekly origins where each origin trains or applies a model using only data before origin.
```

P0053C must not use old M1/M4 prediction artifacts as forecast-safe price features unless provenance and split safety are proven.

## Forecast policy artifact

P0053C must create a reusable policy file, recommended:

```text
memory/spotprice-forecast-period-policy.md
```

It must include:

```text
- canonical data start: 2022-06-01
- canonical holdout start: 2025-06-01
- why pre-2022-06 is excluded
- train/validation/holdout default split
- fixed-CET boundary rule
- context-only lag warmup rule
- forecast-origin requirement for using another forecast as feature
- stale metrics rule
```

If memory path conventions differ, use an appropriate repo memory/requirements location and document it.

## Required evidence files

P0053C must create:

```text
requirements/package-runs/P0053C/CHANGELOG.md
requirements/package-runs/P0053C/review.md
requirements/package-runs/P0053C/design.md
requirements/package-runs/P0053C/functions.md
requirements/package-runs/P0053C/global-period-policy.md
requirements/package-runs/P0053C/old-split-audit.md
requirements/package-runs/P0053C/stale-metrics-classification.md
requirements/package-runs/P0053C/dataset-filtering-and-lag-warmup.md
requirements/package-runs/P0053C/se1-consumption-rebuild-results.md
requirements/package-runs/P0053C/relative-error-metrics.md
requirements/package-runs/P0053C/price-forecast-log-rebuild-plan.md
requirements/package-runs/P0053C/next-package-recommendation.md
requirements/package-runs/P0053C/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0053C/stale-metrics-classification.json
requirements/package-runs/P0053C/se1-consumption-rebuild-metrics.json
requirements/package-runs/P0053C/relative-error-metrics.json
```

## Required answers

P0053C must explicitly answer:

```text
1. What is the canonical forecast-modeling period?
2. What is the canonical train/validation/holdout split?
3. Are split boundaries based on timestamp_utc or model_cet_timestamp?
4. Why is pre-2022-06 excluded?
5. Which old package metrics are stale under the new policy?
6. Was P0053B SE1 consumption rebuilt under the new policy?
7. What are the new SE1 consumption MAE/RMSE/bias/relative-error metrics?
8. Is SE1 consumption still forecast-ready after the rebuild?
9. Can old M1/M4 prediction artifacts be reused, or do we need a synthetic forecast log?
10. What is the next package: rebuild price forecast log, expand consumption to SE2-SE4, or rebuild AI-1/AI-2 price-shape models?
11. Confirm no production API, no devices, no A61 utilization, no future actual price leakage and no SE3 production model.
```

## Tests

Required automated tests:

```text
- split policy object/constants use 2022-06-01 and 2025-06-01 boundaries
- no target training/evaluation rows earlier than 2022-06-01
- holdout rows start at 2025-06-01
- validation rows end before 2025-06-01
- context-only lag warmup rows are not scored as targets
- chronological splits are non-overlapping
- P0053B rebuild feature generation has no future leakage
- relative error metrics are computed correctly
- old metrics are labeled stale where split-incompatible
- no actual future prices used as forecast features
- no A61 utilization/margin created
- no API/device path touched
```

## Pass/fail interpretation

PASS requires:

```text
- global period policy is created and documented
- old split assumptions are audited
- stale metrics classification exists
- P0053B SE1 consumption is rebuilt or a deterministic rebuild command is provided with evidence
- relative error metrics are added
- next package recommendation is explicit
- forbidden API/device/A61/leakage work is not done
```

WARN is acceptable if:

```text
- P0053B rebuild is specified but not fully rerun due to local runtime limits
- old package audit finds additional split assumptions requiring follow-up
- price forecast log rebuild must be a separate package
```

STOP if:

```text
- canonical split cannot be applied cleanly
- data after 2022-06-01 is insufficient for a target
- holdout is contaminated by model selection/training
- Codex builds production/API/device work
- Codex uses future actual price or A61 utilization
```

## Expected Codex output

- PASS/WARN/STOP status
- created policy file path
- canonical split summary
- old split audit summary
- stale metrics classification
- SE1 consumption rebuild metrics including percent-of-volume errors
- price forecast log rebuild recommendation
- next package recommendation
- tests run
- files changed
- confirmation of no API/device/A61/leakage work
- commit SHA after push

## Completion notes

Completed 2026-06-04 with status `PASS`.

Created canonical policy:

```text
memory/spotprice-forecast-period-policy.md
src/mac/services/spotprice_model_diagnostics/forecast_period_policy.py
```

Canonical split:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest
```

Boundary identity is `timestamp_utc`; fixed-CET fields are calendar/features.

P0053B SE1 consumption was rebuilt under the new policy:

```text
requirements/package-runs/P0053C/p0053b-rebuild/
```

Rebuild status `PASS`; best 1h forecast-safe model remains `M4_Ridge_G4_calendar_load_lags_weather` with holdout MAE `6.431734387224803` MW, `2.08%` of holdout mean and `2.20%` of holdout median.

Old P0043/P0044/P0045/P0053B metrics were classified as stale or diagnostic-only when split-incompatible. P0053B-A STOP evidence remains valid because it concerns missing price forecast-origin provenance.

No production API, deployable model artifact, device path, A61 utilization, future actual price feature, SE3 production model, Shelly, Home Assistant or KVS action was performed.
