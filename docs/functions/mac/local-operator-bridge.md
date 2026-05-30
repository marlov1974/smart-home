# Mac Local Operator Bridge

Last changed: P0027

## Purpose

`src.mac.services.local_operator_bridge` is a read-only local bridge POC for operator/dev workflows. It exposes exactly one MCP-shaped JSON-RPC tool and delegates the actual Shelly read to the verified P0026 helper.

P0027 does not claim full MCP stdio compatibility. It uses newline-delimited JSON-RPC-like messages over stdin/stdout and intentionally omits full MCP initialization, capability negotiation and `Content-Length` framing.

## CLI

```bash
python3 -m src.mac.services.local_operator_bridge serve
```

Each stdin line is one JSON request. Each stdout line is one JSON response.

## Supported Methods

### `tools/list`

Returns exactly one tool:

```text
shelly_kvs_get_by_nat_octet
```

### `tools/call`

Calls the one supported tool. Example request:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"shelly_kvs_get_by_nat_octet","arguments":{"octet":30,"key":"hp.price.status","timeout":5}}}
```

The bridge accepts only:

- `octet`
- `key`
- optional `timeout`

Any extra argument such as `url`, `host`, `path`, `method` or shell/proxy/write hints is rejected before P0026 is called.

## P0026 Delegation

The bridge imports and calls:

```text
src.mac.tools.local_kvs_read.kvs_get_by_nat_octet(...)
```

P0026 remains responsible for:

- octet and KVS key validation
- NAT URL construction
- read-only `KVS.Get`
- HTTP timeout handling
- JSON response parsing
- audit logging

## Forbidden Operations

The bridge does not implement:

- `KVS.Set`
- `Script.*`
- `Switch.*`, `Light.*`, `Cover.*`
- relay, dimmer or actuator calls
- component/config/device writes
- arbitrary URL fetch or generic HTTP proxy
- shell execution
- Codex package runner
- Home Assistant bridge
- persistent launchd/service installation

## Functions

### `list_tools()`

Returns the one-tool discovery response.

### `validate_tool_arguments(arguments)`

Rejects non-object arguments, missing `octet`/`key`, invalid timeout and any field outside `octet`, `key`, `timeout`.

### `handle_shelly_kvs_get_by_nat_octet(arguments, kvs_reader=None)`

Delegates one valid call to P0026 and returns the P0026 result as a dictionary.

### `handle_tool_call(name, arguments, kvs_reader=None)`

Routes exactly `shelly_kvs_get_by_nat_octet`; rejects every other tool name.

### `handle_json_rpc_message(message, kvs_reader=None)`

Processes one decoded request for `tools/list` or `tools/call`.

### `process_json_line(line, kvs_reader=None)`

Processes one newline-delimited JSON request and returns one JSON response line.

### `serve(input_stream=None, output_stream=None, kvs_reader=None)`

Runs the bridge loop until EOF.

## Test Coverage

P0027 tests live under:

```text
tests/mac/services/local_operator_bridge/
```

They mock P0026 and do not require live network access.
