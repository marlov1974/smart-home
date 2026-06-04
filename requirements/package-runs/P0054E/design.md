# P0054E Design

Package: P0054E
Label: LABB

## Interpretation

P0054E installs and tests stronger boosted tree families against the P0054D corrected SE4 consumption setup:

- target: `consumption_se4_mw`
- source table: `physical_balance_se1_se4_hourly_v1`
- weather proxy: `se4_load_weather`
- weather label: `weather_actual_as_forecast_proxy`
- feature group: `G4_calendar_load_lags_rollups_weather_proxy`
- split policy: P0053C global split
- baseline to beat: P0054D `ExtraTrees_G4_se4_load_weather`

The output is LABB evidence only. No production model or runtime artifact is created.

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0054e.py`.

The module will reuse P0054D helpers where practical for dataset construction, leakage-safe lags/rollups, split assignment, feature contract validation and metric calculations. P0054E-specific code will add:

- environment/import status capture for LightGBM and XGBoost
- optional model builders for LightGBM and XGBoost
- same-run ExtraTrees baseline comparison
- direct holdout, weekly 168h path and conditional regime comparisons
- feature importance extraction when supported
- P0054E evidence writing

Add `tests/mac/services/spotprice_model_diagnostics/test_p0054e.py` for package-specific contract checks.

## Intended Changes

- Add P0054E package-run evidence files.
- Add P0054E Mac-only diagnostic module.
- Add tests for dependency status handling, identical-row comparison and forbidden-feature contract.
- Mark the P0054E package complete after verification.
- Update `docs/functions/mac/spotprice-model-diagnostics.md` only if durable function documentation changes are needed after implementation.

## Deliberate Non-Changes

- No runtime service changes.
- No Shelly, Home Assistant, KVS or deploy changes.
- No repository dependency framework unless an existing convention is discovered later.
- No broad refactor of P0054D.
- No committed model binaries, wheels, virtualenvs, caches or large raw datasets.

## Installation Plan

Because no repo-local venv or dependency file was found, install optional LABB dependencies in the Python user site:

```text
python3 -m pip install --user lightgbm xgboost
```

Record before/after environment, exact command, install output summary and import versions in package-run evidence.

Implementation note: both Python wheels installed successfully but required OpenMP runtime `libomp.dylib` to import on Mac arm64. Homebrew was available and P0054E installed `libomp` with:

```text
brew install libomp
```

This was recorded in `dependency-install-evidence.md` as Mac-local LABB setup, not a repository runtime dependency.

## Model Policy

The claimed same-run comparison will include:

- `ExtraTrees_G4_se4_load_weather`
- `LightGBM_G4_se4_load_weather` if installed/imported
- `XGBoost_G4_se4_load_weather` if installed/imported

HGB/MLP P0054D metrics may be referenced as evidence-summary baseline, but P0054E will not claim a same-run HGB/MLP comparison unless it reruns them.

Validation may be used for early stopping or bounded parameter choice. Holdout is evaluation only.

## Test And Verification Strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054e
PYTHONPYCACHEPREFIX=/private/tmp/p0054e-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054e.py tests/mac/services/spotprice_model_diagnostics/test_p0054e.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054e-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054e
git diff --check
```

Also verify:

- Python/dependency environment captured before install.
- LightGBM/XGBoost install/import status captured after install.
- `se4_load_weather` exists and covers modeled period.
- P0053C split policy is used.
- feature matrix contains no forbidden columns.
- all claimed same-run model comparisons use identical row sets.
- weekly 168h paths are complete or skipped with reason.
- no large data/model/env artifacts are staged.

## Risks And Uncertainties

- LightGBM or XGBoost wheels may be unavailable for the current CommandLineTools Python and macOS/arm64 combination.
- XGBoost may be slow on the full direct-horizon row set. If needed, bounded first-pass hyperparameters will be used, but comparisons will still use identical rows.
- User-site installation is less isolated than a project venv, but avoids changing repository dependency management.
