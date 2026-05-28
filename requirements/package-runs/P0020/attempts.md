# Package P0020 Attempts

## Attempt 1

Result: passed after adapting tests to avoid local TCP bind in sandbox.

## Implementation summary

- Added standard-library browser server in `server.py`.
- Added local HTML rendering in `html.py`.
- Added `/`, `/api/weekly-home-poc` and `/health` endpoints.
- Added `--once-smoke` non-blocking verification command.
- Updated P0018 lab README with local and phone/LAN commands.
- Added browser/API tests.
- Added durable browser UI memory and function catalog updates.

## Debug adjustment

Initial test implementation used a real `ThreadingHTTPServer(("127.0.0.1", 0), ...)` test server. The sandbox rejected the local bind with:

```text
PermissionError: [Errno 1] Operation not permitted
```

Fix:

- Reworked endpoint tests to execute `BaseHTTPRequestHandler` through a fake socket.
- This keeps automated tests network-free and still exercises routing, status codes, headers and response bodies.

## Verification

### `python3 -m unittest discover tests/mac/weekly_home_optimizer_poc`

```text
Ran 21 tests in 0.682s

OK
```

### `python3 -m unittest discover tests/mac`

```text
Ran 95 tests in 1.173s

OK
```

### `python3 -m src.mac.labs.weekly_home_optimizer_poc.server --once-smoke`

```text
weekly_home_optimizer_poc server smoke ok
```

### `git diff --check`

Passed with no output.

## API / HTML behavior sample

Direct payload/render check:

```text
api_keys ['hours', 'input', 'summary']
hours 168
summary {'hours': 168, 'min_ppm': 547.9, 'max_ppm': 651.5, 'avg_supply_pct': 28.5, 'total_heat_kWh': 2147.7, 'total_cost': 3822.6}
form_has_week True
result_has_table True
```

## Local server command

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081
```

## Phone/LAN command

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Phone URL:

```text
http://<mac-lan-ip>:8081/
```

## Live actions

None.

## Manual phone test

Not run automatically. Package allows phone/LAN manual testing, but automated verification intentionally avoids binding to a real LAN interface.

## Knowhow promotion

Skipped. The sandbox local-bind test adjustment is package evidence, not a durable G2 runtime/tool/API lesson. The durable browser contract is captured in `memory/planning/weekly-home-poc-browser-ui.md`.
