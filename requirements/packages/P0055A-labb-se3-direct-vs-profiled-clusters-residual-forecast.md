# Package P0055A: LABB SE3 direct vs profiled clusters plus residual forecast

## Status

planned

## Package order

P0055A

## Label

```text
LABB
```

This package is local research work under P0054A/P0055. It is not a G2-KANDIDAT evaluation.

## Purpose

Create all SE3 consumption forecasts according to the latest best method, then test them individually and as an aggregated total forecast.

The key question:

```text
Does decomposing SE3 into profiled/load-profile clusters + residual improve forecast accuracy versus the best direct SE3 forecast?
```

The package must compare:

```text
A. Best direct SE3 forecast
B. Individual profiled/load-profile cluster forecasts
C. Individual metered/non-profiled residual forecast
D. Aggregated decomposition forecast = sum(cluster forecasts) + residual forecast
E. Optional reconciled/ensemble forecast = direct + decomposition, learned only inside train_fit/internal validation
```

## Required baseline context

Current best direct SE3 consumption forecast:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
corrected ENTSO-E SE3 actual total load
calendar + historical load + broad weather proxy
no spot price
```

Relevant prior findings:

```text
P0054T4:
  inference-only ±2°C weather noise stayed around 2.69% DayAhead MAE

P0054V2:
  spotprice features should be excluded from SE3 consumption

P0054Y2:
  created 16 profiled/load-profile cluster series plus SE3 metered/non-profiled residual

P0054Z:
  created SE3 climate-zone weather series plus broad SE3 proxy
```

## Required input tables/views

### Direct SE3 target

Use:

```text
entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
```

### Profiled/load-profile cluster targets

Use P0054Y2 outputs:

```text
se3_profiled_mga_cluster_hourly_v1
```

Expected components:

```text
C11..C44
```

Some clusters may be zero-volume historically. Forecast them only if they have non-zero target history; otherwise create explicit zero forecast with evidence.

### Residual target

Use P0054Y2 residual:

```text
se3_consumption_metered_residual_hourly_v1
component = SE3_RESIDUAL_METERED_NON_PROFILED_UNOBSERVED
```

Residual target is calculated historically:

```text
residual = ENTSO-E SE3 total - sum(profiled/load-profile clusters)
```

Do not treat residual as observed per-MGA measured data.

### Weather features

Use P0054Z:

```text
se3_climate_zone_weather_hourly_v1
```

Mapping:

```text
C1* -> SE3_EAST_COAST_MALARDALEN_STOCKHOLM
C2* -> SE3_WEST_COAST_GOTHENBURG
C3* -> SE3_NORTHERN_INLAND
C4* -> SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
residual -> SE3_BROAD_PROXY by default
SE3 direct -> SE3_BROAD_PROXY
```

## Forecast method

Use the latest best method from SE3 direct work as the default model family:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
```

Apply it to:

```text
1. direct SE3 total
2. each non-zero profiled cluster
3. residual series
```

If a cluster is too sparse/zero-volume, do not force a trained model. Use safe rules:

```text
zero historical volume -> zero forecast
very low/insufficient non-zero history -> simple fallback forecast with WARN
normal volume/history -> full model
```

Required fallback hierarchy:

```text
F0: zero forecast for zero-history clusters
F1: seasonal naive / same-hour same-week if model cannot train safely
F2: simpler WeightedEnsemble if HorizonBiasCorrected model fails
F3: STOP only if target/feature construction is invalid
```

Do not stop the whole package just because one empty cluster exists.

## Feature policy

Allowed features:

```text
calendar/time/holiday/weekend
historical target lags for each component
rolling target statistics for each component
mapped climate-zone weather for each component
broad SE3 weather for residual/direct
```

Forbidden features:

```text
spot price
future actual total SE3 consumption
future actual cluster target
future actual residual
flows/exchanges/A61/capacity
old physical_balance target
holdout-derived reconciliation weights
```

Residual model may use its own historical residual lags, but not future actual residual.

## Split policy

Use P0054 split unless a component starts later and this is documented:

