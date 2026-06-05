# Package P0054L2: LABB SE3 advanced spot price forecast serial long-run

## Status

planned

## Package order

P0054L2

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Retry P0054L with an explicit long-running, serial execution policy.

P0054L stopped because the all-candidate implementation over the full direct/168h-expanded SE3 price row set did not complete within a practical package-run window. The operator has observed that Codex may ask to abort long-running jobs shortly before they finish. Therefore P0054L2 must not stop merely because a model takes time. It must run candidate models one at a time, persist evidence after each completed model, and accept partial completed results as WARN rather than discarding them because a later model is slow.

P0054L2 remains price-forecast only. It must not rerun SE3 consumption models.

## Runtime policy

Long runtime is acceptable for this package.

Codex must follow this policy:

```text
Do not abort a running model merely because it is slow.
Run one model family at a time.
Write evidence/checkpoints immediately after each model completes.
If Codex wants to abort because a process has been running a while, wait longer and/or ask the operator before terminating it.
If a process still appears active, prefer waiting over killing it.
If one later model fails or is manually stopped, keep already completed model evidence.
A package with completed useful model evidence should be WARN rather than STOP unless all model families fail.
```

The intended execution order is:

```text
1. Baseline P0054K comparison
2. HGB
3. ExtraTrees
4. LightGBM
5. XGBoost
6. Ensemble/blend if useful and enough candidates completed
```

If XGBoost is slow, it should be the last model so earlier results are preserved.

## Prior package conclusions

P0054L STOP cause:

```text
The direct 168h-expanded row set was too large for the current all-candidate implementation. Three attempts were stopped during model training, and no generated metric evidence was accepted.
```

P0054L review found the package concept implementable and safe, with the downstream warning:

```text
A global model trained on train_fit can safely evaluate holdout predictions, but it is not automatically a forecast-origin-safe train-period feature source for downstream consumption model training.
```

P0054L2 must preserve that warning.

## Core questions

P0054L2 must answer:

```text
1. Can serial long-running execution produce accepted SE3 advanced price forecast evidence?
2. Which completed model family best forecasts SE3 price versus the P0054K baseline?
3. Do any completed advanced models beat P0054K baseline by broad MAE or weekly 168h MAE?
4. Do any completed advanced models improve ranking, spike or ramp metrics even if broad MAE does not improve?
5. Is there a recommended forecast source for a future P0054M downstream SE3 consumption experiment?
```

## Scope boundary

Allowed:

```text
SE3 spot price forecast model training/evaluation
local SQLite reads/writes
local deterministic Python computation
package-run evidence
small source/test changes needed for serial execution and checkpointing
```

Forbidden:

```text
SE3 consumption model rerun
Shelly/Home Assistant/device/runtime work
live API calls
production deployment
G2-KANDIDAT promotion
actual future spot price leakage
production/export/import/A61/future-flow features
large raw dataset/model binary/venv/cache commits
```

## Split policy

Use the P0054I/P0054J/P0054K operator-approved LABB split:

```text
train_fit: timestamp_utc >= 2022-06-01T00:00:00Z
           and timestamp_utc < 2025-06-01T00:00:00Z

holdout:   timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

If internal validation is needed, carve it strictly from inside train_fit, for example:

```text
internal_train:      2022-06-01 .. 2025-02-28
internal_validation: 2025-03-01 .. 2025-05-31
```

## Target

Primary target:

```text
spot_price_se3
```

Use the same target reconstruction identified by P0054L unless Codex finds a better repository-documented canonical source:

```text
spot_price_se3 = system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price
source table = ai2_hour_to_day_training_targets_v2
```

Codex must document exact source table/file, columns, unit, timestamp semantics, coverage and missingness.

## Baseline

Evaluate P0054K baseline on the same comparable holdout rows:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
```

Required label:

```text
forecast_safe_origin_local_baseline_not_m4
```

## Candidate models

Run serially in this order where imports are available:

```text
HGB
ExtraTrees
LightGBM
XGBoost
```

Optional only after at least two candidates complete:

```text
simple ensemble/blend
```

XGBoost must be last. If XGBoost is slow or fails, the package should still complete with WARN if HGB/ExtraTrees/LightGBM produced useful evidence.

## Serial checkpoint requirements

After each model family completes, immediately create/update evidence under:

