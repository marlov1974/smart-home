# Spotprice Model Diagnostics

Last changed: P0054E

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

## P0052A ENTSO-E Token Capacity And Exchange Amendment

`p0052a.run_p0052a_ingestion(...)` orchestrates token-safe ENTSO-E Transparency API discovery, internal Swedish border ingestion, P0052 table extension, wide-feature amendment, validation and evidence writing.

Important functions:

`load_entsoe_token(...)` reads a token from `ENTSOE_SECURITY_TOKEN` or the local user secret file without printing or writing the token value.

`verify_secret_safety(...)` records sanitized secret handling evidence, including outside-repository storage and owner-only permissions.

`build_entsoe_params(...)` builds evidence-safe A09/A11/A61 ENTSO-E request parameters while keeping `securityToken` out of sanitized records.

`fetch_entsoe_rows(...)` queries internal Swedish borders in both directions for scheduled exchange, physical flow and explicit A61 capacity contracts, then filters expanded rows to the requested UTC range.

`parse_entsoe_document(...)`, `parse_entsoe_period_points(...)` and `resolution_to_timedelta(...)` parse ENTSO-E XML, including PT15M/PT30M/PT60M/P1D and period-bound `P1M` capacity periods.

`persist_entsoe_rows(...)` inserts ENTSO-E source rows into the P0052 raw and hourly long tables without replacing SvK/Statnett source identity.

`update_wide_entsoe_features(...)` adds scheduled exchange, physical flow and flow-or-exchange wide fields, and fills compatible directional capacity fields where A61 A02 capacity is available.

`run_p0052a_diagnostics(...)` joins amended transfer/capacity features to the local SE3-SE1 diagnostic table when overlapping price rows exist.

`write_p0052a_evidence(...)` writes sanitized package-run Markdown and JSON evidence under `requirements/package-runs/P0052A/`.

P0052A is diagnostics/data-ingestion only. It explicitly forbids external price-level ingestion, continental price-pressure modeling, SE1-to-SE3 anchoring, production forecast APIs, deployable model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0052B ENTSO-E Capacity Concept Review And Backfill

`p0052b.run_p0052b_ingestion(...)` orchestrates token safety recheck, P0052 metadata schema migration, ENTSO-E representative historical backfill, timestamp-normalized join diagnostics, conservative A61 concept review and sanitized evidence writing.

Important functions:

`capacity_concept_review(...)` documents A61 plus A02/A03/A04 as weekly/monthly/yearly capacity contract types and returns `capacity_concept_uncertain` so utilization/margin remain blocked.

`ensure_p0052b_schema(...)` additively migrates P0052 raw/hourly tables with ENTSO-E metadata columns and extends the wide table with P0052B diagnostic columns.

`fetch_entsoe_rows_for_windows(...)` performs bounded, parallel, token-backed ENTSO-E fetches over representative windows without putting the token into request evidence.

`parse_entsoe_document_clipped(...)`, `parse_entsoe_period_points_clipped(...)` and `expand_entsoe_value_clipped(...)` parse ENTSO-E XML while clipping long capacity periods to the requested chunk before hourly expansion.

`update_wide_entsoe_features_p0052b(...)` inserts missing wide timestamp rows and updates scheduled exchange, physical flow and directional capacity fields.

`normalize_timestamp_sql(...)` normalizes `Z` and `+00:00` UTC timestamp text for diagnostics joins without rewriting source tables.

`run_join_fix_analysis(...)` explains the P0052A zero-row join and reports exact versus normalized join counts.

`run_p0052b_diagnostics(...)` computes SE3 price / SE3-SE1 correlations for scheduled exchange and physical flow, while leaving capacity utilization/margin blocked when concept status is uncertain.

`write_p0052b_evidence(...)` writes P0052B Markdown and JSON evidence under `requirements/package-runs/P0052B/`.

P0052B is diagnostics/data-ingestion only. It explicitly forbids external price-level ingestion, continental price-pressure modeling, SE1-to-SE3 anchoring, production forecast APIs, deployable model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0052C A61 Capacity Sanity Check

`p0052c.run_p0052c_analysis(...)` orchestrates token safety recheck, local P0052B row loading, A61 capacity versus A09/A11 ratio analysis, contract classification and evidence writing.

Important functions:

`load_entsoe_hourly_rows(...)` reads local ENTSO-E A09/A11/A61 hourly rows for the required representative windows.

`build_ratio_observations(...)` joins capacity to scheduled exchange and physical flow by normalized UTC timestamp, directed border and A61 contract type.

`safe_ratio(...)` computes `abs(flow_or_exchange) / capacity` and returns explicit null reasons for missing or invalid capacity.

`ratio_metrics(...)` computes overlap counts, missing counts, percentiles and violation counts above 1.00/1.02/1.05/1.10.

`classify_contract_types(...)` classifies A02/A03/A04 as candidate or blocked capacity proxies.

`worst_ratio_examples(...)` emits sanitized worst-ratio examples without request or token fields.

`write_p0052c_evidence(...)` writes Markdown, JSON and CSV evidence under `requirements/package-runs/P0052C/`.

P0052C concluded that A61 A02/A03/A04 remain blocked for utilization and bottleneck margin because A09 scheduled exchange and A11 physical flow materially exceed all three variants in post-flow-based data.

## P0053A ENTSO-E A09/A11 Internal Swedish Flow/Exchange Backfill

`p0053a.run_p0053a_backfill(...)` orchestrates token-safe ENTSO-E A09/A11 historical backfill for internal Swedish borders, wide-table net/pressure feature derivation, normalized joins to price and physical balance data, validation and evidence writing.

Important functions:

`a09_a11_configs(...)` filters the shared P0052A ENTSO-E document configuration down to A09 scheduled exchange and A11 physical flow only.

`monthly_chunks(...)` creates restart-safe UTC monthly request windows clipped to the requested target range.

`plan_missing_fetch_tasks(...)` inspects existing canonical transfer rows and skips already-complete border/direction/month tasks.

`fetch_missing_entsoe_rows(...)` and `fetch_task(...)` perform parallel token-backed ENTSO-E requests while storing only sanitized request metadata in evidence.

`ensure_p0053a_schema(...)` additively ensures P0052B metadata columns, A09/A11 directional columns and P0053A net/pressure wide columns exist.

`derive_flow_exchange_features(...)` computes net scheduled exchange, net physical flow, SE3/SE4 import aliases and southward pressure features without capacity.

`update_wide_flow_exchange_features(...)` inserts missing wide timestamp rows and updates A09/A11 directional plus derived fields.

`create_joined_analysis_dataset(...)` creates `physical_balance_flow_exchange_analysis_v1` by normalized UTC timestamp matching between the transfer wide table, `se3_se1_demand_response_analysis_v1` and `physical_balance_se1_se4_hourly_v1`.

`directional_coverage_summary(...)` reports raw border/direction/measure missingness; `net_feature_coverage_summary(...)` reports effective net-feature completeness for modeling diagnostics.

`run_p0053a_diagnostics(...)` computes exploratory SE3 price and SE3-SE1 spread correlations plus pre/post Nordic flow-based transition summaries.

P0053A is diagnostics/data-ingestion only. It explicitly excludes A61 requests, utilization, bottleneck-margin derivation, continental price-pressure modeling, SE1-to-SE3 anchoring, production forecast APIs, deployable model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0053B SE1 Consumption Forecast Warmup

`p0053b.run_p0053b_analysis(...)` orchestrates the SE1 consumption forecast warmup: target loading, forecast-safe feature construction, direct-horizon dataset persistence, baseline/model evaluation, 168h path diagnostics and evidence writing.

Important functions:

`load_consumption_source_rows(...)` reads `physical_balance_se1_se4_hourly_v1` and normalizes the hourly `consumption_se1` target.

`validate_target_contract(...)` verifies unique normalized UTC timestamps, finite positive target values, fixed-CET fields, source range and unit semantics.

`load_weather_rows(...)` reads `weather_proxy_se1_core_hourly` when available and labels realized weather as historical-only, while later train-only weather normals may be forecast-safe.

`build_direct_horizon_rows(...)` creates origin/target examples for the required horizons using target-calendar features, origin-safe load lags, origin-safe rollups and optional weather context.

`lag_features_at_origin(...)` and `rolling_features_at_origin(...)` enforce the leakage boundary: lag and rolling features end before the forecast origin.

`forecast_period_policy.canonical_split_for_timestamp(...)` assigns the canonical P0053C train, validation and holdout split from `timestamp_utc`.

