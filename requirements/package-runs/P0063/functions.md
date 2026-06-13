# P0063 Function Design

## Changed Constants

### FTX_STATE_SCRIPT_NAME

Purpose: Add exact live-write allowlist entry for `state_v1_8_0`.

Inputs: none.

Outputs: script name string.

Side effects: Allows existing upload/start helpers to operate on `state_v1_8_0`.

Tests: Unit test verifies `ensure_allowed_script_name(FTX_STATE_SCRIPT_NAME)`.

## New Functions

### build_ftx_recipe_script(recipe_path)

Purpose: Build one complete FTX script from the imported G1-style recipe chunks.

Inputs: recipe JSON path.

Outputs: complete JavaScript source string.

Side effects: reads recipe and chunk files.

Tests: Unit test verifies chunk mapping and output order.

### ftx_state_number_get(base_url, number_id)

Purpose: Read one FTX state virtual number.

Inputs: base URL and numeric component id.

Outputs: numeric value.

Side effects: `Number.GetStatus` RPC read.

Tests: Covered through deploy test.

### ftx_state_kvs_get(base_url, key)

Purpose: Read one allowed FTX state KVS key for verification.

Inputs: base URL and KVS key.

Outputs: KVS value or `None`.

Side effects: `KVS.Get` RPC read.

Tests: Covered through deploy test.

### verify_ftx_state_zero_vvx(base_url)

Purpose: Verify that when `ftx.state.run.vvx` is `0`, VVX efficiency number and history are zero.

Inputs: base URL.

Outputs: summary dictionary.

Side effects: `KVS.Get` and `Number.GetStatus` RPC reads.

Tests: Covered through deploy test.

### deploy_ftx_state(base_url, recipe_path)

Purpose: Upload and run `state_v1_8_0` on the verified dampers endpoint and verify zero VVX efficiency.

Inputs: base URL, recipe path, timeouts and chunk size.

Outputs: `FtxStateDeployResult`.

Side effects: `Script.PutCode`, `Script.Start`, state-script writes to KVS and virtual numbers.

Tests: Unit test verifies RPC sequence and result.
