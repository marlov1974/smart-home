# P0027 function design

## New Functions

### `list_tools()`

- Purpose: Return discovery metadata for the single supported bridge tool.
- Inputs: none.
- Outputs: dictionary containing exactly one tool entry.
- Side effects: none.
- Test coverage: asserts only `shelly_kvs_get_by_nat_octet` is exposed.

### `validate_tool_arguments(arguments)`

- Purpose: Validate the bridge-level argument object before delegation to P0026.
- Inputs: JSON-decoded object.
- Outputs: sanitized dict containing `octet`, `key` and optional `timeout`.
- Side effects: none.
- Test coverage: rejects extra fields, missing fields and non-object arguments.

### `handle_shelly_kvs_get_by_nat_octet(arguments, kvs_reader=None)`

- Purpose: Call P0026 for the only supported bridge tool.
- Inputs: sanitized or raw argument dict plus optional injected reader for tests.
- Outputs: dictionary with P0026 result fields.
- Side effects: one P0026 call for valid requests; P0026 may perform one HTTP GET and audit append.
- Test coverage: mocked P0026 call count and payload.

### `handle_tool_call(name, arguments, kvs_reader=None)`

- Purpose: Route one tool call by name.
- Inputs: tool name, argument object, optional injected reader.
- Outputs: bridge tool result dictionary.
- Side effects: delegates to P0026 only for the exact supported tool.
- Test coverage: unknown and write-like names rejected without P0026 call.

### `handle_json_rpc_message(message, kvs_reader=None)`

- Purpose: Process one decoded JSON-RPC-like request.
- Inputs: decoded JSON object.
- Outputs: decoded JSON response object.
- Side effects: may delegate one valid tool call to P0026.
- Test coverage: `tools/list`, `tools/call`, unknown method and invalid request cases.

### `process_json_line(line, kvs_reader=None)`

- Purpose: Decode one input line and encode one response line.
- Inputs: JSON text line.
- Outputs: JSON text line ending with newline.
- Side effects: may delegate one valid tool call to P0026.
- Test coverage: malformed JSON error and valid request framing.

### `serve(input_stream, output_stream, kvs_reader=None)`

- Purpose: Run the local bridge loop over newline-delimited JSON messages.
- Inputs: text input/output streams and optional injected reader.
- Outputs: integer status code.
- Side effects: reads stdin and writes stdout; may delegate valid tool calls.
- Test coverage: one-line serve smoke.

### `main(argv=None)`

- Purpose: CLI entry point for `python3 -m src.mac.services.local_operator_bridge serve`.
- Inputs: CLI args.
- Outputs: process status code.
- Side effects: runs `serve` for the `serve` subcommand.
- Test coverage: indirect through `serve` and protocol functions.

## Changed Functions

None.

## Removed Functions

None.

## Functions Intentionally Not Created

- No KVS write helpers.
- No script control helpers.
- No switch/light/cover helpers.
- No arbitrary URL fetch/proxy.
- No shell execution.
- No Codex package-runner.
