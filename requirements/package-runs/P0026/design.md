# P0026 implementation design

## Package Interpretation

Build a minimal Mac-side Python standard-library tool that performs exactly one Shelly read operation:

```text
KVS.Get by explicit NAT octet and KVS key
```

The tool must not become a generic HTTP client, proxy, MCP server, deploy helper, or write-capable Shelly RPC wrapper.

## Module and CLI Structure

Use:

```text
src/mac/tools/local_kvs_read/
  __init__.py
  __main__.py
  core.py
```

The CLI shape will be:

```bash
python3 -m src.mac.tools.local_kvs_read get --octet 40 --key hp.price.status
```

## URL Construction Model

Constants:

```text
NAT_HOST = 192.168.86.240
KVS_GET_PATH = /rpc/KVS.Get
```

The NAT base URL is:

```text
http://192.168.86.240:<8000 + octet>/
```

This matches documented examples for known devices and preserves the package-required octet range `1..254`.

## Input Validation Model

- Octet must be an integer in `1..254`.
- Strings such as `"40"` are accepted by the CLI/core validator if they parse exactly as an integer.
- Empty, malformed, boolean and out-of-range octets are rejected before network access.
- KVS key must be a non-empty string without control characters.
- Full URL or path-like key inputs are rejected so callers cannot smuggle host/path/method overrides.

## KVS Key Encoding Model

Use `urllib.parse.urlencode({"key": key})`. The key only appears as the `key` query parameter for `/rpc/KVS.Get`.

## HTTP Timeout and Error Model

Use `urllib.request.urlopen` with a default bounded timeout of 5 seconds. The public read function accepts an injectable opener for tests.

Failures return a structured result instead of raising for normal network/HTTP/JSON/Shelly error cases:

- `network_error`
- `timeout`
- `http_error`
- `json_error`
- `shelly_error`
- `unexpected_error`

Validation errors raise `LocalKvsReadError` before any HTTP request.

## JSON Response Handling Model

The tool decodes JSON when possible and requires a top-level object. A response with an `error` field is a Shelly error. A successful response returns the parsed `result` value if present, otherwise the parsed response object.

## Audit Log Model

Every attempted read after validation writes one JSONL audit record containing timestamp, octet, key, built URL, HTTP status, result status and error summary. The default audit path is:

```text
~/.smart-home/local_kvs_read_audit.jsonl
```

Tests pass a temporary audit path. If audit writing itself fails, the tool still returns the read result with an `audit_error` field so diagnostics are visible.

## Live-Test Boundary

No live verification will be attempted unless an explicit octet/key is supplied. If live verification is skipped, unit tests are the verification basis.

## Forbidden RPC Methods Not Implemented

P0026 will not implement `KVS.Set`, `Script.*`, `Switch.*`, `Light.*`, `Cover.*`, component/config/device write helpers, arbitrary URL input, POST JSON-RPC, or a generic local HTTP proxy.

## Test Strategy

- Unit-test URL building and encoding.
- Unit-test octet/key validation and prove invalid input makes no HTTP request.
- Unit-test mocked HTTP success, HTTP error, timeout, malformed JSON and Shelly error object.
- Unit-test audit record creation.
- Unit-test public module surface to confirm write helpers/generic proxy operations are absent.

## Verification Commands

```bash
python3 -m unittest discover tests/mac/tools
python3 -m unittest discover tests/mac/tools/local_kvs_read
git diff --check
```

## Risks and Uncertainties

- The port formula interpretation is documented in `review.md`; future packages may replace this POC with device-registry resolution if needed.
- Live NAT/device availability is not assumed.
