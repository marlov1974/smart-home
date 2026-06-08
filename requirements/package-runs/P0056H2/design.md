# P0056H2 Implementation Design

## Interpretation

P0056H2 tests one narrow question: if the P0056H 36h rolling-origin schedule is kept but lag and rolling load features are built in P0056C's static style, does performance return toward the old static full36 baselines?

Static-style means lag/rolling features are computed from the forecast origin's historical context and reused for every horizon in the 36h forecast window.

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0056h2.py`.

Reuse package-local helpers from P0056H where appropriate:

- origin schedule
- input contract loading
- schema/metric helpers where compatible
- HGB no-price fit/predict/scoring helpers
- comparison constants

Use package-specific forecast and metrics tables:

```text
area_consumption_36h_static_style_forecast_log_p0056h2_v1
area_consumption_36h_static_style_metrics_p0056h2_v1
```

## Intended Changes

- Add P0056H2 package file and package-run evidence.
- Add P0056H2 diagnostic module.
- Add focused tests for static-style lag anchoring and schedule matching.
- Regenerate P0056H2 DB evidence locally.

## Deliberate Non-Changes

- Do not modify P0056H results.
- Do not rerun P0056C/P0056E/P0056F/P0056G.
- Do not add production forecast weather.
- Do not add APIs, devices, runtime services or deployment artifacts.

## Test Strategy

Unit tests:

```text
python3 -m unittest tests.mac.test_p0056h2_static_style_lags
python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0056h2.py tests/mac/test_p0056h2_static_style_lags.py
```

Package run:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0056h2-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056h2
```

Verification:

```text
sqlite3 ... count forecast/metrics rows for P0056H2
git diff --check
```

## Risks And Uncertainties

- The old static baselines used broader weighted-ensemble logic. P0056H2 uses HGB no-price to isolate feature-shape effects against P0056H. If performance remains worse than static baselines, a later package may need an exact P0056C-style weighted-ensemble rerun.
- Existing target coverage has known incomplete 36h windows; strict incomplete windows will be skipped and documented.
