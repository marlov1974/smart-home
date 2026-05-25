# P0017 Consistency Review

## Result

PASS

## Evidence

- `memory/device-management/mac-layer.md` explicitly lists spot price forecast services as Mac services and requires Python standard-library Mac tooling as the initial default.
- `memory/planning/spot-period-index-api.md` defines `GET /spot/period-index?week=WW`, compact JSON-array output, 21 values, two-decimal rounding and HTTP 400/404 error behavior matching P0017.
- `memory/planning/winter-heat-pump-flex-planner.md` consumes period price indexes as planner input and does not require planner logic changes in this package.
- `data/spot/spotprices-2025-winter-8h-weekly-period-index.json` exists after sync and contains 2025 winter records with `iso_week`, `price_index`, and exactly 21 period values per record.
- Existing source layout has `src/mac/tools/**` but no `src/mac/services/spot_forecast/**`, so adding the service is package-scoped.
- Existing tests use Python standard library `unittest`; P0017 can follow that pattern without new dependencies.

## Assumptions

- ISO week validation accepts numeric weeks 1 through 53.
- A target week is modelable when at least one historical record has absolute week distance 0, 1 or 2 from the requested week. With the current 2025 winter data, mid-year weeks such as 25 should return 404.
- The model uses the `price_index` arrays from committed source data directly; it does not recompute operational-night attribution because that attribution is already represented in the source JSON.

## Boundary Check

- No G1 repository or G1 runtime changes are needed.
- No Shelly runtime, deploy artifact, Home Assistant or heat-pump planner changes are needed.
- No external Python packages are needed.
- No live testing or live writes are allowed or required.
