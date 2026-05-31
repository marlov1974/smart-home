# Package P0034: ML normal spot model M4

## Status

planned

## Package order

P0034

## Primary area

G2 / Mac tooling / spotprice V2 / ML normal spot model / index and level modeling

## Linked requirements

Epic:
- E0001

Features:
- F0001

User stories:
- US0001

## Decision summary

Build M4: the first real ML normal spot model trained on P0033 temperature-normalized price series.

P0034 must train and validate separate models for:

```text
M4A: SE1 system_proxy normal spot model
M4B: SE3-SE1 area_diff_proxy normal spot model
```

SE3 is recomposed only after prediction:

```text
M4_SE3 = M4_SE1 + M4_area_diff_proxy
```

P0034 must produce normal, temperature-neutral price/index outputs. It must not implement M5 temperature forecast delta, M6 forecast API or M7 futures/absolute long-term model.

## Context

P0030 created historical SE3 spotprice data and daily ingest.
P0031 created historical weather data and daily ingest.
P0032 added SE1 system_proxy, SE3-SE1 area_diff_proxy, weather proxy groups and gradients.
P0033 creates temperature-normalized training series through M1/M2/M3.

P0034 consumes P0033 output and trains M4.

## Inputs

Primary input DB:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

Expected P0033 input series:

```text
temp_normalized_price_v1_se1
temp_normalized_area_diff_v1
temp_normalized_price_v1_se3
```

P0034 may also read P0030/P0032 raw price DB for diagnostics only:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

P0034 must not use actual temperature, temperature forecast, wind, solar, or weather-gradient values as predictive features. Weather effects belong to P0033/M3 for training normalization and later P0035/M5 for forecast-time temperature delta.

## Target behavior

Train a reproducible ML normal spot model that learns:

```text
- weekly relative index curves
- clipped calendar-month curves built from week curves
- week-of-year index
- week-within-month index
- month index
- week/month level behavior
- smooth calendar/time structure
- slow trend/regime behavior
```

The model must be split by target:

```text
system_proxy_se1
area_diff_proxy_se3
```

The package must output predictions/diagnostics for:

```text
M4_normal_price_se1
M4_normal_area_diff_proxy
M4_normal_price_se3 = M4_normal_price_se1 + M4_normal_area_diff_proxy
```

## Model architecture requirements

P0034 must implement M4 as a structured model, not a single opaque prediction over raw SE3.

Required conceptual components:

```text
1. Level model
2. Curve/index model
3. Combiner/recomposer
4. Backtest/evaluation layer
```

### Level model

The level model estimates normal price level for each target.

Required level targets or equivalents:

```text
weekly_mean_temp_normalized_se1
monthly_mean_temp_normalized_se1
weekly_mean_temp_normalized_area_diff
monthly_mean_temp_normalized_area_diff
year_or_regime_level where useful
```

### Curve/index model

The curve model estimates relative shape after level normalization.

Required curve/index targets or equivalents:

```text
intra_week_hour_index = temp_normalized_hour_price / temp_normalized_week_mean
week_index_vs_year = week_mean / year_mean
week_index_within_month = week_mean / month_mean
month_index_vs_year = month_mean / year_mean
monthly_curve_index built from clipped weeks
```

P0034 must implement the agreed monthly curve rule:

```text
A month curve is built from the 4-5 ISO week curves that intersect the calendar month.
Outer weeks are clipped so only the target month's days/hours are included.
The clipped month curve is renormalized so its mean over the calendar month is 1.0.
Weeks inside the month must be indexed relative to each other using week-of-year or week-within-month index.
```

## Feature requirements

Allowed features:

```text
hour_sin
hour_cos
weekday_sin
weekday_cos
day_of_year_sin
day_of_year_cos
is_weekend
is_holiday if available
period_of_day
week_of_year_sin/cos or smoothed week position
month position where needed for level/index
calendar month boundary / clipped week metadata
days_since_start / smooth trend
rolling long-term regime features derived only from temperature-normalized prices, e.g. 90d/365d, if design prevents leakage
```

Forbidden features:

```text
raw temperature
actual weather anomaly
weather gradients
weather forecast
wind/solar/cloud/radiation
actual future prices
day-ahead known prices for training targets unless used only in a leakage-safe diagnostic
short lag features that leak target horizon behavior unless design explicitly validates horizon-safe usage
SE3 monolithic target as the primary model target
```

