# Package P0054S: LABB SE3 advanced AI spot price forecast

## Status

planned

## Package order

P0054S

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Run the spot-price equivalent of P0054R: test more advanced AI/modeling methods for SE3 spot price forecasting and compare them against the P0054L2 advanced price forecast baseline.

P0054L2 produced the current best SE3 advanced spot-price forecast:

```text
advanced_spotprice_forecast_log_p0054l2_se3_v1
recommended_model = Ensemble
P0054L2 Ensemble direct holdout MAE ≈ 0.30340
P0054L2 Ensemble improvement vs P0054K baseline ≈ 13.11%
```

P0054S must test whether stronger model architecture, stacking, horizon specialization, path correction and optionally neural sequence methods can improve SE3 spot price forecasts further.

## Important context

P0054Q showed that advanced price features worsened corrected-target SE3 consumption DayAhead/full_36h, while P0054R achieved strong corrected-target consumption results without price features.

P0054S is still valuable because the broader energy-market stack needs good price forecasts for:

```text
DayAhead/intraday trading method candidates
future flow/export-import models
production response models
price-regime and spike/ramp classification
later coupled market-stack iterations
```

However, P0054S must evaluate price forecast quality as a price model, not assume it improves consumption forecast automatically.

## Required target

Primary target:

```text
spot_price_se3
```

Use the same canonical/local target reconstruction used by P0054L2 unless a repository-documented successor exists:

```text
spot_price_se3 = system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price
source table = ai2_hour_to_day_training_targets_v2
```

Codex must verify and document:

```text
source table/file
source columns
unit/currency
area semantics
timestamp semantics
coverage
missingness
```

STOP if no reliable local SE3 price target exists.

## Split policy

Use the existing P0054 train/holdout policy:

```text
train_fit: timestamp_utc >= 2022-06-01T00:00:00Z
           and timestamp_utc < 2025-06-01T00:00:00Z

holdout:   timestamp_utc >= 2025-06-01T00:00:00Z
```

Holdout must not be used for fitting, early stopping, hyperparameter selection, feature selection, ensemble weights, correction layers or model-family selection.

Any validation/tuning must be strictly inside train_fit, preferably:

```text
internal_train:      2022-06-01 .. 2025-02-28
internal_validation: 2025-03-01 .. 2025-05-31
```

If cross-validation is used, it must be blocked/time-series-aware and train_fit-only.

## Forecast use cases

Evaluate at least the same broad price forecast contract as P0054L2:

```text
direct horizon rows
weekly/full_168h paths where complete
ranking/spike/ramp metrics
```

Also add DayAhead-relevant price metrics if practical:

```text
forecast_origin = 12:00 Europe/Stockholm on D-1
delivery_day = D 00:00..23:00 Europe/Stockholm
```

The DayAhead slice is diagnostic only; no Nord Pool/workplace integration is allowed.

## Baselines

Required baselines:

```text
P0054K baseline on comparable rows
P0054L2 Ensemble on comparable rows
```

If exact persisted P0054L2 forecast rows are not aligned with P0054S evaluation origins, Codex may rerun/reconstruct equivalent P0054L2-style baseline using the documented P0054L2 contract, but must label the difference.

## Candidate advanced methods

Run serially and checkpoint after each completed method.

### Tier 0: reproduced comparable baselines

```text
P0054L2 Ensemble baseline
HGB
ExtraTrees
LightGBM
XGBoost
```

### Tier 1: advanced tabular/path models

Required if practical:

```text
Weighted ensemble of HGB + ExtraTrees + LightGBM + XGBoost
Median ensemble
Stacked ensemble with meta-learner trained only on internal validation/oof train_fit predictions
Residual-correction model on top of best baseline
Horizon-specialized models or horizon-bucket-specialized models
Horizon-bias/path correction layer
DayAhead-specialized price model for 12:00 D-1 delivery-day prices
Spike/ramp-specialized correction or classifier-regressor hybrid if practical
```

### Tier 2: sequence/neural models

Optional but desired if dependencies/runtime allow:

```text
MLP with lag-window features
1D CNN / temporal convolution style model
LSTM or GRU sequence model
Transformer-lite / attention model for 168h or 36h price paths if PyTorch is available
```

If PyTorch/TensorFlow is unavailable, document import status and WARN rather than STOP if Tier 1 completes.

### Tier 3: regime-aware calibration

Optional but valuable:

