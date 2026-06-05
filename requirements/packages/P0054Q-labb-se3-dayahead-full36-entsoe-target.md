# Package P0054Q: LABB SE3 DayAhead/full_36h rerun with ENTSO-E target

## Status

completed

## Package order

P0054Q

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Rerun the SE3 DayAhead and full_36h consumption forecast experiments using the corrected ENTSO-E Actual Total Load target built by P0054P2.

P0054K-P0054O used an old proxy-like target:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
```

P0054P2 proved that this old source is not equivalent to total SE3 load:

```text
old SE3 mean ≈ 3 933 MW
ENTSO-E SE3 mean ≈ 9 501 MW
ratio ENTSO-E / old ≈ 2.42
correlation ≈ 0.23
```

Therefore P0054K-P0054O must be interpreted as proxy-target methodology experiments, not validated total-SE3-load forecast results.

P0054Q must produce the first comparable SE3 DayAhead/full_36h forecast metrics on validated total SE3 load.

## Required target source

Use P0054P2 canonical target:

```text
table: entsoe_consumption_area_hourly_v1
area: SE3
target_column: consumption_mw
join_key: timestamp_utc, area
source_type: actual_total_load
area_scope: bidding_zone_internal_consumption_or_load
```

This target is historical observed load only. It may be used as training target and holdout truth, never as a future feature.

STOP if Codex falls back to:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
```

or any cross-border flow/exchange/capacity/production/price source as consumption target.

## Core questions

P0054Q must answer:

```text
1. What is the best SE3 full_36h forecast MAE on ENTSO-E Actual Total Load?
2. What is the best SE3 DayAhead delivery-day forecast error on ENTSO-E Actual Total Load?
3. What are the percent errors against actual ENTSO-E SE3 load?
4. Does advanced SE3 spot-price forecast still help once the target is corrected?
5. Which model family is best on corrected total-load target?
6. How does performance compare to the workplace reference of roughly 3-4% error?
7. How much of P0054N/P0054O's apparent behavior was caused by the old proxy target?
8. Should this corrected setup become the basis for future method-candidate work?
```

## Required split policy

Use the same P0054 train/holdout policy:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for model fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

Any internal validation must be carved strictly from train_fit.

## Forecast use cases

### full_36h

Define a complete 36-hour path from forecast origin:

```text
forecast_origin_timestamp_utc = origin
target_window = origin .. origin + 35h
horizon_hour = 0..35
```

If existing code uses horizon 1..36, document the convention and keep exactly 36 target hours.

### DayAhead delivery day

Use the P0054N timing convention:

```text
decision_time_local = 12:00 Europe/Stockholm on D-1
delivery_day_local = D 00:00..23:00 Europe/Stockholm
submission_deadline_context = before 13:00 Europe/Stockholm on D-1
```

This is a LABB evaluation only. Do not integrate with Nord Pool or workplace systems.

## Features

Allowed features:

```text
calendar/time known in advance
Swedish holiday/special-day classification
historical ENTSO-E SE3 load lags strictly before forecast origin
historical ENTSO-E SE3 load rollups strictly before forecast origin
weather proxy features from existing P0054N/P0054O setup, clearly labeled weather_actual_as_forecast_proxy unless true historical weather forecasts exist
safe advanced SE3 spot-price forecast features from P0054M/P0054N protocol, if available for train and holdout without leakage
```

Forbidden features:

```text
future actual ENTSO-E load
target-window actual load beyond forecast origin
actual future spot price
same-hour realized spot price for target timestamp unless known at origin
cross-border physical flows as consumption target
future actual flows/exchanges/net positions
A61 capacity/utilization/margin
production as target substitute
live API data
```

Historical load lags and rollups must use timestamps strictly before forecast origin.

## Price feature policy

P0054Q should test no-price and with-advanced-price variants where safe.

Preferred advanced price protocol:

```text
Use the safe exact-origin or rolling/oof advanced SE3 price forecast protocol established in P0054M/P0054N.
```

If safe with-price features cannot be built for corrected target rows, P0054Q may still PASS with no-price corrected-target results and WARN the with-price branch, but it must not use unsafe price features.

## Models to evaluate

Minimum required:

```text
HGB_no_price
LightGBM_no_price
XGBoost_no_price
```

Preferred full comparison:

```text
HGB_no_price
HGB_with_advanced_price
ExtraTrees_no_price
ExtraTrees_with_advanced_price
LightGBM_no_price
LightGBM_with_advanced_price
XGBoost_no_price
XGBoost_with_advanced_price
```

If runtime is tight, prioritize:

```text
1. HGB_no_price, because it won P0054N on the old target.
2. XGBoost_no_price, because it was strong in several earlier experiments.
3. LightGBM_with_advanced_price, because price helped LightGBM in earlier runs.
4. ExtraTrees as comparator if practical.
```

## Metrics

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
cold/high-price/spike/ramp regimes where available
```

Required target sanity metrics inside P0054Q:

```text
SE3 holdout mean actual MW
SE3 holdout median actual MW
SE3 DayAhead delivery-day mean actual MW
SE3 daily energy mean GWh/day
comparison to P0054P2 SE3 volume sanity
```

## Comparisons

Compare against P0054N/P0054O only as old-target references:

```text
P0054N old-target best DayAhead MAE ≈ 149 MW
P0054N old-target best full_36h MAE ≈ 150 MW
P0054O old-target baseline percent ≈ 6.4% of old/proxy mean actual
```

Do not present these as comparable total-SE3-load performance metrics. Label them as proxy-target results.

Required P0054Q comparisons:

```text
1. Best no-price corrected-target model.
2. Best with-price corrected-target model if safe.
3. Best DayAhead hourly MAE model.
4. Best DayAhead daily energy error model.
5. Per-model advanced price delta if applicable.
6. Corrected-target percent error versus workplace 3-4% reference.
7. Whether corrected-target result is promising enough for future method-candidate work.
```

## Weather realism note

P0054Q may use the existing weather proxy to isolate the target correction effect:

```text
weather_actual_as_forecast_proxy
```

If so, state clearly that production/DayAhead claims are still not valid until a later package replaces weather actuals with forecast-safe historical weather forecasts or repeats P0054O-style noise/realism tests on the corrected target.

Recommended follow-up after P0054Q:

```text
P0054R LABB SE3 DayAhead weather realism on ENTSO-E target
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054Q/CHANGELOG.md
requirements/package-runs/P0054Q/review.md
requirements/package-runs/P0054Q/design.md
requirements/package-runs/P0054Q/functions.md
requirements/package-runs/P0054Q/labb-label.md
requirements/package-runs/P0054Q/target-source-contract.md
requirements/package-runs/P0054Q/p0054p2-source-review.md
requirements/package-runs/P0054Q/split-policy-applied.md
requirements/package-runs/P0054Q/dataset-contract.md
requirements/package-runs/P0054Q/feature-groups.md
requirements/package-runs/P0054Q/input-classification.md
requirements/package-runs/P0054Q/model-training-evidence.md
requirements/package-runs/P0054Q/full-36h-results.md
requirements/package-runs/P0054Q/dayahead-delivery-day-results.md
requirements/package-runs/P0054Q/percent-error-results.md
requirements/package-runs/P0054Q/daily-energy-error-results.md
requirements/package-runs/P0054Q/advanced-price-ablation.md if applicable
requirements/package-runs/P0054Q/model-comparison.md
requirements/package-runs/P0054Q/conditional-regime-results.md
requirements/package-runs/P0054Q/old-target-comparison.md
requirements/package-runs/P0054Q/leakage-review.md
requirements/package-runs/P0054Q/interpretation.md
requirements/package-runs/P0054Q/what-we-learned.md
requirements/package-runs/P0054Q/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
full-36h-path-metrics.csv
dayahead-delivery-day-metrics.csv
percent-error-summary.json
daily-energy-error-summary.csv
conditional-metrics.csv
```

Do not commit model binaries, large raw data, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054P2/CHANGELOG.md
requirements/package-runs/P0054P2/entsoe-actual-load-source-contract.md
requirements/package-runs/P0054P2/coverage-by-area.md
requirements/package-runs/P0054P2/volume-sanity-by-area-season.md
requirements/package-runs/P0054P2/se3-volume-check.md
requirements/package-runs/P0054P2/old-source-comparison.md
requirements/package-runs/P0054P2/downstream-contract-for-p0054q.md
requirements/package-runs/P0054N/full-36h-results.md
requirements/package-runs/P0054N/dayahead-delivery-day-results.md
requirements/package-runs/P0054O/percent-error-results.md
requirements/package-runs/P0054O/review.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files for P0054N/P0054O modeling and evaluation
```

