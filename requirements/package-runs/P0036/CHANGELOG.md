# P0036 changelog

## 2026-05-31

- Added train-only M1 baselines for fair M4 residual training/evaluation.
- Changed primary M4 residual estimator to bounded `HistGradientBoostingRegressor`.
- Removed unsafe unbounded polynomial time extrapolation from the primary feature/model path.
- Added P0036 holdout, baseline, candidate timing, model-selection and promotion evidence.
- Promoted the P0036 HGB M4 model after PASS quality gate.
- Updated `docs/functions/mac/spotprice-ml-normal-model.md`.
