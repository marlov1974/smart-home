# P0054D Implementation Design

Package: P0054D
Label: LABB

## Interpretation

P0054D fixes P0054C's broad SE4 weather proxy by adding a load-weighted SE4 weather proxy and rerunning the SE4 no-price consumption experiment.

Core question:

```text
Was P0054C's HGB win mainly a model-family result, or partly caused by too-broad weather proxy?
```

## Weather Proxy Structure

Use existing weather-history tables:

- `weather_locations`
- `weather_observations`
- `weather_area_hourly`

Add a new active proxy group:

```text
se4_load_weather
```

Locations:

```text
se4_load_malmo        55.6050  13.0038  0.6010230179028133
se4_load_helsingborg  56.0465  12.6945  0.23785166240409208
se4_load_kristianstad 56.0294  14.1567  0.16112531969309463
```

The weights come from 235000 / 391000, 93000 / 391000 and 63000 / 391000.

Add a stable SQLite view:

```text
weather_proxy_se4_load_hourly
```

## Modeling Structure

Create a new package module:

`src/mac/services/spotprice_model_diagnostics/p0054d.py`

It will reuse P0054C's LABB experiment shape but read `se4_load_weather` instead of `south_connected_weather`.

Models:

- HGB benchmark
- deterministic sklearn MLP
- dependency-safe `ExtraTreesRegressor`

All winner claims use identical validation and holdout row sets.

## Evidence

Evidence is written under:

`requirements/package-runs/P0054D/`

The run writes the required markdown files plus compact JSON/CSV. It also reads P0054C evidence for old-vs-new weather summary comparison.

## Test Strategy

Tests cover:

- SE4 weather proxy weights sum to 1.0.
- `se4_load_weather` is part of initialized weather proxy configuration.
- P0054D feature contract excludes forbidden price/grid/production inputs.
- direct row comparison validation detects identical model row sets.
- weekly 168h path selection requires complete paths.

Verification commands:

```text
python3 -m unittest tests.mac.services.weather_history.test_proxy_groups tests.mac.services.spotprice_model_diagnostics.test_p0054d
PYTHONPYCACHEPREFIX=/private/tmp/p0054d-pycache python3 -m py_compile src/mac/services/weather_history/storage.py src/mac/services/spotprice_model_diagnostics/p0054d.py tests/mac/services/spotprice_model_diagnostics/test_p0054d.py tests/mac/services/weather_history/test_proxy_groups.py
python3 -m src.mac.services.weather_history backfill --start-date 2022-05-30 --end-date 2026-05-29
python3 -m src.mac.services.weather_history validate-proxy-groups --start-date 2022-05-30 --end-date 2026-05-29
PYTHONPYCACHEPREFIX=/private/tmp/p0054d-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054d
git diff --check
```

## Risks

- Weather backfill requires Open-Meteo network access through the existing weather-history service.
- Realized/archive weather remains LABB proxy only.
- ExtraTrees may outperform or underperform HGB; it is diagnostic and not a deployable artifact.
- No model binary or raw weather DB is committed.