## ML dependency policy

P0034 is the first package allowed to introduce a real ML dependency if needed.

Preferred dependency:

```text
scikit-learn
```

Codex must do a dependency review before adding it. If project policy or environment makes scikit-learn unsuitable, Codex must STOP/WARN and implement only a deterministic baseline, documenting the blocker.

Candidate models to evaluate:

```text
HistGradientBoostingRegressor
RandomForestRegressor
Ridge/ElasticNet or Linear/Ridge baseline
```

P0034 must keep the training pipeline reproducible:

```text
fixed random seeds
explicit train/validation/test splits
recorded feature schema
recorded package/model version
recorded model parameters
```

## Training and validation policy

Use time-based validation only. Do not use random row split as the primary score.

Expected validation strategies:

```text
walk-forward backtest
or train/validation/holdout by year
```

Suggested initial split if coverage supports it:

```text
train:      2022-05-30..2024-12-31
validate:   2025-01-01..2025-12-31
holdout:    2026-01-01..latest P0033 coverage
```

Codex may choose walk-forward instead, but must document the scheme.

## Metrics

P0034 must report metrics separately for:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

Required metrics or equivalents:

```text
MAE/RMSE for level predictions
MAE/RMSE for hourly normal price predictions
weekly curve index MAE
monthly curve index MAE
week-of-year index error
rank accuracy for cheapest/most expensive hours where meaningful
top/bottom quantile precision for relative index
comparison against P0033 M1 baseline
comparison against existing/pre-P0034 weekly index model if available
```

For index curves, shape/rank diagnostics are at least as important as absolute error.

## Storage requirements

Use local artifact storage. Do not commit generated model artifacts or local model DBs to repo unless explicitly tiny and justified.

Expected local model directory:

```text
~/.smart-home/data/spotprice_ml_models/m4/
```

Expected local DB/tables, final design may choose equivalent:

```text
m4_model_runs
m4_feature_matrix_manifest
m4_level_predictions
m4_curve_predictions
m4_backtest_results
m4_artifact_manifest
```

Repo must commit:

```text
- ML training/backtest code
- schema/manifest definitions
- small deterministic test fixtures
- docs/functions/mac/spotprice-ml-normal-model.md
- package-run evidence and summaries
```

Repo must not commit:

```text
- large trained binary model artifacts
- generated full local ML artifact directory
- secrets
```

## CLI expectations

Codex must define exact commands in design, but expected equivalents are:

```bash
python3 -m src.mac.services.spotprice_ml_model build-features-m4 \
  --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 \
  --model-dir ~/.smart-home/data/spotprice_ml_models/m4

python3 -m src.mac.services.spotprice_ml_model train-m4 \
  --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 \
  --model-dir ~/.smart-home/data/spotprice_ml_models/m4

python3 -m src.mac.services.spotprice_ml_model backtest-m4 \
  --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 \
  --model-dir ~/.smart-home/data/spotprice_ml_models/m4

python3 -m src.mac.services.spotprice_ml_model validate-m4 \
  --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 \
  --model-dir ~/.smart-home/data/spotprice_ml_models/m4
```

If actual commands differ, document equivalents.

## API policy

P0034 must not create or modify a production forecast API.

Allowed:

```text
- CLI prediction/export for backtest and inspection
- local model artifact manifest
- documentation of how P0036/M6 should consume M4
```

Forbidden:

```text
- HTTP API server
- launchd job
- live forecast service
- actuator/control integration
```

## Non-goals

- No M5 ML temperature forecast delta model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No weather forecast ingestion.
- No futures/forward data.
- No optimizer/control changes.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No Home Assistant integration.
- No FTX/heating-control policy.
- No MCP/tunnel work.
- No live device access.

## Invariants

- Mac-side only.
- No device writes.
- No Shelly RPC calls.
- No actuator/output/switch/cover/relay actions.
- No secrets.
- P0034 must be reproducible from P0033 local feature DB.
- P0034 must not retrain or change P0033 M1/M2/M3 outputs.
- M4 is a normal, temperature-neutral model.
- SE1 and SE3-SE1 remain separate primary targets.
- SE3 is a recomposed diagnostic/output, not the primary training target.

