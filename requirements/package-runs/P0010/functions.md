# Package P0010 Function Design

## Package

`P0010`

## New Functions

### normalize_base_url()

Purpose:
- Normalize a Shelly base URL so RPC and debug-log paths can be appended deterministically.

Inputs:
- Base URL string.

Outputs:
- Base URL without trailing slash.

Side effects:
- None.

Reason:
- Keeps URL assembly centralized and testable.

Tests:
- Unit tests in `tests/mac/tools/shelly_live/test_core.py`.

### rpc_call()

Purpose:
- Send one bounded Shelly JSON-RPC request over HTTP POST.

Inputs:
- Base URL, method, optional params, timeout.

Outputs:
- Decoded `result` object.

Side effects:
- Performs one HTTP request.

Reason:
- Provides a narrow RPC transport primitive for allowed live calls.

Tests:
- Unit tests with a fake opener verify request URL/body and error handling.

### get_status()

Purpose:
- Read Shelly device status.

Inputs:
- Base URL, timeout.

Outputs:
- Shelly status result object.

Side effects:
- Performs `Shelly.GetStatus`.

Reason:
- Required runtime health/read-only check before live deploy.

Tests:
- Covered through mocked RPC call tests.

### list_scripts()

Purpose:
- Read current Shelly script list.

Inputs:
- Base URL, timeout.

Outputs:
- List of script objects.

Side effects:
- Performs `Script.List`.

Reason:
- Required to find or create `hello_v1_0_0` safely.

Tests:
- Unit tests cover script lookup from returned list.

### find_script()

Purpose:
- Locate a script by exact allowed name in a `Script.List` response.

Inputs:
- Script list and script name.

Outputs:
- Matching script object or `None`.

Side effects:
- None.

Reason:
- Separates parsing from RPC transport.

Tests:
- Unit tests for found and missing scripts.

### ensure_allowed_script_name()

Purpose:
- Reject any live-write script name other than `hello_v1_0_0`.

Inputs:
- Script name.

Outputs:
- None.

Side effects:
- None.

Reason:
- Enforces P0010 live safety boundary.

Tests:
- Unit tests verify allowed and forbidden names.

### ensure_script()

Purpose:
- Create `hello_v1_0_0` if missing, otherwise reuse the existing script slot.

Inputs:
- Base URL, script name, timeout.

Outputs:
- Script id.

Side effects:
- May perform `Script.Create` for `hello_v1_0_0`.

Reason:
- Allows idempotent live deploy.

Tests:
- Unit tests with fake RPC responses.

### put_script_code()

Purpose:
- Upload complete built script code to a script slot.

Inputs:
- Base URL, script id, script name, code text, timeout.

Outputs:
- RPC result object.

Side effects:
- Performs `Script.PutCode` for `hello_v1_0_0`.

Reason:
- Core deploy operation.

Tests:
- Unit tests verify method and params.

### start_script()

Purpose:
- Start the `hello_v1_0_0` script.

Inputs:
- Base URL, script id, script name, timeout.

Outputs:
- RPC result object.

Side effects:
- Performs `Script.Start` for `hello_v1_0_0`.

Reason:
- Required package behavior.

Tests:
- Unit tests verify method and params.

### stop_script()

Purpose:
- Stop the `hello_v1_0_0` script when needed.

Inputs:
- Base URL, script id, script name, timeout.

Outputs:
- RPC result object.

Side effects:
- Performs `Script.Stop` for `hello_v1_0_0`.

Reason:
- Safe cleanup/idempotency if a previous run left it running.

Tests:
- Unit tests verify method and params.

### delete_script()

Purpose:
- Delete only `hello_v1_0_0` when cleanup is explicitly requested.

Inputs:
- Base URL, script id, script name, timeout.

Outputs:
- RPC result object.

Side effects:
- Performs `Script.Delete` for `hello_v1_0_0`.

Reason:
- Optional safe rollback residue cleanup.

Tests:
- Unit tests verify method and params and forbidden-name rejection.

### capture_debug_log()

Purpose:
- Capture `/debug/log` output for a bounded time and stop when expected text is observed.

Inputs:
- Base URL, expected text, timeout seconds, HTTP timeout.

Outputs:
- Captured log excerpt text.

Side effects:
- Opens the Shelly debug log stream.

Reason:
- Required live evidence for expected `hello` output.

Tests:
- Unit tests with fake streaming response.

### deploy_hello()

Purpose:
- Orchestrate status read, script list, stop existing script if needed, create/reuse, upload code, start bounded log capture before script start, stop `hello_v1_0_0` after verification, final list, optional cleanup.

Inputs:
- Base URL, script path, expected text, timeouts, cleanup flag.

Outputs:
- Structured deployment result.

Side effects:
- Performs only allowed P0010 live actions for `hello_v1_0_0`.

Reason:
- Main package workflow for live verification.

Tests:
- Unit tests with fake client/transport.

### main()

Purpose:
- Provide CLI entry point for `python3 -m src.mac.tools.shelly_live`.

Inputs:
- CLI arguments.

Outputs:
- Process exit status.

Side effects:
- Runs live deploy workflow when invoked.

Reason:
- Required operator/Codex command surface.

Tests:
- Light unit coverage for argument validation where practical; full behavior covered through function tests.

## Changed Functions

### Existing Shelly build tests

Purpose:
- Align fixture role assertions from `hello` to `hello_v1_0_0`.

Reason:
- P0010 requires installed script name `hello_v1_0_0`.

## Removed Functions

None planned.

## Important Functions Intentionally Left Unchanged

- Existing `shelly_build` core build/chunk/validate functions remain unchanged unless the role rename exposes a narrow test fixture issue.
