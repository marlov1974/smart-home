# P0014 Function Design

## New Module: `src.mac.tools.shelly_device.core`

### `normalize_base_url`

- Status: new
- Purpose: normalize a runtime Shelly base URL for deterministic RPC paths.
- Inputs: base URL string.
- Outputs: normalized URL without trailing slash.
- Side effects: none.
- Reason: P0014 separates runtime endpoint from durable identity.
- Test coverage: unit test for trailing slash and empty value rejection.

### `rpc_call`

- Status: new
- Purpose: send one JSON-RPC request to a Shelly endpoint and return the result.
- Inputs: base URL, method, optional params, timeout, optional opener.
- Outputs: RPC result.
- Side effects: network call when not using a fake opener.
- Reason: shared bounded RPC primitive for plan/apply/verify.
- Test coverage: request body, error handling.

### `read_device_state`

- Status: new
- Purpose: gather the P0014-relevant live identity/config/status state.
- Inputs: base URL, timeout, opener.
- Outputs: `DeviceState`.
- Side effects: read-only RPC calls.
- Reason: one consistent state snapshot for plan, apply, verify and evidence.
- Test coverage: fake RPC sequence populates state and components.

### `verify_target_identity`

- Status: new
- Purpose: confirm reached endpoint is the intended dampers device.
- Inputs: `DeviceState`.
- Outputs: none.
- Side effects: raises on mismatch.
- Reason: package requires physical id verification before writes.
- Test coverage: accepts matching Shelly id suffix, rejects mismatches.

### `find_house_temp_component`

- Status: new
- Purpose: find the unique `House Temp` virtual number component.
- Inputs: `DeviceState`.
- Outputs: component id or `None`.
- Side effects: raises on duplicates or wrong component type.
- Reason: number component operations must be unambiguous.
- Test coverage: missing, present, duplicate and wrong-type cases.

### `build_plan`

- Status: new
- Purpose: compare current state with the P0014 baseline and produce allowlisted actions.
- Inputs: `DeviceState`.
- Outputs: tuple of `PlannedAction`.
- Side effects: none.
- Reason: explicit plan/apply/verify model and idempotency.
- Test coverage: action generation and idempotent no-op plan.

### `validate_plan`

- Status: new
- Purpose: enforce P0014 write allowlist before live apply.
- Inputs: planned actions.
- Outputs: none.
- Side effects: raises on forbidden method.
- Reason: package requires rejection before apply for out-of-scope changes.
- Test coverage: allows P0014 actions, rejects `Switch.Set`.

### `apply_plan`

- Status: new
- Purpose: execute allowlisted planned actions.
- Inputs: base URL, actions, timeout, opener.
- Outputs: list of RPC results.
- Side effects: writes only P0014 baseline config/component changes.
- Reason: separate planning from applying and centralize allowlist.
- Test coverage: fake opener confirms exact write methods and params.

### `verify_baseline`

- Status: new
- Purpose: verify readback matches the P0014 baseline.
- Inputs: `DeviceState`.
- Outputs: summary dict.
- Side effects: none.
- Reason: apply must prove device name, channel name, restore output, and `House Temp`.
- Test coverage: accepts matching state and rejects missing/mismatched state.

### `run_plan`, `run_apply`, `run_verify`

- Status: new
- Purpose: command-level orchestration for CLI modes.
- Inputs: base URL, timeout, opener.
- Outputs: evidence dict.
- Side effects: `run_apply` writes allowlisted changes; others read only.
- Reason: keep CLI thin and testable.
- Test coverage: apply orchestration with fake before/after states.

### `main`

- Status: new
- Purpose: parse CLI arguments and print JSON evidence.
- Inputs: argv.
- Outputs: process exit code.
- Side effects: stdout/stderr and live RPC calls.
- Reason: package-required Mac tool entry point.
- Test coverage: function behavior covered through lower-level units.

## New Module: `src.mac.tools.shelly_device.__main__`

### module entry point

- Status: new
- Purpose: support `python3 -m src.mac.tools.shelly_device`.
- Inputs: CLI args.
- Outputs: process exit code.
- Side effects: delegates to `main`.
- Reason: mirrors existing Mac tool layout.
- Test coverage: import-level only.
