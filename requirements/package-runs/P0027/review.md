# P0027 consistency review

## Result

WARN

P0027 is implementable within the repository's current Mac tooling/service model and can reuse P0026 without expanding Shelly access. The warning is protocol-related: a fully true MCP stdio server implies precise MCP framing, initialization and capability semantics that are larger than the safe P0027 scope when using only the Python standard library and no MCP SDK. P0027 will therefore implement an MCP-shaped local JSON-RPC bridge POC, not claim full MCP stdio compatibility.

## Checks

- P0026 is present, implemented and status-corrected to `verified-local-live`.
- P0026 live evidence shows read-only `KVS.Get` for octet `30`, key `hp.price.status`, HTTP `200`, `result_status: success`.
- P0027 can import and call `src.mac.tools.local_kvs_read.kvs_get_by_nat_octet(...)`; it will not duplicate Shelly HTTP URL construction or network logic.
- Proposed files are inside allowed service/test/docs/package-run scope:
  - `src/mac/services/local_operator_bridge/**`
  - `tests/mac/services/local_operator_bridge/**`
  - `docs/functions/mac/local-operator-bridge.md`
  - `docs/functions/00-index.md`
  - `requirements/package-runs/P0027/**`
  - `requirements/packages/P0027-read-only-mcp-local-operator-bridge.md`
- The bridge remains one-tool-only: `shelly_kvs_get_by_nat_octet`.
- Unknown tools, write-like names, arbitrary URLs, shell commands and generic proxy requests are rejected before P0026 is called.
- No live writes are needed for verification.

## Decision

Continue with an MCP-shaped newline-delimited JSON-RPC POC over stdin/stdout. It supports `tools/list` and `tools/call`, uses Python standard library only, and delegates the only tool call to P0026.
