# Package P0054T3: LABB corrected SE3 consumption weather/price matrix

## Status

completed

## Package order

P0054T3

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Rerun the SE3 consumption 3x2x2 model/weather/price matrix from P0054T, but corrected so that every case is built on the reproducible P0054R row/origin/feature/model contract.

P0054T2 proved that P0054T was not a faithful P0054R reproduction:

```text
P0054R/R_like DayAhead MAE ≈ 253.7006 MW ≈ 2.6388%
P0054T W0/P0 DayAhead MAE ≈ 624.3882 MW ≈ 6.4629%
```

Root cause from P0054T2:

```text
P0054T used the P0054N exact-origin price-coverage skeleton even for no-price cases.
That restricted train_fit to March-May 2025 and produced zero internal-validation rows.
M1 equaled M2 because horizon-bias correction fitted all-zero biases.
```

P0054T3 must supersede P0054T for weather/price conclusions.

## Required baseline reproduction gate

Before running the full matrix, P0054T3 must reproduce P0054R W0/P0 no-price within deterministic tolerance.

Required gate:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
DayAhead hourly MAE must equal or nearly equal 253.7006 MW
acceptable tolerance: <= 1.0 MW absolute difference, unless a documented code/data drift explains a smaller reproducibility tolerance
```

If this gate fails, STOP. Do not run or report the full matrix as authoritative.

## Required target source

Use only corrected ENTSO-E SE3 actual total load:

```text
table: entsoe_consumption_area_hourly_v1
area: SE3
target_column: consumption_mw
source_type: actual_total_load
area_scope: bidding_zone_internal_consumption_or_load
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

Use the P0054R split semantics:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation for ensemble weights and horizon-bias/correction fitting must exist and must be strictly inside train_fit. Prefer P0054R's internal validation window:

```text
internal_validation_start = 2025-03-01T00:00:00Z
```

Expected P0054R-like row counts from P0054T2 reproduction:

```text
source_rows ≈ 35 125
path/direct rows ≈ 52 173
train_fit_rows ≈ 38 985
internal_validation_rows ≈ 3 310
holdout_rows ≈ 13 188
origins ≈ 1 451
DayAhead delivery days ≈ 358
full36 complete origins ≈ 356
```

Exact row counts may vary only with documented data refresh. Large deviations must be explained before matrix execution.

## Forecast use cases

### DayAhead

Use P0054R/P0054Q semantics:

```text
forecast_origin = 12:00 Europe/Stockholm on D-1
delivery_day = D 00:00..23:00 Europe/Stockholm
```

### full_36h

Use complete 36-hour paths:

```text
forecast_origin_timestamp_utc = origin
target_window = 36 target hours from origin
```

Document horizon convention as 0..35 or 1..36 and keep it consistent with P0054R reproduction.

## Corrected matrix design

Run exactly:

```text
3 consumption model variants
x 2 weather modes
x 2 price modes
= 12 combinations
```

### Models

Default required models:

```text
M1 = HorizonBiasCorrected_WeightedEnsemble
M2 = WeightedEnsemble
M3 = XGBoost
```

M1 and M2 must not be identical unless the learned horizon-bias correction is proven to be exactly zero on a valid internal-validation set, which is not expected.

Required M1/M2 diagnostic:

```text
report horizon_bias_nonzero_count
report max_abs_horizon_bias_mw
report prediction_correlation_M1_M2
report p95_abs_prediction_diff_M1_M2
```

### Weather modes

Run both:

```text
W0 = weather_actual_as_forecast_proxy
W1 = temperature_noise_uniform_minus2_plus2C
```

Weather noise protocol:

```python
temp_noisy = temp_actual_proxy + uniform(-2.0, +2.0)
```

Temperature columns must be discovered and documented. Expected examples:

```text
weather_proxy_apparent_temperature_se3
weather_proxy_temperature_2m_se3
```

Use deterministic seeds.

Required minimum:

```text
seeds = 1000..1004
```

Preferred if runtime allows:

