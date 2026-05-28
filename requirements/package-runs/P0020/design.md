# Package P0020 Implementation Design

## Package

`P0020`

## Package interpretation

Add a thin standard-library HTTP wrapper around the P0018 weekly home optimizer POC so the operator can run the planner from a local browser or phone on the same LAN.

## Chosen HTTP command and default host/port

Final server command:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081
```

Manual phone/LAN command:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Default host is `127.0.0.1` for safety. Default port is `8081` to avoid P0017's `8080`.

Non-blocking smoke command:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --once-smoke
```

## P0018 planner function reused by server

The server calls:

```text
build_weekly_plan(week, ppm, house_temp)
rows_for_plan(plan)
```

No optimizer logic is duplicated. P0020 does not change P0018 semantics.

## HTML structure

Add `html.py` with:

- page shell and CSS
- form rendering
- result page rendering
- compact summary rendering
- scrollable 168-hour table rendering
- HTML escaping

The page is simple operational UI, not a landing page. It contains input controls, summary metrics and the hourly plan table.

## JSON API structure

`GET /api/weekly-home-poc?week=2&ppm=500&houseTemp=22` returns:

```json
{
  "input": {"week": 2, "ppm": 500.0, "houseTemp": 22.0},
  "summary": {...},
  "hours": [...]
}
```

`hours` contains the P0018 row dictionaries and must have length 168 for valid input.

`GET /health` returns compact JSON:

```json
{"status":"ok","service":"weekly_home_optimizer_poc"}
```

## Error handling

Invalid inputs are parsed centrally:

- missing or invalid `week`
- missing or invalid `ppm`
- missing or invalid `houseTemp`
- unmodelable week from the P0017/P0018 stack

HTML requests return HTTP 400 with a human-readable error page and the input form. API requests return HTTP 400 JSON.

## Test strategy

Add tests for:

- `/health`
- root form
- valid HTML result from query params
- valid JSON result with 168 hours
- invalid HTML/API errors
- smoke command

Run:

```bash
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --once-smoke
git diff --check
```

## Files/modules intended to change

- `src/mac/labs/weekly_home_optimizer_poc/server.py`
- `src/mac/labs/weekly_home_optimizer_poc/html.py`
- `src/mac/labs/weekly_home_optimizer_poc/README.md`
- `tests/mac/weekly_home_optimizer_poc/test_browser_server.py`
- `tests/mac/weekly_home_optimizer_poc/test_browser_contract.py`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0020/**`

## Files/modules intentionally not changed

- P0018 planner, heat, PPM and table semantics.
- P0017 spot forecast service and compact API.
- `dep/**` deploy artifacts.
- Shelly, Home Assistant and G1 runtime code.

## Manual phone test instructions

1. Start:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

2. Open:

```text
http://<mac-lan-ip>:8081/
```

3. Submit week, ppm and houseTemp.

## Risks and uncertainties

- The UI is trusted-local only and has no authentication.
- LAN testing is not performed automatically because tests must not bind to a real LAN interface.
- The page is static HTML without JavaScript charts in this package.

## Design deviations during implementation

None yet.
