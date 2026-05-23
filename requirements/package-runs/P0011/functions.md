# Package P0011 Function Design

## Package

`P0011`

## New Functions

### ensure_allowed_live_script_name()

Purpose: Allow only `hello_v1_0_0` and `spotprice_v0_9_0` for P0011 live script lifecycle actions.

Inputs: Script name and optional action context.

Outputs: None.

Side effects: None.

Reason: P0011 expands the P0010 live boundary from one script name to two tightly scoped names.

Tests: Unit tests reject unknown names.

### split_rpc_upload_chunks()

Purpose: Split built script text into bounded in-memory upload chunks.

Inputs: Script text and upload chunk byte limit.

Outputs: Ordered chunk strings.

Side effects: None.

Reason: P0011 must prove Mac direct deploy with RPC upload chunks separate from repo deploy chunks.

Tests: Unit tests verify multiple chunks and invalid limits.

### put_script_code_chunked()

Purpose: Upload script code with first chunk replacing existing code and later chunks appending.

Inputs: Base URL, script id, script name, code text, upload chunk byte size, timeout and opener.

Outputs: Upload chunk count.

Side effects: Performs `Script.PutCode` RPC calls only for allowed script names.

Reason: Core P0011 Mac upload behavior.

Tests: Unit tests verify `append:false` then `append:true` calls and chunk count.

### cleanup_hello_residue()

Purpose: Stop and delete only `hello_v1_0_0` if present.

Inputs: Base URL, scripts list, timeout and opener.

Outputs: Whether cleanup happened.

Side effects: May perform `Script.Stop` and `Script.Delete` for `hello_v1_0_0`.

Reason: P0011 requires cleanup of P0010 residue before spotprice deployment.

Tests: Unit tests verify only hello cleanup calls.

### kvs_get()

Purpose: Read one allowed KVS key through Shelly RPC.

Inputs: Base URL, key, timeout and opener.

Outputs: KVS value or `None`.

Side effects: Performs `KVS.Get`.

Reason: P0011 requires KVS read verification.

Tests: Unit tests verify allowed key reads and forbidden key rejection.

### read_spotprice_kvs()

Purpose: Read all documented spotprice KVS keys.

Inputs: Base URL, timeout and opener.

Outputs: Mapping of key to value.

Side effects: Performs bounded `KVS.Get` calls.

Reason: Package evidence needs a complete safe summary of spotprice-owned KVS output.

Tests: Unit tests verify key set and values.

### verify_spotprice_kvs()

Purpose: Validate spotprice KVS output is present and parseable enough for the live proof.

Inputs: KVS value mapping.

Outputs: Safe summary mapping.

Side effects: None.

Reason: P0011 needs objective KVS verification criteria.

Tests: Unit tests verify valid 12-block CSV and failure for malformed values.

### deploy_spotprice()

Purpose: Orchestrate P0011 cleanup, chunked upload, start/log/KVS verification and stop.

Inputs: Base URL, script path, expected log text, upload chunk size, timeouts and opener.

Outputs: Structured deploy result.

Side effects: Performs only P0011-allowed live actions.

Reason: Main package workflow.

Tests: Unit tests with fake opener verify RPC sequence and forbidden operation absence.

## Changed Functions

### put_script_code()

Purpose: Remain as the one-shot code upload helper for P0010 and as the single RPC primitive used by chunked upload.

Change: Use the expanded script-name safety guard.

Tests: Existing P0010 tests plus P0011 forbidden-name tests.

### main()

Purpose: Add `deploy-spotprice` CLI while keeping `deploy-hello`.

Change: Print upload chunk count and KVS summary for spotprice runs.

Tests: Behavior covered through function tests and command verification.

## Removed Functions

None.

## Important Functions Intentionally Left Unchanged

- Existing `shelly_build` build/chunk/validate functions.
- Existing `deploy_hello()` behavior except for shared script-name safety helper compatibility.
