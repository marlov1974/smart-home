# Spotprice Model Diagnostics

Last changed: P0048

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

## P0047 SE3-SE1 Spread Diagnostics

`p0047.run_p0047_analysis(...)` orchestrates the SE3-SE1 spread export and bottleneck/regime diagnostics.

Important functions:

`load_p0047_source_rows(...)` reads corrected P0042 AI2 v2 rows from the local feature DB.

`validate_p0047_contract(...)` verifies required fixed-CET fields and target availability.

`join_spread_rows(...)` joins `system_proxy_se1` and `area_diff_proxy_se3` hourly rows by `timestamp_utc` and reconstructs `se3_price = se1_price + se3_minus_se1`.

`threshold_candidates(...)` computes fixed, quantile and robust-sigma spread threshold candidates.

`assign_spread_regime(...)` assigns near-zero, positive, negative and spike regime labels.

`analyze_persistence(...)` computes regime run lengths and transition counts.

`analyze_signal_attribution(...)` summarizes correlation and regime means for available weather, price and calendar signals.

`write_p0047_evidence(...)` writes package-run CSV, Markdown and JSON evidence under `requirements/package-runs/P0047/`.

P0047 is diagnostics/export-only. It explicitly forbids SE1-to-SE3 anchoring, SE3 API work, production model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0048 SE3-SE1 Bottleneck Feature And Exploratory Models

`p0048.run_p0048_analysis(...)` orchestrates SE3-SE1 bottleneck feature construction, local dataset persistence and exploratory non-deployable modeling.

Important functions:

`build_base_spread_rows(...)` joins corrected AI2 SE1 and area-diff rows and reconstructs `se3_price` and `se3_minus_se1`.

`load_weather_feature_rows(...)` reads local weather proxy source rows for south, central, north and system-oriented wind, solar and temperature features.

`derive_weather_features(...)` attaches actual weather proxy fields, computes fixed-CET seasonal normals/deltas and derives gradient fields.

`add_regime_labels(...)` applies P0047 robust-sigma thresholds to binary and multiclass regime targets.

`add_lagged_features(...)` adds previous-hour and previous-day spread/regime diagnostics using only earlier timestamps.

`assign_chronological_splits(...)` assigns train/validate/holdout by fixed-CET model date.

`persist_modeling_dataset(...)` writes the local SQLite table `se3_se1_bottleneck_training_dataset_v1`.

`evaluate_stage1_classifiers(...)`, `evaluate_stage2_regressors(...)` and `evaluate_continuous_spread_baselines(...)` run exploratory sklearn diagnostics and return metrics only.

`write_p0048_evidence(...)` writes package-run Markdown, CSV and JSON evidence under `requirements/package-runs/P0048/`.

P0048 is diagnostics-only. It explicitly forbids SE1-to-SE3 anchoring, SE3 API work, production model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.
