# Package P0056F: LABB weather feature ablation efficiency

## Status

planned

## Package order

P0056F

## Label

```text
LABB
```

## Purpose

Test whether the current weather feature set contains too many signals and whether model performance peaks with a smaller, cleaner set.

The hypothesis is:

```text
For SE1/SE2, 13 weather signals may add noise/overfit.
A simpler weather stack may perform better.
```

P0056F must start with temperature only, then add weather signals one by one in likely usefulness order, retrain/test, and identify the peak-efficiency weather feature set.

## Areas in scope

Primary:

```text
SE1
SE2
```

Optional control if runtime allows:

```text
SE3
```

Do not run all 18 areas in this package.

## Baselines

Compare against latest committed baselines:

```text
P0056C original multi-area forecast
P0056D Open-Meteo weather retune
P0056E north model variants
```

Use P0056E best-by-area as current benchmark:

```text
SE1 best current observed: V2 WeightedEnsemble_no_price with P0056D weather
SE2 best current observed: V8 RegimeCorrected or V1/P0056D current model, nearly tied
```

Also report comparison against P0056C/P0056D values explicitly.

## Input data

Use:

```text
area_consumption_hourly_v1
P0056D weather features for SE1/SE2 where available
P0056B weather features only as fallback/comparison
```

No spot price, no flows, no exchange, no A61/capacity, no old physical_balance.

## Split policy

Use established split:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

All feature-set selection, model weighting, bias correction and peak-efficiency selection must be based only on train_fit/internal validation.

Holdout may only be used for final reporting of preselected variants.

If the package evaluates all variants on holdout, label the result as LABB exploratory and do not claim production selection without a future nested validation package.

## Fixed non-weather features

Keep calendar and load-history features fixed across all ablation variants:

```text
calendar/time features
holiday features
area load lags
area rolling load statistics
area ramp features
```

Only vary the weather feature subset.

This keeps the test focused on marginal value of weather signals.

## Weather signal order

Test cumulative weather feature stacks in this order:

### W0 no weather

```text
calendar + load-history only
```

Purpose: baseline to measure whether weather helps at all.

### W1 temperature only

```text
weather_proxy_temperature_2m_area
```

### W2 temperature + heating degree

```text
weather_proxy_temperature_2m_area
weather_proxy_heating_degree_hours_area
```

### W3 add temperature rolling mean

```text
weather_proxy_temperature_roll_mean_24h_area
```

### W4 add temperature normal/delta

```text
weather_proxy_train_normal_temperature_2m_area
weather_proxy_temperature_delta_from_train_normal_area
```

### W5 add cold spell flag

```text
weather_proxy_cold_spell_flag_area
```

### W6 add apparent temperature

```text
weather_proxy_apparent_temperature_area
```

### W7 add wind speed

```text
weather_proxy_wind_speed_area
```

### W8 add snow depth

```text
weather_proxy_snow_depth_area
```

### W9 add precipitation

```text
weather_proxy_precipitation_area
```

### W10 add humidity

```text
weather_proxy_humidity_area
```

### W11 add cloud cover

```text
weather_proxy_cloud_cover_area
```

### W12 add cooling degree

```text
weather_proxy_cooling_degree_hours_area
```

The ordering is intentionally based on likely usefulness for Nordic consumption:

```text
temperature / heating demand first
thermal inertia next
anomaly/cold spell next
apparent/wind/snow next
precip/humidity/cloud/cooling last
```

## Model methods to use

Run at least one stable model across all W0-W12 stacks:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

Also run the best P0056E area-specific model if different and runtime allows:

```text
SE1: WeightedEnsemble_no_price
SE2: HorizonBiasCorrected_WeightedEnsemble_no_price or RegimeCorrected variant
```

The main comparison should isolate weather feature count, so use the same model method across stacks.

## Metrics

For each area, method and weather stack report:

```text
weather_stack_id
weather_feature_count
weather_features_included
DayAhead MAE
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
cold/high-load/ramp regimes if available
```

Efficiency metrics:

