# P0053B-A2 Implementation Design

Package interpretation:

P0053B-A2 should test whether P0053C-B anchored absolute SE1 price forecasts improve SE1 consumption forecasts when combined with calendar, recent load state and realized-weather-as-forecast proxy. The result is an offline backtest only because weather actuals are used as forecast proxy and because the price forecast log lacks canonical train coverage.

Implementation structure:

- Add `src/mac/services/spotprice_model_diagnostics/p0053ba2.py`.
- Reuse P0053B helpers for consumption source rows, weather rows, calendar features, lag/rolling load state, metrics and model encoding where practical.
- Read P0053C-B anchored price log from local SQLite.
- Build a joined modeling dataset from price forecast rows:
  - one row per forecast-origin target hour
  - target consumption from `physical_balance_se1_se4_hourly_v1`
  - recent load features at `forecast_origin_timestamp_utc`
  - weather actual proxy at `target_timestamp_utc`
  - G7 price features computed within each 168h forecast-origin path
- Select weekly holdout origins as every seventh complete holdout origin starting from the first holdout origin.
- Fit required Ridge/HGB base and plus_G7 comparisons using validation-origin joined rows only; holdout is report-only.
- Write required evidence files under `requirements/package-runs/P0053B-A2/`.

Feature groups:

- `G0_calendar_only`
- `G1_calendar_plus_recent_load_lags`
- `G4_calendar_load_lags_weather_proxy`
- `G7_price_only_diagnostic`
- `G4_plus_G7_calendar_load_weather_price`

Models:

- `M4_base_Ridge_G4`
- `M4_plus_G7_Ridge_G4_price`
- `M7_base_HGB_G4`
- `M7_plus_G7_HGB_G4_price`

Deliberate decisions:

- Do not mutate P0053B or P0053C-B.
- Do not create new price forecast rows for the train period.
- Do not persist a large modeling dataset to SQLite; write only compact sample/evidence.
- Treat horizon labels as `horizon_hours + 1`, giving required direct horizons `1..168` while preserving P0053C-B origin semantics.

Test strategy:

- Run P0053B-A2 end-to-end.
- Verify anchored log existence and timestamp inequalities.
- Verify all G7 features are computed within forecast origin groups.
- Verify base and plus_G7 use identical row IDs for validation/development and holdout scoring.
- Verify weather proxy label exists.
- Verify weekly holdout paths are complete or documented.
- Run focused unit tests or repository unittest discovery as feasible.
- Run `git diff --check`.

Risks and uncertainties:

- Because plus_G7 has no canonical train-period price forecast rows, the model fit is development-on-validation and not deployable.
- Realized weather proxy can make weather-related performance optimistic.
- Price response may be weak in aggregate and only visible in conditional high/low price-hour subsets.