```text
train_fit: 2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Internal validation for ensemble weights, horizon-bias correction, model selection and reconciliation weights must be strictly inside train_fit.

Prefer:

```text
internal_validation_start = 2025-03-01T00:00:00Z
```

No holdout row may be used for fitting, selection, correction, reconciliation or weighting.

## Forecast use cases

Evaluate both:

```text
DayAhead:
  forecast_origin = 12:00 Europe/Stockholm on D-1
  delivery_day = D 00:00..23:00 Europe/Stockholm

full_36h:
  complete 36-hour path from origin
```

Use the same horizon convention as P0054R/P0054T4.

## Required forecasts

### Direct forecast

Create or reproduce:

```text
forecast_direct_se3_best
```

Expected rough baseline:

```text
DayAhead MAE around 252-259 MW depending on exact protocol
```

### Component forecasts

Create:

```text
forecast_cluster_C11
forecast_cluster_C12
...
forecast_cluster_C44
forecast_residual_metered_non_profiled
```

### Aggregated forecast

Create:

```text
forecast_decomposition_total = sum(all profiled cluster forecasts) + residual forecast
```

### Optional reconciled forecast

If runtime allows, create a train-fit-only learned combination:

```text
forecast_reconciled_total = w1 * direct + w2 * decomposition_total + bias/horizon correction
```

Weights/corrections must be learned only inside train_fit/internal validation.

## Metrics

### Individual component metrics

For each component:

```text
component_id
component_type
mean_actual_mw
share_of_total
DayAhead MAE
DayAhead RMSE
DayAhead bias
full_36h MAE
full_36h RMSE
p90_abs_error
p95_abs_error
MAE_percent_of_component_mean
daily_energy_error_MWh
```

### Total SE3 metrics

For direct, decomposition_total and optional reconciled:

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
cold/high-load/ramp regimes where available
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

### Comparison metrics

```text
decomposition_delta_vs_direct_MW
decomposition_delta_vs_direct_percent
reconciled_delta_vs_direct_MW if run
cluster_sum_error_contribution
residual_error_contribution
best_component_modeling_failures
```

## Required questions to answer

P0055A must answer:

```text
1. Does the aggregated profiled-cluster + residual forecast beat the best direct SE3 forecast?
2. Which individual clusters forecast well or poorly?
3. Does the residual dominate total error?
4. Does climate-zone weather improve cluster behavior enough to help total SE3?
5. Should next work continue hierarchical decomposition or keep direct SE3 as default?
6. Is a reconciled ensemble better than either direct or decomposition alone?
```

## Learning thresholds

Treat decomposition as better only if it improves:

```text
DayAhead hourly MAE by >= 2% relative to direct
or daily energy error by >= 5% without worsening hourly MAE by more than 1%
or full_36h MAE by >= 2% without worsening DayAhead MAE
```

Treat reconciled ensemble as better if it improves:

```text
DayAhead hourly MAE by >= 1% relative to direct
and does not worsen daily energy or full_36h by more than 1%
```

If improvements are below thresholds, keep direct SE3 model as default and retain decomposition as diagnostic/emulator feature.

## Runtime policy

This may be moderately expensive. Codex must:

```text
run serially by component
checkpoint every completed component forecast
not discard completed forecasts if one component fails
use zero/fallback forecasts for zero/sparse components rather than stopping
write component status table/evidence
avoid loading all large tables into memory at once
use SQL/chunked processing where practical
```

## Required evidence files

Create:

```text
requirements/package-runs/P0055A/CHANGELOG.md
requirements/package-runs/P0055A/review.md
requirements/package-runs/P0055A/design.md
requirements/package-runs/P0055A/functions.md
requirements/package-runs/P0055A/labb-label.md
requirements/package-runs/P0055A/input-source-contract.md
requirements/package-runs/P0055A/split-policy-applied.md
requirements/package-runs/P0055A/weather-feature-contract.md
requirements/package-runs/P0055A/component-target-contract.md
requirements/package-runs/P0055A/model-method-contract.md
requirements/package-runs/P0055A/component-training-evidence.md
requirements/package-runs/P0055A/component-forecast-status.md
requirements/package-runs/P0055A/component-results.md
requirements/package-runs/P0055A/direct-se3-results.md
requirements/package-runs/P0055A/decomposition-total-results.md
requirements/package-runs/P0055A/reconciled-results.md if run
requirements/package-runs/P0055A/comparison-vs-direct.md
requirements/package-runs/P0055A/error-contribution-analysis.md
requirements/package-runs/P0055A/dayahead-results.md
requirements/package-runs/P0055A/full-36h-results.md
requirements/package-runs/P0055A/daily-energy-error-results.md
requirements/package-runs/P0055A/leakage-review.md
requirements/package-runs/P0055A/interpretation.md
requirements/package-runs/P0055A/what-we-learned.md
requirements/package-runs/P0055A/next-package-recommendation.md
```

Optional compact evidence:

```text
component-results.csv
forecast-status.csv
total-comparison.csv
error-contribution.csv
metrics-summary.json
```

Do not commit model binaries, large raw time-series dumps, full prediction dumps, virtualenvs or caches.

## Files to inspect

```text
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0054V2/decision.md
requirements/package-runs/P0054Y2/CHANGELOG.md
requirements/package-runs/P0054Y2/decomposition-validation.md
requirements/package-runs/P0054Y2/cluster-segment-dictionary.md
requirements/package-runs/P0054Z/CHANGELOG.md
requirements/package-runs/P0054Z/climate-zone-validation.md
requirements/package-runs/P0054Z/cluster-weather-mapping.md
src/mac/** relevant consumption/model scripts
tests/mac/** relevant tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
```

## Files allowed to change

```text
requirements/packages/P0055A-labb-se3-direct-vs-profiled-clusters-residual-forecast.md
requirements/package-runs/P0055A/**
src/mac/** narrowly scoped forecast/evaluation code if needed
tests/mac/** narrowly scoped tests for component aggregation/leakage if code is added
docs/functions/mac/** if durable docs need updating
local database forecast-log tables if repo owns them and only for P0055A outputs
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
No holdout fitting, selection, reconciliation or weighting.
No treating residual as observed per-MGA measured data.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054Y2 decomposition tables available
P0054Z weather table available
corrected ENTSO-E SE3 target used
old physical_balance target not used
spot price features not used
cluster-weather mapping applied
zero clusters handled safely
component forecasts generated or fallback documented
aggregated decomposition forecast equals sum(component forecasts)
direct SE3 baseline reproduced or documented
comparison against direct computed
no future actual target/residual leakage
no holdout fitting/selection/reconciliation
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- direct SE3 baseline is evaluated.
- all non-zero components are forecasted or safely fallbacked.
- residual is forecasted.
- decomposition total is computed.
- decomposition total is compared against direct SE3.
- component-level and total-level metrics are reported.
- leakage review passes.
```

WARN is acceptable if:

```text
- some zero clusters use zero forecast.
- some sparse clusters use simple fallback.
- optional reconciled ensemble is skipped.
- one component model fails but a documented fallback is used.
```

STOP if:

```text
- P0054Y2 or P0054Z inputs are missing.
- residual target cannot be built/evaluated.
- aggregation cannot be made equal to sum of components.
- corrected ENTSO-E SE3 target cannot be joined.
- leakage is found.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
input tables used
components forecasted/fallbacked/zeroed
direct SE3 metrics
decomposition total metrics
decomposition vs direct delta
reconciled result if run
best individual and worst individual components
residual error contribution
whether decomposition beats direct
recommended next package
tests/commands run
files changed
confirmation no spot price/no old target/no flow/A61/no external integration/no large artifacts
```

## Completion notes

Implemented in P0055A.

Result: `PASS`.

Summary:

- Created `src/mac/services/spotprice_model_diagnostics/p0055a.py`.
- Created `tests/mac/services/spotprice_model_diagnostics/test_p0055a.py`.
- Wrote required evidence under `requirements/package-runs/P0055A/`.
- Forecasted direct SE3, all non-zero profiled/load-profile clusters and the calculated residual.
- Zero-volume clusters `C14`, `C23`, `C24`, `C34`, `C41` used explicit zero forecast.
- Aggregated decomposition total was computed as sum(cluster forecasts) + residual forecast.
- Optional reconciliation was run with weights learned only from internal validation.
- Decomposition did not beat direct SE3 under package thresholds.
- No API, devices, runtime writes, spot-price features, old physical_balance target, flow/A61/capacity features, model binaries or large raw prediction dumps were used.
