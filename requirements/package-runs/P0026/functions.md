# P0026 function design

## New Functions

### `validate_octet(octet)`

- Purpose: Normalize and validate the internal technical-network last octet.
- Inputs: `int` or exact integer string.
- Outputs: integer octet in `1..254`.
- Side effects: none.
- Reason: Reject invalid endpoint selectors before any HTTP request.
- Test coverage: valid known octets, boundaries, malformed values and booleans.

### `build_nat_base_url(octet)`

- Purpose: Construct the fixed operator-side Shelly NAT base URL.
- Inputs: octet accepted by `validate_octet`.
- Outputs: URL string ending in `/`.
- Side effects: none.
- Reason: Keep host and port derivation centralized and non-arbitrary.
- Test coverage: octet `40 -> http://192.168.86.240:8040/`, octet `30 -> http://192.168.86.240:8030/`.

### `validate_kvs_key(key)`

- Purpose: Normalize and validate the requested KVS key.
- Inputs: string.
- Outputs: normalized key string.
- Side effects: none.
- Reason: Prevent empty/control/path/full-URL inputs from becoming endpoint overrides.
- Test coverage: valid dotted key, encoded special characters, full URL and path rejection.

### `build_kvs_get_url(octet, key)`

- Purpose: Construct the complete read-only `KVS.Get` URL.
- Inputs: octet and key.
- Outputs: full URL with encoded `key` query parameter.
- Side effects: none.
- Reason: Guarantee the fixed host/path/query model.
- Test coverage: exact path, fixed host, URL-encoded query.

### `kvs_get_by_nat_octet(octet, key, timeout=5.0, audit_path=None, opener=None)`

- Purpose: Perform one read-only Shelly `KVS.Get` through the derived NAT URL.
- Inputs: octet, key, timeout, optional audit path, optional test opener.
- Outputs: `KvsReadResult`.
- Side effects: one HTTP GET and one audit JSONL append after validation.
- Reason: Public P0026 operation for CLI and future read-only bridge work.
- Test coverage: mocked success, non-200 HTTP, timeout, malformed JSON, Shelly error object and audit behavior.

### `write_audit_record(record, audit_path=None)`

- Purpose: Append one JSONL audit record.
- Inputs: mapping record and optional path.
- Outputs: resolved audit path.
- Side effects: creates parent directory if needed and appends one line.
- Reason: Persist each validated read attempt with enough evidence for package/live diagnostics.
- Test coverage: success record written to temporary file.

### `main(argv=None)`

- Purpose: CLI entry point for `python3 -m src.mac.tools.local_kvs_read`.
- Inputs: CLI args.
- Outputs: process status code.
- Side effects: prints JSON result, may perform one HTTP read and audit write.
- Reason: Manual/debug operator use.
- Test coverage: covered indirectly by core behavior; direct CLI smoke may be added if needed.

## Changed Functions

None.

## Removed Functions

None.

## Functions Intentionally Not Created

- No KVS write helpers.
- No script control helpers.
- No switch/light/cover helpers.
- No device/component/config write helpers.
- No generic URL fetch/proxy function.
