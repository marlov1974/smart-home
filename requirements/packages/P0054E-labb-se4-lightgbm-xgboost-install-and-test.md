# Package P0054E: LABB SE4 LightGBM/XGBoost install and test

## Status

done

## Package order

P0054E

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Install the Mac-local dependencies needed to test stronger gradient-boosted model families on the corrected SE4 consumption setup from P0054D, then rerun the SE4 no-price consumption experiment using `se4_load_weather`.

P0054D found that `ExtraTrees_G4_se4_load_weather` was the best dependency-safe model, with materially better holdout and weekly 168h metrics than HGB and MLP. P0054E tests whether LightGBM and/or XGBoost can improve further.

## Decision summary

Use P0054D as the baseline truth:

```text
weather proxy: se4_load_weather
target: consumption_se4_mw
feature group: G4_calendar_load_lags_rollups_weather_proxy
current best: ExtraTrees_G4_se4_load_weather
```

Install only the dependencies needed for LABB modeling on the Mac environment. Do not add runtime, device, Shelly, Home Assistant or production dependencies.

Preferred packages to make available:

```text
lightgbm
xgboost
```

If one package cannot be installed safely on the Mac, Codex must document the blocker and still run the other if available.

## Core questions

P0054E must answer:

```text
1. Can LightGBM and/or XGBoost be installed and imported in the local Mac LABB environment?
2. Do LightGBM or XGBoost beat ExtraTrees on SE4 consumption with se4_load_weather?
3. Do they improve direct holdout MAE, weekly 168h path MAE, or important conditional regimes by enough to justify further LABB work?
```

## Scope

Allowed:

```text
- Mac-local dependency installation for LABB modeling only.
- Updating documented local LABB dependency instructions if needed.
- Running offline SE4 consumption model experiments.
- Writing package-run evidence.
```

Not allowed:

```text
- G2-KANDIDAT promotion.
- Runtime or device actions.
- Shelly, Home Assistant, KVS or deploy changes.
- Production model deployment.
- Price/production/flow/A61/future-leakage features.
```

## Dependency installation policy

Codex must inspect the current Python environment and repository conventions before installing anything.

Required evidence before install:

```text
python executable
python version
pip version
virtualenv/venv/conda status if detectable
platform and architecture
existing sklearn/numpy/pandas versions if available
existing lightgbm/xgboost import status
```

Preferred install approach:

```text
Use the existing project/local LABB Python environment if one exists.
Use python -m pip install only inside that environment.
Avoid system Python pollution when a venv/project environment is available.
```

If the repository already has a dependency file or Mac LABB environment convention, update it only if that is consistent with existing policy. If no such file exists, Codex may document the install commands in package-run evidence without creating a broad dependency-management framework.

Codex must record exact install commands and resulting versions.

Do not commit installed packages, caches, virtualenv folders, wheel files, model binaries or large artifacts.

## Target and data

Use the same target as P0054D:

```text
consumption_se4_mw
```

Use the same canonical source unless repository truth has changed:

```text
physical_balance_se1_se4_hourly_v1
```

Unit:

```text
MW hourly mean
```

Use the P0053C global split:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

No target rows before 2022-06-01.

## Weather proxy

Use P0054D's corrected proxy:

```text
se4_load_weather
```

The package must validate that the proxy exists and covers the modeled period.

The weather remains LABB proxy weather:

```text
weather_actual_as_forecast_proxy
```

It is not a separate weather forecast model and not deployable evidence.

## Feature set

Use the same feature group as P0054D for apples-to-apples comparison:

```text
G4_calendar_load_lags_rollups_weather_proxy
```

Required feature inputs:

```text
calendar/time known in advance
historical SE4 load lags and rollups strictly before forecast origin
se4_load_weather proxy fields
```

Forbidden model features:

```text
spot price
M4 anchored price forecast
actual future spot price
production
future production
export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental prices
target-window actuals beyond forecast origin
```

## Required models

At minimum compare:

```text
HGB_G4_se4_load_weather
MLP_G4_se4_load_weather
ExtraTrees_G4_se4_load_weather
LightGBM_G4_se4_load_weather if lightgbm installs/imports
XGBoost_G4_se4_load_weather if xgboost installs/imports
```

