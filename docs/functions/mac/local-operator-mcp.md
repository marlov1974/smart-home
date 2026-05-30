# Mac Local Operator MCP

Last changed: P0028

## Purpose

`src.mac.services.local_operator_mcp` is the true MCP stdio adapter for the read-only local operator bridge. It exposes exactly one MCP tool and delegates valid calls to P0027, which delegates to the verified P0026 Shelly KVS.Get helper.

P0028 is protocol adaptation only. It adds no new Shelly capability.

## MCP Compatibility

Target protocol revision:

```text
2025-06-18
```

Supported MCP stdio surface:

- newline-delimited JSON-RPC messages over stdin/stdout
- `initialize`
- `notifications/initialized`
- `tools/list`
- `tools/call`
- MCP tool result shape with `content` and `isError`

Unsupported by design:

- Streamable HTTP
- prompts, resources, sampling, logging negotiation and unrelated MCP primitives
- persistent launchd/service installation

## CLI

```bash
python3 -m src.mac.services.local_operator_mcp serve
```

The process reads MCP JSON-RPC messages from stdin and writes only valid JSON-RPC/MCP response lines to stdout. Diagnostics must go to stderr.

## Mac Host Wrapper

P0028 host-integration follow-up established this wrapper for local MCP hosts:

```text
/Users/marcus.lovenstad/bin/g2-local-operator-mcp
```

Wrapper behavior:

```sh
cd /Users/marcus.lovenstad/dev/smart-home
exec python3 -m src.mac.services.local_operator_mcp serve
```

Codex Desktop/App config entry:

```toml
[mcp_servers.g2-local-operator]
args = []
command = "/Users/marcus.lovenstad/bin/g2-local-operator-mcp"
startup_timeout_sec = 30
```

The host may need restart or config reload before the tool appears.

## Initialize

`initialize` returns:

```json
{
  "protocolVersion": "2025-06-18",
  "capabilities": {
    "tools": {
      "listChanged": false
    }
  },
  "serverInfo": {
    "name": "g2-local-operator-mcp",
    "title": "G2 Local Operator MCP",
    "version": "0.1.0"
  }
}
```

## Tool Discovery

`tools/list` returns exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

Its schema uses MCP `inputSchema` and allows only:

- `octet`
- `key`
- optional `timeout`

## Tool Call

Example request:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"shelly_kvs_get_by_nat_octet","arguments":{"octet":30,"key":"hp.price.status","timeout":5}}}
```

The response is an MCP `CallToolResult`. The P0027/P0026 structured payload is encoded as JSON text in one content item:

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"tool\":\"shelly_kvs_get_by_nat_octet\",...}"
    }
  ],
  "isError": false
}
```

If P0026 returns `ok: false`, the MCP tool result uses the same shape with `isError: true`.

## Delegation

P0028 delegates to:

```text
src.mac.services.local_operator_bridge.handle_tool_call(...)
```

That P0027 bridge delegates to:

```text
src.mac.tools.local_kvs_read.kvs_get_by_nat_octet(...)
```

## Forbidden Operations

The MCP server does not implement:

- extra tools beyond `shelly_kvs_get_by_nat_octet`
- `KVS.Set`
- `Script.*`
- `Switch.*`, `Light.*`, `Cover.*`
- relay, dimmer or actuator calls
- component/config/device writes
- arbitrary URL fetch or generic HTTP proxy
- shell execution
- Codex package runner
- Home Assistant bridge
- Streamable HTTP
- persistent launchd/service installation

## Functions

### `handle_initialize(params)`

Formats the MCP initialize result.

### `handle_initialized_notification(params=None)`

Accepts the initialized notification and emits no response.

### `list_mcp_tools()`

Returns one MCP tool definition with `inputSchema`.

### `call_mcp_tool(params, bridge_handler=None)`

Validates `tools/call` params and delegates to P0027.

### `format_mcp_tool_result(tool_payload)`

Formats P0027/P0026 payload as an MCP `CallToolResult`.

### `handle_mcp_message(message, bridge_handler=None)`

Routes one decoded MCP JSON-RPC message.

### `process_mcp_line(line, bridge_handler=None)`

Processes one newline-delimited MCP JSON-RPC line.

### `serve(input_stream=None, output_stream=None, error_stream=None, bridge_handler=None)`

Runs the stdio loop until EOF.

## Test Coverage

P0028 tests live under:

```text
tests/mac/services/local_operator_mcp/
```

They mock the P0027 bridge and do not require live network access.
