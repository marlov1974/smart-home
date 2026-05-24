# P0014 Consistency Review

## Classification

WARN

## Result

P0014 is consistent with repository truth and implementable inside the stated package scope, with one live-device/API support uncertainty that must remain a runtime gate before apply.

## Evidence

- `memory/device-management/identity-and-registry.md` confirms the P0014 identity split:
  - logical role `ftx-dampers`
  - physical Shelly id `8813bfd99f54`
  - stable LAN address `192.168.77.30`
  - P0014 test Shelly device name `ftx_dampers`
  - P0014 test channel name `dampers`
- `memory/infrastructure/devices.md` confirms the dampers stable LAN address and operator NAT URL as reachability facts:
  - stable LAN address `192.168.77.30`
  - operator NAT URL `http://192.168.86.240:8030/`
  - physical Shelly id `8813bfd99f54`
- `memory/device-management/mac-layer.md` requires Mac tools to accept runtime endpoints separately from durable identity and to verify live identity before writes.
- Existing Mac tooling under `src/mac/tools/shelly_live/` uses Python standard library only and bounded RPC calls; P0014 can add package-scoped device-management tooling under `src/mac/tools/`.

## API Discovery

Official Shelly Gen2+ documentation supports the intended narrow API surface:

- `Shelly.GetDeviceInfo` for physical device identity.
- `Shelly.GetStatus` / `Sys.GetConfig` for live status/config evidence.
- `Sys.SetConfig` with `config.device.name` for the device display name.
- `Switch.GetConfig` / `Switch.SetConfig` for switch channel config, including `name` and `initial_state`.
- `Virtual.Add` creates virtual components with ids in `200..299`.
- `Number.GetConfig` / `Number.SetConfig` / `Number.GetStatus` / `Number.Set` configure and set a virtual number component.
- `Shelly.GetComponents` can list dynamic components with config/status.

## Uncertainty / Gate

Shelly virtual components are documented as available only for Gen3 and Gen2 Pro devices. P0014 target model support must therefore be confirmed from live `Shelly.GetDeviceInfo`, `Shelly.GetComponents`/`Virtual.Add`, or method availability before creating `House Temp`.

This is a WARN rather than STOP because the package explicitly requires discovery and says to stop before applying unsupported/unclear items. The implementation can enforce that by planning all changes, verifying identity first, and refusing apply if the number component API is unavailable.

## Scope Decision

Proceed with implementation limited to:

- package-run evidence under `requirements/package-runs/P0014/`
- Python standard-library Mac device-management tooling under `src/mac/tools/`
- focused tests under `tests/mac/tools/`
- function catalog updates under `docs/functions/`

No Shelly runtime, Home Assistant, floor-cooling, heat-pump, G1, actuator-state, or broad registry changes are needed.
