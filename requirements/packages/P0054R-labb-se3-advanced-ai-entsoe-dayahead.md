# Package P0054R: LABB SE3 advanced AI on ENTSO-E DayAhead/full_36h

## Status

completed

## Package order

P0054R

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Test whether more advanced AI/modeling methods can improve SE3 DayAhead and full_36h consumption forecasting on the corrected ENTSO-E Actual Total Load target from P0054P2/P0054Q.

P0054Q established the corrected-target baseline:

```text
best full_36h: LightGBM_no_price MAE_full_36h ≈ 645 MW, ≈ 6.59% of mean actual
best DayAhead hourly: LightGBM_no_price MAE ≈ 633 MW, ≈ 6.55% of mean actual
best DayAhead daily energy: HGB_no_price ≈ 12.86 GWh absolute error, ≈ 5.28%
advanced price features worsened most 36h/DayAhead results
weather remains weather_actual_as_forecast_proxy
```

P0054R must test more advanced AI against that baseline, while preserving the corrected ENTSO-E target and strict leakage controls.

## Strategic question

The operator wants to test whether a more advanced model can approach or beat a workplace DayAhead reference of roughly 3-4% error.

P0054R must be honest about the remaining LABB limitation:

```text
Weather is still actual-as-forecast proxy unless the package explicitly replaces it with a forecast-safe historical weather forecast source.
```

Therefore any improvement is not production-ready until a later weather-realism package confirms it.

## Required target source

Use only:

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

STOP if the old target or flow data is used as the target.

## Required split policy

Use the P0054 split:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Holdout must not be used for fitting, early stopping, feature selection, hyperparameter selection, ensemble weights or model-family selection.

Any validation/tuning must be strictly inside train_fit, preferably:

```text
internal_train:      2022-06-01 .. 2025-02-28
internal_validation: 2025-03-01 .. 2025-05-31
```

If cross-validation is used, it must be blocked/time-series-aware and inside train_fit only.

## Forecast use cases

### DayAhead

Use P0054Q/P0054N semantics:

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

Document whether horizon convention is 0..35 or 1..36.

## Candidate advanced AI methods

Run as many as practical, in a staged order. Every completed method must produce persisted evidence before starting the next heavy method.

### Tier 0: Required baselines

Reproduce or import P0054Q comparable baselines on the same row set:

```text
LightGBM_no_price
XGBoost_no_price
HGB_no_price
```

### Tier 1: Strong tabular ensembles

Required if libraries are available:

```text
Stacked ensemble of HGB + LightGBM + XGBoost + ExtraTrees
Residual-correction model on top of best P0054Q baseline
Quantile/median ensemble if practical
Horizon-specialized models, one model per horizon or horizon bucket
DayAhead-specialized model trained only for 12:00 D-1 delivery-day task
```

The ensemble meta-learner must be trained only on internal train_fit validation / out-of-fold predictions, never on holdout.

### Tier 2: Sequence/window models

Optional but desired if dependencies/runtime allow:

```text
MLP with lag-window features
1D CNN / temporal convolution style model
LSTM or GRU sequence model
Transformer-lite / attention model for 36h path if PyTorch is available
```

If PyTorch/TensorFlow is unavailable, document import status and WARN rather than STOP if Tier 1 completes.

### Tier 3: Path-structured correction

Optional but valuable:

```text
36h path-bias correction
DayAhead daily-energy calibration layer
peak/ramp correction layer
post-hoc monotonic/smoothness/path-shape correction if it improves validation and is holdout-safe
```

Any correction layer must be fit only on train_fit/internal validation.

## Feature groups

Allowed forecast-safe features:

```text
calendar/time known in advance
Swedish holiday/special-day features
horizon_hour
forecast_origin local hour/date/day/month/week
historical ENTSO-E SE3 load lags strictly before origin
historical ENTSO-E SE3 load rolling stats strictly before origin
same-hour previous day/week values only if source timestamp is strictly before origin
weather proxy features already used by P0054Q, labeled weather_actual_as_forecast_proxy unless true forecast weather exists
optional advanced price forecast features only if proven safe and included in an ablation branch
```

