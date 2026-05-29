# P0026 changelog

## Status

Implemented and verified locally.

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

Live KVS.Get verification was skipped because no explicit live octet/key was supplied.

## Known limitations and follow-up

- This is still a POC and does not resolve logical devices from the registry.
- It intentionally supports only fixed-host, fixed-path, read-only `KVS.Get`.
- No MCP server, persistent service or production deployment was added.

## Bootstrap for next package

Read `docs/functions/mac/local-kvs-read-poc.md` for the durable function contract. The implementation lives in `src/mac/tools/local_kvs_read/core.py`, with mocked unit tests in `tests/mac/tools/local_kvs_read/test_core.py`.
