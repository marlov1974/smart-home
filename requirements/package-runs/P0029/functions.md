# P0029 function design

## New functions

### `is_allowed_origin(origin)`

- Purpose: enforce localhost-only browser origins for the local HTTP wrapper.
- Inputs: optional origin string.
- Outputs: boolean.
- Side effects: none.
- Test coverage: unit tests for missing, localhost and remote origins.

### `json_response_bytes(payload)`

- Purpose: serialize JSON-RPC/MCP response payloads for HTTP.
- Inputs: mapping payload.
- Outputs: UTF-8 JSON bytes.
- Side effects: none.
- Test coverage: indirect through HTTP tests.

### `handle_http_mcp_message(message, bridge_handler=None)`

- Purpose: delegate one decoded MCP JSON-RPC message to P0028.
- Inputs: decoded JSON object and optional mocked bridge handler.
- Outputs: P0028 response object or `None` for accepted notifications.
- Side effects: may delegate valid tool calls to P0028/P0027/P0026.
- Test coverage: indirect through POST tests.

### `make_handler(bridge_handler=None)`

- Purpose: create a `BaseHTTPRequestHandler` subclass bound to the optional bridge handler.
- Inputs: optional bridge handler.
- Outputs: request handler class.
- Side effects: none directly; handler instances read/write HTTP streams.
- Test coverage: local test server tests.

### `serve(host="127.0.0.1", port=8765, bridge_handler=None)`

- Purpose: run the development/manual Streamable HTTP MCP wrapper.
- Inputs: host, port, optional bridge handler.
- Outputs: process exit code when stopped.
- Side effects: binds local TCP socket and serves HTTP.
- Test coverage: handler covered by tests; long-running CLI not exercised directly.

### `main(argv=None)`

- Purpose: CLI entry point for P0029 server.
- Inputs: argv.
- Outputs: process exit code.
- Side effects: starts server for `serve`.
- Test coverage: argument behavior covered lightly if needed.

## Changed functions

None planned. P0029 should reuse P0028/P0027/P0026 without modifying their functions.

## Removed functions

None.
