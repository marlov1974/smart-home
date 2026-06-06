# Package P0054V2: LABB complete spotprice value test with relaxed baseline gate

## Status

completed

## Package order

P0054V2

## Label

```text
LABB
```

This is local research work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Rerun the complete SE3 spotprice value test from P0054V, but with a baseline reproduction gate that accepts small deterministic micro-differences when the row/origin contract is identical and leakage checks pass.

P0054V stopped before price-family ablation because the repeated baseline was slightly outside the strict 1.0 MW tolerance:

```text
P0054V required baseline: 253.70062353819162 MW
P0054V repeated baseline: 252.4272878651775 MW
absolute delta: 1.2733356730141168 MW
strict tolerance: <= 1.0 MW
```

The repeated baseline used the correct P0054R-like row/origin contract:

```text
path/direct rows: 52 173
origins: 1 451
train_fit rows: 38 985
internal validation rows: 3 310
holdout rows: 13 188
DayAhead delivery days: 358
full36 complete origins: 356
```

The delta is only around 0.5% of MAE and the reproduced model was slightly better, not worse. This should not block the price-feature-method test.

## Relationship to P0054V

P0054V2 supersedes P0054V for the current spotprice feature-value question.

P0054V2 must still follow:

```text
requirements/packages/P0054V-labb-complete-spotprice-value-test-se3-consumption.md
requirements/packages/P0054V-operator-clarification-price-stitching.md
```

except where this package explicitly relaxes the baseline gate.

## Required target source

Use only corrected ENTSO-E SE3 actual total load:

```text
table: entsoe_consumption_area_hourly_v1
area: SE3
target_column: consumption_mw
source_type: actual_total_load
```

Forbidden as target:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
cross-border physical flows
net positions
scheduled exchanges
A09/A11 flow/exchange
A61 capacity
production
price
```

STOP if old target or flow data is used as target.

## Required split and internal validation

Use the P0054R/P0054T4 contract:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
internal_validation_start: around 2025-03-01T00:00:00Z, strictly inside train_fit
```

Expected row/origin counts, allowing only documented data-refresh differences:

```text
path/direct rows ≈ 52 173
origins ≈ 1 451
train_fit rows ≈ 38 985
internal_validation rows ≈ 3 310
holdout rows ≈ 13 188
DayAhead delivery days ≈ 358
full36 complete origins ≈ 356
```

Holdout must not be used for model fitting, ensemble weights, correction fitting, feature-family selection, regime threshold fitting or conditional branch selection.

## Relaxed baseline gate

Before any price-family comparison, reproduce the no-price baseline:

```text
model = HorizonBiasCorrected_WeightedEnsemble_no_price
weather = weather_actual_as_forecast_proxy
```

P0054V2 baseline gate passes if all of the following are true:

```text
1. corrected ENTSO-E target is used
2. row/origin contract matches P0054R/P0054T4 or deviations are explained
3. no old target or flow target is used
4. leakage review passes for the baseline
5. DayAhead hourly MAE is close to P0054R/P0054T4 baseline by either rule:
   a. absolute delta <= 2.0 MW
   OR
   b. relative delta <= 1.0% of baseline MAE
```

Reference baseline:

```text
253.70062353819162 MW
```

The P0054V repeated baseline:

```text
252.4272878651775 MW
```

would pass this relaxed gate.

STOP if the relaxed gate fails.

## Price stitching semantics

Follow the P0054V operator clarification exactly.

For the consumption model:

```text
train_fit target timestamps:
  use actual historical SE3 spot price where available

history before forecast origin:
  use actual SE3 spot price strictly before forecast_origin_timestamp_utc
  include previous 48h anchor features where available

future target-window horizons at inference:
  use forecasted SE3 spot price, not realized actual spot
```

Required stitched feature classes:

```text
actual_spot_history_feature
forecast_spot_future_feature
stitched_spot_path_feature
```

Required anchor examples:

```text
actual_spot_lag_1h
actual_spot_lag_24h
actual_spot_lag_48h
actual_spot_history_0_24h_mean
actual_spot_history_24_48h_mean
actual_spot_history_48h_mean
actual_spot_history_48h_min
actual_spot_history_48h_max
actual_spot_history_48h_spread
actual_spot_last_known_value
```

The train/inference skew must be documented:

```text
train_fit target-window price values are actual spot
holdout future target-window price values are forecast spot
```

This is allowed for P0054V2 and must not block the test.

## Full-coverage price forecast source

Create or verify forecast-safe SE3 price forecast coverage for the full P0054R consumption contract:

```text
expected path/direct rows ≈ 52 173
expected origins ≈ 1 451
```

Preferred source:

```text
P0054L2 Ensemble reconstructed for all P0054R origins/horizons
```

Acceptable fallback:

```text
P0054S/P0054L2-equivalent local price model trained only on train_fit-safe price history and applied to all P0054R origins/horizons
```

If a local durable log/table/view is created, use:

```text
advanced_spotprice_forecast_log_p0054v2_se3_full_coverage_v1
```

