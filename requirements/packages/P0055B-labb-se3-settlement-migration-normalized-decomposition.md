# Package P0055B: LABB SE3 settlement-migration normalized decomposition

## Status

planned

## Package order

P0055B

## Label

```text
LABB
```

This package is local research work under P0054A/P0055. It is not a G2-KANDIDAT evaluation.

## Purpose

Test the operator hypothesis that P0055A decomposition failed because the profiled/load-profile and residual components are not stable physical load segments. They are affected by one-way settlement/product migration:

```text
customers move from residual/metered-non-profiled bucket into profiled/load-profile clusters
or, more generally, administrative/product definitions shift volume between buckets
```

P0055B must estimate a simple month-by-month allocation/migration model and create normalized historical component series as if the latest allocation/fördelningsnyckel had existed throughout history.

Then it must forecast:

```text
1. direct SE3 total, current best method
2. normalized profiled/load-profile clusters
3. normalized residual
4. aggregated normalized decomposition total
5. optional reconciliation against direct SE3
```

The core question:

```text
Does removing settlement/product migration from the component history make decomposition forecasting better than direct SE3?
```

## Operator hypothesis

Important assumptions:

```text
- Total SE3 collective load is mostly physical demand: weather, calendar, behavior, economy.
- Profiled/load-profile cluster shares change partly because customer/product allocation changes.
- Residual changes in the opposite direction as customers/products move into cluster/profile buckets.
- Direction is mostly one-way over the historical period.
- If inferred allocation keys move back and forth, the migration signal is not safely readable.
```

P0055B must explicitly test monotonicity / one-way behavior.

## Required input tables/views

Use the outputs from P0054Y2/P0054Z/P0055A:

```text
entsoe_consumption_area_hourly_v1
se3_profiled_mga_cluster_hourly_v1
se3_consumption_metered_residual_hourly_v1
se3_consumption_profiled_residual_decomposition_hourly_v1
se3_climate_zone_weather_hourly_v1
```

Also inspect:

```text
requirements/package-runs/P0055A/comparison-vs-direct.md
requirements/package-runs/P0055A/component-results.md
requirements/package-runs/P0055A/error-contribution-analysis.md
requirements/package-runs/P0054Y2/decomposition-validation.md
requirements/package-runs/P0054Y2/cluster-segment-dictionary.md
```

## Conceptual model

Let:

```text
T_t = actual SE3 total load
C_i,t = observed profiled/load-profile cluster i
R_t = observed residual = T_t - sum_i C_i,t
S_i,t = C_i,t / T_t
S_R,t = R_t / T_t
```

The observed shares are contaminated by settlement/product migration.

P0055B must estimate smooth/monthly allocation shares:

```text
A_i,m = monthly allocation share for cluster i
A_R,m = monthly allocation share for residual
sum_i A_i,m + A_R,m = 1
```

Then construct normalized historical components using a selected reference allocation, preferably latest stable allocation:

```text
C_i_norm,t = T_t * A_i,reference * shape_i,t
R_norm,t = T_t * A_R,reference * shape_R,t
```

The exact formula may be adapted, but must preserve:

```text
sum_i C_i_norm,t + R_norm,t = T_t
```

and must remove month-to-month migration trend as much as possible without using holdout information for fitting.

## Acceptable simplification

A simple linear/monthly model is preferred over complex ML.

Allowed approaches:

```text
1. Monthly linear trend in shares per component.
2. Monotonic constrained smoothing of component shares.
3. Piecewise monthly trend with breakpoints learned only inside train_fit.
4. Latest train_fit allocation held fixed historically.
5. Latest pre-holdout allocation held fixed for holdout simulation, if forecast-safe.
```

Do not overfit share migration with flexible models.

## Monotonicity / one-way migration test

For each component and aggregate profiled/residual share, report:

```text
monthly_share_start
monthly_share_end
monthly_share_slope
number_of_direction_reversals
max_backtrack
monotonicity_score
is_one_way_readable
```

Required aggregate tests:

```text
profiled_total_share_t = sum_i C_i,t / T_t
residual_share_t = R_t / T_t
```

Expected if hypothesis is correct:

```text
profiled_total_share should trend in one primary direction
residual_share should trend in the opposite direction
```

If the shares go back and forth materially, return WARN and label allocation normalization as unreliable.

## Forecast-safety rules

No holdout leakage.