```text
delta_MAE_vs_previous_stack
delta_MAE_percent_vs_previous_stack
delta_MAE_vs_W0
delta_MAE_vs_current_best
feature_count
marginal_gain_per_added_feature
```

## Peak-efficiency decision

For each area, identify:

```text
best_holdout_weather_stack
best_internal_validation_weather_stack if available
smallest_stack_within_0.5_percent_of_best
first_stack_where_marginal_gain_turns_negative
first_stack_where marginal_gain < 0.2 percent
```

Candidate default weather stack if:

```text
improves current best baseline by >= 1 percent DayAhead MAE
or keeps DayAhead within 0.5 percent while reducing weather feature count by >= 50 percent
or improves full36 by >= 1 percent without worsening DayAhead
```

If no stack improves, recommend keeping current feature set or simpler W2/W3 only if nearly equivalent and more robust.

## Required evidence files

Create:

```text
requirements/package-runs/P0056F/CHANGELOG.md
requirements/package-runs/P0056F/review.md
requirements/package-runs/P0056F/design.md
requirements/package-runs/P0056F/functions.md
requirements/package-runs/P0056F/labb-label.md
requirements/package-runs/P0056F/baseline-review.md
requirements/package-runs/P0056F/input-source-contract.md
requirements/package-runs/P0056F/split-policy-applied.md
requirements/package-runs/P0056F/weather-signal-order.md
requirements/package-runs/P0056F/weather-stack-contract.md
requirements/package-runs/P0056F/feature-ablation-results.md
requirements/package-runs/P0056F/area-results.md
requirements/package-runs/P0056F/marginal-gain-analysis.md
requirements/package-runs/P0056F/peak-efficiency-decision.md
requirements/package-runs/P0056F/comparison-vs-baseline.md
requirements/package-runs/P0056F/leakage-review.md
requirements/package-runs/P0056F/what-we-learned.md
requirements/package-runs/P0056F/next-package-recommendation.md
```

Optional compact evidence:

```text
feature-ablation-results.csv
marginal-gain-analysis.csv
metrics-summary.json
```

Do not commit full prediction dumps, model binaries, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056E/feature-group-comparison.md
requirements/package-runs/P0056E/area-variant-results.md
requirements/package-runs/P0056E/comparison-vs-baseline.md
requirements/package-runs/P0056E/decision.md
requirements/package-runs/P0056D/area-results.md
requirements/package-runs/P0056D/comparison-vs-p0056c.md
requirements/package-runs/P0056C/area-results.md
src/mac/** forecast/model/feature scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056F-labb-weather-feature-ablation-efficiency.md
requirements/package-runs/P0056F/**
src/mac/** narrowly scoped feature-stack/model evaluation code if needed
tests/mac/** narrowly scoped tests for feature stack selection/leakage if code is added
local DB metrics tables if repo owns them and only for P0056F outputs
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
No holdout fitting or selection for production claims.
No large prediction/model artifacts committed.
```

## Verification

Codex must define final commands in design.md and run equivalent checks for:

```text
weather stacks W0-W12 constructed correctly
fixed non-weather features identical across stacks
SE1/SE2 inputs available
split policy applied
no forbidden features
no holdout fitting/selection unless LABB exploratory label is explicit
marginal gain analysis computed
peak efficiency decision produced
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP

PASS requires:

```text
W0-W12 tested for SE1 and SE2
metrics reported for each stack
marginal value of each added weather signal is documented
peak-efficiency stack identified per area
leakage review passes
```

WARN is acceptable if:

```text
one optional model method is skipped
holdout evaluation is exploratory and clearly labeled
no stack improves baseline
some optional weather variables are missing and documented
```

STOP if:

```text
weather feature stacks cannot be constructed
inputs are missing
split/leakage safety cannot be verified
most stacks fail to train/test
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
weather stacks tested
best SE1 stack and delta vs baseline
best SE2 stack and delta vs baseline
peak-efficiency stack per area
whether fewer weather features perform better
recommended default weather feature set
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

To be filled after implementation.