## Knowledge updates

Create or update:

```text
docs/functions/mac/spotprice-ml-normal-model.md
docs/functions/00-index.md
```

Update if durable architecture knowledge is created:

```text
docs/functions/mac/spotprice-temperature-normalization.md
docs/functions/mac/spotprice-history.md
memory/device-management/mac-layer.md
memory/knowhow/codex.md
```

## Implementation updates

Expected areas, final paths to be chosen in design:

```text
src/mac/services/spotprice_ml_model/**
tests/mac/services/spotprice_ml_model/**
docs/functions/mac/spotprice-ml-normal-model.md
requirements/package-runs/P0034/**
requirements/packages/P0034-ml-normal-spot-model-m4.md
```

## Files to inspect

- `README.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/08-context-bootstrap-modes.md`
- `memory/device-management/mac-layer.md`
- `requirements/packages/P0033-temperature-normalized-training-foundation.md`
- `requirements/package-runs/P0033/**`
- `docs/functions/mac/spotprice-temperature-normalization.md`
- existing spot forecast/index API docs and code
- existing optimizer/index model tests if present

## Files allowed to change

- `src/mac/services/spotprice_ml_model/**` or equivalent path documented in design
- `tests/mac/services/spotprice_ml_model/**` or equivalent test path documented in design
- `docs/functions/mac/spotprice-ml-normal-model.md`
- `docs/functions/00-index.md`
- `docs/functions/mac/spotprice-temperature-normalization.md` only for cross-link/consumer contract updates
- `memory/device-management/mac-layer.md` only for durable Mac model-pipeline documentation
- `memory/knowhow/codex.md` only for reusable ML/package lessons
- `requirements/package-runs/P0034/**`
- `requirements/packages/P0034-ml-normal-spot-model-m4.md`

Local Mac artifacts expected after verification:

```text
~/.smart-home/data/spotprice_ml_models/m4/
```

## Forbidden changes

- No G1 repository changes.
- No deploy artifact changes under `dep/s/**`.
- No Home Assistant changes.
- No Shelly runtime script changes.
- No live Shelly calls.
- No KVS writes.
- No actuator/output/switch/cover/relay implementation or calls.
- No optimizer policy changes.
- No M5/M6/M7 implementation.
- No temperature forecast delta model.
- No forecast API/server.
- No futures data.
- No launchd job.
- No secrets or credentialed data sources.
- No root/system launch daemon.
- No broad refactor outside the minimal P0034 M4 scope.

## Pre-implementation consistency review

Before editing implementation/model files, Codex must classify as:

- `PASS`: P0033 feature DB and temperature-normalized series exist locally; ML dependency plan is clear; M4 can train/backtest.
- `WARN`: P0033 exists but ML dependency is unavailable and deterministic baseline fallback is needed.
- `STOP`: P0033 is missing/incomplete; feature DB lacks required outputs; package would require M5/M6; or dependency/environment blocker prevents meaningful implementation.

Required review checks:

- P0033 local feature DB exists.
- Required temp-normalized SE1 and area_diff series exist.
- Date coverage and row counts are known.
- No weather features are included in M4 feature set.
- ML dependency availability is checked.
- Existing weekly index model/API location is identified for baseline comparison if available.

Store review evidence in:

```text
requirements/package-runs/P0034/review.md
```

## Implementation design policy

Codex must create design before coding:

```text
requirements/package-runs/P0034/design.md
```

Design must document:

```text
- input P0033 tables/views
- feature schema
- target schema
- monthly clipped-week curve algorithm
- week-of-year/week-within-month index algorithm
- level model algorithm
- curve model algorithm
- ML algorithms/dependencies selected
- train/validation/holdout or walk-forward plan
- model artifact storage
- metrics
- baseline comparisons
- why M5/M6/M7 are deferred
```

## Function design policy

Codex must create function design before implementation:

```text
requirements/package-runs/P0034/functions.md
```

Document functions or equivalent responsibilities:

```text
load_p0033_training_series(...)
build_calendar_features(...)
build_level_targets(...)
build_curve_targets(...)
build_week_of_year_indexes(...)
build_clipped_month_curves(...)
train_m4_target_model(...)
train_m4_level_model(...)
train_m4_curve_model(...)
recompose_se3_predictions(...)
run_walk_forward_backtest(...)
compare_against_baselines(...)
write_model_artifact_manifest(...)
validate_m4_outputs(...)
main(argv=None)
```

