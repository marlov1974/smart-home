# Spotprice Model Diagnostics

Last changed: P0052

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

## P0049 SE3-SE1 Bottleneck Reservoir And Industrial-Response Analysis

`p0049.run_p0049_analysis(...)` orchestrates the P0049 reservoir/memory and industrial-response proxy diagnostics on top of P0048's `se3_se1_bottleneck_training_dataset_v1`.

Important functions:

`load_p0049_source_rows(...)` reads the P0048 bottleneck training dataset from the local feature DB.

`validate_p0049_contract(...)` verifies required fixed-CET fields and reconstructs `se3_minus_se1 = se3_price - se1_price`.

`add_daytype_features(...)` adds deterministic weekday, weekend, holiday, peak-hour and workday proxy fields.

`fit_price_thresholds(...)` fits SE1/SE3 train-only median, p75, p90 and p95 price thresholds.

`add_price_response_features(...)` adds threshold flags, rolling ranks, hours-since-crossing and recent high-price counters.

`add_rolling_features(...)` adds strictly backward-looking rolling mean, max, min, std, trend, binary sum and binary share features.

`add_reservoir_features(...)` builds exploratory weather/price/time pressure signals, reservoir EMA half-lives and day-type interaction fields.

`add_horizon_targets(...)` adds shifted future classification and severity targets for 1h, 3h, 6h, 12h, 24h, 48h, 72h and 168h.

`persist_analysis_dataset(...)` writes the local SQLite table `se3_se1_bottleneck_reservoir_analysis_v1`.

`evaluate_horizon_groups(...)` evaluates deterministic exploratory feature-family groups across all required horizons.

`write_p0049_evidence(...)` writes package-run Markdown, CSV and JSON evidence under `requirements/package-runs/P0049/`.

P0049 is diagnostics-only. It explicitly forbids SE1-to-SE3 anchoring, SE3 API work, production model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0050 SE3-SE1 Baseline-Corrected Demand-Response And Heat-Pump Analysis

`p0050.run_p0050_analysis(...)` orchestrates baseline-corrected SE3-SE1 residual diagnostics, local SE3 price-rank/top-N response analysis and heat-pump pressure proxy analysis.

Important functions:

`load_p0050_source_rows(...)` reads P0048's `se3_se1_bottleneck_training_dataset_v1` as the primary source and joins P0049 reservoir columns when available.

`validate_p0050_contract(...)` verifies fixed-CET fields, source temperature proxy fields, chronological splits and `se3_minus_se1 = se3_price - se1_price`.

`fit_spread_baselines(...)`, `apply_spread_baselines(...)`, `select_spread_baseline(...)` and `apply_selected_residual(...)` build train-only expected-spread baselines and selected residual fields.

`add_local_se3_rank_features(...)` adds deterministic fixed-CET day and trailing-48h SE3 price rank, percentile, top-N and bottom-N features.

`add_consumer_optimizer_response_features(...)` adds backward-looking top/bottom exposure counters and explicitly `_oracle` next-recovery diagnostics.

`add_heat_pump_pressure_features(...)` adds train-only cold thresholds, cold/high-price exposure counters and heat-debt pressure EMA features.

`add_future_targets(...)` adds same-hour and future raw/residual spread targets for response and exploratory model evaluation.

`persist_demand_response_dataset(...)` writes the local SQLite table `se3_se1_demand_response_analysis_v1`.

`write_p0050_evidence(...)` writes package-run Markdown, CSV and JSON evidence under `requirements/package-runs/P0050/`.

P0050 is diagnostics-only. It explicitly forbids SE1-to-SE3 anchoring, SE3 API work, production model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0051 SE1-SE4 Physical Balance Ingestion

`p0051.run_p0051_ingestion(...)` orchestrates eSett Open Data discovery, SE1-SE4 production/consumption ingestion, hourly aggregation, validation and initial physical-signal diagnostics.

Important functions:

`load_existing_ranges(...)` inspects the current modeling range used for overlap selection.

`fetch_esett_period(...)` fetches eSett consumption and production data for SE1-SE4 in chunks.

`parse_esett_consumption(...)` and `parse_esett_production(...)` convert eSett JSON responses into canonical source observations. Consumption source values are normalized to positive MW demand.

`aggregate_hourly(...)` converts quarter-hour source observations into hourly mean-MW canonical rows.

`build_wide_hourly(...)` creates SE1-SE4 wide rows with production, consumption, net load, north/south aggregates and south-minus-north balance fields.

`persist_physical_balance(...)` writes `physical_balance_hourly_raw_v1`, `physical_balance_hourly_v1` and `physical_balance_se1_se4_hourly_v1`.

`validate_physical_balance(...)` checks duplicates, finite values, negative values after normalization and missing required zone/measure hours.

`run_initial_diagnostics(...)` joins physical balance rows to SE3 price/SE3-SE1 diagnostics and computes explanatory correlations and top/bottom price event lifts.

`write_p0051_evidence(...)` writes package-run Markdown and JSON evidence under `requirements/package-runs/P0051/`.

P0051 is diagnostics/data-ingestion only. It explicitly forbids continental price pressure work, SE1-to-SE3 anchoring, SE3 API work, production model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0052 SE1-SE4 Transfer Flow and Import/Export

`p0052.run_p0052_ingestion(...)` orchestrates SvK Kontrollrummet / Statnett flow-map discovery, partial historical ingestion, validation and initial capacity/flow diagnostics.

Important functions:

`fetch_svk_flow_period(...)` fetches quarter-hour SvK/Statnett flow snapshots for the selected overlap range.

`parse_svk_flow_payload(...)` converts SvK flow-map JSON into normalized border-flow and SE1-SE4 import/export observations.

`directed_border_values(...)` applies the SvK direction convention: positive `A_B` means A to B, negative means B to A.

`aggregate_hourly(...)` converts quarter-hour MW observations into hourly mean-MW canonical rows.

`build_wide_hourly(...)` creates `transfer_capacity_flow_se1_se4_hourly_v1` with internal signed flows, SE1-SE4 import/export/net import, pressure features and P0051 balance residual diagnostics.

`persist_transfer_flow(...)` writes `transfer_capacity_flow_raw_v1`, `transfer_capacity_flow_hourly_v1` and `transfer_capacity_flow_se1_se4_hourly_v1` idempotently.

`validate_transfer_flow(...)` checks duplicates, finite values, capacity absence, expected hours, missingness and joins to P0051 physical balance rows.

`run_initial_diagnostics(...)` joins transfer/import-export rows to SE3 price and SE3-SE1 diagnostics. Capacity/utilization diagnostics remain null in P0052 because no auth-free capacity source was available.

`write_p0052_evidence(...)` writes package-run Markdown and JSON evidence under `requirements/package-runs/P0052/`.

P0052 is diagnostics/data-ingestion only. It explicitly forbids continental price pressure work, SE1-to-SE3 anchoring, SE3 API work, production model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.
