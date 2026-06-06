# Package P0054T: LABB SE3 consumption model/weather/price matrix

## Status

completed

## Package order

P0054T

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Run a controlled 12-test matrix for SE3 DayAhead/full_36h consumption forecasting on the corrected ENTSO-E Actual Total Load target.

The matrix combines:

```text
3 most promising consumption models
x 2 weather modes: weather_actual_proxy vs temperature_noise_±2C
x 2 price modes: no_price vs best_spotprice_forecast
= 12 tests
```

The purpose is to identify:

```text
1. which of the best P0054R consumption methods remains strongest under weather noise,
2. whether the best available SE3 spot-price forecast helps or hurts under realistic/noisy weather,
3. whether any combination remains clearly within or below the workplace reference range of roughly 3-4%,
4. which model should be promoted to the next rolling-retrain/weather-realism package.
```

## Baseline context

P0054R found a strong no-price LABB result on corrected ENTSO-E SE3 total load:

```text
best model = HorizonBiasCorrected_WeightedEnsemble_no_price
DayAhead hourly MAE ≈ 253.70 MW ≈ 2.64%
full_36h MAE ≈ 243.68 MW ≈ 2.50%
DayAhead daily energy error ≈ 4 381 MWh ≈ 1.93%
```

P0054S tested more advanced SE3 spot-price models and did not produce a materially better forecast than P0054L2. Therefore the best available spot-price forecast source remains:

```text
advanced_spotprice_forecast_log_p0054l2_se3_v1
recommended_model = Ensemble
```

If P0054L2's persisted origin coverage does not match the required DayAhead/full_36h origins, Codex may use the P0054N/P0054Q exact-origin package-local reconstruction protocol, but must label it clearly as P0054L2-compatible and forecast-safe.

## Required target source

Use only the corrected ENTSO-E target:

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

STOP if the old target or flow data is used as target.

## Required split policy

Use the P0054 split:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for fitting, early stopping, hyperparameter selection, feature selection, ensemble weighting, correction fitting, noise-scenario selection or model-family selection.

Any validation/tuning/correction fitting must happen strictly inside train_fit.

## Forecast use cases

### DayAhead

Use P0054N/P0054Q/P0054R semantics:

```text
forecast_origin = 12:00 Europe/Stockholm on D-1
delivery_day = D 00:00..23:00 Europe/Stockholm
```

### full_36h

Use complete 36-hour forecast paths:

```text
forecast_origin_timestamp_utc = origin
target_window = 36 target hours from origin
```

Document horizon convention as 0..35 or 1..36.

## Required 12-test matrix

### Consumption model variants

Use the three most promising P0054R methods unless Codex documents a reason to substitute one due to implementation/runtime safety.

Required default models:

```text
M1 = HorizonBiasCorrected_WeightedEnsemble
M2 = WeightedEnsemble
M3 = XGBoost
```

Rationale from P0054R:

```text
HorizonBiasCorrected_WeightedEnsemble was best overall.
WeightedEnsemble was the strongest simple ensemble and near-best.
XGBoost was the strongest standalone model and a useful deployability comparator.
```

If exact P0054R implementation cannot be reused safely, STOP or WARN with a precise substitution such as `LightGBM` or `MedianEnsemble`, but preserve the 3x2x2 design.

### Weather variants

Run both:

```text
W0 = weather_actual_as_forecast_proxy
W1 = temperature_noise_uniform_minus2_plus2C
```

Weather noise protocol:

```python
temp_noisy = temp_actual_proxy + uniform(-2.0, +2.0)
```

Use deterministic seeds.

Minimum required:

```text
seeds = 1000..1004
```

Preferred if runtime allows:

```text
seeds = 1000..1009
```

For W1, report mean/std/min/max metrics across seeds. For W0, report the deterministic baseline.

Primary preferred modeling interpretation:

```text
Apply weather noise consistently to train_fit and holdout, then retrain/evaluate each model per seed.
```

If runtime is too high, Codex may use holdout-only sensitivity as WARN, but must label it clearly and not claim it is a trained noisy-weather model.

### Price variants

Run both:

```text
P0 = no_price
P1 = with_best_spotprice_forecast
```

Best spot-price forecast source:

```text
P0054L2 Ensemble forecast, or documented P0054L2-compatible exact-origin reconstruction if origin coverage requires it.
```

Price features must be forecast-safe at the same forecast origin. Minimum feature:

```text
predicted_spot_price_se3
```

Recommended price forecast path features:

```text
price_forecast_0_24h_mean
price_forecast_24_36h_mean
price_forecast_0_36h_mean
price_forecast_rank_within_path
price_forecast_spike_flag_within_path
price_forecast_ramp_from_previous_horizon
price_forecast_peak_offpeak_indicator
```

All path features must be derived only from the forecast path available at `forecast_origin_timestamp_utc`.