Critical requirements:

```text
- Migration/share model parameters must be fit only on train_fit or internal validation inside train_fit.
- Reference allocation for holdout forecasts must be known by forecast_origin.
- Do not use final holdout share as historical reference unless clearly labeled as oracle/sensitivity-only.
- Do not use future actual residual/cluster/SE3 target as feature.
```

Primary result must be forecast-safe.

Optional sensitivity:

```text
oracle latest-full-history allocation
```

This may be reported only as an upper-bound sensitivity, not as primary result.

## Split policy

Use P0054/P0055 split:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation for ensemble weights, horizon-bias correction, model selection, migration reference choice and reconciliation weights must be strictly inside train_fit.

Prefer:

```text
internal_validation_start = 2025-03-01T00:00:00Z
```

## Series to create

Create and document:

```text
se3_component_monthly_allocation_v1
se3_profiled_cluster_normalized_hourly_v1
se3_residual_normalized_hourly_v1
se3_normalized_decomposition_hourly_v1
```

If DB writes are not practical, create compact evidence files, but do not commit full time-series dumps.

### Monthly allocation table minimum columns

```text
month_start_utc
component_id
component_type
observed_share
smoothed_share
reference_share
share_slope
monotonicity_flags
generated_by_package = P0055B
```

### Normalized hourly table minimum columns

```text
timestamp_utc
component_id
component_type
observed_consumption_mw
normalized_consumption_mw
normalization_method
reference_month_or_window
share_used
is_forecast_safe_reference
generated_by_package = P0055B
```

## Forecast method

Use the latest best SE3 method as default:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

Run on:

```text
1. direct SE3 total
2. normalized non-zero profiled clusters
3. normalized residual
```

Allowed features:

```text
calendar/time/holiday/weekend
historical normalized target lags
rolling normalized target statistics
mapped climate-zone weather for cluster components
broad SE3 weather for residual/direct
```

Forbidden features:

```text
spot price
future actual total SE3 consumption
future actual component target
future actual residual
flows/exchanges/A61/capacity
old physical_balance target
holdout-derived migration/reconciliation weights
```

## Forecast use cases

Evaluate both:

```text
DayAhead:
  forecast_origin = 12:00 Europe/Stockholm on D-1
  delivery_day = D 00:00..23:00 Europe/Stockholm

full_36h:
  complete 36-hour path from origin
```

## Required comparisons

Compare at least:

```text
A. Direct SE3 baseline from P0055A/P0054 best method
B. Raw decomposition total from P0055A
C. Normalized decomposition total from P0055B
D. Optional reconciled direct + normalized decomposition
```

Primary total forecast from normalized decomposition must equal sum of normalized component forecasts:

```text
forecast_normalized_decomposition_total = sum(normalized_cluster_forecasts) + normalized_residual_forecast
```

## Metrics

### Share/migration metrics

```text
profiled_total_share_start/end/slope
residual_share_start/end/slope
monthly direction reversal count
monotonicity_score
reference allocation used
share-normalization error
```

### Individual component forecast metrics

```text
component_id
mean_actual_mw
share_of_total
DayAhead MAE
DayAhead RMSE
DayAhead bias
full_36h MAE
full_36h RMSE
MAE_percent_of_component_mean
daily_energy_error_MWh
```

### Total SE3 metrics