P0054D metrics may be reused as evidence-summary baseline only if the same dataset construction is confirmed. Prefer rerunning all models in one comparable run if practical.

If runtime is high, Codex may prioritize:

```text
1. ExtraTrees baseline rerun or P0054D evidence comparison
2. LightGBM
3. XGBoost
4. HGB/MLP reference if time permits or if already built by shared pipeline
```

But any claimed winner must use identical rows and clearly state whether comparison is same-run or evidence-summary.

## Hyperparameter policy

Use sensible bounded first-pass hyperparameters. Do not perform broad hyperparameter search unless the package can do it without leaking holdout or consuming excessive time.

Suggested initial LightGBM parameters:

```text
objective=regression
metric=mae
n_estimators around 500-1200
learning_rate around 0.03-0.08
num_leaves bounded
feature_fraction / bagging_fraction if supported
random_state=54
n_jobs=-1
```

Suggested initial XGBoost parameters:

```text
objective=reg:squarederror or reg:absoluteerror if supported
n_estimators around 500-1200
learning_rate around 0.03-0.08
max_depth bounded
subsample / colsample_bytree if supported
random_state=54
n_jobs=-1
tree_method=hist if supported
```

Validation split may be used for early stopping or model selection. Holdout must not be used for model selection.

## Evaluation

Direct horizons:

```text
1h, 3h, 6h, 12h, 24h, 48h, 72h, 96h, 120h, 144h, 168h
```

Weekly 168h path evaluation on holdout:

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
```

## Required comparisons

P0054E must report:

```text
1. Installed/imported dependency versions.
2. Whether LightGBM ran to completion.
3. Whether XGBoost ran to completion.
4. Best model by direct holdout MAE.
5. Best model by weekly MAE_full_168h.
6. LightGBM vs ExtraTrees.
7. XGBoost vs ExtraTrees.
8. Whether any new model beats P0054D ExtraTrees by >= 2% holdout MAE or weekly MAE_full_168h.
9. Conditional regimes where the new models improve or fail.
10. Whether this suggests follow-up with tuned boosting, sequence models, or stopping SE4 consumption model work for now.
```

Learning threshold:

```text
A model is interesting if it improves holdout MAE or weekly MAE_full_168h by >= 2%, or improves >= 3% in at least two important conditional regimes, compared with P0054D ExtraTrees.
```

This is a LABB learning threshold, not a production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054E/CHANGELOG.md
requirements/package-runs/P0054E/review.md
requirements/package-runs/P0054E/design.md
requirements/package-runs/P0054E/functions.md
requirements/package-runs/P0054E/labb-label.md
requirements/package-runs/P0054E/environment-before-install.md
requirements/package-runs/P0054E/dependency-install-evidence.md
requirements/package-runs/P0054E/import-validation.md
requirements/package-runs/P0054E/dataset-contract.md
requirements/package-runs/P0054E/input-classification.md
requirements/package-runs/P0054E/feature-groups.md
requirements/package-runs/P0054E/model-training-evidence.md
requirements/package-runs/P0054E/lightgbm-results.md
requirements/package-runs/P0054E/xgboost-results.md
requirements/package-runs/P0054E/model-comparison.md
requirements/package-runs/P0054E/direct-horizon-results.md
requirements/package-runs/P0054E/weekly-168h-path-results.md
requirements/package-runs/P0054E/conditional-regime-results.md
requirements/package-runs/P0054E/feature-importance-or-attribution.md
requirements/package-runs/P0054E/interpretation.md
requirements/package-runs/P0054E/what-we-learned.md
requirements/package-runs/P0054E/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
modeling-dataset-sample.csv
training-history.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
memory/energy-market-ai-lab.md
memory/energy-market-simulator-ambition.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054D-labb-se4-load-weighted-weather-proxy-and-advanced-model-rerun.md
requirements/package-runs/P0054D/CHANGELOG.md
requirements/package-runs/P0054D/se4-weather-proxy-validation.md
requirements/package-runs/P0054D/model-comparison.md
requirements/package-runs/P0054D/additional-advanced-model-results.md
requirements/package-runs/P0054D/what-we-learned.md
relevant local source files for P0054D modeling experiment
current local Python environment/dependency files if present
```

Do not read large raw data files during bootstrap unless required by package verification commands.

