# Package P0054V: LABB complete spotprice value test for SE3 consumption

## Status

stopped

## Package order

P0054V

## Label

```text
LABB
```

This is local research work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Run a complete local test of whether SE3 spot-price forecasts improve SE3 consumption forecasts.

Earlier tests showed that simple price on/off worsened the SE3 consumption forecast, but the price branch had narrower coverage than the no-price branch. P0054V must remove that ambiguity by first creating full P0054R-compatible spot-price forecast features, then testing richer price feature families on identical coverage.

The goal is to make a final method decision for SE3 consumption:

```text
default price feature
conditional/regime-only price feature
exclude price from consumption model
```

Even if price is excluded from consumption, P0054V should say whether price features remain useful for later market-emulator layers.

## Prior baseline

Use the corrected SE3 consumption baseline from P0054R/P0054T3:

```text
target = entsoe_consumption_area_hourly_v1.consumption_mw
area = SE3
model = HorizonBiasCorrected_WeightedEnsemble_no_price
DayAhead hourly MAE ≈ 253.7006 MW ≈ 2.6388%
full_36h MAE ≈ 243.6767 MW
daily energy error ≈ 4 381 MWh ≈ 1.9334%
```

Also reference P0054T4 if available:

```text
clean training + inference-only ±2°C weather noise
DayAhead hourly MAE ≈ 258.91 MW ≈ 2.69%
```

## Required target source

Use only:

```text
entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
source_type = actual_total_load
```

Do not use old physical_balance consumption or cross-border flow data as the target.

## Split policy

Use the P0054R split:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

All fitting, threshold selection, ensemble weights and correction layers must be learned inside train_fit only. Holdout is final evaluation only.

## Phase 0: Baseline gates

Before any price experiment, reproduce the no-price baseline:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
DayAhead hourly MAE ≈ 253.7006 MW
acceptable delta <= 1.0 MW
```

STOP if the baseline gate fails.

## Phase 1: Full-coverage price forecast source

Create or verify a forecast-safe SE3 price forecast source covering the full P0054R consumption contract:

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
P0054S/P0054L2-equivalent local price model, trained only on train_fit-safe price history and applied to all P0054R origins/horizons
```

If a durable local log/table/view is created, use:

```text
advanced_spotprice_forecast_log_p0054v_se3_full_coverage_v1
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

STOP if full forecast-safe price coverage cannot be created. Do not present a partial-coverage price result as final.

## Phase 2: Price feature families

Evaluate these feature families on identical full coverage.

### P0: no price

No price features. This is the baseline.

### P1: raw price

```text
predicted_spot_price_se3
```

### P2: path shape

Examples:

```text
0_24h_mean
24_36h_mean
0_36h_mean
daily_min
daily_max
daily_spread
peak_offpeak_spread
hour_rank_in_day
hour_rank_in_36h_path
peak_hour_indicator
offpeak_indicator
```

### P3: price regimes

Examples:

```text
high_price_flag
low_price_flag
negative_or_very_low_flag
top_quartile_flag
bottom_quartile_flag
volatility_regime
daily_spread_regime
```

Thresholds must be learned from train_fit/internal validation only.

### P4: spike and ramp

Examples:

```text
spike_risk_flag
ramp_from_previous_horizon
abs_ramp_from_previous_horizon
morning_ramp
evening_ramp
large_ramp_flag
```

### P5: interactions, optional

Examples:

```text
price with temperature
price with apparent temperature
price with hour
price with weekday/weekend
price with holiday
price with cold regime
price with high-load-lag regime
```

### P6: conditional branch, optional

Test whether price is useful only in selected regimes:

```text
normal regime: no-price model
price-sensitive regime: price-aware correction or price-aware model
```

The rule must be learned inside train_fit only.

## Models

Minimum required:

```text
M1 = HorizonBiasCorrected_WeightedEnsemble
```

Run if practical:

```text
M3 = XGBoost
M2 = WeightedEnsemble
```

Priority is complete M1 evidence before broader model search.

## Weather policy

Primary P0054V uses clean weather proxy to isolate price effect:

```text
weather_actual_as_forecast_proxy
```

Optional: if a price family is promising, repeat it under the P0054T4 inference-only ±2°C weather-noise protocol.

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

## Decision thresholds

Price may be a default consumption feature only if:

```text
DayAhead hourly MAE improves by >= 2% relative on identical full coverage
and full_36h MAE does not worsen by more than 1%
and daily energy error does not worsen by more than 1%
```

Price may be conditional/regime-only if:

```text
a high-risk or high-price regime improves by >= 10%
and broad DayAhead hourly MAE worsens by <= 1%
```

Otherwise exclude price from the default SE3 consumption model.

## Required questions

P0054V must answer:

```text
1. Could full P0054R-compatible price forecast coverage be created safely?
2. Does raw predicted spot price help?
3. Do path-shape features help?
4. Do price-regime features help?
5. Do spike/ramp features help?
6. Do interactions help?
7. Is a conditional price branch useful?
8. Should price be default, conditional-only, or excluded for SE3 consumption?
9. Should price still be carried into later emulator layers?
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054V/CHANGELOG.md
requirements/package-runs/P0054V/review.md
requirements/package-runs/P0054V/design.md
requirements/package-runs/P0054V/functions.md
requirements/package-runs/P0054V/labb-label.md
requirements/package-runs/P0054V/prior-evidence-summary.md
requirements/package-runs/P0054V/target-source-contract.md
requirements/package-runs/P0054V/split-policy-applied.md
requirements/package-runs/P0054V/baseline-reproduction-gate.md
requirements/package-runs/P0054V/price-forecast-source-contract.md
requirements/package-runs/P0054V/price-forecast-log-schema.md
requirements/package-runs/P0054V/price-forecast-log-coverage.md
requirements/package-runs/P0054V/price-forecast-safety-review.md
requirements/package-runs/P0054V/dataset-contract.md
requirements/package-runs/P0054V/feature-families.md
requirements/package-runs/P0054V/price-feature-family-results.md
requirements/package-runs/P0054V/dayahead-results.md
requirements/package-runs/P0054V/full-36h-results.md
requirements/package-runs/P0054V/daily-energy-error-results.md
requirements/package-runs/P0054V/regime-results.md
requirements/package-runs/P0054V/conditional-price-branch-results.md if run
requirements/package-runs/P0054V/feature-importance.md if run
requirements/package-runs/P0054V/leakage-review.md
requirements/package-runs/P0054V/decision.md
requirements/package-runs/P0054V/emulator-stack-recommendation.md
requirements/package-runs/P0054V/interpretation.md
requirements/package-runs/P0054V/what-we-learned.md
requirements/package-runs/P0054V/next-package-recommendation.md
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
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054T3/price-ablation-results.md
requirements/package-runs/P0054T3/price-coverage-policy.md
requirements/package-runs/P0054T3/baseline-reproduction-gate.md
requirements/package-runs/P0054T4/inference-noise-summary.json if available
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
requirements/packages/P0054V-labb-complete-spotprice-value-test-se3-consumption.md
requirements/package-runs/P0054V/**
src/mac/** narrowly scoped full-coverage price forecast and price-feature-family ablation code if needed
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
No external live data calls.
No old target.
No flow data as target.
No future actual price/load/production/flow features.
No holdout fitting or selection.
No partial-coverage price result presented as full-coverage.
No broad refactor unrelated to P0054V.
No large artifacts.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
no-price baseline reproduced
full P0054R-compatible price forecast coverage created or STOP reason documented
corrected ENTSO-E target used
old target not used
price features derived only from forecast-safe predicted price rows
no future actual price/load/production/flow features in feature matrix
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
- baseline gate passes.
- full safe P0054R-compatible price forecast coverage is created or verified.
- P1 raw, P2 shape, P3 regime and P4 spike/ramp families are evaluated for M1.
- price deltas are computed on identical full coverage.
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
- full safe price forecast coverage cannot be produced.
- no-price baseline gate fails.
- partial price coverage is reused as final full-coverage evidence.
- future actual price/load leakage is found.
- holdout is used for fitting or selection.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
baseline reproduction result
full price forecast coverage status
price forecast source/log/table used
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

Stopped as `STOP`.

Required baseline gate failed before a valid P0054V price-family result could be accepted:

```text
required baseline: HorizonBiasCorrected_WeightedEnsemble_no_price
package target DayAhead MAE: approx 253.70062353819162 MW
package tolerance: <= 1.0 MW
current repeated reproduction DayAhead MAE: 252.4272878651775 MW
absolute delta: 1.2733356730141168 MW
```

Repeated gate checks:

```text
run 0: passed=false, DayAhead MAE=252.42728786517762, absolute_delta_MW=1.273335673014003
run 1: passed=false, DayAhead MAE=252.42728786517756, absolute_delta_MW=1.27333567301406
run 2: passed=false, DayAhead MAE=252.4272878651774, absolute_delta_MW=1.2733356730142305
```

The row contract still matched prior P0054T4 shape:

```text
source_rows=35125
direct_rows=52173
path_rows=52173
train_fit_rows=38985
holdout_rows=13188
internal_train_rows=35675
internal_validation_rows=3310
```

No P0054V price-family ablation is reported as valid. A draft local implementation proved that full holdout price forecast coverage can be built without actual holdout target-window spot (`13188/13188` holdout rows), but it was removed from final commit scope because the package STOP gate occurred before a verified package result.

No external API, Shelly, Home Assistant, device/runtime write, production deployment, old target, flow target, A61 input, Nord Pool/workplace integration or large artifact was used.

Recommended follow-up:

```text
Create P0054W to investigate the P0054R/P0054T4 baseline reproducibility drift
or explicitly update the P0054V baseline gate before rerunning the full price-value test.
```