## Context-reset phase gates

Use:

```text
sync -> bootstrap -> review -> design -> function design -> implementation -> feature build -> training -> backtest -> validation -> evidence/changelog
```

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0034/
```

Expected evidence files:

```text
CHANGELOG.md
review.md
design.md
functions.md
attempts.md
feature-matrix-summary.md
model-artifact-summary.md
backtest-summary.md
baseline-comparison.md
```

Evidence must include:

- input coverage
- feature schema
- target schema
- ML dependency decision
- train/validation/test split
- model parameters
- model artifact paths and sizes
- SE1 metrics
- area_diff metrics
- recomposed SE3 metrics
- weekly/monthly curve metrics
- baseline comparison against P0033 M1 and existing index model where available
- confirmation no M5/M6/M7/API/device work was done

## Test cases

### TC1: Load P0033 training data

Given a feature DB with P0033 outputs
When P0034 loads data
Then SE1 and area_diff normalized series are present and timestamp-aligned.

### TC2: Feature schema excludes weather

Given built feature matrix
When schema validation runs
Then no temperature/weather/wind/solar columns are present.

### TC3: Cyclic time features

Given timestamps
When features are built
Then hour/weekday/day-of-year sin/cos features are deterministic.

### TC4: Level targets

Given normalized prices
When level targets are built
Then weekly and monthly means are correct for SE1 and area_diff.

### TC5: Intra-week curve indexes

Given normalized prices and week means
When curve targets are built
Then intra-week indexes equal price/week_mean with safe zero handling.

### TC6: Clipped monthly curves

Given a month crossing ISO week boundaries
When monthly curves are built
Then only hours inside the calendar month are included and curve mean is normalized to 1.0.

### TC7: Week index weighting

Given weeks inside a month
When month curve is built
Then week-of-year/week-within-month indexes weight the clipped week curves relative to each other.

### TC8: Separate target models

Given training
When models are trained
Then SE1 and area_diff models/artifacts are separate.

### TC9: Recompose SE3

Given SE1 and area_diff predictions
When recomposition runs
Then SE3 prediction equals SE1 + area_diff.

### TC10: Time-based validation

Given training data
When backtest runs
Then no random split is used as primary validation.

### TC11: Baseline comparison

Given M4 and M1 predictions
When comparison runs
Then metrics are reported for SE1, area_diff and recomposed SE3.

### TC12: No API/device side effects

Given P0034 commands
When tests run
Then no launchd, HTTP service, Shelly/device or actuator path is touched.

## Verification commands

Codex must define final commands in design, but expected equivalents are:

```bash
python3 -m unittest discover tests/mac/services/spotprice_ml_model
python3 -m unittest discover tests/mac/services
python3 -m src.mac.services.spotprice_ml_model build-features-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model train-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model backtest-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
python3 -m src.mac.services.spotprice_ml_model validate-m4 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --model-dir ~/.smart-home/data/spotprice_ml_models/m4
git diff --check
```

If actual commands differ, document equivalents.

## Runtime health checks

Record:

- P0033 feature DB path
- model dir path
- date interval
- row counts
- feature count
- target count
- model artifacts
- split dates
- metrics by target
- recomposed SE3 metrics
- baseline comparisons

No launchd/service/device health checks are required.

## Deployment plan

P0034 creates local M4 model artifacts and backtest evidence. It is not a production forecast service.

No launchd job, API server, Shelly deploy, Home Assistant integration or device interaction is part of P0034.

## Rollback plan

Rollback means removing or ignoring:

```text
~/.smart-home/data/spotprice_ml_models/m4/
```

Repo rollback is a new forward-moving package if the M4 model foundation is wrong.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- ML dependency decision
- feature schema
- target schema
- model algorithms selected
- train/validation/test split
- model artifact paths
- backtest metrics
- baseline comparisons
- monthly clipped-curve validation
- separate SE1 and area_diff model confirmation
- recomposed SE3 confirmation
- tests run
- files changed
- no M5/M6/M7/API/device confirmation
- commit SHA after push, if successful and pushed
- diff summary

## Completion notes

To be filled after implementation.
