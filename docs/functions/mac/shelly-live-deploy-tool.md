# Mac Shelly Live Deploy Tool Function Catalog

## Scope

Mac-side bounded live deploy/start/log verification for inert Shelly test scripts introduced by P0010.

## Safety Contract

The live-write boundary is hard-coded to:

```text
hello_v1_0_0
```

The tool must reject any other script name for create, code upload, start, stop or delete operations. It does not expose switch, relay, cover, KVS, component, network, MQTT, Bluetooth, cloud or actuator operations.

## Functions

### normalize_base_url()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Normalize a Shelly base URL before appending RPC or debug-log paths.

Inputs:
- Base URL string.

Outputs:
- Base URL string without trailing slash.

Side effects:
- None.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### rpc_call()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Send one bounded Shelly JSON-RPC call over HTTP POST and return the result.

Inputs:
- Base URL, RPC method, optional params, timeout and optional opener for tests.

Outputs:
- Decoded RPC result.

Side effects:
- Performs one HTTP request.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### list_scripts()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Read the Shelly script list and validate that it is parseable.

Inputs:
- Base URL, timeout and optional opener.

Outputs:
- List of script objects.

Side effects:
- Performs `Script.List`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### ensure_allowed_script_name()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Enforce the P0010 live-write script-name boundary.

Inputs:
- Script name.

Outputs:
- None.

Side effects:
- None.

Contract notes:
- Raises unless the name is exactly `hello_v1_0_0`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### ensure_script()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Reuse the existing `hello_v1_0_0` script slot or create it if missing.

Inputs:
- Base URL, script name, timeout and optional opener.

Outputs:
- Numeric script id.

Side effects:
- May perform `Script.Create` for `hello_v1_0_0`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### put_script_code()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Upload complete built script code into the allowed script slot.

Inputs:
- Base URL, script id, script name, code text, timeout and optional opener.

Outputs:
- RPC result.

Side effects:
- Performs `Script.PutCode`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### capture_debug_log()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Capture Shelly `/debug/log` output for a bounded time and return once expected text appears.

Inputs:
- Base URL, expected text, log timeout, HTTP timeout and optional opener.

Outputs:
- Captured log excerpt.

Side effects:
- Opens the debug log stream.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### deploy_hello()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Run the P0010 live sequence: status read, script list, optional stop of existing `hello_v1_0_0`, create/reuse, code upload, start bounded log capture before script start, stop `hello_v1_0_0` after verification, final script list and optional cleanup.

Inputs:
- Base URL, built script path, expected text, log timeout, HTTP timeout, cleanup flag and optional opener.

Outputs:
- `DeployResult` evidence object.

Side effects:
- Performs only allowed P0010 live actions for `hello_v1_0_0`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0010

### main()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Provide the CLI for `python3 -m src.mac.tools.shelly_live deploy-hello`.

Inputs:
- CLI arguments.

Outputs:
- Process exit status.

Side effects:
- Runs live deploy/log verification when invoked.

Tests:
- Behavior covered through core function tests.

Introduced:
- P0010

Last changed:
- P0010