```text
requirements/package-runs/P0054L2/model-checkpoints/<model>.md
requirements/package-runs/P0054L2/model-checkpoints/<model>-metrics.json
```

or an equivalent compact evidence path.

At minimum each checkpoint must include:

```text
model_name
status completed/failed/skipped
start_time/end_time or duration_seconds if available
train_rows
internal_validation_rows if used
holdout_rows
feature_count
hyperparameters
import/version status
holdout MAE/RMSE/bias
weekly MAE_full_168h if computed
ranking/spike/ramp summary if computed
leakage status for that model
```

Do not wait until all models finish before writing evidence.

## Forecast log output

If at least one advanced model beats the P0054K baseline according to learning threshold, create or identify a recommended holdout-safe advanced forecast log:

```text
advanced_spotprice_forecast_log_p0054l2_se3_v1
```

If no advanced model beats baseline, do not create a misleading downstream forecast source. Instead document `no_advanced_source_recommended`.

Important downstream limitation:

```text
A global train_fit price model is holdout-safe for evaluation, but not automatically a train-period feature source for downstream consumption training. P0054M must either use holdout-only evaluation or create rolling/out-of-fold train forecasts if it needs train_fit consumption features.
```

## Feature groups

Allowed forecast-origin-safe features:

```text
calendar/time known in advance
horizon_hour
historical SE3 price lags strictly before origin
historical SE3 price rolling stats strictly before origin
historical SE3 volatility/ramp stats strictly before origin
previous-week same-hour price only when source timestamp is strictly before origin
previous-48h anchor/history features strictly before origin
known market calendar features
optional other Swedish area historical price lags strictly before origin if already local and documented
```

Forbidden features:

```text
actual future SE3 price inside target_window
same-hour realized price for target timestamp unless known at origin
future production
future consumption/load
future export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental actual prices at target timestamp
live API data
```

Avoid physical flow/A61 features entirely.

## Leakage restrictions

For every forecast row and candidate model:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
all lag/rolling/history source timestamps < forecast_origin_timestamp_utc
all model fitting rows used for a prediction are within train_fit
holdout is not used for selection or fitting
no target-window actual price is used as input
```

If a direct multi-horizon model is used, prove horizon-specific targets are shifted correctly and no target-window values enter features.

## Evaluation metrics

Required broad/path metrics:

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
```

Required ranking/extreme metrics where practical:

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

If some expensive metrics are deferred for runtime, broad metrics plus at least one ranking/spike/ramp summary must be produced for completed candidates, or the omission must be documented as WARN.

## Required comparisons

P0054L2 must report:

```text
1. P0054K baseline metrics on comparable holdout rows.
2. Completion/failure status for each serial model.
3. Best completed model by direct MAE.
4. Best completed model by weekly MAE_full_168h.
5. Best completed model by ranking/spike/ramp metrics.
6. Whether any completed model beats P0054K by >= 2% direct MAE or weekly MAE_full_168h.
7. Whether any completed model improves ranking/spike/ramp metrics materially without broad MAE degradation.
8. Whether P0054M should be created, and under what downstream contract.
```

Learning threshold:

