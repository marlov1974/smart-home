# P0054R Implementation Design

Status: `planned-before-code`

## Interpretation

P0054R is an offline LABB experiment testing advanced no-price methods for SE3 consumption forecasting on the corrected ENTSO-E Actual Total Load target. It compares against P0054Q corrected-target baselines and reports DayAhead, full_36h, daily-energy, percent-error, conditional-regime, leakage, and interpretation evidence.

## Implementation Structure

- Add `src/mac/services/spotprice_model_diagnostics/p0054r.py`.
- Reuse P0054Q target loading and evidence conventions.
- Reuse P0054M/P0054N row construction and exact DayAhead origin semantics.
- Reuse P0054K model feature matrix helpers, model specs, prediction helpers, and conditional regime evaluation.
- Add package-local advanced helpers for internal train/validation split, model fitting on explicit row subsets, inverse-MAE ensemble weights, residual correction, horizon-specialized models, DayAhead-specialized models, and checkpoint evidence.
- Add focused unit tests in `tests/mac/services/spotprice_model_diagnostics/test_p0054r.py`.
- Update `docs/functions/mac/spotprice-model-diagnostics.md` with durable function catalog entries for P0054R.

## Split And Leakage Policy

- Target rows start at `2022-06-01T00:00:00Z`.
- `train_fit`: target timestamp `< 2025-06-01T00:00:00Z`.
- `holdout`: target timestamp `>= 2025-06-01T00:00:00Z`.
- Internal validation:
  - `internal_train`: target timestamp `< 2025-03-01T00:00:00Z`.
  - `internal_validation`: `2025-03-01T00:00:00Z <= target timestamp < 2025-06-01T00:00:00Z`.
- Baseline final models fit on all train_fit and predict holdout.
- Ensemble weights and correction choices are fitted only from internal_train/internal_validation predictions.
- Holdout is not used for fitting, early stopping, feature selection, hyperparameter selection, ensemble weighting, model-family selection, or correction fitting.

## Intended Methods

Tier 0:

- Reproduce no-price HGB, ExtraTrees, LightGBM, and XGBoost if libraries are available; P0054Q comparison records the required LightGBM/XGBoost/HGB baselines.

Tier 1:

- Weighted ensemble of HGB + ExtraTrees + LightGBM + XGBoost using inverse internal-validation MAE weights.
- Median ensemble as a robust non-parametric ensemble.
- Residual correction on top of the best internal-validation baseline, fitted on internal-validation residuals only and applied to final holdout predictions.
- Horizon-specialized HGB no-price model with one model per horizon.
- DayAhead-specialized HGB no-price model trained on train_fit rows matching exact 12:00 Europe/Stockholm D-1 delivery-day semantics.

Tier 2:

- Check PyTorch/TensorFlow import status. Skip with WARN evidence unless a lightweight dependency is already available and practical after Tier 1 completes.

Tier 3:

- Fit a horizon bias correction from internal-validation errors and apply it as a path-structured correction to weighted ensemble predictions.

## Evidence Strategy

Write compact Markdown, JSON, and CSV evidence under `requirements/package-runs/P0054R/`. Persist method checkpoints after each completed method in `model-checkpoints/README.md` and the top-level method result files. Do not persist model binaries or raw full datasets beyond compact samples/metrics.

## Risks And Mitigations

- Runtime may be longer than P0054Q because P0054R trains additional models. Mitigation: run methods serially and checkpoint completed evidence.
- Advanced methods may not beat LightGBM_no_price. This is acceptable as clean LABB evidence if leakage review passes.
- Weather remains actual-as-forecast proxy. Evidence must not claim production readiness or workplace-grade equivalence.
- DayAhead-specialized predictions are scoped to DayAhead evaluation; full_36h comparison must distinguish methods that cover all 36h path rows from DayAhead-only methods.

## Verification Commands

Final verification will run equivalent checks for:

```text
/usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054r
/usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054r
git diff --check
git status --short --branch
```

The package run itself writes evidence for corrected target, old-target exclusion, P0054 split, DayAhead 12:00-local timing, full_36h coverage, internal-validation-only ensemble weighting, forbidden feature review, weather proxy label, leakage review, no live API/devices/A61/NordPool/workplace integration, and no large artifacts.