For direct, raw decomposition, normalized decomposition and optional reconciled:

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
cold/high-load/ramp regimes
```

### full_36h total metrics

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

## Decision thresholds

Normalized decomposition is better only if it improves direct SE3 by:

```text
DayAhead hourly MAE >= 2% relative
or full_36h MAE >= 2% relative without worsening DayAhead
or daily energy error >= 5% relative without worsening DayAhead by >1%
```

If normalized decomposition improves raw decomposition but not direct SE3, conclusion should be:

```text
normalization helps decomposition but direct remains default
```

If monotonicity fails materially, conclusion should be:

```text
settlement migration not safely readable from current data
```

## Required evidence files

Create:

```text
requirements/package-runs/P0055B/CHANGELOG.md
requirements/package-runs/P0055B/review.md
requirements/package-runs/P0055B/design.md
requirements/package-runs/P0055B/functions.md
requirements/package-runs/P0055B/labb-label.md
requirements/package-runs/P0055B/input-source-contract.md
requirements/package-runs/P0055B/settlement-migration-hypothesis.md
requirements/package-runs/P0055B/monthly-share-analysis.md
requirements/package-runs/P0055B/monotonicity-review.md
requirements/package-runs/P0055B/allocation-normalization-method.md
requirements/package-runs/P0055B/normalized-series-contract.md
requirements/package-runs/P0055B/database-output-evidence.md if DB tables are written
requirements/package-runs/P0055B/split-policy-applied.md
requirements/package-runs/P0055B/model-method-contract.md
requirements/package-runs/P0055B/component-training-evidence.md
requirements/package-runs/P0055B/component-results.md
requirements/package-runs/P0055B/direct-se3-results.md
requirements/package-runs/P0055B/raw-decomposition-reference.md
requirements/package-runs/P0055B/normalized-decomposition-total-results.md
requirements/package-runs/P0055B/reconciled-results.md if run
requirements/package-runs/P0055B/comparison-vs-direct.md
requirements/package-runs/P0055B/error-contribution-analysis.md
requirements/package-runs/P0055B/leakage-review.md
requirements/package-runs/P0055B/interpretation.md
requirements/package-runs/P0055B/what-we-learned.md
requirements/package-runs/P0055B/next-package-recommendation.md
```

Optional compact evidence:

```text
monthly-shares.csv
monotonicity-summary.csv
component-results.csv
total-comparison.csv
metrics-summary.json
```

Do not commit model binaries, large raw time-series dumps, full prediction dumps, virtualenvs or caches.

## Files to inspect

```text
requirements/package-runs/P0055A/CHANGELOG.md
requirements/package-runs/P0055A/comparison-vs-direct.md
requirements/package-runs/P0055A/component-results.md
requirements/package-runs/P0055A/error-contribution-analysis.md
requirements/package-runs/P0054Y2/decomposition-validation.md
requirements/package-runs/P0054Y2/cluster-segment-dictionary.md
requirements/package-runs/P0054Z/climate-zone-validation.md
requirements/package-runs/P0054Z/cluster-weather-mapping.md
src/mac/** relevant decomposition/model scripts
tests/mac/** relevant tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0055B-labb-se3-settlement-migration-normalized-decomposition.md
requirements/package-runs/P0055B/**
src/mac/** narrowly scoped migration-normalization/forecast/evaluation code if needed
tests/mac/** narrowly scoped tests for monotonicity/normalization/aggregation/leakage if code is added
docs/functions/mac/** if durable docs need updating
local database tables if repo owns them and only for P0055B outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No external live data integration.
No credentials or tokens.
No large raw data/model/prediction commits.
No spot price features.
No old physical_balance target.
No flow/exchange/A61/capacity features.
No future actual cluster/residual/SE3 leakage.
No holdout fitting, selection, reconciliation, migration reference or weighting.
No treating residual as observed per-MGA measured data.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0055A failure reviewed
monthly share analysis completed
monotonicity review completed
normalization method documented
normalized series sum to SE3 total historically
forecast-safe allocation reference used
component forecasts generated or fallback documented
normalized decomposition total equals sum(component forecasts)
direct SE3 baseline evaluated
comparison against direct computed
no future actual target/residual/share leakage
no holdout fitting/selection/reconciliation
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- monthly allocation/share analysis is completed.
- monotonicity/one-way migration is assessed.
- forecast-safe normalized component series are created or a clear reason is documented.
- normalized component forecasts and total forecast are evaluated.
- normalized total is compared against direct SE3 and raw decomposition.
- leakage review passes.
```

WARN is acceptable if:

```text
- monotonicity is weak but normalization is still run as sensitivity.
- optional reconciled ensemble is skipped.
- some zero/sparse components use fallback.
- DB writes are skipped but compact evidence exists.
```

STOP if:

```text
- share migration cannot be estimated without holdout leakage.
- normalized series cannot be made to sum to total.
- required P0054Y2/P0054Z/P0055A inputs are missing.
- leakage is found.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
monthly share trend summary
monotonicity result
normalization method
allocation reference used
raw decomposition vs direct summary
normalized decomposition vs direct summary
whether normalization improved raw decomposition
whether normalized decomposition beats direct
residual error contribution after normalization
recommended next package
tests/commands run
files changed
confirmation no spot price/no old target/no flow/A61/no external integration/no large artifacts
```

## Completion notes

To be filled after implementation.
