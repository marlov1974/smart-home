# P0053B implementation design

Package interpretation:

P0053B is a forecast-safety warmup package for `consumption_se1` only. It builds a local modeling dataset, evaluates baselines and lightweight models across required horizons, evaluates daily-origin 168h paths, writes evidence and recommends the next physical target. It does not produce deployable model artifacts.

Implementation structure:

- Add `src/mac/services/spotprice_model_diagnostics/p0053b.py`.
- Add `tests/mac/services/spotprice_model_diagnostics/test_p0053b.py`.
- Write evidence under `requirements/package-runs/P0053B/`.
- Update `docs/functions/mac/spotprice-model-diagnostics.md` and `docs/functions/00-index.md`.
- Optionally update `memory/knowhow/spotprice.md` if package results create durable modeling lessons.

Local data products:

- Create or replace SQLite table `se1_consumption_forecast_warmup_v1` in the local feature DB.
- Store direct-horizon rows for the required horizons only.
- Do not commit large generated datasets or model binaries.

Feature design:

- Direct rows are indexed by `origin_timestamp_utc`, `target_timestamp_utc` and `horizon_h`.
- Calendar/special-day features are computed for the target timestamp and are forecast-safe.
- Lag and rolling load features end at or before the forecast origin and are forecast-safe.
- Weather normal features are train-only profiles for the target timestamp and are forecast-safe.
- Actual realized weather target features are included only in `G6_diagnostic_historical_only_non_deployable`.
- No future price, future production, future flow/exchange or A61 feature is created.

Model design:

- Baselines: previous day, previous week, train-only calendar hour/weekday profile, train-only seasonal hour/weekday profile and recent-load adjusted profile.
- Lightweight models: Ridge regressors for G0-G5 and one bounded HistGradientBoostingRegressor for G4.
- Diagnostic-only model: Ridge for G6 with actual weather features, labeled non-deployable.
- 168h path mode: evaluate daily forecast origins with exact 168 hourly predictions using previous-week and adjusted-profile baselines. This gives path metrics without training 168 separate deployable models.

Test strategy:

- Unit tests cover target contract, chronological split ordering, lag/rolling leakage guards, train-only profile behavior, feature-group safety classification, forbidden feature exclusions, exact 168h path generation and deterministic metrics.
- Verification runs P0053B tests plus relevant P0051/P0053A tests and `git diff --check`.

Risks and uncertainties:

- Weather forecast-safe improvement may be limited because only normals are allowed as deployable weather features.
- Holdout period is short (`2026-01-01` through `2026-05-25`), so seasonal holdout metrics do not cover a full year.
- Daily-origin path metrics are intentionally bounded for runtime and evidence clarity; they still produce exact 168-hour paths per origin.
