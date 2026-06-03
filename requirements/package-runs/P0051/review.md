# P0051 consistency review

Status: PASS

## Repository/source facts checked

- Repository synchronized and fast-forwarded to `origin/main`.
- P0050 PASS evidence exists under `requirements/package-runs/P0050/`.
- Continental pressure backlog exists and is explicitly parked.
- eSett Open Data API is public and exposes OpenAPI at `https://api.opendata.esett.com/openapi.json`.
- eSett endpoints found:
  - `EXP15/Consumption`
  - `EXP16/Volumes`
  - `EXP15/MBAOptions`
  - `EXP16/MBAOptions`
- eSett MBA options include Swedish bidding zones:
  - SE1 `10Y1001A1001A44P`
  - SE2 `10Y1001A1001A45N`
  - SE3 `10Y1001A1001A46L`
  - SE4 `10Y1001A1001A47J`
- Sample eSett responses return quarter-hour `timestampUTC` values, not hourly rows. P0051 can safely aggregate four quarter-hour values to one hourly mean MW value.
- Sample eSett consumption values are negative; P0051 will store canonical consumption as positive MW demand and document source sign normalization.

## Interpretation

P0051 can proceed with eSett as the selected source. Svenska kraftnät remains documented as investigated but not selected because eSett directly exposes machine-readable SE1-SE4 consumption and production through stable OpenAPI endpoints.

## Scope and safety

P0051 is Mac/local database ingestion and diagnostics only. No Shelly, Home Assistant, KVS, device, production API, deployable model, M5/M6/M7, SE1-to-SE3 anchoring, futures or continental pressure work is required or allowed.

## Result

PASS. Continue with package-scoped design, function design and implementation.