```text
seeds = 1000..1009
```

Primary required interpretation:

```text
apply weather noise consistently to train_fit and holdout, then retrain/evaluate each model per seed
```

Holdout-only noise is not acceptable as the primary P0054T3 result unless the package returns WARN and clearly labels it as sensitivity-only.

### Price modes

Run both:

```text
P0 = no_price
P1 = with_best_spotprice_forecast
```

Best spot-price source remains:

```text
P0054L2 Ensemble
```

because P0054S did not create a materially better recommended forecast log.

Critical correction versus P0054T:

```text
The P0/no-price cases must use the full P0054R row/origin contract.
They must not be restricted by spot-price forecast coverage.
```

For P1, Codex must align price forecast features without destroying the P0054R reproduction contract more than necessary. Acceptable approaches, in order:

```text
1. Build P0054L2-compatible forecast features for all P0054R origins/horizons.
2. If P1 coverage is narrower, run P1 on its safe coverage but also run a matched P0_on_price_coverage diagnostic for fair price delta.
3. Do not use P1's narrower coverage to redefine the primary P0 baseline.
```

If P1 cannot be aligned safely, STOP the price branch and return WARN/STOP with exact reason. Do not produce misleading price deltas.

Price features must be forecast-safe at forecast origin. Allowed examples:

```text
predicted_spot_price_se3
price_forecast_0_24h_mean
price_forecast_24_36h_mean
price_forecast_0_36h_mean
price_forecast_rank_within_path
price_forecast_spike_flag_within_path
price_forecast_ramp_from_previous_horizon
price_forecast_peak_offpeak_indicator
```

