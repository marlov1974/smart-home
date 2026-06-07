# Package P0056B Review Evidence

## Package

`P0056B`

## Consistency result

WARN

## Files checked

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order` files
- `requirements/packages/P0056B-labb-northern-europe-area-weather-proxies.md`
- `requirements/package-runs/P0054Z/CHANGELOG.md`
- `requirements/package-runs/P0054Z/climate-zone-validation.md`
- `requirements/package-runs/P0054Z/station-proxy-selection.md`
- `requirements/package-runs/P0056A/CHANGELOG.md`
- `requirements/package-runs/P0056A/area-code-mapping.md`
- `requirements/package-runs/P0056A/coverage-and-missingness.md`
- `src/mac/services/weather_history/storage.py`
- `src/mac/services/spotprice_model_diagnostics/p0054z.py`
- `src/mac/services/spotprice_model_diagnostics/p0055a.py`

## Checks

### Package vs memory

The package matches the LABB policy: it prepares energy-market AI lab data, does not promote to G2-KANDIDAT, and does not alter runtime behavior.

### Package vs linked requirements

The requested 18 P0056A primary areas exist in P0056A outputs. P0056B asks for weather features for those areas only.

### Package vs previous packages

P0054Z already created SE3 climate-zone and SE3 broad weather actual-proxy features from local `weather_history.sqlite3`. P0055A confirms the current SE3 model consumes `temperature_2m`, `heating_degree_proxy`, and `temperature_2m_roll_mean_24h` plus optional weather fields.

P0056A created multi-area consumption measurements in `area_consumption_hourly_v1`. P0056B can align weather proxy rows to that area scope without training models.

### Package vs implementation/deploy structure

Existing local weather storage contains `weather_observations`, `weather_locations`, and `weather_area_hourly`. This is sufficient to build canonical area weather proxy rows without adding a new external integration.

### Package vs G1/G2 boundary

No Shelly, Home Assistant, device, or production runtime changes are needed or allowed.

### Package vs invariants

The package can be implemented as forecast-safe LABB data preparation. Actual weather proxies must be labelled as actual-weather proxies and not production forecast weather.

### Package vs testability and rollback

The code can be tested with deterministic station/proxy mapping and aggregation unit tests. Database writes are limited to a P0056B-owned table and generated package rows can be replaced deterministically.

### Chat-only assumptions

No operator-provided additional weather source is available for this run.

## Decision

Continue with warnings.

## Warning basis

- Local weather infrastructure has no direct configured weather stations for every P0056A country or bidding zone, especially DE_LU, PL, NL, and the Baltics.
- Some areas therefore need documented fallback composites from existing local stations/proxies.
- Local weather actual-proxy coverage currently ends before the latest P0056A consumption measurements. The gap must be documented rather than hidden.
- `snow_depth` is not available in the current local weather source; existing source has snowfall, so the required nullable `snow_depth` column will be written as null and documented.

## Notes for human/ChatGPT review

The package should not be treated as production weather forecast readiness. It creates a deterministic LABB feature surface so future multi-area consumption forecasts can be tested with `calendar + historical load + weather` and without spot price features.