## Files allowed to change

```text
requirements/packages/P0054E-labb-se4-lightgbm-xgboost-install-and-test.md
requirements/package-runs/P0054E/**
docs/functions/mac/spotprice-model-diagnostics.md if durable function/lab docs need updating
requirements or environment/dependency files only if an existing repository convention makes that appropriate
src/mac/** relevant existing LABB modeling scripts if changes are needed
tests/mac/** relevant tests for changed modeling code
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No price features.
No production/export/import/A61/future-flow features.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054E.
```

## Live/API/device policy

Live testing allowed: no.

Device/API/runtime actions allowed: no.

Package may access Python package indexes only for installing LightGBM/XGBoost dependencies into the approved local Mac LABB environment. This is dependency setup, not device/runtime work.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
python environment captured before install
lightgbm/xgboost install/import status captured after install
se4_load_weather exists and covers modeled period
target/split validation follows P0053C
feature matrix contains no forbidden columns
all claimed model comparisons use identical rows
weekly 168h paths are complete or skipped with reason
no large data/model/env artifacts are staged
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- LightGBM and/or XGBoost installed/imported successfully.
- At least one of LightGBM/XGBoost trained and evaluated on SE4 with se4_load_weather.
- Comparison to P0054D ExtraTrees is reported.
- Best model by holdout and weekly 168h metrics is identified.
- No forbidden features or runtime/device actions occurred.
```

WARN is acceptable if:

```text
- only one of LightGBM/XGBoost installs or runs successfully.
- install succeeds but one model is too slow or fails with documented error.
- comparison to P0054D is evidence-summary rather than same-run for some baseline models.
- no new model beats ExtraTrees but the result is clean and informative.
```

STOP if:

```text
- dependency installation would require unsafe system changes.
- neither LightGBM nor XGBoost can be installed/imported.
- forbidden price/production/flow/A61/future features enter the model matrix.
- holdout is used for model selection.
- device/API/runtime work is created.
```

## Expected Codex output

```text
PASS/WARN/STOP status
python/dependency environment summary
install commands and versions
LightGBM import/train/result status
XGBoost import/train/result status
best model by direct holdout MAE
best model by weekly 168h path MAE
LightGBM/XGBoost vs P0054D ExtraTrees comparison
conditional/regime findings
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no price/API/device/A61/leakage work
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

Implemented in P0054E.

Result:

```text
status: PASS
LightGBM import/train/evaluate: PASS
XGBoost import/train/evaluate: PASS
same-run direct rows: 382106
weekly complete 168h origins: 51
```

Dependency setup:

```text
python3 -m pip install --user lightgbm xgboost
brew install libomp
lightgbm: 4.6.0
xgboost: 2.1.4
libomp: 22.1.7
```

Best direct holdout MAE:

```text
LightGBM_G4_se4_load_weather: 17.70265003542135
ExtraTrees_G4_se4_load_weather: 18.61057286241044
XGBoost_G4_se4_load_weather: 18.130349153087128
```

Best weekly 168h MAE:

```text
XGBoost_G4_se4_load_weather: 18.251117862247646
LightGBM_G4_se4_load_weather: 18.472268705116658
ExtraTrees_G4_se4_load_weather: 19.605137961494318
```

Both LightGBM and XGBoost beat P0054D ExtraTrees by the LABB learning threshold:

```text
LightGBM vs P0054D ExtraTrees:
  holdout MAE: -4.878532400380407%
  weekly MAE_full_168h: -5.778430422691697%

XGBoost vs P0054D ExtraTrees:
  holdout MAE: -2.5803811246094015%
  weekly MAE_full_168h: -6.906455348113622%
```

Interpretation:

```text
candidate_for_followup
```

Recommended next package:

```text
P0054F bounded tuned boosting on validation only, still LABB, with no runtime promotion.
```

Verification run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054e
PYTHONPYCACHEPREFIX=/private/tmp/p0054e-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054e.py tests/mac/services/spotprice_model_diagnostics/test_p0054e.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054e-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054e
```

No runtime, device, Shelly, Home Assistant, KVS, deploy, production model, price, production, flow/export/import, A61 or future-leakage inputs were used. No model binaries, virtualenvs, wheels, caches or large raw datasets were committed.