Forbidden features:

```text
future actual ENTSO-E load
target-window actual load beyond origin
actual future spot price
future actual flows/exchanges/net positions
A61 capacity/utilization/margin
production/export/import future actuals
old physical_balance target as feature unless strictly historical and explicitly classified as old_proxy_history; prefer excluding it
holdout rows for tuning/ensemble weighting
```

Recommended: keep the primary advanced-AI run no-price, because P0054Q showed advanced price worsened 36h/DayAhead on corrected target. If price is tested, isolate it as an ablation branch.

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

Also report:

```text
model runtime
feature count
train rows
holdout rows
origin count
DayAhead delivery-day count
parameter count for neural models if available
```

## Learning threshold

P0054R should treat a method as promising if it achieves any of:

```text
>= 5% relative improvement over P0054Q best DayAhead hourly MAE
>= 5% relative improvement over P0054Q best full_36h MAE
>= 10% relative improvement in daily energy error without worsening hourly MAE by more than 1%
clear movement toward the 3-4% workplace reference range
```

Strongly promising if:

```text
DayAhead hourly MAE <= 5.0% of mean actual
or daily energy error <= 4.0%
```

Do not claim production readiness because weather remains proxy unless replaced.

## Runtime policy

Advanced AI may take time. Codex must:

```text
run methods serially
checkpoint evidence after each method
not discard completed methods because a later neural model is slow
skip unavailable optional libraries with WARN evidence
prefer completing Tier 1 strongly before attempting heavy Tier 2
```

STOP only if no advanced method beyond P0054Q baselines completes with accepted evidence, or if target/leakage safety fails.

## Required evidence files

Create:

```text
requirements/package-runs/P0054R/CHANGELOG.md
requirements/package-runs/P0054R/review.md
requirements/package-runs/P0054R/design.md
requirements/package-runs/P0054R/functions.md
requirements/package-runs/P0054R/labb-label.md
requirements/package-runs/P0054R/target-source-contract.md
requirements/package-runs/P0054R/split-policy-applied.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054R/feature-groups.md
requirements/package-runs/P0054R/input-classification.md
requirements/package-runs/P0054R/runtime-policy.md
requirements/package-runs/P0054R/environment-import-status.md
requirements/package-runs/P0054R/model-training-evidence.md
requirements/package-runs/P0054R/model-checkpoints/README.md
requirements/package-runs/P0054R/baseline-p0054q-comparison.md
requirements/package-runs/P0054R/stacked-ensemble-results.md if run
requirements/package-runs/P0054R/residual-correction-results.md if run
requirements/package-runs/P0054R/horizon-specialized-results.md if run
requirements/package-runs/P0054R/dayahead-specialized-results.md if run
requirements/package-runs/P0054R/neural-sequence-results.md if run or skipped evidence
requirements/package-runs/P0054R/full-36h-results.md
requirements/package-runs/P0054R/dayahead-delivery-day-results.md
requirements/package-runs/P0054R/daily-energy-error-results.md
requirements/package-runs/P0054R/percent-error-results.md
requirements/package-runs/P0054R/conditional-regime-results.md
requirements/package-runs/P0054R/advanced-price-ablation.md if price tested
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/leakage-review.md
requirements/package-runs/P0054R/interpretation.md
requirements/package-runs/P0054R/what-we-learned.md
requirements/package-runs/P0054R/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
model-comparison.csv
dayahead-delivery-day-metrics.csv
full-36h-path-metrics.csv
feature-importance.csv
neural-training-history.csv
```

