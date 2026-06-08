# Package P0056E: LABB north area model variant test

## Status

planned

## Package order

P0056E

## Label

```text
LABB
```

## Purpose

Run a targeted model-variant test for the northern Swedish price areas, especially SE1 and SE2, because P0056C showed high percentage error and P0056D improved weather proxies only marginally.

The goal is to determine whether SE1/SE2 error is primarily:

```text
weather proxy limitation
model family / hyperparameter limitation
feature limitation
load-structure volatility / industrial effects
low-load denominator effect
```

P0056E must test alternative model and feature variants for SE1 and SE2 and compare against P0056C/P0056D baselines.

## Areas in scope

Primary:

```text
SE1
SE2
```

Optional reference/control areas if runtime allows:

```text
SE3
NO3
NO4
```

Do not change all 18 areas in this package.

## Baselines

Use latest committed baselines:

### P0056C original multi-area result

```text
requirements/package-runs/P0056C/area-results.md
```

Baseline values:

```text
SE1 DayAhead MAE 126.498 MW, MAE percent mean 10.031%, full36 MAE 124.609 MW
SE2 DayAhead MAE 209.519 MW, MAE percent mean 12.120%, full36 MAE 201.827 MW
```

### P0056D improved Open-Meteo weather result

```text
requirements/package-runs/P0056D/area-results.md
requirements/package-runs/P0056D/comparison-vs-p0056c.md
```

Baseline values:

```text
SE1 DayAhead MAE 126.028 MW, MAE percent mean 9.994%, full36 MAE 124.361 MW
SE2 DayAhead MAE 206.598 MW, MAE percent mean 11.951%, full36 MAE 197.775 MW
```

For SE2, P0056D is candidate weather default. For SE1, P0056B remains default unless P0056E shows otherwise.

## Input data

Use:

```text
area_consumption_hourly_v1
area_weather_features_hourly_v1
```

For SE2, include both weather options if available:

```text
P0056B weather proxy
P0056D Open-Meteo revised proxy
```

For SE1, include both weather options if available, even though P0056D did not beat threshold.

No spot price, no flows/exchanges/net positions, no A61/capacity, no old physical_balance target.

## Split policy

Use the established split:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation for model selection, horizon-bias correction, model weighting and hyperparameter choice must remain inside train_fit only.

No holdout row may be used for fitting, selection, weighting or correction.

## Model variants to test

At minimum test these variants for SE1 and SE2:

### V0 baseline reproduction

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

Use current default weather for each area.

### V1 P0056D weather with current model

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

Use P0056D weather where available.

### V2 robust direct WeightedEnsemble without horizon correction

```text
WeightedEnsemble_no_price
```

Purpose: check if horizon-bias correction overfits volatile northern areas.

### V3 LightGBM-focused

```text
LightGBM_no_price
```

Use tuned or current hyperparameters. Document exact values.

### V4 XGBoost-focused

```text
XGBoost_no_price
```

Use tuned or current hyperparameters. Document exact values.

### V5 HGB-focused / robust small-data model

```text
HGB_no_price
```

Use tuned or current hyperparameters. Document exact values.

### V6 load-lag-heavy model

A variant that emphasizes autoregressive load history:

```text
recent load lags
same-hour yesterday
same-hour same-week
rolling 24h/48h/168h statistics
calendar
minimal weather
```

Purpose: test whether SE1/SE2 are driven more by persistence/industrial structure than by weather.

### V7 weather-heavy model

A variant that emphasizes weather response:

```text
area weather proxy
heating degree features
rolling temperature
calendar
load lags
```

Purpose: test whether improved weather can help when feature engineering is stronger.

### V8 regime-aware or segmented correction

If practical, test a simple correction by regime:

```text
cold/high-load
low-load/summer
weekday/weekend
ramp regime
```

The correction must be learned only inside train_fit/internal validation.

## Optional variants

If runtime allows:

```text
quantile/Huber/robust loss variant
outlier-trimmed training variant
industrial-ramp exclusion or separate high-volatility regime feature
month-specific bias correction
area-specific horizon-bias correction with stronger regularization
```

## Feature engineering requirements

P0056E must explicitly compare feature groups:

```text
calendar_only_plus_lags
weather_plus_lags
lag_heavy
weather_heavy
current_best_feature_set
```

For each variant document:

```text
feature_count
feature_groups
weather_proxy_version
model_family
hyperparameters
training_rows
holdout_rows
```

## Metrics

For each area and variant report:

```text
DayAhead hourly MAE
DayAhead RMSE
DayAhead bias
MAE percent of mean actual
MAE percent of median actual
absolute daily energy error MWh
signed daily energy error MWh
daily energy error percent of actual
full36 MAE
full36 RMSE
full36 bias
p90 absolute error
p95 absolute error
MAE_0_6h
MAE_0_12h
MAE_0_24h
MAE_24_36h
weekday/weekend split
cold/high-load/ramp regimes
```

Comparison metrics:

```text
delta_vs_P0056C_DayAhead_MW
delta_vs_P0056C_DayAhead_percent
delta_vs_P0056D_DayAhead_MW if applicable
delta_vs_P0056D_DayAhead_percent if applicable
delta_vs_P0056C_full36_percent
delta_vs_P0056D_full36_percent if applicable
```