All price path features must be derived only from forecast rows available at the same forecast origin.

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
weekday/weekend/holiday splits
cold/high-load/high-price/spike/ramp regimes where available
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
price_delta_with_minus_no_price per model/weather mode on matched coverage
weather_noise_delta_noisy_minus_proxy per model/price mode
M1_vs_M2_delta
best_overall_by_dayahead_hourly_MAE
best_overall_by_daily_energy_error
best_overall_by_full36_MAE
robustness_score = noisy_mean_MAE + noisy_std_penalty if useful
```

## Key questions to answer

P0054T3 must answer:

```text
1. After correcting the harness, which model is best under clean weather and no price?
2. How much does ±2°C temperature noise degrade the P0054R winner?
3. Does P0054L2 spot-price forecast help on matched coverage under clean weather?
4. Does P0054L2 spot-price forecast help under noisy weather?
5. Is price still harmful, or was the P0054T price result an artifact?
6. Does any noisy-weather combination remain below 4% DayAhead hourly MAE?
7. Which combination should go to rolling/expanding retrain next?
```

## Learning thresholds

Treat a combination as operationally interesting if:

```text
W0 DayAhead hourly MAE <= 3.0%
W1 noisy mean DayAhead hourly MAE <= 4.0%
```

Treat price as useful only if:

```text
with_price improves DayAhead hourly MAE or daily energy error by >= 2% relative on matched coverage
and does not worsen full_36h MAE by more than 1%
```

Treat a model as robust if:

```text
W1 noisy mean DayAhead MAE worsens by <= 25% relative to W0
and noisy seed std is operationally small
```

## Runtime policy

The corrected matrix may be expensive. Codex must:

```text
run baseline reproduction gate first
run tests serially
checkpoint each completed combination
not discard completed results if later combinations fail
prioritize W0/P0 full P0054R coverage, then W1/P0, then P1 matched-coverage branches
record duration per combination
```

If runtime is too high, use 5 W1 seeds but keep all 12 combinations. If a P1 matched-coverage branch is narrower, keep the primary P0 full-coverage results and add separate matched P0 diagnostics.

## Required evidence files

Create:

```text
requirements/package-runs/P0054T3/CHANGELOG.md
requirements/package-runs/P0054T3/review.md
requirements/package-runs/P0054T3/design.md
requirements/package-runs/P0054T3/functions.md
requirements/package-runs/P0054T3/labb-label.md
requirements/package-runs/P0054T3/p0054t2-root-cause-review.md
requirements/package-runs/P0054T3/baseline-reproduction-gate.md
requirements/package-runs/P0054T3/target-source-contract.md
requirements/package-runs/P0054T3/split-policy-applied.md
requirements/package-runs/P0054T3/dataset-contract.md
requirements/package-runs/P0054T3/model-selection-from-p0054r.md
requirements/package-runs/P0054T3/m1-m2-diagnostic.md
requirements/package-runs/P0054T3/spotprice-source-contract.md
requirements/package-runs/P0054T3/price-coverage-policy.md
requirements/package-runs/P0054T3/weather-noise-protocol.md
requirements/package-runs/P0054T3/feature-groups.md
requirements/package-runs/P0054T3/input-classification.md
requirements/package-runs/P0054T3/runtime-policy.md
requirements/package-runs/P0054T3/model-training-evidence.md
requirements/package-runs/P0054T3/matrix-combinations.md
requirements/package-runs/P0054T3/matrix-results-summary.md
requirements/package-runs/P0054T3/dayahead-results.md
requirements/package-runs/P0054T3/full-36h-results.md
requirements/package-runs/P0054T3/daily-energy-error-results.md
requirements/package-runs/P0054T3/weather-noise-results.md
requirements/package-runs/P0054T3/price-ablation-results.md
requirements/package-runs/P0054T3/robustness-ranking.md
requirements/package-runs/P0054T3/conditional-regime-results.md
requirements/package-runs/P0054T3/leakage-review.md
requirements/package-runs/P0054T3/interpretation.md
requirements/package-runs/P0054T3/what-we-learned.md
requirements/package-runs/P0054T3/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
matrix-results.csv
seed-results.csv
price-deltas.csv
weather-deltas.csv
robustness-ranking.csv
matched-coverage-price-deltas.csv
```

Do not commit model binaries, large raw datasets, full prediction dumps, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054T2/CHANGELOG.md
requirements/package-runs/P0054T2/root-cause-analysis.md
requirements/package-runs/P0054T2/reproduction-attempt-results.md
requirements/package-runs/P0054T2/impact-on-p0054t.md
requirements/package-runs/P0054T2/impact-on-p0054r.md
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/model-training-evidence.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054R/leakage-review.md
requirements/package-runs/P0054S/model-comparison.md
requirements/package-runs/P0054S/leakage-review.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
requirements/package-runs/P0054T/**
requirements/packages/P0054T-labb-se3-consumption-model-weather-price-matrix.md
src/mac/** relevant P0054R/P0054T/P0054T2 modeling/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Files allowed to change

```text
requirements/packages/P0054T3-labb-corrected-se3-consumption-weather-price-matrix.md
requirements/package-runs/P0054T3/**
src/mac/** narrowly scoped corrected matrix/evaluation code if needed
tests/mac/** narrowly scoped tests for reproduction gate/price coverage/weather noise/leakage if code changes are made
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
No actual future spot price as feature.
No holdout fitting or selection.
No P0/no-price coverage restriction caused by price availability.
No broad refactor unrelated to P0054T3.
No large raw data/model/prediction artifacts.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054T2 root cause read
P0054R baseline reproduction gate passes
corrected ENTSO-E target is used
old physical_balance target is not used
P0054R-like row/origin counts confirmed
internal validation rows > 0 for ensemble/bias fitting
M1/M2 are not accidentally aliased
weather noise deterministic and within [-2,+2] C for temperature columns
P0/no-price full coverage is not restricted by price availability
P1 price forecast features are forecast-safe and aligned by origin/horizon
matched-coverage price deltas computed if P1 coverage is narrower
no future actual load/price/flow/A61 columns in features
no holdout tuning or selection
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- P0054R baseline reproduction gate passes.
- Corrected ENTSO-E SE3 target is used.
- All 12 matrix combinations are evaluated, with W1 seed means across at least 5 seeds.
- P0 full-coverage results are preserved.
- P1 price deltas are computed on safe matched coverage if needed.
- Weather and price deltas are clear.
- Leakage review passes.
```

WARN is acceptable if:

```text
- W1 uses 5 seeds instead of 10 due to runtime.
- P1 coverage is narrower but matched P0 diagnostics are clear.
- one optional conditional regime is sparse.
```

STOP if:

```text
- P0054R baseline reproduction gate fails.
- corrected ENTSO-E target cannot be used.
- old target or flow target is used.
- safe price feature alignment fails.
- fewer than the required 12 combinations can be honestly evaluated.
- P0 is restricted by price coverage again.
- future actual load/price leakage is introduced.
- holdout is used for fitting/selection.
- device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
baseline reproduction gate result
P0054R-like row/origin counts
three model variants selected
M1/M2 alias diagnostic
weather noise protocol and seed count
spotprice forecast source and coverage policy
12-combination matrix summary
best W0/P0, W0/P1, W1/P0, W1/P1 results
price deltas by model/weather mode on matched coverage
weather noise deltas by model/price mode
best robust combination
whether any noisy-weather combination remains <= 4% DayAhead hourly MAE
whether price should be kept for next stage
recommended combination for rolling retrain
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation no old target/flow target/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
```

## Completion notes

Completed by Codex on 2026-06-06.

Result: `WARN`.

The P0054R baseline reproduction gate passed:

```text
target DayAhead MAE:      253.70062353819162 MW
reproduced DayAhead MAE:  253.70062353819182 MW
absolute delta:           ~2.0e-13 MW
tolerance:                <= 1.0 MW
```

The corrected P0/no-price branch used full P0054R coverage:

```text
source rows:    35 125
P0 full rows:   52 173
P1 price rows:  16 102
matched P0:     16 102
matrix rows:        12
seed rows:          54
```

`WARN` is due to P1 coverage: the safe P0054N/P0054L2-compatible price forecast rows remain narrower than the P0054R no-price origin skeleton. P0 full coverage was preserved, and price deltas were computed only on matched coverage.

Best primary result by DayAhead hourly MAE:

```text
M1_HorizonBiasCorrectedWeightedEnsemble
W1_tempNoise2C
P0_noPrice_fullCoverage
mean DayAhead MAE: 249.7844 MW
mean DayAhead percent: 2.5980%
mean full36 MAE: 239.3034 MW
mean daily energy error: 4 284.819 MWh
```

Clean-weather no-price P0054R-equivalent result:

```text
M1_HorizonBiasCorrectedWeightedEnsemble
W0_weatherProxy
P0_noPrice_fullCoverage
DayAhead MAE: 253.7006 MW
DayAhead percent: 2.6388%
full36 MAE: 243.6767 MW
daily energy error: 4 381.407 MWh
```

Matched-coverage price result:

```text
P1 worsened DayAhead MAE for all model/weather groups.
M1 W0 price delta: +21.2971 MW (+3.3717%)
M1 W1 price delta: +32.1428 MW (+4.8425%)
M3 W0 price delta: +31.7149 MW (+5.0017%)
M3 W1 price delta: +34.1263 MW (+5.0731%)
```

Weather-noise result:

```text
P0 full coverage did not degrade under deterministic +/-2C retraining sensitivity.
P1 matched coverage degraded by about +6.16% to +6.58% depending on model.
```

Noisy-weather combinations below 4% DayAhead hourly MAE:

```text
3 combinations, all P0 full coverage:
M1, M2 and M3 under W1_tempNoise2C / P0_noPrice_fullCoverage
```

Price should not be kept for the next stage under current safe matched-coverage evidence. Recommended next step is a rolling/expanding retrain package for the P0 full-coverage M1 path, plus a separate package if broader safe price-origin coverage is needed.

No API, devices, runtime, A61, Nord Pool, workplace integration, old physical-balance target, flow/exchange/capacity target, future actual load/price leakage or large model artifacts were used.
