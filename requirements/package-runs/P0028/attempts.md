# P0028 attempts

## Attempt 1

- Status: completed
- Change summary: create true MCP stdio adapter above P0027/P0026 with exactly one read-only tool.
- Initial tests:
  - `python3 -m unittest discover tests/mac/services/local_operator_mcp` initially failed because the MCP adapter delegated unknown tool names and extra arguments to the injected bridge handler before local MCP validation.
  - Fixed `call_mcp_tool(...)` to reject unknown tool names and validate arguments with P0027 `validate_tool_arguments(...)` before delegation.
- Tests run after fix:
  - `python3 -m unittest discover tests/mac/services/local_operator_mcp` passed.
  - `python3 -m unittest discover tests/mac/services` passed.
  - `python3 -m unittest discover tests/mac/tools` passed.
- Live MCP stdio verification:
  - Command/session:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"codex-p0028","version":"1.0"}}}' '{"jsonrpc":"2.0","method":"notifications/initialized"}' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"shelly_kvs_get_by_nat_octet","arguments":{"octet":30,"key":"hp.price.status","timeout":5}}}' | python3 -m src.mac.services.local_operator_mcp serve
```

  - Initialize response summary: `protocolVersion: 2025-06-18`, `capabilities.tools.listChanged: false`, server name `g2-local-operator-mcp`.
  - Initialized notification: accepted with no stdout response.
  - Tools/list summary: exactly one tool, `shelly_kvs_get_by_nat_octet`, using `inputSchema`.
  - Tools/call:
    - Tool: `shelly_kvs_get_by_nat_octet`
    - Octet: `30`
    - KVS key: `hp.price.status`
    - Timeout: `5`
    - P0026-derived URL: `http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status`
  - First sandboxed run: MCP framing succeeded, but tool result had `isError: true`; P0026 returned `result_status: network_error` and an audit permission error for `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.
  - Escalated read-only live run: HTTP `200`, P0026 `result_status: success`, MCP `isError: false`, result value `"ok"`, audit path `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.
  - Proof of read-only scope: MCP session used only `initialize`, `notifications/initialized`, `tools/list` and one `tools/call` for `shelly_kvs_get_by_nat_octet`; implementation delegates to P0027/P0026 and exposes no write-like tools.
- Final verification:
  - `python3 -m unittest discover tests/mac/tools/local_kvs_read` passed.
  - `python3 -m unittest discover tests/mac/tools` passed.
  - `python3 -m unittest discover tests/mac/services/local_operator_bridge` passed.
  - `python3 -m unittest discover tests/mac/services/local_operator_mcp` passed.
  - `python3 -m unittest discover tests/mac/services` passed.
  - `git diff --check` passed.
- Result: implementation, tests and live MCP verification passed.
