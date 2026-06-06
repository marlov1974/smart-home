# Package P0054U: LABB full-coverage price-feature ablation for SE3 consumption

## Status

planned

## Package order

P0054U

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Test whether SE3 spot-price forecasts can improve SE3 consumption forecasts when evaluated correctly on the full P0054R/P0054T3 row/origin contract, using richer price representations than a simple raw price on/off feature.

P0054T3 found that P0054L2 price features worsened SE3 consumption on matched narrower coverage. However, P0054T3 also showed the price branch had narrower coverage:

```text
P0 no-price full coverage rows: 52 173
P1 P0054L2-compatible price rows: 16 102
```

P0054U must remove this ambiguity by first creating or reconstructing full P0054R-compatible spot-price forecast features for all relevant SE3 consumption forecast origins/horizons, then running a controlled feature-family ablation.

The goal is not to assume price helps. The goal is to test all theoretically plausible price-feature uses in a forecast-safe way.

## Required baseline context

Use P0054R/P0054T3 as the consumption baseline:

```text
target = entsoe_consumption_area_hourly_v1.consumption_mw
area = SE3
best clean no-price model = HorizonBiasCorrected_WeightedEnsemble_no_price
DayAhead hourly MAE ≈ 253.7006 MW ≈ 2.6388%
full_36h MAE ≈ 243.6767 MW ≈ 2.5006%
daily energy error ≈ 4 381 MWh ≈ 1.9334%
```

Also inspect P0054T4 if available, because it is the corrected inference-only weather-noise realism package.

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

## Required split and validation

Use P0054R/P0054T3 split semantics:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation for ensemble weights, feature-family selection and correction fitting must be strictly inside train_fit. Prefer:

```text
internal_validation_start = 2025-03-01T00:00:00Z
```

Holdout must not be used for price-model fitting, consumption-model fitting, feature selection, ensemble weighting, correction fitting or model-family selection.

## Forecast use cases

Evaluate both:

```text
DayAhead delivery-day forecast:
  forecast_origin = 12:00 Europe/Stockholm on D-1
  delivery_day = D 00:00..23:00 Europe/Stockholm

full_36h:
  complete 36-hour path from origin
```

Use the same horizon convention as P0054R/P0054T3.

## Phase 1: Full-coverage SE3 price forecast features

P0054U must first create or reconstruct a full P0054R-compatible SE3 spot-price forecast feature source.

Required coverage target:

```text
all P0054R/P0054T3 consumption forecast origins/horizons needed for P0 no-price full coverage
expected direct/path rows ≈ 52 173, unless local data refresh changes row count
```

Preferred source/model:

```text
P0054L2 Ensemble, reconstructed as an exact-origin forecast feature source for all P0054R origins/horizons
```

Acceptable if P0054L2 cannot cover full contract:

```text
P0054S WeightedEnsemble or documented P0054L2-equivalent model, trained only on train_fit-safe price data and applied to all P0054R origins/horizons.
```

Required forecast log/table/view, if created:

```text
advanced_spotprice_forecast_log_p0054u_se3_full_coverage_v1
```

Required schema semantics:

```text
forecast_origin_timestamp_utc
target_timestamp_utc
horizon_hour
area = SE3
predicted_spot_price_se3
price_model_family
price_model_package_source
is_holdout_forecast
unit/currency
generated_by_package = P0054U
```

Price forecast safety rules:

```text
No actual target-window spot price.
No actual future load/production/flow/A61.
No holdout data for fitting or tuning.
Forecast rows must be available at forecast_origin_timestamp_utc.
```

If a full-coverage price forecast cannot be produced safely, STOP before consumption ablation. Do not rerun a partial-coverage price ablation as if it answers the question.

## Phase 2: Price feature families to test

Run all feasible price-feature families below on the full-coverage forecast source.

### P0: no price baseline

```text
No price features.
Must reproduce P0054R/P0054T3 baseline within <= 1 MW DayAhead MAE for M1.
```

### P1: raw price level

```text
predicted_spot_price_se3
```

### P2: daily/path shape features

Examples:

