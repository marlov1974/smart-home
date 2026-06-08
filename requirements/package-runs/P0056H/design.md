# P0056H Implementation Design

## Package Interpretation

P0056H reruns the consumption forecast evaluation as rolling 36h forecasts every 5th day from 2025-06 onward. It tests whether explicit, forecast-safe lag handling recovers performance lost in P0056G's 168h weekly path forecast.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0056h.py`:

- generate 06:00 Europe/Stockholm forecast origins every 5th day
- build training rows from historical 36h origins before each current origin
- build forecast rows for horizons 0..35 hours
- classify lag availability per target/hour/lag
- run two forecast-safe modes:
  - `L1_origin_known_fallback`
  - `L2_recursive_lags`
- persist progress, checkpoint status, compact DB rows and evidence
- compare results against static baselines and P0056G weekly result

Add `tests/mac/test_p0056h_lag_protocol.py`:

- origin schedule rotation
- lag availability classification
- metric scope behavior

## Chosen Model

Use deterministic `HGB_no_price` via existing P0054K feature matrix helpers. This is intentionally narrower than the full weighted ensemble to keep the package focused on lag protocol and tractable for all origins.

## Weather Protocol

- SE1, SE2, FI: P0056D actual-weather proxy.
- SE3: P0056B actual-weather proxy.
- Label all outputs as `actual_weather_proxy_LABB`.

## Test And Verification Commands

```bash
PYTHONPYCACHEPREFIX=/private/tmp/p0056h-pycache python3 -m unittest tests.mac.test_p0056h_lag_protocol
PYTHONPYCACHEPREFIX=/private/tmp/p0056h-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056h
sqlite3 /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 "SELECT 'forecast', COUNT(*) FROM area_consumption_36h_forecast_log_p0056h_v1 WHERE generated_by_package='P0056H' UNION ALL SELECT 'metrics', COUNT(*) FROM area_consumption_36h_metrics_p0056h_v1 WHERE generated_by_package='P0056H';"
git diff --check
```

## Risks And Uncertainty

- The HGB implementation tests the lag protocol but is not an exact full weighted-ensemble reproduction.
- Actual-weather proxy is LABB-only and not production weather.
- The rolling-origin sample is every 5th day, not every day, by package design.
