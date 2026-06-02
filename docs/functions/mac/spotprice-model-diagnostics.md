# Spotprice Model Diagnostics

Last changed: P0046

## Module

```text
src.mac.services.spotprice_model_diagnostics
```

## Purpose

Mac-only historical diagnostics for spot-price model packages. These modules read local SQLite feature/history data and write package-run evidence. They do not create production APIs, call devices, write KVS, deploy Shelly code or alter Home Assistant.

## P0046 Anchored Absolute-Price Backtest

`p0046.run_p0046_backtest(...)` orchestrates the SE1-first anchored absolute-price backtest for P0045's selected `combined_scaled` 168h shape.

Important functions:

`build_origin_windows(...)` builds Monday 06:00 fixed-CET windows with exactly 168 hourly rows.

`window_shape_predictions(...)` reuses P0045 regenerated AI-1/AI-2 predictions to produce the selected combined SE1 shape plus diagnostic baselines.

`fit_anchor(...)` fits deterministic L1/L2/L3 anchoring parameters from anchor hours only.

`apply_anchor(...)` transforms centered shape forecasts into absolute price forecasts.

`evaluate_anchored_window(...)` evaluates only the hours after the selected anchor region.

`select_se1_configuration(...)` selects the deployable SE1 anchoring configuration from validation metrics only.

`write_p0046_evidence(...)` writes package-run evidence under `requirements/package-runs/P0046/`.

## Safety

P0046 is diagnostics-only. It explicitly forbids AI retraining, production API work, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.
