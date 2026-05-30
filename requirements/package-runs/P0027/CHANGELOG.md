# P0027 changelog

## Status

Implemented and verified with read-only live bridge call.

## User-visible behavior changed

Added a local operator bridge POC:

```bash
python3 -m src.mac.services.local_operator_bridge serve
```

It accepts newline-delimited JSON-RPC-like requests on stdin and writes one JSON response per line. The bridge exposes exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

## Files changed

- Added `src/mac/services/local_operator_bridge/`.
- Added `tests/mac/services/local_operator_bridge/`.
- Added `tests/mac/services/__init__.py`.
- Added `docs/functions/mac/local-operator-bridge.md`.
- Updated `docs/functions/00-index.md`.
- Added P0027 package-run review/design/functions/attempts evidence.
- Updated `requirements/packages/P0027-read-only-mcp-local-operator-bridge.md` completion/status.

## Contracts changed

The bridge is documented as an MCP-shaped local JSON-RPC POC, not a true MCP stdio server. It supports `tools/list` and `tools/call`, accepts only `octet`, `key` and optional `timeout`, and delegates the only valid tool call to P0026.

## Verification performed

- `python3 -m unittest discover tests/mac/services/local_operator_bridge`
- `python3 -m unittest discover tests/mac/services`
- `python3 -m unittest discover tests/mac/tools/local_kvs_read`
- `python3 -m unittest discover tests/mac/tools`
- Live bridge command:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":"live-p0027","method":"tools/call","params":{"name":"shelly_kvs_get_by_nat_octet","arguments":{"octet":30,"key":"hp.price.status","timeout":5}}}' | python3 -m src.mac.services.local_operator_bridge serve
```

Live bridge result:

- Tool: `shelly_kvs_get_by_nat_octet`
- Derived URL: `http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status`
- First sandboxed run: P0026 returned `result_status: network_error` with audit permission error.
- Escalated read-only live run: HTTP `200`, `result_status: success`, result value `"ok"`, audit path `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.
- No write-capable RPC, script control, actuator command, generic proxy, shell command, Codex runner or MCP daemon install was used.

## Known limitations and follow-up

- This is MCP-shaped JSON-RPC only; true MCP stdio compatibility remains future work.
- The bridge intentionally exposes only the P0026 read-only KVS.Get helper.
- No persistent service/launchd installation was added.

## Bootstrap for next package

Read `docs/functions/mac/local-operator-bridge.md` for the durable bridge contract. The implementation lives in `src/mac/services/local_operator_bridge/core.py`, with mocked unit tests in `tests/mac/services/local_operator_bridge/test_core.py`.
