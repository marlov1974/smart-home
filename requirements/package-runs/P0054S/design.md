# P0054S Implementation Design

Status: `planned-before-code`

## Interpretation

P0054S is the spot-price equivalent of P0054R. It tests advanced no-leakage SE3 price models against the P0054L2 `Ensemble` baseline and P0054K origin-local baseline. It evaluates price forecast quality directly; it does not claim consumption-model improvement or production readiness.

## Implementation Structure

- Add `src/mac/services/spotprice_model_diagnostics/p0054s.py`.
- Reuse P0054L2 source loading, feature construction, matrix standardization, model specs, and direct/weekly/ranking metrics.
- Add P0054S-specific internal-validation model fits, weighted/median/stacked-style ensembles, residual correction, horizon-bucket specialization, horizon-bias correction, DayAhead selection, optional forecast-log recommendation, and evidence writing.
- Add focused tests in `tests/mac/services/spotprice_model_diagnostics/test_p0054s.py`.
- Update `docs/functions/mac/spotprice-model-diagnostics.md` with durable P0054S entries.

## Split Policy

- `train_fit`: `2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z`.
- `holdout`: `target_timestamp_utc >= 2025-06-01T00:00:00Z`.
- `internal_train`: train_fit rows before `2025-03-01T00:00:00Z`.
- `internal_validation`: train_fit rows from `2025-03-01T00:00:00Z` through May 2025.
- Holdout is not used for fitting, early stopping, hyperparameter selection, feature selection, ensemble weights, correction layers or model-family selection.

## Intended Methods

Tier 0:

- Reproduce comparable HGB, ExtraTrees, LightGBM, and XGBoost model rows using the P0054L2 feature contract.
- Include P0054K baseline metrics and P0054L2 `Ensemble` comparison.

Tier 1:

- Weighted ensemble using inverse internal-validation MAE weights.
- Median ensemble over completed base families.
- Stacked-style linear blend trained on internal-validation predictions only.
- Residual correction on top of the best internal-validation baseline.
- Horizon-bucket specialized models using train_fit only.
- Horizon-bias correction on ensemble predictions using internal-validation errors only.
- DayAhead-specialized price model for exact 12:00 Europe/Stockholm D-1 delivery-day rows.

Tier 2:

- Check PyTorch/TensorFlow import status. Skip with WARN evidence if not practical after Tier 1 completion.

Tier 3:

- High/low-price and ramp/spike interpretation through existing P0054L2 ranking/spike/ramp metrics. Add bias correction evidence if useful.

## Forecast Log Decision

If a P0054S model improves at least 5% over P0054L2 Ensemble direct MAE or full_168h MAE, create/identify `advanced_spotprice_forecast_log_p0054s_se3_v1`. If not, write `no_p0054s_advanced_source_recommended`. Any log is holdout-safe evaluation output, not a rolling train-period downstream feature source.

## Risks

- Advanced methods can overfit internal validation or reduce ranking/spike quality while improving broad MAE. Evidence must separate broad MAE and ranking/spike/ramp metrics.
- P0054L2’s direct and weekly metrics are on identical persisted rows; P0054S must document row comparability if it reconstructs rather than reads the persisted L2 log.
- Neural models may be unavailable or too slow. This remains WARN if Tier 1 completes.

## Verification Commands

Final commands:

```text
/usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054s
/usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054s
git diff --check
git status --short --branch
```

The package run writes evidence for SE3 target source, split policy, strict pre-origin feature audits, P0054K/P0054L2 baseline comparison, internal-validation-only weights/corrections, direct/full_168h/DayAhead/ranking metrics, forecast-log decision, leakage review, no live API/devices/A61/NordPool/workplace integration, and no large artifacts.
