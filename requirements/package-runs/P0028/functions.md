# P0028 function design

## New Functions

### `handle_initialize(params)`

- Purpose: Return MCP initialize result with protocol version, capabilities and serverInfo.
- Inputs: decoded params object.
- Outputs: initialize result dict.
- Side effects: none.
- Test coverage: protocol version and tools capability.

### `handle_initialized_notification(params)`

- Purpose: Accept MCP initialized notification.
- Inputs: optional params.
- Outputs: `None`.
- Side effects: none.
- Test coverage: notification produces no stdout response.

### `list_mcp_tools()`

- Purpose: Return MCP tool discovery metadata with `inputSchema`.
- Inputs: none.
- Outputs: `{"tools": [...]}`.
- Side effects: none.
- Test coverage: exactly one tool and correct schema spelling.

### `call_mcp_tool(params, bridge_handler=None)`

- Purpose: Handle one MCP `tools/call` by delegating to P0027.
- Inputs: params object and optional injected bridge handler for tests.
- Outputs: MCP tool result dict with `content` and `isError`.
- Side effects: one P0027/P0026 call for a valid tool request.
- Test coverage: successful result, delegated failure, unknown/write-like tool rejection and extra arguments.

### `format_mcp_tool_result(tool_payload)`

- Purpose: Convert P0027/P0026 result payload to MCP `CallToolResult`.
- Inputs: bridge payload dict.
- Outputs: dict with `content` and `isError`.
- Side effects: none.
- Test coverage: `isError: false` for `ok: true`, `isError: true` for `ok: false`.

### `handle_mcp_message(message, bridge_handler=None)`

- Purpose: Process one decoded MCP JSON-RPC message.
- Inputs: decoded JSON object and optional bridge handler.
- Outputs: response dict or `None` for notifications.
- Side effects: may delegate one valid tool call.
- Test coverage: initialize, initialized notification, tools/list, tools/call, unknown method and invalid request.

### `process_mcp_line(line, bridge_handler=None)`

- Purpose: Parse one stdin line and produce one stdout response line when required.
- Inputs: JSON text line.
- Outputs: JSON response line or `None` for notifications.
- Side effects: may delegate one valid tool call.
- Test coverage: malformed JSON, valid request framing and no embedded diagnostics.

### `serve(input_stream=None, output_stream=None, error_stream=None, bridge_handler=None)`

- Purpose: Run the MCP stdio loop until EOF.
- Inputs: text streams and optional bridge handler.
- Outputs: process status code.
- Side effects: reads stdin, writes only MCP messages to stdout.
- Test coverage: in-memory serve sequence for initialize, initialized, tools/list and tools/call.

### `main(argv=None)`

- Purpose: CLI entry point for `python3 -m src.mac.services.local_operator_mcp serve`.
- Inputs: CLI args.
- Outputs: process status code.
- Side effects: runs `serve`.
- Test coverage: indirect through `serve`.

## Changed Functions

None.

## Removed Functions

None.

## Functions Intentionally Not Created

- No extra MCP tools.
- No Streamable HTTP transport.
- No shell execution.
- No URL fetch/proxy.
- No KVS write or device-control helper.
