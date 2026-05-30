# P0027 attempts

## Attempt 1

- Status: completed
- Change summary: create an MCP-shaped read-only local JSON-RPC bridge that exposes exactly one tool and delegates to P0026.
- Tests run:
  - `python3 -m unittest discover tests/mac/services/local_operator_bridge` passed.
  - `python3 -m unittest discover tests/mac/services` passed.
  - `python3 -m unittest discover tests/mac/tools/local_kvs_read` passed.
  - `python3 -m unittest discover tests/mac/tools` passed.
- Live bridge verification:
  - Command:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":"live-p0027","method":"tools/call","params":{"name":"shelly_kvs_get_by_nat_octet","arguments":{"octet":30,"key":"hp.price.status","timeout":5}}}' | python3 -m src.mac.services.local_operator_bridge serve
```

  - Tool: `shelly_kvs_get_by_nat_octet`
  - Octet: `30`
  - KVS key: `hp.price.status`
  - Timeout: `5`
  - P0026-derived URL: `http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status`
  - First sandboxed run: bridge protocol succeeded but P0026 returned `result_status: network_error` and audit permission error for `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.
  - Escalated read-only live run: HTTP `200`, `result_status: success`, result value `"ok"`, audit path `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.
  - Proof of read-only scope: the bridge request used only `tools/call` for `shelly_kvs_get_by_nat_octet`; implementation delegates to P0026 `KVS.Get` and exposes no write-like public tools.
- Final verification:
  - `python3 -m unittest discover tests/mac/tools/local_kvs_read` passed.
  - `python3 -m unittest discover tests/mac/tools` passed.
  - `python3 -m unittest discover tests/mac/services` passed.
  - `git diff --check` passed.
- Result: implementation, tests and live bridge verification passed.
