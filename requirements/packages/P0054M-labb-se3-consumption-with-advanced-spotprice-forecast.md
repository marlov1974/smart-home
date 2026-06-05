# Package P0054M: LABB SE3 consumption with advanced SE3 spot price forecast

## Status

done

## Package order

P0054M

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Rerun the SE3 consumption forecast experiment using the improved P0054L2 Ensemble SE3 spot-price forecast as input, and compare it against the previous no-price and P0054K-baseline-price results.

P0054K showed that the simple origin-local SE3 price baseline helped some model families and regimes, especially LightGBM, but worsened the strongest SE3 consumption model, XGBoost. P0054L2 then produced a materially better holdout-safe SE3 price forecast ensemble:

```text
advanced_spotprice_forecast_log_p0054l2_se3_v1
recommended_model = Ensemble
```

P0054M must test whether the better price forecast improves SE3 consumption forecasting.

## Critical downstream safety note

P0054L2's advanced forecast log is holdout-safe for evaluation, but it is not automatically a train-period feature source for downstream consumption model training.

Therefore P0054M must choose one of two safe approaches before modeling:

```text
Option A, preferred if implementable:
  Create a rolling-origin or blocked out-of-fold train_fit SE3 advanced price forecast feature source,
  using the P0054L2 Ensemble method or a documented approximation, so consumption models can train with price features safely.

Option B, allowed as WARN/evaluation-only:
  Do not train consumption models with the P0054L2 price feature.
  Instead train no-price SE3 consumption models on train_fit,
  then evaluate holdout-side feature augmentation/diagnostics only where P0054L2 predictions exist.
```

Do not use the holdout-only P0054L2 forecast log as if it were a complete train_fit consumption feature matrix. STOP if Codex cannot implement a safe route or honestly label the route.

## Core questions

P0054M must answer:

```text
1. Does the P0054L2 Ensemble SE3 spot-price forecast improve SE3 consumption forecasting versus no-price?
2. Does it improve versus the earlier P0054K simple SE3 price baseline result?
3. Does the stronger price forecast help the strongest SE3 consumption model, XGBoost, unlike P0054K?
4. Which consumption model benefits most from the advanced price forecast?
5. Is the effect broad, or mainly in high-price/cold/spike/ramp regimes?
6. Should advanced SE3 price forecast be kept for future spread/flaskhals/response experiments?
```

## Required split policy

Use the P0054I/P0054J/P0054K/P0054L2 policy:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for consumption model fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

Any internal validation must be carved strictly inside `train_fit`.

## Target

Primary target:

```text
consumption_se3_mw
```

Use the same SE3 consumption target source as P0054K unless repository truth has a documented successor. Codex must document exact table/file, target column, unit, coverage, missingness and timestamp semantics.

Unit:

```text
MW hourly mean
```

STOP if no reliable local SE3 consumption target is available.

## Price forecast feature source

Primary advanced price source:

```text
advanced_spotprice_forecast_log_p0054l2_se3_v1
model_name = Ensemble
```

This source is valid for holdout-side evaluation according to P0054L2. It is not sufficient by itself as train_fit feature coverage.

Required P0054M decision before modeling:

```text
price_feature_protocol = rolling_oof_train_plus_holdout
or
price_feature_protocol = holdout_only_advanced_price_evaluation
```

If `rolling_oof_train_plus_holdout` is chosen, Codex must create/document a train_fit-safe forecast source with:

```text
area = SE3
model_name = Ensemble or documented P0054L2-compatible model
forecast_origin_timestamp_utc
target_timestamp_utc
horizon_hour
predicted_price
training_protocol
feature_cutoff_utc / input_data_cutoff_utc
package_id = P0054M
```

If `holdout_only_advanced_price_evaluation` is chosen, Codex must not claim a fully trained with-price consumption model unless train-side advanced price features exist.

## Baselines to compare

Compare against P0054K evidence:

```text
XGBoost_no_price holdout MAE = 48.01602472809628
XGBoost_no_price weekly MAE_full_168h = 108.51610764072525
XGBoost_with_p0054k_se3_price_forecast holdout MAE = 48.491100583964595
XGBoost_with_p0054k_se3_price_forecast weekly MAE_full_168h = 109.81910335762592
LightGBM_with_p0054k_se3_price_forecast holdout MAE = 48.3202873218118
LightGBM_with_p0054k_se3_price_forecast weekly MAE_full_168h = 132.89188052486935
```

Prefer rerunning no-price baselines in P0054M if practical, to ensure identical code/path. If reusing P0054K evidence, label it as evidence-summary comparison.

## Weather proxy

Use the same SE3 weather setup as P0054K unless a documented better SE3 weather proxy exists.

Weather remains LABB proxy unless forecast weather exists:

```text
weather_actual_as_forecast_proxy
```

## Feature variants

### Variant A: no_price

Allowed features:

```text
calendar/time known in advance
historical SE3 consumption lags and rollups strictly before forecast origin
SE3 weather proxy fields where available
```

### Variant B: with_p0054l2_ensemble_price_forecast