```text
An advanced price forecast is useful if it improves direct holdout MAE or MAE_full_168h by >= 2%, or materially improves ranking/spike/ramp metrics without worsening broad MAE by more than 1%.
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054L2/CHANGELOG.md
requirements/package-runs/P0054L2/review.md
requirements/package-runs/P0054L2/design.md
requirements/package-runs/P0054L2/functions.md
requirements/package-runs/P0054L2/labb-label.md
requirements/package-runs/P0054L2/runtime-policy.md
requirements/package-runs/P0054L2/attempts.md
requirements/package-runs/P0054L2/split-policy-applied.md
requirements/package-runs/P0054L2/source-discovery.md
requirements/package-runs/P0054L2/price-target-contract.md
requirements/package-runs/P0054L2/feature-groups.md
requirements/package-runs/P0054L2/input-classification.md
requirements/package-runs/P0054L2/model-training-evidence.md
requirements/package-runs/P0054L2/model-checkpoints/README.md
requirements/package-runs/P0054L2/baseline-p0054k-results.md
requirements/package-runs/P0054L2/hgb-results.md if completed or skipped/failed evidence
requirements/package-runs/P0054L2/extratrees-results.md if completed or skipped/failed evidence
requirements/package-runs/P0054L2/lightgbm-results.md if completed or skipped/failed evidence
requirements/package-runs/P0054L2/xgboost-results.md if completed or skipped/failed evidence
requirements/package-runs/P0054L2/ensemble-results.md if applicable
requirements/package-runs/P0054L2/model-comparison.md
requirements/package-runs/P0054L2/direct-horizon-results.md
requirements/package-runs/P0054L2/weekly-168h-path-results.md
requirements/package-runs/P0054L2/ranking-spike-ramp-results.md
requirements/package-runs/P0054L2/forecast-log-schema.md if a log is created
requirements/package-runs/P0054L2/forecast-log-coverage.md if a log is created
requirements/package-runs/P0054L2/leakage-review.md
requirements/package-runs/P0054L2/downstream-contract-for-p0054m.md
requirements/package-runs/P0054L2/interpretation.md
requirements/package-runs/P0054L2/what-we-learned.md
requirements/package-runs/P0054L2/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
ranking-spike-ramp-summary.json
forecast-log-summary.json
coverage-by-origin.csv
feature-importance.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/packages/P0054L-labb-se3-advanced-spotprice-forecast.md
requirements/package-runs/P0054L/attempts.md
requirements/package-runs/P0054L/review.md
requirements/package-runs/P0054L/design.md
requirements/package-runs/P0054K/CHANGELOG.md
requirements/package-runs/P0054K/se3-price-forecast-source-contract.md
requirements/package-runs/P0054K/se3-price-forecast-log-schema.md
requirements/package-runs/P0054K/se3-price-forecast-coverage.md
requirements/package-runs/P0054K/se3-price-forecast-leakage-review.md
requirements/package-runs/P0054K/model-comparison.md
requirements/package-runs/P0054K/price-forecast-ablation.md
requirements/package-runs/P0054E/import-validation.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
local SQLite table metadata for SE3 price forecast/history tables
relevant local source files for P0054L attempt if present
```

Do not read large raw data files during bootstrap unless required by package verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054L2-labb-se3-advanced-spotprice-forecast-serial-longrun.md
requirements/package-runs/P0054L2/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** relevant existing LABB price forecast scripts if changes are needed
tests/mac/** relevant tests for changed price forecast code
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No downstream SE3 consumption model rerun in this package.
No actual future spot price leakage.
No P0053C-B validation/holdout-only M4 forecast as train feature.
No production/export/import/A61/future-flow features.
No live API calls.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054L2.
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054 split applied
P0054K baseline available and comparable
serial model checkpointing works
candidate feature matrices contain only forecast-origin-safe columns
feature matrix contains no actual future price/production/flow/A61 columns
all lag/rolling/history timestamps strictly before origin
LightGBM/XGBoost import status OK or documented
weekly 168h paths are complete or skipped with reason
leakage review passes
no downstream consumption model outputs are created
git diff --check
no large data/model/env artifacts are staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- P0054K baseline evaluated.
- HGB, ExtraTrees, LightGBM and XGBoost completed serially, or XGBoost completed/skipped with explicit evidence only if not required by final decision.
- Best advanced forecast model identified.
- Leakage review passes.
- Forecast log/source suitable for next-step decision is created or explicitly rejected.
```

WARN is acceptable if:

```text
- At least two advanced model families complete and produce accepted evidence.
- XGBoost is slow/failed/skipped but HGB/ExtraTrees/LightGBM complete.
- Ranking/spike/ramp metrics are partial but broad/path metrics are complete.
- No advanced model beats baseline but the negative result is clean.
```

STOP only if:

```text
- No advanced model family completes with accepted evidence.
- No reliable local SE3 price target exists.
- Safe forecast-origin features cannot be built.
- Actual future price leaks into features.
- Forbidden production/flow/A61/future features enter the matrix.
- Holdout is used for fitting or model selection.
- Device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
runtime behavior summary
serial model completion table
SE3 price target/source summary
split policy summary
baseline metrics
best completed price model by direct MAE
best completed price model by weekly MAE_full_168h
best ranking/spike/ramp model
comparison to P0054K baseline
whether improved forecast source should be used by P0054M
forecast log/table/view name if created
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no actual future price/API/device/A61/leakage work
confirmation no downstream consumption ablation was run
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