```text
price_forecast_0_24h_mean
price_forecast_24_36h_mean
price_forecast_0_36h_mean
price_forecast_daily_min
price_forecast_daily_max
price_forecast_daily_spread
price_forecast_peak_offpeak_spread
price_forecast_hour_rank_in_day
price_forecast_hour_rank_in_36h_path
```

### P3: price regime features

Examples:

```text
price_forecast_high_regime_flag
price_forecast_low_regime_flag
price_forecast_negative_or_very_low_flag
price_forecast_top_quartile_flag
price_forecast_bottom_quartile_flag
price_forecast_volatility_regime
```

Regime thresholds must be learned from train_fit/internal validation only.

### P4: spike/ramp features

Examples:

```text
price_forecast_spike_risk_flag
price_forecast_ramp_from_previous_horizon
price_forecast_abs_ramp_from_previous_horizon
price_forecast_morning_ramp
price_forecast_evening_ramp
price_forecast_peak_hour_indicator
```

### P5: interaction features

Examples:

```text
price_x_temperature
price_x_apparent_temperature
price_x_hour
price_x_weekday_weekend
price_x_high_load_lag_regime
price_x_cold_regime
price_x_holiday
```

Interactions must use forecast-safe price and forecast-known or historical/proxy features available at origin.

### P6: conditional price-aware branch

Test a conditional setup if practical:

```text
normal regime: use P0 no-price model
price-sensitive regime: use price-aware model or correction
```

Regime selection must be based on forecast-safe price regime features and learned only inside train_fit/internal validation.

## Consumption models to evaluate

Minimum required:

```text
M1 = HorizonBiasCorrected_WeightedEnsemble
M3 = XGBoost
```

Preferred if runtime allows:

```text
M1 = HorizonBiasCorrected_WeightedEnsemble
M2 = WeightedEnsemble
M3 = XGBoost
```

Primary comparison should be M1 against P0 no-price baseline.

## Weather policy

Primary P0054U should use clean weather proxy for model-selection clarity:

```text
weather_actual_as_forecast_proxy
```

If P0054T4 has completed and exposed a clean-training/noisy-inference harness, Codex may optionally repeat the most promising price-feature family under inference-only weather noise. This is optional and must not block the core full-coverage price ablation.

Do not use train+holdout noisy weather as the primary price ablation; that was P0054T3 regularization-style noise, not production realism.

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

Required price comparison metrics:

```text
price_family_delta_vs_P0_MW
price_family_delta_vs_P0_percent
best_price_family_by_DayAhead_MAE
best_price_family_by_daily_energy_error
best_price_family_by_full36_MAE
regime-specific deltas
feature importance or permutation importance if feasible
```

## Learning thresholds

Treat price as useful only if a price-feature family improves:

```text
DayAhead hourly MAE by >= 2% relative to P0 no-price on identical full coverage
or daily energy error by >= 5% relative without worsening hourly MAE by more than 1%
or high-price/spike/ramp regime MAE by >= 10% without worsening broad MAE by more than 1%
```

Treat price as strongly useful if:

```text
DayAhead hourly MAE improves by >= 5% relative on full coverage
or it materially improves economically important high-risk regimes.
```

If price improves only on a sparse regime, label it as conditional/regime-only, not default.

## Required questions to answer

P0054U must answer:

```text
1. Can full P0054R-compatible SE3 spot-price forecast coverage be created safely?
2. Does raw predicted spot price improve SE3 consumption forecasting on full coverage?
3. Do price shape/regime/spike/ramp features improve results?
4. Do price-temperature or price-load interaction features help?
5. Is there a conditional price-aware regime where price helps even if it hurts globally?
6. Should spot-price forecast remain excluded from default SE3 consumption model?
7. Is any price-feature approach worth carrying into the market emulator stack?
```

## Runtime policy

Codex must:

```text
run Phase 1 first and STOP if full safe coverage cannot be produced
run P0 reproduction gate before price families
run price families serially
checkpoint after each family
not discard completed families if later optional branches fail
prefer M1 full family test before optional M2/M3 expansion
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054U/CHANGELOG.md
requirements/package-runs/P0054U/review.md
requirements/package-runs/P0054U/design.md
requirements/package-runs/P0054U/functions.md
requirements/package-runs/P0054U/labb-label.md
requirements/package-runs/P0054U/p0054t3-price-coverage-review.md
requirements/package-runs/P0054U/target-source-contract.md
requirements/package-runs/P0054U/split-policy-applied.md
requirements/package-runs/P0054U/price-forecast-source-contract.md
requirements/package-runs/P0054U/price-forecast-log-schema.md
requirements/package-runs/P0054U/price-forecast-log-coverage.md
requirements/package-runs/P0054U/price-forecast-safety-review.md
requirements/package-runs/P0054U/baseline-reproduction-gate.md
requirements/package-runs/P0054U/dataset-contract.md
requirements/package-runs/P0054U/feature-families.md
requirements/package-runs/P0054U/price-feature-family-results.md
requirements/package-runs/P0054U/dayahead-results.md
requirements/package-runs/P0054U/full-36h-results.md
requirements/package-runs/P0054U/daily-energy-error-results.md
requirements/package-runs/P0054U/regime-results.md
requirements/package-runs/P0054U/conditional-price-branch-results.md if run
requirements/package-runs/P0054U/feature-importance.md if run
requirements/package-runs/P0054U/leakage-review.md
requirements/package-runs/P0054U/interpretation.md
requirements/package-runs/P0054U/what-we-learned.md
requirements/package-runs/P0054U/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
price-feature-family-results.csv
regime-deltas.csv
feature-importance.csv
price-forecast-coverage-summary.json
```

Do not commit model binaries, large raw datasets, full prediction dumps, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054T3/CHANGELOG.md
requirements/package-runs/P0054T3/price-ablation-results.md
requirements/package-runs/P0054T3/price-coverage-policy.md
requirements/package-runs/P0054T3/baseline-reproduction-gate.md
requirements/package-runs/P0054S/model-comparison.md
requirements/package-runs/P0054S/leakage-review.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/model-training-evidence.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054T4/** if available
src/mac/** relevant P0054R/P0054L2/P0054S/P0054T3 scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Files allowed to change

```text
requirements/packages/P0054U-labb-full-coverage-price-feature-ablation-se3-consumption.md
requirements/package-runs/P0054U/**
src/mac/** narrowly scoped full-coverage price forecast and ablation code if needed
tests/mac/** narrowly scoped tests for price forecast safety/full coverage/feature-family leakage if code changes are made
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
No future actual spot price as feature.
No future actual load/production/flow/A61 features.
No holdout fitting or selection.
No partial-coverage price result presented as full-coverage result.
No train+holdout noisy weather as primary price-ablation setup.
No broad refactor unrelated to P0054U.
No large raw data/model/prediction artifacts.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054T3 price coverage issue reviewed
full P0054R-compatible price forecast coverage created or STOP reason documented
P0054R/P0054T3 no-price baseline reproduced
corrected ENTSO-E target used
old physical_balance target not used
price features derived only from forecast-safe predicted price rows
no future actual spot/load/production/flow/A61 columns in features
regime thresholds learned only from train_fit/internal validation
same full coverage used for P0 and price-family comparisons
no holdout tuning or selection
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- full safe P0054R-compatible price forecast coverage is created or verified.
- P0 no-price baseline reproduction gate passes.
- at least P1 raw, P2 shape, P3 regime and P4 spike/ramp families are evaluated for M1.
- price deltas are computed on identical full coverage.
- leakage review passes.
```

WARN is acceptable if:

```text
- optional P5 interactions or P6 conditional branch are skipped due to runtime.
- M2/M3 expansion is partial after M1 completes.
- feature importance cannot be computed cheaply.
```

STOP if:

```text
- full safe price forecast coverage cannot be produced.
- no-price baseline reproduction gate fails.
- partial price coverage is reused as if it were full coverage.
- future actual price/load leakage is found.
- holdout is used for fitting/selection.
- device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
full price forecast coverage status
price forecast source/log/table used
baseline reproduction result
price feature families run
best broad MAE result
best daily energy result
best regime-specific result
price family deltas vs no-price
whether price should be default, conditional-only, or excluded
whether any price approach is worth carrying into emulator stack
leakage review result
commands/tests run
files changed
confirmation no old target/flow target/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
```

## Completion notes

To be filled after implementation.
