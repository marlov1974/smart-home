# Mac Local KVS Read POC

Last changed: P0026

## Purpose

`src.mac.tools.local_kvs_read` is a narrow Mac-side proof of concept for reading exactly one Shelly KVS key through the operator NAT convention.

It is intentionally read-only. It does not implement KVS writes, script control, switch/light/cover control, component/config/device writes, arbitrary URL input, POST JSON-RPC or a generic HTTP proxy.

## Public CLI

```bash
python3 -m src.mac.tools.local_kvs_read get --octet 40 --key hp.price.status
```

Optional:

```bash
--timeout 5
--audit-path /path/to/audit.jsonl
```

The CLI prints a JSON result and exits with:

- `0` on successful Shelly JSON response
- `1` on HTTP/network/timeout/JSON/Shelly error response
- `2` on local input validation error

## URL Contract

The runtime URL is derived only from:

- fixed host: `192.168.86.240`
- fixed path: `/rpc/KVS.Get`
- octet-derived port: `8000 + octet`
- URL-encoded query parameter: `key=<KVS key>`

Examples:

```text
build_nat_base_url(40) -> http://192.168.86.240:8040/
build_nat_base_url(30) -> http://192.168.86.240:8030/
build_kvs_get_url(40, "hp.price.status") -> http://192.168.86.240:8040/rpc/KVS.Get?key=hp.price.status
```

## Functions

### `validate_octet(octet)`

Accepts an integer or exact integer string and returns an integer in `1..254`. Invalid values are rejected before network access.

### `build_nat_base_url(octet)`

Returns the fixed operator NAT base URL for one Shelly octet.

### `validate_kvs_key(key)`

Accepts a non-empty KVS key string. Rejects control characters, full URLs, leading paths and embedded `/rpc/` path overrides.

### `build_kvs_get_url(octet, key)`

Returns the complete fixed-path `KVS.Get` URL with the key encoded by `urllib.parse.urlencode`.

### `kvs_get_by_nat_octet(octet, key, timeout=5.0, audit_path=None, opener=None)`

Performs one HTTP `GET` against the derived URL and returns `KvsReadResult`.

Normal failure statuses are returned as data:

- `network_error`
- `timeout`
- `http_error`
- `json_error`
- `shelly_error`
- `unexpected_error`

Validation failures raise `LocalKvsReadError` before any HTTP request.

### `write_audit_record(record, audit_path=None)`

Appends one JSONL audit record. The default audit path is:

```text
~/.smart-home/local_kvs_read_audit.jsonl
```

Each validated read attempt records timestamp, package id, octet, key, built URL, HTTP status, result status and error summary.

## Test Coverage

P0026 tests live under:

```text
tests/mac/tools/local_kvs_read/
```

They use mocked HTTP openers and do not require live Shelly or local network access.