Variant A plus forecast-safe advanced SE3 price forecast features.

Minimum advanced price feature:

```text
predicted_price
```

Recommended additional price forecast features, computed only from the forecast path available at the same origin:

```text
price_forecast_0_24h_mean
price_forecast_24_48h_mean
price_forecast_0_168h_mean
price_forecast_rank_within_path
price_forecast_spike_flag_within_path
price_forecast_ramp_from_previous_horizon
price_forecast_peak_offpeak_indicator
```

If these are used, prove they derive only from forecast rows available at `forecast_origin_timestamp_utc`.

## Forbidden inputs

The consumption model feature matrix must not contain:

```text
actual future spot price
same-hour realized spot price for target timestamp unless known at forecast origin
P0054L2 holdout-only forecast used as train_fit feature without rolling/oof protocol
P0053C-B validation/holdout-only M4 forecast as train feature
production
future production
export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental actual prices
target-window actual consumption beyond forecast origin
```

Historical SE3 consumption lags and rollups are allowed only when strictly before forecast origin.

## Required models

Run these SE3 consumption model families where safe for the selected price-feature protocol:

```text
HGB
ExtraTrees
LightGBM
XGBoost
```

Optional:

```text
MLP if practical
```

Minimum required if `rolling_oof_train_plus_holdout` is implemented:

```text
HGB_no_price
HGB_with_p0054l2_ensemble_price_forecast
ExtraTrees_no_price
ExtraTrees_with_p0054l2_ensemble_price_forecast
LightGBM_no_price
LightGBM_with_p0054l2_ensemble_price_forecast
XGBoost_no_price
XGBoost_with_p0054l2_ensemble_price_forecast
```

If only holdout-only advanced price evaluation is possible, Codex must define a narrower, honest analysis and must not overstate it as trained with-price models.

## Hyperparameter policy

Use bounded hyperparameters from P0054K for comparability. Do not perform broad tuning unless strictly inside train_fit and bounded.

Holdout must never influence hyperparameters.

## Evaluation

Final scoring period:

```text
holdout only: target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Required direct horizons:

```text
1h, 3h, 6h, 12h, 24h, 48h, 72h, 96h, 120h, 144h, 168h
```

Weekly 168h path evaluation:

```text
weekly origins from 2025-06-01 onward where complete 168h paths exist
```

Direct metrics:

```text
MAE
RMSE
bias
median absolute error
p90
p95
sMAPE
MAE percent of mean/median actual
R2 where useful
```

Path metrics:

```text
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
MAE_full_168h
bias_full_168h
p90/p95 full path
daily energy error proxy
peak load hour error
```

Conditional metrics:

```text
cold hours
very cold hours
rapid temperature drop
weekday
weekend
holiday
morning ramp
evening peak
summer low load
winter high load
high advanced forecast price
low advanced forecast price
large advanced forecast price ramp
advanced forecast price spike
```

## Required comparisons

P0054M must report:

```text
1. Selected price feature protocol and why it is safe.
2. Best no-price SE3 consumption model.
3. Best with-advanced-price SE3 consumption model, if safely trainable.
4. Per-model advanced price delta versus no-price.
5. Advanced price result versus P0054K simple-price result.
6. Whether XGBoost benefits from advanced price forecast.
7. Whether LightGBM's P0054K benefit improves further.
8. Conditional regimes where advanced price helps or hurts.
9. Whether advanced SE3 price should be kept for future experiments.
```

Learning threshold:

```text
Advanced price forecast is useful if it improves holdout MAE or weekly MAE_full_168h by >= 2%, or improves >= 3% in at least two important price/temperature/load regimes without materially worsening broad holdout metrics.
```

This is a LABB learning threshold, not production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054M/CHANGELOG.md
requirements/package-runs/P0054M/review.md
requirements/package-runs/P0054M/design.md
requirements/package-runs/P0054M/functions.md
requirements/package-runs/P0054M/labb-label.md
requirements/package-runs/P0054M/price-feature-protocol-decision.md
requirements/package-runs/P0054M/split-policy-applied.md
requirements/package-runs/P0054M/dataset-contract.md
requirements/package-runs/P0054M/advanced-price-source-contract.md
requirements/package-runs/P0054M/input-classification.md
requirements/package-runs/P0054M/feature-groups.md
requirements/package-runs/P0054M/model-training-evidence.md
requirements/package-runs/P0054M/no-price-results.md
requirements/package-runs/P0054M/with-advanced-price-results.md if applicable
requirements/package-runs/P0054M/advanced-price-ablation.md
requirements/package-runs/P0054M/model-comparison.md
requirements/package-runs/P0054M/direct-horizon-results.md
requirements/package-runs/P0054M/weekly-168h-path-results.md
requirements/package-runs/P0054M/conditional-regime-results.md
requirements/package-runs/P0054M/p0054k-comparison.md
requirements/package-runs/P0054M/feature-importance-or-attribution.md
requirements/package-runs/P0054M/leakage-review.md
requirements/package-runs/P0054M/interpretation.md
requirements/package-runs/P0054M/what-we-learned.md
requirements/package-runs/P0054M/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
advanced-price-ablation-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
modeling-dataset-sample.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054L2/CHANGELOG.md
requirements/package-runs/P0054L2/model-comparison.md
requirements/package-runs/P0054L2/leakage-review.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
requirements/package-runs/P0054K/CHANGELOG.md
requirements/package-runs/P0054K/model-comparison.md
requirements/package-runs/P0054K/price-forecast-ablation.md
requirements/package-runs/P0054K/se3-price-forecast-leakage-review.md
requirements/package-runs/P0054K/input-classification.md
requirements/package-runs/P0054E/import-validation.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
docs/functions/mac/weather-history-dataset.md
local SQLite metadata for advanced_spotprice_forecast_log_p0054l2_se3_v1
local source files for P0054K and P0054L2 modeling
```

