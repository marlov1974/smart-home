# P0043 implementation design

## Package interpretation

P0043 trains the first AI model in the seven-day index track: AI-2 hour-to-day `hour_shape`.

The package uses only the corrected P0042 fixed-CET dataset table:

```text
ai2_hour_to_day_training_targets_v2
```

## Chosen implementation structure

Add `src/mac/services/spotprice_model_diagnostics/p0043.py`.

The module will:

- Load corrected P0042 AI-2 rows from the local feature DB.
- Validate required fixed-CET and target fields.
- Split chronologically by `model_cet_date`:
  - train through 2024-12-31
  - validate through 2025-12-31
  - holdout from 2026-01-01
- Train and evaluate separate target-series models.
- Compare baselines B0/B1/B2/B3 and feature groups F0-F4.
- Use deterministic categorical encoding for calendar/special-day fields.
- Use `HistGradientBoostingRegressor` with bounded parameters.
- Evaluate centered predictions as default if daily prediction means are non-zero.
- Write evidence and small JSON configs, not binary model artifacts.

## Feature groups

- F0 time only.
- F1 time plus calendar.
- F2 F1 plus actual weather.
- F3 F2 plus normal/delta weather.
- F4 F3 plus relative-to-day/rank weather features.

## Model selection

For each target series, select the feature group with the best validation MAE. If validation MAE is exactly tied, choose the simpler feature group.

## Test strategy

Unit tests cover dataset contract, chronological split, train-only baselines, deterministic categorical encoding, separate target training, finite predictions and forbidden path constants.

Package verification runs the P0043 training command, P0041-P0043 tests, relevant regression tests and `git diff --check`.

## Risks

If baselines already capture most intraday shape, HGB may improve rank metrics more than MAE. P0043 reports this as WARN only if SE1 fails the package PASS criteria.
