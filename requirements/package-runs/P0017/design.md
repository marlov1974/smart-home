# P0017 Implementation Design

## Package Interpretation

P0017 creates the first local Mac spot period index service for the winter heat-pump planner. The service predicts a compact 21-number weekly price shape for a requested ISO week using the committed 2025 winter period-index dataset and the week-distance weights specified in the package.

The response contract stays minimal: the default HTTP response is a JSON array only, with no metadata.

## Implementation Structure

New source package:

```text
src/mac/services/spot_forecast/
  __init__.py
  __main__.py
  model.py
  schema.py
  server.py
```

New tests:

```text
tests/mac/spot_forecast/
  __init__.py
  test_week_weight_model.py
  test_period_index_api.py
  test_contract_shape.py
```

Durable function documentation:

```text
docs/functions/mac/spot-forecast.md
```

Package evidence:

```text
requirements/package-runs/P0017/
```

## Data Loading

The model loads:

```text
data/spot/spotprices-2025-winter-8h-weekly-period-index.json
```

Only records with numeric `iso_year`, numeric `iso_week`, and a 21-number `price_index` list are accepted. Invalid source shape raises a service/model error rather than being silently normalized.

## Week-Weight Model

For a requested week:

```text
distance 0 => weight 1.00
distance 1 => weight 0.70
distance 2 => weight 0.40
else       => no contribution
```

The implementation averages every period independently across contributing historical records. With one source year, the model is a week-neighborhood smoother. The record structure keeps `iso_year` so future years can be added without changing the public API.

## Normalization and Rounding

Internal calculations retain float precision.

After weighted averaging, the 21-value vector is normalized so the arithmetic mean is exactly 1.0 before output rounding. Public API output rounds values to two decimals at the boundary only.

## HTTP API

`server.py` exposes:

```text
GET /spot/period-index?week=WW
```

Behavior:

- valid modeled week: HTTP 200 with compact JSON array
- missing, non-numeric or out-of-range `week`: HTTP 400 with `{"error":"invalid week"}`
- valid but unmodelable week: HTTP 404 with `{"error":"week not found"}`
- unknown path: HTTP 404 with `{"error":"not found"}`

The server is standard-library only, based on `http.server`.

## CLI

Commands:

```bash
python3 src/mac/services/spot_forecast/server.py --once --week 2
python3 -m src.mac.services.spot_forecast --once --week 2
python3 -m src.mac.services.spot_forecast --host 127.0.0.1 --port 8080
```

`--once --week WW` prints the compact JSON array and exits. This gives deterministic package verification without leaving a service running.

## Files Intentionally Not Changed

- No Shelly source or deploy artifacts.
- No Home Assistant files.
- No heat-pump planner implementation.
- No package file edits unless completion notes are explicitly requested later.
- No packaging/check files unless tests reveal an import/path need.

## Test Strategy

Run:

```bash
python3 -m unittest discover tests/mac/spot_forecast
python3 src/mac/services/spot_forecast/server.py --once --week 2
python3 src/mac/services/spot_forecast/server.py --once --week 25
git diff --check
```

The week 25 command is expected to exit non-zero and print a compact `week not found` error because the current winter-only dataset has no week-distance 0/1/2 contributors for week 25.

## Risks and Uncertainties

- The package does not define ISO week wrap-around behavior between week 52 and week 1. P0017 uses direct absolute week-number distance only, which is consistent with the stated `abs(target_week - historical_week)` style and keeps behavior deterministic.
- The first dataset has only one year, so forecasts are smoothed historical winter shapes rather than multi-year forecasts.
- Running the HTTP server persistently is local/manual only in this package; no launchd deployment is added.
