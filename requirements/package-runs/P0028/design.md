# P0028 implementation design

## Package Interpretation

P0028 promotes the P0027 bridge into a true MCP stdio-compatible server for the package-required subset of MCP 2025-06-18: initialization, initialized notification handling, tool discovery and tool invocation. It is protocol adaptation only.

## Chosen Module Path

Use a new service adapter:

```text
src/mac/services/local_operator_mcp/
  __init__.py
  __main__.py
  core.py
```

Tests:

```text
tests/mac/services/local_operator_mcp/
```

## MCP Spec / Version Checked

Target protocol revision:

```text
2025-06-18
```

Checked current official MCP pages for stdio transport, lifecycle, schema and tools. The implementation follows newline-delimited JSON-RPC stdio, `initialize`, `notifications/initialized`, `tools/list`, `tools/call`, `inputSchema` and MCP tool result `content`/`isError`.

## Stdio Framing Model

The server reads UTF-8 JSON-RPC messages one line at a time from stdin and writes one newline-delimited JSON response to stdout for requests. Notification messages such as `notifications/initialized` do not produce stdout responses.

No diagnostic text is written to stdout. Any future diagnostics must go to stderr.

## Initialization / Lifecycle Model

`initialize` returns:

```json
{
  "protocolVersion": "2025-06-18",
  "capabilities": {"tools": {"listChanged": false}},
  "serverInfo": {
    "name": "g2-local-operator-mcp",
    "title": "G2 Local Operator MCP",
    "version": "0.1.0"
  }
}
```

If the client requests `2025-06-18`, respond with the same version. Otherwise respond with the server-supported version, per MCP version negotiation.

`notifications/initialized` is accepted as a notification and returns no response.

## Tools/List Model

`tools/list` returns exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

The schema uses MCP spelling `inputSchema` and allows only `octet`, `key` and optional `timeout`.

## Tools/Call Model

`tools/call` validates the tool name and arguments, then delegates to P0027:

```python
src.mac.services.local_operator_bridge.handle_tool_call(...)
```

P0027 delegates valid calls to P0026 `kvs_get_by_nat_octet(...)`.

## MCP Tool Result Content Model

The P0027/P0026 structured result is JSON-encoded into a single MCP text content item:

```json
{
  "content": [{"type": "text", "text": "{...json...}"}],
  "isError": false
}
```

If P0026 returns `ok: false`, the MCP result still uses the tool result shape and sets `isError: true`. Unknown tools, bad arguments and malformed protocol messages are protocol/JSON-RPC errors and do not call P0026.

## Validation and Error Mapping

- Malformed JSON: JSON-RPC parse error `-32700`.
- Non-object request: invalid request `-32600`.
- Unknown method: method not found `-32601`.
- Invalid `tools/call` params or unknown tool: invalid params `-32602`.
- Internal unexpected bridge failure: internal error `-32603`.
- P0026 read/network/Shelly failure: MCP tool result with `isError: true`.

## P0027/P0026 Integration Model

P0028 imports P0027 constants and routing. It does not import or call P0026 directly except through P0027. This keeps the one place for bridge-level argument validation and P0026 delegation.

## Forbidden Operations Not Implemented

No new Shelly tools, `KVS.Set`, `Script.*`, switch/light/cover/relay/dimmer/actuator calls, component/config/device writes, URL fetch, generic proxy, shell execution, Codex runner, Home Assistant bridge, Streamable HTTP or launchd/persistent service installation.

## Live-Test Boundary

Optional live verification may send initialize, initialized notification, tools/list and a single tools/call for octet `30`, key `hp.price.status`, timeout `5`. It must use the P0028 MCP stdio entry point and the existing P0027/P0026 path.

## Verification Commands

```bash
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/tools
python3 -m unittest discover tests/mac/services/local_operator_bridge
python3 -m unittest discover tests/mac/services/local_operator_mcp
python3 -m unittest discover tests/mac/services
git diff --check
```

## Risks and Uncertainties

- This is stdio MCP only, not Streamable HTTP.
- The implementation covers the required MCP lifecycle/tool subset and does not implement unrelated MCP primitives such as prompts, resources, logging negotiation or cancellation.
