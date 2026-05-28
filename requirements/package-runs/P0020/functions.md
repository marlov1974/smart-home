# Package P0020 Function Design

## Package

`P0020`

## Scope

Browser/server wrapper for:

```text
src.mac.labs.weekly_home_optimizer_poc
```

## New functions

### `parse_plan_query(query)`

Purpose: parse HTTP query parameters for week, ppm and houseTemp.

Inputs: mapping from query keys to values.

Outputs: `PlanRequest`.

Side effects: none.

Reason: centralize browser/API input validation.

Tests: invalid and valid endpoint tests.

### `plan_payload(request)`

Purpose: build JSON-serializable input, summary and hourly rows from the P0018 planner.

Inputs: `PlanRequest`.

Outputs: dictionary with `input`, `summary`, `hours`.

Side effects: local CPU calculation and committed data reads through P0018/P0017.

Reason: shared API and HTML result source.

Tests: JSON endpoint and HTML result tests.

### `render_page(title, body, status_message=None)`

Purpose: render complete HTML document with local CSS.

Inputs: title, body HTML, optional status message.

Outputs: HTML string.

Side effects: none.

Reason: avoid duplicated page shell.

Tests: root form and HTML result tests.

### `render_form(values=None, error=None)`

Purpose: render the browser input form.

Inputs: optional current values and error text.

Outputs: HTML string.

Side effects: none.

Reason: root page and error page.

Tests: root form and invalid input tests.

### `render_result(payload)`

Purpose: render summary and 168-hour table from a valid payload.

Inputs: payload from `plan_payload()`.

Outputs: HTML string.

Side effects: none.

Reason: browser inspection output.

Tests: HTML plan result tests.

### `build_handler()`

Purpose: create an HTTP request handler class for the POC server.

Inputs: none.

Outputs: `BaseHTTPRequestHandler` subclass.

Side effects: none until used by an HTTP server.

Reason: testable server construction.

Tests: HTTP endpoint tests.

### `run_server(host, port)`

Purpose: serve the POC HTTP server.

Inputs: host and port.

Outputs: none until interrupted.

Side effects: binds local TCP port and serves read-only HTTP responses.

Reason: manual browser/phone test command.

Tests: not directly blocking-tested; handler is tested with ephemeral server.

### `run_once_smoke()`

Purpose: deterministic non-blocking verification of server rendering and API payload.

Inputs: none.

Outputs: status code.

Side effects: local CPU calculation only.

Reason: package verification command.

Tests: smoke command test.

### `parse_args(argv)`

Purpose: parse server CLI host, port and smoke options.

Inputs: optional argv sequence.

Outputs: argparse namespace.

Side effects: none.

Reason: server command contract.

Tests: smoke command and command documentation.

### `main(argv)`

Purpose: server module entrypoint.

Inputs: optional argv sequence.

Outputs: process status code.

Side effects: either runs smoke calculation or binds HTTP server.

Reason: `python3 -m ...server` command.

Tests: smoke command test.

## Changed functions

None intended.

## Removed functions

None.

## Important unchanged functions

### `build_weekly_plan()`

Reason for no change: P0020 must expose the P0018 planner, not rewrite it.

### `rows_for_plan()`

Reason for no change: P0020 uses the existing P0018 row contract for HTML and JSON output.

## Design deviations during implementation

None yet.
