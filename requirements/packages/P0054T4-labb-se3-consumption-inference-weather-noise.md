# Package P0054T4: LABB SE3 inference-only weather noise realism

## Status

completed

## Package order

P0054T4

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Correct the weather-noise interpretation from P0054T3.

P0054T3 applied ±2°C temperature noise consistently to both train_fit and holdout before retraining/evaluation. That tested noise-training/regularization, not the operator's intended production realism.

The operator clarification is:

```text
Weather should be correct/actuals in training.
Weather should be noisy only at forecast/question time.
```

In other words:

```text
train_fit weather features = weather_actual_as_forecast_proxy, unchanged
holdout/inference weather features = weather_actual_as_forecast_proxy + deterministic temperature noise
```

P0054T4 must test the selected P0054T3/P0054R consumption candidate under inference-only weather error.

## Required baseline

Reproduce the P0054R/P0054T3 W0/P0 baseline first:

```text
model = HorizonBiasCorrected_WeightedEnsemble_no_price
training weather = weather_actual_as_forecast_proxy
holdout weather = weather_actual_as_forecast_proxy
DayAhead hourly MAE ≈ 253.7006 MW
full_36h MAE ≈ 243.6767 MW
daily energy error ≈ 4 381 MWh ≈ 1.9334%
```

Required gate:

```text
DayAhead MAE must be within <= 1.0 MW of 253.7006 MW.
```

STOP if this reproduction gate fails.

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

## Weather modes

Run at least these weather modes:

```text
W0 = clean actual-weather proxy for train_fit and holdout
W1 = inference-only temperature noise ±2°C on holdout/question rows only
```

Optional, if cheap:

```text
W2 = inference-only temperature noise ±1°C
W3 = inference-only temperature noise ±3°C
W4 = biased cold/warm scenarios, e.g. -2°C and +2°C constant holdout temperature bias
```

Primary required protocol:

```text
Fit model once using clean train_fit weather.
For each holdout/inference seed, keep the trained model fixed.
Apply temperature noise only to holdout/inference weather feature columns.
Evaluate predictions.
```

Do not retrain the model on noisy training weather for the primary W1 result.

## Temperature columns

Discover and document temperature-like SE3 weather columns. Expected examples:

```text
weather_proxy_temperature_2m_se3
weather_proxy_apparent_temperature_se3
```

Apply noise only to temperature-like columns. Do not noise calendar, target, lag/load, price, or non-temperature features.

If weather feature engineering derives degree-days or temperature transforms before modeling, Codex must make clear whether noise is applied:

```text
before derived weather features are computed
or directly to already-computed model input temperature columns
```

Preferred production-realism approximation:

```text
apply noise to raw temperature proxy columns before derived weather features are computed
```

If only final feature matrix is available, apply to final temperature model-input columns and document limitation.

## Seeds

Use deterministic seeds:

```text
required: 1000..1009
minimum acceptable WARN: 1000..1004
```

Report mean/std/min/max across seeds.

## Model scope

Primary required model:

```text
M1 = HorizonBiasCorrected_WeightedEnsemble_no_price
```

Optional if cheap:

```text
M2 = WeightedEnsemble_no_price
M3 = XGBoost_no_price
```

Do not include spot-price features in the primary result. P0054T3 showed price worsened matched-coverage consumption metrics; P0054T4 is a weather-realism package.

## Required split and validation

Use the P0054R split and internal validation semantics:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
internal validation starts around 2025-03-01T00:00:00Z, strictly inside train_fit
```

Holdout must not be used for model fitting, model selection, ensemble weights, horizon-bias correction or feature selection.

## Forecast use cases

Evaluate both:

```text
DayAhead delivery-day forecast:
  forecast_origin = 12:00 Europe/Stockholm on D-1
  delivery_day = D 00:00..23:00 Europe/Stockholm

full_36h:
  complete 36-hour path from origin