## Files allowed to change

```text
requirements/packages/P0054Q-labb-se3-dayahead-full36-entsoe-target.md
requirements/package-runs/P0054Q/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped corrected-target DayAhead/full_36h modeling code if needed
tests/mac/** narrowly scoped tests for target selection/leakage/timing if code changes are made
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No Nord Pool/workplace integration.
No use of physical_balance_se1_se4_hourly_v1.consumption_se3 as target.
No cross-border flow/exchange/capacity data as target.
No future actual load or future actual price leakage.
No live API calls.
No large raw data/model binary/venv/cache commits.
No broad refactor unrelated to P0054Q.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054P2 target table exists and is used
SE3 target source is entsoe_consumption_area_hourly_v1.consumption_mw
old physical_balance target is not used
P0054 split applied
DayAhead 12:00 Europe/Stockholm D-1 timing verified
full_36h paths complete or skipped with reason
no-price and with-price paired rows identical where paired modeling is claimed
feature matrix contains no future actual load/price/flow/A61 columns
weather proxy label preserved if weather actuals are used
target sanity metrics match P0054P2 order of magnitude
leakage review passes
git diff --check
no large data/model/env artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- Corrected ENTSO-E SE3 target is used.
- full_36h and DayAhead metrics are reported.
- Percent errors and daily energy errors are reported.
- Old-target comparison is explicitly labeled.
- Leakage review passes.
```

WARN is acceptable if:

```text
- with-price branch is skipped because safe price rows are not available.
- one model family fails but key HGB/XGBoost/LightGBM no-price results are available.
- conditional regimes are sparse.
- weather remains actual-as-forecast proxy, as long as it is labeled.
```

STOP if:

```text
- corrected ENTSO-E target cannot be used.
- old physical_balance target is used as target.
- cross-border flow data is used as target.
- DayAhead/full_36h paths cannot be constructed.
- actual future load/price leakage is introduced.
- holdout is used for fitting or model selection.
- device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
target source used
SE3 target volume sanity during modeling
models run
best full_36h model and MAE
best DayAhead hourly MAE model
best DayAhead daily energy error model
percent error against corrected ENTSO-E actual load
advanced price effect if applicable
comparison to 3-4% workplace reference
old-target comparison and interpretation
weather proxy caveat
leakage review result
what we learned
next package recommendation
commands/tests run
files changed
confirmation no old target/flow target/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

P0054Q completed with PASS.

Implemented corrected-target SE3 DayAhead/full_36h LABB evaluation:

```text
src/mac/services/spotprice_model_diagnostics/p0054q.py
tests/mac/services/spotprice_model_diagnostics/test_p0054q.py
```

Target source used:

```text
entsoe_consumption_area_hourly_v1.consumption_mw
area = SE3
source_type = actual_total_load
area_scope = bidding_zone_internal_consumption_or_load
```

The old physical-balance target was not used as target.

Run result:

```text
status = PASS
source_rows = 35125
train_fit_rows = 3310
holdout_rows = 12792
full36_complete_origin_rows = 345
dayahead_delivery_days = 347
```

Best corrected-target full_36h model:

```text
LightGBM_no_price
MAE_full_36h = 644.987 MW
MAE_percent_of_mean_actual = 6.586%
```

Best corrected-target DayAhead hourly MAE model:

```text
LightGBM_no_price
hourly_MAE_delivery_day = 632.787 MW
MAE_percent_of_mean_actual = 6.550%
```

Best DayAhead daily-energy model:

```text
HGB_no_price
absolute_daily_energy_error_MWh = 12862.666
daily_energy_error_percent_of_actual = 5.283%
```

Advanced price did not help on the corrected target overall; it worsened HGB, LightGBM and XGBoost for both full_36h and DayAhead hourly MAE, with only a tiny ExtraTrees full_36h improvement.

P0054Q remains LABB-only. The weather input is still `weather_actual_as_forecast_proxy`, so the results are not production DayAhead or G2-KANDIDAT evidence. Recommended follow-up:

```text
P0054R LABB SE3 DayAhead weather realism on ENTSO-E target
```
