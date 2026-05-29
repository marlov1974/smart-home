# P0026 changelog

## Status

Implemented, package status corrected to `verified-local-live`, and read-only live KVS.Get verified.

## User-visible behavior changed

Added a Mac CLI/module for one read-only Shelly KVS.Get through the operator NAT convention:

```bash
python3 -m src.mac.tools.local_kvs_read get --octet 40 --key hp.price.status
```

The command prints structured JSON and audit-logs validated read attempts.

## Files changed

- Added `src/mac/tools/local_kvs_read/`.
- Added `tests/mac/tools/local_kvs_read/`.
- Added `docs/functions/mac/local-kvs-read-poc.md`.
- Updated `docs/functions/00-index.md`.
- Added P0026 package-run review/design/functions/attempts evidence.

## Contracts changed

The new function contract is documented in `docs/functions/mac/local-kvs-read-poc.md`.

The NAT port is implemented as `8000 + octet`, preserving documented examples such as `40 -> 8040` and supporting the package-required octet range `1..254`.

## Verification performed

- `python3 -m unittest discover tests/mac/tools/local_kvs_read`
- `python3 -m unittest discover tests/mac/tools`
- `python3 -m src.mac.tools.local_kvs_read get --octet 0 --key hp.price.status`
- `python3 -m src.mac.tools.local_kvs_read get --octet 30 --key hp.price.status --timeout 5`

Live KVS.Get follow-up:

- Derived URL: `http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status`
- First sandboxed run: failed with `result_status: network_error` and audit directory permission error for `/Users/marcus.lovenstad/.smart-home`.
- Escalated read-only run: succeeded with HTTP `200`, `result_status: success`, result value `"ok"` and audit path `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`.

No write-capable RPC, script control, actuator command, generic proxy or MCP server was used.

## Known limitations and follow-up

- This is still a POC and does not resolve logical devices from the registry.
- It intentionally supports only fixed-host, fixed-path, read-only `KVS.Get`.
- No MCP server, persistent service or production deployment was added.

## Bootstrap for next package

Read `docs/functions/mac/local-kvs-read-poc.md` for the durable function contract. The implementation lives in `src/mac/tools/local_kvs_read/core.py`, with mocked unit tests in `tests/mac/tools/local_kvs_read/test_core.py`.
