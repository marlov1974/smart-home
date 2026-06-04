# P0054J Function Design

## New Functions

| function | purpose |
|---|---|
| `run_p0054j_analysis` | orchestrates dataset build, model fitting, evaluation and evidence |
| `load_se1_consumption_rows` | reads SE1 consumption target rows |
| `load_weather_proxy_rows` | reads `se1_core_weather` proxy rows |
| `load_price_forecast_rows` | reads filtered P0054H forecast rows |
| `build_direct_horizon_rows` | builds paired direct-horizon modeling rows |
| `build_weekly_path_rows` | builds holdout 168h weekly path rows |
| `attach_calendar_features` | adds known-ahead calendar features |
| `lag_features_at_origin` | adds strictly pre-origin load lags |
| `rolling_features_at_origin` | adds strictly pre-origin load rollups |
| `attach_price_path_features` | derives path-only P0054H price features |
| `assign_p0054i_splits` | applies train_fit/holdout policy |
| `feature_group_contract` | defines no-price and with-price features |
| `validate_feature_contract` | checks forbidden feature names and labels allowed price forecast fields |
| `fit_model_pair` | fits one model family for no-price and with-price features |
| `evaluate_direct_horizons` | reports direct horizon metrics |
| `evaluate_weekly_paths` | reports 168h path metrics |
| `evaluate_conditional_regimes` | reports conditional holdout metrics |
| `compare_price_ablation` | summarizes per-family with-price minus no-price deltas |
| `write_p0054j_evidence` | writes package-run evidence |

## Changed Functions

None.

## Removed Functions

None.

## Durable Function Catalog

`docs/functions/mac/spotprice-model-diagnostics.md` will be updated after implementation.