```

## Metrics

Required DayAhead metrics:

```text
hourly_MAE_delivery_day
hourly_RMSE_delivery_day
bias_delivery_day
hourly_MAE_percent_of_mean_actual
hourly_MAE_percent_of_median_actual
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
MAE_percent_of_mean_actual
MAE_percent_of_median_actual
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
```

Required deltas:

```text
inference_noise_delta_W1_minus_W0_MW
inference_noise_delta_W1_minus_W0_percent
seed_mean
seed_std
seed_min
seed_max
worst_seed
best_seed
```

## Key questions to answer

P0054T4 must answer:

```text
1. How much does ±2°C inference-only temperature error degrade the best SE3 consumption model?
2. Does the model remain below 3% DayAhead hourly MAE?
3. Does the model remain below 4% DayAhead hourly MAE?
4. How stable are results across seeds?
5. Is P0054T3's noise-training improvement just regularization rather than production realism?
6. Should the next package be rolling retrain, real historical weather forecast ingestion, or both?
```

## Interpretation policy

P0054T4 must explicitly distinguish:

```text
P0054T3 W1 = train+holdout noise / regularization-style test
P0054T4 W1 = clean training + noisy inference / forecast-weather-error test
```

Only P0054T4 should be used for weather-error realism conclusions.

## Required evidence files

Create:

```text
requirements/package-runs/P0054T4/CHANGELOG.md
requirements/package-runs/P0054T4/review.md
requirements/package-runs/P0054T4/design.md
requirements/package-runs/P0054T4/functions.md
requirements/package-runs/P0054T4/labb-label.md
requirements/package-runs/P0054T4/p0054t3-weather-interpretation-review.md
requirements/package-runs/P0054T4/baseline-reproduction-gate.md
requirements/package-runs/P0054T4/target-source-contract.md
requirements/package-runs/P0054T4/split-policy-applied.md
requirements/package-runs/P0054T4/dataset-contract.md
requirements/package-runs/P0054T4/model-contract.md
requirements/package-runs/P0054T4/weather-noise-protocol.md
requirements/package-runs/P0054T4/temperature-feature-selection.md
requirements/package-runs/P0054T4/model-training-evidence.md
requirements/package-runs/P0054T4/inference-noise-results.md
requirements/package-runs/P0054T4/dayahead-results.md
requirements/package-runs/P0054T4/full-36h-results.md
requirements/package-runs/P0054T4/daily-energy-error-results.md
requirements/package-runs/P0054T4/seed-stability-results.md
requirements/package-runs/P0054T4/leakage-review.md
requirements/package-runs/P0054T4/interpretation.md
requirements/package-runs/P0054T4/what-we-learned.md
requirements/package-runs/P0054T4/next-package-recommendation.md
```

Optional compact evidence:

```text
inference-noise-summary.json
seed-results.csv
weather-deltas.csv
```

Do not commit model binaries, large raw datasets, full prediction dumps, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054T3/CHANGELOG.md
requirements/package-runs/P0054T3/baseline-reproduction-gate.md
requirements/package-runs/P0054T3/weather-noise-results.md
requirements/package-runs/P0054T3/interpretation.md
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/model-training-evidence.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054R/leakage-review.md
src/mac/** relevant P0054R/P0054T3 modeling/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Files allowed to change

```text
requirements/packages/P0054T4-labb-se3-consumption-inference-weather-noise.md
requirements/package-runs/P0054T4/**
src/mac/** narrowly scoped inference-weather-noise evaluation code if needed
tests/mac/** narrowly scoped tests for train-clean/holdout-noisy weather semantics if code changes are made
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No Nord Pool/workplace integration.
No live API calls.
No old physical_balance target.
No flow/exchange/capacity target.
No future actual load/price leakage.
No spot-price features in primary P0054T4 result.
No noisy train_fit weather in primary W1 result.
No holdout fitting or selection.
No broad refactor unrelated to P0054T4.
No large raw data/model/prediction artifacts.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054R/P0054T3 baseline reproduction gate passes
corrected ENTSO-E target is used
old physical_balance target is not used
training weather remains clean in W1
holdout/inference weather is noisy in W1
noise is applied only to selected temperature features
noise bounds within [-2,+2] C for W1
model is not retrained per noisy holdout seed for primary W1 unless explicitly documented as a separate optional branch
no future actual load/price/flow/A61 columns in features
no holdout tuning or selection
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- baseline reproduction gate passes.
- clean training + noisy inference W1 is evaluated for M1.
- at least 10 seeds are run, or 5 seeds with WARN.
- DayAhead and full_36h metrics are reported.
- inference-only weather delta is clear.
- leakage review passes.
```

WARN is acceptable if:

```text
- only 5 seeds are run due to runtime.
- noise can only be applied to final model-input temperature columns, not raw pre-derivation weather columns.
- optional M2/M3 are skipped.
```

STOP if:

```text
- baseline reproduction gate fails.
- corrected ENTSO-E target cannot be used.
- noisy training weather is used for the primary W1 result.
- holdout is used for fitting/selection.
- future actual load/price leakage is introduced.
- device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
baseline reproduction gate result
model used
weather feature columns noised
seed count
W0 clean result
W1 inference-only noisy result
W1-W0 delta
whether W1 remains <=3% and <=4% DayAhead MAE
seed stability
comparison against P0054T3 train+holdout noise result
recommended next package
commands/tests run
files changed
confirmation no old target/flow target/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
```

## Completion notes

Completed as `WARN`.

WARN reason:

```text
P0054T4 applies deterministic +/-2 C noise to the final model-input
temperature columns because the available P0054R/P0054Q path exposes the
already-derived model matrix, not a raw-weather recomputation hook.
```

Baseline reproduction gate passed:

```text
model: HorizonBiasCorrected_WeightedEnsemble_no_price
target DayAhead MAE: 253.70062353819162 MW
reproduced DayAhead MAE: 253.70062353819182 MW
absolute delta: 1.9895196601282805e-13 MW
tolerance: 1.0 MW
```

P0054T4 used corrected ENTSO-E SE3 actual total load from
`entsoe_consumption_area_hourly_v1` as target and kept the P0054R split
semantics. Primary W1 fitted M1 once on clean train_fit weather, kept the
trained model, ensemble weights and horizon-bias correction fixed per seed,
and applied noise only to holdout/inference rows.

Temperature model-input columns noised:

```text
weather_proxy_apparent_temperature_se3
weather_proxy_temperature_2m_se3
```

Seeds:

```text
1000..1009
```

Result:

```text
W0 clean DayAhead MAE: 253.70062353819173 MW
W0 clean DayAhead MAE percent of mean actual: 2.638782944935854%
W0 clean full_36h MAE: 243.67666893537262 MW
W0 clean daily absolute energy error: 4381.407120292003 MWh

W1 inference-only noisy DayAhead MAE mean: 258.9097276451904 MW
W1 inference-only noisy DayAhead MAE std: 0.5364553349088972 MW
W1 inference-only noisy DayAhead MAE min: 257.77387412076644 MW
W1 inference-only noisy DayAhead MAE max: 259.791251709251 MW
W1 inference-only noisy DayAhead MAE percent of mean actual: 2.692963714711827%
W1 inference-only noisy full_36h MAE mean: 248.4812084287683 MW
W1 inference-only noisy daily absolute energy error mean: 4394.273511199443 MWh

W1-W0 DayAhead MAE delta: +5.209104106998666 MW
W1-W0 DayAhead MAE relative delta: +2.0532484447025783%
W1 remains <=3% DayAhead MAE: true
W1 remains <=4% DayAhead MAE: true
```

Interpretation:

```text
P0054T3 W1 tested train+holdout noise and should be read as
regularization-style robustness, not production weather-error realism.

P0054T4 W1 tests clean training plus noisy inference and is the weather-error
realism result for this candidate.
```

Leakage and forbidden-action review passed. P0054T4 did not use old
`physical_balance` targets, flow/exchange/capacity/A61 inputs, spot-price
features, live APIs, devices, runtime writes, Nord Pool/workplace integration,
or holdout fitting/selection. No large raw datasets, model binaries or full
prediction dumps were created.

Recommended next package:

```text
Proceed to rolling/expanding retrain for the no-price M1 path, and separately
add real historical weather forecast ingestion.
```
