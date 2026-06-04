# P0054E Review

Package: P0054E
Label: LABB
Result: WARN

## Understanding

P0054E is a Mac-local LABB package that tests whether LightGBM and/or XGBoost improve the P0054D SE4 no-price consumption experiment using the corrected `se4_load_weather` proxy and the same `G4_calendar_load_lags_rollups_weather_proxy` feature group.

The package is not a G2-KANDIDAT evaluation and must not create runtime, device, Shelly, Home Assistant, KVS, deploy, production model, price, production, flow/export/import, A61 or future-leakage changes.

## Repository Evidence

- `memory/energy-market-ai-lab.md` defines this work as `LABB` by default and allows proxy weather only when clearly labeled non-deployable.
- `memory/spotprice-forecast-period-policy.md` defines the P0053C target rows and train/validation/holdout split required by P0054E.
- `requirements/package-runs/P0054D/model-comparison.md` establishes the P0054D baseline: `ExtraTrees_G4_se4_load_weather` holdout MAE `18.610572862410447` and weekly 168h MAE `19.605137961494325`.
- `src/mac/services/spotprice_model_diagnostics/p0054d.py` already contains leakage-safe SE4 row construction, lag/rollup features, split assignment, direct metrics, weekly 168h path metrics, conditional metrics and evidence helpers that can be reused or mirrored.
- `docs/functions/mac/spotprice-model-diagnostics.md` documents these diagnostics as Mac-only and non-runtime.

## Environment Evidence Before Install

- Python executable: `/Library/Developer/CommandLineTools/usr/bin/python3`
- Python version: `3.9.6`
- venv detected: `false`
- conda detected: none
- virtualenv detected: none
- platform: `macOS-26.4.1-arm64-arm-64bit`
- machine: `arm64`
- pip: `pip 21.2.4`
- numpy import: `2.0.2`
- sklearn import: `1.6.1`
- pandas import: unavailable
- lightgbm import: unavailable
- xgboost import: unavailable

No repository dependency file or project venv convention was found with the inspected dependency-file patterns.

## Consistency Classification

`WARN`

The package is implementable and inside LABB scope, but there is no existing project-local venv or dependency file. To avoid a broad dependency-management change, P0054E will use Mac user-site installation only:

```text
python3 -m pip install --user lightgbm xgboost
```

This is documented as LABB environment setup, not as a G2 runtime dependency. If either package cannot be installed/imported safely, P0054E will document the blocker and continue with the other package if available.

## Scope Guardrails

- No device/API/runtime work.
- No Shelly, Home Assistant, KVS or deploy changes.
- No price, production, flow, export/import, A61, capacity/utilization/margin or future target-window actual features.
- No holdout use for model selection.
- No committed packages, caches, virtualenv folders, wheel files, model binaries or large raw datasets.
