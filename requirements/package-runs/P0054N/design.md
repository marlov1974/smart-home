# P0054N Design

## Interpretation

Build a LABB-only SE3 consumption evaluation for exact DayAhead-style 36h forecast paths. The core target is `consumption_se3_mw`; split policy is P0054I/J/K/M train-fit through `2025-05-31` and holdout from `2025-06-01`.

The repository convention uses `horizon_h = horizon_hours + 1`, so P0054N full_36h is `horizon_h 1..36`, corresponding to target hours `origin..origin+35h`.

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0054n.py`.

The module will:

- load SE3 consumption rows and weather proxy rows via P0054K.
- load SE3 price source rows via P0054L2.
- build exact local 12:00 D-1 origins for train-side blocked and holdout windows.
- generate in-memory advanced price rows for horizons 0..35 with P0054L2 feature logic and deterministic model specs.
- build consumption modeling rows with P0054M/P0054K row construction logic.
- train paired no-price and with-advanced-price HGB, ExtraTrees, LightGBM and XGBoost variants where imports are available.
- score complete holdout 36h paths and DayAhead delivery-day slices.
- write compact package-run evidence under `requirements/package-runs/P0054N/`.

## Deliberate Refactoring

No broad refactor. P0054N reuses P0054K/P0054M helpers directly. New helpers are package-local because exact DayAhead origin handling is a P0054N experiment and should not alter prior package behavior.

## Test Strategy

Add `tests/mac/services/spotprice_model_diagnostics/test_p0054n.py` for:

- Europe/Stockholm DayAhead origin conversion around DST.
- full_36h complete-origin filtering and horizon convention.
- DayAhead delivery-day row selection.
- matrix safety rejecting holdout price protocol in train rows.
- advanced price ablation delta convention.

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054n
python3 -m src.mac.services.spotprice_model_diagnostics.p0054n
git diff --check
```

## Risks And Uncertainties

The advanced price feature is package-local and in-memory for exact 12:00-local origins because the persisted P0054M/P0054L2 logs only contain `23:00Z` origins. Results should therefore be interpreted as a P0054N exact-origin LABB extension of the P0054M protocol, not as a direct read from the persisted advanced-price log.

Weather remains an actual-history LABB proxy unless a separate forecast weather source is later introduced.

If a model family import is unavailable, P0054N may WARN if ExtraTrees and XGBoost still run.