If safe price features cannot be aligned to the matrix rows, STOP the price branch and report no valid 12-test matrix.

## Expected matrix labels

Use clear labels such as:

```text
M1_HorizonBiasCorrectedWeightedEnsemble__W0_weatherProxy__P0_noPrice
M1_HorizonBiasCorrectedWeightedEnsemble__W0_weatherProxy__P1_p0054l2Price
M1_HorizonBiasCorrectedWeightedEnsemble__W1_tempNoise2C__P0_noPrice
M1_HorizonBiasCorrectedWeightedEnsemble__W1_tempNoise2C__P1_p0054l2Price
...
M3_XGBoost__W1_tempNoise2C__P1_p0054l2Price
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

Required comparison metrics:

```text
price_delta_with_minus_no_price per model/weather mode
weather_noise_delta_noisy_minus_proxy per model/price mode
best_overall_by_dayahead_hourly_MAE
best_overall_by_daily_energy_error
best_overall_by_full36_MAE
robustness_score = noisy_mean_MAE + noisy_std_penalty if useful
```

## Key questions to answer

P0054T must answer:

```text
1. Which of the three best P0054R consumption models is best under weather_actual_proxy?
2. Which is best under ±2°C temperature noise?
3. Does P0054L2 spot-price forecast help any model when weather is clean?
4. Does P0054L2 spot-price forecast help any model when weather is noisy?
5. Is price still harmful on corrected SE3 total load, or does it help when weather uncertainty increases?
6. Which model/price/weather combination is most robust?
7. Does any noisy-weather combination remain below 3-4% DayAhead hourly error?
8. Which combination should be used for the next rolling retrain package?
```

## Learning thresholds

Treat a combination as operationally interesting if:

```text
DayAhead hourly MAE <= 3.0% under W0
and noisy W1 mean DayAhead hourly MAE <= 4.0%
```

Treat price as useful only if:

```text
with_price improves DayAhead hourly MAE or daily energy error by >= 2% relative
under the same model and weather condition,
and does not worsen full_36h MAE by more than 1%.
```

Treat a model as robust if:

```text
W1 noisy mean DayAhead MAE worsens by <= 25% relative to W0
and noisy seed std is small enough to be operationally stable.
```

## Runtime policy

The matrix may be expensive. Codex must:

```text
run tests serially
checkpoint each completed combination
not discard completed results if a later combination fails
prioritize W0/P0 baselines first, then W0/P1, then W1/P0, then W1/P1
record duration per combination
```

If runtime is too high, Codex may reduce W1 seeds to 5 but must not reduce the 3x2x2 combination count unless it returns WARN with a precise reason.

## Required evidence files

Create:

```text
requirements/package-runs/P0054T/CHANGELOG.md
requirements/package-runs/P0054T/review.md
requirements/package-runs/P0054T/design.md
requirements/package-runs/P0054T/functions.md
requirements/package-runs/P0054T/labb-label.md
requirements/package-runs/P0054T/target-source-contract.md
requirements/package-runs/P0054T/split-policy-applied.md
requirements/package-runs/P0054T/dataset-contract.md
requirements/package-runs/P0054T/model-selection-from-p0054r.md
requirements/package-runs/P0054T/spotprice-source-contract.md
requirements/package-runs/P0054T/weather-noise-protocol.md
requirements/package-runs/P0054T/feature-groups.md
requirements/package-runs/P0054T/input-classification.md
requirements/package-runs/P0054T/runtime-policy.md
requirements/package-runs/P0054T/model-training-evidence.md
requirements/package-runs/P0054T/matrix-combinations.md
requirements/package-runs/P0054T/matrix-results-summary.md
requirements/package-runs/P0054T/dayahead-results.md
requirements/package-runs/P0054T/full-36h-results.md
requirements/package-runs/P0054T/daily-energy-error-results.md
requirements/package-runs/P0054T/weather-noise-results.md
requirements/package-runs/P0054T/price-ablation-results.md
requirements/package-runs/P0054T/robustness-ranking.md
requirements/package-runs/P0054T/conditional-regime-results.md
requirements/package-runs/P0054T/leakage-review.md
requirements/package-runs/P0054T/interpretation.md
requirements/package-runs/P0054T/what-we-learned.md
requirements/package-runs/P0054T/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
matrix-results.csv
seed-results.csv
price-deltas.csv
weather-deltas.csv
robustness-ranking.csv
```

Do not commit model binaries, large raw datasets, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/baseline-p0054q-comparison.md
requirements/package-runs/P0054R/leakage-review.md
requirements/package-runs/P0054S/model-comparison.md
requirements/package-runs/P0054S/leakage-review.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
requirements/package-runs/P0054Q/dataset-contract.md
requirements/package-runs/P0054Q/leakage-review.md
requirements/package-runs/P0054P2/downstream-contract-for-p0054q.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files for P0054R/P0054Q/P0054O/P0054N matrix/modeling logic
```

