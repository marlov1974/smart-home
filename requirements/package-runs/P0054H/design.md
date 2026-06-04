# P0054H Implementation Design

## Package Interpretation

Create a local forecast-origin log for SE1 anchored absolute price forecasts across train, validation and holdout under P0053C. The package explicitly allows a simpler origin-local anchored baseline when safe M4 training is not practical.

## Chosen Implementation Structure

Add a narrow Mac diagnostics module:

```text
src/mac/services/spotprice_model_diagnostics/p0054h.py
```

The module will:

1. load SE1 hourly source prices from local SQLite
2. select complete 168h daily forecast-origin windows whose target hours all belong to one canonical split
3. produce forecast rows using only pre-origin price history
4. persist rows to a local SQLite forecast-origin log table
5. compute coverage, leakage checks and validation/holdout price metrics
6. compare validation/holdout metrics to P0053C-B when that table exists
7. write package-run evidence under `requirements/package-runs/P0054H/`

## Forecast Method

Output table:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
```

Method:

```text
source_model_family = P0054H_origin_local_history_baseline
training_protocol = origin_local_no_fit_pre_origin_history
prediction_kind = anchored_absolute_price
area = SE1
```

Prediction rule, in priority order:

1. previous-week same-hour price, if `target_timestamp_utc - 168h < forecast_origin_timestamp_utc`
2. mean of prior 48h prices with the same fixed-CET hour, if available
3. median of the prior 48h prices

This is an anchored absolute price path because every path is anchored entirely to observed pre-origin price levels. It is not M4 and does not use P0045 AI1/AI2 shape predictions.

## Intended Changes

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054h.py
tests/mac/services/spotprice_model_diagnostics/test_p0054h.py
requirements/package-runs/P0054H/**
```

Update:

```text
requirements/packages/P0054H-labb-rolling-origin-se1-price-forecast-log.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Deliberate Refactoring Decisions

No broad refactor of P0045/P0053C-B is planned. Rolling or expanding M4 retraining would be a larger modeling protocol. This package creates a safer baseline source now and documents its limitations.

## Test Strategy

Unit tests:

- prediction uses previous-week same-hour when available and safe
- fallback uses prior-48h same-hour/median without target-window data
- leakage review rejects bad cutoff/origin/history ordering
- forecast log rows contain required schema semantics

Generation verification:

- run `python3 -m src.mac.services.spotprice_model_diagnostics.p0054h`
- confirm table exists
- query coverage by target split and forecast-origin split
- query cutoff/origin/history violations
- run `python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054h`
- run `git diff --check`
- confirm no large generated artifacts are staged

## Risks And Uncertainties

The generated source will likely be weaker than P0053C-B because it does not use M4 shape. That is acceptable under P0054H WARN if the source is safe and sufficiently covered for downstream ablation.

P0054I/P0054F retry should compare downstream usefulness carefully and label this input as a simple forecast-safe price baseline.