## Decision rules

A variant is candidate default for an area if it improves the best current baseline for that area by:

```text
DayAhead MAE >= 2% relative
or full36 MAE >= 2% relative without worsening DayAhead
or daily energy error >= 5% relative without worsening DayAhead by more than 1%
```

If no variant clears threshold, keep current default and document what failed.

## Runtime policy

This package may run many variants but only for a few areas. It should print and persist progress per area and variant.

Required progress format:

```text
[P0056E progress] area=SE1 variant=V0 phase=train status=start timestamp=...
[P0056E progress] area=SE1 variant=V0 phase=train status=done elapsed_seconds=...
[P0056E progress] area=SE1 variant=V0 phase=test status=done elapsed_seconds=...
```

Create:

```text
requirements/package-runs/P0056E/progress-log.md
requirements/package-runs/P0056E/variant-job-status.md
```

If interrupted, return WARN with resume instructions and completed variants.

## Required evidence files

Create:

```text
requirements/package-runs/P0056E/CHANGELOG.md
requirements/package-runs/P0056E/review.md
requirements/package-runs/P0056E/design.md
requirements/package-runs/P0056E/functions.md
requirements/package-runs/P0056E/labb-label.md
requirements/package-runs/P0056E/baseline-review.md
requirements/package-runs/P0056E/input-source-contract.md
requirements/package-runs/P0056E/split-policy-applied.md
requirements/package-runs/P0056E/model-variant-contract.md
requirements/package-runs/P0056E/feature-group-comparison.md
requirements/package-runs/P0056E/progress-log.md
requirements/package-runs/P0056E/variant-job-status.md
requirements/package-runs/P0056E/area-variant-results.md
requirements/package-runs/P0056E/dayahead-results.md
requirements/package-runs/P0056E/full-36h-results.md
requirements/package-runs/P0056E/daily-energy-error-results.md
requirements/package-runs/P0056E/regime-results.md
requirements/package-runs/P0056E/comparison-vs-baseline.md
requirements/package-runs/P0056E/leakage-review.md
requirements/package-runs/P0056E/decision.md
requirements/package-runs/P0056E/what-we-learned.md
requirements/package-runs/P0056E/next-package-recommendation.md
```

Optional compact evidence:

```text
area-variant-results.csv
comparison-vs-baseline.csv
metrics-summary.json
variant-job-status.csv
```

Do not commit full prediction dumps, model binaries, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056C/area-results.md
requirements/package-runs/P0056C/cross-area-summary.md
requirements/package-runs/P0056D/area-results.md
requirements/package-runs/P0056D/comparison-vs-p0056c.md
requirements/package-runs/P0056D/decision.md
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/model-training-evidence.md
requirements/package-runs/P0054T4/inference-noise-summary.json
src/mac/** forecast/model scripts
tests/mac/** relevant tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056E-labb-north-area-model-variant-test.md
requirements/package-runs/P0056E/**
src/mac/** narrowly scoped SE1/SE2 model-variant testing code if needed
tests/mac/** narrowly scoped tests for split, leakage, feature groups, progress/checkpointing if code is added
docs/functions/mac/** if durable docs need updating
local DB metrics tables if repo owns them and only for P0056E outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No external live data integration.
No spot price features.
No old physical_balance target.
No flow/exchange/A61/capacity features.
No future actual load leakage.
No holdout fitting or selection.
No large prediction/model artifacts committed.
```

## Verification

Codex must define final commands in design.md and run equivalent checks for:

```text
P0056C and P0056D baselines loaded
SE1/SE2 inputs available
split policy applied
all planned variants run or documented fallback
no forbidden features
no holdout fitting/selection
leakage review passes
comparison against baseline computed
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP

PASS requires:

```text
SE1 and SE2 variants are tested
metrics are reported for all planned variants or documented fallbacks
comparison against current baseline is complete
candidate default decision per area is clear
leakage review passes
```

WARN is acceptable if:

```text
some optional variants are skipped
one variant fails but enough variants complete for decision
no variant beats baseline
```

STOP if:

```text
inputs are missing
split/leakage safety cannot be verified
most variants fail to train/test
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
variants tested
best SE1 variant and delta vs baseline
best SE2 variant and delta vs baseline
whether any variant becomes candidate default
runtime/progress summary
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

Completed as `WARN` on 2026-06-08.

- Ran 18 primary SE1/SE2 variants: V0..V8 for both areas.
- Failed/skipped variants: 0.
- Best SE1 variant by DayAhead MAE: V2 `WeightedEnsemble_no_price` with P0056D weather, 125.220 MW DayAhead MAE. It improved current P0056D baseline by about 0.64%, below the 2% candidate threshold.
- Best SE2 variant by DayAhead MAE: V8 regime-corrected current model with P0056D weather, 206.521 MW DayAhead MAE. It improved current P0056D baseline by about 0.04%, below the 2% candidate threshold.
- Decision: keep current default for SE1 and SE2. P0056D remains the current best LABB baseline for both, and SE2 remains the earlier P0056D candidate vs P0056C.
- No devices, runtime changes, production activation, external live data, spot price, flow/exchange/A61/capacity or future actual load leakage.
