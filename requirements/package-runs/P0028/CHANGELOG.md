# P0028 changelog

## Status

Implemented and verified with read-only live MCP stdio call.

## User-visible behavior changed

Added a true MCP stdio-compatible local server for the existing read-only Shelly KVS tool:

```bash
python3 -m src.mac.services.local_operator_mcp serve
```

It supports `initialize`, `notifications/initialized`, `tools/list` and `tools/call` for exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

## Files changed

- Added `src/mac/services/local_operator_mcp/`.
- Added `tests/mac/services/local_operator_mcp/`.
- Added `docs/functions/mac/local-operator-mcp.md`.
- Updated `docs/functions/00-index.md`.
- Added P0028 package-run review/design/functions/attempts evidence.
- Updated `requirements/packages/P0028-true-mcp-stdio-local-operator-bridge.md` completion/status.

## Contracts changed

P0028 adds a true MCP stdio adapter for MCP protocol revision `2025-06-18`. It reuses P0027/P0026 and does not add any new Shelly capability. Tool metadata uses MCP `inputSchema`; tool calls return MCP `content` and `isError`.

## Verification performed

- MCP spec check against official `modelcontextprotocol.io` `2025-06-18` transport, lifecycle, tools and schema pages.
- `python3 -m unittest discover tests/mac/services/local_operator_mcp`
- `python3 -m unittest discover tests/mac/services`
- `python3 -m unittest discover tests/mac/tools`
- Live MCP stdio session:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"codex-p0028","version":"1.0"}}}' '{"jsonrpc":"2.0","method":"notifications/initialized"}' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"shelly_kvs_get_by_nat_octet","arguments":{"octet":30,"key":"hp.price.status","timeout":5}}}' | python3 -m src.mac.services.local_operator_mcp serve
```

Live MCP result:

- Initialize: `protocolVersion: 2025-06-18`, tools capability advertised.
- Initialized notification: no stdout response.
- Tools/list: exactly `shelly_kvs_get_by_nat_octet`.
- Tools/call derived URL: `http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status`
- First sandboxed run: MCP framing worked, but P0026 returned `network_error` and audit permission error.
- Escalated read-only live run: HTTP `200`, P0026 `result_status: success`, MCP `isError: false`, value `"ok"`, audit path `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.
- No write-capable RPC, script control, actuator command, generic proxy, shell command, Codex runner, Streamable HTTP server or persistent install was used.

## Known limitations and follow-up

- This is stdio MCP only, not Streamable HTTP.
- Only the P0028-required MCP lifecycle/tool subset is implemented.
- The server intentionally exposes only the P0026 read-only KVS.Get helper.
- No persistent service/launchd installation was added.

## Bootstrap for next package

Read `docs/functions/mac/local-operator-mcp.md` for the durable MCP server contract. The implementation lives in `src/mac/services/local_operator_mcp/core.py`, with mocked unit tests in `tests/mac/services/local_operator_mcp/test_core.py`.
