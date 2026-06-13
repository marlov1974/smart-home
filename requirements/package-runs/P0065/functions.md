# P0065 Function Design

## Changed Constants

### FTX_BRAIN_SCRIPT_NAME

Purpose: Add exact live-write allowlist entry for `brain_v2_13_0`.

Inputs: none.

Outputs: script name string.

Side effects: Allows existing upload/start helpers to operate on `brain_v2_13_0`.

Tests: `tests/mac/tools/shelly_live/test_core.py`.

## New Functions

### get_script_code()

Purpose: Read live Shelly script code for verification.

Inputs: base URL, script id, timeout and optional opener.

Outputs: JavaScript source text.

Side effects: `Script.GetCode` RPC read.

Tests: covered by deploy brain test.

### verify_ftx_brain_target_floor_code()

Purpose: Verify that a brain script has the P0059/P0060 target-floor behavior.

Inputs: script code text.

Outputs: summary dictionary.

Side effects: none.

Tests: stale-code rejection and deploy brain test.

### ftx_brain_intent_get()

Purpose: Read local dampers brain intent as proof the brain output path completed.

Inputs: base URL, timeout and optional opener.

Outputs: local `ftx.intent.dev.dmp` value.

Side effects: `KVS.Get` RPC read.

Tests: covered by deploy brain test.

### deploy_ftx_brain()

Purpose: Upload, start and verify `brain_v2_13_0` on dampers.

Inputs: base URL, recipe path, expected log text, upload chunk size and timeouts.

Outputs: `FtxBrainDeployResult`.

Side effects: `Script.PutCode`, `Script.Start`, and brain runtime writes to number 204 plus intent KVS contracts.

Tests: deploy brain unit test.