Do not read large raw data files during bootstrap unless required by package verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054M-labb-se3-consumption-with-advanced-spotprice-forecast.md
requirements/package-runs/P0054M/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
docs/functions/mac/weather-history-dataset.md if durable docs need updating
src/mac/** relevant existing LABB price/consumption modeling scripts if changes are needed
tests/mac/** relevant tests for changed modeling code
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No actual future spot price leakage.
No P0054L2 holdout-only forecast used as train_fit feature without rolling/oof protocol.
No P0053C-B validation/holdout-only M4 forecast as train feature.
No production/export/import/A61/future-flow features.
No live API calls.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054M.
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054 split applied
P0054L2 advanced price source contract verified
price feature protocol is safe and documented
SE3 consumption target source verified
no-price and with-price matrices use identical target rows where paired modeling is claimed
feature matrix contains no actual future price/production/flow/A61 columns
P0054L2 holdout-only source is not used as train_fit feature unless rolling/oof train forecasts are created
LightGBM/XGBoost import status OK or documented
weekly 168h paths complete or skipped with reason
leakage review passes
no large data/model/env artifacts staged
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- safe price-feature protocol is selected and implemented.
- SE3 consumption target is found and validated.
- advanced price impact is evaluated without leakage.
- model comparison and P0054K comparison are clear.
- leakage review passes.
```

WARN is acceptable if:

```text
- only holdout-only advanced price evaluation is possible and clearly labeled.
- rolling/oof train forecasts are too expensive but an honest evaluation-only result is produced.
- one boosted model fails but enough model families run.
- advanced price does not help but negative result is clean.
```

STOP if:

```text
- no safe way exists to use P0054L2 forecast in SE3 consumption evaluation.
- P0054L2 holdout-only forecast would be used as train_fit feature without rolling/oof protocol.
- actual future spot price leaks into features.
- forbidden production/flow/A61/future features enter the matrix.
- holdout is used for fitting or model selection.
- device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
price feature protocol decision
SE3 target/data coverage
advanced price source contract
models run
best no-price model
best with-advanced-price model if applicable
per-model advanced price deltas
comparison against P0054K simple price result
whether XGBoost benefits from advanced price
conditional/regime findings
whether advanced SE3 price should be kept
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no actual future price/API/device/A61/leakage work
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

P0054M completed with `PASS`.

Selected price feature protocol:

```text
price_feature_protocol = rolling_oof_train_plus_holdout
```

Implemented a safe partial train-side advanced price source:

```text
advanced_spotprice_forecast_log_p0054m_se3_train_blocked_oof_v1
target range: 2025-03-01T00:00:00Z .. 2025-05-31T22:00:00Z
rows: 14945
forecast origins: 92
training cutoff: 2025-02-28T23:00:00Z
```

Used existing P0054L2 Ensemble holdout source for holdout evaluation:

```text
advanced_spotprice_forecast_log_p0054l2_se3_v1
model_name = Ensemble
```

Consumption model rows:

```text
train_fit paired direct rows: 966
holdout paired direct rows: 3872
weekly path rows: 8568
```

Best no-price holdout model:

```text
ExtraTrees_no_price
MAE = 144.69949632494485
```

Best with-advanced-price holdout model:

```text
ExtraTrees_with_p0054l2_ensemble_price_forecast
MAE = 140.54830097681355
```

Best weekly with-advanced-price model:

```text
XGBoost_with_p0054l2_ensemble_price_forecast
MAE_full_168h = 206.2574365420684
```

The advanced price feature helped XGBoost in this safe protocol:

```text
XGBoost direct MAE: 154.77299216360825 -> 148.0499748921278
XGBoost weekly MAE_full_168h: 213.72331614362525 -> 206.2574365420684
```

Important limitation:

```text
The train-side advanced price source is partial 2025-03..2025-05 blocked OOF coverage, not a full train_fit rolling forecast source.
P0054K comparison is therefore an evidence-summary comparison, not an identical-row rerun.
```

No actual future spot price, P0054L2 holdout-as-train feature, live API, device, Shelly, Home Assistant, runtime, A61, production/export/import/future-flow or deployable model artifact was used.
