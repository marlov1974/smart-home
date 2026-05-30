# P0027 implementation design

## Package Interpretation

Build a small local bridge process that exposes the verified P0026 read-only KVS helper through a constrained JSON-RPC shape. P0027 must not add new Shelly access paths, write-capable operations, shell execution, generic HTTP access or production service installation.

## Chosen Module Path

Use a service path because the bridge is a local process boundary rather than a one-shot diagnostic tool:

```text
src/mac/services/local_operator_bridge/
  __init__.py
  __main__.py
  core.py
```

Tests:

```text
tests/mac/services/local_operator_bridge/
```

## Protocol Classification

P0027 implements:

```text
MCP-shaped local JSON-RPC bridge POC
```

It does not claim true MCP stdio compatibility. It deliberately omits full MCP initialization, capability negotiation and `Content-Length` framing. A later package can replace or wrap this with a true MCP server once dependency/protocol decisions are explicit.

## Protocol / Message Model

Use newline-delimited JSON-RPC-like messages over stdin/stdout.

Supported methods:

```text
tools/list
tools/call
```

Each input line is one JSON object. Each output line is one JSON object with `jsonrpc`, matching `id`, and either `result` or `error`.

## Tool Discovery Model

`tools/list` returns exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

The tool metadata includes a minimal input schema for `octet`, `key` and optional `timeout`.

## Tool-Call Input Schema

`tools/call` accepts:

```json
{
  "name": "shelly_kvs_get_by_nat_octet",
  "arguments": {
    "octet": 30,
    "key": "hp.price.status",
    "timeout": 5
  }
}
```

Only `octet`, `key` and `timeout` are allowed in `arguments`. Extra fields such as `url`, `host`, `path`, `method`, `shell` or write-operation hints are rejected before P0026 is called.

## Output Schema

Successful `tools/call` returns:

```json
{
  "tool": "shelly_kvs_get_by_nat_octet",
  "result": { "...P0026 KvsReadResult fields...": "..." }
}
```

Unknown tools and protocol errors return JSON-RPC-style local errors and do not call P0026.

## P0026 Integration Model

Import P0026:

```python
from src.mac.tools.local_kvs_read import kvs_get_by_nat_octet
```

The bridge calls that function exactly once per valid tool request. P0026 remains responsible for octet/key validation, URL construction, HTTP timeout behavior, JSON parsing and audit logging.

## Validation and Error Mapping

- Malformed JSON: local parse error.
- Non-object request: invalid request.
- Unknown method: method not found.
- Unknown tool: invalid params.
- Extra arguments: invalid params.
- P0026 validation errors: invalid params.
- P0026 read failures: returned as a successful bridge response containing P0026 `ok: false` result data, because the bridge itself handled the tool call.

## Audit Behavior

Audit logging is inherited from P0026. The bridge does not accept an audit-path argument in P0027, because the target input schema only allows octet/key/timeout.

## Forbidden Operations Not Implemented

No `KVS.Set`, `Script.*`, `Switch.*`, `Light.*`, `Cover.*`, relay, dimmer, actuator, component/config/device write, arbitrary URL fetch, shell execution, Codex package-runner, generic proxy, Home Assistant bridge or MCP server daemon installation is implemented.

## Live-Test Boundary

Optional live verification may call the bridge with octet `30`, key `hp.price.status`, timeout `5`. It must use only the bridge `tools/call` path, which delegates to P0026 `KVS.Get`.

## Verification Commands

```bash
python3 -m unittest discover tests/mac/tools/local_kvs_read
python3 -m unittest discover tests/mac/tools
python3 -m unittest discover tests/mac/services
python3 -m unittest discover tests/mac/services/local_operator_bridge
git diff --check
```

If live verification is attempted, use a newline-delimited JSON-RPC request piped to:

```bash
python3 -m src.mac.services.local_operator_bridge serve
```

## Risks and Uncertainties

- The POC is MCP-shaped, not a true MCP stdio server.
- Default P0026 audit writes under `~/.smart-home/`; live verification may require running outside the sandbox.
