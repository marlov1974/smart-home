# P0054O Design

## Interpretation

P0054O estimates how sensitive P0054N's SE3 full_36h and DayAhead delivery-day consumption forecasts are to imperfect temperature forecasts. It keeps P0054N's exact DayAhead timing and safe exact-origin advanced price protocol, then injects deterministic synthetic temperature error.

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0054o.py`.

The module will:

- build the same exact-origin P0054N base rows.
- discover temperature-like P0054N weather features.
- preserve a no-noise baseline for the selected models.
- for seeds `1000..1009`, apply `uniform(-2,+2)` noise to source temperature weather columns in both train_fit and holdout rows before model training.
- recompute train-fit temperature profiles after noise.
- train selected variants:
  - `HGB_no_price`
  - `LightGBM_no_price`
  - `LightGBM_with_p0054n_exact_dayahead_advanced_price`
  - `XGBoost_no_price`
- evaluate full_36h and DayAhead delivery-day metrics with P0054N helpers.
- report mean/std/min/max seed distributions, percent-of-load metrics, daily energy error percent and price-feature comparison for LightGBM.
- write required evidence under `requirements/package-runs/P0054O/`.

## Deliberate Refactoring

No broad refactor. P0054O adds package-local helpers and reuses P0054N/P0054K functions. P0054N behavior is not changed.

## Test Strategy

Add `tests/mac/services/spotprice_model_diagnostics/test_p0054o.py` for:

- deterministic uniform noise by seed.
- noise range stays within ±2°C.
- only selected source temperature columns are perturbed.
- percent-of-load and daily energy percent calculations.

Verification commands:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054o
python3 -m src.mac.services.spotprice_model_diagnostics.p0054o
git diff --check
```

## Risks And Uncertainties

Weather remains a LABB proxy. Synthetic uniform temperature noise is not a calibrated real forecast-error distribution.

The model set is intentionally narrower than P0054N full comparison to keep runtime practical while covering the package-required winner, with-price comparison and XGBoost comparison.