Required columns:

```text
forecast_origin_timestamp_utc
target_timestamp_utc
horizon_hour
area
predicted_spot_price_se3
price_model_family
price_model_package_source
unit_or_currency
generated_by_package
```

STOP if full forecast-safe price coverage cannot be created or verified.

## Price feature families

Evaluate on identical full coverage.

Required for M1:

```text
P0 no price baseline
P1 raw forecast price / stitched raw price
P2 path and daily shape features
P3 price regime features
P4 spike and ramp features
```

Optional if runtime allows:

```text
P5 interactions with temperature/calendar/load regimes
P6 conditional price-aware branch
M3 XGBoost expansion
M2 WeightedEnsemble expansion
P0054T4 inference-only weather-noise repeat for promising price family
```

Feature-family examples should follow P0054V.

## Decision thresholds

Price may be default in SE3 consumption only if:

```text
DayAhead hourly MAE improves by >= 2% relative to P0 on identical full coverage
and full_36h MAE does not worsen by more than 1%
and daily energy error does not worsen by more than 1%
```

Price may be conditional/regime-only if:

```text
high-risk or high-price regime MAE improves by >= 10%
and broad DayAhead hourly MAE worsens by <= 1%
```

Otherwise exclude price from the default SE3 consumption model.

Even if excluded from consumption, decide whether price features should still be carried into later market-emulator layers.

## Metrics

Required DayAhead metrics:

```text
hourly_MAE_delivery_day
hourly_RMSE_delivery_day
bias_delivery_day
hourly_MAE_percent_of_mean_actual
absolute_daily_energy_error_MWh
signed_daily_energy_error_MWh
daily_energy_error_percent_of_actual
peak_hour_error_MW
peak_hour_timing_error_hours
offpeak_MAE
morning_ramp_MAE
evening_peak_MAE
```

Required full_36h metrics:

```text
MAE_full_36h
RMSE_full_36h
bias_full_36h
p90_absolute_error
p95_absolute_error
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
```

Required comparisons:

```text
price_family_delta_vs_P0_MW
price_family_delta_vs_P0_percent
best_price_family_by_DayAhead_MAE
best_price_family_by_daily_energy_error
best_price_family_by_full36_MAE
best_regime_specific_result
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054V2/CHANGELOG.md
requirements/package-runs/P0054V2/review.md
requirements/package-runs/P0054V2/design.md
requirements/package-runs/P0054V2/functions.md
requirements/package-runs/P0054V2/labb-label.md
requirements/package-runs/P0054V2/prior-evidence-summary.md
requirements/package-runs/P0054V2/p0054v-stop-review.md
requirements/package-runs/P0054V2/target-source-contract.md
requirements/package-runs/P0054V2/split-policy-applied.md
requirements/package-runs/P0054V2/baseline-reproduction-gate.md
requirements/package-runs/P0054V2/price-stitching-policy.md
requirements/package-runs/P0054V2/actual-spot-training-policy.md
requirements/package-runs/P0054V2/price-history-anchor-features.md
requirements/package-runs/P0054V2/train-inference-skew-review.md
requirements/package-runs/P0054V2/price-forecast-source-contract.md
requirements/package-runs/P0054V2/price-forecast-log-schema.md
requirements/package-runs/P0054V2/price-forecast-log-coverage.md
requirements/package-runs/P0054V2/price-forecast-safety-review.md
requirements/package-runs/P0054V2/dataset-contract.md
requirements/package-runs/P0054V2/feature-families.md
requirements/package-runs/P0054V2/price-feature-family-results.md
requirements/package-runs/P0054V2/dayahead-results.md
requirements/package-runs/P0054V2/full-36h-results.md
requirements/package-runs/P0054V2/daily-energy-error-results.md
requirements/package-runs/P0054V2/regime-results.md
requirements/package-runs/P0054V2/conditional-price-branch-results.md if run
requirements/package-runs/P0054V2/feature-importance.md if run
requirements/package-runs/P0054V2/leakage-review.md
requirements/package-runs/P0054V2/decision.md
requirements/package-runs/P0054V2/emulator-stack-recommendation.md
requirements/package-runs/P0054V2/interpretation.md
requirements/package-runs/P0054V2/what-we-learned.md
requirements/package-runs/P0054V2/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
price-feature-family-results.csv
regime-deltas.csv
price-forecast-coverage-summary.json
```

Do not commit large raw data, model binaries, full prediction dumps, virtualenvs or caches.

## Files to inspect

