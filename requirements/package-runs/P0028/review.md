# P0028 consistency review

## Result

PASS

P0028 is consistent and implementable as a true MCP stdio-compatible server for the narrow surface required by this package. The implementation can stay in Python standard library, reuse P0027/P0026, and avoid adding any new Shelly capability.

## MCP Spec Evidence

Checked MCP protocol revision `2025-06-18` on `modelcontextprotocol.io`:

- `basic/transports`: stdio uses stdin/stdout, JSON-RPC messages are UTF-8, newline-delimited, and stdout must contain only valid MCP messages; logging may go to stderr.
- `basic/lifecycle`: the client sends `initialize`, the server responds with negotiated `protocolVersion`, `capabilities` and `serverInfo`; the client then sends `notifications/initialized`.
- `server/tools` and `schema`: tool servers declare the `tools` capability; `tools/list` returns tool definitions using `inputSchema`; `tools/call` returns `content` and `isError`; tool-originated errors should be represented in the tool result with `isError: true`.

## Repository Checks

- P0026 is present and `verified-local-live`.
- P0027 is present, `verified-local-live`, and explicitly documented as an MCP-shaped JSON-RPC POC rather than true MCP stdio.
- P0028 can reuse P0027 `handle_tool_call(...)` and P0026 through that path.
- Proposed files are inside allowed scope:
  - `src/mac/services/local_operator_mcp/**`
  - `tests/mac/services/local_operator_mcp/**`
  - `docs/functions/mac/local-operator-mcp.md`
  - `docs/functions/00-index.md`
  - `requirements/package-runs/P0028/**`
  - `requirements/packages/P0028-true-mcp-stdio-local-operator-bridge.md`
- No live writes are required for verification.

## Safety Decision

Continue implementation. P0028 will add protocol adaptation only:

- one MCP tool: `shelly_kvs_get_by_nat_octet`
- read-only P0027/P0026 delegation
- no generic URL, shell, proxy, Codex runner, HA bridge, Streamable HTTP or persistent service.
