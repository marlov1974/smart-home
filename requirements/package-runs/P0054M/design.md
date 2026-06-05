# P0054M Implementation Design

## Package Interpretation

P0054M evaluates SE3 consumption models with and without P0054L2-compatible advanced SE3 price forecast features. It remains `LABB`, not `G2-KANDIDAT`.

## Price Feature Protocol

Selected protocol:

```text
price_feature_protocol = rolling_oof_train_plus_holdout
```

Implementation detail:

- Build P0054L2-compatible SE3 price examples from reconstructed SE3 price rows.
- Train HGB, ExtraTrees, LightGBM and XGBoost price models only on rows with target timestamps before `2025-03-01T00:00:00Z`.
- Predict train-side advanced price features for `2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z`.
- Average completed model predictions into an Ensemble row.
- Use existing P0054L2 Ensemble rows for holdout targets.
- Train consumption no-price and with-price variants on identical train rows with safe train-side price coverage.

This is safe but partial train_fit coverage. It is not a full rolling forecast source across all train_fit.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054m.py
tests/mac/services/spotprice_model_diagnostics/test_p0054m.py
requirements/package-runs/P0054M/**
```

Update:

```text
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054M-labb-se3-consumption-with-advanced-spotprice-forecast.md
```

## Test Strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054m
python3 -m src.mac.services.spotprice_model_diagnostics.p0054m
git diff --check
```

Verification covers:

- SE3 consumption target contract.
- P0054L2 advanced holdout source contract.
- P0054M blocked train-side price source contract.
- Paired no-price/with-price consumption row sets.
- No forbidden feature names.
- No holdout price forecast used as train feature.
- Leakage review.
- No large data/model/env artifacts staged.

## Risks and Uncertainties

- Train-side advanced price coverage is limited to 2025-03..2025-05, so consumption models train on a narrower subset than P0054K.
- If a model family fails, completed model evidence remains useful.
- A negative result is still valid evidence: a better price forecast may not improve generic SE3 consumption models.