`forecast_period_policy.is_modeling_target_timestamp(...)` enforces the canonical modeling start and allows pre-start rows only as context-only lag warmup.

`assign_chronological_splits(...)` uses target `timestamp_utc` through the shared forecast period policy; fixed-CET fields are calendar/features only.

`fit_train_profiles(...)`, `apply_profile_features(...)` and `apply_baseline_predictions(...)` fit train-only calendar/weather profiles and required baselines.

`feature_group_contract(...)` classifies G0-G5 as forecast-safe and G6 actual-weather features as historical-only diagnostic.

`evaluate_baselines(...)` and `evaluate_models(...)` report direct-horizon metrics for required baselines and lightweight Ridge/HGB models. Metrics include absolute errors, bias, sMAPE and P0053C relative error fields. No model binary is persisted.

`evaluate_168h_paths(...)` evaluates daily-origin exact 168-hour path baselines and reports path MAE, bias, peak-hour error and daily-energy error proxy.

`write_p0053b_evidence(...)` writes Markdown, JSON and CSV evidence under `requirements/package-runs/P0053B/`.

P0053B is diagnostics/model-warmup only. It explicitly forbids SE1 price modeling, SE3 price modeling, SE3-SE1 modeling, production forecasting, export/import forecasting, future actual A09/A11 leakage, A61 utilization, production APIs, deployable model artifacts, M5/M6/M7 work, Shelly, device, KVS and Home Assistant paths.

## P0053C-A M4/P0045 Price-Shape Rebuild

`p0053ca.run_p0053ca_rebuild(...)` orchestrates the P0053C-A M4/P0045 price-shape rebuild under the global forecast period policy.

Important functions:

`filter_ai2_policy_rows(...)` removes scored AI-2 target rows before `2022-06-01T00:00:00Z`.

`assign_policy_splits(...)` applies canonical P0053C train, validation and holdout splits from `timestamp_utc`.

`assign_ai1_policy_splits(...)` classifies AI-1 daily rows by the UTC start represented by the fixed-CET model date.

`build_policy_forecast_windows(...)` builds exact 168h windows and keeps only windows whose hourly targets all belong to one canonical split.

`build_forecast_origin_log_rows(...)` emits holdout selected-formula shape/index predictions with `forecast_origin_timestamp_utc`, `input_data_cutoff_utc`, `target_timestamp_utc`, `horizon_hours`, `area_or_target`, `predicted_price_or_index`, `prediction_unit` and `prediction_kind`.

`persist_forecast_origin_log(...)` writes the local SQLite table `m4_price_shape_forecast_origin_log_p0053ca_v1`.

P0053C-A output is `prediction_kind=shape_index` and `prediction_unit=centered_shape_index`; it is not absolute price. It may support future rank/top-bottom relative price-shape features, but absolute price-response features require a later safe anchoring package.

P0053C-A is diagnostics/rebuild-only. It does not create a production API, deployable model artifact, A61 utilization, future actual price feature, Shelly, Home Assistant, KVS or device path.

## P0054E SE4 LightGBM/XGBoost LABB Comparison

`p0054e.run_p0054e_analysis(...)` orchestrates the Mac-local LABB comparison of ExtraTrees, LightGBM and XGBoost on the corrected P0054D SE4 consumption setup.

Important functions:

`capture_environment_status(...)` records Python, pip, platform, package version and optional LightGBM/XGBoost import status.

`optional_model_specs(...)` builds the same-run model list, always including ExtraTrees and adding LightGBM/XGBoost only when importable.

`fit_p0054e_model(...)` trains one bounded first-pass model on train rows and evaluates validation/holdout rows without persisting model artifacts.

`attach_named_predictions(...)` and `attach_weekly_predictions(...)` add dynamic model prediction columns for direct and weekly 168h path evaluation.

`compare_p0054e_models(...)` identifies the best direct/weekly model and compares boosted models to same-run and P0054D ExtraTrees baselines.

`write_p0054e_evidence(...)` writes LABB-only Markdown, JSON and CSV evidence under `requirements/package-runs/P0054E/`.

P0054E is diagnostics-only. It explicitly forbids runtime, device, Shelly, Home Assistant, KVS, deploy, production model, price, production, flow/export/import, A61 and future-leakage inputs.