Do not commit large model binaries, raw datasets, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054Q/CHANGELOG.md
requirements/package-runs/P0054Q/model-comparison.md
requirements/package-runs/P0054Q/dataset-contract.md
requirements/package-runs/P0054Q/advanced-price-ablation.md
requirements/package-runs/P0054Q/leakage-review.md
requirements/package-runs/P0054P2/downstream-contract-for-p0054q.md
requirements/package-runs/P0054P2/se3-volume-check.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files for P0054Q modeling/evaluation
```

## Files allowed to change

```text
requirements/packages/P0054R-labb-se3-advanced-ai-entsoe-dayahead.md
requirements/package-runs/P0054R/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped advanced-AI corrected-target modeling code if needed
tests/mac/** narrowly scoped tests for target selection/leakage/ensemble timing if code changes are made
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No Nord Pool/workplace integration.
No use of old physical_balance target.
No flow/exchange/capacity data as target.
No future actual load/price leakage.
No holdout tuning or ensemble weighting.
No live API calls.
No large raw data/model binary/venv/cache commits.
No broad refactor unrelated to P0054R.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
ENTSO-E corrected target is used
old physical_balance target is not used
P0054 split applied
DayAhead 12:00 Europe/Stockholm D-1 timing verified
full_36h paths complete or skipped with reason
ensemble/meta-learner uses train_fit/internal validation only
no future actual load/price/flow/A61 columns in features
weather proxy label preserved
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- At least one advanced method beyond P0054Q baselines completes.
- Corrected ENTSO-E target is used.
- DayAhead and full_36h metrics are reported.
- Comparison to P0054Q baseline is clear.
- Leakage review passes.
```

WARN is acceptable if:

```text
- Neural models are skipped due to missing dependencies but Tier 1 advanced ensembles complete.
- Advanced methods do not improve baseline, if the negative result is clean.
- Runtime prevents some optional methods but checkpoints preserve completed results.
```

STOP if:

```text
- Corrected ENTSO-E target cannot be used.
- Old target or flow target is used.
- No advanced method completes.
- Holdout is used for tuning/ensemble weighting.
- Actual future load/price leakage is introduced.
- Device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
target source used
advanced methods run/skipped
best P0054Q baseline reproduced or referenced
best advanced DayAhead hourly MAE and percent
best advanced full_36h MAE and percent
best daily energy error and percent
relative improvement vs P0054Q
whether advanced AI moves toward 3-4% reference
whether price features should stay excluded
weather proxy caveat
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation no old target/flow target/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

Completed with `PASS`.

Implemented a LABB-only corrected-target advanced-AI experiment in `src/mac/services/spotprice_model_diagnostics/p0054r.py`, with package evidence under `requirements/package-runs/P0054R/`.

Target source used:

```text
entsoe_consumption_area_hourly_v1.consumption_mw
area=SE3
source_type=actual_total_load
area_scope=bidding_zone_internal_consumption_or_load
```

No old `physical_balance_se1_se4_hourly_v1.consumption_se3` target, flow/exchange/capacity/A61 data, API calls, device writes, runtime changes, Nord Pool integration or workplace integration were used.

Final row counts:

```text
source_rows=35125
direct_rows=52173
train_fit_rows=38985
internal_train_rows=35675
internal_validation_rows=3310
holdout_rows=13188
full36_complete_origins=356
dayahead_delivery_days=358
```

Best advanced method:

```text
HorizonBiasCorrected_WeightedEnsemble_no_price
full_36h MAE=243.67666893537265 MW, 2.500614436538169% of mean actual
DayAhead hourly MAE=253.70062353819162 MW, 2.6387829449358526% of mean actual
daily energy absolute error=4381.407120291999 MWh, 1.9333789651384488% of actual
```

Relative improvement vs P0054Q corrected-target baseline:

```text
full_36h=62.21992990470855%
DayAhead hourly=59.9074154345852%
daily energy=65.93702154219062%
```

Leakage review passed:

```text
ok=true
holdout_used_for_model_fitting_or_selection=false
holdout_used_for_ensemble_weights_or_correction=false
old_physical_balance_target_used=false
actual_future_load_feature_used=false
actual_future_spot_price_feature_used=false
flow_export_import_a61_used=false
```

Optional neural sequence models were skipped with WARN evidence after Tier 1 advanced tabular methods completed. Weather remains `weather_actual_as_forecast_proxy`, so the result remains LABB-only and is not production-ready or G2-KANDIDAT.