```text
high-price regime correction
low-price regime correction
spike/ramp calibration
path-level mean/bias correction
quantile-aware or robust-loss model if available
```

Any correction/calibration must be fit using train_fit/internal validation only.

## Feature groups

Allowed forecast-origin-safe features:

```text
calendar/time known in advance
horizon_hour
forecast origin local date/hour/day/month/week
historical SE3 price lags strictly before forecast origin
historical SE3 price rolling stats strictly before forecast origin
historical SE3 volatility/ramp stats strictly before forecast origin
previous-week same-hour price only if source timestamp is strictly before origin
previous-48h anchor/history features strictly before origin
known market calendar features
optional historical price lags from other Swedish areas strictly before forecast origin if local and documented
optional ENTSO-E actual load historical lags only if strictly before origin and clearly classified as historical context, not future actual load
```

Forbidden features:

```text
actual future SE3 price inside target window
same-hour realized SE3 price for target timestamp unless known at origin
future actual consumption/load
future actual production
future actual flows/exchanges/net positions
A61 capacity/utilization/margin
future weather actuals as price target-window signal unless explicitly forecast-safe
continental actual prices at target timestamp
live API data
holdout rows for tuning/ensemble weighting/correction fitting
```

Avoid production/export/import/A61/future-flow features entirely in this package.

## Metrics

Required direct/path metrics:

```text
MAE
RMSE
bias
median absolute error
p90 absolute error
p95 absolute error
sMAPE
R2 where useful
MAE_full_168h
bias_full_168h
p90/p95 full path
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
```

Required DayAhead metrics if DayAhead slice is run:

```text
hourly_MAE_delivery_day
hourly_RMSE_delivery_day
bias_delivery_day
absolute_daily_price_path_error where meaningful
peak_price_hour_error
peak_price_timing_error_hours
offpeak_MAE
morning_ramp_MAE
evening_peak_MAE
```

Required ranking/extreme metrics:

```text
Spearman correlation
top20_168h_precision
bottom20_168h_precision
top8_day_precision if practical
bottom8_day_precision if practical
spike detection precision/recall/F1
ramp detection precision/recall/F1
high price regime MAE
low price regime MAE
large price ramp MAE
forecast price spike MAE
```

Also report:

```text
runtime per model
feature_count
train_rows
internal_validation_rows if used
holdout_rows
forecast_origin_count
path_count
```

## Learning threshold

Treat a method as useful if it achieves one of:

```text
>= 5% relative improvement over P0054L2 Ensemble direct holdout MAE
>= 5% relative improvement over P0054L2 Ensemble MAE_full_168h
>= 10% improvement in spike/ramp/ranking metrics without worsening broad MAE by more than 1%
```

Treat it as strongly promising if:

```text
>= 10% relative improvement in direct MAE or full_168h MAE
or clearly superior spike/ramp performance with similar broad MAE
```

## Runtime policy

Advanced AI may take time. Codex must:

```text
run methods serially
checkpoint evidence after each method
not discard completed results because a later neural model is slow
skip unavailable optional libraries with WARN evidence
prefer completing Tier 1 before attempting heavy Tier 2
```

STOP only if no advanced method beyond P0054L2-style baseline completes with accepted evidence, or if target/leakage safety fails.

## Forecast log output

If a P0054S model beats P0054L2 according to the learning threshold, create or identify a recommended holdout-safe advanced forecast log:

```text
advanced_spotprice_forecast_log_p0054s_se3_v1
```

If no model beats P0054L2, do not create a misleading downstream source. Document:

```text
no_p0054s_advanced_source_recommended
```

Important downstream limitation remains:

```text
A global train_fit price model is holdout-safe for evaluation, but not automatically a train-period feature source for downstream consumption/production/flow training. Any downstream package needing train_fit price features must create rolling/out-of-fold train forecasts.
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054S/CHANGELOG.md
requirements/package-runs/P0054S/review.md
requirements/package-runs/P0054S/design.md
requirements/package-runs/P0054S/functions.md
requirements/package-runs/P0054S/labb-label.md
requirements/package-runs/P0054S/target-source-contract.md
requirements/package-runs/P0054S/split-policy-applied.md
requirements/package-runs/P0054S/dataset-contract.md
requirements/package-runs/P0054S/feature-groups.md
requirements/package-runs/P0054S/input-classification.md
requirements/package-runs/P0054S/runtime-policy.md
requirements/package-runs/P0054S/environment-import-status.md
requirements/package-runs/P0054S/model-training-evidence.md
requirements/package-runs/P0054S/model-checkpoints/README.md
requirements/package-runs/P0054S/baseline-p0054k-results.md
requirements/package-runs/P0054S/baseline-p0054l2-comparison.md
requirements/package-runs/P0054S/weighted-ensemble-results.md if run
requirements/package-runs/P0054S/median-ensemble-results.md if run
requirements/package-runs/P0054S/stacked-ensemble-results.md if run
requirements/package-runs/P0054S/residual-correction-results.md if run
requirements/package-runs/P0054S/horizon-specialized-results.md if run
requirements/package-runs/P0054S/horizon-bias-correction-results.md if run
requirements/package-runs/P0054S/dayahead-specialized-results.md if run
requirements/package-runs/P0054S/neural-sequence-results.md if run or skipped evidence
requirements/package-runs/P0054S/direct-horizon-results.md
requirements/package-runs/P0054S/weekly-168h-path-results.md
requirements/package-runs/P0054S/dayahead-price-results.md if run
requirements/package-runs/P0054S/ranking-spike-ramp-results.md
requirements/package-runs/P0054S/model-comparison.md
requirements/package-runs/P0054S/forecast-log-schema.md if log is created
requirements/package-runs/P0054S/forecast-log-coverage.md if log is created
requirements/package-runs/P0054S/leakage-review.md
requirements/package-runs/P0054S/downstream-contract.md
requirements/package-runs/P0054S/interpretation.md
requirements/package-runs/P0054S/what-we-learned.md
requirements/package-runs/P0054S/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
model-comparison.csv
direct-horizon-metrics.csv
weekly-path-metrics.csv
ranking-spike-ramp-summary.json
dayahead-price-metrics.csv
feature-importance.csv
```

Do not commit large model binaries, raw datasets, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054L2/CHANGELOG.md
requirements/package-runs/P0054L2/model-comparison.md
requirements/package-runs/P0054L2/leakage-review.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
requirements/package-runs/P0054K/model-comparison.md
requirements/package-runs/P0054K/se3-price-forecast-source-contract.md
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/baseline-p0054q-comparison.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files for P0054L2 price modeling/evaluation
```

## Files allowed to change

```text
requirements/packages/P0054S-labb-se3-advanced-ai-spotprice-forecast.md
requirements/package-runs/P0054S/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped advanced-AI price forecasting code if needed
tests/mac/** narrowly scoped tests for price target/leakage/ensemble timing if code changes are made
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No Nord Pool/workplace integration.
No future actual spot price leakage.
No future actual load/production/flow/A61 features.
No holdout tuning or ensemble weighting.
No live API calls.
No large raw data/model binary/venv/cache commits.
No broad refactor unrelated to P0054S.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
SE3 price target source verified
P0054 split applied
P0054K/P0054L2 baseline comparable
all lag/rolling/history timestamps strictly before forecast origin
ensemble/meta-learner uses train_fit/internal validation only
no future actual spot/load/production/flow/A61 columns in features
weekly/full_168h paths complete or skipped with reason
ranking/spike/ramp metrics computed or WARN-labeled
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- P0054L2 baseline comparison is available.
- At least one advanced method beyond P0054L2-style Ensemble completes.
- Direct and full_168h/path metrics are reported.
- Ranking/spike/ramp interpretation is reported.
- Leakage review passes.
```

WARN is acceptable if:

```text
- Neural models are skipped due to missing dependencies but Tier 1 advanced methods complete.
- DayAhead price slice is skipped but P0054L2-compatible direct/full_168h evidence is complete.
- Advanced methods do not improve baseline, if the negative result is clean.
- Runtime prevents optional methods but completed checkpoints are preserved.
```

STOP if:

```text
- No reliable local SE3 price target exists.
- No advanced method beyond P0054L2-style baseline completes.
- Holdout is used for tuning/ensemble weighting/correction fitting.
- Actual future spot/load/flow/A61 leakage is introduced.
- Device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
SE3 price target source used
advanced methods run/skipped
P0054K and P0054L2 baselines
best direct MAE model
best full_168h model
best ranking/spike/ramp model
relative improvement vs P0054L2
whether P0054S forecast log was created
whether price forecast is good enough for later flow/production/stack packages
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation no future actual price/load/flow/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
