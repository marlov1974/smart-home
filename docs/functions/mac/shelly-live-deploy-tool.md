# Mac Shelly Live Deploy Tool Function Catalog

## Scope

Mac-side bounded live deploy/start/log/KVS verification for Shelly test scripts introduced by P0010 and extended by P0011/P0013.

## Safety Contract

The live-write boundary is hard-coded to:

```text
hello_v1_0_0
spotprice_v0_9_0
```

The tool must reject any other script name for create, code upload, start, stop or delete operations. `hello_v1_0_0` is used for P0010 and cleanup residue. `spotprice_v0_9_0` is used for P0011/P0013 upload/log/KVS verification.

The tool does not expose switch, relay, cover, component, network, MQTT, Bluetooth, cloud or actuator operations. KVS access is read-only and limited to the documented spotprice keys.

## Build/deploy source contract

Mac direct deploy reads one complete built Shelly script from `build/shelly/**`.

It does not read `dep/s/ch/**` as its direct-deploy source. Repo deploy chunks are generated artifacts for a possible future Shelly-side pull/install model.

The live deploy tool may split the complete built script into bounded in-memory RPC upload chunks for `Script.PutCode` transport. Those RPC upload chunks are temporary Mac memory chunks, not repository source architecture and not the same as `dep/s/ch/**` chunks.

Packages that change Mac live deploy must preserve this distinction unless the package explicitly changes the deployment model.

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
- Enforce the live-write script-name boundary.

Inputs:
- Script name.

Outputs:
- None.

Side effects:
- None.

Contract notes:
- Raises unless the name is exactly `hello_v1_0_0` or `spotprice_v0_9_0`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0011

### ensure_script()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Reuse the existing allowed script slot or create it if missing.

Inputs:
- Base URL, script name, timeout and optional opener.

Outputs:
- Numeric script id.

Side effects:
- May perform `Script.Create` for an allowed script name only.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0010

Last changed:
- P0011

### split_rpc_upload_chunks()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Split complete built script code into bounded in-memory RPC upload chunks.

Inputs:
- Script code text read from the built script and upload chunk byte limit.

Outputs:
- Ordered chunk strings.

Side effects:
- None.

Contract notes:
- Input must be the complete built script, not concatenated repo deploy chunks from `dep/s/ch/**`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0011

Last changed:
- P0013

### put_script_code_chunked()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Upload script code by replacing with the first RPC chunk and appending subsequent chunks.

Inputs:
- Base URL, script id, script name, complete built-script code text, upload chunk byte limit, timeout and optional opener.

Outputs:
- Upload chunk count.

Side effects:
- Performs `Script.PutCode`.

Contract notes:
- Uses temporary in-memory RPC upload chunks created from the complete built script.
- Does not read or require `dep/s/ch/**` repo deploy chunks.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0011

Last changed:
- P0013

### read_spotprice_kvs()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Read the documented spotprice KVS keys.

Inputs:
- Base URL, timeout and optional opener.

Outputs:
- Mapping from KVS key to value.

Side effects:
- Performs read-only `KVS.Get` calls.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0011

Last changed:
- P0013

### verify_spotprice_kvs()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Validate that spotprice KVS output is present and parseable.

Inputs:
- Mapping of KVS key to value.

Outputs:
- Safe summary containing status, price count/range, date, area and updated time.

Side effects:
- None.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0011

Last changed:
- P0013

### deploy_spotprice()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_live/core.py`

Purpose:
- Run the live sequence: status read, `spotprice_v0_9_0` create/reuse, chunked built-script upload, start, bounded log capture, KVS read/validation, stop and final script list.

Inputs:
- Base URL, built script path, expected text, upload chunk byte limit, log timeout, KVS timeout, HTTP timeout and optional opener.

Outputs:
- `SpotpriceDeployResult` evidence object.

Side effects:
- Performs only allowed live actions for `spotprice_v0_9_0`, plus read-only `KVS.Get` for documented spotprice keys.

Contract notes:
- The script path must point to a complete built script, normally under `build/shelly/**`.
- The deploy source is not `dep/s/ch/**`.

Tests:
- `tests/mac/tools/shelly_live/test_core.py`

Introduced:
- P0011

Last changed:
- P0013

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

Contract notes:
- The script path must point to a complete built script.

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
- Provide the CLI for `python3 -m src.mac.tools.shelly_live`.

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
- P0013