```text
requirements/package-runs/P0054V/CHANGELOG.md
requirements/package-runs/P0054V/baseline-reproduction-gate.md
requirements/package-runs/P0054V/review.md
requirements/packages/P0054V-operator-clarification-price-stitching.md
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054T3/baseline-reproduction-gate.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0054S/model-comparison.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
src/mac/** relevant local modeling scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Files allowed to change

```text
requirements/packages/P0054V2-labb-complete-spotprice-value-test-relaxed-gate.md
requirements/package-runs/P0054V2/**
src/mac/** narrowly scoped full-coverage price forecast and price-feature-family ablation code if needed
tests/mac/** narrowly scoped tests for price stitching, full coverage and leakage if code changes are made
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No external live data calls.
No old target.
No flow data as target.
No future actual holdout spot price as feature.
No future actual load/production/flow features.
No holdout fitting or selection.
No partial-coverage price result presented as full-coverage.
No broad refactor unrelated to P0054V2.
No large artifacts.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054V STOP reason reviewed
relaxed no-price baseline gate passes
full P0054R-compatible price forecast coverage created or STOP reason documented
corrected ENTSO-E target used
old target not used
price features follow actual-history plus forecast-future stitching
previous 48h anchor is strictly before origin
no holdout target-window actual spot in feature matrix
no future actual load/production/flow features in feature matrix
regime thresholds learned only from train_fit/internal validation
same full coverage used for P0 and price-family comparisons
no holdout fitting or selection
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- relaxed baseline gate passes.
- full safe P0054R-compatible price forecast coverage is created or verified.
- P1 raw, P2 shape, P3 regime and P4 spike/ramp families are evaluated for M1.
- price deltas are computed on identical full coverage.
- actual-training/forecast-inference stitching is documented.
- final decision is explicit.
- leakage review passes.
```

WARN is acceptable if:

```text
- optional P5/P6 are skipped due to runtime.
- M2/M3 expansion is skipped after complete M1 results.
- feature importance is skipped.
- optional P0054T4 weather-noise repeat is skipped.
```

STOP if:

```text
- relaxed baseline gate fails.
- full safe price forecast coverage cannot be produced.
- partial price coverage is reused as final full-coverage evidence.
- future actual price/load leakage is found.
- holdout is used for fitting or selection.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
P0054V STOP review
relaxed baseline reproduction result
full price forecast coverage status
price stitching summary
price feature families run/skipped
best broad MAE result
best daily energy result
best high-risk regime result
price family deltas versus no-price
final decision: default / conditional-only / excluded
emulator-stack recommendation
tests/commands run
files changed
confirmation no old target/flow target/external/device/runtime integration
confirmation no large artifacts committed
```

## Completion notes

Completed as `PASS`.

Relaxed baseline gate passed:

```text
model: HorizonBiasCorrected_WeightedEnsemble_no_price
reference DayAhead MAE: 253.70062353819162 MW
reproduced DayAhead MAE: 252.4272878651774 MW
absolute delta: 1.2733356730142305 MW
relative delta: 0.501904825954259%
gate: absolute_delta <= 2.0 MW OR relative_delta <= 1.0%
```

Full row/origin contract:

```text
source_rows: 35125
direct_rows: 52173
path_rows: 52173
origins: 1451
train_fit_rows: 38985
holdout_rows: 13188
internal_validation_rows: 3310
DayAhead delivery days: 358
full36 complete origins: 356
```

Full forecast-safe holdout price coverage was created locally without live API calls:

```text
required_holdout_rows: 13188
price_forecast_rows: 13188
missing_required_holdout_rows: 0
```

P0054V2 followed the operator stitching policy:

```text
train_fit target-window price values: actual historical SE3 spot
holdout future target-window price values: forecast SE3 spot
actual spot anchor: strictly before forecast_origin_timestamp_utc
```

M1 price-family results on identical full coverage:

```text
P0 no price:
  DayAhead MAE: 252.4272878651775 MW
  full36 MAE: 242.5642604364506 MW
  daily energy error: 4346.592563127953 MWh

P1 raw stitched price:
  DayAhead delta vs P0: +3.6193472393223374 MW / +1.4338177421037959%
  full36 delta vs P0: +1.3517865494121513%
  daily energy delta vs P0: +2.3848392500110194%

P2 path shape:
  DayAhead delta vs P0: +7.440069694042791 MW / +2.9474110176299813%

P3 price regime:
  DayAhead delta vs P0: +9.307249298514535 MW / +3.6871010964098208%

P4 spike/ramp:
  DayAhead delta vs P0: +8.434365970096906 MW / +3.341305150258452%
```

Best broad, daily-energy and full36 result was `P0_no_price`.

Best high-risk/regime result:

```text
regime: low_price
family: P4_spike_ramp
regime MAE delta: -0.6998468530605615%
```

This is far below the `>= 10%` conditional threshold, while broad P4 DayAhead MAE worsened by `+3.341305150258452%`.

Decision:

```text
generic SE3 consumption model price feature: excluded
conditional price branch: not supported by P0054V2 evidence
market-emulator layers: keep price as an emulator/cost/regime input
```

Leakage review passed. P0054V2 did not use old target, flow target, future actual holdout spot, future actual load/production/flow/A61 features, holdout fitting/selection, external live data calls, device/runtime writes, Shelly, Home Assistant, Nord Pool/workplace integration or large artifacts.

Optional P5/P6/M2/M3/P0054T4 weather-noise repeats were skipped after complete required M1 P0-P4 evidence.