## Files allowed to change

```text
requirements/packages/P0054T-labb-se3-consumption-model-weather-price-matrix.md
requirements/package-runs/P0054T/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped matrix/evaluation code if needed
tests/mac/** narrowly scoped tests for target selection/weather noise/price alignment/leakage if code changes are made
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
No actual future spot price as feature.
No holdout tuning or selection.
No live API calls.
No large raw data/model binary/venv/cache commits.
No broad refactor unrelated to P0054T.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
ENTSO-E corrected target is used
old physical_balance target is not used
P0054 split applied
DayAhead 12:00 Europe/Stockholm D-1 timing verified
full_36h paths complete or skipped with reason
12 matrix combinations exist or WARN/STOP reason is clear
weather noise deterministic and within [-2,+2] C for temperature columns
price forecast features are forecast-safe and aligned by origin/horizon
each price path feature derives only from forecast rows available at same origin
no future actual load/price/flow/A61 columns in features
no holdout tuning or selection
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- all 12 combinations are evaluated, or all 12 W0 plus W1 seed-mean variants are evaluated.
- corrected ENTSO-E SE3 target is used.
- P0054L2/P0054S price-source decision is respected.
- DayAhead and full_36h metrics are reported.
- weather and price deltas are clear.
- leakage review passes.
```

WARN is acceptable if:

```text
- W1 uses 5 seeds instead of 10 due to runtime.
- one model is substituted with documented reason.
- optional conditional regimes are sparse.
- noisy retraining is too expensive and holdout-only sensitivity is clearly labeled.
```

STOP if:

```text
- corrected ENTSO-E target cannot be used.
- old target or flow target is used.
- safe price feature alignment fails.
- fewer than the required 12 model/weather/price combinations can be honestly evaluated.
- future actual load/price leakage is introduced.
- holdout is used for fitting/selection.
- device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
target source used
three model variants selected
weather noise protocol and seed count
spotprice forecast source used
12-combination matrix summary
best W0/P0, W0/P1, W1/P0, W1/P1 results
price deltas by model/weather mode
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
commit SHA after push
```

## Completion notes

Completed with `PASS`.

Implemented `src/mac/services/spotprice_model_diagnostics/p0054t.py` and wrote evidence under `requirements/package-runs/P0054T/`.

P0054T evaluated all required 12 summarized matrix combinations:

```text
3 model variants x 2 weather modes x 2 price modes = 12
W1 used 5 deterministic seeds: 1000..1004
seed/scenario result rows = 36
```

Target source:

```text
entsoe_consumption_area_hourly_v1.consumption_mw
area=SE3
source_type=actual_total_load
area_scope=bidding_zone_internal_consumption_or_load
```

Price source:

```text
P0054L2-compatible exact-origin package-local reconstruction
protocol=p0054n_exact_origin_blocked_train_plus_trainfit_holdout
rows=16187
```

Important comparability note:

```text
P0054T P0/P1 results are comparable inside the 12-test matrix because both branches use the P0054L2-compatible exact-origin price-row coverage. They are not a direct rerun of P0054R's broader no-price origin skeleton, so absolute MAE values differ from P0054R's best 253.70 MW DayAhead result.
```

Best clean-weather matrix result:

```text
M1_HorizonBiasCorrectedWeightedEnsemble / W0_weatherProxy / P0_noPrice
DayAhead hourly MAE=624.3881907571396 MW
DayAhead hourly percent=6.462887993090327%
full_36h MAE=639.3018518489251 MW
daily energy error=12819.954733521994 MWh
```

Best noisy-weather robust result:

```text
M1_HorizonBiasCorrectedWeightedEnsemble / W1_tempNoise2C / P0_noPrice
noisy mean DayAhead hourly MAE=657.9873224754929 MW
noisy mean DayAhead percent=6.810664309451293%
noisy std DayAhead hourly MAE=4.891424487743269 MW
```

Price conclusion:

```text
P0054L2-compatible price features did not help any selected model/weather mode by the package threshold.
All price deltas worsened DayAhead hourly MAE by about 4.15%..5.63%.
price_useful_by_threshold=false
```

Weather-noise conclusion:

```text
No noisy-weather combination remained <=4% DayAhead hourly error.
The best noisy no-price combination remained the most robust within this matrix.
```

Leakage review passed:

```text
ok=true
old_physical_balance_target_used=false
actual_future_load_or_price_feature_used=false
flow_export_import_a61_used=false
holdout_used_for_fitting_or_selection=false
holdout_used_for_ensemble_weights_or_correction=false
weather_noise_bounds_ok=true
api_device_runtime_nordpool_workplace_used=false
```

No API, device, runtime, A61, flow, Nord Pool, workplace, old-target, future actual leakage, model binary, venv, wheel or raw dataset actions were performed.
