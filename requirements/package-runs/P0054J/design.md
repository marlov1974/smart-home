# P0054J Implementation Design

## Package Interpretation

Train paired SE1 consumption models with and without P0054H price forecast features. Score final comparisons only on June 2025 onward.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054j.py
tests/mac/services/spotprice_model_diagnostics/test_p0054j.py
```

The module will:

1. load SE1 consumption rows from `physical_balance_se1_se4_hourly_v1`
2. load SE1 weather proxy rows from `weather_area_hourly` with `area_proxy='se1_core_weather'`
3. load P0054H forecast-safe price rows with required filters
4. build direct horizon rows and weekly 168h path rows
5. attach calendar, lag, rollup, weather proxy and price forecast path features
6. split rows into `train_fit` and `holdout`
7. fit paired no-price and with-price models for HGB, ExtraTrees, LightGBM and XGBoost when importable
8. optionally skip MLP with documented runtime/pipeline rationale
9. write compact evidence and samples

## Intended Changes

Allowed package scope:

```text
src/mac/services/spotprice_model_diagnostics/p0054j.py
tests/mac/services/spotprice_model_diagnostics/test_p0054j.py
requirements/package-runs/P0054J/**
requirements/packages/P0054J-labb-se1-consumption-spotprice-forecast-ai.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Test Strategy

Unit tests:

- P0054I split assignment
- price path features use only rows from the same forecast origin
- no-price and with-price feature contracts do not include forbidden terms
- row-set fairness detects unequal paired rows

Execution verification:

- run `python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054j`
- run `python3 -m src.mac.services.spotprice_model_diagnostics.p0054j`
- inspect evidence summaries
- run `git diff --check`
- confirm no large artifacts are staged

## Risks And Uncertainties

LightGBM/XGBoost runtime may be non-trivial. The package should use bounded hyperparameters and no broad search.

P0054H price source is a simple historical price baseline, not M4. If it hurts model quality, that is still a clean LABB result.
