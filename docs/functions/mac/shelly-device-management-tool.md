# Shelly Device Management Tool

Last changed: P0014

## Module

```text
src.mac.tools.shelly_device.core
```

## Purpose

Mac-side Shelly device configuration management for narrow, package-scoped baselines.

P0014 implements only the dampers safe baseline:

- verify physical Shelly id `8813bfd99f54`
- set device display name `ftx_dampers`
- set switch channel name `dampers`
- set switch `initial_state` to `restore_last`
- create or verify virtual number component `House Temp`

## CLI

```bash
python3 -m src.mac.tools.shelly_device plan --base-url <runtime endpoint>
python3 -m src.mac.tools.shelly_device apply --base-url <runtime endpoint>
python3 -m src.mac.tools.shelly_device verify --base-url <runtime endpoint>
```

The runtime endpoint is execution-environment reachability, not durable device identity.

## Important Functions

`read_device_state(base_url, timeout, opener)` gathers live identity and P0014-relevant config/status using read-only RPC calls.

`verify_target_identity(state)` confirms the reached endpoint is the intended physical dampers Shelly before writes.

`build_plan(state)` compares current state with the P0014 baseline and returns explicit planned actions.

`validate_plan(actions)` enforces the P0014 write allowlist before apply.

`apply_plan(base_url, actions, timeout, opener)` executes only allowlisted configuration/component actions.

`verify_baseline(state)` verifies readback after apply.

## Safety Boundary

The tool does not perform actuator-state writes. It must not call `Switch.Set`, `Switch.Toggle`, relay, cover, or equivalent output-control RPCs for P0014.

Current write allowlist:

- `Sys.SetConfig`
- `Switch.SetConfig`
- `Virtual.Add`
- `Number.SetConfig`
- `Number.Set`

`Number.Set` is used only to set the neutral initial value for the non-actuating `House Temp` virtual number component.
